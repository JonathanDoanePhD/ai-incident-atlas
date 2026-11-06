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

export const loadEdges = () => loadJSON<EdgeBundle>('edges.json');

export async function loadProfile(id: number): Promise<Profile | undefined> {
  const chunk = await loadJSON<Record<string, Profile>>(`profiles/p${Math.floor(id / 100)}.json`);
  return chunk[String(id)];
}
