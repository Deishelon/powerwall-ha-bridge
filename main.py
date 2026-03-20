import pypowerwall
import os
import logging
from mqtt_paho import MqttClient
import time

def get_pw_api():
    host = os.getenv('POWERWALL_HOST', "192.168.91.1")
    gw_pwd = os.getenv('POWERWALL_GW_PWD', "")
    password = os.getenv('POWERWALL_PASSWORD', "")
    email = os.getenv('POWERWALL_EMAIL', "")
    timezone = os.getenv('POWERWALL_TIMEZONE', "Pacific/Auckland")

    return pypowerwall.Powerwall(host, password, email, timezone, gw_pwd=gw_pwd, auto_select=True)

def get_mqtt_client():
    broker = os.getenv('MQTT_BROKER', "localhost")
    port = int(os.getenv('MQTT_PORT', "1883"))
    client_id = os.getenv('MQTT_CLIENT_ID', "powerwall2mqtt")
    username = os.getenv('MQTT_USERNAME')
    password = os.getenv('MQTT_PASSWORD')
    
    return MqttClient(broker, port, client_id, username, password)

def main():
    logger = logging.getLogger(__name__)
    poll_time_sec = int(os.getenv('POLL_TIME_S', "10"))
    pw_api = get_pw_api()
    mqtt = get_mqtt_client()

    try:
        while True:
            logger.info("Polling...")
            time.sleep(poll_time_sec)
    except KeyboardInterrupt:
        logger.info("Stopping...")
    finally:
        mqtt.disconnect()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()

