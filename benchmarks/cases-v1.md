# FashionOS Executor Benchmark Cases v1

Status: CASE CATALOG DEFINED / SOURCE ASSETS PENDING

The benchmark does not produce a global provider winner. Scores are stored by capability.

## B-001 Strict Preservation — Identity + Garment
Capability: image_edit
Required dimensions:
- identity_preservation
- garment_preservation
- pose_composition_preservation
- lighting_realism
- anti_ai

Pass condition:
No critical lock dimension <=2/5.

## B-002 Garment Detail — Embroidery
Capability: image_edit
Required dimensions:
- embroidery_structure
- seam_consistency
- garment_color
- material_realism

## B-003 Product Fidelity
Capability: image_edit
Required dimensions:
- geometry
- logo_text
- material
- source_similarity

## B-004 Fashion Editorial Generation
Capability: image_generation
Required dimensions:
- brief_adherence
- anatomy
- garment_material
- camera_lens
- lighting
- originality
- anti_ai

## B-005 Lifestyle Realism
Capability: image_generation
Required dimensions:
- physical_causality
- environment
- human_realism
- capture_plausibility
- delivery_realism

## B-006 Research / Source Extraction
Capability: research
Required dimensions:
- source_relevance
- source_authority
- claim_support
- provenance
- duplicate_rejection

## B-007 Structured Reasoning
Capability: reasoning
Required dimensions:
- constraint_adherence
- uncertainty_handling
- contradiction_handling
- decision_traceability

## B-008 Vision / QC
Capability: vision_qc
Required dimensions:
- critical_failure_recall
- false_failure_rate
- lock_violation_detection
- causality_detection
- calibration

## B-009 Typography Rendering
Capability: image_generation
Required dimensions:
- text_accuracy
- hierarchy
- layout_adherence
- visual_quality

## B-010 Video Fashion Intelligence
Capability: video_analysis
Required dimensions:
- shot_boundary_accuracy
- camera_motion
- subject_motion
- garment_motion
- continuity
- edit_rhythm

## Benchmark rules
- identical task/source contract across compared executors
- model/provider version recorded internally
- latency and cost recorded
- human acceptance can be recorded separately
- re-run on material model/version change
- no benchmark result becomes a permanent universal ranking
