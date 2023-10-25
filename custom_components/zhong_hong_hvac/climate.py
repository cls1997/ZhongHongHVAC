"""Support for ZhongHong HVAC Controller."""
import logging
from typing import Any

from .hvac import HVAC as ZhongHongHVAC
from .const import (
   MODE_TO_STATE,
   SIGNAL_DEVICE_ADDED 
)

from homeassistant.const import ATTR_TEMPERATURE

from homeassistant.components.climate import (
    ATTR_HVAC_MODE,
    HVACMode,
    ClimateEntity,
    ClimateEntityFeature,
    UnitOfTemperature
)

from homeassistant.helpers.dispatcher import async_dispatcher_send

_LOGGER = logging.getLogger(__name__)

class ZhongHongClimate(ClimateEntity):
    """Representation of a ZhongHong controller support HVAC."""

    _attr_hvac_modes = [
        HVACMode.COOL,
        HVACMode.HEAT,
        HVACMode.DRY,
        HVACMode.FAN_ONLY,
        HVACMode.OFF,
    ]
    _attr_should_poll = False
    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE | ClimateEntityFeature.FAN_MODE
    )
    _attr_temperature_unit = UnitOfTemperature.CELSIUS

    def __init__(self, hub, addr_out, addr_in):
        """Set up the ZhongHong climate devices."""

        self._device = ZhongHongHVAC(hub, addr_out, addr_in)
        self._hub = hub
        self._current_operation = None
        self._current_temperature = None
        self._target_temperature = None
        self._current_fan_mode = None
        self.is_initialized = False

    async def async_added_to_hass(self) -> None:
        """Register callbacks."""
        self._device.register_update_callback(self._after_update)
        self.is_initialized = True
        async_dispatcher_send(self.hass, SIGNAL_DEVICE_ADDED)

    def _after_update(self, climate):
        """Handle state update."""
        _LOGGER.debug("async update ha state")
        if self._device.current_operation:
            self._current_operation = MODE_TO_STATE[
                self._device.current_operation.lower()
            ]
        if self._device.current_temperature:
            self._current_temperature = self._device.current_temperature
        if self._device.current_fan_mode:
            self._current_fan_mode = self._device.current_fan_mode
        if self._device.target_temperature:
            self._target_temperature = self._device.target_temperature
        self.schedule_update_ha_state()

    @property
    def name(self):
        """Return the name of the thermostat, if any."""
        return self.unique_id

    @property
    def unique_id(self):
        """Return the unique ID of the HVAC."""
        return f"zhong_hong_hvac_{self._device.addr_out}_{self._device.addr_in}"

    @property
    def hvac_mode(self) -> HVACMode:
        """Return current operation ie. heat, cool, idle."""
        if self.is_on:
            return self._current_operation
        return HVACMode.OFF

    @property
    def current_temperature(self):
        """Return the current temperature."""
        return self._current_temperature

    @property
    def target_temperature(self):
        """Return the temperature we try to reach."""
        return self._target_temperature

    @property
    def target_temperature_step(self):
        """Return the supported step of target temperature."""
        return 1

    @property
    def is_on(self):
        """Return true if on."""
        return self._device.is_on

    @property
    def fan_mode(self):
        """Return the fan setting."""
        return self._current_fan_mode

    @property
    def fan_modes(self):
        """Return the list of available fan modes."""
        return self._device.fan_list

    @property
    def min_temp(self):
        """Return the minimum temperature."""
        return self._device.min_temp

    @property
    def max_temp(self):
        """Return the maximum temperature."""
        return self._device.max_temp

    def turn_on(self) -> None:
        """Turn on ac."""
        return self._device.turn_on()

    def turn_off(self) -> None:
        """Turn off ac."""
        return self._device.turn_off()

    def set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        if (temperature := kwargs.get(ATTR_TEMPERATURE)) is not None:
            self._device.set_temperature(temperature)

        if (operation_mode := kwargs.get(ATTR_HVAC_MODE)) is not None:
            self.set_hvac_mode(operation_mode)

    def set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new target operation mode."""
        if hvac_mode == HVACMode.OFF:
            if self.is_on:
                self.turn_off()
            return

        if not self.is_on:
            self.turn_on()

        self._device.set_operation_mode(hvac_mode.upper())

    def set_fan_mode(self, fan_mode: str) -> None:
        """Set new target fan mode."""
        self._device.set_fan_mode(fan_mode)