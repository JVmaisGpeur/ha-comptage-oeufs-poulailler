"""Comptage Œufs Poulailler (Chicken Coop Egg Counter): counts laid eggs with a camera and Home Assistant AI."""

from __future__ import annotations

from pathlib import Path

import voluptuous as vol

from homeassistant.components.frontend import add_extra_js_url
from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall, SupportsResponse
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import ConfigType

from . import websocket
from .const import (
    ATTR_COUNT,
    ATTR_DATE,
    ATTR_ENTITY_ID,
    ATTR_ENTRY_ID,
    ATTR_REMAINING,
    CARD_FILENAME,
    CARD_URL,
    CONF_IMPORT_ENTITY,
    DOMAIN,
    SERVICE_COLLECTED,
    SERVICE_CORRECT,
    SERVICE_COUNT_NOW,
    SERVICE_IMPORT,
    VERSION,
)
from .manager import PoulaillerManager

PLATFORMS = [
    Platform.BUTTON,
    Platform.IMAGE,
    Platform.NUMBER,
    Platform.SENSOR,
    Platform.SWITCH,
    Platform.TIME,
]

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

type PoulaillerConfigEntry = ConfigEntry[PoulaillerManager]

_ENTRY = {vol.Optional(ATTR_ENTRY_ID): cv.string}


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Enregistre la carte Lovelace, l'API websocket et les services (une seule fois)."""
    hass.data.setdefault(DOMAIN, {})

    card = Path(__file__).parent / "frontend" / CARD_FILENAME
    await hass.http.async_register_static_paths(
        [StaticPathConfig(CARD_URL, str(card), False)]
    )
    add_extra_js_url(hass, f"{CARD_URL}?v={VERSION}")
    websocket.async_register(hass)

    def managers(call: ServiceCall) -> list[PoulaillerManager]:
        all_managers: dict[str, PoulaillerManager] = hass.data[DOMAIN]
        if entry_id := call.data.get(ATTR_ENTRY_ID):
            if entry_id not in all_managers:
                raise ServiceValidationError(
                    translation_domain=DOMAIN,
                    translation_key="entry_not_found",
                    translation_placeholders={"entry_id": entry_id},
                )
            return [all_managers[entry_id]]
        if not all_managers:
            raise ServiceValidationError(
                translation_domain=DOMAIN, translation_key="no_entry"
            )
        return list(all_managers.values())

    async def count_now(call: ServiceCall) -> None:
        for manager in managers(call):
            manager.entry.async_create_background_task(
                hass, manager.async_count("manual"), f"{DOMAIN}_comptage_manuel"
            )

    async def correct(call: ServiceCall) -> None:
        for manager in managers(call):
            await manager.async_correct(call.data[ATTR_DATE], call.data[ATTR_COUNT])

    async def collected(call: ServiceCall) -> None:
        for manager in managers(call):
            manager.async_collected(call.data[ATTR_REMAINING])

    async def import_history(call: ServiceCall) -> dict:
        result = {}
        for manager in managers(call):
            result[manager.entry.entry_id] = await manager.async_import(call.data[ATTR_ENTITY_ID])
        return {"imported_days": result}

    hass.services.async_register(DOMAIN, SERVICE_COUNT_NOW, count_now, vol.Schema(_ENTRY))
    hass.services.async_register(
        DOMAIN,
        SERVICE_CORRECT,
        correct,
        vol.Schema(
            {
                **_ENTRY,
                vol.Required(ATTR_DATE): cv.date,
                vol.Required(ATTR_COUNT): vol.All(vol.Coerce(int), vol.Range(min=0, max=999)),
            }
        ),
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_COLLECTED,
        collected,
        vol.Schema(
            {
                **_ENTRY,
                vol.Optional(ATTR_REMAINING, default=0): vol.All(
                    vol.Coerce(int), vol.Range(min=0, max=999)
                ),
            }
        ),
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_IMPORT,
        import_history,
        vol.Schema({**_ENTRY, vol.Required(ATTR_ENTITY_ID): cv.entity_id}),
        supports_response=SupportsResponse.OPTIONAL,
    )
    return True


async def async_setup_entry(hass: HomeAssistant, entry: PoulaillerConfigEntry) -> bool:
    manager = PoulaillerManager(hass, entry)
    await manager.async_setup()
    entry.runtime_data = manager
    hass.data[DOMAIN][entry.entry_id] = manager

    import_entity = entry.data.get(CONF_IMPORT_ENTITY)
    if import_entity and not manager.data.get("imported"):
        try:
            await manager.async_import(import_entity)
        except ServiceValidationError:
            manager.data["imported"] = True  # entité disparue : on n'insiste pas

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_reload))
    manager.async_start()
    return True


async def _async_reload(hass: HomeAssistant, entry: PoulaillerConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: PoulaillerConfigEntry) -> bool:
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        await entry.runtime_data.async_stop()
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unloaded


async def async_remove_entry(hass: HomeAssistant, entry: PoulaillerConfigEntry) -> None:
    """Suppression définitive : on efface aussi les photos et l'historique stocké."""
    manager = PoulaillerManager(hass, entry)
    await hass.async_add_executor_job(manager._prepare_media)  # noqa: SLF001
    await manager.async_remove_files()
