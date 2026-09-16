# Source Preservation / Hard-Lock Editing

## Purpose
Prevent destructive "enhancement" where the system redesigns the person, garment, product, pose, environment, or composition.

## Modes
### Strict preservation
Original visual content is the source of truth. Enhancement must remain an edit, not a re-creation.

### Selective edit
Only user-authorized regions/properties may change.

### Creative regeneration
Broader redesign is allowed only when explicitly requested.

## Default hard locks in strict preservation
- identity / facial geometry
- recognizable age
- skin tone
- hair and beard
- glasses/accessories
- body proportions
- outfit design and construction
- logos/text/branding
- pose and hand position
- environment geometry
- props and furniture
- camera angle
- crop/composition
- narrative action

## Typical allowed treatment
- denoise/deblur
- resolution recovery
- exposure
- white balance
- tonal balance
- highlight/shadow recovery
- subtle local contrast
- color correction
- restrained creative grade
- realistic skin/fabric detail recovery
- controlled sharpening
- small distraction cleanup if it does not alter identity/context

## Forbidden unless explicitly authorized
- replacing the person
- changing facial structure
- changing hairstyle/beard
- changing garment color/cut/embroidery
- changing pose
- changing table/chair/architecture
- adding cinematic lighting that contradicts original scene
- rebuilding the background
- changing photographic class

## Preservation QC
Compare source vs output:
1. face geometry
2. hair/beard/glasses
3. outfit shape/details
4. body/pose/hands
5. scene objects/layout
6. framing
7. lighting direction
8. product/logo/text
If any locked element drifted, the edit fails even if aesthetically better.
