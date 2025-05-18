"""Wage calc."""

from calendar import monthrange, weekday
from datetime import UTC, date, datetime, time, timedelta

from holidays import HolidayBase, country_holidays

from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util

from .hass_util import async_hass_add_executor_job


# ------------------------------------------------------------------
# ------------------------------------------------------------------
class WageCalc:
    """Wage calc."""

    def __init__(
        self,
        hass: HomeAssistant,
        weekly_work_hours: list[float],
        weekly_work_starts_at: list[str],
        hourly_wage: float = 0.0,
        flex_hours: float = 0.0,
        country: str = "DK",
        update_continuously: bool = True,
    ) -> None:
        """Initialize WageCalc."""

        self.hass: HomeAssistant = hass

        self._work_hours_week: list[float] = weekly_work_hours

        self._flex_hours: float = flex_hours
        self._country: str = country
        self._update_continuously: bool = update_continuously
        self._work_starts_at_week: time = [
            datetime.strptime(t, "%H:%M:%S").time() for t in weekly_work_starts_at
        ]

        self._same_month_year: bool = False

        self.month_work_days: int = 0
        self.total_hours: float = 0.0
        self.month_work_days_before_today: int = 0
        self.total_hours_before_today: float = 0.0
        self.month_work_days_after_today: int = 0
        self.total_hours_after_today: float = 0.0

        self.year: int = 0
        self.month: int = 0
        self.day: int = 0
        self.hourly_wage: float = hourly_wage
        self.holidays: HolidayBase = None
        self.salary: float = 0.0
        self.salary_before_today: float = 0.0
        self.salery_before_today_with_hourly_update: float = 0.0
        self.salary_after_today: float = 0.0
        self.today_hours: float = 0.0

    # ------------------------------------------------------------------
    async def async_init(self) -> None:
        """Initialize the component."""

        await self.get_holidays(self._country)

        self.calculate()

    # ------------------------------------------------------------------
    @async_hass_add_executor_job()
    def get_holidays(self, country: str) -> None:
        """Get holidays."""

        self.holidays = country_holidays(country)

    # ------------------------------------------------------------------
    def calc_todays_work(self) -> float:
        """Calculate todays work."""

        tmp_todays_work_hours: timedelta = dt_util.as_local(
            datetime.now(UTC)
        ) - dt_util.as_local(
            datetime.combine(
                date.today(),
                self._work_starts_at_week[weekday(self.year, self.month, self.day)],
            )
        )

        tmp_today_hours: float = tmp_todays_work_hours.total_seconds() // 3600 + (
            int(((tmp_todays_work_hours.total_seconds() % 3600) // 60) * 1.6666666667)
            / 100
        )

        return max(
            0,
            min(
                tmp_today_hours,
                self._work_hours_week[weekday(self.year, self.month, self.day)],
            ),
        )

    # ------------------------------------------------------------------
    def calculate(self, year: int = 0, month: int = 0) -> None:
        """Calculate work hours."""

        self._same_month_year = False
        self.month_work_days = 0
        self.total_hours = 0.0
        self.month_work_days_before_today = 0
        self.total_hours_before_today = 0.0
        self.month_work_days_after_today = 0
        self.total_hours_after_today = 0.0

        if year == 0 or month == 0:
            self.year = date.today().year
            self.month = date.today().month
            self.day = date.today().day
        else:
            self.year = year
            self.month = month

        if self.year == date.today().year and self.month == date.today().month:
            self._same_month_year = True
            self.day = date.today().day

            if self._update_continuously:
                self.today_hours = self.calc_todays_work()

        for day in range(1, (monthrange(self.year, self.month))[1] + 1):
            if date(self.year, self.month, day) not in self.holidays:
                if (
                    day_work_hours := self._work_hours_week[
                        weekday(self.year, self.month, day)
                    ]
                ) != 0.0:
                    self.month_work_days += 1
                    self.total_hours += day_work_hours

                    if self._same_month_year:
                        if day < self.day:
                            self.month_work_days_before_today += 1
                            self.total_hours_before_today += day_work_hours
                        else:
                            self.month_work_days_after_today += 1
                            self.total_hours_after_today += day_work_hours

        self.total_hours += self._flex_hours
        self.salary = self.total_hours * self.hourly_wage
        self.salary_before_today = self.total_hours_before_today * self.hourly_wage
        self.salery_before_today_with_hourly_update = (
            self.total_hours_before_today + self.today_hours
        ) * self.hourly_wage
        self.salary_after_today = self.total_hours_after_today * self.hourly_wage

    # ------------------------------------------------------------------
    @property
    def flex_hours(self) -> float:
        """Get flex hours."""
        return self._flex_hours

    # ------------------------------------------------------------------
    @flex_hours.setter
    def flex_hours(self, hours: float) -> None:
        """Set flex hours."""
        self._flex_hours = hours
        self.calculate(self.year, self.month)

    # ------------------------------------------------------------------
    def __str__(self) -> str:
        """Representation of MonthlyWorkHours as as string."""
        return (
            f"Month work days before today: {self.month_work_days_before_today:>10}\n"
            f"Total hours before today:     {self.total_hours_before_today:>10,.2f}\n"
            f"Salary before today:         {self.salary_before_today:>10,.2f}\n"
            f"Month work days after today:  {self.month_work_days_after_today:>10}\n"
            f"Total hours after today:      {self.total_hours_after_today:>10,.2f}\n"
            f"Salary after today:          {self.salary_after_today:>10,.2f}\n"
            f"Month work days:              {self.month_work_days:>10}\n"
            f"Flex hours:                   {self.flex_hours:>10,.2f}\n"
            f"Total hours:                  {self.total_hours:>10,.2f}\n"
            f"Wage:                      {self.salary:>10,.2f}\n"
        )
