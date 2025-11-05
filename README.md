# Commander
v.0.1

Video demonstration: https://drive.google.com/file/d/1Ds7zqAlJ2sx9urdMYQNlb15su59btKz4/view?usp=sharing

A desktop toolkit for composing, inspecting, and exporting **GATE** simulation projects through a clean, PyQt6-based UI. Commander lets you build detector geometries, sources, physics/digitizer chains, and output pipelines using a structured **node tree** with rich parameter editors. It targets day‑to‑day productivity (quick iterations, presets, live validation) while staying faithful to GATE macro semantics.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Why Commander?](#why-Commander)
3. [Architecture](#architecture)
4. [Core Concepts](#core-concepts)
   - [GateObject](#gateobject)
   - [GateParameter](#gateparameter)
   - [StaticData](#staticdata)
   - [GObjectCreator](#gobjectcreator)
5. [UI Overview](#ui-overview)
6. [Project Lifecycle & Workflows](#project-lifecycle--workflows)
7. [Geometry & World Building](#geometry--world-building)
8. [Sources](#sources)
9. [Digitizer & Coincidences](#digitizer--coincidences)
10. [Distributions](#distributions)
12. [Acquisition & Random Engine](#acquisition--random-engine)
13. [Visualization Controls](#visualization-controls)
14. [JSON Model & Persistence](#json-model--persistence)
15. [Extending Commander](#extending-Commander)
16. [Folder Layout](#folder-layout)
17. [CLI Entrypoints](#cli-entrypoints)
18. [Version Compatibility (GATE 9.2 ↔ 9.3+)](#version-compatibility-gate-92--93)
19. [Quality & Testing Notes](#quality--testing-notes)
20. [Roadmap](#roadmap)
21. [License](#license)

---

## Quick Start

You have two simple ways to use CTCommander:

### A) One-click on Windows
1. **Double-click BuildAndRun.bat at the project root**
What it does automatically:

- If dist\CTCommander.exe exists → it runs it.
- If not, it creates a local .venv, installs dependencies, builds the EXE, and then runs it.
- If building an EXE isn’t possible on your machine, it runs Commander directly via Python from the .venv.

Note: The EXE is not stored in Git (it’s too large). This script builds it locally on first run. If you see a Windows SmartScreen, click More info → Run anyway.

If PowerShell is blocked:
Right-click the .bat and run it (the .bat calls PowerShell with a safe temporary policy).
If you prefer PowerShell directly, run as admin once:

*Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned*

### 2) Run from source (development)
> Useful if you want to hack on the code, try nightly features, or file detailed bug reports.

**PowerShell (Windows):**
```powershell
# From the project root (the folder that contains main.py)
python -m venv .venv
. .\.venv\Scripts\Activate.ps1

# Make sure pip operates inside the venv
python -m pip install --upgrade pip

# Install dependencies (pinned for stability)
pip install -r requirements.txt

# Run the app
python .\main.py
```

**Deactivation (optional):**
```powershell
deactivate
```

> Tip: If your global Python has admin‑locked scripts, always call `python -m pip ...` to ensure you modify pip inside the virtual environment rather than the system installation.

---

## Why Commander?

- **Faster authoring:** Build complex macro trees without memorizing command syntax.
- **Type‑safe editing:** Every field knows its widget, unit domain, and defaults.
- **Export‑ready:** Parameters map directly to GATE macros; you can keep a human‑readable JSON alongside reproducible exports.
- **Scalable:** Hierarchical node model supports large scanners with repeaters, nested daughters, and modular digitizer chains.
- **Future‑proof:** Handles both classic 9.2 style and 9.3+ parameter layouts through a small version‑normalizer.

---

## Architecture

```
Commander.py           # PyQt6 app bootstrap (MainWindow, panes, signals)
Classes/
  GateObject.py          # Node type for the hierarchy tree
  GateParameter.py       # Typed parameter with UI/rendering metadata
  StaticData.py          # Constants (units, enums, colors, etc.)
  GObjectCreator.py      # Factories/builders for nodes and parameter sets
MaterialDB/              # Material presets (user-provided database files)
build/                   # PyInstaller artifacts (ignored in VCS)
dist/                    # Packaged executables (created by build script)
```

The **UI** presents a *Hierarchy Tree* (left), *Inspector* (right), and a *Console Log* (bottom). When you select a node, the Inspector renders the corresponding `GateParameter` controls (text areas, dropdowns, checkboxes, selectors, etc.).

---

## Core Concepts

### GateObject
Represents a single node in the simulation tree (e.g., `world`, `source/mySource`, `digitizer`, `output`).

### GateParameter
A typed field rendered in the Inspector.

### StaticData
A constants hub imported where needed:
- Units: `LENGTH_UNITS`, `ANGLE_UNITS`, `TIME_UNITS`, `ENERGY_UNITS`, etc.
- Enums & option lists: `PHYSICS_LISTS`, `SOURCE_TYPES`, `COLORS`, `LINE_STYLE`, `VIEWER_TYPES`, `RANDOM_ENGINES`, `RANDOM_SEED_MODE`, `DISTRIBUTION_TYPES`, etc.
- UI helpers like `INC_EXC` (inclusive/exclusive flags for inspector rules).

### GObjectCreator
A collection of **builders** that output `GateObject` instances (and parameter lists) with consistent paths, labels, defaults, and units.

Highlights:
- **World daughters & shapes:** `create_world_daughter(name, shape, material_db)`
- **Repeaters:** `build_repeater(base_path, type)`
- **Placement/Movement:** `build_placement_parameters(base_path)`, `build_moving_parameters(base_path)`
- **Visualization:** `get_visualization_parameters(name)`
- **Root structure:** `create_gate_root()`, `create_static_objects(gate, material_db, gate_version, sd_names)`
- **Sources:** `create_source_child(name, source_type)` and specialized builders (`_build_gps_params`, `_build_pbs_params`, `_build_extended_params`, etc.)
- **Digitizer:** version‑aware `build_digitizer_manager_parameters(...)`, singles chains, coincidence sorter, and module registry.
- **Distributions:** `create_distributions_root()`, `create_distribution_child(...)`, add/read helpers.
- **Acquisition/Random:** `build_acquisition_parameters()`

A minimal *Gate version* normalizer `_norm_gv(...)` makes conditional paths predictable between 9.2 and 9.3+.

---

## UI Overview

- **Hierarchy Tree**  
  Displays the structured `GateObject` nodes. Root includes `physics`, `source`, `digitizer`, `output`, `acquisition`, `verbose`, `vis`, and `world`.
- **Inspector**  
  Renders grouped sections (e.g., Output → `[ASCII Output]`, `[ROOT Output]`, `[ROOT Online Plotter]`). Multi‑value rows like `["TextArea","DropDown","TextArea"]` encode value+unit+value patterns.
- **Console Log**  
  Shows validation messages, export traces, or runtime info from the app.

*Visual cues:* Parameters under `/vis/` can be highlighted as *visualization controls*. World daughters can include enable/disable checkboxes in the hierarchy (greyed when disabled).

---

## Project Lifecycle & Workflows

1. **Create a project** (JSON in memory).  
   The root is produced by `create_gate_root()` then populated by `create_static_objects(...)`.
2. **Define World & Geometry.**  
   Add *world daughters* (e.g., box, cylinder) via `create_world_daughter(...)`. Use *repeaters* to place arrays/rings. Set placements & movements.
3. **Add Sources.**  
   Under `/source`, insert `gps`, `PencilBeam`, `TPSPencilBeam`, `fastI124`, `fastY90`, or `Extended` using the source factory.
4. **Configure Physics & Digitizer.**  
   Pick physics list; design the singles chain by adding modules (readout, energyResolution, etc.). Configure coincidences.
5. **Outputs & Acquisition.**  
   Choose ASCII/ROOT outputs, plotter options, and acquisition timing. Configure random engine & seeding.
6. **Export Macros.**  
   The exporter (not shown here) traverses the node tree, rendering GATE commands in a deterministic order based on `GateParameter` values.

---

## Geometry & World Building

- Shapes supported (examples): `box`, `sphere`, `cylinder`, `cone`, `ellipsoid`, `elliptical tube`, `hexagon`, `wedge`, `tet-mesh-box`.
- Each shape contributes a standard set of geometry parameters (e.g., `setXLength`, `setRmax`, `setHeight`, angles for partial solids, etc.).
- **Material** is attached to the volume (`/name/setMaterial`) via dropdown bound to the loaded *MaterialDB* list.
- **Placement** helpers: translation vector, spherical translation (phi/theta/magnitude), rotation axis/angle, align‑to axis.
- **Movement** helpers: translational, rotational, orbiting, wobbling (oscillatory), eccentric rotation, and generic (from file).

**Repeaters** (`linear`, `ring`, `cubicArray`, `quadrant`, `sphere`, `genericRepeater`) automate lattice/ring distributions with intuitive labels and units.

---

## Sources

`create_source_child(name, source_type)` wires a base parameter block (activity/intensity) and a type‑specific payload built by dedicated helpers. Common helpers include unit‑aware energy, angular distributions, GPS domain/shape, placement centre, back‑to‑back emission, and voxelized phantom settings where applicable.

Special models:
- **Extended**: model switch (`sg` etc.), emission energy, fixed emission direction enable, de‑excitation gamma, positronium options.
- **fastI124 / fastY90**: focused blocks with the relevant toggles and files.

Every source exposes a *visualizer* helper row: `(count, color, pixel size)`.

---

## Digitizer & Coincidences

Two modes are supported transparently:

1. **GATE 9.2 ("classic"):**  
   - Chain lives under `/digitizer/Singles` with an `insert` dropdown and module‑specific parameter blocks.
   - Coincidence sorter under `/digitizer/Coincidences` with `setWindow`, `setMin/MaxEnergy`, etc.

2. **GATE 9.3+ (`digitizerMgr`):**  
   - Per‑SD **SinglesDigitizer** at `/gate/digitizerMgr/{SD}/SinglesDigitizer/{Singles}`.  
   - Global toggle and input collection mapping.  
   - Optional multiple Singles branches (e.g., `LESingles`, `HESingles`) with energy framing examples.

**Module registry** (shared in both worlds) includes: `adder`, `readout`, `energyResolution`, `timeResolution`, `spatialResolution`, `energyFraming`, `clustering`, `efficiency`, `pileup`, `deadtime`, `noise`, `merger`, `intrinsicResolution`, `crosstalk`, `buffer`, `gridDiscretizator`, `adderComptPhotIdeal`, `doIModel`, `timeDelay`, `multipleRejection`, `virtualSegmentation`.

Each module’s builder returns fully labeled parameters with sensible defaults and units.

---

## Distributions

A dedicated `/distributions` subtree lets you define reusable 1D/2D distributions and bind them by name: types include `Flat`, `Gaussian`, `Exponential`, `Manual`, `File`. Builders expose consistent controls like `setMin/Max`, `setMean/Sigma`, file/columns, auto‑X, and read flags.

---

## Acquisition & Random Engine

- **Events**: total primaries, per‑run primaries, or read from file.
- **Time slicing**: fixed or variable slices (add or read slice times).
- **Random**: `setEngineName`, `setEngineSeed` mode (`default`, `manual`, etc.), manual numeric seed, seed file reset.

---

## Visualization Controls

Global viewer node (`/vis`) exposes: viewer backend, pan/zoom, and viewpoint (theta/phi). Per‑object `/vis/*` parameters control color, visibility, daughter visibility, line style/width, and solid/wireframe overrides. These are emphasized in the Inspector for discoverability.

---

## JSON Model & Persistence

- Editing in the Inspector writes through to the in‑memory `GateParameter.values` attached to each `GateObject`.
- The **MainWindow** ensures changes persist into the manager’s `node_tree`; loading a project rehydrates parameters back into the Inspector with the saved state (including dropdown selections—stored as `GateParameter` defaults for dropdowns).
- Exporters transform the node tree into GATE macros; importers (optional) can re‑create the tree from saved JSON.

Recommended top‑level shape (illustrative):

```json
{
  "project": {
    "version": "1.0",
    "gate_version": "9.3.0",
    "nodes": [ /* serialized GateObject tree */ ]
  }
}
```

---

## Extending Commander

1. **Add a new module (digitizer):**
   - Implement a builder: `def _mod_newThing(base: str) -> list[GateParameter]: ...`
   - Register it in `_module_registry()`.
2. **Add a new source type:**
   - Implement `_build_mySource_params(base)` and add to `create_source_child` dispatch.
3. **Add a new world shape or repeater:**
   - Extend the `SHAPE_FIELDS` table or `build_repeater`.
4. **Add constants/options:**
   - Update `StaticData.py` (keep UI labels and units coherent).
5. **UI tweaks:**
   - Inspector grouping: add `["Label"]` rows like `"__section__/..."` to create titled blocks.

Best practice: keep *paths, labels, units, and defaults* authoritative in builders to avoid divergence between UI and exporter.

---

## Folder Layout

Your current structure typically looks like:

```
Commander/
  build/                 # pyinstaller build cache
  Classes/
  dist/                  # holds the executable
  MaterialDB/            # user/material resources
  Commander.py         # app entrypoint (GUI)
  Commander.spec       # PyInstaller spec (generated)
  project.json           # example project (optional)
  README.md
  requirements.txt
```

---

## CLI Entrypoints

- **Run the app (dev):**
  ```bash
  python Commander.py
  ```

- **Build a Windows executable:**
  Use the provided `build.ps1` (PowerShell) which handles venv, deps, and PyInstaller.

- **Docker (optional):**  
  The `Dockerfile` is included as a starting point for headless testing or CI packaging workflows.

---

## Version Compatibility (GATE 9.2 ↔ 9.3+)

A small helper `_norm_gv(gate_version)` safely normalizes inputs like `"9.3"` or `(9,3,0)` into `(major,minor,patch)`. Paths and defaults are selected accordingly:

- **9.2** → `/digitizer/Singles`, `/digitizer/{Coincidences}`
- **9.3+** → `/gate/digitizerMgr/{SD}/SinglesDigitizer/{Singles}`, `/gate/digitizerMgr/CoincidenceSorter/{Chain}` and extra mapping/disable flags

When in doubt, Commander prefers graceful fallbacks to 9.2 semantics.

---

## Quality & Testing Notes

- **Deterministic exports:** Builders define sorted parameter blocks; exporter should respect a stable traversal order.
- **Validation:** Keep lightweight validators next to builders (e.g., numeric ranges, enum membership). Emit warnings to the Console.
- **Unit safety:** Prefer providing `units` and `default_unit_index` everywhere a physical quantity is edited.
- **Regression:** Record sample JSON projects and snapshot‑test the generated macro output.

---

## Roadmap

- Input verification to prevent errors
- Developpement of the Gate Wrapper to create MAC files.
- Visual scene preview window
- Cross‑platform packaged builds (Linux/macOS)

---

## License


See LICENSE file in repository
