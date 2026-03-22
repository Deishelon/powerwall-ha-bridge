from typing import List

import ha_entity


class HaDevice:
    def __init__(
            self,
            device_id: str,
            device_name: str,
            firmware: str,
            model: str,
            manufacturer: str,
    ):
        self.device_id = device_id
        self.device_name = device_name
        self.firmware = firmware
        self.model = model
        self.manufacturer = manufacturer

    def get_discovery(self, entities: List[HaEntity.HaEntity], discovery_prefix: str):
        payload = {
            "device": {
                "identifiers": [self.device_id],
                "name": self.device_name,
                "manufacturer": self.manufacturer,
                "model": self.model,
                "sw_version": self.firmware,
            },
            "origin": {
                "name": "powerwall2mqtt",
                "sw_version": "1.0",
                "support_url": "https://github.com/Deishelon/powerwall2mqtt"
            },
            "components": {
                entity.component_id: entity.get_discovery_config(self.device_id, discovery_prefix) for entity in
                entities
            },
            "qos": 2
        }
        topic = f"{discovery_prefix}/device/{self.device_id}/config"
        return topic, payload
