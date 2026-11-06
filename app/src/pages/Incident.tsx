import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { useApp } from '../state';
import { loadProfile } from '../lib/data';
import type { Profile, TagOut } from '../lib/types';

const SEV_LABEL = ['No realized harm', 'Minor', 'Moderate', 'Severe', 'Critical'];
const DIM_ORDER: [string, string][] = [
  ['sector', 'Sector'],
  ['technology', 'Technology'],
  ['failure_mode', 'Failure mode'],
  ['harm_type', 'Harm type'],
  ['affected_population', 'Affected population'],
  ['lifecycle_stage', 'Lifecycle stage'],
];

function Evidence({ tag, dim }: { tag: TagOut; dim: string }) {
  const { termLabel } = useApp();
  return (
    <li className={`tag ev-${tag.ev}`}>
      <span className="tag-name">{termLabel(dim, tag.id)}</span>
      <span className={`ev-badge ${tag.ev}`} title={tag.ev === 'confirmed' ? 'Stated in a report (quote verified verbatim)' : 'Inferred from the evidence; not stated outright'}>
        {tag.ev}
      </span>
      {tag.q && (
        <blockquote>
          “{tag.q}”{' '}
          <cite>
            — {tag.url ? <a href={tag.url} target="_blank" rel="noopener noreferrer">{tag.src ?? 'source'}</a> : tag.src}
          </cite>
        </blockquote>
      )}
    </li>
  );
}

export default function IncidentPage() {
  const { id } = useParams();
  const iid = Number(id);
  const { data, termLabel } = useApp();
  const node = data!.byId.get(iid);
  const [prof, setProf] = useState<Profile | null | undefined>(undefined);

  useEffect(() => {
    setProf(undefined);
    loadProfile(iid).then((p) => setProf(p ?? null)).catch(() => setProf(null));
    window.scrollTo(0, 0);
  }, [iid]);

  if (!node) return <div className="page">Incident {id} not found. <Link to="/catalog">Back to the catalog</Link></div>;

  return (
    <article className="page profile">
      <p className="crumbs"><Link to="/catalog">Catalog</Link> / Incident {iid}</p>
      <h1>{node.t}</h1>
      <p className="meta-line">
        {node.d} · {node.nrep} report{node.nrep === 1 ? '' : 's'} ·{' '}
        <a href={`https://incidentdatabase.ai/cite/${iid}/`} target="_blank" rel="noopener noreferrer">AIID entry #{iid}</a>
      </p>
      {!node.x && <p className="notice">This incident has not been coded by the extraction pipeline yet; only AIID data is shown.</p>}

      <div className="profile-grid">
        <section>
          <h2>Summary</h2>
          <p className="lead">{node.s}</p>
          {prof?.technical_summary && (
            <>
              <h3>How it happened</h3>
              <p>{prof.technical_summary}</p>
            </>
          )}
          {prof?.description && (
            <details>
              <summary>AIID description</summary>
              <p>{prof.description}</p>
            </details>
          )}
          {prof?.tags && (
            <>
              <h2>Classification</h2>
              <p className="muted small">
                <span className="ev-badge confirmed">confirmed</span> tags quote a report verbatim (checked by code);{' '}
                <span className="ev-badge inferred">inferred</span> tags are a reasonable reading but not stated outright.
              </p>
              {DIM_ORDER.map(([dim, label]) =>
                prof.tags![dim]?.length ? (
                  <div key={dim} className="tag-group">
                    <h3>{label}</h3>
                    <ul className="tags">{prof.tags![dim].map((t) => <Evidence key={t.id} tag={t} dim={dim} />)}</ul>
                  </div>
                ) : null,
              )}
            </>
          )}
        </section>

        <aside>
          <div className="facts">
            {node.sev !== null && (
              <div className="fact">
                <span className="fact-label">Severity</span>
                <span className={`sev sev${node.sev}`}>{node.sev} — {SEV_LABEL[node.sev]}</span>
                {prof?.severity && <ul className="tags compact"><Evidence tag={prof.severity} dim="severity" /></ul>}
              </div>
            )}
            {node.rd && (
              <div className="fact">
                <span className="fact-label">Risk domain (MIT)</span>
                {node.rd}. {termLabel('risk_domain', node.rd)}
                {prof?.risk_subdomain && <div className="muted small">{prof.risk_subdomain} {termLabel('risk_subdomain', prof.risk_subdomain)}</div>}
              </div>
            )}
            {node.pfm && (
              <div className="fact"><span className="fact-label">Primary failure mode</span>{termLabel('failure_mode', node.pfm)}</div>
            )}
            {node.int && (
              <div className="fact"><span className="fact-label">Intent / cause</span>{node.int} · {node.cause === 'ai' ? 'AI system' : node.cause}</div>
            )}
            {prof?.systems && prof.systems.length > 0 && (
              <div className="fact"><span className="fact-label">Systems</span>{prof.systems.join(', ')}</div>
            )}
            {prof && prof.developers.length > 0 && (
              <div className="fact"><span className="fact-label">Developers (alleged)</span>{prof.developers.join(', ')}</div>
            )}
            {prof && prof.deployers.length > 0 && (
              <div className="fact"><span className="fact-label">Deployers (alleged)</span>{prof.deployers.join(', ')}</div>
            )}
            {prof && prof.harmed_groups.length > 0 && (
              <div className="fact"><span className="fact-label">Harmed or nearly harmed</span>{prof.harmed_groups.join(', ')}</div>
            )}
            {prof?.notes && <div className="fact"><span className="fact-label">Coder note</span><span className="muted">{prof.notes}</span></div>}
          </div>
        </aside>
      </div>

      {prof?.related && prof.related.length > 0 && (
        <section>
          <h2>Related incidents — and why</h2>
          <ul className="related">
            {prof.related.map((r) => {
              const n = data!.byId.get(r.id);
              return n ? (
                <li key={r.id}>
                  <Link to={`/incident/${r.id}`}>{n.t}</Link> <span className="muted">({n.y})</span>
                  <div className="why">{r.why}</div>
                </li>
              ) : null;
            })}
          </ul>
        </section>
      )}

      {prof && (
        <section>
          <h2>Sources</h2>
          <p className="muted small">Original reporting, linked; headlines shown up to 25 words. Full articles are not republished.</p>
          <ol className="sources">
            {prof.reports.map((r) => (
              <li key={r.n}>
                {r.url ? <a href={r.url} target="_blank" rel="noopener noreferrer">{r.title}</a> : r.title}
                <span className="muted"> — {r.source ?? 'unknown source'}{r.date ? `, ${r.date}` : ''}</span>
              </li>
            ))}
          </ol>
        </section>
      )}
      {prof === undefined && <p role="status">Loading details…</p>}
    </article>
  );
}
