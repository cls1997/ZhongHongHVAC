import logging
import voluptuous as vol
from typing import Any, Dict
from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    FlowResult,
    OptionsFlowWithConfigEntry
)
from homeassistant.core import callback
import homeassistant.helpers.config_validation as cv

from . import (
    init_integration_data
)
from .const import (
    DOMAIN,
    CONF_HOST,
    CONF_PORT,
    DEFAULT_PORT,
    CONF_GATEWAY_ADDRRESS,
    DEFAULT_GATEWAY_ADDRRESS
)
from .hub import ZhongHongGateway

_LOGGER = logging.getLogger(__name__)


async def test_hub(user_input: Dict[str, Any]):
    host = user_input.get(CONF_HOST)
    port = user_input.get(CONF_PORT)
    gateway_address = user_input.get(CONF_GATEWAY_ADDRRESS)

    # hub = ZhongHongGateway(host, port, gateway_address)
    # TODO: test


def schema_generator(default_provider: Dict[str, Any]) -> vol.Schema:
    return vol.Schema({
        vol.Required(CONF_HOST, default=default_provider.get(CONF_HOST, vol.UNDEFINED)): cv.string,
        vol.Optional(CONF_PORT, default=default_provider.get(CONF_PORT, DEFAULT_PORT)): cv.port,
        vol.Optional(
            CONF_GATEWAY_ADDRRESS, default=default_provider.get(
                CONF_GATEWAY_ADDRRESS, DEFAULT_GATEWAY_ADDRRESS)
        ): cv.positive_int,
    })


class ZhongHongConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(entry: ConfigEntry):
        return ZhongHongOptionsFlow(entry)

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        hass = self.hass

        init_integration_data(hass)

        errors: Dict[str, str] = {}
        if user_input is None:
            user_input = {}
        else:
            data = {}
            for k, v in user_input.items():
                if k in [CONF_HOST, CONF_PORT, CONF_GATEWAY_ADDRRESS]:
                    data[k] = v
            try:
                await test_hub(user_input)
            except ValueError:
                errors["base"] = "connection_error"
            if not errors:
                return self.async_create_entry(
                    title="config",
                    data=data
                )
        data_schema = schema_generator(user_input)
        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
            last_step=True
        )


class ZhongHongOptionsFlow(OptionsFlowWithConfigEntry):
    def __init__(self, config_entry: ConfigEntry) -> None:
        super().__init__(config_entry)

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        errors: Dict[str, str] = {}
        data = self.config_entry.data
        if user_input is None:
            user_input = {}
        else:
            try:
                await test_hub(user_input)
            except ValueError:
                errors["base"] = "connection_error"
            if not errors:
                config = {}
                for k, v in user_input.items():
                    if k in [CONF_HOST, CONF_PORT, CONF_GATEWAY_ADDRRESS]:
                        config[k] = v

                self.hass.config_entries.async_update_entry(
                    self.config_entry, data={
                        **self.config_entry.data, **config
                    }
                )

                return self.async_create_entry(
                    title="",
                    data=config
                )

        _LOGGER.debug("Options: %s", data)

        data_schema = schema_generator(user_input)
        return self.async_show_form(
            step_id="init",
            data_schema=data_schema,
            errors=errors,
            last_step=True
        )
