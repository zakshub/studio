# Website Source Treatment Workflow

## Goal
Use existing client imagery as production source while treating other websites as reference intelligence unless explicitly authorized.

## Flow
1. Register primary website.
2. Register optional secondary reference websites.
3. Discover assets.
4. Store source URL and source role.
5. Deduplicate and quality-screen.
6. Select candidate primary assets.
7. Determine treatment mode:
   - strict preservation
   - selective edit
   - retouch
   - grade
   - crop/reframe
   - generative edit only when authorized
8. Build locks from source.
9. Apply relevant Studio Brain intelligence.
10. Execute with deterministic processing where sufficient; route to an AI executor only where needed.
11. Run source-preservation QC.
12. Save derivative with lineage to original.
13. Present result and approval state, not private methodology.

## Secondary websites
Use for:
- composition reference
- lighting reference
- color reference
- styling reference
- category benchmark
- research observations

Do not use secondary assets as publishable derivatives by default.

## Failure rule
If treatment changes a locked garment, identity, product, environment, or composition beyond authorization, fail the output and retain the source unchanged.