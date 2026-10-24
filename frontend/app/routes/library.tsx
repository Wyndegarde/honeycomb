import {
  Box,
  Button,
  MenuItem,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from "@mui/material";
import { useState } from "react";
import { Link as RouterLink, useRevalidator, useSearchParams } from "react-router";

import { api, MEDIA_TYPES, TYPE_LABEL, type Graph, type Media } from "../api";
import { MediaDialog } from "../components/media-dialog";
import type { Route } from "./+types/library";

// shortcut: loads the first 500 (API max); add paging past a personal-scale catalogue
export async function clientLoader({ request }: Route.ClientLoaderArgs) {
  const sp = new URL(request.url).searchParams;
  const qs = new URLSearchParams({ limit: "500" });
  for (const k of ["q", "type"]) if (sp.get(k)) qs.set(k, sp.get(k)!);
  const [media, graph] = await Promise.all([api<Media[]>(`/media?${qs}`), api<Graph>("/graph")]);
  return { media, graph };
}

export default function Library({ loaderData }: Route.ComponentProps) {
  const { media, graph } = loaderData;
  const [params, setParams] = useSearchParams();
  const setFilter = (k: string, v: string) =>
    setParams((p) => (v ? p.set(k, v) : p.delete(k), p), { replace: true });
  const { revalidate } = useRevalidator();
  const [adding, setAdding] = useState(false);

  return (
    <Box sx={{ p: 3, maxWidth: 1000, mx: "auto" }}>
      <Stack direction="row" spacing={2} sx={{ mb: 2 }}>
        <TextField
          size="small"
          label="Search title or creator"
          defaultValue={params.get("q") ?? ""}
          onChange={(e) => setFilter("q", e.target.value)}
          sx={{ flex: 1 }}
        />
        <TextField
          select
          size="small"
          label="Type"
          value={params.get("type") ?? ""}
          onChange={(e) => setFilter("type", e.target.value)}
          sx={{ minWidth: 140 }}
        >
          <MenuItem value="">All</MenuItem>
          {MEDIA_TYPES.map((t) => (
            <MenuItem key={t} value={t}>{TYPE_LABEL[t]}</MenuItem>
          ))}
        </TextField>
        <Button variant="contained" onClick={() => setAdding(true)}>Add media</Button>
      </Stack>
      {media.length === 0 ? (
        <Typography color="text.secondary">No media found.</Typography>
      ) : (
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Title</TableCell>
              <TableCell>Creator</TableCell>
              <TableCell>Type</TableCell>
              <TableCell>Year</TableCell>
              <TableCell>Rating</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {media.map((m) => (
              <TableRow key={m.id} hover>
                <TableCell>
                  <RouterLink to={`/media/${m.id}`} style={{ color: "inherit" }}>{m.title}</RouterLink>
                </TableCell>
                <TableCell>{m.creator}</TableCell>
                <TableCell>{TYPE_LABEL[m.media_type]}</TableCell>
                <TableCell>{m.year ?? ""}</TableCell>
                <TableCell>{m.review ? `${m.review.rating}/5` : ""}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}
      {adding && (
        <MediaDialog
          open
          onClose={() => setAdding(false)}
          onSaved={() => revalidate()}
          mediaOptions={graph.nodes}
          themeOptions={[...new Set(graph.edges.flatMap((e) => e.themes))].sort()}
        />
      )}
    </Box>
  );
}
