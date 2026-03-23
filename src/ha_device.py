from typing import List

from ha_entity import HaEntity


class HaDevice:
    def __init__(
            self,
            device_id: str,
            device_name: str,
            model: str,
            manufacturer: str,
    ):
        self.device_id = device_id
        self.device_name = device_name
        self.model = model
        self.manufacturer = manufacturer
        self.entities: List[HaEntity] = []


    def register_entity(self, entity: HaEntity):
        for index, existing_entity in enumerate(self.entities):
            if existing_entity.component_id == entity.component_id:
                self.entities[index] = entity
                return
        self.entities.append(entity)


    def get_discovery(self, entities: List[HaEntity], discovery_prefix: str):
        payload = {
            "device": {
                "identifiers": [self.device_id],
                "name": self.device_name,
                "manufacturer": self.manufacturer,
                "model": self.model,
            },
            "origin": {
                "name": "pw-ha-bridge",
                "sw_version": "1.0",
                "support_url": "https://github.com/Deishelon/pw-ha-bridge"
            },
            "components": {
                entity.component_id: entity.get_discovery_config(self.device_id, discovery_prefix) for entity in
                entities
            },
            "qos": 2
        }
        topic = f"{discovery_prefix}/device/{self.device_id}/config"
        return topic, payload
