from enum import Enum

# https://www.home-assistant.io/integrations/sensor/#device-class
class DeviceClass(Enum):
    NONE = 0
    POWER = 1
    BATTERY = 2
    VOLTAGE = 3
    CURRENT = 4
    ENERGY_STORAGE = 5
    DURATION = 6

def device_class_serialized(device: DeviceClass) -> str | None:
    match device:
        case DeviceClass.NONE:
            return None
        case DeviceClass.POWER:
            return "power"
        case DeviceClass.BATTERY:
            return "battery"
        case DeviceClass.VOLTAGE:
            return "voltage"
        case DeviceClass.CURRENT:
            return "current"
        case DeviceClass.ENERGY_STORAGE:
            return "energy_storage"
        case DeviceClass.DURATION:
            return "duration"


class StateClass(Enum):
    NONE = 0
    measurement = 1


def state_class_serialized(state: StateClass) -> str | None:
    match state:
        case StateClass.NONE:
            return None
        case StateClass.measurement:
            return "measurement"