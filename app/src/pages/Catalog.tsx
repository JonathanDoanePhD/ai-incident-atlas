import { useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import FilterPanel from '../components/FilterPanel';
import { useApp } from '../state';
import { matches } from '../lib/filters';
import { search } from '../lib/search';
import type { IncidentNode } from '../lib/types';

type Sort = 'relevance' | 'newest' | 'oldest' | 'severity' | 'reports';
const SEV_LABEL = ['none', 'minor', 'moderate', 'severe', 'critical'];
const PAGE = 48;

export default function CatalogPage() {
  const { data, filters, index, query, setQuery, termLabel, orgName } = useApp();
  const nodes = data!.nodes;
  const [mode, setMode] = useState<'cards' | 'table'>('cards');
  const [sort, setSort] = useState<Sort>('relevance');
  const [limit, setLimit] = useState(PAGE);
  const [compare, setCompare] = useState<number[]>([]);

  const results = useMemo(() => {
    const hits = index ? search(index, query) : null;
    const rank = hits ? new Map(hits.map((id, i) => [id, i])) : null;
    let rows = nodes.filter((n) => matches(n, filters) && (!rank || rank.has(n.id)));
    const by: Record<Sort, (a: IncidentNode, b: IncidentNode) => number> = {
      relevance: rank ? (a, b) => rank.get(a.id)! - rank.get(b.id)! : (a, b) => b.d.localeCompare(a.d),
      newest: (a, b) => b.d.localeCompare(a.d),
      oldest: (a, b) => a.d.localeCompare(b.d),
      severity: (a, b) => (b.sev ?? -1) - (a.sev ?? -1) || b.nrep - a.nrep,
      reports: (a, b) => b.nrep - a.nrep,
    };
    rows = [...rows].sort(by[sort]);
    return rows;
  }, [nodes, filters, index, query, sort]);

  const toggleCompare = (id: number) =>
    setCompare((c) => (c.includes(id) ? c.filter((x) => x !== id) : c.length >= 3 ? [...c.slice(1), id] : [...c, id]));

  return (
    <div className="catalog">
      <aside className="catalog-filters" aria-label="Catalog filters">
        <FilterPanel nodes={nodes} />
      </aside>
      <section className="catalog-main">
        <div className="catalog-bar">
          <label className="search-big">
            <span className="sr-only">Search incidents</span>
            <input type="search" placeholder="Search titles, organizations, summaries…" value={query}
              onChange={(e) => { setQuery(e.target.value); setLimit(PAGE); }} />
          </label>
          <label className="field inline">
            <span>Sort</span>
            <select value={sort} onChange={(e) => setSort(e.target.value as Sort)}>
              <option value="relevance">{query ? 'Relevance' : 'Relevance (newest)'}</option>
              <option value="newest">Newest</option>
              <option value="oldest">Oldest</option>
              <option value="severity">Severity</option>
              <option value="reports">Most reported</option>
            </select>
          </label>
          <div className="seg" role="group" aria-label="View mode">
            <button type="button" aria-pressed={mode === 'cards'} onClick={() => setMode('cards')}>Cards</button>
            <button type="button" aria-pressed={mode === 'table'} onClick={() => setMode('table')}>Table</button>
          </div>
        </div>
        <p className="muted" aria-live="polite">{results.length.toLocaleString()} incidents</p>

        {compare.length > 0 && (
          <CompareTray ids={compare} onRemove={toggleCompare} />
        )}

        {mode === 'cards' ? (
          <div className="cards">
            {results.slice(0, limit).map((n) => (
              <article className="card" key={n.id}>
                <div className="hc-year">
                  {n.d} · {n.nrep} report{n.nrep === 1 ? '' : 's'}
                  {n.sev !== null && <> · <span className={`sev sev${n.sev}`}>severity {n.sev}</span></>}
                </div>
                <h3><Link to={`/incident/${n.id}`}>{n.t}</Link></h3>
                <p>{n.s.length > 240 ? n.s.slice(0, 240) + '…' : n.s}</p>
                <div className="chip-row">
                  {n.tech.slice(0, 2).map((t) => <span className="chip" key={t}>{termLabel('technology', t)}</span>)}
                  {n.pfm && <span className="chip">{termLabel('failure_mode', n.pfm)}</span>}
                  {n.sec.slice(0, 1).map((t) => <span className="chip" key={t}>{termLabel('sector', t)}</span>)}
                </div>
                <label className="check small">
                  <input type="checkbox" checked={compare.includes(n.id)} onChange={() => toggleCompare(n.id)} /> Compare
                </label>
              </article>
            ))}
          </div>
        ) : (
          <div className="table-wrap">
            <table className="data">
              <thead>
                <tr>
                  <th scope="col">Compare</th><th scope="col">Date</th><th scope="col">Incident</th><th scope="col">Technology</th>
                  <th scope="col">Failure mode</th><th scope="col">Severity</th><th scope="col">Reports</th><th scope="col">Organizations</th>
                </tr>
              </thead>
              <tbody>
                {results.slice(0, limit).map((n) => (
                  <tr key={n.id}>
                    <td><input type="checkbox" aria-label={`Compare incident ${n.id}`} checked={compare.includes(n.id)} onChange={() => toggleCompare(n.id)} /></td>
                    <td className="nowrap">{n.d}</td>
                    <td><Link to={`/incident/${n.id}`}>{n.t}</Link></td>
                    <td>{n.tech.map((t) => termLabel('technology', t)).join(', ') || '–'}</td>
                    <td>{n.pfm ? termLabel('failure_mode', n.pfm) : '–'}</td>
                    <td>{n.sev !== null ? `${n.sev} ${SEV_LABEL[n.sev]}` : '–'}</td>
                    <td className="num">{n.nrep}</td>
                    <td>{n.org.slice(0, 3).map(orgName).join(', ') || '–'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {results.length > limit && (
          <button type="button" className="btn more" onClick={() => setLimit((l) => l + PAGE)}>
            Show more ({results.length - limit} remaining)
          </button>
        )}
      </section>
    </div>
  );
}

function CompareTray({ ids, onRemove }: { ids: number[]; onRemove: (id: number) => void }) {
  const { data, termLabel, orgName } = useApp();
  const rows: [string, (n: IncidentNode) => string][] = [
    ['Date', (n) => n.d],
    ['Summary', (n) => n.s],
    ['Sector', (n) => n.sec.map((t) => termLabel('sector', t)).join(', ') || '–'],
    ['Technology', (n) => n.tech.map((t) => termLabel('technology', t)).join(', ') || '–'],
    ['Failure modes', (n) => n.fm.map((t) => termLabel('failure_mode', t)).join(', ') || '–'],
    ['Harm', (n) => n.harm.map((t) => termLabel('harm_type', t)).join(', ') || '–'],
    ['Severity', (n) => (n.sev !== null ? `${n.sev} (${SEV_LABEL[n.sev]})` : '–')],
    ['Risk domain', (n) => (n.rd ? `${n.rd}. ${termLabel('risk_domain', n.rd)}` : '–')],
    ['Organizations', (n) => n.org.map(orgName).join(', ') || '–'],
    ['Reports', (n) => String(n.nrep)],
  ];
  const ns = ids.map((i) => data!.byId.get(i)!).filter(Boolean);
  return (
    <section className="compare" aria-label="Side-by-side comparison">
      <h2>Compare ({ns.length}/3)</h2>
      <div className="table-wrap">
        <table className="data compare-table">
          <thead>
            <tr>
              <th scope="col" />
              {ns.map((n) => (
                <th scope="col" key={n.id}>
                  <Link to={`/incident/${n.id}`}>{n.t}</Link>{' '}
                  <button type="button" className="link" aria-label={`Remove ${n.t} from comparison`} onClick={() => onRemove(n.id)}>×</button>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map(([label, f]) => (
              <tr key={label}>
                <th scope="row">{label}</th>
                {ns.map((n) => <td key={n.id}>{f(n)}</td>)}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
