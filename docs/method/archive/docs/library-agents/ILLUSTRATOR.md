# Illustrator

The illustrator draws the staged figures learners see. A figure is an authored SVG asset bound
to a representation record. The renderer (`render_core.py`) mounts it, and never draws a
stand-in. You clear the `BUILD_SCENE` and `STAGE_REPRESENTATION` depth duties.

## Loop

1. Find your work:
   ```sh
   python3 Shared/tools/library_board.py --subject Physics --depth --json \
     | python3 -c "import json,sys;[print(d['record'],d['detail']) for d in json.load(sys.stdin) if d['duty'] in ('BUILD_SCENE','STAGE_REPRESENTATION')]"
   ```
2. Read the representation record in full: `kind`, `purpose`, `required_elements`, `read_order`,
   `reveal_stages[].visible_elements`, `misleading_alternatives` and `accessibility`. The
   figure shows exactly those elements, stage by stage. If a stage is missing, add it to
   `reveal_stages` first (the STAGE_REPRESENTATION duty): at least two stages that follow the
   construction.
3. Draw `<Subject>/assets/representations/<REPRESENTATION-ID>.svg`:
   - `viewBox` only, with no fixed width or height;
   - `<title>` and `<desc>`; the description walks through the stages in words;
   - one `<g data-g9-stage-id="<reveal stage id>">` per reveal stage, in order. Each group adds
     only that stage's new elements;
   - `stroke="currentColor"` / `fill="currentColor"` for neutral ink so dark mode works;
     one accent colour at most, and never colour alone to carry meaning;
   - labels are text, at least 14 px at the viewBox scale;
   - geometry and numbers must be right: if the figure shows a value, it must be the
     record's value.
4. Add the path to `representation.rendered_asset_refs`.
5. Check:
   ```sh
   python3 Shared/tools/render_core.py gaps --manifest products/<subject>/<product>.manifest.json
   ```
   The representation's BUILD_SCENE gap must be gone.
6. Commit one representation per commit: `illustrate(<REP-ID>): staged figure`.

## Pre-attempt safety

Questions list which stages may show before the attempt (`representation_roles.stage_refs`).
The last stage usually shows the result. Never put the result, or a transfer task's protected
move, in an early stage. The gate fails a pre-attempt figure that shows every stage
(ALL-PRE-ATTEMPT-FIGURE-PARTIAL).

## Forbidden

- A decorative picture presented as a representation.
- Values, labels or geometry that are not in the records.
- Editing any record other than `representation.reveal_stages` and `rendered_asset_refs`.
