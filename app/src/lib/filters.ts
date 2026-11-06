import type { IncidentNode } from './types';

/** Category facets that can be filtered (multi-select, OR within a facet, AND across facets). */
export const FACETS = {
  rd: { dim: 'risk_domain', label: 'Risk domain' },
  sec: { dim: 'sector', label: 'Sector' },
  tech: { dim: 'technology', label: 'Technology' },
  fm: { dim: 'failure_mode', label: 'Failure mode' },
  harm: { dim: 'harm_type', label: 'Harm type' },
  pop: { dim: 'affected_population', label: 'Affected population' },
} as const;

export type FacetKey = keyof typeof FACETS;

export interface Filters {
  years: [number, number];
  severity: [number, number];
  minReports: number;
  includeUnknownSeverity: boolean;
  facets: Partial<Record<FacetKey, string[]>>;
  cluster: number | null;
  org: string | null;
}

export function defaultFilters(minYear: number, maxYear: number): Filters {
  return {
    years: [minYear, maxYear],
    severity: [0, 4],
    minReports: 0,
    includeUnknownSeverity: true,
    facets: {},
    cluster: null,
    org: null,
  };
}

export function facetValues(n: IncidentNode, key: FacetKey): string[] {
  if (key === 'rd') return n.rd ? [n.rd] : [];
  return n[key];
}

/** Pure predicate: does node `n` pass filters `f`? */
export function matches(n: IncidentNode, f: Filters): boolean {
  if (n.y < f.years[0] || n.y > f.years[1]) return false;
  if (n.sev === null) {
    if (!f.includeUnknownSeverity) return false;
  } else if (n.sev < f.severity[0] || n.sev > f.severity[1]) return false;
  if (n.nrep < f.minReports) return false;
  if (f.cluster !== null && n.cl !== f.cluster) return false;
  if (f.org !== null && !n.org.includes(f.org)) return false;
  for (const key of Object.keys(f.facets) as FacetKey[]) {
    const sel = f.facets[key];
    if (!sel || sel.length === 0) continue;
    const vals = facetValues(n, key);
    if (!sel.some((s) => vals.includes(s))) return false;
  }
  return true;
}

export function toggleFacet(f: Filters, key: FacetKey, value: string): Filters {
  const cur = f.facets[key] ?? [];
  const next = cur.includes(value) ? cur.filter((v) => v !== value) : [...cur, value];
  return { ...f, facets: { ...f.facets, [key]: next } };
}

/** Count values of a facet across nodes, sorted by count desc then id; skips empty values. */
export function facetCounts(nodes: IncidentNode[], key: FacetKey): [string, number][] {
  const c = new Map<string, number>();
  for (const n of nodes) for (const v of facetValues(n, key)) if (v) c.set(v, (c.get(v) ?? 0) + 1);
  return [...c.entries()].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]));
}

export function activeFilterCount(f: Filters, minYear: number, maxYear: number): number {
  let k = 0;
  if (f.years[0] !== minYear || f.years[1] !== maxYear) k++;
  if (f.severity[0] !== 0 || f.severity[1] !== 4 || !f.includeUnknownSeverity) k++;
  if (f.minReports > 0) k++;
  if (f.cluster !== null) k++;
  if (f.org !== null) k++;
  for (const v of Object.values(f.facets)) if (v && v.length) k++;
  return k;
}
