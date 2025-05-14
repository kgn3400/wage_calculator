"""Constants for the Wage calculator integration."""

from logging import Logger, getLogger

DOMAIN = "wage_calculator"
DOMAIN_NAME = "Wage calculator"

LOGGER: Logger = getLogger(__name__)

TRANSLATION_KEY = DOMAIN

CONF_HOURLY_WAGE = "hourly_wage"
CONF_FLEX_HOURS = "flex_hours"
CONF_UPDATE_CONTINUOUSLY = "update_continuously"
CONF_WORK_HOURS = "work_hours_"
CONF_WORK_STARTS = "work_starts_"
