"""Image : photo du dernier œuf confirmé."""

from __future__ import annotations

from homeassistant.components.image import ImageEntity
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.util import dt as dt_util

from .entity import PoulaillerEntity


async def async_setup_entry(
    hass: HomeAssistant, entry, async_add_entities: AddConfigEntryEntitiesCallback
) -> None:
    async_add_entities([LastEggImage(hass, entry.runtime_data)])


class LastEggImage(PoulaillerEntity, ImageEntity):
    platform_domain = "image"
    _attr_content_type = "image/jpeg"
    _attr_icon = "mdi:egg-easter"

    def __init__(self, hass: HomeAssistant, manager) -> None:
        ImageEntity.__init__(self, hass)
        PoulaillerEntity.__init__(self, manager, "dernier_oeuf_detecte")
        self._refresh()

    def _refresh(self) -> None:
        last = self.manager.data.get("last_egg") or {}
        self._image_rel = last.get("image")
        self._attr_image_last_updated = (
            dt_util.parse_datetime(last["time"]) if last.get("time") else None
        )

    @callback
    def _handle_update(self) -> None:
        self._refresh()
        super()._handle_update()

    async def async_image(self) -> bytes | None:
        path = self.manager.file_path(self._image_rel)
        if path is None:
            return None
        try:
            return await self.hass.async_add_executor_job(path.read_bytes)
        except OSError:
            return None
