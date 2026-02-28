from __future__ import annotations

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult

from .const import (
    CONF_HOST,
    CONF_KIND,
    CONF_NAME,
    CONF_PORT,
    DEFAULT_KIND,
    DEFAULT_PORT,
    DOMAIN,
    VOICEMEETER_KINDS,
)


class VoicemeeterConfigFlow(ConfigFlow, domain=DOMAIN):

    VERSION = 1

    async def async_step_user(self, user_input: dict | None = None) -> ConfigFlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            # Prevent duplicate entries for the same host
            await self.async_set_unique_id(
                f"{user_input[CONF_HOST]}:{user_input[CONF_PORT]}"
            )
            self._abort_if_unique_id_configured()
            name = user_input.get(CONF_NAME, "").strip()
            title = name if name else f"Voicemeeter ({user_input[CONF_HOST]})"
            return self.async_create_entry(title=title, data=user_input)

        schema = vol.Schema(
            {
                vol.Optional(CONF_NAME, default=""): str,
                vol.Required(CONF_HOST, default="192.168.1.63"): str,
                vol.Required(CONF_PORT, default=DEFAULT_PORT): int,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )
