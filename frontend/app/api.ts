export const MEDIA_TYPES = [
  "book",
  "tv_show",
  "film",
  "game",
  "podcast",
  "other",
] as const;
export type MediaType = (typeof MEDIA_TYPES)[number];

export const TYPE_LABEL: Record<MediaType, string> = {
  book: "Book",
  tv_show: "TV show",
  film: "Film",
  game: "Game",
  podcast: "Podcast",
  other: "Other",
};

export type Review = {
  id: number;
  media_id: number;
  rating: number;
  body: string | null;
};
export type Media = {
  id: number;
  title: string;
  creator: string;
  media_type: MediaType;
  year: number | null;
  description: string | null;
  review: Review | null;
};
export type NewMedia = Omit<Media, "id" | "review"> & { links?: NewLink[] };
export type NewLink = { media_id: number; themes: string[]; note: string | null };
export type Link = { media_id: number; title: string; themes: string[]; note: string | null };
export type Graph = {
  nodes: Pick<Media, "id" | "title" | "creator" | "media_type" | "year">[];
  edges: { source: number; target: number; themes: string[]; note: string | null }[];
};

// FastAPI sends a string for HTTP errors and a list of {loc, msg} for 422s
function describe(detail: unknown): string | null {
  if (typeof detail === "string") return detail;
  if (!Array.isArray(detail)) return null;
  return detail
    .map((d: { loc?: (string | number)[]; msg?: string }) =>
      [d.loc?.filter((x) => x !== "body").join("."), d.msg].filter(Boolean).join(": "),
    )
    .join("; ");
}

export async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`/api${path}`, {
    ...init,
    headers: init?.body ? { "Content-Type": "application/json" } : undefined,
  });
  if (!res.ok) {
    const detail = await res.json().then((j) => j.detail).catch(() => null);
    throw new Error(describe(detail) ?? res.statusText);
  }
  return res.status === 204 ? (undefined as T) : res.json();
}

export const send = <T = unknown>(method: string, path: string, body?: unknown) =>
  api<T>(path, { method, body: body === undefined ? undefined : JSON.stringify(body) });
