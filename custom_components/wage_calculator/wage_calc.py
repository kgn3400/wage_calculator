"""Wage calc."""

from calendar import monthrange, weekday
from datetime import date

from holidays import HolidayBase, country_holidays

from homeassistant.core import HomeAssistant


# ------------------------------------------------------------------
# ------------------------------------------------------------------
class WageCalc:
    """Wage calc."""

    def __init__(
        self,
        hass: HomeAssistant,
        weekly_work_hours: list[float] | None = None,
        mon_hours: float = 0.0,
        tue_hours: float = 0.0,
        wed_hours: float = 0.0,
        thu_hours: float = 0.0,
        fri_hours: float = 0.0,
        sat_hours: float = 0.0,
        sun_hours: float = 0.0,
        hourly_wage: float = 0.0,
        flex_hours: float = 0.0,
        country: str = "DK",
    ) -> None:
        """Initialize WageCalc."""

        self.hass: HomeAssistant = hass
        self.country: str = country

        if weekly_work_hours is not None:
            self.weekly_work_hours: list[float] = weekly_work_hours
        else:
            self.weekly_work_hours = [
                mon_hours,
                tue_hours,
                wed_hours,
                thu_hours,
                fri_hours,
                sat_hours,
                sun_hours,
            ]
        self._flex_hours: float = flex_hours
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
        self.salary_after_today: float = 0.0

    # ------------------------------------------------------------------
    async def async_init(self) -> None:
        """Initialize the component."""
        self.holidays = await self.hass.async_add_executor_job(
            country_holidays, self.country
        )
        self.calculate()

    # ------------------------------------------------------------------
    def calculate(self, year: int = 0, month: int = 0) -> None:
        """Calculate work hours."""

        self._same_month_year = False

        if year == 0 or month == 0:
            self.year = date.today().year
            self.month = date.today().month
            self.day = date.today().day
            self._same_month_year = True
        else:
            self.year = year
            self.month = month

            if self.year == date.today().year and self.month == date.today().month:
                self._same_month_year = True
                self.day = date.today().day

        self.month_work_days = 0
        self.total_hours = 0.0
        self.month_work_days_before_today = 0
        self.total_hours_before_today = 0.0
        self.month_work_days_after_today = 0
        self.total_hours_after_today = 0.0
        self.salary = 0.0
        self.salary_before_today = 0.0
        self.salary_after_today = 0.0

        cal = monthrange(self.year, self.month)

        for day in range(1, cal[1] + 1):
            if date(self.year, self.month, day) not in self.holidays:
                if (
                    day_work_hours := self.weekly_work_hours[
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
