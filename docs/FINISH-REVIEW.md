# Build verification

Reviewed on 6 September 2026. The independent final reviewer returned **ship** after scoring all three requested fixes resolved: the handle is inside the terminal, link arrows stay attached on mobile, and the work-map image alternative contains the actual counts from the drawing's shared data function.

Validation completed:

- All 24 existing unit tests passed, covering data failures, public-data filtering, generated-file drift, escaping, and artifact generation.
- The checked-in activity snapshot passed offline validation.
- Generated README and all eight SVG assets matched the renderer's output.
- Desktop and mobile identity/navigation were inspected in light and dark themes. Image loading and horizontal overflow were checked in the local browser preview.
- Project screenshot provenance scan reported three rasters with none missing metadata. The seasonal GIF has a separate source record.
- Native disclosure and the local preview's width/theme controls were exercised. Preview label encoding was checked in the browser DOM.

The local preview uses the actual README HTML with approximate GitHub typography. It does not establish live GitHub sanitization, exact Markdown spacing, or a successful hosted Actions run. This review was performed before publication and did not modify a repository or public profile. The workflow becomes operational after the complete repository is published and Actions is enabled.

Reproduce the checks using the commands in [SETUP.md](SETUP.md). Design choices are recorded in [DESIGN.md](../DESIGN.md), and refresh behavior in [AUTOMATION.md](AUTOMATION.md).
