"""Config flow (UI setup) and options flow."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, ConfigFlow, ConfigFlowResult, OptionsFlow
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import (
    CONF_AI_TASK,
    CONF_CAMERA,
    CONF_IMPORT_ENTITY,
    CONF_NAME,
    CONF_NESTS,
    CONF_NOTIFY_ENTITY,
    CONF_NOTIFY_SERVICE,
    CONF_PROMPT,
    CONF_SENSITIVITY,
    CONF_SNAPSHOT_DAYS,
    DEFAULT_NESTS,
    DEFAULT_SENSITIVITY,
    DEFAULT_SNAPSHOT_DAYS,
    DOMAIN,
)
from .i18n import text

CAMERA = selector.EntitySelector(selector.EntitySelectorConfig(domain="camera"))
AI_TASK = selector.EntitySelector(selector.EntitySelectorConfig(domain="ai_task"))
NOTIFY = selector.EntitySelector(selector.EntitySelectorConfig(domain="notify"))
INPUT_TEXT = selector.EntitySelector(selector.EntitySelectorConfig(domain="input_text"))
NESTS = selector.NumberSelector(
    selector.NumberSelectorConfig(min=1, max=20, step=1, mode=selector.NumberSelectorMode.BOX)
)
SENSITIVITY = selector.NumberSelector(
    selector.NumberSelectorConfig(
        min=0, max=20, step=0.1, unit_of_measurement="%", mode=selector.NumberSelectorMode.BOX
    )
)
DAYS = selector.NumberSelector(
    selector.NumberSelectorConfig(
        min=1, max=365, step=1, unit_of_measurement="j", mode=selector.NumberSelectorMode.BOX
    )
)
PROMPT = selector.TextSelector(selector.TextSelectorConfig(multiline=True))


def _optional(key: str, defaults: dict[str, Any]) -> vol.Optional:
    """Champ optionnel pré-rempli seulement s'il a une valeur (sinon il peut rester vide)."""
    if defaults.get(key):
        return vol.Optional(key, description={"suggested_value": defaults[key]})
    return vol.Optional(key)


class PoulaillerConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            await self.async_set_unique_id(user_input[CONF_CAMERA])
            self._abort_if_unique_id_configured()
            user_input[CONF_NESTS] = int(user_input.get(CONF_NESTS, DEFAULT_NESTS))
            default_name = text(self.hass.config.language, "default_name")
            title = user_input.pop(CONF_NAME, default_name) or default_name
            return self.async_create_entry(title=title, data=user_input)

        # Pre-fill the import for users of the original YAML dashboard (if present)
        legacy = "input_text.poulailler_historique_oeufs"
        defaults = {CONF_IMPORT_ENTITY: legacy if self.hass.states.get(legacy) else None}
        schema = vol.Schema(
            {
                vol.Required(
                    CONF_NAME, default=text(self.hass.config.language, "default_name")
                ): str,
                vol.Required(CONF_CAMERA): CAMERA,
                vol.Optional(CONF_AI_TASK): AI_TASK,
                vol.Required(CONF_NESTS, default=DEFAULT_NESTS): NESTS,
                vol.Optional(CONF_NOTIFY_ENTITY): NOTIFY,
                _optional(CONF_IMPORT_ENTITY, defaults): INPUT_TEXT,
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        return PoulaillerOptionsFlow()


class PoulaillerOptionsFlow(OptionsFlow):
    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        current = {**self.config_entry.data, **self.config_entry.options}
        default_prompt = text(self.hass.config.language, "prompt")
        if user_input is not None:
            user_input[CONF_NESTS] = int(user_input[CONF_NESTS])
            user_input[CONF_SNAPSHOT_DAYS] = int(user_input[CONF_SNAPSHOT_DAYS])
            # Un champ vidé doit vraiment effacer l'ancienne valeur de entry.data
            for key in (CONF_AI_TASK, CONF_NOTIFY_ENTITY, CONF_NOTIFY_SERVICE, CONF_PROMPT):
                user_input.setdefault(key, None)
            # The default prompt is not stored: it then follows the HA language
            if (user_input.get(CONF_PROMPT) or "").strip() == default_prompt.strip():
                user_input[CONF_PROMPT] = None
            return self.async_create_entry(data=user_input)

        schema = vol.Schema(
            {
                vol.Required(CONF_CAMERA, default=current.get(CONF_CAMERA)): CAMERA,
                _optional(CONF_AI_TASK, current): AI_TASK,
                vol.Required(CONF_NESTS, default=current.get(CONF_NESTS, DEFAULT_NESTS)): NESTS,
                _optional(CONF_NOTIFY_ENTITY, current): NOTIFY,
                _optional(CONF_NOTIFY_SERVICE, current): str,
                vol.Optional(
                    CONF_PROMPT,
                    description={"suggested_value": current.get(CONF_PROMPT) or default_prompt},
                ): PROMPT,
                vol.Required(
                    CONF_SENSITIVITY, default=current.get(CONF_SENSITIVITY, DEFAULT_SENSITIVITY)
                ): SENSITIVITY,
                vol.Required(
                    CONF_SNAPSHOT_DAYS, default=current.get(CONF_SNAPSHOT_DAYS, DEFAULT_SNAPSHOT_DAYS)
                ): DAYS,
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)
