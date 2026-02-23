from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode
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
        entities.append(StripGainNumber(coordinator, entry.entry_id, strip.index))
    for bus in coordinator.data.buses:
        entities.append(BusGainNumber(coordinator, entry.entry_id, bus.index))
    async_add_entities(entities)


class StripGainNumber(VoicemeeterEntity, NumberEntity):
    _attr_native_min_value = -60.0
    _attr_native_max_value = 12.0
    _attr_native_step = 0.1
    _attr_native_unit_of_measurement = "dB"
    _attr_mode = NumberMode.SLIDER

    def __init__(
        self, coordinator: VoicemeeterCoordinator, entry_id: str, index: int
    ) -> None:
        super().__init__(coordinator, entry_id)
        self._index = index
        self._attr_unique_id = f"{entry_id}_strip_{index}_gain"

    @property
    def name(self) -> str:
        strip = self._strip
        kind = self.coordinator.data.kind if self.coordinator.data else "banana"
        label = (
            strip.label if strip and strip.label else get_strip_label(kind, self._index)
        )
        return f"{label} Gain"

    @property
    def native_value(self) -> float:
        strip = self._strip
        return strip.gain if strip else 0.0

    @property
    def _strip(self):
        if not self.coordinator.data:
            return None
        return next(
            (s for s in self.coordinator.data.strips if s.index == self._index), None
        )

    async def async_set_native_value(self, value: float) -> None:
        await self.coordinator.config_entry.runtime_data.ws.send(
            {
                "type": "set",
                "target": "strip",
                "index": self._index,
                "param": "gain",
                "value": value,
            }
        )


class BusGainNumber(VoicemeeterEntity, NumberEntity):
    _attr_entity_category = EntityCategory.CONFIG
    _attr_native_min_value = -60.0
    _attr_native_max_value = 12.0
    _attr_native_step = 0.1
    _attr_native_unit_of_measurement = "dB"
    _attr_mode = NumberMode.SLIDER

    def __init__(
        self, coordinator: VoicemeeterCoordinator, entry_id: str, index: int
    ) -> None:
        super().__init__(coordinator, entry_id)
        self._index = index
        self._attr_unique_id = f"{entry_id}_bus_{index}_gain"

    @property
    def name(self) -> str:
        if not self.coordinator.data:
            return f"Bus {self._index} Master Gain"
        if self._bus.label:
            return f"{self._bus.label} Master Gain"
        return f"{get_bus_label(self.coordinator.data.kind, self._index)} Master Gain"

    @property
    def native_value(self) -> float:
        bus = self._bus
        return bus.gain if bus else 0.0

    @property
    def _bus(self):
        if not self.coordinator.data:
            return None
        return next(
            (b for b in self.coordinator.data.buses if b.index == self._index), None
        )

    async def async_set_native_value(self, value: float) -> None:
        await self.coordinator.config_entry.runtime_data.ws.send(
            {
                "type": "set",
                "target": "bus",
                "index": self._index,
                "param": "gain",
                "value": value,
            }
        )
