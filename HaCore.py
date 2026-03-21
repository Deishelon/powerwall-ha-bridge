from enum import Enum

class DeviceClass(Enum):
    NONE = 1
    POWER = 2

def device_class_serialized(device: DeviceClass) -> str:
    match device:
        case DeviceClass.NONE:
            return "None"
        case DeviceClass.POWER:
            return "power"


class StateClass(Enum):
    measurement = 1


def state_class_serialized(state: StateClass) -> str:
    match state:
        case StateClass.measurement:
            return "measurement"