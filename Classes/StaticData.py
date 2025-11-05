# Units
LENGTH_UNITS = ['pc', 'km', 'm', 'cm', 'mm', 'mum', 'nm', 'Ang']
SURFACE_UNITS = ['km2', 'm2', 'cm2', 'mm2']
VOLUME_UNITS = ['km3', 'm3', 'cm3', 'mm3']
ANGLE_UNITS = ['rad', 'mrad', 'sr', 'deg']
TIME_UNITS = ['s', 'ms', 'mus', 'ns', 'ps']
SPEED_UNITS = ['m/s', 'cm/s', 'mm/s', 'm/min', 'cm/min', 'mm/min', 'm/h', 'cm/h', 'mm/h']
ANGULAR_SPEED_UNITS = ['rad/s', 'deg/s', 'rot/s', 'rad/min', 'deg/min', 'rot/min', 'rad/h', 'deg/h', 'rot/h']
ENERGY_UNITS = ['eV', 'KeV', 'MeV', 'GeV', 'TeV', 'PeV', 'j']
ACTIVITY_DOSE_UNITS = ['Bq', 'Ci', 'Gy']
AMOUNT_OF_SUBSTANCE_UNITS = ['mol']
MASS_UNITS = ['mg', 'g', 'kg']
VOLUMIC_MASS_UNITS = ['g/cm3', 'mg/cm3', 'kg/m3']
ELECTRIC_CHARGE_UNITS = ['e+', 'C', 'muA', 'nA']
ELECTRIC_CURRENT_UNITS = ['A', 'mA']
ELECTRIC_POTENTIAL_UNITS = ['V', 'kV', 'MV', 'kG']
MAGNETIC_FLUX_UNITS = ['Wb', 'T', 'G']
TEMPERATURE_UNITS = ['K']
FORCE_PRESSURE_UNITS = ['N', 'Pa', 'bar', 'atm']
POWER_UNITS = ['W']
FREQUENCY_UNITS = ['Hz', 'kHz', 'MHz']
PHYSICS_LISTS = [
    " - ", "FTFP_BERT", "FTFP_BERT_ATL", "FTFP_BERT_HP", "FTFP_BERT_TRV", "FTFP_INCLXX",
    "FTFQGSP_BERT", "FTF_BIC", "LBE", "NuBeam", "QBBC", "QBBC_ABLA", "QGSP_BERT",
    "QGSP_BERT_HP", "QGSP_BIC", "QGSP_BIC_AllHP", "QGSP_BIC_HP", "QGSP_BIC_HPT",
    "QGSP_FTFP_BERT", "QGSP_INCLXX", "QGS_BIC", "Shielding", "ShieldingLEND"
]
PHYSICS_PROCESSES = {
    "PhotoElectric": {"process": ["gamma"],
                "model": [" - ", "StandardModel", "LivermoreModel", "LivermorePolarizedModel", "PenelopeModel"]},
    "Compton": {"process": ["gamma"],
                "model": [" - ", "StandardModel", "LivermoreModel", "LivermorePolarizedModel", "PenelopeModel"]},
    "RayleighScattering": {"process": ["gamma"],
                           "model": [" - ", "LivermoreModel", "LivermorePolarizedModel", "PenelopeModel"]},
    "GammaConversion": {"process": [" - "],
                        "model": [" - ", "StandardModel", "LivermoreModel", "LivermorePolarizedModel", "PenelopeModel"]},
    "ElectronIonisation": {"process": ["e+", "e-"],
                           "model": [" - ", "StandardModel", "LivermoreModel", "LivermorePolarizedModel", "PenelopeModel"]}
}

COLORS = ["white", "gray", "black", "red", "green", "blue", "cyan", "magenta", "yellow"]
LINE_STYLE = ["dashed", "dotted", "unbroken"]
INC_EXC = ["exclude", "include"]

REPEATER_TYPES = [" - ", "linear", "ring", "cubicArray", "quadrant", "sphere", "genericRepeater"]

VIEWER_TYPES = ["-", "OGL", "OGLS","OGLSQt", "OGLSX", "OGLI", "OGLIQt", "OGLIX", "DAWNFILE", "VRML2FILE"]

#
# Scanner:  There is no geometrical constraints on the five different components.
# 
SYSTEM_TYPES = [
    "scanner", "CTscanner", "cylindricalPET", "CPET", "SPECTHead", "ecat", "ecatAccel", "OPET", "OpticalSystem"
]

SYSTEM_LEVELS_BY_TYPE = {
    "scanner":          ["level1","level2","level3","level4","level5"],
    "CTscanner":        ["module","cluster","pixel"],
    "cylindricalPET":   ["rsector","module","submodule","crystal","layer"], #layer[i], i=0..3
    "CPET":             ["sector","cassette","module","crystal","layer"], #layer[i], i=0..3
    "SPECTHead":        ["crystal","pixel"],
    "ecat":             ["block","crystal"],
    "ecatAccel":        ["block","crystal"],
    "OPET":             ["rsector","module","submodule","crystal","layer"], #layer[i], i=0..7
    "OpticalSystem":    ["crystal","pixel"],
}

# values: "box", "cylinder", "wedge", "any"
SYSTEM_LEVEL_SHAPES = {
    "scanner":        {"level1":"any","level2":"any","level3":"any","level4":"any","level5":"any"},
    "CTscanner":      {"module":"box","cluster":"box","pixel":"box"},
    "cylindricalPET": {"rsector":"box","module":"box","submodule":"box","crystal":"box","layer":"box"},
    "CPET":           {"sector":"cylinder","cassette":"cylinder","module":"box","crystal":"box","layer":"box"},
    "SPECTHead":      {"crystal":"any","pixel":"any"},
    "ecat":           {"block":"box","crystal":"box"},
    "ecatAccel":      {"block":"box","crystal":"box"},
    "OPET":           {"rsector":"box","module":"box","submodule":"box","crystal":"box","layer":"wedge"},
    "OpticalSystem":  {"crystal":"any","pixel":"any"},
}


# === Source kinds (Gate keywords) ===
SOURCE_TYPES = [
    "gps",
    "fastI124",
    "PencilBeam",
    "TPSPencilBeam",
    "fastY90",
    "Extended",
    "voxelized",
    "linacBeam",
    "phaseSpace",
]

SOURCE_PARTICLES = ["gamma","e+","e-","proton","neutron","ion","GenericIon"]
SOURCE_ENERGY_TYPES = ["Mono","Lin","Pow","Exp","Gauss","Brem","Bbody","Cdg","UserSpectrum","Arb",
                       "Epn", "Fluor18"]
SOURCE_ANG_TYPES = ["iso"]
SOURCE_DOMAINS = ["Point","Beam","Plane","Surface","Volume"]
SOURCE_SHAPES_BY_DOMAIN = {
    "Point":   ["(none)"],
    "Beam":    ["(none)"],
    "Plane":   ["Circle","Annulus","Ellipsoid","Square","Rectangle"],
    "Surface": ["Sphere","Ellipsoid","Cylinder","Para"],
    "Volume":  ["Sphere","Ellipsoid","Cylinder","Para"],
}

# ExtendedVSource models
EXTENDED_MODELS = ["sg", "pPs", "oPs", "Ps"]

# Optional helper maps (Maybe for tooltips)
EXTV_GAMMA_TYPE = {0:"not EVS", 1:"single gamma (sg)", 2:"annihilation gamma", 3:"prompt gamma"}
EXTV_SOURCE_TYPE = {0:"not EVS", 1:"sg", 2:"pPs", 3:"oPs"}
EXTV_DECAY_TYPE  = {0:"unknown", 1:"standard decay", 2:"de-excitation + decay"}

# For PencilBeam emittance fields
EMITTANCE_UNIT = "mm*mrad"


# Acquisition values
RANDOM_ENGINES = ["Ranlux64", "JamesRandom", "MixMaxRng", "MersenneTwister"]
RANDOM_SEED_MODE = ["default", "auto", "manual"]

# Digitizer values
DIGITIZERMGR_FUNCS = ["SinglesDigitizer", "CoincidenceSorter"] # Upcoming: CoincidenceDigitizer, WaveformGenerator
DISTRIBUTION_TYPES = ["Flat", "Gaussian", "Exponential", "Manual", "File"]