import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import Constellation, { hasWebGL, type GLink } from '../components/Constellation';
import FilterPanel from '../components/FilterPanel';
import { useApp } from '../state';
import { loadEdges } from '../lib/data';
import { activeFilterCount, matches } from '../lib/filters';
import { search } from '../lib/search';
import {
  buildEncoder, COLOR_OPTIONS, minMax, PRESETS, scaleTo, SIZE_OPTIONS, sizeValue, VIEW_OPTIONS,
  type ColorBy, type SizeBy, type View,
} from '../lib/style';
import type { EdgeBundle, IncidentNode } from '../lib/types';

const SEV_LABEL = ['none', 'minor', 'moderate', 'severe', 'critical'];

export default function ExplorePage() {
  const { data, filters, setFilters, yearBounds, termLabel, orgName, index, query, setQuery } = useApp();
  const nodes = data!.nodes;
  const meta = data!.meta;
  const [preset, setPreset] = useState('clusters');
  const [colorBy, setColorBy] = useState<ColorBy>('cluster');
  const [sizeBy, setSizeBy] = useState<SizeBy>('nrep');
  const [view, setView] = useState<View>('blend');
  const [edges, setEdges] = useState<EdgeBundle | null>(null);
  const [hover, setHover] = useState<IncidentNode | null>(null);
  const [selected, setSelected] = useState<IncidentNode | null>(null);
  const [legendFocus, setLegendFocus] = useState<string | null>(null);
  const [focusId, setFocusId] = useState<number | null>(null);
  const [playing, setPlaying] = useState(false);
  const [panelOpen, setPanelOpen] = useState(false);
  const [mouse, setMouse] = useState<[number, number]>([0, 0]);
  const webgl = useMemo(hasWebGL, []);
  const stage = useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadEdges().then(setEdges);
  }, []);

  const applyPreset = (id: string) => {
    const p = PRESETS.find((x) => x.id === id)!;
    setPreset(id);
    setColorBy(p.color);
    setSizeBy(p.size);
    setView(p.view);
    setLegendFocus(null);
  };

  const clusterNames = useMemo(() => new Map(data!.clusters.clusters.map((c) => [c.cluster, c.name])), [data]);
  const encoder = useMemo(() => buildEncoder(colorBy, meta, nodes, clusterNames), [colorBy, meta, nodes, clusterNames]);

  // Links for the current view (the only thing that triggers a data re-join).
  const links = useMemo<GLink[]>(() => {
    if (!edges || view === 'none') return [];
    return (edges.views[view] ?? []).map(([s, t, w, why]) => ({ source: s, target: t, w, why }));
  }, [edges, view]);

  const degree = useMemo(() => {
    const d = new Map<number, number>();
    for (const l of links) {
      const s = l.source as number;
      const t = l.target as number;
      d.set(s, (d.get(s) ?? 0) + 1);
      d.set(t, (d.get(t) ?? 0) + 1);
    }
    return d;
  }, [links]);

  const neighbors = useMemo(() => {
    const m = new Map<number, { id: number; w: number; why: number }[]>();
    for (const l of links) {
      const s = l.source as number;
      const t = l.target as number;
      if (!m.has(s)) m.set(s, []);
      if (!m.has(t)) m.set(t, []);
      m.get(s)!.push({ id: t, w: l.w, why: l.why });
      m.get(t)!.push({ id: s, w: l.w, why: l.why });
    }
    return m;
  }, [links]);

  // Size: min–max scaled between fixed bounds, over all nodes (stable while filtering).
  const sizeOf = useMemo(() => {
    const vals = nodes.map((n) => sizeValue(sizeBy, n, degree));
    const mm = minMax(vals);
    const cache = new Map(nodes.map((n, i) => [n.id, scaleTo(vals[i], mm)]));
    return (n: IncidentNode) => cache.get(n.id) ?? 2;
  }, [sizeBy, nodes, degree]);

  const searchHits = useMemo(() => (index ? search(index, query) : null), [index, query]);
  const visible = useMemo(() => {
    const hit = searchHits ? new Set(searchHits) : null;
    return new Set(nodes.filter((n) => matches(n, filters) && (!hit || hit.has(n.id))).map((n) => n.id));
  }, [nodes, filters, searchHits]);

  const highlight = useMemo(() => {
    if (selected) return new Set([selected.id, ...(neighbors.get(selected.id) ?? []).map((x) => x.id)]);
    if (legendFocus) return new Set(nodes.filter((n) => encoder.valueOf(n) === legendFocus).map((n) => n.id));
    return new Set<number>();
  }, [selected, neighbors, legendFocus, nodes, encoder]);

  const colorOf = encoder.color;

  // Year playback: animate the upper bound of the year range.
  useEffect(() => {
    if (!playing) return;
    const start = Math.max(yearBounds[0], 2010);
    setFilters((f) => ({ ...f, years: [yearBounds[0], start] }));
    const id = window.setInterval(() => {
      setFilters((f) => {
        if (f.years[1] >= yearBounds[1]) {
          setPlaying(false);
          return f;
        }
        return { ...f, years: [f.years[0], f.years[1] + 1] };
      });
    }, 900);
    return () => window.clearInterval(id);
  }, [playing, yearBounds, setFilters]);

  const onSelect = useCallback((n: IncidentNode | null) => setSelected(n), []);
  const onHover = useCallback((n: IncidentNode | null) => setHover(n), []);

  const legendClick = (key: string) => {
    if (colorBy === 'cluster' && !key.startsWith('__')) {
      setFilters((f) => ({ ...f, cluster: f.cluster === Number(key) ? null : Number(key) }));
      return;
    }
    setLegendFocus((k) => (k === key ? null : key));
  };

  const currentPreset = PRESETS.find((p) => p.id === preset);
  const nActive = activeFilterCount(filters, yearBounds[0], yearBounds[1]);
  const sel = selected;

  return (
    <div className="explore">
      <aside className={`panel ${panelOpen ? 'open' : ''}`} aria-label="Constellation controls">
        <button type="button" className="panel-toggle" aria-expanded={panelOpen} onClick={() => setPanelOpen((o) => !o)}>
          {panelOpen ? 'Hide controls' : `Controls${nActive ? ` · ${nActive} filter${nActive > 1 ? 's' : ''}` : ''}`}
        </button>
        <div className="panel-body">
          <label className="field">
            <span>Preset view</span>
            <select value={preset} onChange={(e) => applyPreset(e.target.value)}>
              {PRESETS.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.label}
                </option>
              ))}
              {!currentPreset && <option value="custom">Custom</option>}
            </select>
          </label>
          {currentPreset && <p className="blurb">{currentPreset.blurb}</p>}
          <label className="field">
            <span>Color by</span>
            <select value={colorBy} onChange={(e) => { setColorBy(e.target.value as ColorBy); setPreset('custom'); setLegendFocus(null); }}>
              {COLOR_OPTIONS.map(([v, l]) => <option key={v} value={v}>{l}</option>)}
            </select>
          </label>
          <label className="field">
            <span>Size by</span>
            <select value={sizeBy} onChange={(e) => { setSizeBy(e.target.value as SizeBy); setPreset('custom'); }}>
              {SIZE_OPTIONS.map(([v, l]) => <option key={v} value={v}>{l}</option>)}
            </select>
          </label>
          <label className="field">
            <span>Connections</span>
            <select value={view} onChange={(e) => { setView(e.target.value as View); setPreset('custom'); setSelected(null); }}>
              {VIEW_OPTIONS.map(([v, l]) => <option key={v} value={v}>{l}</option>)}
            </select>
          </label>
          <label className="field">
            <span>Search</span>
            <input type="search" placeholder="e.g. facial recognition police" value={query} onChange={(e) => setQuery(e.target.value)} />
          </label>
          <FilterPanel nodes={nodes} />
        </div>
      </aside>

      <section className="stage" ref={stage} aria-label="Incident constellation"
        onMouseMove={(e) => {
          const r = stage.current?.getBoundingClientRect();
          if (r) setMouse([e.clientX - r.left, e.clientY - r.top]);
        }}>
        {webgl ? (
          <Constellation nodes={nodes} links={links} colorOf={colorOf} sizeOf={sizeOf} visible={visible}
            selected={sel?.id ?? null} highlight={highlight} onHover={onHover} onSelect={onSelect} focusId={focusId} />
        ) : (
          <ListFallback nodes={nodes.filter((n) => visible.has(n.id))} />
        )}

        <div className="hud-top">
          <span className="count-pill" aria-live="polite">
            {visible.size.toLocaleString()} of {nodes.length.toLocaleString()} incidents
          </span>
          {webgl && <span className="hint">Drag to rotate · scroll to zoom · right-drag to pan · click a star</span>}
        </div>

        <div className="legend" role="group" aria-label="Color legend">
          <div className="legend-title">{COLOR_OPTIONS.find(([v]) => v === colorBy)?.[1]}</div>
          {encoder.legend.map((it) => (
            <button type="button" key={it.key} className={`legend-item ${legendFocus === it.key || (colorBy === 'cluster' && filters.cluster === Number(it.key)) ? 'on' : ''}`}
              onClick={() => legendClick(it.key)} title={colorBy === 'cluster' ? 'Isolate this cluster' : 'Highlight'}>
              <span className="swatch" style={{ background: it.color }} />
              {it.label}
            </button>
          ))}
        </div>

        <div className="timeline">
          <button type="button" className="btn" onClick={() => setPlaying((p) => !p)} aria-pressed={playing}>
            {playing ? '❚❚ Pause' : '▶ Play years'}
          </button>
          <label className="sr-only" htmlFor="year-upper">Show incidents up to year</label>
          <input id="year-upper" type="range" min={yearBounds[0]} max={yearBounds[1]} value={filters.years[1]}
            onChange={(e) => setFilters((f) => ({ ...f, years: [f.years[0], Math.max(Number(e.target.value), f.years[0])] }))} />
          <span className="year-label">≤ {filters.years[1]}</span>
        </div>

        {hover && !sel && (
          <div className="hovercard" style={{ left: Math.min(mouse[0] + 16, (stage.current?.clientWidth ?? 800) - 330), top: Math.max(mouse[1] - 10, 50) }}>
            <div className="hc-year">{hover.d} · {hover.nrep} report{hover.nrep === 1 ? '' : 's'}{hover.sev !== null ? ` · severity ${hover.sev} (${SEV_LABEL[hover.sev]})` : ''}</div>
            <div className="hc-title">{hover.t}</div>
            <p>{hover.s.length > 220 ? hover.s.slice(0, 220) + '…' : hover.s}</p>
            <div className="chip-row">
              {hover.tech.slice(0, 2).map((t) => <span className="chip" key={t}>{termLabel('technology', t)}</span>)}
              {hover.pfm && <span className="chip">{termLabel('failure_mode', hover.pfm)}</span>}
            </div>
          </div>
        )}

        {sel && (
          <aside className="selection" aria-label="Selected incident">
            <button type="button" className="close" aria-label="Close" onClick={() => setSelected(null)}>×</button>
            <div className="hc-year">#{sel.id} · {sel.d}</div>
            <h2>{sel.t}</h2>
            <p>{sel.s}</p>
            <div className="chip-row">
              {sel.sec.map((t) => <span className="chip" key={t}>{termLabel('sector', t)}</span>)}
              {sel.tech.map((t) => <span className="chip" key={t}>{termLabel('technology', t)}</span>)}
              {sel.fm.map((t) => <span className="chip" key={t}>{termLabel('failure_mode', t)}</span>)}
            </div>
            {sel.org.length > 0 && (
              <p className="muted small">Organizations: {sel.org.slice(0, 5).map(orgName).join(', ')}</p>
            )}
            <div className="row">
              <Link className="btn primary" to={`/incident/${sel.id}`}>Open profile</Link>
              <button type="button" className="btn" onClick={() => setFocusId(sel.id)}>Fly to</button>
            </div>
            <h3>Connected in this view ({(neighbors.get(sel.id) ?? []).length})</h3>
            <ul className="neighbors">
              {(neighbors.get(sel.id) ?? [])
                .sort((a, b) => b.w - a.w)
                .slice(0, 8)
                .map((nb) => {
                  const n = data!.byId.get(nb.id);
                  return n ? (
                    <li key={nb.id}>
                      <button type="button" className="link" onClick={() => { setSelected(n); setFocusId(n.id); }}>
                        {n.t}
                      </button>
                      <span className="why">{edges?.explanations[nb.why]}</span>
                    </li>
                  ) : null;
                })}
            </ul>
          </aside>
        )}
      </section>
    </div>
  );
}

function ListFallback({ nodes }: { nodes: IncidentNode[] }) {
  return (
    <div className="fallback">
      <p role="note">3-D view unavailable (WebGL is disabled or unsupported). Showing a list instead.</p>
      <ul>
        {nodes.slice(0, 300).map((n) => (
          <li key={n.id}>
            <Link to={`/incident/${n.id}`}>{n.t}</Link> <span className="muted">({n.y})</span>
          </li>
        ))}
      </ul>
      {nodes.length > 300 && <p className="muted">Showing 300 of {nodes.length}. Use the Catalog for the full list.</p>}
    </div>
  );
}
