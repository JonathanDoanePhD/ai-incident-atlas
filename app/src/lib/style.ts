import type { IncidentNode, Meta } from './types';

/**
 * Validated categorical palette (dark-surface steps of the reference 8-slot palette, fixed order).
 * Dimensions with more than 7 terms show the 7 most frequent terms in colour and fold the rest into "Other".
 * Frequency rank is computed ONCE on the full dataset so colours never repaint when filters change.
 */
export const CATEGORICAL = ['#3987e5', '#d95926', '#199e70', '#c98500', '#d55181', '#008300', '#9085e9', '#e66767'];
export const OTHER = '#8a8f98';
export const UNKNOWN = '#4b5058';
/** Sequential blue ramp, dark → light (low values recede into the dark surface). */
export const SEQ = ['#184f95', '#256abf', '#3987e5', '#6da7ec', '#9ec5f4', '#cde2fb'];
export const SIZE_BOUNDS: [number, number] = [1.5, 14];

export type ColorBy = 'cluster' | 'rd' | 'pfm' | 'tech' | 'sector' | 'harm' | 'sev' | 'year' | 'era' | 'cause';
export type SizeBy = 'uniform' | 'nrep' | 'sev' | 'degree' | 'orgs';
export type View = 'blend' | 'semantic' | 'failure' | 'technology' | 'sector' | 'harm' | 'entity' | 'none';

export const COLOR_OPTIONS: [ColorBy, string][] = [
  ['cluster', 'Cluster'],
  ['rd', 'Risk domain (MIT)'],
  ['pfm', 'Primary failure mode'],
  ['tech', 'Technology'],
  ['sector', 'Sector group'],
  ['harm', 'Harm type'],
  ['sev', 'Severity'],
  ['year', 'Year'],
  ['era', 'Before / after ChatGPT'],
  ['cause', 'Primary cause'],
];
export const SIZE_OPTIONS: [SizeBy, string][] = [
  ['nrep', 'Number of reports (media attention)'],
  ['sev', 'Severity'],
  ['degree', 'Connections in view'],
  ['orgs', 'Named organizations'],
  ['uniform', 'Uniform'],
];
export const VIEW_OPTIONS: [View, string][] = [
  ['blend', 'Blended similarity'],
  ['semantic', 'Semantic (text embeddings)'],
  ['failure', 'Shared failure mode'],
  ['technology', 'Shared technology'],
  ['sector', 'Shared sector'],
  ['harm', 'Shared harm'],
  ['entity', 'Same developer / deployer'],
  ['none', 'No connections'],
];

export interface Preset {
  id: string;
  label: string;
  blurb: string;
  color: ColorBy;
  size: SizeBy;
  view: View;
}

export const PRESETS: Preset[] = [
  { id: 'clusters', label: 'Overview: risk landscape', blurb: 'Nearby stars are similar incidents (text + taxonomy). Colour shows the MIT risk domain; links show the closest overall matches. Switch “Color by” to Cluster to isolate a cluster.', color: 'rd', size: 'nrep', view: 'blend' },
  { id: 'failures', label: 'Recurring failure modes', blurb: 'Colour shows the central failure mechanism; links join incidents that fail the same way — often across very different sectors.', color: 'pfm', size: 'degree', view: 'failure' },
  { id: 'actors', label: 'Who builds and deploys', blurb: 'Links join incidents involving the same named developer or deployer; larger nodes name more organizations.', color: 'tech', size: 'orgs', view: 'entity' },
  { id: 'harms', label: 'Harm landscape', blurb: 'Colour shows the type of harm, size its severity; links join incidents with the same kinds of harm.', color: 'harm', size: 'sev', view: 'harm' },
  { id: 'genai', label: 'Generative-AI era', blurb: 'Incidents before and after the public release of ChatGPT (30 Nov 2022), linked by meaning. Use the year slider to replay.', color: 'era', size: 'sev', view: 'semantic' },
];

export interface LegendItem {
  key: string;
  label: string;
  color: string;
}

export interface Encoder {
  color: (n: IncidentNode) => string;
  legend: LegendItem[];
  valueOf: (n: IncidentNode) => string | null;
}

function firstOrNull(xs: string[]): string | null {
  return xs.length ? xs[0] : null;
}

/** Category extractor per colour mode (one category per node, used for colour & legend). */
export function categoryOf(mode: ColorBy, meta: Meta): (n: IncidentNode) => string | null {
  const sectorParent = new Map(meta.dimensions.sector.terms.map((t) => [t.id, t.parent ?? t.id]));
  switch (mode) {
    case 'cluster':
      return (n) => (n.cl >= 0 ? String(n.cl) : null);
    case 'rd':
      return (n) => n.rd;
    case 'pfm':
      return (n) => n.pfm ?? firstOrNull(n.fm);
    case 'tech':
      return (n) => firstOrNull(n.tech);
    case 'sector':
      return (n) => (n.sec.length ? sectorParent.get(n.sec[0]) ?? n.sec[0] : null);
    case 'harm':
      return (n) => firstOrNull(n.harm.filter((h) => h !== 'no_harm_near_miss')) ?? firstOrNull(n.harm);
    case 'era':
      return (n) => (n.d >= '2022-11-30' ? 'post' : 'pre');
    case 'cause':
      return (n) => n.cause;
    default:
      return () => null;
  }
}

export function minMax(values: number[]): [number, number] {
  let lo = Infinity;
  let hi = -Infinity;
  for (const v of values) {
    if (v < lo) lo = v;
    if (v > hi) hi = v;
  }
  return lo === Infinity ? [0, 1] : [lo, hi];
}

/** Min–max scale to fixed bounds; constant inputs map to the midpoint. */
export function scaleTo(v: number, [lo, hi]: [number, number], [a, b]: [number, number] = SIZE_BOUNDS): number {
  if (hi <= lo) return (a + b) / 2;
  return a + ((v - lo) / (hi - lo)) * (b - a);
}

export function seqColor(t: number): string {
  const i = Math.max(0, Math.min(SEQ.length - 1, Math.round(t * (SEQ.length - 1))));
  return SEQ[i];
}

export function buildEncoder(
  mode: ColorBy,
  meta: Meta,
  allNodes: IncidentNode[],
  clusterNames: Map<number, string>,
): Encoder {
  if (mode === 'sev') {
    const legend = ['0 none', '1 minor', '2 moderate', '3 severe', '4 critical'].map((l, i) => ({
      key: String(i),
      label: l,
      color: seqColor(i / 4),
    }));
    legend.push({ key: 'unknown', label: 'not coded', color: UNKNOWN });
    return {
      color: (n) => (n.sev === null ? UNKNOWN : seqColor(n.sev / 4)),
      legend,
      valueOf: (n) => (n.sev === null ? null : String(n.sev)),
    };
  }
  if (mode === 'year') {
    const [lo, hi] = [2012, Math.max(...allNodes.map((n) => n.y))];
    const ticks = [2012, 2016, 2020, 2023, hi];
    return {
      color: (n) => seqColor((Math.max(n.y, lo) - lo) / (hi - lo)),
      legend: ticks.map((y) => ({ key: String(y), label: y === lo ? `≤ ${y}` : String(y), color: seqColor((y - lo) / (hi - lo)) })),
      valueOf: (n) => String(n.y),
    };
  }
  const cat = categoryOf(mode, meta);
  const labelOf = (key: string): string => {
    if (mode === 'cluster') return clusterNames.get(Number(key)) ?? `Cluster ${key}`;
    if (mode === 'era') return key === 'post' ? 'After ChatGPT (≥ 30 Nov 2022)' : 'Before ChatGPT';
    if (mode === 'cause') return { ai: 'AI system', human: 'Human', other: 'Other / unclear' }[key] ?? key;
    const dim = { rd: 'risk_domain', pfm: 'failure_mode', tech: 'technology', harm: 'harm_type', sector: 'sector' }[mode as string];
    if (mode === 'sector') return meta.dimensions.sector.parents?.[key] ?? meta.dimensions.sector.terms.find((t) => t.id === key)?.label ?? key;
    const term = dim ? meta.dimensions[dim]?.terms.find((t) => t.id === key) : undefined;
    return term ? (mode === 'rd' ? `${key}. ${term.label}` : term.label) : key;
  };
  // Rank categories by frequency on the FULL dataset (stable colours under filtering).
  const counts = new Map<string, number>();
  for (const n of allNodes) {
    const c = cat(n);
    if (c !== null) counts.set(c, (counts.get(c) ?? 0) + 1);
  }
  let ranked = [...counts.entries()].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0])).map(([k]) => k);
  if (mode === 'rd') ranked = [...counts.keys()].sort();
  if (mode === 'era') ranked = ['pre', 'post'];
  const colored = ranked.length > CATEGORICAL.length ? ranked.slice(0, CATEGORICAL.length - 1) : ranked;
  const colorMap = new Map(colored.map((k, i) => [k, CATEGORICAL[i]]));
  const legend: LegendItem[] = colored.map((k) => ({ key: k, label: labelOf(k), color: colorMap.get(k)! }));
  if (ranked.length > colored.length) legend.push({ key: '__other', label: `Other (${ranked.length - colored.length} more)`, color: OTHER });
  legend.push({ key: '__unknown', label: 'Not coded / unknown', color: UNKNOWN });
  return {
    color: (n) => {
      const c = cat(n);
      if (c === null) return UNKNOWN;
      return colorMap.get(c) ?? OTHER;
    },
    legend,
    valueOf: (n) => {
      const c = cat(n);
      if (c === null) return '__unknown';
      return colorMap.has(c) ? c : '__other';
    },
  };
}

export function sizeValue(mode: SizeBy, n: IncidentNode, degree: Map<number, number>): number {
  switch (mode) {
    case 'nrep':
      return Math.log1p(n.nrep);
    case 'sev':
      return n.sev ?? 0;
    case 'degree':
      return degree.get(n.id) ?? 0;
    case 'orgs':
      return n.org.length;
    default:
      return 1;
  }
}
