// Data contract for the static bundle written by `python -m atlas.export.bundle`.

export interface Term {
  id: string;
  label: string;
  color: string;
  parent?: string;
}

export interface Dimension {
  label: string;
  multi: boolean;
  terms: Term[];
  parents?: Record<string, string>;
}

export interface Meta {
  generated: string;
  snapshot: string;
  snapshot_date: string;
  taxonomy_version: string;
  n_incidents: number;
  n_extracted: number;
  dimensions: Record<string, Dimension>;
  unknown_color: string;
  views: string[];
  n_predicted?: number;
  propagation_cv?: { n: number; single: Record<string, { accuracy: number; majority_baseline: number }>; multi: Record<string, { jaccard: number }> } | null;
  license: { data: string; code: string; attribution: string };
}

/** Compact incident node (see NODE_FIELDS in src/atlas/export/bundle.py). */
export interface IncidentNode {
  id: number;
  t: string;
  y: number;
  d: string;
  s: string;
  sec: string[];
  tech: string[];
  fm: string[];
  pfm: string | null;
  harm: string[];
  pop: string[];
  life: string[];
  sev: number | null;
  rd: string | null;
  int: string | null;
  cause: string | null;
  org: string[];
  nrep: number;
  cl: number;
  p: [number, number, number];
  br: number;
  x: number;
  /** 1 when tags are kNN-predicted (no LLM extraction) */
  pr: number;
}

/** [source, target, weight, explanationIndex] */
export type PackedEdge = [number, number, number, number];

export interface EdgeBundle {
  explanations: string[];
  views: Record<string, PackedEdge[]>;
}

export interface TagOut {
  id: string;
  ev: 'confirmed' | 'inferred';
  q?: string;
  rn?: number;
  src?: string | null;
  url?: string | null;
}

export interface Profile {
  id: number;
  aiid_url: string;
  description: string | null;
  reports: { n: number; title: string; url: string | null; source: string | null; date: string | null }[];
  developers: string[];
  deployers: string[];
  harmed_groups: string[];
  technical_summary?: string;
  systems?: string[];
  tags?: Record<string, TagOut[]>;
  severity?: TagOut | null;
  risk_subdomain?: string | null;
  notes?: string | null;
  related?: { id: number; w: number; why: string }[];
  predicted?: { confidence: number | null };
}

export interface Entity {
  name: string;
  kind: string;
  n: number;
}

export interface ClusterInfo {
  cluster: number;
  size: number;
  name: string;
  over_represented: { dimension: string; term: string; label: string; share: number; lift: number }[];
}

export interface Clusters {
  k: number;
  chosen: { k: number; silhouette: number; bootstrap_ari: number; bootstrap_ari_sd: number; score: number };
  seed_ari: number[];
  selection: { k: number; silhouette: number; bootstrap_ari: number; score: number }[];
  clusters: ClusterInfo[];
}
