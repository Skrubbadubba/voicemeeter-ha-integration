from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import VoicemeeterCoordinator


class VoicemeeterEntity(CoordinatorEntity[VoicemeeterCoordinator]):
    _attr_has_entity_name = True

    def __init__(self, coordinator: VoicemeeterCoordinator, entry_id: str) -> None:
        super().__init__(coordinator)
        self._entry_id = entry_id

    @property
    def available(self) -> bool:
        return self.coordinator.connected

    @property
    def device_info(self) -> DeviceInfo:
        kind = self.coordinator.data.kind if self.coordinator.data else "voicemeeter"
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry_id)},
            name=f"Voicemeeter {self.coordinator.config_entry.title}",
            manufacturer="VB-Audio",
            model=kind.capitalize(),
        )
