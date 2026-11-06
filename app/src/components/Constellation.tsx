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
  focusId: number | null;
}

const SCALE = 55;
const DIM = 'rgba(120,128,140,0.10)';

type Graph = InstanceType<typeof ForceGraph3D>;

const linkEnd = (v: number | GNode) => (typeof v === 'object' ? v.id : v);

export default function Constellation(props: Props) {
  const { nodes, links, colorOf, sizeOf, visible, selected, highlight, onHover, onSelect, focusId } = props;
  const el = useRef<HTMLDivElement>(null);
  const graph = useRef<Graph | null>(null);
  const cbs = useRef({ onHover, onSelect });
  cbs.current = { onHover, onSelect };
  const visibleRef = useRef(visible);
  visibleRef.current = visible;
  const joined = useRef<GLink[]>([]);

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
      .backgroundColor('#0b0d12')
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
      g._destructor();
      graph.current = null;
    };
  }, []);

  // ---- data join: only when node set or link view changes --------------------------------------------
  useEffect(() => {
    joined.current = links.map((l) => ({ ...l }));
    graph.current?.graphData({ nodes: gnodes, links: joined.current });
    applyVisibilitySoon();
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
    if (!g || focusId === null) return;
    const n = gnodes.find((x) => x.id === focusId);
    if (!n) return;
    const d = 70;
    const r = Math.hypot(n.x, n.y, n.z) || 1;
    const k = 1 + d / r;
    g.cameraPosition({ x: n.x * k, y: n.y * k, z: n.z * k }, { x: n.x, y: n.y, z: n.z }, 900);
  }, [focusId, gnodes]);

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
