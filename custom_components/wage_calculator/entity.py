"""Base entity for the Wage calculator integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.entity import DeviceInfo, Entity
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import DOMAIN, TRANSLATION_KEY


class ComponentEntity(CoordinatorEntity[DataUpdateCoordinator], Entity):
    """Defines a Wage calculator entity."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the Wage calculator entity."""
        super().__init__(coordinator=coordinator)
        self._attr_device_info = DeviceInfo(
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(DOMAIN, entry.entry_id)},
            manufacturer="KGN",
            translation_key=TRANSLATION_KEY,
            suggested_area="",
            sw_version="1.0",
            name=DOMAIN,
        )
