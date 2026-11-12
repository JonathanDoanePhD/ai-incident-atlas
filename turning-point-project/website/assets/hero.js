/* Hero wireframe: a slowly turning icosahedron in light cyan, echoing the brand slide.
   Static frame when the viewer prefers reduced motion. */
(function () {
  "use strict";
  const c = document.getElementById("heroGeo");
  if (!c || !c.getContext) return;
  const ctx = c.getContext("2d");
  const t = (1 + Math.sqrt(5)) / 2;
  const V = [[-1, t, 0], [1, t, 0], [-1, -t, 0], [1, -t, 0], [0, -1, t], [0, 1, t], [0, -1, -t], [0, 1, -t], [t, 0, -1], [t, 0, 1], [-t, 0, -1], [-t, 0, 1]];
  const E = [];
  for (let i = 0; i < 12; i++) for (let j = i + 1; j < 12; j++) {
    const d = V[i].reduce((s, v, k) => s + (v - V[j][k]) ** 2, 0);
    if (Math.abs(d - 4) < 1e-6) E.push([i, j]);
  }
  const dots = Array.from({ length: 26 }, (_, i) => [((i * 97) % 100) / 100, ((i * 57 + 13) % 100) / 100, 0.6 + ((i * 31) % 10) / 10]);
  const still = matchMedia("(prefers-reduced-motion: reduce)").matches;
  function draw(time) {
    const W = c.width, H = c.height, a = time * 0.00012, b = 0.42 + Math.sin(time * 0.00007) * 0.12;
    ctx.clearRect(0, 0, W, H);
    ctx.fillStyle = "rgba(155,222,255,0.35)";
    dots.forEach(([x, y, r]) => { ctx.beginPath(); ctx.arc(x * W, y * H, r * 2.2, 0, 7); ctx.fill(); });
    const P = V.map(([x, y, z]) => {
      const x1 = x * Math.cos(a) + z * Math.sin(a), z1 = -x * Math.sin(a) + z * Math.cos(a);
      const y2 = y * Math.cos(b) - z1 * Math.sin(b), z2 = y * Math.sin(b) + z1 * Math.cos(b);
      const s = W * 0.2 / (1 + z2 * 0.08);
      return [W / 2 + x1 * s, H / 2 + y2 * s, z2];
    });
    E.forEach(([i, j]) => {
      const depth = (P[i][2] + P[j][2]) / 2;
      ctx.strokeStyle = `rgba(155,222,255,${0.45 + 0.25 * (depth / 2)})`;
      ctx.lineWidth = 2;
      ctx.beginPath(); ctx.moveTo(P[i][0], P[i][1]); ctx.lineTo(P[j][0], P[j][1]); ctx.stroke();
    });
    ctx.fillStyle = "#d8f3ff";
    P.forEach(([x, y]) => { ctx.beginPath(); ctx.arc(x, y, 4.5, 0, 7); ctx.fill(); });
    if (!still) requestAnimationFrame(draw);
  }
  requestAnimationFrame(draw);
})();
