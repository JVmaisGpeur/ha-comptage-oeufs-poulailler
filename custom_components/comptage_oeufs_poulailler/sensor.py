"""Capteurs : œufs du jour, totaux, œufs dans les pondoirs, état du comptage."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .entity import PoulaillerEntity
from .manager import PoulaillerManager

UNIT = "œufs"


@dataclass(frozen=True, kw_only=True)
class EggSensorDescription(SensorEntityDescription):
    value: Callable[[PoulaillerManager], Any]


SENSORS: tuple[EggSensorDescription, ...] = (
    EggSensorDescription(
        key="oeufs_aujourd_hui",
        icon="mdi:egg",
        native_unit_of_measurement=UNIT,
        state_class=SensorStateClass.MEASUREMENT,
        value=lambda m: m.data["today"],
    ),
    EggSensorDescription(
        key="oeufs_hier",
        icon="mdi:egg-outline",
        native_unit_of_measurement=UNIT,
        value=lambda m: m.stats()["hier"],
    ),
    EggSensorDescription(
        key="oeufs_7_jours",
        icon="mdi:calendar-week",
        native_unit_of_measurement=UNIT,
        value=lambda m: m.stats()["7_jours"],
    ),
    EggSensorDescription(
        key="oeufs_ce_mois",
        icon="mdi:calendar-month",
        native_unit_of_measurement=UNIT,
        value=lambda m: m.stats()["ce_mois"],
    ),
    EggSensorDescription(
        key="oeufs_cette_annee",
        icon="mdi:calendar",
        native_unit_of_measurement=UNIT,
        value=lambda m: m.stats()["cette_annee"],
    ),
    EggSensorDescription(
        key="oeufs_total",
        icon="mdi:sigma",
        native_unit_of_measurement=UNIT,
        value=lambda m: m.stats()["total"],
    ),
    EggSensorDescription(
        key="oeufs_dans_les_pondoirs",
        icon="mdi:basket",
        native_unit_of_measurement=UNIT,
        value=lambda m: m.data["baseline"],
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry, async_add_entities: AddConfigEntryEntitiesCallback
) -> None:
    manager: PoulaillerManager = entry.runtime_data
    entities: list[SensorEntity] = [EggSensor(manager, d) for d in SENSORS]
    entities.append(StatusSensor(manager))
    async_add_entities(entities)


class EggSensor(PoulaillerEntity, SensorEntity):
    platform_domain = "sensor"
    entity_description: EggSensorDescription

    def __init__(self, manager: PoulaillerManager, description: EggSensorDescription) -> None:
        self.entity_description = description
        super().__init__(manager, description.key)

    @property
    def native_value(self) -> Any:
        return self.entity_description.value(self.manager)

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        if self.entity_description.key != "oeufs_aujourd_hui":
            return None
        last = self.manager.data.get("last_reading") or {}
        return {
            "dans_les_pondoirs": self.manager.data["baseline"],
            "derniere_lecture": last.get("time"),
            "derniere_lecture_oeufs": last.get("eggs"),
            "poule_presente": last.get("hen"),
            "comptage_automatique": self.manager.data["auto"],
        }


class StatusSensor(PoulaillerEntity, SensorEntity):
    """Dernière ligne du journal ; le journal complet est en attribut (non enregistré)."""

    platform_domain = "sensor"
    _attr_icon = "mdi:text-box-outline"
    _unrecorded_attributes = frozenset({"journal"})

    def __init__(self, manager: PoulaillerManager) -> None:
        super().__init__(manager, "etat_du_comptage")

    @property
    def native_value(self) -> str | None:
        journal = self.manager.data["journal"]
        return journal[-1][:255] if journal else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {"en_cours": self.manager.counting, "journal": self.manager.data["journal"][-20:]}
