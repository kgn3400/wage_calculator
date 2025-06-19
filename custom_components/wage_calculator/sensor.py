"""Sensor for Wage calculator."""

from __future__ import annotations

from datetime import timedelta
from typing import Any

import voluptuous as vol

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import MATCH_ALL
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import entity_platform
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.selector import NumberSelector, NumberSelectorConfig

from . import CommonConfigEntry
from .const import CONF_FLEX_HOURS
from .entity import ComponentEntity


# ------------------------------------------------------
async def async_setup_entry(
    hass: HomeAssistant,
    entry: CommonConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Sensor setup."""

    sensors = []

    sensors.append(WageCalcSensor(hass, entry))

    async_add_entities(sensors)


# ------------------------------------------------------
# ------------------------------------------------------
class WageCalcSensor(ComponentEntity, SensorEntity):
    """Sensor class for Wage calculator."""

    _unrecorded_attributes = frozenset({MATCH_ALL})

    # ------------------------------------------------------
    def __init__(
        self,
        hass: HomeAssistant,
        entry: CommonConfigEntry,
    ) -> None:
        """Wage calculator sensor."""

        super().__init__(entry.runtime_data.coordinator, entry)

        self.hass: HomeAssistant = hass
        self.entry: CommonConfigEntry = entry
        self.component_api = entry.runtime_data.component_api
        self.coordinator = entry.runtime_data.coordinator

        self.translation_key = "salary"

        platform = entity_platform.async_get_current_platform()
        platform.async_register_entity_service(
            "flex_hours_set",
            {
                vol.Required(CONF_FLEX_HOURS): NumberSelector(
                    NumberSelectorConfig(
                        min=-999,
                        max=999,
                    )
                ),
            },
            self.async_flex_hours_set,
        )
        platform.async_register_entity_service(
            "flex_hours_add",
            {
                vol.Required(CONF_FLEX_HOURS): NumberSelector(
                    NumberSelectorConfig(
                        min=0,
                        max=999,
                    )
                ),
            },
            self.async_flex_hours_add,
        )
        platform.async_register_entity_service(
            "flex_hours_subtract",
            {
                vol.Required(CONF_FLEX_HOURS): NumberSelector(
                    NumberSelectorConfig(
                        min=0,
                        max=999,
                    )
                ),
            },
            self.async_flex_hours_subtract,
        )

        self.coordinator.update_method = self.async_refresh
        self.coordinator.update_interval = timedelta(minutes=15)

    # ------------------------------------------------------------------
    async def async_flex_hours_set(
        self, entity: WageCalcSensor, service_data: ServiceCall
    ) -> None:
        """Set flex hours."""

        entity.component_api.calc_monthly_wage.flex_hours = service_data.data.get(
            CONF_FLEX_HOURS, 0.0
        )

        entity.update_config()
        await entity.coordinator.async_refresh()

    # ------------------------------------------------------------------
    async def async_flex_hours_add(
        self, entity: WageCalcSensor, service_data: ServiceCall
    ) -> None:
        """Add flex hours."""

        entity.component_api.calc_monthly_wage.flex_hours += service_data.data.get(
            CONF_FLEX_HOURS, 0.0
        )
        entity.update_config()
        await entity.coordinator.async_refresh()

    # ------------------------------------------------------------------
    async def async_flex_hours_subtract(
        self, entity: WageCalcSensor, service_data: ServiceCall
    ) -> None:
        """Add flex hours."""
        entity.component_api.calc_monthly_wage.flex_hours -= service_data.data.get(
            CONF_FLEX_HOURS, 0.0
        )
        entity.update_config()
        await entity.coordinator.async_refresh()

    # ------------------------------------------------------------------
    def update_config(self) -> None:
        """Update config."""

        tmp_options: dict[str, Any] = self.entry.options.copy()
        tmp_options[CONF_FLEX_HOURS] = self.component_api.calc_monthly_wage.flex_hours

        self.hass.config_entries.async_update_entry(
            self.entry, data=tmp_options, options=tmp_options
        )

    # ------------------------------------------------------
    @property
    def name(self) -> str:
        """Name.

        Returns:
            str: Name of sensor

        """

        return self.entry.title + " " + super().name

    # ------------------------------------------------------
    @property
    def native_value(self) -> float | None:
        """Native value.

        Returns:
            str | None: Native value

        """
        return self.component_api.calc_monthly_wage.salary

    # ------------------------------------------------------
    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return the unit the value is expressed in."""

        return self.component_api.currency_sign

    # ------------------------------------------------------
    @property
    def extra_state_attributes(self) -> dict:
        """Extra state attributes.

        Returns:
            dict: Extra state attributes

        """
        return {
            "salary_before_today": self.component_api.calc_monthly_wage.salary_before_today,
            "salary_after_today": self.component_api.calc_monthly_wage.salary_after_today,
            "total_hours": self.component_api.calc_monthly_wage.total_hours,
            "total_hours_before_today": self.component_api.calc_monthly_wage.total_hours_before_today,
            "total_hours_after_today": self.component_api.calc_monthly_wage.total_hours_after_today,
            "month_work_days": self.component_api.calc_monthly_wage.month_work_days,
            "month_work_days_before_today": self.component_api.calc_monthly_wage.month_work_days_before_today,
            "month_work_days_after_today": self.component_api.calc_monthly_wage.month_work_days_after_today,
            "flex_hours": self.component_api.calc_monthly_wage.flex_hours,
            "markdown": self.component_api.markdown,
        }

    # ------------------------------------------------------
    @property
    def unique_id(self) -> str:
        """Unique id.

        Returns:
            str: Unique  id

        """
        return self.entry.entry_id + "_wage_calculator"

    # ------------------------------------------------------
    @property
    def should_poll(self) -> bool:
        """No need to poll. Coordinator notifies entity of updates."""
        return False

    # ------------------------------------------------------
    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success

    # -------------------------------------------------------------------
    async def async_refresh(self) -> None:
        """Refresh."""

        await self.component_api.async_update()

        # self.async_write_ha_state()

    # ------------------------------------------------------
    async def async_update(self) -> None:
        """Update the entity. Only used by the generic entity update service."""
        await self.coordinator.request_refresh()

    # ------------------------------------------------------
    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )
