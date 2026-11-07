import { useApp } from '../state';

const REPO = 'https://github.com/jonathandoanephd/ai-incident-atlas';

export default function AboutPage() {
  const { data } = useApp();
  const meta = data!.meta;
  return (
    <article className="page prose">
      <h1>About &amp; methodology</h1>
      <p className="lead">
        The AI Incident Atlas is an evidence-grounded map of real-world AI incidents. It re-codes every incident in the AI Incident
        Database with a consistent taxonomy, links each confirmed label to a verbatim quote from the original reporting, and connects
        incidents that fail in the same way — often in completely different sectors.
      </p>

      <h2>Data source &amp; license</h2>
      <ul>
        <li>
          Source: <a href="https://incidentdatabase.ai">AI Incident Database</a> (Responsible AI Collaborative), official weekly snapshot{' '}
          <code>{meta.snapshot}</code> ({meta.snapshot_date}), downloaded from the{' '}
          <a href="https://incidentdatabase.ai/research/snapshots/">AIID snapshots page</a> and verified by SHA-256.
        </li>
        <li>
          The AIID database (incidents, classifications, entities, taxonomies) is licensed{' '}
          <a href="https://creativecommons.org/licenses/by-sa/4.0/">CC BY-SA 4.0</a>. All derived data in this atlas is therefore also
          released under CC BY-SA 4.0. The application code is MIT-licensed.
        </li>
        <li>
          Report texts are owned by their publishers and are <strong>not</strong> covered by the AIID license. They were used only for
          local analysis. The atlas shows our own summaries, short attributed excerpts (≤ 25 words) linked to the original article, and
          links to sources — never full articles.
        </li>
      </ul>

      <h2>Pipeline</h2>
      <ol>
        <li><strong>Ingestion.</strong> The snapshot is loaded into a normalized SQLite database (raw tables kept verbatim, clean tables, bridge tables for incident↔report, incident↔entity-with-role and incident↔expert-label, provenance with checksums).</li>
        <li><strong>Taxonomy (v{meta.taxonomy_version}).</strong> Multi-label dimensions for sector, technology, failure mode, harm type, severity, lifecycle stage and affected population, plus a risk-domain dimension aligned with the MIT AI Risk Repository. A crosswalk maps the expert taxonomies in AIID (MIT, GMF, CSETv1) onto ours for evaluation only.</li>
        <li><strong>Evidence-grounded extraction.</strong> A language model reads up to three report excerpts per incident and returns a schema-validated record: summaries, tags marked <em>confirmed</em> (with a quote) or <em>inferred</em>, severity, and roles. Code checks every quote verbatim against the cached report text; a failed quote blocks loading until it is fixed (snapped to the exact span, or downgraded to inferred). A 20-incident pilot preceded scale-up and changed the prompt and taxonomy.</li>
        <li><strong>Evaluation.</strong> Agreement with expert labels (accuracy, macro-F1, κ, confusion matrices, analyzed disagreements) and a blind re-coding of a random sample by a different model. See the <a href="#/insights">Insights</a> page and the <a href={`${REPO}/blob/HEAD/reports/evaluation.md`}>evaluation report</a>.</li>
        <li><strong>Connections.</strong> Sentence embeddings (all-MiniLM-L6-v2) plus IDF-weighted tag overlap give seven similarity views (semantic, failure mode, technology, sector, harm, shared organization, blended). Each keeps a sparse top-6 graph, and every edge stores an explanation built from what the two incidents actually share.</li>
        <li><strong>Clusters &amp; layout.</strong> UMAP (10-d) + Ward clustering, with k chosen by silhouette × bootstrap stability; clusters are labelled by over-represented taxonomy terms. A separate 3-D UMAP gives the fixed constellation positions.</li>
      </ol>

      <h2>Reading the constellation</h2>
      <ul>
        <li>Positions come from a 3-D projection of the same features used for clustering: nearby stars are similar incidents. Positions are fixed, so filtering never moves anything.</li>
        <li>Size is min–max scaled between fixed bounds. Number of reports measures <em>media attention</em>, not severity.</li>
        <li>Gray marks missing values. Categories past the seventh most common share one “Other” color; the legend and hover card always name them.</li>
      </ul>

      <h2>Limitations</h2>
      <ul>
        <li>AIID is a convenience sample of publicly reported incidents, skewed toward English-language media and high-profile companies. Trends reflect reporting as well as reality.</li>
        <li>Extraction reads at most three report excerpts (≈2,500 characters each), so later details can be missed; tags are then marked inferred or absent.</li>
        <li>LLM coding is imperfect; agreement with experts is reported honestly, including where it is weak. Expert labels exist for only part of the database, and the experts disagree with each other too.</li>
        <li>Severity is a coarse, judgment-based band. Allegations in lawsuits or reports are not verified facts.</li>
        <li>Clusters and similarity edges are analytical lenses. A pretty graph is not evidence; the explanation on each edge is the claim.</li>
      </ul>

      <h2>Ethics</h2>
      <ul>
        <li>The atlas focuses on systems, organizations and categories of harm. Names of private individuals (for example people who were harmed) are classified and removed from entity lists, and redacted from titles and summaries.</li>
        <li>Report text was treated as untrusted data; instructions inside articles were never followed.</li>
        <li>Harms are described factually; organizations are named as <em>alleged</em> developers or deployers, as in AIID.</li>
      </ul>

      <p className="muted small">
        Built by Jonathan Doane. Generated {meta.generated}. Taxonomy v{meta.taxonomy_version}. {meta.n_extracted.toLocaleString()} of{' '}
        {meta.n_incidents.toLocaleString()} incidents coded. Source code and reports: <a href={REPO}>{REPO.replace('https://', '')}</a>.
      </p>
      <p className="muted small">{meta.license.attribution}</p>
    </article>
  );
}
