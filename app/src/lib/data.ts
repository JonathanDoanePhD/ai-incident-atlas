import type { Clusters, EdgeBundle, Entity, IncidentNode, Meta, Profile } from './types';

const BASE = `${import.meta.env.BASE_URL}data/`;
const cache = new Map<string, Promise<unknown>>();

export function loadJSON<T>(path: string): Promise<T> {
  if (!cache.has(path)) {
    cache.set(
      path,
      fetch(BASE + path).then((r) => {
        if (!r.ok) throw new Error(`Failed to load ${path}: ${r.status}`);
        return r.json();
      }),
    );
  }
  return cache.get(path) as Promise<T>;
}

export interface CoreData {
  meta: Meta;
  nodes: IncidentNode[];
  byId: Map<number, IncidentNode>;
  entities: Record<string, Entity>;
  clusters: Clusters;
}

let core: Promise<CoreData> | null = null;

export function loadCore(): Promise<CoreData> {
  if (!core) {
    core = Promise.all([
      loadJSON<Meta>('meta.json'),
      loadJSON<IncidentNode[]>('nodes.json'),
      loadJSON<Record<string, Entity>>('entities.json'),
      loadJSON<Clusters>('clusters.json'),
    ]).then(([meta, nodes, entities, clusters]) => ({
      meta,
      nodes,
      byId: new Map(nodes.map((n) => [n.id, n])),
      entities,
      clusters,
    }));
  }
  return core;
}

/** Shared explanation sentences (edges and profiles store indices into this table; see src/atlas/export/compact.py). */
export const loadExplanations = () => loadJSON<string[]>('explanations.json');

let edgesP: Promise<EdgeBundle> | null = null;
export function loadEdges(): Promise<EdgeBundle> {
  if (!edgesP) {
    edgesP = Promise.all([loadJSON<Pick<EdgeBundle, 'views'>>('edges.json'), loadExplanations()]).then(([e, explanations]) => ({
      views: e.views,
      explanations,
    }));
  }
  return edgesP;
}

/** [incident id, weight, explanation index] as stored in profile chunks. */
type PackedRelated = [number, number, number];

export async function loadProfile(id: number): Promise<Profile | undefined> {
  const [chunk, explanations] = await Promise.all([
    loadJSON<Record<string, Omit<Profile, 'related'> & { related?: PackedRelated[] }>>(`profiles/p${Math.floor(id / 100)}.json`),
    loadExplanations(),
  ]);
  const raw = chunk[String(id)];
  if (!raw) return undefined;
  return { ...raw, related: (raw.related ?? []).map(([rid, w, k]) => ({ id: rid, w, why: explanations[k] ?? '' })) };
}
