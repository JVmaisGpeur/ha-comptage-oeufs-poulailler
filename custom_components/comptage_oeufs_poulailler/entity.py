"""Entité de base partagée par toutes les plateformes."""

from __future__ import annotations

from homeassistant.core import callback
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import Entity
from homeassistant.util import slugify

from .const import DOMAIN, VERSION
from .manager import PoulaillerManager


class PoulaillerEntity(Entity):
    """Entité rattachée à l'appareil du poulailler, mise à jour par signal."""

    _attr_has_entity_name = True
    _attr_should_poll = False
    platform_domain: str = ""

    def __init__(self, manager: PoulaillerManager, key: str) -> None:
        self.manager = manager
        entry = manager.entry
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_translation_key = key
        # Identifiant stable et lisible, quelle que soit la langue de HA
        self.entity_id = f"{self.platform_domain}.{slugify(entry.title)}_{key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.title,
            manufacturer="JVmaisGpeur",
            model="Comptage Œufs Poulailler",
            sw_version=VERSION,
            entry_type=DeviceEntryType.SERVICE,
        )

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(
            async_dispatcher_connect(self.hass, self.manager.signal, self._handle_update)
        )

    @callback
    def _handle_update(self) -> None:
        self.async_write_ha_state()
