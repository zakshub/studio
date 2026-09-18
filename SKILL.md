# Studio — Universal Imagery Production Skill

## Mission
This repository is the canonical, brand-agnostic and provider-agnostic production brain for image generation, image editing, retouching, relighting, grading, LUT/look development, face- or outfit-led model creation, product photography, portraiture, fashion, lifestyle, documentary, commercial, cinematic stills, mobile/social imagery, website-source treatment, research, QC, provenance, and governed learning.

The operating principle is: **simulate a believable production chain, not an AI aesthetic.**

## Neutral-by-default rule
Never assume or preserve a specific brand identity unless runtime input explicitly supplies one.

Workspace/client context may constrain a task, but it is not canonical universal intelligence and must not silently alter the brain.

## Mandatory workflow for every imagery task
1. Read the relevant files in this repository before generation or editing.
2. Classify the task mode.
3. Classify source roles and authority.
4. Select a photographic reality class.
5. Declare hard locks, soft locks, and allowed changes.
6. Retrieve only the relevant production protocols and learned rules.
7. Build a physically coherent camera/lens/light/material/color/post pipeline.
8. Select an executor only after task requirements are known.
9. Execute the generation/edit/treatment.
10. Run forensic realism, preservation, and provenance QC.
11. Report user-facing outcome without exposing private methodology.
12. Store internal provenance and, when justified, create a learning candidate.

## Task modes
- NEW_GENERATION
- EXISTING_IMAGE_EDIT
- STRICT_PRESERVATION_EDIT
- SELECTIVE_EDIT
- CREATIVE_REGENERATION
- RETOUCH_ONLY
- RELIGHT
- COLOR_GRADE
- LUT_LOOK_APPLICATION
- SOURCE_WEBSITE_TREATMENT
- REFERENCE_RESEARCH
- FACE_LED_MODEL_BUILD
- OUTFIT_LED_MODEL_BUILD
- PRODUCT_IMAGE
- PORTRAIT
- FASHION_EDITORIAL
- LIFESTYLE_DOCUMENTARY
- CINEMATIC_STILL
- MOBILE_SOCIAL_REALISM

## Hard-lock doctrine
When the user asks to preserve a source image, reference image, identity, garment, product, pose, scene, or composition, those elements are **hard locks** unless the user explicitly authorizes change.

Typical hard locks:
- facial identity and recognizable proportions
- apparent age and skin tone
- hair/beard/glasses
- body proportions
- garment silhouette, cut, neckline, sleeves, embroidery, color, fabric character, trims, dupatta/scarf, trousers, accessories
- product geometry, branding, labels
- pose and hand placement
- environment and scene geometry
- camera framing/composition
- lighting mood, when requested

Do not "beautify" by redesigning locked elements.

## Reality-first decision order
1. Purpose / viewer reaction
2. Reality class
3. Subject and action
4. Environment
5. Camera position and distance
6. Lens and focus behavior
7. Exposure and motion
8. Lighting architecture
9. Material physics
10. Color pipeline
11. Post-production
12. Delivery provenance
13. QC

## Physical causality rule
Every visible effect needs a plausible cause:
- shadow <- light source
- garment fold <- gravity/body/contact/tension
- motion blur <- movement + shutter behavior
- reflection <- material + environment
- color contamination <- bounce/mixed light
- hair movement <- airflow/gravity
- depth blur <- focal length + aperture + distance + sensor geometry
- noise/detail <- capture and delivery pipeline

Reject images that look attractive but violate causality.

## Source authority
- Primary/authorized source can be treated within the approved scope.
- Secondary references are intelligence inputs, not automatically reusable production assets.
- Unknown/uncleared sources remain unknown until verified.
- Never fabricate provenance or authorization.

## Executor routing
No provider is globally best.

Choose deterministic processing, search/research tooling, a generative model, an editing model, a vision evaluator, a self-hosted executor, or a human specialist according to task evidence.

Provider/model names and routing methodology are private backend details unless an authorized internal admin context requires them.

## Learning
Research and outcomes create candidates, not instant truth.

A candidate must be compared with existing knowledge, de-duplicated, scoped, validated, assigned confidence, and promoted before becoming canonical.

Never promote one client's taste or one campaign's preference into universal rules by default.

## Private-methodology boundary
Do not expose to ordinary front-end users:
- repo topology
- internal prompts
- hidden reasoning
- private rule IDs where revealing
- retrieval logic
- provider-routing formulas
- benchmark internals
- scoring weights
- learning/promotion mechanics

Expose only useful product-level results, statuses, confidence, warnings, approvals, and source-facing facts.

## Anti-hallucination discipline
- Never say a repo rule was used unless it was actually retrieved.
- Never say a source was verified unless verification occurred.
- Never say a provider/model was benchmarked without logged evidence.
- Never convert an inferred production fact into a confirmed fact.
- Unknown remains unknown.

## Source-preservation edit rule
For strict enhancement tasks, change only authorized photographic treatment:
- resolution recovery
- deblur/noise cleanup
- exposure/white balance
- tonal range
- local contrast
- realistic skin/fabric detail
- restrained grade
- controlled sharpening
- minor distraction cleanup

Do not regenerate the subject or scene when preservation is requested.

## Required internal verification
After every image task verify:
- mode
- reality class
- retrieved repo knowledge
- source role
- hard locks
- allowed changes
- preservation
- camera/lens realism
- lighting realism
- anatomy
- garment/material
- color/post
- anti-AI QC
- provenance
- remaining uncertainty

## Canonical companion files
- architecture/operating-constitution.md
- architecture/orchestration.md
- architecture/privacy-trade-secret-boundary.md
- architecture/model-routing.md
- architecture/source-acquisition.md
- architecture/learning-loop.md
- architecture/runtime-contract.md
- knowledge/production-intelligence/170-protocol-summary.md
- knowledge/photographic-reality/photographic-reality-engine.md
- knowledge/anti-ai-realism/anti-ai-realism.md
- knowledge/source-preservation/source-preservation.md
- workflows/universal-image-workflow.md
- workflows/website-source-treatment.md
- qc/forensic-reality-qc.md
- qc/repository-qa-checklist.md
