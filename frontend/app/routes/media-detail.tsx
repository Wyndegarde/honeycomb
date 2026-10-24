import {
  Alert,
  Box,
  Button,
  Chip,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  IconButton,
  List,
  ListItem,
  ListItemText,
  Rating,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import DeleteIcon from "@mui/icons-material/Delete";
import EditIcon from "@mui/icons-material/Edit";
import { useState } from "react";
import { Link as RouterLink, useNavigate, useRevalidator } from "react-router";

import { api, send, TYPE_LABEL, type Graph, type Link, type Media } from "../api";
import { LinkFields, linkReady, type LinkDraft } from "../components/fields";
import { MediaDialog } from "../components/media-dialog";
import type { Route } from "./+types/media-detail";

export async function clientLoader({ params }: Route.ClientLoaderArgs) {
  const [media, links, graph] = await Promise.all([
    api<Media>(`/media/${params.id}`),
    api<Link[]>(`/media/${params.id}/links?limit=500`),
    api<Graph>("/graph"),
  ]);
  return { media, links, graph };
}

export default function MediaDetail({ loaderData }: Route.ComponentProps) {
  const { media, links, graph } = loaderData;
  const navigate = useNavigate();
  const { revalidate } = useRevalidator();
  const [editing, setEditing] = useState(false);
  const [linkDraft, setLinkDraft] = useState<LinkDraft | null>(null);
  const [error, setError] = useState<string | null>(null);
  const themeOptions = [...new Set(graph.edges.flatMap((e) => e.themes))].sort();

  async function run(fn: () => Promise<unknown>) {
    setError(null);
    try {
      await fn();
      await revalidate();
      return true;
    } catch (e) {
      setError(e instanceof Error ? e.message : "Request failed");
      return false;
    }
  }

  async function saveLink() {
    const d = linkDraft!;
    const body = { themes: d.themes, note: d.note.trim() || null };
    const existing = links.some((l) => l.media_id === d.media_id);
    const ok = await run(() =>
      existing
        ? send("PATCH", `/media/${media.id}/links/${d.media_id}`, body)
        : send("POST", `/media/${media.id}/links`, { ...body, media_id: d.media_id }),
    );
    if (ok) setLinkDraft(null);
  }

  async function remove() {
    if (!confirm(`Delete "${media.title}" and its links?`)) return;
    if (await run(() => send("DELETE", `/media/${media.id}`))) navigate("/library");
  }

  const linkable = graph.nodes.filter((n) => n.id !== media.id && !links.some((l) => l.media_id === n.id));

  return (
    <Box sx={{ p: 3, maxWidth: 800, mx: "auto" }}>
      {error && <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>{error}</Alert>}
      <Stack direction="row" sx={{ alignItems: "flex-start" }}>
        <Box sx={{ flex: 1 }}>
          <Typography variant="h4">{media.title}</Typography>
          <Typography color="text.secondary">
            {media.creator} · {TYPE_LABEL[media.media_type]}
            {media.year ? ` · ${media.year}` : ""}
          </Typography>
        </Box>
        <IconButton aria-label="Edit media" onClick={() => setEditing(true)}><EditIcon /></IconButton>
        <IconButton aria-label="Delete media" onClick={remove}><DeleteIcon /></IconButton>
      </Stack>
      {media.description && <Typography sx={{ mt: 2 }}>{media.description}</Typography>}

      <ReviewEditor key={media.review?.id ?? "new"} media={media} run={run} />

      <Stack direction="row" sx={{ mt: 4, alignItems: "center" }}>
        <Typography variant="h6" sx={{ flex: 1 }}>Links</Typography>
        <Button disabled={!linkable.length} onClick={() => setLinkDraft({ media_id: null, themes: [], note: "" })}>
          Add link
        </Button>
      </Stack>
      {links.length === 0 && <Typography color="text.secondary">Not linked to anything yet.</Typography>}
      <List>
        {links.map((l) => (
          <ListItem
            key={l.media_id}
            divider
            secondaryAction={
              <>
                <IconButton aria-label="Edit link" onClick={() => setLinkDraft({ media_id: l.media_id, themes: l.themes, note: l.note ?? "" })}>
                  <EditIcon />
                </IconButton>
                <IconButton aria-label="Remove link" onClick={() => run(() => send("DELETE", `/media/${media.id}/links/${l.media_id}`))}>
                  <DeleteIcon />
                </IconButton>
              </>
            }
          >
            <ListItemText
              disableTypography
              primary={<RouterLink to={`/media/${l.media_id}`} style={{ color: "inherit" }}>{l.title}</RouterLink>}
              secondary={
                <>
                  <Stack direction="row" spacing={0.5} sx={{ my: 0.5 }}>
                    {l.themes.map((t) => <Chip key={t} size="small" label={t} />)}
                  </Stack>
                  {l.note && <Typography variant="body2" color="text.secondary">{l.note}</Typography>}
                </>
              }
            />
          </ListItem>
        ))}
      </List>

      {editing && (
        <MediaDialog open onClose={() => setEditing(false)} onSaved={() => revalidate()} media={media} mediaOptions={[]} themeOptions={[]} />
      )}
      <Dialog open={!!linkDraft} onClose={() => setLinkDraft(null)} fullWidth maxWidth="sm">
        <DialogTitle>{links.some((l) => l.media_id === linkDraft?.media_id) ? "Edit link" : "Add link"}</DialogTitle>
        <DialogContent>
          {linkDraft && (
            <Box sx={{ pt: 1 }}>
              {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
              <LinkFields
                value={linkDraft}
                onChange={setLinkDraft}
                themeOptions={themeOptions}
                // Editing keeps the other Media fixed
                options={links.some((l) => l.media_id === linkDraft.media_id) ? undefined : linkable}
              />
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setLinkDraft(null)}>Cancel</Button>
          <Button variant="contained" disabled={!linkDraft || !linkReady(linkDraft)} onClick={saveLink}>Save</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

function ReviewEditor({ media, run }: { media: Media; run: (fn: () => Promise<unknown>) => Promise<boolean> }) {
  const [rating, setRating] = useState(media.review?.rating ?? 0);
  const [body, setBody] = useState(media.review?.body ?? "");
  return (
    <Box sx={{ mt: 4 }}>
      <Typography variant="h6">Review</Typography>
      <Rating value={rating} onChange={(_, v) => setRating(v ?? 0)} />
      <TextField fullWidth multiline minRows={3} label="Write-up" value={body} onChange={(e) => setBody(e.target.value)} sx={{ my: 1 }} />
      <Stack direction="row" spacing={1}>
        <Button variant="outlined" onClick={() => run(() => send("PUT", `/media/${media.id}/review`, { rating, body: body.trim() || null }))}>
          Save review
        </Button>
        {media.review && (
          <Button color="error" onClick={() => run(() => send("DELETE", `/media/${media.id}/review`))}>
            Delete review
          </Button>
        )}
      </Stack>
    </Box>
  );
}
