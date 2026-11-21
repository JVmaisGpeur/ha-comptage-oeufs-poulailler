"""Core of the integration: scheduling, camera + AI readings, history and photos."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
import logging
from pathlib import Path
import shutil
from typing import Any

from homeassistant.components import camera
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.event import async_call_later, async_track_time_change
from homeassistant.helpers.storage import Store
from homeassistant.util import dt as dt_util

from .const import (
    AI_TIMEOUT,
    CAMERA_TIMEOUT,
    CONF_AI_TASK,
    CONF_CAMERA,
    CONF_NESTS,
    CONF_NOTIFY_ENTITY,
    CONF_NOTIFY_SERVICE,
    CONF_PROMPT,
    CONF_SENSITIVITY,
    CONF_SNAPSHOT_DAYS,
    DEFAULT_DELAY,
    DEFAULT_END,
    DEFAULT_INTERVAL,
    DEFAULT_NESTS,
    DEFAULT_SENSITIVITY,
    DEFAULT_SNAPSHOT_DAYS,
    DEFAULT_START,
    DOMAIN,
    EVENT_NEW_EGG,
    FINAL_RETRY_DELAY,
    FORCE_AI_AFTER,
    MAX_EVENTS,
    MAX_JOURNAL,
    MEDIA_FOLDER,
    RETRY_DELAYS,
    STORAGE_VERSION,
)
from .i18n import render_line, text
from .logic import build_prompt, changed_fraction, parse_legacy_history, stats, thumbnail

_LOGGER = logging.getLogger(__name__)

LAST_IMAGE = "derniere_lecture.jpg"
TEMP_IMAGE = "lecture_en_cours.jpg"
EVENTS_DIR = "evenements"


def _reading(number: int) -> dict[str, Any]:
    """Translated « Reading N » label, resolved when the line is displayed."""
    return {"key": "reading", "params": {"r": number}}


def _reason(err: Exception) -> dict[str, Any] | str:
    """Short, translated reason for an AI failure."""
    message = str(err)
    if isinstance(err, TimeoutError):
        return {"key": "reason_timeout"}
    if isinstance(err, (KeyError, TypeError, ValueError)):
        return {"key": "reason_invalid"}
    if "503" in message or "overloaded" in message.lower() or "high demand" in message.lower():
        return {"key": "reason_overloaded"}
    if "429" in message or "quota" in message.lower() or "RESOURCE_EXHAUSTED" in message:
        return {"key": "reason_quota"}
    first_line = message.strip().splitlines()[0] if message.strip() else type(err).__name__
    return first_line[:80]


@dataclass
class Reading:
    """Résultat d'une lecture."""

    eggs: int
    hen: bool
    image: bytes | None
    reused: bool = False


def _default_data() -> dict[str, Any]:
    return {
        "history": {},
        "today_date": None,
        "today": 0,
        "baseline": None,  # œufs actuellement dans les pondoirs (None = pas encore initialisé)
        "auto": True,
        "start": DEFAULT_START,
        "end": DEFAULT_END,
        "interval": DEFAULT_INTERVAL,
        "delay": DEFAULT_DELAY,
        "events": [],
        "journal": [],
        "last_reading": None,
        "last_egg": None,
        "imported": False,
    }


class PoulaillerManager:
    """Gère un poulailler (une entrée de configuration)."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self.entry = entry
        self.signal = f"{DOMAIN}_{entry.entry_id}_update"
        self.data: dict[str, Any] = _default_data()
        self._store: Store[dict[str, Any]] = Store(
            hass, STORAGE_VERSION, f"{DOMAIN}.{entry.entry_id}"
        )
        self._lock = asyncio.Lock()
        self._unsubs: list = []
        self._ref_thumb: bytes | None = None
        self.media_root: Path | None = None
        self._media_uri: str | None = None
        self.media_url: str | None = None
        self.counting = False

    # ------------------------------------------------------------------ options
    @property
    def options(self) -> dict[str, Any]:
        return {**self.entry.data, **self.entry.options}

    @property
    def language(self) -> str:
        return self.hass.config.language

    @property
    def name(self) -> str:
        return self.entry.title

    @property
    def camera_entity(self) -> str:
        return self.options[CONF_CAMERA]

    @property
    def start(self) -> time:
        return time.fromisoformat(self.data["start"])

    @property
    def end(self) -> time:
        return time.fromisoformat(self.data["end"])

    @property
    def interval(self) -> int:
        return int(self.data["interval"])

    @property
    def delay(self) -> int:
        return int(self.data["delay"])

    # ------------------------------------------------------------------ cycle de vie
    async def async_setup(self) -> None:
        stored = await self._store.async_load()
        if stored:
            self.data.update(stored)
        await self.hass.async_add_executor_job(self._prepare_media)
        self._ensure_today()

    def _prepare_media(self) -> None:
        media_dirs = self.hass.config.media_dirs or {}
        if not media_dirs:
            _LOGGER.warning(
                "Aucun dossier média configuré : les photos ne seront pas conservées"
            )
            return
        key = "local" if "local" in media_dirs else next(iter(media_dirs))
        rel = f"{MEDIA_FOLDER}/{self.entry.entry_id}"
        self.media_root = Path(media_dirs[key]) / rel
        (self.media_root / EVENTS_DIR).mkdir(parents=True, exist_ok=True)
        self._media_uri = f"media-source://media_source/{key}/{rel}"
        self.media_url = f"/media/{key}/{rel}"

    @callback
    def async_start(self) -> None:
        self._unsubs.append(async_track_time_change(self.hass, self._on_minute, second=0))

    async def async_stop(self) -> None:
        for unsub in self._unsubs:
            unsub()
        self._unsubs.clear()
        await self._store.async_save(self.data)

    async def async_remove_files(self) -> None:
        """Supprime les photos à la suppression de l'intégration."""
        if self.media_root:
            await self.hass.async_add_executor_job(
                shutil.rmtree, self.media_root, True
            )
        await self._store.async_remove()

    # ------------------------------------------------------------------ outils
    def _save(self) -> None:
        self._store.async_delay_save(lambda: self.data, 2)

    @callback
    def _updated(self) -> None:
        self._save()
        async_dispatcher_send(self.hass, self.signal)

    def _log(self, key: str, *, cycle: bool = False, **params: Any) -> None:
        """Journal line stored as key + parameters, translated when displayed."""
        line = {"t": dt_util.now().strftime("%H:%M:%S"), "k": key, "p": params, "c": cycle}
        _LOGGER.debug("[%s] %s", self.name, render_line("en", line))
        journal = self.data["journal"]
        journal.append(line)
        del journal[:-MAX_JOURNAL]
        self._updated()

    def journal(self, language: str | None = None, count: int = 20) -> list[str]:
        """Last journal lines in the requested language (HA language by default)."""
        lang = language or self.language
        return [render_line(lang, line) for line in self.data["journal"][-count:]]

    def _today(self) -> date:
        return dt_util.now().date()

    def _set_today(self, value: int) -> None:
        self.data["today"] = max(0, int(value))
        self.data["history"][self.data["today_date"]] = self.data["today"]

    @callback
    def _ensure_today(self) -> None:
        """Passage à un nouveau jour : compteur à zéro (les œufs restés au nid ne sont pas recomptés)."""
        today = self._today().isoformat()
        if self.data["today_date"] == today:
            return
        self.data["today_date"] = today
        self.data["today"] = int(self.data["history"].get(today, 0))
        self.data["history"][today] = self.data["today"]
        self.hass.async_create_task(self._async_prune())
        self._updated()

    async def _async_prune(self) -> None:
        """Supprime les photos plus vieilles que la durée de conservation."""
        days = int(self.options.get(CONF_SNAPSHOT_DAYS, DEFAULT_SNAPSHOT_DAYS))
        limit = dt_util.now() - timedelta(days=days)
        keep, drop = [], []
        for event in self.data["events"]:
            (keep if dt_util.parse_datetime(event["time"]) >= limit else drop).append(event)
        keep, extra = keep[:MAX_EVENTS], keep[MAX_EVENTS:]
        drop += extra
        if not drop:
            return
        self.data["events"] = keep
        if self.media_root:
            files = [self.media_root / f for e in drop for f in e.get("images", [])]
            await self.hass.async_add_executor_job(_unlink_all, files)
        self._updated()

    # ------------------------------------------------------------------ planification
    @callback
    def _on_minute(self, now: datetime) -> None:
        self._ensure_today()
        if not self.data["auto"]:
            return
        now = dt_util.as_local(now).replace(second=0, microsecond=0)
        start = now.replace(hour=self.start.hour, minute=self.start.minute)
        end = now.replace(hour=self.end.hour, minute=self.end.minute)
        if now == end:
            source = "final"
        elif start <= now < end and int((now - start).total_seconds() // 60) % self.interval == 0:
            source = "auto"
        else:
            return
        self.entry.async_create_background_task(
            self.hass, self.async_count(source), f"{DOMAIN}_comptage"
        )

    # ------------------------------------------------------------------ comptage
    async def async_count(self, source: str = "manual") -> None:
        if self._lock.locked():
            self._log("already_running")
            return
        success = True
        async with self._lock:
            self.counting = True
            self._updated()
            try:
                success = await self._run_cycle(source)
            except Exception as err:  # noqa: BLE001
                _LOGGER.exception("Error while counting")
                self._log("unexpected_error", error=str(err)[:120])
            finally:
                self.counting = False
                self._updated()
        if not success and source == "final":
            # Do not let the last eggs of the day slip to tomorrow
            self._log("final_retry", min=FINAL_RETRY_DELAY)
            self._unsubs.append(
                async_call_later(self.hass, FINAL_RETRY_DELAY * 60, self._final_retry)
            )

    @callback
    def _final_retry(self, _now: datetime) -> None:
        self.entry.async_create_background_task(
            self.hass, self.async_count("retry"), f"{DOMAIN}_comptage"
        )

    async def _run_cycle(self, source: str) -> bool:
        """One counting cycle. Returns False when no reading could be made."""
        self._ensure_today()
        self._log("cycle_start", cycle=True, source={"key": f"source_{source}"})

        r1 = await self._reading(1, force=source != "auto")
        if r1 is None:
            self._log("reading_failed", reading=_reading(1))
            return False

        base = self.data["baseline"]
        if base is None:
            self.data["baseline"] = r1.eggs
            self._log("init", n=r1.eggs)
            return True

        n1 = r1.eggs
        if n1 == base:
            self._log("same", reading=_reading(1), n=n1)
            return True
        if n1 < base and r1.hen:
            self._log("hen_keep", reading=_reading(1), n=n1, base=base)
            return True

        rising = n1 > base
        self._log(
            "rise_wait" if rising else "drop_wait",
            reading=_reading(1), n=n1, base=base, delay=self.delay,
        )
        await asyncio.sleep(self.delay * 60)
        if source != "manual" and not self.data["auto"]:
            self._log("paused_abort")
            return True

        r2 = await self._reading(2, force=True)
        if r2 is None:
            self._log("reading_failed", reading=_reading(2))
            return True
        base2 = self.data["baseline"] if self.data["baseline"] is not None else base
        n2 = r2.eggs

        if rising:
            confirmed = min(n1, n2)
            if confirmed > base2:
                new = confirmed - base2
                self.data["baseline"] = confirmed
                self._set_today(self.data["today"] + new)
                images = await self._save_event("confirme", r1, r2, base2, confirmed)
                self.data["last_egg"] = {
                    "time": dt_util.now().isoformat(),
                    "image": images[-1] if images else None,
                }
                self._log(
                    "confirmed", reading=_reading(2), n=n2, new=new, today=self.data["today"]
                )
                await self._notify_new(new)
            else:
                await self._save_event("rejete", r1, r2, base2, base2)
                self._log("not_confirmed", reading=_reading(2), n=n2)
        elif n2 < base2 and not r2.hen:
            remaining = max(n1, n2)
            self.data["baseline"] = remaining
            await self._save_event("ramassage", r1, r2, base2, remaining)
            self._log("collect_confirmed", n=remaining)
        else:
            self._log("drop_not_confirmed", reading=_reading(2), n=n2, base=base2)
        return True

    async def _reading(self, number: int, *, force: bool) -> Reading | None:
        """Photo + AI, retried with increasing delays (AI services saturate briefly)."""
        label = _reading(number)
        attempts = len(RETRY_DELAYS) + 1
        for attempt in range(attempts):
            wait = RETRY_DELAYS[attempt] if attempt < len(RETRY_DELAYS) else None
            try:
                image = await camera.async_get_image(
                    self.hass, self.camera_entity, timeout=CAMERA_TIMEOUT
                )
                content = image.content
            except HomeAssistantError as err:
                self._log("camera_unavailable", reading=label, error=str(err)[:80])
                if wait is None:
                    return None
                await asyncio.sleep(wait)
                continue

            thumb = await self.hass.async_add_executor_job(thumbnail, content)
            reused = self._reuse_last(thumb, force)
            if reused is not None:
                self._log(
                    "unchanged", reading=label, pct=float(reused[1]), n=reused[0].eggs
                )
                return reused[0]

            result = await self._ask_ai(content)
            if not isinstance(result, tuple):
                if wait is None:
                    self._log("ai_failed", reading=label, reason=result)
                    return None
                self._log("ai_retry", reading=label, reason=result, s=wait)
                await asyncio.sleep(wait)
                continue

            eggs, hen = result
            self._ref_thumb = thumb
            self.data["last_reading"] = {
                "time": dt_util.now().isoformat(),
                "eggs": eggs,
                "hen": hen,
            }
            await self._write(LAST_IMAGE, content)
            if hen:
                self._log("hen_seen", reading=label, n=eggs)
            return Reading(eggs, hen, content)
        return None

    def _reuse_last(self, thumb: bytes | None, force: bool) -> tuple[Reading, float] | None:
        """Last reading again if the image has not changed (saves AI calls)."""
        sensitivity = float(self.options.get(CONF_SENSITIVITY, DEFAULT_SENSITIVITY)) / 100
        last = self.data.get("last_reading")
        if force or sensitivity <= 0 or thumb is None or self._ref_thumb is None or not last:
            return None
        age = dt_util.now() - dt_util.parse_datetime(last["time"])
        if age > timedelta(minutes=FORCE_AI_AFTER):
            return None
        fraction = changed_fraction(thumb, self._ref_thumb)
        if fraction >= sensitivity:
            return None
        return Reading(int(last["eggs"]), bool(last["hen"]), None, reused=True), fraction

    def prompt(self) -> str:
        nests = int(self.options.get(CONF_NESTS, DEFAULT_NESTS))
        template = self.options.get(CONF_PROMPT) or text(self.language, "prompt")
        return build_prompt(template, nests)

    async def _ask_ai(self, content: bytes) -> tuple[int, bool] | dict[str, Any] | str:
        """(eggs, hen) on success, otherwise the reason of the failure."""
        if self._media_uri and await self._write(TEMP_IMAGE, content):
            media_id = f"{self._media_uri}/{TEMP_IMAGE}"
        else:
            media_id = f"media-source://camera/{self.camera_entity}"
        lang = self.language
        data: dict[str, Any] = {
            "task_name": text(lang, "task_name", name=self.name),
            "instructions": self.prompt(),
            "structure": {
                "eggs": {
                    "description": text(lang, "field_eggs"),
                    "required": True,
                    "selector": {"number": {"min": 0, "max": 60, "mode": "box"}},
                },
                "hen_present": {
                    "description": text(lang, "field_hen"),
                    "required": True,
                    "selector": {"boolean": {}},
                },
            },
            "attachments": [{"media_content_id": media_id, "media_content_type": "image/jpeg"}],
        }
        if ai_entity := self.options.get(CONF_AI_TASK):
            data["entity_id"] = ai_entity
        try:
            async with asyncio.timeout(AI_TIMEOUT):
                response = await self.hass.services.async_call(
                    "ai_task", "generate_data", data, blocking=True, return_response=True
                )
            result = (response or {}).get("data") or {}
            eggs = int(float(result["eggs"]))
            hen = bool(result.get("hen_present", False))
        except (HomeAssistantError, TimeoutError, KeyError, TypeError, ValueError) as err:
            _LOGGER.warning("[%s] AI reading failed: %s", self.name, err)
            return _reason(err)
        if eggs < 0:
            return {"key": "reason_invalid"}
        return eggs, hen

    async def _write(self, relative: str, content: bytes) -> bool:
        if not self.media_root:
            return False
        path = self.media_root / relative
        try:
            await self.hass.async_add_executor_job(path.write_bytes, content)
        except OSError as err:
            _LOGGER.warning("Impossible d'écrire %s : %s", path, err)
            return False
        return True

    async def _save_event(
        self, kind: str, r1: Reading, r2: Reading, before: int, after: int
    ) -> list[str]:
        now = dt_util.now()
        event_id = now.strftime("%Y%m%d_%H%M%S")
        images: list[str] = []
        for index, reading in enumerate((r1, r2), start=1):
            if reading.image is None:
                continue
            name = f"{EVENTS_DIR}/{event_id}_{index}.jpg"
            if await self._write(name, reading.image):
                images.append(name)
        self.data["events"].insert(
            0,
            {
                "id": event_id,
                "time": now.isoformat(),
                "type": kind,
                "lecture1": r1.eggs,
                "lecture2": r2.eggs,
                "poule1": r1.hen,
                "poule2": r2.hen,
                "avant": before,
                "apres": after,
                "images": images,
            },
        )
        if len(self.data["events"]) > MAX_EVENTS:
            self.hass.async_create_task(self._async_prune())
        return images

    async def _notify_new(self, new: int) -> None:
        today = self.data["today"]
        key = "notify_one" if new == 1 else "notify_many"
        message = text(self.language, key, name=self.name, new=new, today=today)
        self.hass.bus.async_fire(
            EVENT_NEW_EGG,
            {"config_entry_id": self.entry.entry_id, "new": new, "total": today},
        )
        calls: list[tuple[str, str, dict[str, Any]]] = []
        if entity := self.options.get(CONF_NOTIFY_ENTITY):
            calls.append(("notify", "send_message", {"entity_id": entity, "message": message}))
        if service := (self.options.get(CONF_NOTIFY_SERVICE) or "").strip():
            domain, _, name = service.partition(".")
            calls.append((domain, name, {"message": message}))
        for domain, name, data in calls:
            try:
                await self.hass.services.async_call(domain, name, data, blocking=True)
            except (HomeAssistantError, ValueError) as err:
                self._log("notify_failed", service=f"{domain}.{name}", error=str(err)[:80])

    # ------------------------------------------------------------------ actions
    async def async_correct(self, day: date, count: int) -> None:
        self._ensure_today()
        today = self._today()
        if day > today:
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="future_date",
                translation_placeholders={"date": day.isoformat()},
            )
        if day == today:
            self._set_today(count)
        else:
            self.data["history"][day.isoformat()] = max(0, int(count))
        self._log("corrected", date=day.isoformat(), n=count)

    @callback
    def async_collected(self, remaining: int = 0) -> None:
        self.data["baseline"] = max(0, int(remaining))
        self._log("collected", n=remaining)

    async def async_import(self, entity_id: str) -> int:
        state = self.hass.states.get(entity_id)
        if state is None:
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="entity_not_found",
                translation_placeholders={"entity_id": entity_id},
            )
        imported = parse_legacy_history(state.state)
        history = self.data["history"]
        today = self._today().isoformat()
        added = 0
        for day, count in imported.items():
            if day == today or (day in history and history[day] != 0):
                continue  # never overwrite today or a value already known
            history[day] = count
            added += 1
        self.data["imported"] = True
        self._log("imported", entity=entity_id, n=added)
        return added

    @callback
    def async_set_setting(self, key: str, value: Any) -> None:
        if key in ("start", "end") and isinstance(value, time):
            value = value.replace(microsecond=0).isoformat()
        self.data[key] = value
        self._updated()

    # ------------------------------------------------------------------ read
    def stats(self) -> dict[str, int]:
        return stats(self.data["history"], self._today())

    def file_path(self, relative: str | None) -> Path | None:
        if not relative or not self.media_root:
            return None
        return self.media_root / relative


def _unlink_all(paths: list[Path]) -> None:
    for path in paths:
        try:
            path.unlink(missing_ok=True)
        except OSError:
            pass
