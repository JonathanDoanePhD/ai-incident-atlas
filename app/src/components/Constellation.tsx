import { useEffect, useMemo, useRef } from 'react';
import ForceGraph3D from '3d-force-graph';
import type { IncidentNode } from '../lib/types';

/**
 * 3-D constellation. Design rules (see README "Front-end engineering"):
 *  - Node objects are created ONCE (cached in a ref) with fixed positions from the precomputed 3-D UMAP layout,
 *    so nothing ever "jumps": there is no force simulation.
 *  - Each styling concern has its own effect scoped to its own inputs (colour, size, visibility, links,
 *    highlight). Filter changes therefore only restyle; the graph is only re-joined when the link view changes.
 *  - Visibility is applied by toggling `object.visible` on the cached three.js objects. (The library's
 *    nodeVisibility accessor removes hidden objects from the scene and recreates them when shown again, which
 *    made the year slider rebuild nodes; verified by scripts/verify.cjs.)
 */

interface ThreeHolder {
  __threeObj?: { visible: boolean };
  __lineObj?: { visible: boolean };
}

export interface GNode extends ThreeHolder {
  id: number;
  ref: IncidentNode;
  x: number;
  y: number;
  z: number;
  fx: number;
  fy: number;
  fz: number;
}

export interface GLink extends ThreeHolder {
  source: number | GNode;
  target: number | GNode;
  w: number;
  why: number;
}

interface Props {
  nodes: IncidentNode[];
  links: GLink[];
  colorOf: (n: IncidentNode) => string;
  sizeOf: (n: IncidentNode) => number;
  visible: Set<number>;
  selected: number | null;
  highlight: Set<number>;
  onHover: (n: IncidentNode | null) => void;
  onSelect: (n: IncidentNode | null) => void;
  /** Camera fly-to request; `seq` changes on every request so re-clicking the same star re-flies. */
  focus: { id: number; seq: number } | null;
}

const SCALE = 55;
const bgColor = () => (document.documentElement.dataset.theme === 'light' ? '#f6f7fb' : '#0b0f17');
const DIM = 'rgba(120,128,140,0.10)';

type Graph = InstanceType<typeof ForceGraph3D>;

const linkEnd = (v: number | GNode) => (typeof v === 'object' ? v.id : v);

export default function Constellation(props: Props) {
  const { nodes, links, colorOf, sizeOf, visible, selected, highlight, onHover, onSelect, focus } = props;
  const el = useRef<HTMLDivElement>(null);
  const graph = useRef<Graph | null>(null);
  const cbs = useRef({ onHover, onSelect });
  cbs.current = { onHover, onSelect };
  const visibleRef = useRef(visible);
  visibleRef.current = visible;
  const joined = useRef<GLink[]>([]);
  const fitted = useRef(false);
  const baseOpacity = useRef(0.22);
  const selectedRef = useRef(selected);
  selectedRef.current = selected;

  /** Show/hide cached objects in place (never removes them from the scene). */
  const applyVisibility = () => {
    const vis = visibleRef.current;
    for (const n of gnodes) if (n.__threeObj) n.__threeObj.visible = vis.has(n.id);
    for (const l of joined.current) {
      if (l.__lineObj) l.__lineObj.visible = vis.has(linkEnd(l.source)) && vis.has(linkEnd(l.target));
    }
  };
  const applyVisibilitySoon = () => {
    applyVisibility();
    requestAnimationFrame(() => requestAnimationFrame(applyVisibility));
  };

  // Node objects: created once per dataset, never recreated by styling changes.
  const gnodes = useMemo<GNode[]>(
    () =>
      nodes.map((n) => {
        const [x, y, z] = n.p.map((v) => v * SCALE);
        return { id: n.id, ref: n, x, y, z, fx: x, fy: y, fz: z };
      }),
    [nodes],
  );

  // ---- create the graph once ------------------------------------------------------------------------
  useEffect(() => {
    if (!el.current) return;
    const g = new ForceGraph3D(el.current, { controlType: 'orbit' })
      .backgroundColor(bgColor())
      .showNavInfo(false)
      .nodeId('id')
      .nodeLabel(() => '')
      .nodeOpacity(0.92)
      .nodeResolution(10)
      .nodeRelSize(1.6)
      .linkOpacity(0.22)
      .enableNodeDrag(false)
      .cooldownTicks(0)
      .warmupTicks(0)
      .onNodeHover((n) => {
        const ok = n && visibleRef.current.has((n as GNode).id);
        if (el.current) el.current.style.cursor = ok ? 'pointer' : 'grab';
        cbs.current.onHover(ok ? (n as GNode).ref : null);
      })
      .onNodeClick((n) => {
        if (visibleRef.current.has((n as GNode).id)) cbs.current.onSelect((n as GNode).ref);
      })
      .onBackgroundClick(() => cbs.current.onSelect(null));
    graph.current = g;
    // follow the light/dark theme toggle
    const mo = new MutationObserver(() => g.backgroundColor(bgColor()));
    mo.observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
    (window as unknown as { __atlasGraph: Graph }).__atlasGraph = g;
    const resize = () => {
      if (el.current) g.width(el.current.clientWidth).height(el.current.clientHeight);
    };
    resize();
    const ro = new ResizeObserver(resize);
    ro.observe(el.current);
    g.cameraPosition({ x: 0, y: 0, z: 260 });
    return () => {
      ro.disconnect();
      mo.disconnect();
      g._destructor();
      graph.current = null;
    };
  }, []);

  // ---- data join: only when node set or link view changes --------------------------------------------
  useEffect(() => {
    joined.current = links.map((l) => ({ ...l }));
    // Denser views fade their links so structure stays readable (≈ 0.22 at 1,500 links, floor 0.05).
    baseOpacity.current = Math.max(0.05, Math.min(0.22, (0.22 * 1500) / Math.max(links.length, 1)));
    graph.current?.linkOpacity(selectedRef.current !== null ? 0.95 : baseOpacity.current);
    graph.current?.graphData({ nodes: gnodes, links: joined.current });
    applyVisibilitySoon();
    if (!fitted.current && graph.current) {
      fitted.current = true;
      const g = graph.current;
      window.setTimeout(() => g.zoomToFit(0, 70), 60);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [gnodes, links]);

  // ---- colour + highlight (restyle only) -----------------------------------------------------------
  useEffect(() => {
    const g = graph.current;
    if (!g) return;
    const hl = highlight.size > 0;
    g.nodeColor((n) => {
      const r = (n as GNode).ref;
      if (hl && !highlight.has(r.id)) return DIM;
      return colorOf(r);
    });
    g.linkColor((l) => {
      const a = linkEnd((l as GLink).source);
      const b = linkEnd((l as GLink).target);
      if (hl) return highlight.has(a) && highlight.has(b) && (a === selected || b === selected) ? '#f5f7fa' : 'rgba(120,128,140,0.05)';
      return '#7c8696';
    });
    g.linkWidth((l) => {
      const a = linkEnd((l as GLink).source);
      const b = linkEnd((l as GLink).target);
      return hl && (a === selected || b === selected) ? 0.8 : 0;
    });
    applyVisibilitySoon();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [colorOf, highlight, selected]);

  // ---- pulses: particles flow along the selected star's connections (both directions) ---------------
  useEffect(() => {
    const g = graph.current;
    if (!g) return;
    const vis = visibleRef.current;
    const live = (l: GLink) => {
      const a = linkEnd(l.source);
      const b = linkEnd(l.target);
      return selected !== null && (a === selected || b === selected) && vis.has(a) && vis.has(b);
    };
    // Particle opacity is scaled by link opacity (kept low so 7,800 links stay readable). While a star is
    // selected, raise it: only the selected star's links are coloured opaque; all others stay ~transparent.
    g.linkOpacity(selected !== null ? 0.95 : baseOpacity.current);
    g.linkDirectionalParticles((l) => (live(l as GLink) ? 4 : 0))
      .linkDirectionalParticleSpeed((l) => 0.004 + 0.012 * Math.max(0, (l as GLink).w - 0.3))
      .linkDirectionalParticleWidth(3.4)
      .linkDirectionalParticleResolution(8)
      .linkDirectionalParticleColor(() => '#ffd479');
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selected, visible, links]);

  // ---- size (restyle only) ---------------------------------------------------------------------------
  useEffect(() => {
    graph.current?.nodeVal((n) => sizeOf((n as GNode).ref));
    applyVisibilitySoon();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sizeOf]);

  // ---- visibility (filters, year slider) ------------------------------------------------------------
  useEffect(() => {
    applyVisibilitySoon();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [visible]);

  // ---- camera focus -----------------------------------------------------------------------------------
  useEffect(() => {
    const g = graph.current;
    if (!g || focus === null) return;
    const n = gnodes.find((x) => x.id === focus.id);
    if (!n) return;
    // Frame the star together with its connected neighbours, so the pulses along every link stay in view.
    const byId = new Map(gnodes.map((x) => [x.id, x]));
    let spread = 0;
    for (const l of joined.current) {
      const a = linkEnd(l.source);
      const b = linkEnd(l.target);
      if (a !== n.id && b !== n.id) continue;
      const o = byId.get(a === n.id ? b : a);
      if (o) spread = Math.max(spread, Math.hypot(o.x - n.x, o.y - n.y, o.z - n.z));
    }
    const d = Math.min(320, Math.max(90, spread * 2.4 + 40));
    const r = Math.hypot(n.x, n.y, n.z) || 1;
    const k = 1 + d / r;
    g.cameraPosition({ x: n.x * k, y: n.y * k, z: n.z * k }, { x: n.x, y: n.y, z: n.z }, 900);
  }, [focus, gnodes]);

  return <div ref={el} className="constellation-canvas" aria-hidden="true" />;
}

export function hasWebGL(): boolean {
  try {
    const c = document.createElement('canvas');
    return !!(c.getContext('webgl2') || c.getContext('webgl'));
  } catch {
    return false;
  }
}
