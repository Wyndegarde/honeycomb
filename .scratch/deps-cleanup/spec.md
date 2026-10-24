# Spec: Simplify route dependencies

Status: ready-for-agent

## Problem Statement

The shared route dependencies file makes the developer write a factory function and a type alias for every repository. More repositories are planned, so this boilerplate will grow. The "get Media/Link or 404" helpers look like FastAPI dependencies but every route calls them by hand, so each route repeats a lookup line and the signature is misleading. Reviewing the file also surfaced a lookup-per-item pattern worth checking.

## Solution

Repositories are wired through one small generic helper, so adding a repository is a single line. The 404 helpers become real FastAPI dependencies on routes where the Media or Link is identified by path parameters, so those routes receive the loaded object directly. Where the id comes from the request body, the helpers stay as plain calls. API behaviour (status codes, messages, payloads) does not change.

## User Stories

1. As a developer adding a new repository, I want to register it in one line, so that I do not copy a factory function and an alias.
2. As a developer reading a route, I want the route signature to show that it needs an existing Media, so that I can see its preconditions at a glance.
3. As a developer writing a new path-based route, I want to declare the Media or Link as a dependency, so that I cannot forget the 404 check.
4. As a developer, I want repositories to stay free of FastAPI imports, so that they can be used and tested outside the web layer.
5. As an API client, I want a missing Media to return 404 "Media not found" on get, patch, list-links and link routes, so that behaviour is unchanged after the refactor.
6. As an API client, I want a missing Link to return 404 "Link not found" on patch and delete, so that behaviour is unchanged after the refactor.
7. As an API client, I want deleting a Media that does not exist to return 404 without extra database work, so that delete stays cheap.
8. As an API client, I want creating a Media with links to a missing Media to return 404 and save nothing, so that partial data is never stored.
9. As an API client, I want swapped Media ids on a Link route to find the same Link, so that Links stay undirected as defined in the glossary.
10. As a maintainer, I want a request that uses both a dependency and its own repository to share one session, so that reads and writes stay in one transaction.
11. As a maintainer, I want the 404 dependencies reused across routers, so that the not-found rule lives in one place.

## Implementation Decisions

- Repository wiring: the repository classes keep their current constructors taking a session and gain no FastAPI imports. The shared dependencies module gets one generic helper that takes a repository class and returns an annotated dependency type bound to the request session. The three existing repository aliases are produced by that helper. The three existing factory functions are removed. Existing route imports of the repository aliases keep working with the same names.
- The helper must keep static typing useful: route parameters annotated with the alias should still be typed as the specific repository. Verify with the project's type checker; if the generic form loses the type, keep a thin explicit alias per repository built from the helper.
- 404 as dependencies: the Media lookup is used as a dependency on routes with a path id: get Media, update Media, list Links for a Media. The Link lookup is used as a dependency on update Link and delete Link. Both helpers keep their current signatures and error messages.
- Delete Media stays as a single delete that checks whether a row was removed. It does not gain a dependency, to avoid an extra query.
- Routes where the Media id comes from the body (create Media with links, create Link) keep calling the lookup directly. Create Link also still checks its own path id.
- Create Media with links does one lookup per link today. The `links` field is already capped at 100 and has unique targets, so this is bounded. No batch lookup method is added (decision: only add it if there were no cap).
- The existing handling of a Media deleted between check and write (foreign-key error mapped to 404) stays unchanged.
- No schema, migration, or API contract changes.

## Testing Decisions

- A good test exercises only external HTTP behaviour: status code and response body for a request. It does not inspect which dependency functions were called.
- Single seam: the HTTP API through the existing async test client against the real Postgres test container. No new seams.
- Existing tests already cover 404 for: get, patch and delete Media; list Links on a missing Media; create Link with a missing source or target; patch and delete a missing Link; create Media with a missing link target and nothing saved. These must pass unchanged before and after the refactor and act as the safety net.
- Add a test only for gaps found when checking: at minimum confirm there is one for patching a Link with swapped ids returning the same Link, and one for a missing Media on patch Link. If already covered, add nothing.
- Prior art: the media and links test modules.
- Run the full backend test suite and the "Done" checklist in the backend standards skill before finishing.

## Out of Scope

- Changing the repositories' constructors or base class.
- A batch "get many" repository method and the lookup-per-link query (capped at 100, deferred).
- Changing error messages, status codes, or response shapes.
- New endpoints or schema changes.
- Reworking the session or transaction handling.

## Further Notes

- Origin: a review of the shared dependencies module. Two of its findings were dropped after reading the code: the check-then-write race is already handled by catching the foreign-key error, and Link lookup already handles both id orders because ids are sorted.
- Suggested order: confirm the existing 404 tests pass, add any gaps, introduce the repository helper, convert routes to the 404 dependencies, run the suite and type checker.
