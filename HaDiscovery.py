from typing import List

import HaEntity


class HaDiscovery:
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

    def get_discovery_payload(self, entities: List[HaEntity], discovery_prefix: str):
        payload = {
            "device": {
                "identifiers": [self.device_id],
                "name": self.device_name,
                "manufacturer": self.manufacturer,
                "model": self.model,
                "sw_version": self.firmware,
                "serial_number": self.device_id
            },
            "origin": {
                "name": "pypowerwall",
                "sw_version": "1.0",
                "support_url": "https://github.com/jasonacox/pypowerwall"
            },
            "qos": 1,
            "component": {
                entity.component_id: entity.get_discovery_config(self.device_id, discovery_prefix) for entity in entities
            }
        }
        return payload
