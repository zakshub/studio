# Source Record Schema

```yaml
asset_id: string
source_type: upload|primary_website|secondary_reference|internal_asset|generated|derived
source_url: string|null
parent_asset_ids: [string]
role: primary|secondary_reference|internal_approved|unknown
rights_status: authorized|reference_only|unknown
retrieved_at: datetime|null
original_filename: string|null
mime_type: string|null
width: number|null
height: number|null
content_hash: string|null
quality_flags: [string]
workspace_id: string|null
```

The system must never infer authorization merely because an asset is publicly accessible.
