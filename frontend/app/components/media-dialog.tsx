import {
  Alert,
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  MenuItem,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import { useState } from "react";

import { MEDIA_TYPES, TYPE_LABEL, send, type Media, type MediaType } from "../api";
import { LinkFields, linkReady, type LinkDraft, type MediaOption } from "./fields";

const emptyLink: LinkDraft = { media_id: null, themes: [], note: "" };

// Create when `media` is absent (can add Links); edit otherwise
export function MediaDialog(props: {
  open: boolean;
  onClose: () => void;
  onSaved: (m: Media) => void;
  media?: Media;
  mediaOptions: MediaOption[];
  themeOptions: string[];
}) {
  const { media } = props;
  const [title, setTitle] = useState(media?.title ?? "");
  const [creator, setCreator] = useState(media?.creator ?? "");
  const [type, setType] = useState<MediaType>(media?.media_type ?? "book");
  const [year, setYear] = useState(media?.year?.toString() ?? "");
  const [description, setDescription] = useState(media?.description ?? "");
  const [links, setLinks] = useState<LinkDraft[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function save() {
    setBusy(true);
    setError(null);
    const body = {
      title: title.trim(),
      creator: creator.trim(),
      media_type: type,
      year: year ? Number(year) : null,
      description: description.trim() || null,
    };
    try {
      const saved = media
        ? await send<Media>("PATCH", `/media/${media.id}`, body)
        : await send<Media>("POST", "/media", {
            ...body,
            links: links.filter(linkReady).map((l) => ({
              media_id: l.media_id,
              themes: l.themes,
              note: l.note.trim() || null,
            })),
          });
      props.onSaved(saved);
      props.onClose();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Save failed");
    } finally {
      setBusy(false);
    }
  }

  const taken = new Set(links.map((l) => l.media_id));
  return (
    <Dialog open={props.open} onClose={props.onClose} fullWidth maxWidth="sm">
      <DialogTitle>{media ? "Edit media" : "Add media"}</DialogTitle>
      <DialogContent>
        <Stack spacing={2} sx={{ pt: 1 }}>
          {error && <Alert severity="error">{error}</Alert>}
          <TextField label="Title" required value={title} onChange={(e) => setTitle(e.target.value)} />
          <TextField label="Creator" required value={creator} onChange={(e) => setCreator(e.target.value)} />
          <Stack direction="row" spacing={2}>
            <TextField select label="Type" value={type} onChange={(e) => setType(e.target.value as MediaType)} sx={{ flex: 1 }}>
              {MEDIA_TYPES.map((t) => (
                <MenuItem key={t} value={t}>{TYPE_LABEL[t]}</MenuItem>
              ))}
            </TextField>
            <TextField label="Year" type="number" value={year} onChange={(e) => setYear(e.target.value)} sx={{ flex: 1 }} />
          </Stack>
          <TextField label="Description" multiline minRows={2} value={description} onChange={(e) => setDescription(e.target.value)} />
          {!media && (
            <>
              <Typography variant="subtitle2">Links</Typography>
              {links.map((l, i) => (
                <Box key={i} sx={{ p: 2, border: 1, borderColor: "divider", borderRadius: 1 }}>
                  <LinkFields
                    value={l}
                    themeOptions={props.themeOptions}
                    options={props.mediaOptions.filter((o) => o.id === l.media_id || !taken.has(o.id))}
                    onChange={(v) => setLinks(links.map((x, j) => (j === i ? v : x)))}
                  />
                  <Button size="small" color="error" onClick={() => setLinks(links.filter((_, j) => j !== i))}>
                    Remove
                  </Button>
                </Box>
              ))}
              <Box>
                <Button onClick={() => setLinks([...links, emptyLink])}>Add link</Button>
              </Box>
            </>
          )}
        </Stack>
      </DialogContent>
      <DialogActions>
        <Button onClick={props.onClose}>Cancel</Button>
        <Button variant="contained" disabled={busy || !title.trim() || !creator.trim() || links.some((l) => !linkReady(l))} onClick={save}>
          Save
        </Button>
      </DialogActions>
    </Dialog>
  );
}
