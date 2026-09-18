# Public / Internal Ingress Boundary

## Goal
Prevent customer-facing clients from discovering or calling private intelligence methods.

## Public ingress
Only route:
- /health
- /api/v1/*

## Internal ingress
Route only on private service network:
- /internal/v1/*

## Rules
- /internal/v1 must never be exposed through public CDN/load balancer routes.
- Internal token is defense-in-depth, not a substitute for network isolation.
- FastAPI docs/OpenAPI endpoints are disabled by default in the MVP service.
- Provider/model/repository details remain internal.
- Internal logs must not be rendered into customer error responses.
- Admin tooling should use a separate authenticated internal surface rather than customer application routes.

## Deployment QA
Before production:
1. public host returns 404/403 for /internal/v1/*
2. public host returns 404 for /docs and /openapi.json
3. internal service route requires service credential
4. customer token cannot call internal route
5. reverse proxy configuration is reviewed
