(() => {
  const clock = document.querySelector("[data-cluster-clock]");
  if (clock) {
    const fmt = new Intl.DateTimeFormat("pt-BR", {
      timeZone: "America/Sao_Paulo",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
      hour12: false,
    });
    const tick = () => {
      clock.textContent = fmt.format(new Date()) + " -03";
    };
    tick();
    window.setInterval(tick, 1000);
  }

  const canvas = document.getElementById("mesh");
  if (!canvas || window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    return;
  }

  const ctx = canvas.getContext("2d");
  const nodes = [];
  const count = 18;

  const resize = () => {
    canvas.width = canvas.clientWidth * devicePixelRatio;
    canvas.height = canvas.clientHeight * devicePixelRatio;
    ctx.setTransform(devicePixelRatio, 0, 0, devicePixelRatio, 0, 0);
  };

  const seed = () => {
    nodes.length = 0;
    const w = canvas.clientWidth;
    const h = canvas.clientHeight;
    for (let i = 0; i < count; i += 1) {
      nodes.push({
        x: Math.random() * w,
        y: Math.random() * h,
        vx: (Math.random() - 0.5) * 0.25,
        vy: (Math.random() - 0.5) * 0.25,
      });
    }
  };

  const step = () => {
    const w = canvas.clientWidth;
    const h = canvas.clientHeight;
    ctx.clearRect(0, 0, w, h);
    ctx.lineWidth = 1;
    nodes.forEach((n) => {
      n.x += n.vx;
      n.y += n.vy;
      if (n.x < 0 || n.x > w) n.vx *= -1;
      if (n.y < 0 || n.y > h) n.vy *= -1;
    });
    for (let i = 0; i < nodes.length; i += 1) {
      for (let j = i + 1; j < nodes.length; j += 1) {
        const a = nodes[i];
        const b = nodes[j];
        const d = Math.hypot(a.x - b.x, a.y - b.y);
        if (d < 160) {
          ctx.strokeStyle = `rgba(126, 200, 227, ${0.12 * (1 - d / 160)})`;
          ctx.beginPath();
          ctx.moveTo(a.x, a.y);
          ctx.lineTo(b.x, b.y);
          ctx.stroke();
        }
      }
    }
    nodes.forEach((n) => {
      ctx.fillStyle = "rgba(126, 200, 227, 0.55)";
      ctx.beginPath();
      ctx.arc(n.x, n.y, 1.6, 0, Math.PI * 2);
      ctx.fill();
    });
    requestAnimationFrame(step);
  };

  resize();
  seed();
  step();
  window.addEventListener("resize", () => {
    resize();
    seed();
  });
})();
