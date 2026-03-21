from enum import Enum

class DeviceClass(Enum):
    NONE = 0
    POWER = 1
    BATTERY = 2

def device_class_serialized(device: DeviceClass) -> str | None:
    match device:
        case DeviceClass.NONE:
            return None
        case DeviceClass.POWER:
            return "power"
        case DeviceClass.BATTERY:
            return "battery"


class StateClass(Enum):
    NONE = 0
    measurement = 1


def state_class_serialized(state: StateClass) -> str | None:
    match state:
        case StateClass.NONE:
            return None
        case StateClass.measurement:
            return "measurement"