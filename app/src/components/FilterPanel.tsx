import { useState } from 'react';
import { useApp } from '../state';
import { FACETS, facetCounts, toggleFacet, type FacetKey } from '../lib/filters';
import type { IncidentNode } from '../lib/types';

interface RangeProps {
  label: string;
  min: number;
  max: number;
  value: [number, number];
  onChange: (v: [number, number]) => void;
  format?: (v: number) => string;
}

/** One track, two handles (same component style as the AI Project Atlas). */
export function RangeSlider({ label, min, max, value, onChange, format = String }: RangeProps) {
  const id = label.replace(/\W+/g, '-').toLowerCase();
  const pct = (v: number) => `${((v - min) / Math.max(1, max - min)) * 100}%`;
  return (
    <fieldset className="range">
      <legend>{label}</legend>
      <div className="range-vals"><span>{format(value[0])}</span><span>{format(value[1])}</span></div>
      <div className="dual" style={{ ['--lo' as string]: pct(value[0]), ['--hi' as string]: pct(value[1]) }}>
        <label className="sr-only" htmlFor={`${id}-lo`}>{label} minimum</label>
        <input id={`${id}-lo`} type="range" min={min} max={max} value={value[0]}
          onChange={(e) => onChange([Math.min(Number(e.target.value), value[1]), value[1]])} />
        <label className="sr-only" htmlFor={`${id}-hi`}>{label} maximum</label>
        <input id={`${id}-hi`} type="range" min={min} max={max} value={value[1]}
          onChange={(e) => onChange([value[0], Math.max(Number(e.target.value), value[0])])} />
      </div>
    </fieldset>
  );
}

const SEV_LABEL = ['none', 'minor', 'moderate', 'severe', 'critical'];

export default function FilterPanel({ nodes }: { nodes: IncidentNode[] }) {
  const { filters, setFilters, yearBounds, termLabel, data, resetFilters } = useApp();
  const [open, setOpen] = useState<Record<string, boolean>>({});
  const maxRep = Math.max(...nodes.map((n) => n.nrep));
  return (
    <div className="filters">
      <div className="filters-head">
        <h2>Filters</h2>
        <button type="button" className="link" onClick={resetFilters}>
          Reset
        </button>
      </div>
      <RangeSlider label="Incident year" min={yearBounds[0]} max={yearBounds[1]} value={filters.years}
        onChange={(years) => setFilters((f) => ({ ...f, years }))} />
      <RangeSlider label="Severity" min={0} max={4} value={filters.severity} format={(v) => `${v} ${SEV_LABEL[v]}`}
        onChange={(severity) => setFilters((f) => ({ ...f, severity }))} />
      <label className="check">
        <input type="checkbox" checked={filters.includeUnknownSeverity}
          onChange={(e) => setFilters((f) => ({ ...f, includeUnknownSeverity: e.target.checked }))} />
        Include incidents without a coded severity
      </label>
      <label className="check">
        <input type="checkbox" checked={filters.includePredicted}
          onChange={(e) => setFilters((f) => ({ ...f, includePredicted: e.target.checked }))} />
        Use predicted tags for {data?.meta.n_predicted ?? 0} incidents not yet coded
      </label>
      <fieldset className="range">
        <legend>Minimum reports</legend>
        <div className="range-vals"><span>{filters.minReports}</span><span>{Math.min(maxRep, 30)}</span></div>
        <input aria-label="Minimum number of reports" type="range" min={0} max={Math.min(maxRep, 30)} value={filters.minReports}
          onChange={(e) => setFilters((f) => ({ ...f, minReports: Number(e.target.value) }))} />
      </fieldset>
      {filters.cluster !== null && (
        <p className="chip-row">
          <span className="chip active">
            Cluster: {data?.clusters.clusters.find((c) => c.cluster === filters.cluster)?.name}
            <button type="button" aria-label="Remove cluster filter" onClick={() => setFilters((f) => ({ ...f, cluster: null }))}>
              ×
            </button>
          </span>
        </p>
      )}
      {filters.org !== null && (
        <p className="chip-row">
          <span className="chip active">
            Organization: {data?.entities[filters.org]?.name}
            <button type="button" aria-label="Remove organization filter" onClick={() => setFilters((f) => ({ ...f, org: null }))}>
              ×
            </button>
          </span>
        </p>
      )}
      {(Object.keys(FACETS) as FacetKey[]).map((key) => {
        const counts = facetCounts(nodes, key);
        const sel = filters.facets[key] ?? [];
        const expanded = open[key];
        // Selected values always stay visible even when collapsed.
        const shown = expanded ? counts : [...counts.slice(0, 3), ...counts.slice(3).filter(([v]) => sel.includes(v))];
        const dim = FACETS[key].dim;
        return (
          <fieldset key={key} className="facet">
            <legend>{FACETS[key].label}</legend>
            {shown.map(([v, c]) => (
              <label key={v} className="check">
                <input type="checkbox" checked={sel.includes(v)} onChange={() => setFilters((f) => toggleFacet(f, key, v))} />
                <span className="facet-label">{key === 'rd' ? `${v}. ${termLabel(dim, v)}` : termLabel(dim, v)}</span>
                <span className="count">{c}</span>
              </label>
            ))}
            {counts.length > 3 && (
              <button type="button" className="link" aria-expanded={!!expanded}
                onClick={() => setOpen((o) => ({ ...o, [key]: !o[key] }))}>
                {expanded ? 'Show fewer' : `+${counts.length - 3} more`}
              </button>
            )}
          </fieldset>
        );
      })}
    </div>
  );
}
