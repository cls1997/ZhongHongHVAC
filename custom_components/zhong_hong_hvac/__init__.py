"""The zhong_hong component."""
from __future__ import annotations

import logging

import voluptuous as vol
from .hub import ZhongHongGateway
from .climate import ZhongHongClimate
from .const import SIGNAL_DEVICE_ADDED

from homeassistant.components.climate import PLATFORM_SCHEMA
from homeassistant.const import (
    CONF_HOST,
    CONF_PORT,
    EVENT_HOMEASSISTANT_STOP,
)
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

_LOGGER = logging.getLogger(__name__)

CONF_GATEWAY_ADDRRESS = "gateway_address"

DEFAULT_PORT = 9999
DEFAULT_GATEWAY_ADDRRESS = 1

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_HOST): cv.string,
        vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
        vol.Optional(
            CONF_GATEWAY_ADDRRESS, default=DEFAULT_GATEWAY_ADDRRESS
        ): cv.positive_int,
    }
)



def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the ZhongHong HVAC platform."""

    host = config.get(CONF_HOST)
    port = config.get(CONF_PORT)
    gw_addr = config.get(CONF_GATEWAY_ADDRRESS)
    hub = ZhongHongGateway(host, port, gw_addr)
    devices = [
        ZhongHongClimate(hub, addr_out, addr_in)
        for (addr_out, addr_in) in hub.discovery_ac()
    ]

    _LOGGER.debug("We got %s zhong_hong climate devices", len(devices))

    hub_is_initialized = False

    def _start_hub():
        """Start the hub socket and query status of all devices."""
        hub.start_listen()
        hub.query_all_status()

    async def startup():
        """Start hub socket after all climate entity is set up."""
        nonlocal hub_is_initialized
        if not all(device.is_initialized for device in devices):
            return

        if hub_is_initialized:
            return

        _LOGGER.debug("zhong_hong hub start listen event")
        await hass.async_add_executor_job(_start_hub)
        hub_is_initialized = True

    async_dispatcher_connect(hass, SIGNAL_DEVICE_ADDED, startup)

    # add devices after SIGNAL_DEVICE_SETTED_UP event is listened
    add_entities(devices)

    def stop_listen(event):
        """Stop ZhongHongHub socket."""
        hub.stop_listen()

    hass.bus.listen_once(EVENT_HOMEASSISTANT_STOP, stop_listen)
