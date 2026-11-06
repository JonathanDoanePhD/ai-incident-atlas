import { useState, type ReactNode } from 'react';

/** Small, dependency-free SVG charts following the project's dataviz rules:
 *  one axis per chart, thin marks, recessive grid, hover tooltip on every mark, table fallback nearby. */

const W = 640;
const PAD = { l: 44, r: 12, t: 12, b: 28 };

interface Tip {
  x: number;
  y: number;
  html: ReactNode;
}

function useTip() {
  const [tip, setTip] = useState<Tip | null>(null);
  const node = tip ? (
    <div className="chart-tip" style={{ left: `${(tip.x / W) * 100}%`, top: tip.y }} role="status">
      {tip.html}
    </div>
  ) : null;
  return { setTip, node };
}

function ticks(lo: number, hi: number, n = 4): number[] {
  const span = hi - lo || 1;
  const step = Math.pow(10, Math.floor(Math.log10(span / n)));
  const err = (n * step) / span;
  const mult = err <= 0.15 ? 10 : err <= 0.35 ? 5 : err <= 0.75 ? 2 : 1;
  const s = step * mult;
  const out = [];
  for (let v = Math.ceil(lo / s) * s; v <= hi + 1e-9; v += s) out.push(Number(v.toFixed(10)));
  return out;
}

export function BarWithFit({ xs, ys, fit, height = 240, yLabel }: { xs: number[]; ys: number[]; fit?: (x: number) => number; height?: number; yLabel: string }) {
  const { setTip, node } = useTip();
  const H = height;
  const ymax = Math.max(...ys, ...(fit ? xs.map(fit) : [])) * 1.08;
  const bw = (W - PAD.l - PAD.r) / xs.length;
  const sx = (i: number) => PAD.l + i * bw;
  const sy = (v: number) => H - PAD.b - (v / ymax) * (H - PAD.t - PAD.b);
  const fitPts = fit ? xs.map((x, i) => `${sx(i) + bw / 2},${sy(fit(x))}`).join(' ') : '';
  return (
    <div className="chart">
      <svg viewBox={`0 0 ${W} ${H}`} role="img" aria-label={yLabel}>
        {ticks(0, ymax).map((t) => (
          <g key={t}>
            <line x1={PAD.l} x2={W - PAD.r} y1={sy(t)} y2={sy(t)} className="grid" />
            <text x={PAD.l - 6} y={sy(t) + 4} className="axis" textAnchor="end">{t}</text>
          </g>
        ))}
        {ys.map((v, i) => (
          <g key={xs[i]} onMouseEnter={() => setTip({ x: sx(i) + bw / 2, y: sy(v) - 8, html: <><b>{xs[i]}</b>: {v} incidents{fit ? <> · trend {fit(xs[i]).toFixed(0)}</> : null}</> })}
            onMouseLeave={() => setTip(null)}>
            <rect x={sx(i)} y={PAD.t} width={bw} height={H - PAD.t - PAD.b} fill="transparent" />
            <rect x={sx(i) + 1} y={sy(v)} width={Math.max(bw - 2, 1)} height={H - PAD.b - sy(v)} rx={2} className="bar" />
          </g>
        ))}
        {fit && <polyline points={fitPts} className="fit" />}
        {xs.map((x, i) => (i % Math.ceil(xs.length / 9) === 0 || i === xs.length - 1 ? (
          <text key={x} x={sx(i) + bw / 2} y={H - 8} className="axis" textAnchor="middle">{x}</text>
        ) : null))}
      </svg>
      {node}
    </div>
  );
}

export function SmallMultiples({ years, series, labels, height = 110 }: { years: number[]; series: Record<string, number[]>; labels: Record<string, string>; height?: number }) {
  const keys = Object.keys(series);
  const ymax = Math.max(...keys.flatMap((k) => series[k])) * 1.1 || 1;
  return (
    <div className="multiples">
      {keys.map((k) => (
        <Spark key={k} title={labels[k] ?? k} years={years} ys={series[k]} ymax={ymax} height={height} />
      ))}
    </div>
  );
}

function Spark({ title, years, ys, ymax, height }: { title: string; years: number[]; ys: number[]; ymax: number; height: number }) {
  const { setTip, node } = useTip();
  const w = W;
  const H = height;
  const p = { l: 36, r: 10, t: 8, b: 20 };
  const sx = (i: number) => p.l + (i / Math.max(years.length - 1, 1)) * (w - p.l - p.r);
  const sy = (v: number) => H - p.b - (v / ymax) * (H - p.t - p.b);
  const pts = ys.map((v, i) => `${sx(i)},${sy(v)}`).join(' ');
  const last = ys.length - 1;
  return (
    <figure className="spark chart">
      <figcaption>{title}</figcaption>
      <svg viewBox={`0 0 ${w} ${H}`} role="img" aria-label={`${title}: share of incidents by year`}
        onMouseLeave={() => setTip(null)}
        onMouseMove={(e) => {
          const r = (e.currentTarget as SVGSVGElement).getBoundingClientRect();
          const x = ((e.clientX - r.left) / r.width) * w;
          const i = Math.max(0, Math.min(last, Math.round(((x - p.l) / (w - p.l - p.r)) * last)));
          setTip({ x: sx(i), y: sy(ys[i]) - 6, html: <><b>{years[i]}</b>: {(ys[i] * 100).toFixed(1)}%</> });
        }}>
        {[0, ymax / 2].map((t) => (
          <g key={t}>
            <line x1={p.l} x2={w - p.r} y1={sy(t)} y2={sy(t)} className="grid" />
            <text x={p.l - 4} y={sy(t) + 4} className="axis" textAnchor="end">{Math.round(t * 100)}%</text>
          </g>
        ))}
        <polyline points={pts} className="line" />
        <circle cx={sx(last)} cy={sy(ys[last])} r={3.5} className="dot" />
        <text x={sx(0)} y={H - 4} className="axis">{years[0]}</text>
        <text x={sx(last)} y={H - 4} className="axis" textAnchor="end">{years[last]}</text>
      </svg>
      {node}
    </figure>
  );
}

export interface DumbbellRow {
  label: string;
  a: number;
  b: number;
  note?: string;
}

/** Two-point comparison per row (before → after). Dots carry identity by position AND legend; values in tooltip. */
export function Dumbbell({ rows, aLabel, bLabel }: { rows: DumbbellRow[]; aLabel: string; bLabel: string }) {
  const { setTip, node } = useTip();
  const rowH = 26;
  const H = rows.length * rowH + 36;
  const left = 230;
  const xmax = Math.max(...rows.flatMap((r) => [r.a, r.b])) * 1.1 || 1;
  const sx = (v: number) => left + (v / xmax) * (W - left - 20);
  return (
    <div className="chart">
      <div className="chart-legend">
        <span><i className="dot-a" /> {aLabel}</span>
        <span><i className="dot-b" /> {bLabel}</span>
      </div>
      <svg viewBox={`0 0 ${W} ${H}`} role="img" aria-label={`${aLabel} versus ${bLabel}`}>
        {ticks(0, xmax).map((t) => (
          <g key={t}>
            <line x1={sx(t)} x2={sx(t)} y1={6} y2={H - 22} className="grid" />
            <text x={sx(t)} y={H - 6} className="axis" textAnchor="middle">{Math.round(t * 100)}%</text>
          </g>
        ))}
        {rows.map((r, i) => {
          const y = 18 + i * rowH;
          return (
            <g key={r.label} onMouseEnter={() => setTip({ x: sx(Math.max(r.a, r.b)), y: y - 10, html: <><b>{r.label}</b><br />{aLabel}: {(r.a * 100).toFixed(1)}% → {bLabel}: {(r.b * 100).toFixed(1)}%{r.note ? <><br />{r.note}</> : null}</> })}
              onMouseLeave={() => setTip(null)}>
              <rect x={0} y={y - rowH / 2} width={W} height={rowH} fill="transparent" />
              <text x={left - 10} y={y + 4} className="label" textAnchor="end">{r.label}</text>
              <line x1={sx(r.a)} x2={sx(r.b)} y1={y} y2={y} className="connector" />
              <circle cx={sx(r.a)} cy={y} r={5} className="dot-a" />
              <circle cx={sx(r.b)} cy={y} r={5} className="dot-b" />
            </g>
          );
        })}
      </svg>
      {node}
    </div>
  );
}

/** Scatter with deterministic jitter (integer data) and a fitted line. */
export function ScatterFit({ points, fit, xLabel, yLabel }: { points: [number, number][]; fit: { slope: number; intercept: number }; xLabel: string; yLabel: string }) {
  const { setTip, node } = useTip();
  const H = 280;
  const xs = points.map(([x]) => Math.log1p(x));
  const xmax = Math.max(...xs) * 1.05;
  const sx = (v: number) => PAD.l + (v / xmax) * (W - PAD.l - PAD.r);
  const sy = (v: number) => H - PAD.b - ((v + 0.5) / 5) * (H - PAD.t - PAD.b);
  const jitter = (i: number) => (((i * 9301 + 49297) % 233280) / 233280 - 0.5) * 0.5;
  const xt = [0, 1, 2, 5, 10, 20, 50].filter((v) => Math.log1p(v) <= xmax);
  return (
    <div className="chart">
      <svg viewBox={`0 0 ${W} ${H}`} role="img" aria-label={`${yLabel} by ${xLabel}`}>
        {[0, 1, 2, 3, 4].map((t) => (
          <g key={t}>
            <line x1={PAD.l} x2={W - PAD.r} y1={sy(t)} y2={sy(t)} className="grid" />
            <text x={PAD.l - 6} y={sy(t) + 4} className="axis" textAnchor="end">{t}</text>
          </g>
        ))}
        {xt.map((t) => (
          <text key={t} x={sx(Math.log1p(t))} y={H - 8} className="axis" textAnchor="middle">{t}</text>
        ))}
        {points.map(([x, y], i) => (
          <circle key={i} cx={sx(Math.log1p(x) + jitter(i + 7) * 0.15)} cy={sy(y + jitter(i))} r={2.4} className="pt"
            onMouseEnter={() => setTip({ x: sx(Math.log1p(x)), y: sy(y) - 10, html: <>{x} reports · severity {y}</> })}
            onMouseLeave={() => setTip(null)} />
        ))}
        <line x1={sx(0)} x2={sx(xmax)} y1={sy(fit.intercept)} y2={sy(fit.intercept + fit.slope * xmax)} className="fit" />
        <text x={W - PAD.r} y={H - 8} className="axis" textAnchor="end">{xLabel} (log scale)</text>
      </svg>
      {node}
    </div>
  );
}

/** Heatmap for a confusion matrix: sequential single hue, value printed in each cell. */
export function Heatmap({ rows, cols, values, rowTitle, colTitle }: { rows: string[]; cols: string[]; values: number[][]; rowTitle: string; colTitle: string }) {
  const max = Math.max(...values.flat(), 1);
  return (
    <div className="table-wrap">
      <table className="heatmap">
        <caption className="muted small">{rowTitle} (rows) × {colTitle} (columns)</caption>
        <thead>
          <tr><th />{cols.map((c) => <th key={c} scope="col">{c}</th>)}</tr>
        </thead>
        <tbody>
          {values.map((row, i) => (
            <tr key={rows[i]}>
              <th scope="row">{rows[i]}</th>
              {row.map((v, j) => {
                const t = v / max;
                return (
                  <td key={j} title={`${rows[i]} → ${cols[j]}: ${v}`}
                    style={{ background: v ? `rgba(57,135,229,${0.12 + 0.8 * t})` : 'transparent', color: t > 0.55 ? '#fff' : undefined }}
                    className={i === j ? 'diag' : ''}>
                    {v || ''}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
