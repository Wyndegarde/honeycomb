import { type RouteConfig, index, route } from "@react-router/dev/routes";

export default [
  index("routes/graph.tsx"),
  route("library", "routes/library.tsx"),
  route("media/:id", "routes/media-detail.tsx"),
] satisfies RouteConfig;
