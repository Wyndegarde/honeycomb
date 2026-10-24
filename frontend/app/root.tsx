import {
  AppBar,
  Box,
  Button,
  CssBaseline,
  ThemeProvider,
  Toolbar,
  Typography,
  createTheme,
} from "@mui/material";
import {
  isRouteErrorResponse,
  Links,
  Meta,
  NavLink,
  Outlet,
  Scripts,
  ScrollRestoration,
} from "react-router";

import type { Route } from "./+types/root";
import "./app.css";

const theme = createTheme({ colorSchemes: { dark: true } });

export const links: Route.LinksFunction = () => [
  { rel: "preconnect", href: "https://fonts.googleapis.com" },
  { rel: "preconnect", href: "https://fonts.gstatic.com", crossOrigin: "anonymous" },
  {
    rel: "stylesheet",
    href: "https://fonts.googleapis.com/css2?family=Inter:wght@300..700&display=swap",
  },
];

export function Layout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        <meta charSet="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>Honeycomb</title>
        <Meta />
        <Links />
      </head>
      <body>
        <ThemeProvider theme={theme}>
          <CssBaseline />
          {children}
        </ThemeProvider>
        <ScrollRestoration />
        <Scripts />
      </body>
    </html>
  );
}

export function HydrateFallback() {
  return null;
}

export default function App() {
  return (
    <>
      <AppBar position="static" color="default" enableColorOnDark>
        <Toolbar>
          <Typography variant="h6" sx={{ mr: 3 }}>
            Honeycomb
          </Typography>
          <Button component={NavLink} to="/" end color="inherit">
            Graph
          </Button>
          <Button component={NavLink} to="/library" color="inherit">
            Library
          </Button>
        </Toolbar>
      </AppBar>
      <Box component="main">
        <Outlet />
      </Box>
    </>
  );
}

export function ErrorBoundary({ error }: Route.ErrorBoundaryProps) {
  const message = isRouteErrorResponse(error)
    ? error.status === 404
      ? "Page not found"
      : error.statusText
    : error instanceof Error
      ? error.message
      : "An unexpected error occurred.";
  return (
    <Box sx={{ p: 4 }}>
      <Typography variant="h5">Something went wrong</Typography>
      <Typography color="text.secondary">{message}</Typography>
      <Button component={NavLink} to="/" sx={{ mt: 2 }}>
        Back to graph
      </Button>
    </Box>
  );
}
