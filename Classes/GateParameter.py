import Classes.StaticData as StaticData

class GateParameter(object):
    def __init__(self, path, displayed_name, input_type_list, default_value_list, value_list, unit_list=None, default_unit=0):
        self.path = path
        self.displayed_name = displayed_name
        self.input_type_list = input_type_list        
        self.default_value_list = default_value_list
        self.value_list = value_list
        #self.set_value = None
        self.unit_list = unit_list
        self.default_unit = default_unit
        if unit_list:
            self.default_unit = unit_list[default_unit]
        else:
            self.default_unit = None
    
    def to_dict(self):
        return {
            "path": self.path,
            "name": self.displayed_name,
            "input_types": self.input_type_list,
            "default_values": self.default_value_list,
            "values": self.value_list,
            "unit_list": self.compare_lists(),
            "chosen_unit": self.default_unit
        }
        
    def compare_lists(self):
        """Compares the stored unit_list with unit lists in StaticData and returns the matching list name as a string."""
        if not self.unit_list:
            return None  # No unit list to compare
        
        unit_lists = {
            "LENGTH_UNITS": StaticData.LENGTH_UNITS,
            "SURFACE_UNITS": StaticData.SURFACE_UNITS,
            "VOLUME_UNITS": StaticData.VOLUME_UNITS,
            "ANGLE_UNITS": StaticData.ANGLE_UNITS,
            "TIME_UNITS": StaticData.TIME_UNITS,
            "SPEED_UNITS": StaticData.SPEED_UNITS,
            "ANGULAR_SPEED_UNITS": StaticData.ANGULAR_SPEED_UNITS,
            "ENERGY_UNITS": StaticData.ENERGY_UNITS,
            "ACTIVITY_DOSE_UNITS": StaticData.ACTIVITY_DOSE_UNITS,
            "AMOUNT_OF_SUBSTANCE_UNITS": StaticData.AMOUNT_OF_SUBSTANCE_UNITS,
            "MASS_UNITS": StaticData.MASS_UNITS,
            "VOLUMIC_MASS_UNITS": StaticData.VOLUMIC_MASS_UNITS,
            "ELECTRIC_CHARGE_UNITS": StaticData.ELECTRIC_CHARGE_UNITS,
            "ELECTRIC_CURRENT_UNITS": StaticData.ELECTRIC_CURRENT_UNITS,
            "ELECTRIC_POTENTIAL_UNITS": StaticData.ELECTRIC_POTENTIAL_UNITS,
            "MAGNETIC_FLUX_UNITS": StaticData.MAGNETIC_FLUX_UNITS,
            "TEMPERATURE_UNITS": StaticData.TEMPERATURE_UNITS,
            "FORCE_PRESSURE_UNITS": StaticData.FORCE_PRESSURE_UNITS,
            "POWER_UNITS": StaticData.POWER_UNITS,
            "FREQUENCY_UNITS": StaticData.FREQUENCY_UNITS
        }

        for list_name, predefined_list in unit_lists.items():
            if set(self.unit_list) == set(predefined_list):  # Compare as sets to avoid order dependency
                return list_name

        return "UNKNOWN"  # If no match is found