# FashionOS v2 — Figma Page Map

Status: DESIGN STRUCTURE FROZEN FOR FIRST PASS

This structure intentionally hides Studio Brain methodology from ordinary customer-facing screens.

## Documentation / system pages
### 00 — Cover
Product identity and high-level positioning.

### 01 — Product Architecture
Design documentation only. Shows product modules and UX relationships, not customer runtime internals.

### 02 — Core User Flows
Primary journeys and state transitions.

### 03 — Design Foundations
Color, typography, spacing, status language, imagery, accessibility.

### 04 — Components
Reusable UI components and states.

---

## Customer product pages

### 10 — Dashboard
Screens:
- Active workspace
- New workspace
- Multiple projects/collections
- Decision/review queue
- Recent assets
- Source activity summary

Customer sees product status, not brain/provider internals.

### 11 — Source Intake
Screens:
- Upload files
- Paste URL
- Register website
- Source classification
- Rights/usage confirmation
- Intake progress
- Discovered asset selection

### 12 — Website Import
Screens:
- Primary website
- Secondary reference websites
- Scan status
- New/changed assets
- Duplicates
- Quality filters
- Select assets for treatment
- Reference-only result summary

### 13 — Collection Studio
Screens:
- Collections list
- New collection/context setup
- Collection overview
- Look detail
- Compare/refine
- Approval

### 14 — Design Intelligence
Customer-safe naming. Avoid provider/model terminology.
Screens:
- Direction
- Silhouette
- Color
- Motif/surface
- Variations
- Refine/final

### 15 — Visualization Studio
Core visual-production workspace.
Entry modes:
- Generate New
- Edit Existing
- Treat Existing
- Import From Website

Screens:
- Task setup
- Source/reference selection
- Preserve/change controls
- Visual direction
- Generate/process state
- Compare results
- Final selection

### 16 — Existing Image Treatment
Screens:
- Source image
- Preservation requirements
- Allowed improvements
- Before/after compare
- Revision history
- Final approval

Do not expose prompts, routing, provider or internal rule names.

### 17 — Campaign Studio
Screens:
- Campaign brief
- Asset sequence
- Hero/detail/motion plan
- Platform variants
- Campaign continuity review
- Export/delivery

### 18 — Assets Library
Screens:
- All assets
- Original sources
- Generated
- Treated
- Approved masters
- Versions
- Filters
- Asset detail
- User-safe lineage

### 19 — Review & Approval
Use customer-safe language rather than exposing internal forensic methodology.
Screens:
- Pending reviews
- Result compare
- Warnings
- Preservation summary
- Approve / request changes / reject
- Review history

### 20 — Workspace Settings
Customer-visible only:
- members
- workspace preferences
- approved context
- source permissions
- export preferences

No provider/repo settings.

---

## Restricted internal product pages

### 90 — Internal Operations
Not available to customers.
Screens:
- system health
- failed jobs
- ingestion queues
- QC exceptions
- source crawler status
- cost/latency summaries

### 91 — Intelligence Administration
Highly restricted.
Screens:
- knowledge freshness
- candidate learning queue
- expert-intelligence ingestion status
- benchmark status
- routing health
- canonical promotion/rejection controls

Do not expose raw hidden reasoning.

### 92 — Integration Administration
Restricted.
Screens:
- provider availability
- private integration health
- storage/database health
- source adapters
- secret-reference status

---

## Navigation principle
Customer primary nav should remain task-oriented:
Dashboard
Sources
Collections
Design
Visualization
Campaign
Assets
Review

The UI should not have a customer-facing “Studio Brain”, “GitHub Brain”, “Model Router”, “Gemini”, or “OpenAI” module.
