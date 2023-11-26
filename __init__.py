"""The zhong_hong component."""

import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from .const import (
    DOMAIN,
    CONF_HOST,
    CONF_PORT,
    CONF_GATEWAY_ADDRRESS,
    DEFAULT_PORT,
    DEFAULT_GATEWAY_ADDRRESS,
)

_LOGGER = logging.getLogger(__name__)


def init_integration_data(hass: HomeAssistant):
    hass.data.setdefault(DOMAIN, {})


async def async_setup_entry(
    hass: HomeAssistant, config_entry: ConfigEntry
) -> bool:
    _LOGGER.info("Entry setup...")
    init_integration_data(hass)

    _LOGGER.debug(
        f"Cofig Entry: {config_entry.entry_id} [{config_entry.unique_id}]")

    _LOGGER.debug("Config Entry Data: %s", config_entry.data)
    config = dict(config_entry.data)

    hass.data[DOMAIN][config_entry.entry_id] = config

    if not config_entry.update_listeners:
        config_entry.add_update_listener(async_update_options)

    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(
            config_entry, Platform.CLIMATE)
    )

    return True


async def async_update_options(hass: HomeAssistant, config_entry: ConfigEntry):
    _LOGGER.info("Options Updated.")
    _LOGGER.debug("Config Entry Data: %s", config_entry.data)

    await hass.config_entries.async_reload(config_entry.entry_id)


async def async_setup_config_entry(hass, config_entry, async_setup_platform, async_add_entities, domain=None):
    entry_id = config_entry.entry_id
    cfg = hass.data[DOMAIN].get(entry_id) or {}
    if not cfg:
        hass.data[DOMAIN].setdefault(entry_id, {})
    if domain:
        hass.data[DOMAIN][entry_id].setdefault('add_entities', {})
        hass.data[DOMAIN][entry_id]['add_entities'][domain] = async_add_entities
    cls = cfg.get('configs')
    if not cls:
        cls = [
            hass.data[DOMAIN].get(entry_id, config_entry.data),
        ]
    for c in cls:
        if async_setup_platform is None:
            _LOGGER.error(
                "Something goes wrong, async_setup_platform is None.")
        await async_setup_platform(hass, c, async_add_entities)
    return cls
