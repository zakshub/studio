# Studio Brain Service Architecture v1

## Goal
Make the canonical repository consumable by FashionOS at runtime without sending the entire repository to every executor.

## Components

### Repository Sync
Reads approved canonical content from the configured repository/ref.

### Normalizer
Converts Markdown documents into structured knowledge units with:
- document ID
- section path
- knowledge domain
- authority
- scope
- tags
- version/revision
- text payload

### Indexer
Builds searchable metadata and semantic index.

### Retriever
Given Task Context, returns the smallest sufficient rule bundle.

### Conflict Resolver
Applies precedence and reports unresolved conflicts.

### Revision Manager
Pins every ProductionPlan to the brain revision used.

### Health Monitor
Reports:
- repository reachable
- last successful sync
- current indexed revision
- index freshness
- retrieval readiness

## Authority order
1. Operating constitution / invariants
2. Source authority / preservation rules
3. Task-specific canonical knowledge
4. Reality-class knowledge
5. Validated learned rules
6. Research candidates are excluded from production retrieval unless explicitly running research evaluation

## Runtime flow
Task Context
-> Retrieval Query
-> Metadata filter
-> Semantic retrieval
-> Authority ordering
-> conflict resolution
-> compact rule bundle
-> ProductionPlan

## Privacy
Repository paths and revision identifiers are internal and never returned by the public API.
