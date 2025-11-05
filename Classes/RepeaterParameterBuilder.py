from Classes.GateParameter import GateParameter
from Classes.StaticData import LENGTH_UNITS
from Classes.StaticData import REPEATER_TYPES

class RepeaterParameterBuilder:
    @staticmethod
    def get_parameters(name, repeater_type):
        if repeater_type == "linear":
            return [
                GateParameter(f"/{name}/repeaters/insert linear", "Insert Linear Repeater", [], [], []),
                GateParameter(f"/{name}/linear/setRepeatNumber", "Repeat Number", ["TextArea"], [1], [1], LENGTH_UNITS),
                GateParameter(f"/{name}/linear/setRepeatVector", "Repeat Vector", ["TextArea"], ["0 1 0"], ["0 1 0"], LENGTH_UNITS)
            ]
        elif repeater_type == "ring":
            return [
                GateParameter(f"/{name}/repeaters/insert ring", "Insert Ring Repeater", [], [], []),
                GateParameter(f"/{name}/ring/setRepeatNumber", "Repeat Number", ["TextArea"], [8], [8]),
                GateParameter(f"/{name}/ring/setRadius", "Radius", ["TextArea"], [10], [10], LENGTH_UNITS),
                GateParameter(f"/{name}/ring/setFirstAngle", "First Angle", ["TextArea"], [0], [0], LENGTH_UNITS),
                GateParameter(f"/{name}/ring/setAngularSpan", "Angular Span", ["TextArea"], [360], [360], LENGTH_UNITS)
            ]
        elif repeater_type == "cubicArray":
            return [
                GateParameter(f"/{name}/repeaters/insert cubicArray", "Insert Cubic Array", [], [], []),
                GateParameter(f"/{name}/cubicArray/setRepeatNumberX", "Repeat X", ["TextArea"], [1], [1]),
                GateParameter(f"/{name}/cubicArray/setRepeatNumberY", "Repeat Y", ["TextArea"], [1], [1]),
                GateParameter(f"/{name}/cubicArray/setRepeatNumberZ", "Repeat Z", ["TextArea"], [1], [1]),
                GateParameter(f"/{name}/cubicArray/setRepeatVector", "Repeat Vector", ["TextArea"], ["1 1 1"], ["1 1 1"], LENGTH_UNITS)
            ]
        elif repeater_type == "quadrant":
            return [
                GateParameter(f"/{name}/repeaters/insert quadrant", "Insert Quadrant", [], [], []),
                GateParameter(f"/{name}/quadrant/setRepeatNumber", "Repeat Number", ["TextArea"], [4], [4], LENGTH_UNITS)
            ]
        elif repeater_type == "sphere":
            return [
                GateParameter(f"/{name}/repeaters/insert sphere", "Insert Sphere Repeater", [], [], []),
                GateParameter(f"/{name}/sphere/setRepeatNumberPhi", "Repeat Phi", ["TextArea"], [8], [8], LENGTH_UNITS),
                GateParameter(f"/{name}/sphere/setRepeatNumberTheta", "Repeat Theta", ["TextArea"], [8], [8], LENGTH_UNITS),
                GateParameter(f"/{name}/sphere/setRadius", "Radius", ["TextArea"], [10], [10], LENGTH_UNITS)
            ]
        elif repeater_type == "generic":
            return [
                GateParameter(f"/{name}/repeaters/insert generic", "Insert Generic Repeater", [], [], []),
                GateParameter(f"/{name}/generic/addMatrixTransformation", "Add Transformation", ["TextArea"], ["1 0 0 0 0 1 0 0 0 0 1 0"], ["1 0 0 0 0 1 0 0 0 0 1 0"], LENGTH_UNITS)
            ]
        else:
            return []