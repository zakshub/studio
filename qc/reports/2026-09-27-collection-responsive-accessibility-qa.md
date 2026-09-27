# Collection responsive and accessibility QA — 2026-09-27

Result: **PASS** for responsive design and the static accessibility contract. Runtime keyboard, assistive-technology and browser validation remains open until a frontend exists.

## Deliverables

- Canonical Figma: https://www.figma.com/design/wdzD8DwmeulOeRUOqaQe64/fos-brain
- Mobile filled: `73:702`
- Mobile validation error: `73:744`
- Mobile stale conflict: `73:786`
- Accessibility annotation: `73:831`

All mobile frames are 390 x 932. Fields are 326 x 88. Primary and secondary actions are 326 x 48.

## Accessibility checks

- Linear order is documented as Menu, Objective, Preserve, Allowed changes, primary action and Back.
- Field labels stay visible. Error meaning uses an error border plus explicit helper text.
- Disabled Continue remains labeled and visually distinct.
- Stale conflict uses a visible status banner, preserves draft values and requires explicit reload.
- Screens expose task and validation state without provider names, prompts, internal rules, scoring or hidden reasoning.

## Contrast defect and fix

The token audit found:

- `danger/500` on white: 3.76:1
- prior muted `neutral/300` on white: 2.52:1

Corrections:

- Added `danger/700` for Light error text: 6.47:1 on white
- Added `danger/300` for Dark error text: 10.41:1 on neutral/950
- Mapped Light muted text to neutral/500: 4.80:1 on white
- Mapped Dark muted text to neutral/300: 7.83:1 on neutral/950
- Error borders remain danger/500

## Visual and structural QA

Initial screenshots found a wrapped mobile Preserve value and a missing validation Back label. The value was shortened without changing meaning, and the label was restored. Repeat screenshots passed.

Programmatic read-back verified:

- three Form Field instances per screen
- expected Filled, Error and Focus variants
- full-width 48px actions
- Inter-only typography
- zero detected visible child overflow

## Regression

- Command: `.\.venv\Scripts\python.exe -m pytest -q`
- Result: **84 passed, 2 known dependency deprecation warnings, 0 failed**
- Duration: 20.06s

## Remaining implementation validation

- Browser keyboard traversal and focus-visible behavior
- Screen-reader label, description, error and live-region announcements
- Browser/device contrast and zoom/reflow behavior
- Runtime submission and stale-revision API integration
