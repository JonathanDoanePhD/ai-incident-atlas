import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { BarWithFit, Dumbbell, Heatmap, ScatterFit, SmallMultiples } from '../components/Charts';
import { loadJSON } from '../lib/data';
import { useApp } from '../state';

interface Shift { term: string; label: string; pre_share: number; post_share: number; change_pp: number; p_exploratory: number }
interface Insights {
  n: number; n_pre: number; n_post: number; genai_cutoff: string;
  yearly: { years: number[]; counts: number[]; growth_fit: { annual_growth: number; slope: number; intercept: number } };
  by_year: Record<string, { years: number[]; n: number[]; series: Record<string, number[]> }>;
  era_shift: Record<string, Shift[]>;
  harm_x_technology: { a_label: string; b_label: string; n: number; lift: number }[];
  cross_sector_failures: { label: string; incidents: number; sectors: number; normalized_entropy: number; top_sectors: { label: string; n: number }[] }[];
  recurring_actors: { entity_id: string; name: string; incidents: number; as_developer: number; as_deployer: number; top_failure_modes: { label: string; n: number }[]; mean_severity: number | null }[];
  severity_vs_attention: { spearman_rho: number; p_exploratory: number; n: number; fit: { slope: number; intercept: number }; points: [number, number][] };
  severity_by_technology: { label: string; n: number; mean_severity: number; share_s3_plus: number }[];
  evidence_mix: Record<string, number>;
}
interface SingleScore { n: number; accuracy: number; macro_f1: number; kappa: number; labels: string[]; confusion: number[][]; majority_baseline: number }
interface MultiScore { n: number; jaccard: number; any_overlap: number; micro_f1: number; macro_f1: number }
interface Evaluation {
  n_extracted: number;
  mit: { domain: SingleScore; subdomain_accuracy: number | null; via_failure_mode_accuracy: number | null; intent: SingleScore; entity: SingleScore };
  gmf_failure: MultiScore; cset_sector: MultiScore; gmf_technology: MultiScore;
  expert_baseline: Record<string, { pairs: number; jaccard: number | null; exact_agreement: number | null }>;
  second_coder: { n: number; jaccard?: Record<string, number>; risk_domain?: { agreement: number; kappa: number }; primary_failure_mode?: { agreement: number; kappa: number }; severity?: { exact: number; within_one: number; weighted_kappa: number; n: number } };
}

const pct = (v: number | null | undefined, d = 0) => (v === null || v === undefined ? '–' : `${(v * 100).toFixed(d)}%`);

export default function InsightsPage() {
  const { data, termLabel, setFilters } = useApp();
  const [ins, setIns] = useState<Insights | null>(null);
  const [ev, setEv] = useState<Evaluation | null>(null);
  const [shiftDim, setShiftDim] = useState('failure_mode');
  useEffect(() => {
    loadJSON<Insights>('insights.json').then(setIns);
    loadJSON<Evaluation>('evaluation.json').then(setEv);
  }, []);
  if (!ins || !ev) return <div className="page" role="status">Loading insights…</div>;

  const g = ins.yearly.growth_fit;
  const fit = (x: number) => Math.exp(g.intercept + g.slope * x);
  const rd = ins.by_year.risk_domain;
  const rdLabels = Object.fromEntries(Object.keys(rd.series).map((k) => [k, `${k}. ${termLabel('risk_domain', k)}`]));
  const yearsIdx = rd.years.map((y, i) => [y, i] as const).filter(([y]) => y >= 2014 && y <= 2026);
  const rdSeries = Object.fromEntries(Object.entries(rd.series).sort().map(([k, v]) => [k, yearsIdx.map(([, i]) => v[i])]));
  const shifts = ins.era_shift[shiftDim].filter((s) => s.pre_share + s.post_share > 0.02).slice(0, 10);
  const sva = ins.severity_vs_attention;
  const cl = data!.clusters;
  const m = ev.mit.domain;

  return (
    <div className="page insights">
      <h1>Insights</h1>
      <p className="lead">
        Patterns across {ins.n.toLocaleString()} coded incidents. AIID is a convenience sample of <em>publicly reported</em> incidents, so
        trends mix real change with changes in reporting and curation. Statistical tests are exploratory.
      </p>

      <section>
        <h2>Reported incidents keep accelerating</h2>
        <p>Incidents by year of occurrence, with a log-linear trend fitted to complete years 2014–2025: about <strong>{pct(g.annual_growth)}</strong> more each year. 2026 is partial (snapshot of 2 Nov 2026).</p>
        <BarWithFit xs={ins.yearly.years} ys={ins.yearly.counts} fit={fit} yLabel="Incidents per year" />
      </section>

      <section>
        <h2>What kind of risk? Share of incidents by MIT risk domain</h2>
        <p>Each panel is one domain's share of that year's incidents (same scale across panels, 2014–2026).</p>
        <SmallMultiples years={yearsIdx.map(([y]) => y)} series={rdSeries} labels={rdLabels} />
      </section>

      <section>
        <h2>Before and after ChatGPT</h2>
        <p>
          Share of incidents with each tag before ({ins.n_pre}) and after ({ins.n_post}) the public release of ChatGPT on {ins.genai_cutoff}. Sorted by size of change.
        </p>
        <div className="seg" role="group" aria-label="Dimension">
          {[['failure_mode', 'Failure modes'], ['technology', 'Technologies'], ['harm_type', 'Harms'], ['risk_domain', 'Risk domains']].map(([k, l]) => (
            <button type="button" key={k} aria-pressed={shiftDim === k} onClick={() => setShiftDim(k)}>{l}</button>
          ))}
        </div>
        <Dumbbell aLabel="Before" bLabel="After" rows={shifts.map((s) => ({
          label: shiftDim === 'risk_domain' ? `${s.term}. ${s.label}` : s.label, a: s.pre_share, b: s.post_share,
          note: `${s.change_pp > 0 ? '+' : ''}${s.change_pp} pp · p ${s.p_exploratory <= 1e-16 ? '< 1e-16' : '= ' + s.p_exploratory} (exploratory)`,
        }))} />
      </section>

      <section>
        <h2>Same failure, different sector</h2>
        <p>Failure modes ranked by how evenly they spread across sectors (normalized entropy, 1 = perfectly even). The top rows are the
          failures that recur everywhere.</p>
        <div className="table-wrap">
          <table className="data">
            <thead><tr><th scope="col">Failure mode</th><th scope="col" className="num">Incidents</th><th scope="col" className="num">Sectors</th><th scope="col" className="num">Spread</th><th scope="col">Top sectors</th></tr></thead>
            <tbody>
              {ins.cross_sector_failures.map((r) => (
                <tr key={r.label}>
                  <td>{r.label}</td><td className="num">{r.incidents}</td><td className="num">{r.sectors}</td>
                  <td className="num"><span className="bar-inline" style={{ width: `${r.normalized_entropy * 60}px` }} /> {r.normalized_entropy.toFixed(2)}</td>
                  <td>{r.top_sectors.slice(0, 3).map((s) => `${s.label} (${s.n})`).join(', ')}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section>
        <h2>Severity is not media attention</h2>
        <p>
          Each dot is an incident: number of reports (log scale) against coded severity (0–4), lightly jittered. Spearman ρ = <strong>{sva.spearman_rho.toFixed(2)}</strong> (n = {sva.n}, exploratory p = {sva.p_exploratory}). The fitted line shows severity rising only slightly with coverage.
        </p>
        <ScatterFit points={sva.points} fit={sva.fit} xLabel="Reports per incident" yLabel="Severity" />
      </section>

      <section className="two-col">
        <div>
          <h2>Which organizations recur?</h2>
          <div className="table-wrap">
            <table className="data">
              <thead><tr><th scope="col">Organization</th><th scope="col" className="num">Incidents</th><th scope="col">Most common failure modes</th></tr></thead>
              <tbody>
                {ins.recurring_actors.slice(0, 15).map((a) => (
                  <tr key={a.entity_id}>
                    <td><Link to="/catalog" onClick={() => setFilters((f) => ({ ...f, org: a.entity_id }))}>{a.name}</Link></td>
                    <td className="num">{a.incidents}</td>
                    <td>{a.top_failure_modes.map((t) => t.label).join(', ')}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
        <div>
          <h2>Harms that cluster with technologies</h2>
          <p className="muted small">Lift = how much more often the pair co-occurs than if independent (n ≥ 10).</p>
          <div className="table-wrap">
            <table className="data">
              <thead><tr><th scope="col">Technology</th><th scope="col">Harm</th><th scope="col" className="num">n</th><th scope="col" className="num">Lift</th></tr></thead>
              <tbody>
                {ins.harm_x_technology.slice(0, 15).map((r) => (
                  <tr key={r.a_label + r.b_label}><td>{r.a_label}</td><td>{r.b_label}</td><td className="num">{r.n}</td><td className="num">{r.lift.toFixed(1)}×</td></tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      <section>
        <h2>Severity by technology</h2>
        <div className="table-wrap">
          <table className="data">
            <thead><tr><th scope="col">Technology</th><th scope="col" className="num">Incidents</th><th scope="col" className="num">Mean severity</th><th scope="col" className="num">Share severe or critical</th></tr></thead>
            <tbody>
              {ins.severity_by_technology.map((r) => (
                <tr key={r.label}><td>{r.label}</td><td className="num">{r.n}</td><td className="num">{r.mean_severity.toFixed(2)}</td><td className="num">{pct(r.share_s3_plus)}</td></tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section>
        <h2>Clusters</h2>
        <p>
          {cl.k} clusters (Ward on a 10-d UMAP of text embeddings + taxonomy tags), chosen by silhouette × bootstrap stability:
          silhouette {cl.chosen.silhouette.toFixed(3)} in the original space, bootstrap ARI {cl.chosen.bootstrap_ari.toFixed(2)} ± {cl.chosen.bootstrap_ari_sd.toFixed(2)},
          seed ARI {cl.seed_ari.map((v) => v.toFixed(2)).join(' / ')}. Clusters are a lens, not ground truth.
        </p>
        <div className="table-wrap">
          <table className="data">
            <thead><tr><th scope="col">Cluster</th><th scope="col" className="num">Incidents</th><th scope="col">Over-represented terms (share in cluster, lift)</th></tr></thead>
            <tbody>
              {[...cl.clusters].sort((a, b) => b.size - a.size).map((c) => (
                <tr key={c.cluster}>
                  <td><Link to="/" onClick={() => setFilters((f) => ({ ...f, cluster: c.cluster }))}>{c.name}</Link></td>
                  <td className="num">{c.size}</td>
                  <td>{c.over_represented.slice(0, 4).map((t) => `${t.label} (${pct(t.share)}, ${t.lift.toFixed(1)}×)`).join('; ')}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section id="evaluation">
        <h2>How reliable is the coding?</h2>
        <p>Our LLM-assisted coding compared with expert labels shipped in AIID (the coder never saw them), and with a blind second coder.</p>
        <div className="kpis">
          <div className="kpi"><span className="kpi-v">{pct(m.accuracy)}</span><span className="kpi-l">MIT risk-domain accuracy (n = {m.n}; majority baseline {pct(m.majority_baseline)})</span></div>
          <div className="kpi"><span className="kpi-v">{m.kappa.toFixed(2)}</span><span className="kpi-l">Cohen's κ vs MIT experts</span></div>
          <div className="kpi"><span className="kpi-v">{pct(ev.cset_sector.any_overlap)}</span><span className="kpi-l">Sector overlaps CSET expert (n = {ev.cset_sector.n})</span></div>
          <div className="kpi"><span className="kpi-v">{ev.second_coder.severity ? ev.second_coder.severity.weighted_kappa.toFixed(2) : '–'}</span><span className="kpi-l">Severity weighted κ, blind second coder</span></div>
        </div>
        <h3>MIT risk domain — confusion matrix</h3>
        <Heatmap rows={m.labels.map((l) => l.split(' ')[0].replace('.', ''))} cols={m.labels.map((l) => l.split(' ')[0].replace('.', ''))}
          values={m.confusion} rowTitle="Expert" colTitle="Ours" />
        <p className="muted small">Domains: {m.labels.join(' · ')}</p>
        <div className="table-wrap">
          <table className="data">
            <thead><tr><th scope="col">Comparison</th><th scope="col" className="num">n</th><th scope="col" className="num">Metric</th></tr></thead>
            <tbody>
              <tr><td>MIT risk subdomain (23 classes), exact</td><td className="num">{m.n}</td><td className="num">{pct(ev.mit.subdomain_accuracy)}</td></tr>
              <tr><td>MIT intent</td><td className="num">{ev.mit.intent.n}</td><td className="num">{pct(ev.mit.intent.accuracy)} (κ {ev.mit.intent.kappa.toFixed(2)})</td></tr>
              <tr><td>MIT cause entity</td><td className="num">{ev.mit.entity.n}</td><td className="num">{pct(ev.mit.entity.accuracy)} (κ {ev.mit.entity.kappa.toFixed(2)})</td></tr>
              <tr><td>Failure mode vs GMF technical failure (Jaccard / any overlap)</td><td className="num">{ev.gmf_failure.n}</td><td className="num">{ev.gmf_failure.jaccard.toFixed(2)} / {pct(ev.gmf_failure.any_overlap)}</td></tr>
              <tr><td>Sector vs CSETv1 (Jaccard / any overlap)</td><td className="num">{ev.cset_sector.n}</td><td className="num">{ev.cset_sector.jaccard.toFixed(2)} / {pct(ev.cset_sector.any_overlap)}</td></tr>
              <tr><td>Technology vs GMF AI goal (Jaccard / any overlap)</td><td className="num">{ev.gmf_technology.n}</td><td className="num">{ev.gmf_technology.jaccard.toFixed(2)} / {pct(ev.gmf_technology.any_overlap)}</td></tr>
              {Object.entries(ev.expert_baseline).filter(([, v]) => v.pairs).map(([k, v]) => (
                <tr key={k}><td>Context: CSET annotator vs annotator — {k} (Jaccard)</td><td className="num">{v.pairs}</td><td className="num">{v.jaccard?.toFixed(2)}</td></tr>
              ))}
            </tbody>
          </table>
        </div>
        <p><a href="https://github.com/jonathandoanephd/ai-incident-atlas/blob/HEAD/reports/evaluation.md">Full evaluation report, including analyzed disagreements →</a></p>
      </section>
    </div>
  );
}
