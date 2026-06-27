# Project Status

## Current state

| Item | Status |
|---|---|
| Design | Approved (Revision 3) |
| Project documentation | Being established |
| Application implementation | Not started |
| Django project scaffolding | Not started |
| Database migrations | Not started |
| Application code | None exists |

## Design baseline

Revision 3 of the design proposal is the approved baseline. It is captured
across the `docs/` documentation set. No further design changes are expected
before Phase 1 implementation begins.

See `docs/DECISIONS_NEEDED.md` for unresolved decisions that must be addressed
before or during specific implementation phases.

## Next intended work

**Phase 1 — Foundation**

The first feature to be implemented is rapid inbox capture:

- Django project skeleton with settings split
- Authentication (login / logout)
- Base template and navigation shell
- `InboxItem` model
- Persistent capture bar visible on all pages
- Active inbox list

The inbox capture feature will be the first spec written using
`specs/TEMPLATE.md`.

## Revision history

| Revision | Date | Summary |
|---|---|---|
| Revision 1 | 2026-06-27 | Initial design proposal |
| Revision 2 | 2026-06-27 | Corrections to entities, date semantics, app structure |
| Revision 3 | 2026-06-27 | Final corrections; approved as baseline |
| Documentation | 2026-06-27 | Permanent project documentation established |
