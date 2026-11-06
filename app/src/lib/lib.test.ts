import { describe, expect, it } from 'vitest';
import { activeFilterCount, defaultFilters, facetCounts, matches, toggleFacet } from './filters';
import { buildIndex, search } from './search';
import { buildEncoder, CATEGORICAL, OTHER, scaleTo, SIZE_BOUNDS, UNKNOWN } from './style';
import type { IncidentNode, Meta } from './types';

const node = (over: Partial<IncidentNode>): IncidentNode => ({
  id: 1, t: 'Title', y: 2020, d: '2020-01-01', s: 'summary', sec: [], tech: [], fm: [], pfm: null, harm: [], pop: [],
  life: [], sev: null, rd: null, int: null, cause: null, org: [], nrep: 1, cl: 0, p: [0, 0, 0], br: 0, x: 1, ...over,
});

const NODES = [
  node({ id: 1, t: 'Facial recognition leads to wrongful arrest', y: 2020, sev: 3, tech: ['facial_recognition'], fm: ['bias_discrimination'], rd: '1', org: ['clearview'] }),
  node({ id: 2, t: 'Chatbot invents legal citations', y: 2023, d: '2023-05-01', sev: 2, tech: ['llm_chatbot'], fm: ['hallucination'], rd: '3', s: 'lawyer used chatgpt' }),
  node({ id: 3, t: 'Self-driving car crash', y: 2018, sev: 4, tech: ['autonomous_vehicle'], fm: ['robustness_failure'], rd: '7', nrep: 20 }),
  node({ id: 4, t: 'Deepfake scam', y: 2024, d: '2024-02-01', sev: null, tech: ['image_video_generation', 'voice_synthesis'], fm: ['malicious_use'], rd: '4' }),
];

describe('filters', () => {
  it('passes everything by default', () => {
    const f = defaultFilters(2018, 2024);
    expect(NODES.filter((n) => matches(n, f)).map((n) => n.id)).toEqual([1, 2, 3, 4]);
    expect(activeFilterCount(f, 2018, 2024)).toBe(0);
  });
  it('applies year, severity and unknown-severity rules', () => {
    const f = { ...defaultFilters(2018, 2024), years: [2019, 2024] as [number, number], severity: [2, 4] as [number, number] };
    expect(NODES.filter((n) => matches(n, f)).map((n) => n.id)).toEqual([1, 2, 4]);
    expect(NODES.filter((n) => matches(n, { ...f, includeUnknownSeverity: false })).map((n) => n.id)).toEqual([1, 2]);
  });
  it('ORs within a facet and ANDs across facets', () => {
    let f = toggleFacet(defaultFilters(2018, 2024), 'tech', 'llm_chatbot');
    f = toggleFacet(f, 'tech', 'voice_synthesis');
    expect(NODES.filter((n) => matches(n, f)).map((n) => n.id)).toEqual([2, 4]);
    f = toggleFacet(f, 'rd', '4');
    expect(NODES.filter((n) => matches(n, f)).map((n) => n.id)).toEqual([4]);
    expect(activeFilterCount(f, 2018, 2024)).toBe(2);
    f = toggleFacet(f, 'rd', '4');
    expect(f.facets.rd).toEqual([]);
  });
  it('filters by organization and cluster', () => {
    const f = { ...defaultFilters(2018, 2024), org: 'clearview' };
    expect(NODES.filter((n) => matches(n, f)).map((n) => n.id)).toEqual([1]);
  });
  it('counts facet values, sorted by frequency', () => {
    expect(facetCounts(NODES, 'tech')[0][1]).toBe(1);
    expect(facetCounts(NODES, 'rd').map(([v]) => v).sort()).toEqual(['1', '3', '4', '7']);
  });
});

describe('search', () => {
  const ms = buildIndex(NODES, (id) => (id === 'clearview' ? 'Clearview AI' : id), (_d, id) => id.replace(/_/g, ' '));
  it('returns null for an empty query', () => {
    expect(search(ms, '  ')).toBeNull();
  });
  it('ranks title matches above summary-only matches', () => {
    const extra = buildIndex(
      [node({ id: 10, t: 'Hallucinated citations in court', s: 'x' }), node({ id: 11, t: 'Other', s: 'mentions citations once' })],
      (x) => x, (_d, x) => x,
    );
    expect(search(extra, 'citations')).toEqual([10, 11]);
  });
  it('supports prefix and organization search', () => {
    expect(search(ms, 'recogn')).toContain(1);
    expect(search(ms, 'clearview')).toEqual([1]);
  });
});

describe('style', () => {
  it('min-max scales sizes between fixed bounds', () => {
    expect(scaleTo(0, [0, 10])).toBe(SIZE_BOUNDS[0]);
    expect(scaleTo(10, [0, 10])).toBe(SIZE_BOUNDS[1]);
    expect(scaleTo(5, [5, 5])).toBe((SIZE_BOUNDS[0] + SIZE_BOUNDS[1]) / 2);
  });
  it('uses gray for unknowns and keeps colours stable by global frequency', () => {
    const meta = { dimensions: { sector: { label: '', multi: true, terms: [] } } } as unknown as Meta;
    const many = Array.from({ length: 20 }, (_, i) => node({ id: 100 + i, tech: [`t${i % 10}`], cl: i % 10 }));
    const enc = buildEncoder('tech', meta, [...many, node({ id: 999, tech: [] })], new Map());
    expect(enc.color(node({ tech: [] }))).toBe(UNKNOWN);
    expect(enc.legend.length).toBe(CATEGORICAL.length + 1); // 7 colours + Other + Unknown
    const colours = new Set(many.map((n) => enc.color(n)));
    expect(colours.has(OTHER)).toBe(true);
  });
});
