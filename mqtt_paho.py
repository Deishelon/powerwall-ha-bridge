import paho.mqtt.client as mqtt
from mqtt_interface import MqttClientInterface
import logging


class MqttClient(MqttClientInterface):
    def __init__(self, broker: str, port: int, client_id: str, username: str, password: str):
        self._paho = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=client_id)

        if username and password:
            self._paho.username_pw_set(username, password)

        self._paho.on_connect = self._on_connect
        self._paho.on_disconnect = self._on_disconnect

        logging.info(f"Connecting to MQTT broker {broker}:{port}...")
        self._paho.connect(broker, port)
        self._paho.loop_start()

    def _on_connect(self, client, userdata, flags, rc, properties):
        if rc == 0:
            logging.info("Connected to MQTT broker")
        else:
            logging.error(f"Failed to connect to MQTT broker, return code {rc}")

    def _on_disconnect(self, client, userdata, disconnect_flags, rc, properties):
        logging.warning(f"Disconnected from MQTT broker with return code {rc}")

    def publish(self, topic: str, payload: str, retain: bool):
        result = self._paho.publish(topic, payload, retain=retain)
        status = result[0]
        if status != 0:
            logging.error(f"Failed to send message to topic {topic}")

    def disconnect(self):
        self._paho.loop_stop()
        self._paho.disconnect()
