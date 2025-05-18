"""Component api."""

from dataclasses import dataclass

from babel.numbers import format_decimal, get_currency_symbol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_COUNTRY_CODE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.template import Template
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    CONF_FLEX_HOURS,
    CONF_HOURLY_WAGE,
    CONF_UPDATE_CONTINUOUSLY,
    CONF_WORK_HOURS,
    CONF_WORK_STARTS,
    DayOfWeekEnum,
)
from .hass_util import Translate, async_hass_add_executor_job
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
                entry.options.get(CONF_WORK_HOURS + str(i), 0.0)
                for i in DayOfWeekEnum.range()
            ],
            [
                entry.options.get(CONF_WORK_STARTS + str(i), "00:00:00")
                for i in DayOfWeekEnum.range()
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

        self._md_today_hours_template: str = await Translate(
            self.hass
        ).async_get_localized_str(
            "defaults.default_md_today_hours_monthly_template",
            file_name="_defaults.json",
        )

        self._default_md_txt_template: str = await Translate(
            self.hass
        ).async_get_localized_str(
            "defaults.default_md_txt_monthly_template",
            file_name="_defaults.json",
        )

        self.currency_sign: str = await self.get_currency_symb()
        await self.calc_monthly_wage.async_init()
        self.markdown = await self.async_create_markdown()

    # -------------------------------------------------------------------
    @async_hass_add_executor_job()
    def get_currency_symb(self) -> str:
        """Get currency symbol."""

        return get_currency_symbol(
            self.hass.config.currency, locale=self.hass.config.language
        )

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
            value_template: Template | None = Template(
                self._md_today_hours_template, self.hass
            )
            tmp_hours = (
                value_template.async_render(
                    {
                        "today_hours": await self.format_decimal(
                            self.calc_monthly_wage.today_hours, "#,###,##0.0"
                        )
                    }
                )
                + " "
            )

        values: dict = {
            "currency": self.hass.config.currency,
            "currency_sign": self.currency_sign,
            "tmp_hours": tmp_hours,
            "today_hours": await self.format_decimal(
                self.calc_monthly_wage.today_hours, "#,###,##0.0"
            ),
            "month_work_days_before_today": self.calc_monthly_wage.month_work_days_before_today,
            "salery_before_today_with_hourly_update": await self.format_decimal(
                self.calc_monthly_wage.salery_before_today_with_hourly_update
            ),
            "month_work_days_after_today": self.calc_monthly_wage.month_work_days_after_today,
            "salary": await self.format_decimal(self.calc_monthly_wage.salary),
        }

        value_template: Template | None = Template(
            self._default_md_txt_template, self.hass
        )

        return value_template.async_render(values)
