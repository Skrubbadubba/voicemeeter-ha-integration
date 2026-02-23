"""
WebSocket client for the Voicemeeter companion app.

Manages the connection lifecycle: connect, receive messages, reconnect on
drop. Communicates with the coordinator exclusively through callbacks so it
has no dependency on HA internals.
"""

from __future__ import annotations

import asyncio
import json
from collections.abc import Callable
from typing import Any

import aiohttp

from .const import LOGGER

RECONNECT_DELAY = 5  # seconds between reconnect attempts


class VoicemeeterWebSocket:
    """
    Persistent WebSocket connection to the companion app.

    Owns the connection loop. Calls provided callbacks when messages arrive
    or the connection state changes. Accepts outbound messages via send().
    """

    def __init__(
        self,
        host: str,
        port: int,
        on_message: Callable[[dict[str, Any]], None],
        on_connect: Callable[[], None],
        on_disconnect: Callable[[], None],
    ) -> None:
        self._url = f"ws://{host}:{port}/ws"
        self._on_message = on_message
        self._on_connect = on_connect
        self._on_disconnect = on_disconnect

        self._ws: aiohttp.ClientWebSocketResponse | None = None
        self._running = False

    async def start(self) -> None:
        """
        Start the connection loop.

        Runs until stop() is called. Should be launched as a background task:
            hass.async_create_background_task(ws.start(), ...)
        """
        self._running = True
        while self._running:
            try:
                await self._connect()
            except Exception as err:
                LOGGER.warning("Voicemeeter WS connection error: %s", err)

            if self._running:
                self._on_disconnect()
                LOGGER.debug(
                    "Voicemeeter WS disconnected, retrying in %ss", RECONNECT_DELAY
                )
                await asyncio.sleep(RECONNECT_DELAY)

    async def stop(self) -> None:
        """Stop the connection loop and close the socket."""
        self._running = False
        if self._ws and not self._ws.closed:
            await self._ws.close()

    async def send(self, data: dict[str, Any]) -> None:
        """
        Send a message to the companion app.

        Silently drops the message if not connected. The caller does not need
        to handle the disconnected case — the entity will become unavailable
        and the user cannot interact with it.
        """
        if self._ws and not self._ws.closed:
            await self._ws.send_str(json.dumps(data))
        else:
            LOGGER.debug("WS send skipped, not connected: %s", data)

    async def _connect(self) -> None:
        """Open a connection and block until it closes."""
        async with aiohttp.ClientSession() as session, session.ws_connect(
            self._url,
            heartbeat=30,  # aiohttp sends WS pings every 30s
            timeout=aiohttp.ClientWSTimeout(ws_close=5),
        ) as ws:
            self._ws = ws
            self._on_connect()
            LOGGER.info("Connected to Voicemeeter companion app at %s", self._url)

            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    try:
                        self._on_message(json.loads(msg.data))
                    except Exception as err:
                        LOGGER.error("Failed to handle WS message: %s", err)
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    LOGGER.warning("Voicemeeter WS error frame received")
                    break

            self._ws = None
