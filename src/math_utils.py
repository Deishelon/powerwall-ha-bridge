def battery_runtime_minutes(power_w: float, soc: float, capacity_wh: float) -> int:
    """
    Returns estimated minutes until empty or full
    or 0 = idle / negligible power

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
        minutes_to_empty = (remaining_wh / power_w) * 60
        return round(minutes_to_empty)

    # Charging (power < 0)
    elif power_w < -100 and soc < 99.9:
        missing_wh = capacity_wh - remaining_wh
        minutes_to_full = missing_wh / abs(power_w) * 60
        return round(minutes_to_full)

    # Idle
    else:
        return 0
