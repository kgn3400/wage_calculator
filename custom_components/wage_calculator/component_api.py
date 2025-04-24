"""Component api."""

from dataclasses import dataclass
from functools import partial

from babel.numbers import format_decimal

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_COUNTRY_CODE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    CONF_FLEX_HOURS,
    CONF_HOURLY_WAGE,
    CONF_WORK_HOURS_FRI,
    CONF_WORK_HOURS_MON,
    CONF_WORK_HOURS_SAT,
    CONF_WORK_HOURS_SUN,
    CONF_WORK_HOURS_THU,
    CONF_WORK_HOURS_TUE,
    CONF_WORK_HOURS_WED,
)
from .wage_calc import WageCalc


# ------------------------------------------------------------------
# ------------------------------------------------------------------
@dataclass
class ComponentApi:
    """Wage calculator component api."""

    def __init__(
        self,
        hass: HomeAssistant,
        coordinator: DataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Component api."""
        self.hass = hass
        self.coordinator: DataUpdateCoordinator = coordinator
        self.entry: ConfigEntry = entry

        self.calc_monthly_wage: WageCalc = WageCalc(
            hass,
            mon_hours=entry.options.get(CONF_WORK_HOURS_MON, 0.0),
            tue_hours=entry.options.get(CONF_WORK_HOURS_TUE, 0.0),
            wed_hours=entry.options.get(CONF_WORK_HOURS_WED, 0.0),
            thu_hours=entry.options.get(CONF_WORK_HOURS_THU, 0.0),
            fri_hours=entry.options.get(CONF_WORK_HOURS_FRI, 0.0),
            sat_hours=entry.options.get(CONF_WORK_HOURS_SAT, 0.0),
            sun_hours=entry.options.get(CONF_WORK_HOURS_SUN, 0.0),
            hourly_wage=entry.options.get(CONF_HOURLY_WAGE, 0.0),
            flex_hours=entry.options.get(CONF_FLEX_HOURS, 0.0),
            country=entry.options.get(CONF_COUNTRY_CODE, "DK"),
        )

        self.markdown: str = ""

    # -------------------------------------------------------------------
    async def async_init(self) -> None:
        """Init."""

        await self.calc_monthly_wage.async_init()
        self.markdown = await self.async_create_markdown()

        # await self.coordinator.async_config_entry_first_refresh()

    # -------------------------------------------------------------------
    async def async_update(self) -> None:
        """Update."""

        self.calc_monthly_wage.calculate()

        self.markdown = await self.async_create_markdown()

    # ------------------------------------------------------------------
    async def async_format_decimal(self, number: float) -> str:
        """Format decimal."""

        number_str: str = await self.hass.async_add_executor_job(
            partial(
                format_decimal,
                number=number,
                format="#,###,##0.00",
                locale=self.hass.config.language,
            )
        )
        return number_str

    # -------------------------------------------------------------------
    async def async_create_markdown(self) -> None:
        """Create markdown."""

        return (
            f"### Månedsløn\n"
            f"**{self.calc_monthly_wage.month_work_days_before_today}** dage af arbejdsmåneden er gået og der er tjent:\n"
            f"&nbsp;&nbsp;&nbsp;&nbsp;**{await self.async_format_decimal(self.calc_monthly_wage.salary_before_today)}** Kr.\n\n"
            f"Efter de næste **{self.calc_monthly_wage.month_work_days_after_today}** arbejdsdage er der tjent ialt:\n"
            f"&nbsp;&nbsp;&nbsp;&nbsp;**{await self.async_format_decimal(self.calc_monthly_wage.salary)}** Kr."
        )
