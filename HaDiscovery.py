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

    def get_device_info(self):
        return {
            "identifiers": [self.device_id],
            "name": self.device_name,
            "manufacturer": self.manufacturer,
            "model": self.model,
            "sw_version": self.firmware,
        }

    def get_discovery_payloads(self, entities: List[HaEntity.HaEntity], discovery_prefix: str):
        device_info = self.get_device_info()
        payloads = {}
        for entity in entities:
            topic = f"{discovery_prefix}/sensor/{self.device_id}/{entity.component_id}/config"
            payloads[topic] = entity.get_discovery_config(self.device_id, discovery_prefix, device_info)
        return payloads
