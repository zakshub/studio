# Permissions and Access Model v1

## Roles

### Workspace Viewer
- view approved assets
- view completed tasks
- view safe quality summaries

### Workspace Contributor
- all Viewer permissions
- create tasks
- upload sources
- register authorized websites
- request revisions

### Workspace Approver
- all Contributor permissions
- approve/reject review items
- approve context/profile versions

### Workspace Admin
- all workspace permissions
- manage members
- manage workspace settings
- manage source registry
- manage retention within policy

### Internal Operator
Backend/internal role only.
- operational health
- failed jobs
- source ingestion diagnostics
- non-secret internal IDs
- manually retry system jobs

### Intelligence Admin
Highly restricted.
- brain revisions
- internal rule promotion
- benchmark routing data
- learning candidates
- research promotion/rejection
- provider/model configuration

### Security Admin
- credentials and secret references
- security controls
- incident response
- access audit

## Trade-secret boundary
Workspace roles must never receive:
- provider/model names by default
- internal prompts
- repo path/branch/commit
- proprietary rule topology
- routing weights
- benchmark internals
- hidden reasoning
- learning promotion mechanics

## Multi-tenant rule
Every customer entity carrying workspace_id must be authorization-filtered by workspace membership.

## Service accounts
Internal APIs require service identity and scoped permissions, not user session tokens.

## High-risk actions
Require explicit authorization and audit event:
- promote learning candidate
- change provider routing policy
- delete original source
- change rights status from unknown/reference_only to authorized
- export internal brain
- rotate secrets
