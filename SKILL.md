# Studio — Universal Imagery Production Skill

## Mission
This repository is the canonical production brain for image generation, image editing, retouching, relighting, grading, LUT/look development, face- or outfit-led model creation, product photography, portraiture, fashion, lifestyle, documentary, commercial, cinematic stills, mobile/social imagery, and other photographic workflows.

The operating principle is: **simulate a believable production chain, not an AI aesthetic.**

## Mandatory workflow for every imagery task
1. Read the relevant files in this repository before generation or editing.
2. Classify the task mode.
3. Select a photographic reality class.
4. Declare hard locks and allowed changes.
5. Select relevant production protocols.
6. Build a physically coherent camera/lens/light/material/color/post pipeline.
7. Execute the generation or edit.
8. Run forensic realism and preservation QC.
9. Report what was taken from the repo, what was changed, what was preserved, and what passed/failed verification.

## Task modes
- NEW_GENERATION
- EXISTING_IMAGE_EDIT
- STRICT_PRESERVATION_EDIT
- RETOUCH_ONLY
- RELIGHT
- COLOR_GRADE
- LUT_LOOK_APPLICATION
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

## Reality class examples
- raw smartphone capture
- smartphone portrait mode
- social/Reel frame
- documentary still
- consumer DSLR/mirrorless
- professional lifestyle
- editorial fashion
- commercial campaign
- direct-flash fashion
- medium-format editorial
- cinematic still
- film-emulated still
- compressed repost/screenshot

The selected class constrains sharpness, dynamic range, depth of field, noise, computational processing, grade, retouch intensity, and delivery artifacts.

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

## Anti-AI default
Avoid:
- plastic skin
- procedural pore overlays
- perfect semantic edges
- impossible bokeh
- fake lens compression
- inconsistent shadows
- floating feet/objects
- random wrinkles
- impossible reflections
- universal sharpness
- excessive "cinematic" teal/orange
- flawless showroom environments when the reality class is ordinary
- fake grain used as a realism shortcut
- unnecessary redesign in edit mode

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

## Required final report
After every image task, provide:
- Mode
- Reality class
- Repo knowledge used
- Hard locks
- Allowed changes
- Work applied
- Verification result
- Any remaining uncertainty/failure

## Canonical companion files
- knowledge/production-intelligence/170-protocol-summary.md
- knowledge/photographic-reality/photographic-reality-engine.md
- knowledge/anti-ai-realism/anti-ai-realism.md
- knowledge/source-preservation/source-preservation.md
- workflows/universal-image-workflow.md
- qc/forensic-reality-qc.md
