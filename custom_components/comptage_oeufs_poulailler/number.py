"""Nombres : intervalle entre deux comptages, délai de confirmation."""

from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.const import EntityCategory, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .entity import PoulaillerEntity


async def async_setup_entry(
    hass: HomeAssistant, entry, async_add_entities: AddConfigEntryEntitiesCallback
) -> None:
    manager = entry.runtime_data
    async_add_entities(
        [
            SettingNumber(manager, "intervalle_de_comptage", "interval", 5, 120, 5, "mdi:timer-refresh-outline"),
            SettingNumber(manager, "delai_de_confirmation", "delay", 1, 15, 1, "mdi:timer-sand"),
        ]
    )


class SettingNumber(PoulaillerEntity, NumberEntity):
    platform_domain = "number"
    _attr_entity_category = EntityCategory.CONFIG
    _attr_mode = NumberMode.BOX
    _attr_native_unit_of_measurement = UnitOfTime.MINUTES

    def __init__(self, manager, key, setting, minimum, maximum, step, icon) -> None:
        super().__init__(manager, key)
        self._setting = setting
        self._attr_native_min_value = minimum
        self._attr_native_max_value = maximum
        self._attr_native_step = step
        self._attr_icon = icon

    @property
    def native_value(self) -> float:
        return float(self.manager.data[self._setting])

    async def async_set_native_value(self, value: float) -> None:
        self.manager.async_set_setting(self._setting, int(value))
