"""WebSocket API used by the Lovelace card."""

from __future__ import annotations

from datetime import timedelta
from typing import Any
from urllib.parse import quote

import voluptuous as vol

from homeassistant.components import websocket_api
from homeassistant.components.http.auth import async_sign_path
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import entity_registry as er
from homeassistant.util import dt as dt_util

from .const import DOMAIN
from .manager import LAST_IMAGE, PoulaillerManager

SIGN_DURATION = timedelta(hours=12)


@callback
def async_register(hass: HomeAssistant) -> None:
    websocket_api.async_register_command(hass, ws_entries)
    websocket_api.async_register_command(hass, ws_data)


@websocket_api.websocket_command({vol.Required("type"): f"{DOMAIN}/entries"})
@callback
def ws_entries(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict) -> None:
    managers: dict[str, PoulaillerManager] = hass.data.get(DOMAIN, {})
    connection.send_result(
        msg["id"], [{"entry_id": k, "title": m.name} for k, m in managers.items()]
    )


@websocket_api.websocket_command(
    {
        vol.Required("type"): f"{DOMAIN}/data",
        vol.Optional("entry_id"): str,
        vol.Optional("days", default=60): vol.All(int, vol.Range(min=1, max=3660)),
        vol.Optional("events", default=20): vol.All(int, vol.Range(min=0, max=500)),
        vol.Optional("language"): str,
    }
)
@callback
def ws_data(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict) -> None:
    managers: dict[str, PoulaillerManager] = hass.data.get(DOMAIN, {})
    entry_id = msg.get("entry_id") or next(iter(managers), None)
    manager = managers.get(entry_id) if entry_id else None
    if manager is None:
        connection.send_error(msg["id"], "not_found", "No chicken coop configured")
        return

    def url(relative: str | None, stamp: str | None = None) -> str | None:
        if not relative or not manager.media_url:
            return None
        path = f"{manager.media_url}/{quote(relative)}"
        if stamp:  # change à chaque nouvelle photo : évite le cache du navigateur
            path += f"?v={quote(stamp)}"
        # Le paramètre v fait partie de la signature (HA refuse les paramètres non signés)
        return async_sign_path(
            hass, path, SIGN_DURATION, refresh_token_id=connection.refresh_token_id
        )

    data = manager.data
    today = dt_util.now().date()
    first = (today - timedelta(days=msg["days"] - 1)).isoformat()
    history = sorted(
        ({"date": d, "count": c} for d, c in data["history"].items() if d >= first),
        key=lambda item: item["date"],
    )
    events: list[dict[str, Any]] = []
    for event in data["events"][: msg["events"]]:
        events.append({**event, "urls": [url(img) for img in event.get("images", [])]})

    registry = er.async_get(hass)
    prefix = f"{manager.entry.entry_id}_"
    entities = {
        e.unique_id.removeprefix(prefix): e.entity_id
        for e in er.async_entries_for_config_entry(registry, manager.entry.entry_id)
    }
    last = data.get("last_reading") or {}

    connection.send_result(
        msg["id"],
        {
            "entry_id": manager.entry.entry_id,
            "title": manager.name,
            "today_date": data["today_date"],
            "today": data["today"],
            "baseline": data["baseline"],
            "auto": data["auto"],
            "counting": manager.counting,
            "settings": {k: data[k] for k in ("start", "end", "interval", "delay")},
            "stats": manager.stats(),
            "history": history,
            "events": events,
            "journal": manager.journal(msg.get("language"), 15),
            "last_reading": last,
            "last_image_url": url(LAST_IMAGE, last.get("time")) if last else None,
            "camera": manager.camera_entity,
            "entities": entities,
        },
    )
