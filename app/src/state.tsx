import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from 'react';
import type MiniSearch from 'minisearch';
import { loadCore, type CoreData } from './lib/data';
import { defaultFilters, type Filters } from './lib/filters';
import { buildIndex, type SearchDoc } from './lib/search';

interface AppState {
  data: CoreData | null;
  error: string | null;
  filters: Filters;
  setFilters: (f: Filters | ((f: Filters) => Filters)) => void;
  resetFilters: () => void;
  query: string;
  setQuery: (q: string) => void;
  index: MiniSearch<SearchDoc> | null;
  yearBounds: [number, number];
  termLabel: (dim: string, id: string) => string;
  orgName: (id: string) => string;
}

const Ctx = createContext<AppState | null>(null);

export function AppProvider({ children }: { children: ReactNode }) {
  const [data, setData] = useState<CoreData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState<Filters>(defaultFilters(1983, 2026));
  const [query, setQuery] = useState('');

  useEffect(() => {
    loadCore()
      .then((d) => {
        setData(d);
        const ys = d.nodes.map((n) => n.y);
        setFilters(defaultFilters(Math.min(...ys), Math.max(...ys)));
      })
      .catch((e) => setError(String(e)));
  }, []);

  // Stable identity: depends on the data only (a new array on every filter change restarted year playback).
  const yearBounds = useMemo<[number, number]>(() => {
    const ys = data ? data.nodes.map((n) => n.y) : [1983, 2026];
    return [Math.min(...ys), Math.max(...ys)];
  }, [data]);

  const value = useMemo<AppState>(() => {
    const labels = new Map<string, string>();
    if (data) {
      for (const [dim, spec] of Object.entries(data.meta.dimensions)) {
        for (const t of spec.terms) labels.set(`${dim}:${t.id}`, t.label);
      }
    }
    const termLabel = (dim: string, id: string) => labels.get(`${dim}:${id}`) ?? id;
    const orgName = (id: string) => data?.entities[id]?.name ?? id;
    return {
      data,
      error,
      filters,
      setFilters,
      resetFilters: () => setFilters(defaultFilters(yearBounds[0], yearBounds[1])),
      query,
      setQuery,
      index: data ? buildIndex(data.nodes, orgName, termLabel) : null,
      yearBounds,
      termLabel,
      orgName,
    };
  }, [data, error, filters, query, yearBounds]);

  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}

export function useApp(): AppState {
  const v = useContext(Ctx);
  if (!v) throw new Error('useApp outside provider');
  return v;
}
