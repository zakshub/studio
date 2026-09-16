# Photographic Reality Engine

## Goal
Create or edit imagery that behaves as if it passed through a plausible real photographic chain.

## 1. Reality class
Pick the intended photographic class before choosing camera or grade. The class determines allowable polish and defects.

## 2. Subject reality
Check anatomy, asymmetry, posture, weight distribution, hand logic, gaze, micro-expression, object contact, and biomechanical plausibility.

## 3. Skin reality
Preserve variation:
- pores with non-uniform scale
- peach fuzz and fine lines where appropriate
- local pigmentation/redness
- different forehead/nose/cheek behavior
- subtle oil/specular response
- subsurface softness without waxiness
- under-eye and lip texture
Do not paste uniform pore/noise texture over the face.

## 4. Hair reality
Hair must show:
- strand groups and clumping
- variable density
- flyaways/baby hair
- scalp/root logic
- gravity/wind/humidity response
- realistic highlight ribbons
- non-perfect edges

## 5. Garment physics
Garment appearance must follow:
- fabric weight/thickness
- weave and stiffness
- drape and elasticity
- gravity folds
- tension folds
- compression folds
- bend folds
- seam/hem construction
- embroidery weight
- ironing state
- body contact
- movement and airflow
Random decorative wrinkles are a failure.

## 6. Material response
Different materials must respond differently to light.
- cotton: mostly diffuse
- silk/satin: directional sheen
- velvet: angle-dependent deep response
- metal: strong environment reflection
- glass: reflection + transmission/refraction
- wood: grain + roughness
- skin: diffuse + specular + subsurface
- painted wall: rough diffuse response
Use plausible roughness, reflectivity, translucency, wear, and aging.

## 7. Camera geometry
Specify:
- camera height
- pitch/yaw/roll
- camera-to-subject distance
- subject-to-background distance
- sensor class where relevant
Perspective is driven primarily by viewpoint/distance; focal length then frames that perspective.

## 8. Lens optics
Control:
- focal length
- aperture
- perspective/compression
- focus plane
- depth-of-field falloff
- bokeh
- edge softness
- distortion
- vignetting
- chromatic aberration
- flare/ghosting
Optical defects must be subtle and justified.

## 9. Exposure and motion
Maintain a coherent aperture / shutter / ISO relationship.
Movement in body, hair, garment and camera must agree with shutter behavior.
Do not freeze all moving details while implying a slow shutter.

## 10. Lighting physics
Define:
- source and motivation
- direction/height/angle
- apparent source size
- hardness/softness
- diffusion/feathering
- key/fill/negative fill
- rim/background/practical
- spill control
- bounce
- mixed-light color temperatures
- shadow edge/density
- highlight control
Every major shadow/highlight should be traceable to a plausible source.

## 11. Global illumination and bounce
Model light as a field:
source -> subject
source -> wall/floor -> subject
garment/environment -> skin
Expect subtle color contamination when surfaces justify it.

## 12. Environment reality
Use:
- plausible scale
- age/wear
- clutter appropriate to use
- foreground/midground/background layers
- correct contact and occlusion
- architecture/material consistency
- practical lights
- non-showroom imperfection when appropriate

## 13. Depth and atmospheric cues
Depth should be supported by:
- relative scale
- overlap
- perspective
- focus falloff
- contrast falloff
- atmosphere
- light falloff

## 14. Color pipeline
Scene light -> sensor response -> white balance -> camera profile -> base correction -> tonal curve -> HSL/color correction -> creative grade -> optional LUT/film emulation -> output color space.

LUT is not a substitute for physical realism.

## 15. Post-production
Use only enough processing to complete the production intent:
- base correction
- selective retouch
- dodge & burn
- garment/background cleanup
- local contrast
- noise control
- sharpening
- restrained grain/halation/bloom if motivated
Protect texture and avoid plasticity.

## 16. Controlled imperfection
Realism comes from plausible limits, not random dirt:
- slight focus deviation
- minor asymmetry
- non-uniform sharpness
- realistic clipping
- sensor noise
- imperfect but plausible crop
- ordinary clutter
- subtle optical softness
Imperfections must match the reality class.

## 17. Capture-to-delivery provenance
Model the visible history:
Example A: phone sensor -> computational HDR -> platform upload -> recompression -> screenshot.
Example B: full-frame RAW -> Lightroom -> retouch -> JPEG -> social platform.
Example C: cinema log -> grade -> stream encode -> screenshot.
Final detail, noise, sharpening and compression should match the chain.

## 18. Causal reality test
Ask of every important cue: **what caused this?**
If no plausible physical or production cause exists, revise/reject.
