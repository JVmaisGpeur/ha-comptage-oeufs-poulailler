"""Boutons : compter maintenant, œufs ramassés."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import DOMAIN
from .entity import PoulaillerEntity


async def async_setup_entry(
    hass: HomeAssistant, entry, async_add_entities: AddConfigEntryEntitiesCallback
) -> None:
    manager = entry.runtime_data
    async_add_entities([CountNowButton(manager), CollectedButton(manager)])


class CountNowButton(PoulaillerEntity, ButtonEntity):
    platform_domain = "button"
    _attr_icon = "mdi:camera-iris"

    def __init__(self, manager) -> None:
        super().__init__(manager, "compter_maintenant")

    async def async_press(self) -> None:
        self.manager.entry.async_create_background_task(
            self.hass, self.manager.async_count("manual"), f"{DOMAIN}_comptage_manuel"
        )


class CollectedButton(PoulaillerEntity, ButtonEntity):
    platform_domain = "button"
    _attr_icon = "mdi:basket-check"

    def __init__(self, manager) -> None:
        super().__init__(manager, "oeufs_ramasses")

    async def async_press(self) -> None:
        self.manager.async_collected(0)
