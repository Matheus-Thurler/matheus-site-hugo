#!/usr/bin/env python3
"""Compare Hugo prod vs Django Cloud Run — status, titles, post slugs."""

from __future__ import annotations

import json
import re
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass

PROD = "https://matheusthurler.com.br"
STAGING = "https://matheus-blog-rrqajqgnaq-rj.a.run.app"

PATHS = [
    "/",
    "/posts/",
    "/about/",
    "/archives/",
    "/categories/",
    "/tags/",
    "/privacy/",
    "/terms/",
    "/search/",
    "/links/",
    "/posts/nginx-vs-traefik-vs-caddy/",
    "/posts/internal-developer-platform-kubernetes/",
    "/pt/",
    "/pt/posts/",
    "/index.json",
    "/index.xml",
    "/sitemap.xml",
    "/robots.txt",
    "/ads.txt",
    "/llms.txt",
    "/newsletter/subscribe/",
    "/admin/login/",
]


@dataclass
class FetchResult:
    status: int
    title: str | None
    error: str | None = None


def fetch(base: str, path: str, timeout: int = 20) -> FetchResult:
    url = base.rstrip("/") + path
    req = urllib.request.Request(url, headers={"User-Agent": "site-compare/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read(500_000).decode("utf-8", errors="replace")
            m = re.search(r"<title[^>]*>([^<]+)</title>", body, re.I)
            return FetchResult(resp.status, m.group(1).strip() if m else None)
    except urllib.error.HTTPError as exc:
        return FetchResult(exc.code, None, str(exc))
    except Exception as exc:  # noqa: BLE001
        return FetchResult(0, None, str(exc))


def post_slugs(base: str) -> set[str]:
    posts: set[str] = set()
    # from /posts/ listing
    req = urllib.request.Request(
        base.rstrip("/") + "/posts/",
        headers={"User-Agent": "site-compare/1.0"},
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        html = resp.read().decode("utf-8", errors="replace")
    for m in re.finditer(r'href="(/posts/[a-z0-9-]+/)"', html):
        posts.add(m.group(1))
    # from index.json if available
    try:
        req = urllib.request.Request(
            base.rstrip("/") + "/index.json",
            headers={"User-Agent": "site-compare/1.0"},
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode())
        for item in data if isinstance(data, list) else data.get("pages", []):
            uri = item.get("uri") or item.get("url") or ""
            if "/posts/" in uri:
                posts.add(uri if uri.startswith("/") else f"/{uri}")
    except Exception:
        pass
    return posts


def main() -> int:
    print(f"PROD:    {PROD}")
    print(f"STAGING: {STAGING}\n")
    print(f"{'PATH':<45} {'PROD':<8} {'STAGE':<8} NOTE")
    print("-" * 90)

    issues: list[str] = []
    for path in PATHS:
        prod = fetch(PROD, path)
        stage = fetch(STAGING, path)
        note = ""
        if prod.status != stage.status:
            note = "STATUS DIFF"
            issues.append(f"{path}: prod={prod.status} staging={stage.status}")
        elif prod.status >= 400:
            note = "ERROR"
            issues.append(f"{path}: both {prod.status}")
        elif path.endswith(".json") or path.endswith(".xml") or path.endswith(".txt"):
            note = "ok" if prod.status == 200 else ""
        print(f"{path:<45} {prod.status:<8} {stage.status:<8} {note}")

    print("\n--- Post slugs ---")
    try:
        prod_posts = post_slugs(PROD)
        stage_posts = post_slugs(STAGING)
        only_prod = sorted(prod_posts - stage_posts)
        only_stage = sorted(stage_posts - prod_posts)
        print(f"Prod: {len(prod_posts)} | Staging: {len(stage_posts)} | Shared: {len(prod_posts & stage_posts)}")
        if only_prod:
            print(f"  Only prod ({len(only_prod)}): {', '.join(only_prod[:5])}{'...' if len(only_prod) > 5 else ''}")
            issues.append(f"Posts only on prod: {len(only_prod)}")
        if only_stage:
            print(f"  Only staging ({len(only_stage)}): {', '.join(only_stage[:5])}")
    except Exception as exc:  # noqa: BLE001
        print(f"  Could not compare posts: {exc}")
        issues.append(f"Post slug compare failed: {exc}")

    print("\n--- Summary ---")
    if issues:
        print(f"ISSUES ({len(issues)}):")
        for i in issues:
            print(f"  - {i}")
        return 1
    print("All compared paths OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
