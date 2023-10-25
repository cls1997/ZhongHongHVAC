"""Constants for the ZhongHong HVAC integration."""
from homeassistant.components.climate import HVACMode

SIGNAL_DEVICE_ADDED = "zhong_hong_device_added"
SIGNAL_ZHONG_HONG_HUB_START = "zhong_hong_hub_start"

ZHONG_HONG_MODE_COOL = "cool"
ZHONG_HONG_MODE_HEAT = "heat"
ZHONG_HONG_MODE_DRY = "dry"
ZHONG_HONG_MODE_FAN_ONLY = "fan_only"


MODE_TO_STATE = {
    ZHONG_HONG_MODE_COOL: HVACMode.COOL,
    ZHONG_HONG_MODE_HEAT: HVACMode.HEAT,
    ZHONG_HONG_MODE_DRY: HVACMode.DRY,
    ZHONG_HONG_MODE_FAN_ONLY: HVACMode.FAN_ONLY,
}
