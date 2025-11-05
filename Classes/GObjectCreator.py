from Classes.GateParameter import GateParameter
from Classes.GateObject import GateObject
from Classes.StaticData import (
    LENGTH_UNITS, ANGLE_UNITS, PHYSICS_LISTS, COLORS, LINE_STYLE, INC_EXC, TIME_UNITS, VIEWER_TYPES, SPEED_UNITS, ANGULAR_SPEED_UNITS, 
    FREQUENCY_UNITS, ENERGY_UNITS, SOURCE_PARTICLES, SOURCE_ENERGY_TYPES, SOURCE_ANG_TYPES, SOURCE_DOMAINS, SOURCE_SHAPES_BY_DOMAIN, 
    EXTENDED_MODELS, SOURCE_TYPES, RANDOM_ENGINES, RANDOM_SEED_MODE, DISTRIBUTION_TYPES, DIGITIZERMGR_FUNCS
)

from typing import Iterable, Sequence

class GObjectCreator():
    # ---------------------- small factories ----------------------
    ### Method to create a TextArea parameter line
    @staticmethod
    def _txt(path: str, label: str, dval, vval=None, units: list[str] | None = None, default_unit_index: int | None = None) -> GateParameter:
        return GateParameter(path, label, ["TextArea"], [dval], [dval if vval is None else vval], units, default_unit_index)

    ### Method to create a multi-TextArea parameter line
    @staticmethod
    def _txtN(path: str, label: str, n: int, dvals: Sequence, vvals: Sequence | None = None,
              units: list[str] | None = None, default_unit_index: int | None = None) -> GateParameter:
        # ensure lengths
        #turn dval into a list with a length of n. Will add 0s if dval < n
        d = list(dvals)[:n] + [0] * max(0, n-len(dvals))
        vv = (list(dvals) if vvals is None else list(vvals))
        v = vv[:n] + [0] * max(0, n - len(vv))
        return GateParameter(path, label, ["TextArea"] * n, d, v, units, default_unit_index)
    
    ### Method to create a Dropdown parameter line
    @staticmethod
    def _dd(path: str, label: str, dval, options: Iterable) -> GateParameter:
        return GateParameter(path, label, ["DropDown"], [dval], [list(options)])
    
    ### Method to create a Checkbox parameter line
    @staticmethod
    def _cb(path: str, label: str, checked: bool) -> GateParameter:
        return GateParameter(path, label, ["CheckBox"], [checked], [checked])
    
    ### Method to create a Select Button parameter line
    @staticmethod
    def _sel(path: str, label: str, dval=None, vval=None) -> GateParameter:
        return GateParameter(path, label, ["Select"], [dval], [vval])
    
    # tiny joiners
    @staticmethod
    def _geom(name: str, sub: str) -> str: return f"/{name}/geometry/{sub}"
    
    @staticmethod
    def _vis(name: str, sub: str) -> str:  return f"/{name}/vis/{sub}"
    
    
    # Gate version normalizer
    @staticmethod
    def _norm_gv(gv_input):
        """Return (major, minor, patch) with robust fallbacks."""
        if callable(gv_input):
            try:
                gv_input = gv_input()
            except Exception:
                return (9, 2, 0)

        if isinstance(gv_input, str):
            try:
                parts = [int(p) for p in gv_input.split(".") if p.strip()]
            except Exception:
                return (9, 2, 0)
            return tuple((parts + [0, 0, 0])[:3])

        try:
            parts = [int(x) for x in list(gv_input)]
            return tuple((parts + [0, 0, 0])[:3])
        except Exception:
            return (9, 2, 0)


    # Create a child GObject of the world
    @staticmethod
    def create_world_daughter(name: str, shape: str, material_db):
        g = GObjectCreator
        
        # Field templates per shape: (subpath, label, inputs_count, units, default_unit_index)
        SHAPE_FIELDS: dict[str, list[tuple[str, str, int, list[str] | None, int | None]]] = {
            "box": [
                ("setXLength", "X Length", 1, LENGTH_UNITS, 3),
                ("setYLength", "Y Length", 1, LENGTH_UNITS, 3),
                ("setZLength", "Z Length", 1, LENGTH_UNITS, 3),
            ],
            "sphere": [
                ("setRmin", "Internal Radius", 1, LENGTH_UNITS, 3),
                ("setRmax", "External Radius", 1, LENGTH_UNITS, 3),
                ("setPhiStart", "Start Phi Angle", 1, ANGLE_UNITS, 3),
                ("setDeltaPhi", "Phi Angular Span", 1, ANGLE_UNITS, 3),
                ("setThetaStart", "Start Theta Angle", 1, ANGLE_UNITS, 3),
                ("setDeltaTheta", "Theta Angular Span", 1, ANGLE_UNITS, 3),
            ],
            "cylinder": [
                ("setRmin", "Internal Radius", 1, LENGTH_UNITS, 3),
                ("setRmax", "External Radius", 1, LENGTH_UNITS, 3),
                ("setHeight", "Height", 1, LENGTH_UNITS, 3),
                ("setPhiStart", "Start Phi Angle", 1, ANGLE_UNITS, 3),
                ("setDeltaPhi", "Phi Angular Span", 1, ANGLE_UNITS, 3),
            ],
            "cone": [
                ("setRmin1", "Internal Radius 1", 1, LENGTH_UNITS, 3),
                ("setRmax1", "External Radius 1", 1, LENGTH_UNITS, 3),
                ("setRmin2", "Internal Radius 2", 1, LENGTH_UNITS, 3),
                ("setRmax2", "External Radius 2", 1, LENGTH_UNITS, 3),
                ("setHeight", "Height", 1, LENGTH_UNITS, 3),
                ("setPhiStart", "Start Phi Angle", 1, ANGLE_UNITS, 3),
                ("setDeltaPhi", "Phi Angular Span", 1, ANGLE_UNITS, 3),
            ],
            "ellipsoid": [
                ("setXLength", "Half Axis Length X", 1, LENGTH_UNITS, 3),
                ("setYLength", "Half Axis Length Y", 1, LENGTH_UNITS, 3),
                ("setZLength", "Half Axis Length Z", 1, LENGTH_UNITS, 3),
                ("setZBottomCut", "Z Bottom Cut", 1, LENGTH_UNITS, 3),
                ("setZTopCut", "Z Top Cut", 1, LENGTH_UNITS, 3),
            ],
            "elliptical tube": [
                ("setLong", "Semimajor Axis Length", 1, LENGTH_UNITS, 3),
                ("setShort", "Semiminor Axis Length", 1, LENGTH_UNITS, 3),
                ("setHeight", "Height", 1, LENGTH_UNITS, 3),
            ],
            "hexagon": [
                ("setRadius", "Radius", 1, LENGTH_UNITS, 3),
                ("setHeight", "Height", 1, LENGTH_UNITS, 3),
            ],
            "wedge": [
                ("setNarrowerXLength", "Shorter Side Length X", 1, LENGTH_UNITS, 3),
                ("setXLength", "Wedge Length X", 1, LENGTH_UNITS, 3),
                ("setYLength", "Wedge Length Y", 1, LENGTH_UNITS, 3),
                ("setZLength", "Wedge Length Z", 1, LENGTH_UNITS, 3),
            ],
            "tet-mesh-box": [
                ("setPathToELEFile", "Path to .ele File", 0, None, None),   # Select below
                ("setUnitOfLength", "Unit of Length", 1, LENGTH_UNITS, None),
                ("setPathToAttributeMap", "Path to Attribute Map", 0, None, None),
            ],
        }
                
        params: list[GateParameter] = []

        # geometry fields
        for sub, label, n, units, dui in SHAPE_FIELDS.get(shape, []):
            path = g._geom(name, sub)
            if sub.startswith("setPathTo"):
                params.append(g._sel(path, label))      # Select
            elif sub == "setUnitOfLength":
                params.append(g._dd(path, label, LENGTH_UNITS[0], LENGTH_UNITS))  # DropDown
            elif n <= 1:
                params.append(g._txt(path, label, 0, 0, units, dui))        # TextArea
            else:
                params.append(g._txtN(path, label, n, [0]*n, [0]*n, units, dui))    # Multi-TextArea

        # Material (unchanged)
        params.append(GateParameter(f"/{name}/setMaterial", "Material", ["DropDown"], [None], [material_db]))

        # Placement, Moving, Visualization (reuse your builders)
        params += GObjectCreator.build_placement_parameters(f"/{name}")
        params += GObjectCreator.build_moving_parameters(f"/{name}")
        params += GObjectCreator.get_visualization_parameters(name)

        obj = GateObject(name, "", "world", params)
        obj.subtype = shape
        return obj
    
    
    @staticmethod
    def build_repeater(base_path: str, repeater_type: str) -> list[GateParameter]:
        g = GObjectCreator
        B = f"{base_path}"
        rp = repeater_type

        if rp == "linear":
            return [
                g._txt(f"{B}/linear/setRepeatNumber", "Repeat Number", 1, 1, LENGTH_UNITS),
                g._txtN(f"{B}/linear/setRepeatVector", "Repeat Vector (X, Y, Z)", 3, [0,0,1], [0,0,1], LENGTH_UNITS),
                g._dd(f"{B}/linear/autoCenter", "Auto Center", "true", ["true","false"]),
            ]

        if rp == "ring":
            return [
                g._txt(f"{B}/ring/setRepeatNumber", "Repeat Number", 1, 1, LENGTH_UNITS),
                g._txtN(f"{B}/ring/setPoint1", "Axis Point 1 (X, Y, Z)", 3, [0,1,0], [0,1,0], LENGTH_UNITS),
                g._txtN(f"{B}/ring/setPoint2", "Axis Point 2 (X, Y, Z)", 3, [0,0,0], [0,0,0], LENGTH_UNITS),
                g._txt(f"{B}/ring/setFirstAngle", "First Angle", 0, 0, ANGLE_UNITS),
                g._txt(f"{B}/ring/setAngularSpan", "Angular Span", 360, 360, ANGLE_UNITS),
                g._cb(f"{B}/ring/enableAutoRotation", "Auto Rotation", True),
            ]

        if rp == "cubicArray":
            return [
                g._txt(f"{B}/cubicArray/setRepeatNumberX", "Repeat X", 1, 1, LENGTH_UNITS),
                g._txt(f"{B}/cubicArray/setRepeatNumberY", "Repeat Y", 1, 1, LENGTH_UNITS),
                g._txt(f"{B}/cubicArray/setRepeatNumberZ", "Repeat Z", 1, 1, LENGTH_UNITS),
                g._txtN(f"{B}/cubicArray/setRepeatVector", "Repeat Vector (X, Y, Z)", 3, [0,5,15], [0,5,15], LENGTH_UNITS),
                g._dd(f"{B}/cubicArray/autoCenter", "Auto Center", "true", ["true","false"]),
            ]

        if rp == "quadrant":
            return [
                g._txt(f"{B}/quadrant/setLineNumber", "Line Number", 5, 5, LENGTH_UNITS),
                g._txt(f"{B}/quadrant/setOrientation", "Orientation", 90, 90, ANGLE_UNITS),
                g._txt(f"{B}/quadrant/setCopySpacing", "Copy Spacing", 6, 6, LENGTH_UNITS),
                g._txt(f"{B}/quadrant/setMaxRange", "Max Range", 30, 30, LENGTH_UNITS),
            ]

        if rp == "sphere":
            return [
                g._txt(f"{B}/sphere/setRadius", "Sphere Radius", 25, 25, LENGTH_UNITS),
                g._txt(f"{B}/sphere/setRepeatNumberWithTheta", "Repeat With Theta", 10, 10, LENGTH_UNITS),
                g._txt(f"{B}/sphere/setRepeatNumberWithPhi", "Repeat With Phi", 3, 3, LENGTH_UNITS),
                g._txt(f"{B}/sphere/setThetaAngle", "Theta Angle", 36, 36, ANGLE_UNITS),
                g._txt(f"{B}/sphere/setPhiAngle", "Phi Angle", 20, 20, ANGLE_UNITS),
            ]

        if rp == "genericRepeater":
            return [
                g._sel(f"{B}/genericRepeater/setPlacementsFilename", "Placement File"),
                g._dd(f"{B}/genericRepeater/useRelativeTranslation", "Relative Translation", "1", ["0","1"]),
            ]

        return []
    
    
    @staticmethod
    def build_placement_parameters(base_path: str):
        g = GObjectCreator
        return [
            g._txtN(f"{base_path}/placement/setTranslation", "Set Translation", 3, [0,0,0], [0,0,0], LENGTH_UNITS, 3),
            g._txt(f"{base_path}/placement/setPhiOfTranslation", "Phi Angle (XY Plane)", 0, 0, ANGLE_UNITS, 3),
            g._txt(f"{base_path}/placement/setThetaOfTranslation", "Theta Angle (Z Axis)", 0, 0, ANGLE_UNITS, 3),
            g._txt(f"{base_path}/placement/setMagOfTranslation", "Translation Magnitude", 0, 0, LENGTH_UNITS, 3),
            g._dd(f"{base_path}/placement/setRotationAxis", "Rotation Axis", " - ", [" - "," X "," Y "," Z "]),
            g._txt(f"{base_path}/placement/setRotationAngle", "Rotation Angle", 0, 0, ANGLE_UNITS, 3),
            g._dd(f"{base_path}/placement/setAxis", "Axis", " - ", [" - "," X "," Y "," Z "]),
            g._dd(f"{base_path}/placement/alignToX", "Align To Axis", " - ", [" - "," X "," Y "," Z "]),
        ]

    @staticmethod
    def build_moving_parameters(base_path: str):
        g = GObjectCreator
        return [
            g._cb(f"{base_path}/moves/insert", "Enable Translational Movement", False),
            g._txtN(f"{base_path}/translation/setSpeed", "Translation Speed", 3, [0,0,0], [0,0,0], SPEED_UNITS, 1),
            g._cb(f"{base_path}/moves/insert", "Enable Rotational Movement", False),
            g._txt(f"{base_path}/rotation/setSpeed", "Rotation Speed", 0, 0, ANGULAR_SPEED_UNITS, 0),
            g._dd(f"{base_path}/rotation/setAxis", "Moving Rotation Axis", " - ", [" - "," X "," Y "," Z "]),
            g._cb(f"{base_path}/moves/insert", "Enable Orbiting Movement", False),
            g._txt(f"{base_path}/orbiting/setSpeed", "Orbiting Speed", 0, 0, ANGULAR_SPEED_UNITS, 0),
            g._txtN(f"{base_path}/orbiting/setPoint1", "Orbiting Point 1", 3, [0,0,0], [0,0,0], LENGTH_UNITS, 3),
            g._txtN(f"{base_path}/orbiting/setPoint2", "Orbiting Point 2", 3, [0,0,0], [0,0,0], LENGTH_UNITS, 3),
            g._cb(f"{base_path}/moves/insert", "Enable Wobbling Movement", False),
            g._txtN(f"{base_path}/osc-trans/setAmplitude", "Wobbling Amplitude", 3, [0,0,0], [0,0,0], LENGTH_UNITS, 3),
            g._txt(f"{base_path}/osc-trans/setFrequency", "Wobbling Frequency", 0, 0, FREQUENCY_UNITS, 0),
            g._txt(f"{base_path}/osc-trans/setPeriod", "Wobbling Period", 0, 0, TIME_UNITS, 0),
            g._txt(f"{base_path}/osc-trans/setPhase", "Wobbling Phase", 0, 0, ANGLE_UNITS, 3),
            g._cb(f"{base_path}/moves/insert", "Enable Eccentric Rotation", False),
            g._txtN(f"{base_path}/eccent-rot/setSpeed", "Eccentric Rot Shift", 3, [0,0,0], [0,0,0], LENGTH_UNITS, 3),
            g._txt(f"{base_path}/eccent-rot/setSpeed", "Eccentric Rot Speed", 0, 0, ANGULAR_SPEED_UNITS, 0),
            g._cb(f"{base_path}/moves/insert", "Enable Generic Movement", False),
            g._sel(f"{base_path}/genericMove/setPlacementsFilename", "Generic Movement Filepath"),
            g._cb(f"{base_path}/moves/insert", "Enable Generic Repeater Move", False),
            g._sel(f"{base_path}/genericRepeaterMove/setPlacementsFilename", "Generic Repeater Filepath"),
            g._cb(f"{base_path}/genericRepeaterMove/useRelativeTranslation", "Use Relative Translation", False),
        ]
    
    @staticmethod
    def get_visualization_parameters(name):
        g = GObjectCreator
        return [
            GateParameter(g._vis(name, "setColor"), "Color", ["DropDown"], [0], [COLORS], INC_EXC),
            GateParameter(g._vis(name, "setVisible"), "IsVisible", ["CheckBox"], [1], [0], INC_EXC),
            GateParameter(g._vis(name, "setDaughtersInvisible"), "Hide Daughters", ["CheckBox"], [0], [0], INC_EXC),
            GateParameter(g._vis(name, "setLineStyle"), "Line Style", ["DropDown"], [0], [LINE_STYLE], INC_EXC),
            GateParameter(g._vis(name, "setLineWidth"), "Line Width", ["TextArea"], [0], [0], INC_EXC),
            GateParameter(g._vis(name, "forceSolid"), "Force Solid", ["CheckBox"], [0], [0], INC_EXC),
            GateParameter(g._vis(name, "forceWireframe"), "Force Wireframe", ["CheckBox"], [0], [0], INC_EXC),
        ]
    
    @staticmethod
    def create_gate_root():
        parameter_list = [
            GateParameter("/geometry/setMaterialDatabase", "Material Database", ["Select"], None, None)
        ]
        gate = GateObject("gate", "/gate", "root", parameter_list)
        
        return gate
    
    @staticmethod
    def create_static_objects(gate, material_db, gate_version=(9,2,0), sd_names=None):        
        
        # Creation of the PHYSICS node
        parameter_list = [ GateParameter("/addPhysicsList", "Physics List", ["DropDown"], [PHYSICS_LISTS], [PHYSICS_LISTS]) ]
        physics = GateObject("physics", "/physics", "root", parameter_list)
        
        digitizer = GObjectCreator.create_digitizer_object(
            gate_version=gate_version,
            sd_names=sd_names or [],
            coincidence_chain="Coincidences"
        )

        distributions = GObjectCreator.create_distributions_root()        
                
        parameter_list = []
        source = GateObject("source", "/source", "root", parameter_list)
        
        output_params = GObjectCreator.build_output_parameters_grouped()
        output = GateObject("output", "/output", "root", output_params)
        
        parameter_list = GObjectCreator.build_acquisition_parameters()
        acquisition = GateObject("acquisition", "", "root", parameter_list)
        
        #TODO VERBOSE NOT IN GATE OBJECT
        parameter_list = []
        verbose = GateObject("verbose", "", "root", parameter_list)
        
        #TODO VIS
        parameter_list = [
            GateParameter("/open", "Viewer", ["DropDown"], [2], [VIEWER_TYPES]),
            GateParameter("/viewer/panTo", "Pan to", ["TextArea", "TextArea"], [0, 0], [0, 0]),
            GateParameter("/viewer/zoom", "Zoom", ["TextArea"], [0.5], [0.5]),
            GateParameter("/viewer/set/viewpointThetaPhi", "Viewing Angle", ["TextArea", "TextArea"], [90, 90], [90, 90]),
        ]
        vis = GateObject("vis", "../vis", "root", parameter_list)
        
        parameter_list = [
            GateParameter("/world/geometry/setXLength", "X Length", ["TextArea"], [0], [0], LENGTH_UNITS, 3),
            GateParameter("/world/geometry/setYLength", "Y Length", ["TextArea"], [0], [0], LENGTH_UNITS, 3),
            GateParameter("/world/geometry/setZLength", "Z Length", ["TextArea"], [0], [0], LENGTH_UNITS, 3),
            GateParameter("/world/setMaterial", "Material", ["DropDown"], None, [material_db]),
            GateParameter("/world/vis/setVisible", "SetVisible" , ["CheckBox"], [0], [0]) # 0 = False, 1 = True  GATE DOC
        ]
        
        world = GateObject("world", "", "root", parameter_list)
        
        # Add root children
        gate.add_daughter(physics)
        gate.add_daughter(source)
        gate.add_daughter(digitizer)
        #gate.add_daughter(distributions)
        gate.add_daughter(output)
        gate.add_daughter(acquisition)
        gate.add_daughter(verbose)
        gate.add_daughter(vis)
        gate.add_daughter(world)
        
        return gate
    
        
    @staticmethod
    def build_output_ascii_parameters() -> list[GateParameter]:
        """
        Parameters for Gate /output/ascii
        
        """
        
        params = [
            GateParameter("/output/ascii/enable", "Enable ASCII output", ["CheckBox"], [1], [1]),
            GateParameter("/output/ascii/setFileName", "ASCII output filename", ["TextArea"], [""], [""]),
            GateParameter("/output/ascii/setOutFileHitsFlag", "Write hits file", ["CheckBox"], [1], [1]),
            GateParameter("/output/ascii/setOutFileSinglesFlag", "Write singles file", ["CheckBox"], [1], [1]),
            GateParameter("/output/ascii/setOutFileCoincidencesFlag", "Write coincidences file", ["CheckBox"], [1], [1]),

            # Clarify the intent for the UI/exporter:
            GateParameter("/output/ascii/__digitizerName", "Digitizer name (for singles tree flag)", ["TextArea"], [""], [""]),
            GateParameter("/output/ascii/setOutFileSingles<digitizerName>Flag", "Output for singles (resolved at export)", ["CheckBox"], [1], [1]),

            GateParameter("/output/ascii/setCoincidenceMask", "Coincidence mask (0/1 …)", ["TextArea"], ["000000"], ["000000"]),
            GateParameter("/output/ascii/setSingleMask", "Single mask (0/1 …)", ["TextArea"], ["0000"], ["0000"]),
            GateParameter("/output/ascii/setOutFileSizeLimit", "File size limit (bytes)", ["TextArea"], [2000000000], [2000000000]),
        ]
        
        return params
    
    @staticmethod
    def build_output_root_parameters() -> list[GateParameter]:
        
        """
        Parameters for Gate /output/root
        """
        params = [
            # Basic parameters
            GateParameter("/output/root/enable", "Enable ROOT ouput", ["CheckBox"], [1], [1]),
            GateParameter("/output/root/setFileName", "ROOT output filename", ["TextArea"], [""], [""]),
            
            #Trees
            GateParameter("/output/root/setRootHitFlag", "Generate Hit tree", ["CheckBox"], [1], [1]),
            GateParameter("/output/root/setRootSinglesFlag", "Generate Singles tree", ["CheckBox"], [1], [1]),
            GateParameter("/output/root/setRootCoincidencesFlag", "Generate Coincidences tree", ["CheckBox"], [1], [1]),
            GateParameter("/output/root/setRootNtupleFlag", "Generate Ntuple tree", ["CheckBox"], [1], [1]),
            
            # Singles Actions after one action of the digitizer chain
            GateParameter("/output/root/setOutFileSinglesAdderFlag", "Adder Tree", ["CheckBox"], [0], [0]),
            GateParameter("/output/root/setOutFileSinglesReadoutFlag", "Readout Tree", ["CheckBox"], [0], [0]),
            GateParameter("/output/root/setOutFileSinglesSpblurringFlag", "Spblurring Tree", ["CheckBox"], [0], [0]),
            GateParameter("/output/root/setOutFileSinglesBlurringFlag", "Blurring Tree", ["CheckBox"], [0], [0]),
            GateParameter("/output/root/setOutFileSinglesThresholderFlag", "Threshholder Tree", ["CheckBox"], [0], [0]),
            GateParameter("/output/root/setOutFileSinglesUpholderFlag", "Upholder Tree", ["CheckBox"], [0], [0]),                        
        ]
        
        return params
    
    @staticmethod
    def build_output_root_plotter_parameters() -> list[GateParameter]:  
        """
        Parameters for Gate /output/plotter
        """
        params = [
            # ROOT online plotter
            GateParameter("/output/plotter/enable", "Enable ROOT online plotter", ["CheckBox"], [0], [0]),
            GateParameter("/output/plotter/showPlotter", "Show Plotter", ["CheckBox"], [0], [0]),
                # sets the number of display windows to be used
            GateParameter("/output/plotter/setNColumns", "Amount of Columns", ["TextArea"], [0], [0]),
            GateParameter("/output/plotter/setPlotHeight", "Plot Height", ["TextArea"], [0], [0]),
            GateParameter("/output/plotter/setPlotWidth", "Plot Width", ["TextArea"], [0], [0]),
                # plots an histogram previously defined in GATE
            #TODO Add other variables
        ]
        
        return params
        
        
    @staticmethod
    def build_output_parameters_grouped() -> list[GateParameter]:
        """
        Output parameters grouped in UI sections:
          - [ASCII Output]
          - [ROOT Output]
          - [ROOT Online Plotter]
        Each section starts with a Label-only GateParameter so your Inspector can
        render a titled block.
        """
        P: list[GateParameter] = []

        # --- ASCII section ---
        P.append(GateParameter("__section__/output/ascii", "[ASCII Output]", ["Label"], [""], [""]))
        P += GObjectCreator.build_output_ascii_parameters()

        # --- ROOT section ---
        P.append(GateParameter("__section__/output/root", "[ROOT Output]", ["Label"], [""], [""]))
        P += GObjectCreator.build_output_root_parameters()

        # --- Plotter section ---
        P.append(GateParameter("__section__/output/plotter", "[ROOT Online Plotter]", ["Label"], [""], [""]))
        P += GObjectCreator.build_output_root_plotter_parameters()

        return P
        
    
    # ---------- SOURCE FACTORY ----------
    @staticmethod
    def create_source_child(name: str, source_type: str) -> GateObject:
        """
        Factory for a single source under /source.
        """
        g = GObjectCreator
        st = source_type if source_type in SOURCE_TYPES else "gps"
        base = f"/source/{name}"

        # Present in ALL sources
        params: list[GateParameter] = [
            # Activity (value, unit). Using ENERGY_UNITS here to match available imports.
            g._txtN(f"{base}/setActivity", "Activity", 2, [0.0, "Bq"], [0.0, "Bq"], ENERGY_UNITS, 0),
            # Optional “intensity” (priority) when several sources and no activity
            g._txt(f"{base}/setIntensity", "Intensity (priority)", 0, 0),
        ]

        # Type-specific block via dispatch
        builder_by_type = {
            "gps":            g._build_gps_params,
            "PencilBeam":     g._build_pbs_params,
            "TPSPencilBeam":  g._build_tps_params,
            "fastI124":       g._build_fastI124_params,
            "fastY90":        g._build_fastY90_params,
            "Extended":       g._build_extended_params,
        }
        build = builder_by_type.get(st, g._build_gps_params)
        params += build(base)

        # Common visualize helper (mixed controls -> construct directly)
        params.append(
            GateParameter(
                f"{base}/visualize",
                "Visualize (count, color, px)",
                ["TextArea", "DropDown", "TextArea"],
                [0, "yellow", 2],
                [0, COLORS, 2]
            )
        )

        obj = GateObject(name, base, "source", params)
        obj.subtype = st
        obj.source_type = st
        return obj


    # ---------- SOURCE BUILDERS ----------
    @staticmethod
    def _build_gps_params(base: str) -> list:
        g = GObjectCreator
        P: list[GateParameter] = []

        # particle + ion
        P.append(g._dd(f"{base}/gps/particle", "Particle", SOURCE_PARTICLES[0], SOURCE_PARTICLES))
        P.append(g._txtN(f"{base}/gps/ion", "Ion(Z,A,Q,E_keV)", 4, [0,0,0,0], [0,0,0,0]))

        # decay helpers
        P.append(g._cb(f"{base}/setForcedUnstableFlag", "Forced Unstable", False))
        P.append(g._txt(f"{base}/setForcedHalfLife", "Half-life", 0, 0, TIME_UNITS, 0))

        # energy
        P.append(g._dd(f"{base}/gps/energytype", "Energy distribution", "Mono", SOURCE_ENERGY_TYPES))
        P.append(g._txt(f"{base}/gps/monoenergy", "Mono energy", 0, 0, ENERGY_UNITS, 1))
        P.append(g._sel(f"{base}/gps/setSpectrumFile", "UserSpectrum file"))
        P.append(g._txt(f"{base}/setIntensity", "Per-source Intensity", 0, 0))

        # angles
        P.append(g._dd(f"{base}/gps/angtype", "Angular type", SOURCE_ANG_TYPES[0], SOURCE_ANG_TYPES))
        P += [
            g._txt(f"{base}/gps/mintheta", "min theta", 0, 0, ANGLE_UNITS, 3),
            g._txt(f"{base}/gps/maxtheta", "max theta", 0, 0, ANGLE_UNITS, 3),
            g._txt(f"{base}/gps/minphi",   "min phi",   0, 0, ANGLE_UNITS, 3),
            g._txt(f"{base}/gps/maxphi",   "max phi",   0, 0, ANGLE_UNITS, 3),
        ]

        # domain + shape + dims
        P.append(g._dd(f"{base}/gps/type",  "Domain", "Point",  SOURCE_DOMAINS))
        P.append(g._dd(f"{base}/gps/shape", "Shape",  "Sphere", SOURCE_SHAPES_BY_DOMAIN["Volume"]))
        P += [
            g._txt(f"{base}/gps/radius", "radius", 0, 0, LENGTH_UNITS, 3),
            g._txt(f"{base}/gps/halfz",  "half z", 0, 0, LENGTH_UNITS, 3),
            g._txt(f"{base}/gps/halfx",  "half x", 0, 0, LENGTH_UNITS, 3),
            g._txt(f"{base}/gps/halfy",  "half y", 0, 0, LENGTH_UNITS, 3),
        ]

        # placement + attach/confine
        P.append(g._txtN(f"{base}/gps/centre", "centre (x,y,z)", 3, [0,0,0], [0,0,0], LENGTH_UNITS, 3))
        P.append(g._txt(f"{base}/attachTo",    "Attach to volume", "", ""))
        P.append(g._txt(f"{base}/gps/confine", "Confine (vol_phys)", "", ""))

        # back-to-back etc
        P.append(g._dd(f"{base}/setType", "Special type", " - ", [" - ","backtoback"]))
        P.append(g._cb(f"{base}/setAccolinearityFlag", "Accolinearity", False))
        P.append(g._txt(f"{base}/setAccoValue", "Accolinearity FWHM", 0, 0, ANGLE_UNITS, 3))
        return P

    @staticmethod
    def _build_pbs_params(base: str) -> list:
        g = GObjectCreator
        P: list[GateParameter] = []

        P.append(g._dd(f"{base}/setParticleType", "Particle", "proton", SOURCE_PARTICLES))
        P.append(g._txtN(f"{base}/setIonProperties", "Ion(Z,A,Q,E_keV)", 4, [0,0,0,0], [0,0,0,0]))

        P.append(g._txt(f"{base}/setEnergy",      "Mean Energy",  0, 0, ENERGY_UNITS, 2))
        P.append(g._txt(f"{base}/setSigmaEnergy", "Sigma Energy", 0, 0, ENERGY_UNITS, 2))

        P.append(g._txtN(f"{base}/setPosition", "Position (x,y,z)", 3, [0,0,0], [0,0,0], LENGTH_UNITS, 3))
        P += [
            g._txt(f"{base}/setSigmaX",    "Sigma X",    0, 0, LENGTH_UNITS, 3),
            g._txt(f"{base}/setSigmaY",    "Sigma Y",    0, 0, LENGTH_UNITS, 3),
            g._txt(f"{base}/setSigmaTheta","Sigma Theta",0, 0, ANGLE_UNITS,  3),
            g._txt(f"{base}/setSigmaPhi",  "Sigma Phi",  0, 0, ANGLE_UNITS,  3),
        ]

        P += [
            g._txt(f"{base}/setEllipseXThetaEmittance", "Emittance X-Theta (mm·mrad)", 0, 0),
            g._txt(f"{base}/setEllipseYPhiEmittance",   "Emittance Y-Phi (mm·mrad)",   0, 0),
            g._dd(f"{base}/setEllipseXThetaRotationNorm", "X-Theta Rotation", "negative", ["negative","positive"]),
            g._dd(f"{base}/setEllipseYPhiRotationNorm",  "Y-Phi Rotation",   "negative", ["negative","positive"]),
        ]

        P.append(g._txtN(f"{base}/setRotationAxis", "Rotation Axis (x,y,z)", 3, [0,0,0], [0,0,0]))
        P.append(g._txt(f"{base}/setRotationAngle", "Rotation Angle", 0, 0, ANGLE_UNITS, 3))
        P.append(g._cb(f"{base}/setTestFlag", "Test flag", False))
        return P

    @staticmethod
    def _build_tps_params(base: str) -> list:
        g = GObjectCreator
        P: list[GateParameter] = []

        P.append(g._dd(f"{base}/setParticleType", "Particle", "proton", SOURCE_PARTICLES))
        P.append(g._sel(f"{base}/setPlan", "Plan description file"))

        P += [
            g._txt(f"{base}/setNotAllowedFieldID", "Not allowed Field IDs (csv)", "", ""),
            g._txt(f"{base}/setAllowedFieldID",    "Allowed Field ID",            "", ""),
            g._txt(f"{base}/selectLayerID",        "Select Layer ID",             "", ""),
            g._txt(f"{base}/selectSpotID",         "Select Spot ID",              "", ""),
        ]

        P += [
            g._cb(f"{base}/setFlatGenerationFlag",       "Flat generation",        False),
            g._cb(f"{base}/setSortedSpotGenerationFlag", "Sorted spot generation", False),
        ]

        P.append(g._sel(f"{base}/setSourceDescriptionFile", "Source description file"))

        P += [
            g._cb(f"{base}/setSpotIntensityAsNbIons", "Spot intensity is #ions", True),
            g._cb(f"{base}/setBeamConvergence",       "Beam convergence",        False),
            g._cb(f"{base}/setBeamConvergenceXTheta", "Convergent X-Theta",      False),
            g._cb(f"{base}/setBeamConvergenceYPhi",   "Convergent Y-Phi",        False),
            g._cb(f"{base}/setSigmaEnergyInMeVFlag",  "SigmaEnergy in MeV",      False),
            g._cb(f"{base}/setTestFlag",              "Test flag",               False),
        ]
        return P

    @staticmethod
    def _build_extended_params(base: str) -> list:
        g = GObjectCreator
        P: list[GateParameter] = []

        P.append(g._dd(f"{base}/setType", "Extended model", "sg", EXTENDED_MODELS))
        P.append(g._txt(f"{base}/setEmissionEnergy", "Emission energy (sg only)", 511, 511, ENERGY_UNITS, 1))
        P.append(g._txtN(f"{base}/setFixedEmissionDirection", "Fixed dir (x,y,z)", 3, [0,0,1], [0,0,1]))
        P.append(g._cb(f"{base}/setEnableFixedEmissionDirection", "Enable fixed dir", False))
        P.append(g._cb(f"{base}/setEnableDeexcitation", "Enable de-excitation gamma", False))
        P.append(g._txt(f"{base}/setPromptGammaEnergy", "Prompt gamma energy", 0.0, 0.0, ENERGY_UNITS, 1))
        P.append(g._txtN(f"{base}/setPostroniumLifetime", "Positronium lifetime (pPs/oPs,value,unit)", 3, ["pPs",0.125,"ns"], ["pPs",0.125,"ns"], TIME_UNITS, 0))
        P.append(g._txtN(f"{base}/setPositroniumFraction", "Ps fraction (pPs/oPs,prob)", 2, ["pPs",0.5], ["pPs",0.5]))
        return P
    
    
    @staticmethod
    def _build_fastI124_params(base: str) -> list:
        g = GObjectCreator; P: list[GateParameter] = []

        P.append(g._dd(f"{base}/setType", "Type", "fastI124", ["fastI124"]))
        P.append(g._cb(f"{base}/setForcedUnstableFlag", "Forced Unstable", True))
        P.append(g._txt(f"{base}/setForcedHalfLife", "Half-life", 0, 0, TIME_UNITS, 0))
        return P
        
    @staticmethod
    def _build_fastY90_params(base: str) -> list:
        g = GObjectCreator; P: list[GateParameter] = []

        P.append(g._txt(f"{base}/setMinBremEnergy", "Min Brem Energy", 0, 0, ENERGY_UNITS, 1))
        P.append(g._txt(f"{base}/setPositronProbability", "Positron probability", 0, 0))
        P.append(g._sel(f"{base}/loadVoxelizedPhantom", "Load voxelized phantom (hdr)"))
        P.append(g._txtN(f"{base}/setVoxelizedPhantomPosition", "Voxel pos (x,y,z)", 3, [0,0,0], [0,0,0], LENGTH_UNITS, 3))
        return P
    
    # ---------- DIGITIZER MODULE REGISTRY ----------
    @staticmethod
    def _mod_adder(base: str) -> list:
        # Label-only informational row
        return [GateParameter(f"{base}/adder/__info",
                            "adder (energy-weighted centroid). No parameters.",
                            ["Label"], [""], [""])]

    @staticmethod
    def _mod_adderCompton(base: str) -> list:
        return [GateParameter(f"{base}/adderCompton/__info",
                            "adderCompton (>=9.3): add e- edep to previous photon in same volume; position stays at photon.",
                            ["Label"], [""], [""])]

    @staticmethod
    def _mod_readout(base: str) -> list:
        g = GObjectCreator
        return [
            g._dd(f"{base}/readout/setPolicy", "Readout policy",
                "TakeEnergyWinner", ["TakeEnergyWinner","TakeEnergyCentroid"]),
            g._txt(f"{base}/readout/setDepth", "Depth (winner policy)", 1, 1),
            g._txt(f"{base}/setReadoutVolume", "Readout volume name (alternative to depth)", "", ""),
            g._cb(f"{base}/readout/forceReadoutVolumeForEnergyCentroid",
                "Force readout volume for energy centroid", False),
        ]

    @staticmethod
    def _mod_energyResolution(base: str) -> list:
        g = GObjectCreator
        return [
            g._txt(f"{base}/energyResolution/fwhm", "FWHM (fraction @ Eref)", 0.15, 0.15),
            g._txt(f"{base}/energyResolution/energyOfReference", "Reference energy",
                511.0, 511.0, ENERGY_UNITS, 1),
            g._txt(f"{base}/energyResolution/fwhmMin", "FWHM min (fraction)", 0.0, 0.0),
            g._txt(f"{base}/energyResolution/fwhmMax", "FWHM max (fraction)", 0.0, 0.0),
            g._txt(f"{base}/energyResolution/slope", "Linear slope (1/Energy)",
                0.0, 0.0, ENERGY_UNITS, 1),
        ]

    @staticmethod
    def _mod_timeResolution(base: str) -> list:
        g = GObjectCreator
        return [
            g._txt(f"{base}/timeResolution/fwhm", "Time FWHM", 1.4, 1.4, TIME_UNITS, 0),
            g._txt(f"{base}/timeResolution/CTR",  "Coincidence Time Resolution (CTR)", 0.0, 0.0, TIME_UNITS, 0),
            g._txt(f"{base}/timeResolution/DOIdimention4CTR", "DOI dimension for CTR approx", 0.0, 0.0, LENGTH_UNITS, 3),
        ]

    @staticmethod
    def _mod_spatialResolution(base: str) -> list:
        g = GObjectCreator
        P = [
            g._txt(f"{base}/spatialResolution/fwhm",  "FWHM (isotropic)", 0.0, 0.0, LENGTH_UNITS, 3),
            g._txt(f"{base}/spatialResolution/fwhmX", "FWHM X",           0.0, 0.0, LENGTH_UNITS, 3),
            g._txt(f"{base}/spatialResolution/fwhmY", "FWHM Y",           0.0, 0.0, LENGTH_UNITS, 3),
            g._txt(f"{base}/spatialResolution/fwhmZ", "FWHM Z",           0.0, 0.0, LENGTH_UNITS, 3),
            g._cb (f"{base}/spatialResolution/confineInsideOfSmallestElement",
                "Confine inside smallest element", True),
            g._cb (f"{base}/spatialResolution/useTruncatedGaussian",
                "Use truncated Gaussian near edges", True),
            g._dd (f"{base}/spatialResolution/nameAxis",
                "Distribution axis (for 2D map)", "XY", ["XY"]),
            g._txt(f"{base}/spatialResolution/fwhmDistrib2D",
                "2D FWHM distribution name", "", ""),
            g._txt(f"{base}/spatialResolution/fwhmYdistrib",
                "1D FWHM distribution for Y", "", ""),
        ]
        return P

    @staticmethod
    def _mod_energyFraming(base: str) -> list:
        g = GObjectCreator
        return [
            g._txt(f"{base}/energyFraming/setMin", "Energy min", 0.0, 0.0, ENERGY_UNITS, 1),
            g._txt(f"{base}/energyFraming/setMax", "Energy max", 0.0, 0.0, ENERGY_UNITS, 1),
            g._dd (f"{base}/energyFraming/setLaw", "Energy policy (law)", "classic",
                ["classic","solidAngleWeighted"]),
            g._txt(f"{base}/energyFraming/solidAngleWeighted/setRentangleLengthX",
                "Pixel length X (solidAngleWeighted)", 0.0, 0.0, LENGTH_UNITS, 3),
            g._txt(f"{base}/energyFraming/solidAngleWeighted/setRentangleLengthY",
                "Pixel length Y (solidAngleWeighted)", 0.0, 0.0, LENGTH_UNITS, 3),
            g._txt(f"{base}/energyFraming/solidAngleWeighted/setZSense4Readout",
                "Z sense for readout (+1 or -1; length-like)", 0.0, 0.0, LENGTH_UNITS, 3),
        ]

    @staticmethod
    def _mod_clustering(base: str) -> list:
        g = GObjectCreator
        return [
            g._txt(f"{base}/clustering/setAcceptedDistance", "Accepted distance", 5.0, 5.0, LENGTH_UNITS, 3),
            g._cb (f"{base}/clustering/setRejectionMultipleClusters",
                "Reject events with multiple clusters (same vol)", False),
        ]

    @staticmethod
    def _mod_efficiency(base: str) -> list:
        g = GObjectCreator
        return [
            g._txt(f"{base}/efficiency/setUniqueEfficiency", "Unique efficiency (0..1)", 1.0, 1.0),
            g._dd (f"{base}/efficiency/setMode", "Mode", "unique", ["unique","energy","crystal"]),
            g._txt(f"{base}/efficiency/setEfficiency", "Efficiency distribution name", "", ""),
            g._txt(f"{base}/efficiency/enableLevel",  "Enable level (hierarchy index)", 0, 0),
            g._txt(f"{base}/efficiency/disableLevel", "Disable level (hierarchy index)", 0, 0),
        ]

    @staticmethod
    def _mod_pileup(base: str) -> list:
        g = GObjectCreator
        return [
            g._txt(f"{base}/pileup/setDepth",       "Pile-up depth (hierarchy index)", 1, 1),
            g._txt(f"{base}/pileup/setPileupVolume","Pile-up volume name (alternative to depth)", "", ""),
            g._txt(f"{base}/pileup/setPileup",      "Signal formation time", 100.0, 100.0, TIME_UNITS, 0),
        ]

    @staticmethod
    def _mod_deadtime(base: str) -> list:
        g = GObjectCreator
        return [
            g._txt(f"{base}/deadtime/setDeadTime", "Dead time", 100000.0, 100000.0, TIME_UNITS, 0),
            g._dd (f"{base}/deadtime/setMode", "Dead-time model", "paralysable",
                ["paralysable","nonparalysable"]),
            g._txt(f"{base}/deadtime/chooseDTVolume", "Dead-time volume name", "", ""),
            g._txt(f"{base}/deadtime/setBufferSize",  "Buffer size (value, unit)", 1, 1),   # UI label mentions units ("MB")
            g._txt(f"{base}/deadtime/setBufferMode",  "Buffer mode (0: shared, 1: freed-on-send)", 0, 0),
        ]

    @staticmethod
    def _mod_noise(base: str) -> list:
        g = GObjectCreator
        return [
            g._txt(f"{base}/noise/setDeltaTDistribution", "Inter-event Δt distribution name", "", ""),
            g._txt(f"{base}/noise/setEnergyDistribution", "Energy distribution name", "", ""),
        ]

    @staticmethod
    def _mod_merger(base: str) -> list:
        g = GObjectCreator
        return [
            g._dd (f"{base}/insert", "Insert module", "merger", ["merger"]),
            g._txt(f"{base}/addInput", "Add Singles input (e.g. Singles_crystal1)", "", ""),
            # (UI can repeat addInput row to accept multiple inputs)
        ]

    @staticmethod
    def _mod_intrinsicResolution(base: str) -> list:
        g = GObjectCreator
        return [
            g._dd (f"{base}/insert", "Insert module", "intrinsicResolution", ["intrinsicResolution"]),
            g._txt(f"{base}/intrinsicResolution/setIntrinsicResolution",
                "Intrinsic resolution (fraction, e.g. 0.088)", 0.088, 0.088),
            g._txt(f"{base}/intrinsicResolution/setEnergyOfReference",
                "Energy of reference", 511, 511, ENERGY_UNITS, 1),
            g._txt(f"{base}/intrinsicResolution/setTECoef",
                "Transfer efficiency (0..1)", 0.28, 0.28),
            g._txt(f"{base}/intrinsicResolution/setLightOutput",
                "Light yield (photons per MeV)", 27000, 27000),
            g._txt(f"{base}/intrinsicResolution/setUniqueQE",
                "Quantum efficiency (0..1)", 0.10, 0.10),
            g._txt(f"{base}/intrinsicResolution/setXtalkEdgesFraction",
                "Crosstalk fraction to edges", 0.10, 0.10),
            g._txt(f"{base}/intrinsicResolution/setXtalkCornersFraction",
                "Crosstalk fraction to corners", 0.05, 0.05),
            g._sel(f"{base}/intrinsicResolution/useFileDataForQE",
                "QE file (per module, 8x8 etc.)"),
        ]

    @staticmethod
    def _mod_crosstalk(base: str) -> list:
        g = GObjectCreator
        return [
            g._dd (f"{base}/insert", "Insert module", "crosstalk", ["crosstalk"]),
            g._txt(f"{base}/crosstalk/setEdgesFraction",   "Edges energy fraction",   0.10, 0.10),
            g._txt(f"{base}/crosstalk/setCornersFraction", "Corners energy fraction", 0.05, 0.05),
        ]

    @staticmethod
    def _mod_buffer(base: str) -> list:
        g = GObjectCreator
        return [
            g._dd (f"{base}/insert", "Insert module", "buffer", ["buffer"]),
            g._txt(f"{base}/buffer/setBufferSize",   "Buffer size (count of Singles)", 64, 64),  # UI label mentions unit "B"
            g._txt(f"{base}/buffer/setReadFrequency","Read frequency", 10, 10, FREQUENCY_UNITS, 0),
            g._txt(f"{base}/buffer/setMode",         "Read mode (0: event-by-event, 1: empty whole buffer)", 1, 1),
        ]

    @staticmethod
    def _mod_gridDiscretizator(base: str) -> list:
        g = GObjectCreator
        return [
            g._dd (f"{base}/insert", "Insert module", "gridDiscretizator", ["gridDiscretizator"]),
            g._txt(f"{base}/gridDiscretizator/setNumberStripsX", "Number of strips/pixels X", 1, 1),
            g._txt(f"{base}/gridDiscretizator/setNumberStripsY", "Number of strips/pixels Y", 1, 1),
            g._txt(f"{base}/gridDiscretizator/setStripOffsetX",  "Strip offset X",  0.0, 0.0, LENGTH_UNITS, 3),
            g._txt(f"{base}/gridDiscretizator/setStripOffsetY",  "Strip offset Y",  0.0, 0.0, LENGTH_UNITS, 3),
            g._txt(f"{base}/gridDiscretizator/setStripOffsetZ",  "Strip offset Z",  0.0, 0.0, LENGTH_UNITS, 3),
            g._txt(f"{base}/gridDiscretizator/setStripWidthX",   "Strip/pixel width X", 0.3, 0.3, LENGTH_UNITS, 3),
            g._txt(f"{base}/gridDiscretizator/setStripWidthY",   "Strip/pixel width Y", 0.3, 0.3, LENGTH_UNITS, 3),
            g._txt(f"{base}/gridDiscretizator/setStripWidthZ",   "Strip/pixel width Z", 0.3, 0.3, LENGTH_UNITS, 3),
            g._txt(f"{base}/gridDiscretizator/setNumberReadOutBlocksX", "Readout blocks X", 1, 1),
            g._txt(f"{base}/gridDiscretizator/setNumberReadOutBlocksY", "Readout blocks Y", 1, 1),
        ]

    @staticmethod
    def _mod_adderComptPhotIdeal(base: str) -> list:
        g = GObjectCreator
        return [
            g._dd (f"{base}/insert", "Insert module", "adderComptPhotIdeal", ["adderComptPhotIdeal"]),
            g._cb (f"{base}/adderComptPhotIdeal/rejectEvtOtherProcesses",
                "Reject events with other processes", False),
        ]

    @staticmethod
    def _mod_doIModel(base: str) -> list:
        g = GObjectCreator
        return [
            g._dd (f"{base}/insert", "Insert module", "doIModel", ["doIModel"]),
            g._txtN(f"{base}/doIModel/setAxis", "DoI growth axis (x,y,z)", 3, [0,0,1], [0,0,1]),
            g._dd (f"{base}/doIModel/setDoIModel", "DoI model", "dualLayer", ["dualLayer","DoIBlurrNegExp"]),
            g._txt(f"{base}/doIModel/DoIBlurrNegExp/setExpInvDecayConst",
                "Exp inverse decay constant", 1.4, 1.4, LENGTH_UNITS, 3),
            g._txt(f"{base}/doIModel/DoIBlurrNegExp/setCrysEntranceFWHM",
                "FWHM at entrance (max uncertainty)", 1.4, 1.4, LENGTH_UNITS, 3),
        ]

    @staticmethod
    def _mod_timeDelay(base: str) -> list:
        g = GObjectCreator
        return [
            g._dd (f"{base}/insert", "Insert module", "timeDelay", ["timeDelay"]),
            g._txt(f"{base}/timeDelay/setTimeDelay", "Time delay", 12, 12, TIME_UNITS, 0),
        ]

    @staticmethod
    def _mod_multipleRejection(base: str) -> list:
        g = GObjectCreator
        return [
            g._dd (f"{base}/insert", "Insert module", "multipleRejection", ["multipleRejection"]),
            g._dd (f"{base}/multipleRejection/setMultipleDefinition",
                "Multiplicity definition", "volumeID", ["volumeID","volumeName"]),
            g._cb (f"{base}/multipleRejection/setEventRejection",
                "Reject whole event (1) or only local pulses (0)", True),
        ]

    @staticmethod
    def _mod_virtualSegmentation(base: str) -> list:
        g = GObjectCreator
        return [
            g._dd (f"{base}/insert", "Insert module", "virtualSegmentation", ["virtualSegmentation"]),
            g._dd (f"{base}/virtualSegmentation/nameAxis", "Axes to segment", "XYZ",
                ["X","Y","Z","XY","XZ","YZ","XYZ"]),
            g._txt(f"{base}/virtualSegmentation/pitch",  "Pitch (all axes)", 1.0, 1.0, LENGTH_UNITS, 3),
            # These three kept with mm unit and None default to match previous behavior
            g._txt(f"{base}/virtualSegmentation/pitchX", "Pitch X (override)", None, None, LENGTH_UNITS, 3),
            g._txt(f"{base}/virtualSegmentation/pitchY", "Pitch Y (override)", None, None, LENGTH_UNITS, 3),
            g._txt(f"{base}/virtualSegmentation/pitchZ", "Pitch Z (override)", None, None, LENGTH_UNITS, 3),
            g._cb (f"{base}/virtualSegmentation/useMacroGenerator",
                "Generate segmented geometry macro", False),
        ]

    @staticmethod
    def _module_registry() -> dict[str, callable]:
        # central map: module -> builder (unchanged)
        return {
            "adder":                 GObjectCreator._mod_adder,
            "adderCompton":          GObjectCreator._mod_adderCompton,
            "readout":               GObjectCreator._mod_readout,
            "energyResolution":      GObjectCreator._mod_energyResolution,
            "timeResolution":        GObjectCreator._mod_timeResolution,
            "spatialResolution":     GObjectCreator._mod_spatialResolution,
            "energyFraming":         GObjectCreator._mod_energyFraming,
            "clustering":            GObjectCreator._mod_clustering,
            "efficiency":            GObjectCreator._mod_efficiency,
            "pileup":                GObjectCreator._mod_pileup,
            "deadtime":              GObjectCreator._mod_deadtime,
            "noise":                 GObjectCreator._mod_noise,
            "merger":                GObjectCreator._mod_merger,
            "intrinsicResolution":   GObjectCreator._mod_intrinsicResolution,
            "crosstalk":             GObjectCreator._mod_crosstalk,
            "buffer":                GObjectCreator._mod_buffer,
            "gridDiscretizator":     GObjectCreator._mod_gridDiscretizator,
            "adderComptPhotIdeal":   GObjectCreator._mod_adderComptPhotIdeal,
            "doIModel":              GObjectCreator._mod_doIModel,
            "timeDelay":             GObjectCreator._mod_timeDelay,
            "multipleRejection":     GObjectCreator._mod_multipleRejection,
            "virtualSegmentation":   GObjectCreator._mod_virtualSegmentation,
        }

    @staticmethod
    def build_acquisition_parameters() -> list[GateParameter]:
        """
        Parameters for /gate/application and /gate/random (regular and variable-slice modes).
        """
        g = GObjectCreator
        P: list[GateParameter] = []

        # Events control
        P.append(g._txt("/application/setTotalNumberOfPrimaries",
                        "Total primaries (split over time)", "NaN", "NaN"))
        P.append(g._txt("/application/setNumberOfPrimariesPerRun",
                        "Primaries per slice (weight by duration)", "NaN", "NaN"))
        P.append(g._sel("/application/readNumberOfPrimariesInAFile",
                        "Primaries per slice (from file)"))

        # Regular time-slice mode
        P += [
            g._txt("/application/setTimeSlice", "Time slice", 1, 1, TIME_UNITS, 0),
            g._txt("/application/setTimeStart", "Time start", 0, 0, TIME_UNITS, 0),
            g._txt("/application/setTimeStop",  "Time stop",  2, 2, TIME_UNITS, 0),
        ]

        # Variable time-slice mode
        P += [
            g._sel("/application/readTimeSlicesIn", "Read slice times (file)"),
            g._txt("/application/addSlice", "Add slice (value, unit)", 0, 0, TIME_UNITS, 0),
        ]

        # Seed mode + optional numeric seed (used when mode == 'manual')
        P += [
            g._dd("/random/setEngineSeed", "Seed mode", "default", RANDOM_SEED_MODE),
            g._txt("/random/setEngineSeed (manual value)", "Manual seed (0..900000000)", 0, 0),
            g._dd("/random/setEngineName", "Random engine", "JamesRandom", RANDOM_ENGINES),
            g._sel("/random/resetEngineFrom", "Reset engine from seed file"),
        ]
        return P
    
    # Base paths for Gate 9.2
    @staticmethod
    def _digitizer_base_92() -> str:
        return "/gate/digitizer/Singles"

    @staticmethod
    def _coincidence_base_92(chain_name: str = "Coincidences") -> str:
        return f"/gate/digitizer/{chain_name}"

    @staticmethod
    def coincidence_base(gate_version, chain_name: str = "Coincidences") -> str:
        gv = GObjectCreator._norm_gv(gate_version)
        if gv >= (9, 3, 0):
            return f"/gate/digitizerMgr/CoincidenceSorter/{chain_name}"
        return GObjectCreator._coincidence_base_92(chain_name)

    @staticmethod
    def singles_digitizer_base(
        gate_version: tuple[int, int] | tuple[int, int, int],
        sd_name: str,
        singles_digitizer_name: str = "Singles",
    ) -> str | None:
        gv = GObjectCreator._norm_gv(gate_version)
        if gv >= (9, 3, 0):
            return f"/gate/digitizerMgr/{sd_name}/SinglesDigitizer/{singles_digitizer_name}"
        return None


    @staticmethod
    def build_digitizer_manager_parameters(
        gate_version: tuple[int, int] | tuple[int, int, int],
        sd_names: list[str] | None = None,
        coincidence_chain: str = "Coincidences"
    ) -> list[GateParameter]:
        g = GObjectCreator
        params: list[GateParameter] = []
        gv = GObjectCreator._norm_gv(gate_version)
        sd_list = (sd_names or ["crystal"])

        # 3.2.3 — global disable (>=9.3)
        if gv >= (9, 3, 0):
            params.append(g._cb("/gate/digitizerMgr/disable",
                                "Disable entire Digitizer (>=9.3)", False))

            # 3.2.1/3.2.2 — SinglesDigitizer input collection (per SD)
            for sd in sd_list:
                sd_base = g.singles_digitizer_base(gate_version, sd, "Singles")
                params.append(g._dd(f"{sd_base}/setInputCollection",
                                    f"SinglesDigitizer input (SD='{sd}')",
                                    "Singles", ["Singles"]))

        # CoincidenceSorter input collection
        coinc_base = g.coincidence_base(gate_version, chain_name=coincidence_chain)
        if gv >= (9, 3, 0):
            singles_options = [f"Singles_{sd}" for sd in sd_list]
            default_value = singles_options[0]
        else:
            singles_options = ["Singles"]
            default_value = "Singles"

        params.append(g._dd(f"{coinc_base}/setInputCollection",
                            "CoincidenceSorter: Input Singles collection",
                            default_value, singles_options))
        return params


    # Coincidence sorter (Gate 9.2)
    @staticmethod
    def build_coincidence_parameters_92(chain_name: str = "Coincidences") -> list[GateParameter]:
        g = GObjectCreator
        C = g._coincidence_base_92(chain_name)
        P: list[GateParameter] = []

        P += [
            g._txt(f"{C}/setWindow",     "Coincidence window",      4.0, 4.0, TIME_UNITS, 0),
            g._txt(f"{C}/setMinEnergy",  "Energy min",              350, 350, ENERGY_UNITS, 1),
            g._txt(f"{C}/setMaxEnergy",  "Energy max",              650, 650, ENERGY_UNITS, 1),
            g._cb (f"{C}/setMultiWindow","Reject multiple hits in window", False),
            g._txt(f"{C}/setOffset",     "Time offset (optional)",  0.0, 0.0, TIME_UNITS, 0),
        ]
        P.append(g._dd(f"{C}/setInputCollection", "Input Singles collection",
                    "Singles", ["Singles"]))
        return P


    # --- create_digitizer_object stays the same; it will inherit the new params ---
    @staticmethod
    def create_digitizer_object(
        gate_version: tuple[int, int] | tuple[int, int, int],
        sd_names: list[str] | None = None,
        coincidence_chain: str = "Coincidences"
    ) -> "GateObject":
        parameter_list = GObjectCreator.build_digitizer_manager_parameters(
            gate_version=gate_version,
            sd_names=sd_names or [],
            coincidence_chain=coincidence_chain
        )

        # Show one basic Singles chain UI for the first SD so users have modules to edit
        first_sd = (sd_names or ["crystal"])[0]
        parameter_list += GObjectCreator._build_basic_singles_chain_params(
            gate_version=gate_version,
            sd_name=first_sd,
            singles_name="Singles"
        )

        # (Optional) add the LESingles/HESingles example for >= 9.3
        gv = GObjectCreator._norm_gv(gate_version)
        if gv >= (9,3,0):
            parameter_list += GObjectCreator.build_multiple_singles_branches(
                gate_version=gate_version,
                sd_name=first_sd,
                singles_name="Singles",
            )

        return GateObject("digitizer", "/digitizer", "root", parameter_list)


    @staticmethod
    def create_distributions_root() -> GateObject:
        # Root holder for /gate/distributions
        return GateObject("distributions", "/distributions", "root", [])
    
    @staticmethod
    def create_default_distributions_children() -> list[GateObject]:
        return [
            GObjectCreator.create_distribution_child("my_gauss", "Gaussian"),
            GObjectCreator.create_distribution_child("energy_eff_distrib", "File"),
            GObjectCreator.create_distribution_child("my_distrib2D", "File"),
        ]
        
    @staticmethod
    def add_distribution_under_root(distributions_node: "GateObject", name: str, dtype: str) -> "GateObject":
        kids = getattr(distributions_node, "daughters", [])
        existing = {c.get_name() for c in kids}
        base_name = (name or "").strip() or "distribution"
        new_name, i = base_name, 2
        while new_name in existing:
            new_name = f"{base_name}_{i}"
            i += 1
        child = GObjectCreator.create_distribution_child(new_name, dtype)
        distributions_node.add_daughter(child)
        return child

    @staticmethod
    def create_distribution_child(name: str, dtype: str) -> GateObject:
        """
        Create a single distribution under /distributions with type-specific parameters.
        dtype ∈ ["Flat", "Gaussian", "Exponential", "Manual", "File"].
        """
        g = GObjectCreator
        t = dtype if dtype in DISTRIBUTION_TYPES else "Flat"
        base = f"/distributions/{name}"
        P: list[GateParameter] = []

        # Editable name + read-only type
        P.append(g._txt("/distributions/name", "Distribution name", name, name))
        P.append(GateParameter("/distributions/insert", "Distribution type",
                            ["Label"], [t], [t]))

        match t:
            case "Flat":
                P += [
                    g._txt(f"{base}/setMin",       "min",       0, 0),
                    g._txt(f"{base}/setMax",       "max",       1, 1),
                    g._txt(f"{base}/setAmplitude", "amplitude", 1, 1),
                ]
            case "Gaussian":
                P += [
                    g._txt(f"{base}/setMean",      "mean",      0, 0),
                    g._txt(f"{base}/setSigma",     "sigma",     1, 1),
                    g._txt(f"{base}/setAmplitude", "amplitude", 1, 1),
                ]
            case "Exponential":
                P += [
                    g._txt(f"{base}/setLambda",    "lambda (power)", 1, 1),
                    g._txt(f"{base}/setAmplitude", "amplitude",      1, 1),
                ]
            case "Manual":
                P += [
                    g._txt(f"{base}/setUnitX",    "unit X", "", ""),
                    g._txt(f"{base}/setUnitY",    "unit Y", "", ""),
                    g._txt(f"{base}/insertPoint", "insertPoint (x,y)", 0, 0),   # x,y in UI row
                    g._txt(f"{base}/addPoint",    "addPoint (y)",      0, 0),
                    g._txt(f"{base}/autoXstart",  "auto X start",      0, 0),
                ]
            case "File":
                P += [
                    g._txt(f"{base}/setUnitX",   "unit X", "", ""),
                    g._txt(f"{base}/setUnitY",   "unit Y", "", ""),
                    g._cb (f"{base}/autoX",      "auto X (increment if true)", False),
                    g._txt(f"{base}/autoXstart", "auto X start", 0, 0),
                    g._sel(f"{base}/setFileName","ASCII file"),
                    g._txt(f"{base}/setColumnX", "column X (0- or 1-based)", 0, 0),
                    g._txt(f"{base}/setColumnY", "column Y (0- or 1-based)", 1, 1),
                    g._cb (f"{base}/read",       "read file", False),
                    g._cb (f"{base}/ReadMatrix2d","read 2D matrix file", False),
                ]

        return GateObject(name, base, "distributions", P)
    

    @staticmethod
    def _build_singles_digitizer_92_params() -> list[GateParameter]:
        """
        Gate 9.2 'classic' digitizer chain under /digitizer/Singles.
        """
        g = GObjectCreator
        base = "/digitizer/Singles"

        module_choices = [
            "adder","adderCompton","readout","energyResolution","timeResolution",
            "spatialResolution","energyFraming","clustering","efficiency","pileup",
            "deadtime","noise","merger","intrinsicResolution","crosstalk","buffer",
            "gridDiscretizator","adderComptPhotIdeal","doIModel","timeDelay",
            "multipleRejection","virtualSegmentation",
        ]

        P: list[GateParameter] = []
        P.append(g._dd(f"{base}/insert", "Insert digitizer module (9.2)",
                    module_choices[0], module_choices))
        P.append(g._dd(f"{base}/__ui_selected_module", "Selected module (for UI)",
                    module_choices[0], module_choices))
        # Render the default module parameters (your UI can re-render this block on change)
        P += g._build_module_params_92(base, module_choices[0])
        return P


    @staticmethod
    def _build_module_params_92(base: str, module_type: str) -> list[GateParameter]:
        """
        Per-module parameters (Gate 9.2).
        Delegates to the central registry so we don't duplicate definitions.
        Paths, labels, defaults, and units are preserved by the builders.
        """
        reg = GObjectCreator._module_registry()
        builder = reg.get(module_type)
        if builder is not None:
            return builder(base)

        # Fallback: unknown / not yet implemented module
        return [
            GateParameter(
                f"{base}/{module_type}/__info",
                f"{module_type}: parameters pending (add docs).",
                ["Label"], [""], [""]
            )
        ]
    

    @staticmethod
    def build_multiple_singles_branches(
        gate_version: tuple[int, int] | tuple[int, int, int],
        sd_name: str = "crystal",
        singles_name: str = "Singles",
    ) -> list[GateParameter]:
        g = GObjectCreator
        gv = g._norm_gv(gate_version)
        if gv < (9, 3, 0):
            return []

        P: list[GateParameter] = []

        # Base Singles chain example
        base = g.singles_digitizer_base(gate_version, sd_name, singles_name)
        P += [
            g._dd (f"{base}/insert", "Insert module",
                "adder", ["adder","adderCompton","readout","energyResolution",
                            "timeResolution","spatialResolution","energyFraming",
                            "clustering","efficiency","pileup","deadtime","noise",
                            "merger","intrinsicResolution","crosstalk","buffer",
                            "gridDiscretizator","adderComptPhotIdeal","doIModel",
                            "timeDelay","multipleRejection","virtualSegmentation"]),
            g._txt(f"{base}/readout/setDepth", "Readout depth", 1, 1),
            g._dd (f"{base}/insert", "Insert module", "-", ["-","energyResolution"]),
            g._txt(f"{base}/energyResolution/fwhm", "Energy FWHM", 0.26, 0.26),
            g._txt(f"{base}/energyResolution/energyOfReference",
                "Energy of reference", 511, 511, ENERGY_UNITS, 1),
        ]

        # LESingles branch
        P += [
            g._txt("/gate/digitizerMgr/name", "New SinglesDigitizer name", "LESingles", "LESingles"),
            g._txt("/gate/digitizerMgr/chooseSD", "Choose sensitive detector", sd_name, sd_name),
            g._dd ("/gate/digitizerMgr/insert", "Insert Digitizer functionality",
                "SinglesDigitizer", DIGITIZERMGR_FUNCS),
            g._dd (f"/gate/digitizerMgr/{sd_name}/SinglesDigitizer/LESingles/setInputCollection",
                "LESingles: input Singles collection", singles_name, [singles_name]),
            g._dd (f"/gate/digitizerMgr/{sd_name}/SinglesDigitizer/LESingles/insert",
                "Insert module", "energyFraming", ["energyFraming"]),
            g._txt(f"/gate/digitizerMgr/{sd_name}/SinglesDigitizer/LESingles/energyFraming/setMin",
                "LE min", 50, 50, ENERGY_UNITS, 1),
            g._txt(f"/gate/digitizerMgr/{sd_name}/SinglesDigitizer/LESingles/energyFraming/setMax",
                "LE max", 350, 350, ENERGY_UNITS, 1),
        ]

        # HESingles branch
        P += [
            g._txt("/gate/digitizerMgr/name", "New SinglesDigitizer name", "HESingles", "HESingles"),
            g._txt("/gate/digitizerMgr/chooseSD", "Choose sensitive detector", sd_name, sd_name),
            g._dd ("/gate/digitizerMgr/insert", "Insert Digitizer functionality",
                "SinglesDigitizer", DIGITIZERMGR_FUNCS),
            g._dd (f"/gate/digitizerMgr/{sd_name}/SinglesDigitizer/HESingles/setInputCollection",
                "HESingles: input Singles collection", singles_name, [singles_name]),
            g._dd (f"/gate/digitizerMgr/{sd_name}/SinglesDigitizer/HESingles/insert",
                "Insert module", "energyFraming", ["energyFraming"]),
            g._txt(f"/gate/digitizerMgr/{sd_name}/SinglesDigitizer/HESingles/energyFraming/setMin",
                "HE min", 350, 350, ENERGY_UNITS, 1),
            g._txt(f"/gate/digitizerMgr/{sd_name}/SinglesDigitizer/HESingles/energyFraming/setMax",
                "HE max", 650, 650, ENERGY_UNITS, 1),
        ]

        return P


    @staticmethod
    def _build_basic_singles_chain_params(
        gate_version,
        sd_name: str = "crystal",
        singles_name: str = "Singles"
    ) -> list[GateParameter]:
        g = GObjectCreator
        gv = g._norm_gv(gate_version)
        base = (f"/gate/digitizerMgr/{sd_name}/SinglesDigitizer/{singles_name}"
                if gv >= (9,3,0) else "/digitizer/Singles")

        P: list[GateParameter] = [
            g._dd (f"{base}/insert", "Insert Adder", "False", ["False","True"]),
            g._dd (f"{base}/insert", "Insert Readout", "False", ["False","True"]),
            g._txt(f"{base}/readout/setDepth", "Readout depth", 1, 1),
            g._dd (f"{base}/insert", "Insert EnergyResolution", "False", ["False","True"]),
            g._txt(f"{base}/energyResolution/fwhm", "Energy FWHM", 0.26, 0.26),
            g._txt(f"{base}/energyResolution/energyOfReference",
                "Reference energy", 511, 511, ENERGY_UNITS, 1),
        ]

        # Optional selector to show a module block immediately
        P.append(g._dd(f"{base}/__ui_selected_module", "Selected module (for UI)",
                    "readout",
                    ["adder","readout","energyResolution","timeResolution",
                        "spatialResolution","energyFraming"]))
        P += g._build_module_params_92(base, "readout")
        return P