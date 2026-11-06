import MiniSearch from 'minisearch';
import type { IncidentNode } from './types';

/**
 * Relevance-ranked search. Title matches weigh 3×, organization names 2×, summary 1×.
 * Prefix and light fuzzy matching help with partial words ("recogn", "chatbto").
 */
export interface SearchDoc {
  id: number;
  title: string;
  summary: string;
  orgs: string;
  tags: string;
}

export function buildIndex(
  nodes: IncidentNode[],
  orgName: (id: string) => string,
  termLabel: (dim: string, id: string) => string,
): MiniSearch<SearchDoc> {
  const ms = new MiniSearch<SearchDoc>({
    fields: ['title', 'summary', 'orgs', 'tags'],
    storeFields: ['id'],
    searchOptions: { boost: { title: 3, orgs: 2, tags: 1.2 }, prefix: true, fuzzy: 0.15, combineWith: 'AND' },
  });
  ms.addAll(
    nodes.map((n) => ({
      id: n.id,
      title: n.t,
      summary: n.s,
      orgs: n.org.map(orgName).join(' '),
      tags: [
        ...n.tech.map((t) => termLabel('technology', t)),
        ...n.fm.map((t) => termLabel('failure_mode', t)),
        ...n.sec.map((t) => termLabel('sector', t)),
        ...n.harm.map((t) => termLabel('harm_type', t)),
      ].join(' '),
    })),
  );
  return ms;
}

/** Returns ids in relevance order; empty query → null (meaning "no search active"). */
export function search(ms: MiniSearch<SearchDoc>, q: string): number[] | null {
  const query = q.trim();
  if (!query) return null;
  let res = ms.search(query);
  if (res.length === 0) res = ms.search(query, { combineWith: 'OR' });
  return res.map((r) => r.id as number);
}
