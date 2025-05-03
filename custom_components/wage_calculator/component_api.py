"""Component api."""

from dataclasses import dataclass

from babel.numbers import format_decimal

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_COUNTRY_CODE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    CONF_FLEX_HOURS,
    CONF_HOURLY_WAGE,
    CONF_UPDATE_CONTINUOUSLY,
    CONF_WORK_HOURS_FRI,
    CONF_WORK_HOURS_MON,
    CONF_WORK_HOURS_SAT,
    CONF_WORK_HOURS_SUN,
    CONF_WORK_HOURS_THU,
    CONF_WORK_HOURS_TUE,
    CONF_WORK_HOURS_WED,
    CONF_WORK_STARTS_FRI,
    CONF_WORK_STARTS_MON,
    CONF_WORK_STARTS_SAT,
    CONF_WORK_STARTS_SUN,
    CONF_WORK_STARTS_THU,
    CONF_WORK_STARTS_TUE,
    CONF_WORK_STARTS_WED,
)
from .hass_util import async_hass_add_executor_job
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
            [
                entry.options.get(CONF_WORK_HOURS_MON, 0.0),
                entry.options.get(CONF_WORK_HOURS_TUE, 0.0),
                entry.options.get(CONF_WORK_HOURS_WED, 0.0),
                entry.options.get(CONF_WORK_HOURS_THU, 0.0),
                entry.options.get(CONF_WORK_HOURS_FRI, 0.0),
                entry.options.get(CONF_WORK_HOURS_SAT, 0.0),
                entry.options.get(CONF_WORK_HOURS_SUN, 0.0),
            ],
            [
                entry.options.get(CONF_WORK_STARTS_MON, "00:00:00"),
                entry.options.get(CONF_WORK_STARTS_TUE, "00:00:00"),
                entry.options.get(CONF_WORK_STARTS_WED, "00:00:00"),
                entry.options.get(CONF_WORK_STARTS_THU, "00:00:00"),
                entry.options.get(CONF_WORK_STARTS_FRI, "00:00:00"),
                entry.options.get(CONF_WORK_STARTS_SAT, "00:00:00"),
                entry.options.get(CONF_WORK_STARTS_SUN, "00:00:00"),
            ],
            hourly_wage=entry.options.get(CONF_HOURLY_WAGE, 0.0),
            flex_hours=entry.options.get(CONF_FLEX_HOURS, 0.0),
            country=entry.options.get(CONF_COUNTRY_CODE, "DK"),
            update_continuously=entry.options.get(CONF_UPDATE_CONTINUOUSLY, False),
        )

        self.markdown: str = ""

    # -------------------------------------------------------------------
    async def async_init(self) -> None:
        """Init."""

        await self.calc_monthly_wage.async_init()
        self.markdown = await self.async_create_markdown()

    # -------------------------------------------------------------------
    async def async_update(self) -> None:
        """Update."""

        self.calc_monthly_wage.calculate()

        self.markdown = await self.async_create_markdown()

    @async_hass_add_executor_job()
    # ------------------------------------------------------------------
    def format_decimal(self, number: float, format: str = "#,###,##0.00") -> str:
        """Format decimal."""

        return format_decimal(number, format=format, locale=self.hass.config.language)

    # -------------------------------------------------------------------
    async def async_create_markdown(self) -> None:
        """Create markdown."""

        tmp_hours: str = ""

        if self.calc_monthly_wage.today_hours > 0:
            tmp_hours = f"og **{await self.format_decimal(self.calc_monthly_wage.today_hours, '#,###,##0.0')}** timer i dag "

        return (
            f"### Månedsløn\n"
            f"**{self.calc_monthly_wage.month_work_days_before_today}** dage {tmp_hours}af arbejdsmåneden er gået og der er tjent:\n"
            f"&nbsp;&nbsp;&nbsp;&nbsp;**{await self.format_decimal(self.calc_monthly_wage.salery_before_today_with_hourly_update)}** Kr.\n\n"
            f"Efter de næste **{self.calc_monthly_wage.month_work_days_after_today}** arbejdsdage er der tjent ialt:\n"
            f"&nbsp;&nbsp;&nbsp;&nbsp;**{await self.format_decimal(self.calc_monthly_wage.salary)}** Kr."
        )
