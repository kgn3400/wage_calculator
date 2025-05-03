"""Config flow for Calendar merge helper."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, cast

import voluptuous as vol

from homeassistant.const import CONF_COUNTRY_CODE, CONF_NAME
from homeassistant.core import callback
from homeassistant.helpers import selector
from homeassistant.helpers.schema_config_entry_flow import (
    SchemaCommonFlowHandler,
    SchemaConfigFlowHandler,
    SchemaFlowFormStep,
    SchemaFlowMenuStep,
)
from homeassistant.helpers.selector import (
    BooleanSelector,
    CountrySelector,
    NumberSelector,
    NumberSelectorMode,
    TimeSelector,
)
from homeassistant.util.uuid import random_uuid_hex

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
    DOMAIN,
)
from .hass_util import NumberSelectorConfigTranslate


async def _validate_input(
    handler: SchemaCommonFlowHandler, user_input: dict[str, Any]
) -> dict[str, Any]:
    """Validate user input."""
    # if len(user_input[CONF_CALENDAR_ENTITY_IDS]) == 0:
    #     raise SchemaFlowError("missing_selection")

    return user_input


CONFIG_NAME = {
    vol.Required(
        CONF_NAME,
    ): selector.TextSelector(),
}


# ------------------------------------------------------------------
async def config_options_dict(handler: SchemaCommonFlowHandler) -> dict:
    """Return dict for the sensor options step."""

    return {
        vol.Required(
            CONF_COUNTRY_CODE,
            default=handler.parent_handler.hass.config.country,
        ): CountrySelector(),
        vol.Required(
            CONF_HOURLY_WAGE,
            default=0,
        ): NumberSelector(
            await NumberSelectorConfigTranslate(
                handler.parent_handler.hass,
                min=0,
                max=99999,
                step=1.0,
                mode=NumberSelectorMode.BOX,
                unit_of_measurement=handler.parent_handler.hass.config.currency,
            )()
        ),
        vol.Required(
            CONF_FLEX_HOURS,
            default=0,
        ): NumberSelector(
            await NumberSelectorConfigTranslate(
                handler.parent_handler.hass,
                min=-999,
                max=999,
                step=1.0,
                mode=NumberSelectorMode.BOX,
                unit_of_measurement="hours",
            )()
        ),
        vol.Required(
            CONF_UPDATE_CONTINUOUSLY,
            default=True,
        ): BooleanSelector(),
    }


# ------------------------------------------------------------------
async def config_options_work_days_dict(handler: SchemaCommonFlowHandler) -> dict:
    """Return dict for the work days options step."""

    return {
        vol.Required(
            CONF_WORK_HOURS_MON,
            default=7.5,
        ): NumberSelector(
            await NumberSelectorConfigTranslate(
                handler.parent_handler.hass,
                min=0,
                max=24,
                step=1.0,
                mode=NumberSelectorMode.BOX,
                unit_of_measurement="hours",
            )()
        ),
        vol.Required(
            CONF_WORK_HOURS_TUE,
            default=7.5,
        ): NumberSelector(
            await NumberSelectorConfigTranslate(
                handler.parent_handler.hass,
                min=0,
                max=24,
                step=0.5,
                mode=NumberSelectorMode.BOX,
                unit_of_measurement="hours",
            )(),
        ),
        vol.Required(
            CONF_WORK_HOURS_WED,
            default=7.5,
        ): NumberSelector(
            await NumberSelectorConfigTranslate(
                handler.parent_handler.hass,
                min=0,
                max=24,
                step=0.5,
                mode=NumberSelectorMode.BOX,
                unit_of_measurement="hours",
            )()
        ),
        vol.Required(
            CONF_WORK_HOURS_THU,
            default=7.5,
        ): NumberSelector(
            await NumberSelectorConfigTranslate(
                handler.parent_handler.hass,
                min=0,
                max=24,
                step=0.5,
                mode=NumberSelectorMode.BOX,
                unit_of_measurement="hours",
            )()
        ),
        vol.Required(
            CONF_WORK_HOURS_FRI,
            default=7.5,
        ): NumberSelector(
            await NumberSelectorConfigTranslate(
                handler.parent_handler.hass,
                min=0,
                max=24,
                step=0.5,
                mode=NumberSelectorMode.BOX,
                unit_of_measurement="hours",
            )()
        ),
        vol.Required(
            CONF_WORK_HOURS_SAT,
            default=0.0,
        ): NumberSelector(
            await NumberSelectorConfigTranslate(
                handler.parent_handler.hass,
                min=0,
                max=24,
                step=0.5,
                mode=NumberSelectorMode.BOX,
                unit_of_measurement="hours",
            )()
        ),
        vol.Required(
            CONF_WORK_HOURS_SUN,
            default=0.0,
        ): NumberSelector(
            await NumberSelectorConfigTranslate(
                handler.parent_handler.hass,
                min=0,
                max=24,
                step=0.5,
                mode=NumberSelectorMode.BOX,
                unit_of_measurement="hours",
            )()
        ),
    }


# ------------------------------------------------------------------
async def config_options_work_starts_dict(handler: SchemaCommonFlowHandler) -> dict:
    """Return dict for the work starts step."""

    return {
        vol.Required(
            CONF_WORK_STARTS_MON,
            default="08:00:00",
        ): TimeSelector(),
        vol.Required(
            CONF_WORK_STARTS_TUE,
            default="08:00:00",
        ): TimeSelector(),
        vol.Required(
            CONF_WORK_STARTS_WED,
            default="08:00:00",
        ): TimeSelector(),
        vol.Required(
            CONF_WORK_STARTS_THU,
            default="08:00:00",
        ): TimeSelector(),
        vol.Required(
            CONF_WORK_STARTS_FRI,
            default="08:00:00",
        ): TimeSelector(),
        vol.Required(
            CONF_WORK_STARTS_SAT,
            default="00:00:00",
        ): TimeSelector(),
        vol.Required(
            CONF_WORK_STARTS_SUN,
            default="00:00:00",
        ): TimeSelector(),
    }


# ------------------------------------------------------------------
async def config_options_schema(handler: SchemaCommonFlowHandler) -> vol.Schema:
    """Return schema for the sensor options step."""

    return vol.Schema(await config_options_dict(handler))


# ------------------------------------------------------------------
async def config_options_work_days_schema(
    handler: SchemaCommonFlowHandler,
) -> vol.Schema:
    """Return schema for the work days options step."""

    return vol.Schema(await config_options_work_days_dict(handler))


# ------------------------------------------------------------------
async def config_options_work_starts_schema(
    handler: SchemaCommonFlowHandler,
) -> vol.Schema:
    """Return schema for the work starts options step."""

    return vol.Schema(await config_options_work_starts_dict(handler))


# ------------------------------------------------------------------
async def config_schema(handler: SchemaCommonFlowHandler) -> vol.Schema:
    """Return schema for the sensor options step."""

    if handler.parent_handler.unique_id is None:
        await handler.parent_handler.async_set_unique_id(random_uuid_hex())
        handler.parent_handler._abort_if_unique_id_configured()  # noqa: SLF001
        # tmp_dict = await config_options_dict(handler)
    return vol.Schema({**CONFIG_NAME, **(await config_options_dict(handler))})


# ------------------------------------------------------------------
async def next_weekly_work_starts_at_config_step(options: dict[str, Any]) -> str | None:
    """Return next step_id for config flow."""

    if options[CONF_UPDATE_CONTINUOUSLY]:
        return "user_work_starts"

    return None


# ------------------------------------------------------------------
async def next_weekly_work_starts_at_options_step(
    options: dict[str, Any],
) -> str | None:
    """Return next step_id for options flow."""

    if options[CONF_UPDATE_CONTINUOUSLY]:
        return "init_work_starts"

    return None


# ------------------------------------------------------------------

CONFIG_FLOW: dict[str, SchemaFlowFormStep | SchemaFlowMenuStep] = {
    "user": SchemaFlowFormStep(
        config_schema,
        validate_user_input=_validate_input,
        next_step="user_work_days",
    ),
    "user_work_days": SchemaFlowFormStep(
        config_options_work_days_schema,
        validate_user_input=_validate_input,
        next_step=next_weekly_work_starts_at_config_step,
    ),
    "user_work_starts": SchemaFlowFormStep(
        config_options_work_starts_schema,
        validate_user_input=_validate_input,
    ),
}

OPTIONS_FLOW: dict[str, SchemaFlowFormStep | SchemaFlowMenuStep] = {
    "init": SchemaFlowFormStep(
        config_options_schema,
        validate_user_input=_validate_input,
        next_step="init_work_days",
    ),
    "init_work_days": SchemaFlowFormStep(
        config_options_work_days_schema,
        validate_user_input=_validate_input,
        next_step=next_weekly_work_starts_at_options_step,
    ),
    "init_work_starts": SchemaFlowFormStep(
        config_options_work_starts_schema,
        validate_user_input=_validate_input,
    ),
}


# ------------------------------------------------------------------
# ------------------------------------------------------------------
class ConfigFlowHandler(SchemaConfigFlowHandler, domain=DOMAIN):
    """Handle a config or options flow."""

    config_flow = CONFIG_FLOW
    options_flow = OPTIONS_FLOW

    # ------------------------------------------------------------------
    def async_config_entry_title(self, options: Mapping[str, Any]) -> str:
        """Return config entry title."""

        return cast(str, options[CONF_NAME])

    # ------------------------------------------------------------------
    @callback
    def async_config_flow_finished(self, options: Mapping[str, Any]) -> None:
        """Take necessary actions after the config flow is finished, if needed.

        The options parameter contains config entry options, which is the union of user
        input from the config flow steps.
        """
