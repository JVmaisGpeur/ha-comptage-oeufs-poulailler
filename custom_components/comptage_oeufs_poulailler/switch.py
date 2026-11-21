"""Interrupteur : comptage automatique (pause / reprise)."""

from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .entity import PoulaillerEntity


async def async_setup_entry(
    hass: HomeAssistant, entry, async_add_entities: AddConfigEntryEntitiesCallback
) -> None:
    async_add_entities([AutoSwitch(entry.runtime_data)])


class AutoSwitch(PoulaillerEntity, SwitchEntity):
    platform_domain = "switch"
    _attr_icon = "mdi:timer-play-outline"

    def __init__(self, manager) -> None:
        super().__init__(manager, "comptage_automatique")

    @property
    def is_on(self) -> bool:
        return bool(self.manager.data["auto"])

    async def async_turn_on(self, **kwargs: Any) -> None:
        self.manager.async_set_setting("auto", True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        self.manager.async_set_setting("auto", False)
