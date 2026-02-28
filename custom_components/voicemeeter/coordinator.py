from __future__ import annotations

from typing import Any

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.config_entries import ConfigEntryDisabler

from .const import DOMAIN, LOGGER
from .data import VoicemeeterState, apply_update_message, parse_state_message


class VoicemeeterCoordinator(DataUpdateCoordinator[VoicemeeterState | None]):
    """
    Holds current Voicemeeter state and notifies entities on change.

    Data is None until the first state message arrives from the companion app.
    Entities check coordinator.data is not None to determine availability.
    """

    def __init__(self, hass: HomeAssistant) -> None:
        super().__init__(
            hass,
            LOGGER,
            name=DOMAIN,
        )
        self.connected = False

    # ------------------------------------------------------------------
    # WebSocket callbacks — called by VoicemeeterWebSocket
    # ------------------------------------------------------------------

    @callback
    def handle_connect(self) -> None:
        """
        Called when the WebSocket connection is established.

        We don't set data here — we wait for the state message that the
        companion app sends immediately after connect. That way entities
        only become available once we actually have state, not just a socket.
        """
        self.connected = True
        LOGGER.debug("Voicemeeter coordinator: connected")

    @callback
    def handle_disconnect(self) -> None:
        """Called when the WebSocket connection is lost."""
        self.connected = False
        self.async_update_listeners()
        LOGGER.debug("Voicemeeter coordinator: disconnected, entities now unavailable")

    @callback
    def handle_message(self, msg: dict[str, Any]) -> None:
        """Called for every incoming WebSocket message."""
        msg_type = msg.get("type")

        if msg_type == "state":
            LOGGER.debug(f"Recieved state: {msg}")
            old_state = self.data
            old_kind = old_state.kind if old_state else None
            old_protocol = old_state.protocol if old_state else None

            parsed_new_state = parse_state_message(msg)
            self.async_set_updated_data(parsed_new_state)

            if old_kind and old_kind != parsed_new_state.kind:
                LOGGER.debug(f"New kind ({parsed_new_state.kind}) recieved, reloading entry")
                self.hass.async_create_task(
                    self.hass.config_entries.async_reload(self.config_entry.entry_id)
                )

            if old_protocol and old_protocol != parsed_new_state.protocol:
                old_major_ver = old_protocol.split(".")[0]
                new_major_ver = parsed_new_state.protocol.split(".")[0]
                if old_major_ver != new_major_ver:
                    LOGGER.warning("Protocol major version change detected, triggering reload")
                    self.hass.async_create_task(
                        self.hass.config_entries.async_reload(self.config_entry.entry_id)
                    )
                    return

                # TODO: Notify user
                pass

        elif msg_type == "update":
            LOGGER.debug(f"Voicemeeter: recieved update message: {msg}")
            if self.data is None:
                # Received an update before the initial state dump — ignore.
                LOGGER.warning("Voicemeeter: received update before state, ignoring")
                return
            self.async_set_updated_data(apply_update_message(self.data, msg))

        else:
            LOGGER.debug("Voicemeeter: unknown message type %r, ignoring", msg_type)
