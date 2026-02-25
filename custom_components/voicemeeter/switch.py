from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import get_bus_label, get_strip_label
from .coordinator import VoicemeeterCoordinator
from .entity import VoicemeeterEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data.coordinator
    entities = []
    for strip in coordinator.data.strips:
        entities.append(StripMuteSwitch(coordinator, entry.entry_id, strip.index))
        for bus in coordinator.data.buses:
            entities.append(
                StripRouteSwitch(coordinator, entry.entry_id, strip.index, bus.index)
            )
    for bus in coordinator.data.buses:
        entities.append(BusMuteSwitch(coordinator, entry.entry_id, bus.index))
    async_add_entities(entities)


class StripMuteSwitch(VoicemeeterEntity, SwitchEntity):
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(
        self, coordinator: VoicemeeterCoordinator, entry_id: str, index: int
    ) -> None:
        super().__init__(coordinator, entry_id)
        self._index = index
        self._attr_unique_id = f"{entry_id}_strip_{index}_mute"

    @property
    def name(self) -> str:
        strip = self._strip
        kind = self.coordinator.data.kind if self.coordinator.data else "banana"
        label = (
            strip.label if strip and strip.label else get_strip_label(kind, self._index)
        )
        return f"{label} Mute"

    @property
    def is_on(self) -> bool:
        strip = self._strip
        return strip.mute if strip else False

    @property
    def _strip(self):
        if not self.coordinator.data:
            return None
        return next(
            (s for s in self.coordinator.data.strips if s.index == self._index), None
        )

    async def async_turn_on(self, **kwargs) -> None:
        await self.coordinator.config_entry.runtime_data.ws.send(
            {
                "type": "set",
                "target": "strip",
                "index": self._index,
                "param": "mute",
                "value": True,
            }
        )

    async def async_turn_off(self, **kwargs) -> None:
        await self.coordinator.config_entry.runtime_data.ws.send(
            {
                "type": "set",
                "target": "strip",
                "index": self._index,
                "param": "mute",
                "value": False,
            }
        )


class StripRouteSwitch(VoicemeeterEntity, SwitchEntity):
    def __init__(
        self,
        coordinator: VoicemeeterCoordinator,
        entry_id: str,
        strip_index: int,
        bus_index: int,
    ) -> None:
        super().__init__(coordinator, entry_id)
        self._strip_index = strip_index
        self._bus_index = bus_index
        self._attr_unique_id = f"{entry_id}_strip_{strip_index}-bus_{bus_index}_toggle"

    @property
    def name(self) -> str:
        strip = self._strip
        bus = self._bus
        kind = self.coordinator.data.kind if self.coordinator.data else "banana"
        strip_label = (
            strip.label
            if strip and strip.label
            else get_strip_label(kind, self._strip_index)
        )
        bus_label = bus.label if bus and bus.label else get_bus_label(kind, self._bus_index)
        return f"{strip_label} - {bus_label} Toggle"

    @property
    def is_on(self) -> bool:
        strip = self._strip
        if not strip:
            return False
        kind = self.coordinator.data.kind if self.coordinator.data else 'banana'
        bus_canonical_label = get_bus_label(kind, self._bus_index).lower()
        return getattr(strip, bus_canonical_label, False)

    @property
    def _strip(self):
        if not self.coordinator.data:
            return None
        return next(
            (s for s in self.coordinator.data.strips if s.index == self._strip_index),
            None,
        )

    @property
    def _bus(self):
        if not self.coordinator.data:
            return None
        return next(
            (b for b in self.coordinator.data.buses if b.index == self._bus_index), None
        )

    async def async_turn_on(self, **kwargs) -> None:
        await self.coordinator.config_entry.runtime_data.ws.send(
            {
                "type": "set",
                "target": "strip",
                "index": self._strip_index,
                "param": get_bus_label(
                    self.coordinator.data.kind or "banana", self._bus_index
                ).lower(),
                "value": True,
            }
        )

    async def async_turn_off(self, **kwargs) -> None:
        await self.coordinator.config_entry.runtime_data.ws.send(
            {
                "type": "set",
                "target": "strip",
                "index": self._strip_index,
                "param": get_bus_label(
                    self.coordinator.data.kind or "banana", self._bus_index
                ).lower(),
                "value": False,
            }
        )


class BusMuteSwitch(VoicemeeterEntity, SwitchEntity):
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(
        self, coordinator: VoicemeeterCoordinator, entry_id: str, index: int
    ) -> None:
        super().__init__(coordinator, entry_id)
        self._index = index
        self._attr_unique_id = f"{entry_id}_bus_{index}_mute"

    @property
    def name(self) -> str:
        if not self.coordinator.data:
            return f"Bus {self._index} Master Mute"
        if self._bus.label:
            return f"{self._bus.label} Master Mute"
        return f"{get_bus_label(self.coordinator.data.kind, self._index)} Master Mute"

    @property
    def is_on(self) -> bool:
        bus = self._bus
        return bus.mute if bus else False

    @property
    def _bus(self):
        if not self.coordinator.data:
            return None
        return next(
            (b for b in self.coordinator.data.buses if b.index == self._index), None
        )

    async def async_turn_on(self, **kwargs) -> None:
        await self.coordinator.config_entry.runtime_data.ws.send(
            {
                "type": "set",
                "target": "bus",
                "index": self._index,
                "param": "mute",
                "value": True,
            }
        )

    async def async_turn_off(self, **kwargs) -> None:
        await self.coordinator.config_entry.runtime_data.ws.send(
            {
                "type": "set",
                "target": "bus",
                "index": self._index,
                "param": "mute",
                "value": False,
            }
        )
