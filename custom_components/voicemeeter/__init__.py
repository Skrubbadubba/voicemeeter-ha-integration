from __future__ import annotations

import asyncio

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady, ConfigEntryError

from .const import CONF_HOST, CONF_PORT, DEFAULT_PORT, LOGGER, SUPPORTED_PROTOCOL_MAJOR
from .coordinator import VoicemeeterCoordinator
from .data import VoicemeeterRuntimeData
from .websocket import VoicemeeterWebSocket

PLATFORMS = [Platform.SWITCH, Platform.NUMBER]

FIRST_STATE_TIMEOUT = 10 # seconds


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    coordinator = VoicemeeterCoordinator(hass)

    ws = VoicemeeterWebSocket(
        host=entry.data[CONF_HOST],
        port=entry.data.get(CONF_PORT, DEFAULT_PORT),
        on_message=coordinator.handle_message,
        on_connect=coordinator.handle_connect,
        on_disconnect=coordinator.handle_disconnect,
    )

    entry.runtime_data = VoicemeeterRuntimeData(coordinator=coordinator, ws=ws)

    ws_task = hass.async_create_background_task(
        ws.start(),
        name="voicemeeter_websocket",
    )
    async def _cancel_ws_task() -> None:
        ws_task.cancel()

    entry.async_on_unload(_cancel_ws_task)
    entry.async_on_unload(ws.stop)

    # Wait until the coordinator has real state (set by first state message)
    # before setting up platforms — entities need coordinator.data to exist
    # so they know how many strips and buses to create.
    try:
        await asyncio.wait_for(
            _wait_for_state(coordinator),
            timeout=FIRST_STATE_TIMEOUT,
        )
        current_protocol = coordinator.data.protocol
        _check_protocol(current_protocol)
    except TimeoutError:
        LOGGER.warning(
            "Voicemeeter companion app did not send state within %ss — "
            "check that the app is running at %s:%s",
            FIRST_STATE_TIMEOUT,
            entry.data[CONF_HOST],
            entry.data.get(CONF_PORT, DEFAULT_PORT),
        )
        raise ConfigEntryNotReady("No state received from companion app")

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def _wait_for_state(coordinator: VoicemeeterCoordinator) -> None:
    """Block until coordinator.data is populated."""
    while coordinator.data is None:
        await asyncio.sleep(0.1)

def _check_protocol(current_protocol: str) -> None:
    
    current_major = current_protocol.split(".")[0]

    if current_major != SUPPORTED_PROTOCOL_MAJOR:
        raise ConfigEntryError(
            f"Unsupported protocol version {current_protocol}. "
            f"This integration requires protocol {SUPPORTED_PROTOCOL_MAJOR}.x. "
            "Update your companion app or the integration."
        )


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
