# Brain Sync Policy v1

## Source of truth
Default approved branch/ref is configurable server-side.

## Sync triggers
- startup
- scheduled poll
- explicit internal sync request
- repository webhook later
- manual admin refresh

## Sync algorithm
1. Fetch current repository tree/revision.
2. If unchanged, exit with no reindex.
3. Fetch changed text files only.
4. Validate UTF-8 and allowed paths.
5. Parse/normalize changed documents.
6. Rebuild affected index entries.
7. Run structural validation.
8. Atomically mark new revision active.
9. Keep prior known-good revision available for rollback.

## Failure behavior
- Never replace known-good active index with partial/failed sync.
- Mark health stale/degraded.
- Continue serving last known-good revision if policy allows.
- Emit internal audit event.

## Exclusions
- binaries
- secrets
- temporary files
- unapproved research candidates
- customer/workspace data
