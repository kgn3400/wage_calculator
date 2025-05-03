"""Constants for the Wage calculator integration."""

from logging import Logger, getLogger

DOMAIN = "wage_calculator"
DOMAIN_NAME = "Wage calculator"

LOGGER: Logger = getLogger(__name__)

TRANSLATION_KEY = DOMAIN


CONF_HOURLY_WAGE = "hourly_wage"
CONF_FLEX_HOURS = "flex_hours"
CONF_UPDATE_CONTINUOUSLY = "update_continuously"
CONF_WORK_HOURS_MON = "work_hours_mon"
CONF_WORK_HOURS_TUE = "work_hours_tue"
CONF_WORK_HOURS_WED = "work_hours_wed"
CONF_WORK_HOURS_THU = "work_hours_thu"
CONF_WORK_HOURS_FRI = "work_hours_fri"
CONF_WORK_HOURS_SAT = "work_hours_sat"
CONF_WORK_HOURS_SUN = "work_hours_sun"

CONF_WORK_STARTS_MON = "work_starts_mon"
CONF_WORK_STARTS_TUE = "work_starts_tue"
CONF_WORK_STARTS_WED = "work_starts_wed"
CONF_WORK_STARTS_THU = "work_starts_thu"
CONF_WORK_STARTS_FRI = "work_starts_fri"
CONF_WORK_STARTS_SAT = "work_starts_sat"
CONF_WORK_STARTS_SUN = "work_starts_sun"


SERVICE_ADD_ENTITY_ID = "add_entity_id"
