"""Heures de début et de fin du comptage."""

from __future__ import annotations

from datetime import time

from homeassistant.components.time import TimeEntity
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .entity import PoulaillerEntity


async def async_setup_entry(
    hass: HomeAssistant, entry, async_add_entities: AddConfigEntryEntitiesCallback
) -> None:
    manager = entry.runtime_data
    async_add_entities(
        [
            SettingTime(manager, "heure_de_debut", "start", "mdi:clock-start"),
            SettingTime(manager, "heure_de_fin", "end", "mdi:clock-end"),
        ]
    )


class SettingTime(PoulaillerEntity, TimeEntity):
    platform_domain = "time"
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, manager, key, setting, icon) -> None:
        super().__init__(manager, key)
        self._setting = setting
        self._attr_icon = icon

    @property
    def native_value(self) -> time:
        return time.fromisoformat(self.manager.data[self._setting])

    async def async_set_value(self, value: time) -> None:
        self.manager.async_set_setting(self._setting, value)
