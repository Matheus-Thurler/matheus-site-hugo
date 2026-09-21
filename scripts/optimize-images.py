#!/usr/bin/env python3
"""Compress oversized raster images to WebP/JPEG for the public site."""

from __future__ import annotations

import io
import urllib.request
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
IMAGES = ROOT / "static" / "images"
YOUTUBE_IDS = ("5_fiNmpHYNE", "joP5JzS9Bro")
MAX_EDGE = 1400
SKIP_DIRS = {"icons"}
SKIP_NAMES = {"logo.svg", "avatar.svg"}


def crop_center_16x9(im: Image.Image) -> Image.Image:
    width, height = im.size
    target_h = round(width * 9 / 16)
    if height <= target_h:
        return im
    top = (height - target_h) // 2
    return im.crop((0, top, width, top + target_h))


def save_webp(im: Image.Image, dest: Path, quality: int = 78) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    params = {"quality": quality, "method": 6}
    if im.mode == "RGBA":
        params["exact"] = True
    im.save(dest, "WEBP", **params)


def fit(im: Image.Image, max_w: int, max_h: int | None = None) -> Image.Image:
    width, height = im.size
    max_h = max_h or max_w * 4
    if width <= max_w and height <= max_h:
        return im
    im = im.copy()
    im.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)
    return im


def open_image(path: Path) -> Image.Image:
    im = Image.open(path)
    if im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info):
        return im.convert("RGBA")
    return im.convert("RGB")


def convert_raster(path: Path) -> Path | None:
    if path.suffix.lower() not in {".png", ".jpg", ".jpeg"}:
        return None
    if path.parent.name in SKIP_DIRS or path.name in SKIP_NAMES:
        return None
    if path.stat().st_size < 80_000:
        return None

    im = open_image(path)
    quality = 82 if "logo" in path.name else 78
    if path.name == "avatar.png":
        im = fit(im, 512, 512)
        webp = IMAGES / "avatar.webp"
        jpg = IMAGES / "avatar.jpg"
        touch = IMAGES / "apple-touch-icon.png"
        save_webp(im, webp, quality=80)
        rgb = im.convert("RGB")
        rgb.save(jpg, "JPEG", quality=82, optimize=True, progressive=True)
        rgb.resize((180, 180), Image.Resampling.LANCZOS).save(
            touch, "PNG", optimize=True
        )
        print(f"avatar {path.stat().st_size} -> {webp.stat().st_size} / {jpg.stat().st_size}")
        return webp

    im = fit(im, MAX_EDGE)
    dest = path.with_suffix(".webp")
    save_webp(im, dest, quality=quality)
    print(f"{path.relative_to(ROOT)} {path.stat().st_size} -> {dest.stat().st_size}")
    return dest


def fetch_youtube_thumbs() -> None:
    dest_dir = IMAGES / "youtube"
    dest_dir.mkdir(parents=True, exist_ok=True)
    for video_id in YOUTUBE_IDS:
        dest = dest_dir / f"{video_id}.webp"
        last_error = None
        for name in ("maxresdefault.jpg", "sddefault.jpg", "hqdefault.jpg"):
            url = f"https://i.ytimg.com/vi/{video_id}/{name}"
            try:
                with urllib.request.urlopen(url, timeout=20) as response:
                    data = response.read()
            except Exception as exc:  # noqa: BLE001
                last_error = exc
                continue
            im = Image.open(io.BytesIO(data)).convert("RGB")
            if im.width < 320 or im.height < 180:
                continue
            im = crop_center_16x9(im)
            im = fit(im, 960)
            save_webp(im, dest, quality=76)
            print(f"youtube {video_id} {name} {im.size} -> {dest.stat().st_size}")
            break
        else:
            raise SystemExit(f"failed to fetch thumb {video_id}: {last_error}")


def replace_refs(converted: list[tuple[Path, Path]]) -> None:
    mapping = {}
    for src, dest in converted:
        old = "/" + src.relative_to(ROOT / "static").as_posix()
        new = "/" + dest.relative_to(ROOT / "static").as_posix()
        mapping[old] = new
    mapping["/images/avatar.png"] = "/images/avatar.webp"
    roots = [
        ROOT / "content",
        ROOT / "layouts",
        ROOT / "hugo.yaml",
        ROOT / "data",
    ]
    files: list[Path] = []
    for root in roots:
        if root.is_file():
            files.append(root)
            continue
        files.extend(p for p in root.rglob("*") if p.suffix in {".md", ".html", ".yaml", ".yml", ".json"})
    for path in files:
        text = path.read_text(encoding="utf-8")
        updated = text
        for old, new in mapping.items():
            updated = updated.replace(old, new)
        if updated != text:
            path.write_text(updated, encoding="utf-8")
            print(f"updated refs {path.relative_to(ROOT)}")


def main() -> None:
    converted: list[tuple[Path, Path]] = []
    for path in sorted(IMAGES.rglob("*")):
        if not path.is_file():
            continue
        dest = convert_raster(path)
        if dest is not None and dest != path:
            converted.append((path, dest))
    fetch_youtube_thumbs()
    replace_refs(converted)
    for src, dest in converted:
        if src.exists() and src != dest and src.suffix.lower() == ".png":
            src.unlink()
            print(f"removed {src.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
