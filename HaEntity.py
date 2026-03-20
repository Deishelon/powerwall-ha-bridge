class Entity:
    def __init__(
            self,
            component_id,
            name,
            component_type="sensor",
            device_class=None,
            unit=None,
            state_topic=None,
            payload_on=None,
            payload_off=None
    ):
        self.component_id = component_id
        self.name = name
        self.component_type = component_type
        self.device_class = device_class
        self.unit = unit
        self.state_topic = state_topic
        self.payload_on = payload_on
        self.payload_off = payload_off

    def get_discovery_config(self, device_id):
        config = {
            "platform": self.component_type,
            "name": self.name,
            "unique_id": f"{device_id}_{self.component_id}",
            "state_topic": self.state_topic,
        }
        if self.device_class:
            config["device_class"] = self.device_class
        if self.unit:
            config["unit_of_measurement"] = self.unit
        if self.payload_on:
            config["payload_on"] = self.payload_on
        if self.payload_off:
            config["payload_off"] = self.payload_off
        return config