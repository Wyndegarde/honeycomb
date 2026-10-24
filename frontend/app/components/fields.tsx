import { Autocomplete, Chip, Stack, TextField } from "@mui/material";

export type MediaOption = { id: number; title: string };
export type LinkDraft = { media_id: number | null; themes: string[]; note: string };

export function ThemeInput(props: {
  value: string[];
  onChange: (v: string[]) => void;
  options: string[];
}) {
  return (
    <Autocomplete
      multiple
      freeSolo
      // Commit typed text on blur, else Save stays disabled until Enter is pressed
      autoSelect
      options={props.options}
      value={props.value}
      onChange={(_, v) => props.onChange(v.map((t) => t.trim().toLowerCase()).filter(Boolean))}
      renderValue={(v, getItemProps) =>
        v.map((t, i) => <Chip size="small" label={t} {...getItemProps({ index: i })} key={t} />)
      }
      renderInput={(p) => <TextField {...p} label="Themes" placeholder="Type a theme, press enter for more" />}
    />
  );
}

// media is fixed (shown by the parent) when `options` is omitted
export function LinkFields(props: {
  value: LinkDraft;
  onChange: (v: LinkDraft) => void;
  themeOptions: string[];
  options?: MediaOption[];
}) {
  const { value, onChange } = props;
  return (
    <Stack spacing={2}>
      {props.options && (
        <Autocomplete
          options={props.options}
          getOptionLabel={(o) => o.title}
          value={props.options.find((o) => o.id === value.media_id) ?? null}
          onChange={(_, o) => onChange({ ...value, media_id: o?.id ?? null })}
          renderInput={(p) => <TextField {...p} label="Linked media" />}
        />
      )}
      <ThemeInput
        value={value.themes}
        options={props.themeOptions}
        onChange={(themes) => onChange({ ...value, themes })}
      />
      <TextField
        label="Note"
        multiline
        minRows={2}
        value={value.note}
        onChange={(e) => onChange({ ...value, note: e.target.value })}
      />
    </Stack>
  );
}

export const linkReady = (l: LinkDraft) => l.media_id !== null && l.themes.length > 0;
