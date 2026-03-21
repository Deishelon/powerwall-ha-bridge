from HaCore import DeviceClass, StateClass, device_class_serialized, state_class_serialized
from typing import Callable


class HaEntity:
    def __init__(
            self,
            component_id: str,
            name: str,
            device_class: DeviceClass,
            state_class: StateClass,
            unit: str,
            lookup: Callable[[], str | int | float],
            suggested_display_precision: int | None = None
    ):
        self.component_id = component_id
        self.name = name
        self.device_class = device_class
        self.state_class = state_class
        self.unit = unit
        self.lookup = lookup
        self.suggested_display_precision = suggested_display_precision

    def state_topic(self, device_id: str, discovery_prefix: str):
        return f"{discovery_prefix}/sensor/{device_id}/{self.component_id}/state"

    def get_discovery_config(self, device_id: str, discovery_prefix: str, device_info: dict = None):
        config = dict()

        config["platform"] = "sensor"
        config["name"] = self.name
        config["unique_id"] = f"{device_id}_{self.component_id}"
        config["state_topic"] = self.state_topic(device_id, discovery_prefix)

        device_class = device_class_serialized(self.device_class)
        if device_class:
            config["device_class"] = device_class

        state_class = state_class_serialized(self.state_class)
        if state_class:
            config["state_class"] = state_class

        if self.unit:
            config["unit_of_measurement"] = self.unit

        if self.suggested_display_precision is not None:
            config["suggested_display_precision"] = self.suggested_display_precision

        if device_info:
            config["device"] = device_info

        return config
