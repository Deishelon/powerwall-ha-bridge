import json
from logging import Logger
from typing import List

import pypowerwall
import os
import logging

from HaCore import DeviceClass, StateClass
from HaDevice import HaDevice
from HaEntity import HaEntity
from mqtt_paho import MqttClient
import time


def get_pw_api():
    host = os.getenv('POWERWALL_HOST', "192.168.91.1")
    gw_pwd = os.getenv('POWERWALL_GW_PWD', "")
    password = os.getenv('POWERWALL_PASSWORD', "")
    email = os.getenv('POWERWALL_EMAIL', "")
    timezone = os.getenv('POWERWALL_TIMEZONE', os.getenv('TZ', "Pacific/Auckland"))

    return pypowerwall.Powerwall(host, password, email, timezone, gw_pwd=gw_pwd, auto_select=True)


def get_mqtt_client():
    broker = os.getenv('MQTT_BROKER', "localhost")
    port = int(os.getenv('MQTT_PORT', "1883"))
    client_id = os.getenv('MQTT_CLIENT_ID', "powerwall2mqtt")
    username = os.getenv('MQTT_USERNAME')
    password = os.getenv('MQTT_PASSWORD')

    return MqttClient(broker, port, client_id, username, password)


def publish_ha_device(ha_device: HaDevice, entities: List[HaEntity.HaEntity], discovery_prefix: str, mqtt: MqttClient):
    topic, payload = ha_device.get_discovery(entities, discovery_prefix)
    mqtt.publish(
        topic=topic,
        payload=json.dumps(payload),
        retain=True,
    )


def get_power_entities(pw_api: pypowerwall.Powerwall) -> list[HaEntity]:
    # {'site': -14, 'solar': 2200, 'battery': 344, 'load': 2529}
    # {'site': 83, 'solar': 2628, 'battery': -122, 'load': 2610.25}
    power = pw_api.power()
    battery_power = power['battery']  # Negative=charging, Positive=discharging

    return [
        HaEntity(
            component_id="solar_generation",
            name="Solar Generation",
            device_class=DeviceClass.POWER,
            state_class=StateClass.measurement,
            unit="W",
            lookup=lambda: power['solar'],
        ),
        HaEntity(
            component_id="home_power",
            name="Home Power",
            device_class=DeviceClass.POWER,
            state_class=StateClass.measurement,
            unit="W",
            lookup=lambda: power['load'],
        ),
        HaEntity(
            component_id="grid_power",
            name="Grid Power",
            device_class=DeviceClass.POWER,
            state_class=StateClass.measurement,
            unit="W",
            lookup=lambda: power['site'],
        ),
        HaEntity(
            component_id="battery_power",
            name="Battery Power",
            device_class=DeviceClass.POWER,
            state_class=StateClass.measurement,
            unit="W",
            lookup=lambda: battery_power,
        ),
        HaEntity(
            component_id="battery_state",
            name="Battery State",
            device_class=DeviceClass.NONE,
            state_class=StateClass.NONE,
            unit="",
            lookup=lambda: "Idle" if battery_power == 0 else "Charging" if battery_power < 0 else "Discharging",
        ),
    ]


def get_strings_entities(pw_api: pypowerwall.Powerwall) -> list[HaEntity]:
    # strings(verbose=False)={'A': {'State': 'Pv_Active', 'Voltage': 414, 'Current': 2.05, 'Power': 848.6999999999999, 'Connected': True}, 'B': {'State': 'Pv_Active_Parallel', 'Voltage': 414, 'Current': 1.9499999999999997, 'Power': 807.2999999999998, 'Connected': True}, 'C': {'State': 'Pv_Active', 'Voltage': 278, 'Current': 2.0999999999999996, 'Power': 583.8, 'Connected': True}, 'D': {'State': 'Pv_Active_Parallel', 'Voltage': 278, 'Current': 1.9999999999999998, 'Power': 555.9999999999999, 'Connected': True}, 'E': {'State': 'Pv_Active', 'Voltage': 0, 'Current': 0, 'Power': 0, 'Connected': True}, 'F': {'State': 'Pv_Active_Parallel', 'Voltage': 0, 'Current': 0, 'Power': 0, 'Connected': True}}
    # strings(verbose=True)={'PVAC--1707000-30-L--TG1252600023PG': {'PVAC_Pout': -2350, 'PVAC_PvState_A': 'Pv_Active', 'PVAC_PVMeasuredVoltage_A': 414, 'PVAC_PVCurrent_A': 2.05, 'PVAC_PVMeasuredPower_A': 848.6999999999999, 'PVAC_PvState_B': 'Pv_Active_Parallel', 'PVAC_PVMeasuredVoltage_B': 414, 'PVAC_PVCurrent_B': 1.9499999999999997, 'PVAC_PVMeasuredPower_B': 807.2999999999998, 'PVAC_PvState_C': 'Pv_Active', 'PVAC_PVMeasuredVoltage_C': 278, 'PVAC_PVCurrent_C': 2.0999999999999996, 'PVAC_PVMeasuredPower_C': 583.8, 'PVAC_PvState_D': 'Pv_Active_Parallel', 'PVAC_PVMeasuredVoltage_D': 278, 'PVAC_PVCurrent_D': 1.9999999999999998, 'PVAC_PVMeasuredPower_D': 555.9999999999999, 'PVAC_PvState_E': 'Pv_Active', 'PVAC_PVMeasuredVoltage_E': 0, 'PVAC_PVCurrent_E': 0, 'PVAC_PVMeasuredPower_E': 0, 'PVAC_PvState_F': 'Pv_Active_Parallel', 'PVAC_PVMeasuredVoltage_F': 0, 'PVAC_PVCurrent_F': 0, 'PVAC_PVMeasuredPower_F': 0, 'PVS_StringA_Connected': True, 'PVS_StringB_Connected': True, 'PVS_StringC_Connected': True, 'PVS_StringD_Connected': True, 'PVS_StringE_Connected': True, 'PVS_StringF_Connected': True}}
    strings = pw_api.strings()

    entities = list[HaEntity]()

    for pv_id, pv_data in strings.items():
        def make_lookup(data, key):
            return lambda: data[key]

        entities_for_string = [
            HaEntity(
                component_id=f"array{pv_id}_voltage",
                name=f"Array {pv_id} Voltage",
                device_class=DeviceClass.VOLTAGE,
                state_class=StateClass.measurement,
                unit="V",
                lookup=make_lookup(pv_data, 'Voltage'),
            ),
            HaEntity(
                component_id=f"array{pv_id}_current",
                name=f"Array {pv_id} Current",
                device_class=DeviceClass.CURRENT,
                state_class=StateClass.measurement,
                unit="A",
                lookup=make_lookup(pv_data, 'Current'),
            ),
            HaEntity(
                component_id=f"array{pv_id}_power",
                name=f"Array {pv_id} Power",
                device_class=DeviceClass.POWER,
                state_class=StateClass.measurement,
                unit="W",
                lookup=make_lookup(pv_data, 'Power'),
            )
        ]
        entities.extend(entities_for_string)
        pass

    return entities


def get_battery_blocks_entities(pw_api: pypowerwall.Powerwall) -> list[HaEntity]:
    # battery_blocks={'TG1252600023PG': {'Type': '', 'PackagePartNumber': '1707000-30-L', 'disabled_reasons': [], 'pinv_state': 'AcMode_GridFollowing', 'pinv_grid_state': None, 'nominal_energy_remaining': 8680, 'nominal_full_pack_energy': 14380, 'p_out': -2.41, 'q_out': None, 'v_out': 237, 'f_out': 50.05, 'i_out': None, 'energy_charged': None, 'energy_discharged': None, 'off_grid': None, 'vf_mode': None, 'wobble_detected': None, 'charge_power_clamped': None, 'backup_ready': None, 'OpSeqState': None, 'version': None}}
    blocks = pw_api.battery_blocks()
    entities = list[HaEntity]()
    if blocks is None:
        return entities

    for block_id, block_data in blocks.items():
        def make_lookup(data, key):
            return lambda: data[key]

        nominal_energy_remaining = block_data['nominal_energy_remaining']
        nominal_full_pack_energy = block_data['nominal_full_pack_energy']
        soc = nominal_energy_remaining / nominal_full_pack_energy * 100

        # Negative=charging, Positive=discharging
        block_power_w = block_data['p_out'] * 1000
        runtime_m = battery_runtime_minutes(block_power_w, soc, nominal_energy_remaining)

        entities_for_block = [
            HaEntity(
                component_id=f"battery_{block_id}_nominal_energy_remaining",
                name=f"Battery Nominal Energy Remaining - {block_id}",
                device_class=DeviceClass.ENERGY_STORAGE,
                state_class=StateClass.measurement,
                unit="Wh",
                lookup=lambda: nominal_energy_remaining,
            ),
            HaEntity(
                component_id=f"battery_{block_id}_nominal_full_pack_energy",
                name=f"Battery Nominal Full Pack Energy - {block_id}",
                device_class=DeviceClass.ENERGY_STORAGE,
                state_class=StateClass.measurement,
                unit="Wh",
                lookup=lambda: nominal_full_pack_energy,
            ),
            HaEntity(
                component_id=f"battery_{block_id}_runtime_minutes",
                name=f"Battery Runtime - {block_id}",
                device_class=DeviceClass.DURATION,
                state_class=StateClass.measurement,
                unit="min",
                lookup=lambda: runtime_m,
            ),
        ]
        entities.extend(entities_for_block)
        pass

    return entities


def fetch_pw_data(
        pw_api: pypowerwall.Powerwall,
        mqtt: MqttClient,
        logger: Logger,
        discovery_prefix: str
):
    entities = list[HaEntity]()
    entities.extend(get_power_entities(pw_api))
    entities.extend(get_strings_entities(pw_api))
    entities.extend(get_battery_blocks_entities(pw_api))

    entities.append(
        HaEntity(
            component_id="battery_level",
            name="Battery Level",
            device_class=DeviceClass.BATTERY,
            state_class=StateClass.measurement,
            unit="%",
            # level(Scale=False)=60.41666666666667
            # level(Scale=True)=58.33333333333334
            lookup=lambda: pw_api.level(scale=True),
        )
    )

    # INFO:powerwall2mqtt:status={'din': '1707000-30-L--TG1252600023PG', 'start_time': '2026-03-16T17:03:05+13:00', 'up_time_seconds': None, 'is_new': False, 'version': '26.2.1 a7456b0a', 'git_hash': None, 'commission_count': 0, 'device_type': None, 'teg_type': 'unknown', 'sync_type': 'unknown', 'cellular_disabled': False, 'can_reboot': True}
    status = pw_api.status()

    ha_device = HaDevice(
        device_id=f"test-{status['din']}",
        device_name=f"test-{pw_api.site_name()}",
        firmware=pw_api.version(),  # version=26.2.1 a7456b0a
        model="Powerwall",
        manufacturer="Tesla",
    )
    publish_ha_device(ha_device, entities, discovery_prefix, mqtt)

    for entity in entities:
        mqtt.publish(
            topic=entity.state_topic(ha_device.device_id, discovery_prefix),
            payload=entity.lookup(),
            retain=True,
        )

    # INFO:powerwall2mqtt:system_status={'command_source': 'Configuration', 'battery_target_power': 0, 'battery_target_reactive_power': 0, 'nominal_full_pack_energy': 14400, 'nominal_energy_remaining': 8600, 'max_power_energy_remaining': 0, 'max_power_energy_to_be_charged': 0, 'max_charge_power': None, 'max_discharge_power': None, 'max_apparent_power': None, 'instantaneous_max_discharge_power': 0, 'instantaneous_max_charge_power': 0, 'instantaneous_max_apparent_power': 0, 'hardware_capability_charge_power': 0, 'hardware_capability_discharge_power': 0, 'grid_services_power': None, 'system_island_state': 'SystemGridConnected', 'available_blocks': 0, 'available_charger_blocks': 0, 'battery_blocks': [{'Type': '', 'PackagePartNumber': '1707000-30-L', 'PackageSerialNumber': 'TG1252600023PG', 'disabled_reasons': [], 'pinv_state': 'AcMode_GridFollowing', 'pinv_grid_state': None, 'nominal_energy_remaining': 8590, 'nominal_full_pack_energy': 14380, 'p_out': -1.77, 'q_out': None, 'v_out': 238, 'f_out': 49.92, 'i_out': None, 'energy_charged': None, 'energy_discharged': None, 'off_grid': None, 'vf_mode': None, 'wobble_detected': None, 'charge_power_clamped': None, 'backup_ready': None, 'OpSeqState': None, 'version': None}], 'ffr_power_availability_high': 0, 'ffr_power_availability_low': 0, 'load_charge_constraint': 0, 'max_sustained_ramp_rate': 0, 'grid_faults': [], 'can_reboot': 'Yes', 'smart_inv_delta_p': 0, 'smart_inv_delta_q': 0, 'last_toggle_timestamp': '2023-10-13T04:08:05.957195-07:00', 'solar_real_power_limit': None, 'score': 10000, 'blocks_controlled': 0, 'primary': True, 'auxiliary_load': 0, 'all_enable_lines_high': True, 'inverter_nominal_usable_power': 0, 'expected_energy_remaining': 0}
    # logger.info(f"system_status={pw_api.system_status()}")

    # INFO:powerwall2mqtt:vitals={'VITALS': {'text': 'Device vitals generated from Tesla Powerwall Gateway TEDAPI', 'timestamp': 1774040502.68937, 'gateway': '192.168.91.1', 'pyPowerwall': '0.14.10'}, 'STSTSM--1707000-30-L--TG1252600023PG': {'STSTSM-Location': 'Gateway', 'alerts': ['SystemConnectedToGrid', 'FWUpdateSucceeded'], 'firmwareVersion': None, 'lastCommunicationTime': None, 'manufacturer': 'TESLA', 'partNumber': '1707000-30-L', 'serialNumber': 'TG1252600023PG', 'teslaEnergyEcuAttributes': {'ecuType': 207}}, 'TESLA--None': {'componentParentDin': 'STSTSM--1707000-30-L--TG1252600023PG', 'lastCommunicationTime': None, 'manufacturer': 'TESLA', 'meterAttributes': {'meterLocation': [1]}, 'serialNumber': None}, 'TESYNC--1493315-02-H--JBL25163Y2H0EY': {'ISLAND_FreqL1_Load': 50.04, 'ISLAND_FreqL1_Main': 50.04, 'ISLAND_FreqL2_Load': 50.04, 'ISLAND_FreqL2_Main': 50.04, 'ISLAND_FreqL3_Load': 50.04, 'ISLAND_FreqL3_Main': 49.97, 'ISLAND_GridConnected': 'ISLAND_GridConnected_Connected', 'ISLAND_GridState': 'ISLAND_GridState_Grid_Compliant', 'ISLAND_L1L2PhaseDelta': None, 'ISLAND_L1L3PhaseDelta': None, 'ISLAND_L1MicrogridOk': None, 'ISLAND_L2L3PhaseDelta': None, 'ISLAND_L2MicrogridOk': None, 'ISLAND_L3MicrogridOk': None, 'ISLAND_PhaseL1_Main_Load': None, 'ISLAND_PhaseL2_Main_Load': None, 'ISLAND_PhaseL3_Main_Load': None, 'ISLAND_ReadyForSynchronization': None, 'ISLAND_VL1N_Load': 238, 'ISLAND_VL1N_Main': 239.5, 'ISLAND_VL2N_Load': 8, 'ISLAND_VL2N_Main': 8, 'ISLAND_VL3N_Load': 1.5, 'ISLAND_VL3N_Main': 0.5, 'METER_X_CTA_I': 6.6635, 'METER_X_CTA_InstReactivePower': 1322, 'METER_X_CTA_InstRealPower': 6, 'METER_X_CTB_I': 0, 'METER_X_CTB_InstReactivePower': 0, 'METER_X_CTB_InstRealPower': 0, 'METER_X_CTC_I': 0, 'METER_X_CTC_InstReactivePower': 0, 'METER_X_CTC_InstRealPower': 0, 'METER_X_LifetimeEnergyExport': None, 'METER_X_LifetimeEnergyImport': None, 'METER_X_VL1N': 237.26, 'METER_X_VL2N': 8.040000000000001, 'METER_X_VL3N': 0.45, 'METER_Y_CTA_I': 0, 'METER_Y_CTA_InstReactivePower': 0, 'METER_Y_CTA_InstRealPower': 0, 'METER_Y_CTB_I': 0, 'METER_Y_CTB_InstReactivePower': 0, 'METER_Y_CTB_InstRealPower': 0, 'METER_Y_CTC_I': 0, 'METER_Y_CTC_InstReactivePower': 0, 'METER_Y_CTC_InstRealPower': 0, 'METER_Y_LifetimeEnergyExport': None, 'METER_Y_LifetimeEnergyImport': None, 'METER_Y_VL1N': 236.1, 'METER_Y_VL2N': 8, 'METER_Y_VL3N': 1.51, 'SYNC_ExternallyPowered': None, 'SYNC_SiteSwitchEnabled': None, 'alerts': [], 'componentParentDin': 'STSTSM--1707000-30-L--TG1252600023PG', 'firmwareVersion': None, 'manufacturer': 'TESLA', 'partNumber': '1493315-02-H', 'serialNumber': 'JBL25163Y2H0EY', 'teslaEnergyEcuAttributes': {'ecuType': 259}}, 'TEPOD--1707000-30-L--TG1252600023PG': {'alerts': [], 'POD_nom_energy_remaining': 8680, 'POD_nom_energy_to_be_charged': 5700, 'POD_nom_full_pack_energy': 14380}, 'PVAC--1707000-30-L--TG1252600023PG': {'PVAC_Fout': 50.05, 'PVAC_Vout': 237.20000000000002, 'PVAC_VL1Ground': 118.60000000000001, 'PVAC_VL2Ground': 118.60000000000001, 'PVAC_Pout': -2460, 'PVAC_State': 'AcMode_GridFollowing', 'PVAC_PvState_A': 'Pv_Active', 'PVAC_PVMeasuredVoltage_A': 416, 'PVAC_PVCurrent_A': 2.0999999999999996, 'PVAC_PVMeasuredPower_A': 873.5999999999999, 'manufacturer': 'TESLA', 'partNumber': '1707000-30-L', 'serialNumber': 'TG1252600023PG', 'PVAC_PvState_B': 'Pv_Active_Parallel', 'PVAC_PVMeasuredVoltage_B': 416, 'PVAC_PVCurrent_B': 1.9999999999999998, 'PVAC_PVMeasuredPower_B': 831.9999999999999, 'PVAC_PvState_C': 'Pv_Active', 'PVAC_PVMeasuredVoltage_C': 280, 'PVAC_PVCurrent_C': 2.0999999999999996, 'PVAC_PVMeasuredPower_C': 587.9999999999999, 'PVAC_PvState_D': 'Pv_Active_Parallel', 'PVAC_PVMeasuredVoltage_D': 280, 'PVAC_PVCurrent_D': 1.9999999999999998, 'PVAC_PVMeasuredPower_D': 559.9999999999999, 'PVAC_PvState_E': 'Pv_Active', 'PVAC_PVMeasuredVoltage_E': 0, 'PVAC_PVCurrent_E': 0, 'PVAC_PVMeasuredPower_E': 0, 'PVAC_PvState_F': 'Pv_Active_Parallel', 'PVAC_PVMeasuredVoltage_F': 0, 'PVAC_PVCurrent_F': 0, 'PVAC_PVMeasuredPower_F': 0}, 'PVS--1707000-30-L--TG1252600023PG': {'PVS_StringA_Connected': True, 'PVS_StringB_Connected': True, 'PVS_StringC_Connected': True, 'PVS_StringD_Connected': True, 'PVS_StringE_Connected': True, 'PVS_StringF_Connected': True}, 'TEPINV--1707000-30-L--TG1252600023PG': {'PINV_Fout': 50.05, 'PINV_Vout': 237.20000000000002, 'PINV_VSplit1': 118.60000000000001, 'PINV_VSplit2': 118.60000000000001, 'PINV_Pout': -2.46, 'PINV_State': 'AcMode_GridFollowing'}}
    # logger.info(f"vitals={pw_api.vitals()}")

    # INFO:powerwall2mqtt:alerts=['SystemConnectedToGrid', 'FWUpdateSucceeded']
    # logger.info(f"alerts={pw_api.alerts()}")

    # INFO:powerwall2mqtt:site_name=My Home
    # logger.info(f"site_name={pw_api.site_name()}")

    # INFO:powerwall2mqtt:status={'din': '1707000-30-L--TG1252600023PG', 'start_time': '2026-03-16T17:03:05+13:00', 'up_time_seconds': None, 'is_new': False, 'version': '26.2.1 a7456b0a', 'git_hash': None, 'commission_count': 0, 'device_type': None, 'teg_type': 'unknown', 'sync_type': 'unknown', 'cellular_disabled': False, 'can_reboot': True}
    # logger.info(f"status={pw_api.status()}")
    pass


def main():
    logger = logging.getLogger("powerwall2mqtt")
    poll_time_sec = int(os.getenv('POLL_TIME_S', "10"))

    try:
        pw_api = get_pw_api()
    except Exception as e:
        logger.error(f"Failed to connect to Powerwall: {e}")
        exit(1)

    try:
        mqtt = get_mqtt_client()
    except (ConnectionRefusedError, OSError) as e:
        logger.error(f"Failed to connect to MQTT broker: {e}")
        exit(1)

    try:
        while True:
            logger.info("Polling...")
            fetch_pw_data(
                pw_api=pw_api,
                mqtt=mqtt,
                logger=logger,
                discovery_prefix=os.getenv('MQTT_HA_PREFIX', "homeassistant")
            )
            time.sleep(poll_time_sec)
    except KeyboardInterrupt:
        logger.info("Stopping...")
    finally:
        mqtt.disconnect()


def battery_runtime_minutes(power_w: float, soc: float, capacity_wh: float) -> int:
    """
    Returns estimated minutes until:
      + positive = minutes until empty (when discharging)
      - negative = minutes until full (when charging)
      0 = idle / negligible power
    
    Args:
        power_w: Current power in watts (W)
                      > 0  → discharging
                      < 0  → charging
        soc:          State of charge in % (0–100)
        capacity_wh:  Total battery capacity in watt-hours (Wh)
    """
    if not (0 <= soc <= 100):
        return 0

    remaining_wh = (soc / 100.0) * capacity_wh

    # Discharging (power > 0)
    if power_w > 100 and remaining_wh > 100:
        minutes = (remaining_wh / power_w) * 60
        return round(minutes)

    # Charging (power < 0)
    elif power_w < -100 and soc < 99.9:
        missing_wh = capacity_wh - remaining_wh
        minutes_to_full = missing_wh / abs(power_w) * 60
        return -round(minutes_to_full)

    # Idle
    else:
        return 0


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
