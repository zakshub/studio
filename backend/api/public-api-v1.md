# Public API Contract v1

## Design goals
- Stable customer-facing semantics.
- No leakage of proprietary methodology.
- Async-first for long-running visual tasks.
- Idempotent where possible.
- Every response carries request/correlation IDs.

## Standard envelope
```json
{
  "data": {},
  "meta": {
    "requestId": "req_x",
    "correlationId": "cor_x"
  },
  "error": null
}
```

## Create task
POST /api/v1/tasks

Request:
```json
{
  "workspaceId": "ws_123",
  "objective": "Enhance this image while preserving the garment exactly",
  "mode": "STRICT_PRESERVATION_EDIT",
  "sourceAssetIds": ["asset_1"],
  "referenceAssetIds": [],
  "locks": {
    "hard": ["identity", "garment", "pose", "composition"],
    "soft": []
  },
  "allowedChanges": ["exposure", "white_balance", "denoise", "subtle_grade"],
  "target": {
    "type": "image",
    "aspectRatio": "4:5",
    "platform": "social"
  }
}
```

Response:
```json
{
  "data": {
    "taskId": "task_123",
    "status": "validating",
    "next": "processing"
  },
  "meta": {"requestId":"req_1","correlationId":"cor_1"},
  "error": null
}
```

## Task response
GET /api/v1/tasks/:taskId

Customer-safe fields:
- taskId
- status
- objective
- mode label
- createdAt
- progress
- resultAssetIds
- warnings
- approval status
- user actions

Explicitly excluded:
- provider/model
- internal prompt
- internal rule IDs
- repo/commit
- routing reason
- benchmark score
- hidden reasoning

## Quality summary
GET /api/v1/jobs/:jobId/quality

```json
{
  "data": {
    "status": "needs_review",
    "preservation": "passed",
    "confidence": "high",
    "warnings": [
      {"code":"MINOR_LIGHTING_VARIANCE","message":"Lighting differs slightly from the source."}
    ],
    "requiresHumanReview": true
  }
}
```

## Website source registration
POST /api/v1/sources/websites

```json
{
  "workspaceId": "ws_123",
  "url": "https://example.com",
  "role": "primary",
  "rightsStatus": "authorized"
}
```

Secondary reference:
```json
{
  "workspaceId": "ws_123",
  "url": "https://reference.example",
  "role": "secondary_reference",
  "rightsStatus": "reference_only"
}
```

## Approval
POST /api/v1/reviews/:reviewId/approve

```json
{
  "comment": "Approved for campaign use"
}
```

## Idempotency
POST endpoints that create tasks, website scans, or uploads should support:
Idempotency-Key: <opaque client key>

## Pagination
Cursor-based:
- ?cursor=
- ?limit=50

## Versioning
Breaking changes require /api/v2.
Additive fields may be introduced in v1.
