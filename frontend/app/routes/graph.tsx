import { Autocomplete, Box, Button, Chip, Paper, Stack, TextField, Typography } from "@mui/material";
import { lazy, Suspense, useMemo, useRef, useState, useEffect } from "react";
import { useNavigate, useRevalidator } from "react-router";

import { api, MEDIA_TYPES, TYPE_LABEL, type Graph, type MediaType } from "../api";
import { MediaDialog } from "../components/media-dialog";
import type { Route } from "./+types/graph";

// Canvas library touches window on import
const ForceGraph2D = lazy(() => import("react-force-graph-2d"));

const TYPE_COLOR: Record<MediaType, string> = {
  book: "#42a5f5",
  tv_show: "#ab47bc",
  film: "#ef5350",
  game: "#66bb6a",
  podcast: "#ffa726",
  other: "#bdbdbd",
};

// force-graph renders tooltips as HTML, so user text must be escaped
const esc = (s: string) =>
  s.replace(/[&<>"']/g, (c) => `&#${c.charCodeAt(0)};`);

export const clientLoader = () => api<Graph>("/graph");

export default function GraphPage({ loaderData: graph }: Route.ComponentProps) {
  const navigate = useNavigate();
  const { revalidate } = useRevalidator();
  const [types, setTypes] = useState<MediaType[]>([]);
  const [themes, setThemes] = useState<string[]>([]);
  const [adding, setAdding] = useState(false);
  const box = useRef<HTMLDivElement>(null);
  const [size, setSize] = useState({ width: 800, height: 600 });

  useEffect(() => {
    const el = box.current;
    if (!el) return;
    const ro = new ResizeObserver(() => setSize({ width: el.clientWidth, height: el.clientHeight }));
    ro.observe(el);
    return () => ro.disconnect();
  }, []);

  const allThemes = useMemo(() => [...new Set(graph.edges.flatMap((e) => e.themes))].sort(), [graph]);

  const data = useMemo(() => {
    // Selected themes keep only edges carrying one of them (OR)
    const edges = graph.edges
      .filter((e) => !themes.length || e.themes.some((t) => themes.includes(t)))
      .map((e) => ({ ...e, label: esc(e.themes.join(", ")) }));
    const linked = new Set(edges.flatMap((e) => [e.source, e.target]));
    const nodes = graph.nodes
      .filter((n) => !types.length || types.includes(n.media_type))
      .filter((n) => !themes.length || linked.has(n.id))
      .map((n) => ({ ...n }));
    const ids = new Set(nodes.map((n) => n.id));
    return { nodes, links: edges.filter((e) => ids.has(e.source) && ids.has(e.target)) };
  }, [graph, types, themes]);

  return (
    <Box sx={{ display: "flex", flexDirection: "column", height: "calc(100vh - 64px)" }}>
      <Paper square sx={{ p: 2 }}>
        <Stack direction="row" spacing={2} sx={{ alignItems: "center", flexWrap: "wrap", rowGap: 1 }}>
          <Stack direction="row" spacing={1}>
            {MEDIA_TYPES.map((t) => (
              <Chip
                key={t}
                label={TYPE_LABEL[t]}
                variant={types.includes(t) ? "filled" : "outlined"}
                onClick={() => setTypes(types.includes(t) ? types.filter((x) => x !== t) : [...types, t])}
                sx={{ borderColor: TYPE_COLOR[t], bgcolor: types.includes(t) ? TYPE_COLOR[t] : undefined }}
              />
            ))}
          </Stack>
          <Autocomplete
            multiple
            size="small"
            options={allThemes}
            value={themes}
            onChange={(_, v) => setThemes(v)}
            sx={{ minWidth: 280, flex: 1 }}
            renderInput={(p) => <TextField {...p} label="Filter by theme" />}
          />
          <Button variant="contained" onClick={() => setAdding(true)}>
            Add media
          </Button>
        </Stack>
      </Paper>
      <Box ref={box} sx={{ flex: 1, minHeight: 0, position: "relative" }}>
        {graph.nodes.length === 0 ? (
          <Typography color="text.secondary" sx={{ p: 4 }}>
            Nothing here yet. Add some media, then link it by theme.
          </Typography>
        ) : (
          <Suspense fallback={null}>
            <ForceGraph2D
              {...size}
              graphData={data}
              backgroundColor="transparent"
              nodeLabel={(n) => esc(`${n.title} — ${n.creator}`)}
              nodeColor={(n) => TYPE_COLOR[n.media_type as MediaType]}
              linkLabel="label"
              linkColor={() => "#9e9e9e"}
              onNodeClick={(n) => navigate(`/media/${n.id}`)}
            />
          </Suspense>
        )}
      </Box>
      {adding && (
        <MediaDialog
          open
          onClose={() => setAdding(false)}
          onSaved={() => revalidate()}
          mediaOptions={graph.nodes}
          themeOptions={allThemes}
        />
      )}
    </Box>
  );
}
