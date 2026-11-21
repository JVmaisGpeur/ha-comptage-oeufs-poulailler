"""Constantes de l'intégration Comptage Œufs Poulailler."""

from __future__ import annotations

DOMAIN = "comptage_oeufs_poulailler"
VERSION = "1.0.0"

STORAGE_VERSION = 1

# Configuration (config flow / options flow)
CONF_NAME = "name"
CONF_CAMERA = "camera"
CONF_AI_TASK = "ai_task_entity"
CONF_NOTIFY_ENTITY = "notify_entity"
CONF_NOTIFY_SERVICE = "notify_service"
CONF_NESTS = "nests"
CONF_PROMPT = "prompt"
CONF_SENSITIVITY = "sensitivity"
CONF_SNAPSHOT_DAYS = "snapshot_days"
CONF_IMPORT_ENTITY = "import_entity"

DEFAULT_NAME = "Poulailler"
DEFAULT_NESTS = 2
DEFAULT_SENSITIVITY = 0.1  # % de pixels modifiés en dessous duquel l'image est jugée identique (un œuf ≈ 0,2-2 %)
DEFAULT_SNAPSHOT_DAYS = 30
DEFAULT_PROMPT = (
    "Cette image vient d'une caméra qui filme {pondoirs} pondoir(s) (nids de paille) "
    "d'un poulailler. Compte le nombre total d'œufs visibles dans tous les pondoirs. "
    "Ne compte pas ce qui n'est pas un œuf (paille, plume, pastille, copeaux…). "
    "Indique aussi si une poule est présente dans un pondoir ou cache une partie d'un nid."
)

# Réglages modifiables depuis les entités / la carte
DEFAULT_START = "08:00:00"
DEFAULT_END = "17:30:00"
DEFAULT_INTERVAL = 15  # min
DEFAULT_DELAY = 2  # min

# Comportement interne
RETRY_DELAY = 30  # s avant un nouvel essai si la caméra ou l'IA échoue
AI_TIMEOUT = 120  # s
CAMERA_TIMEOUT = 20  # s
FORCE_AI_AFTER = 60  # min : au-delà, l'IA est rappelée même si l'image semble identique
DIFF_PIXEL_THRESHOLD = 30  # écart de niveau de gris (0-255) pour qu'un pixel compte comme modifié
THUMB_SIZE = (160, 120)
MAX_EVENTS = 500
MAX_JOURNAL = 60

# Événement bus HA
EVENT_NEW_EGG = f"{DOMAIN}_nouvel_oeuf"

# Services
SERVICE_COUNT_NOW = "compter_maintenant"
SERVICE_CORRECT = "corriger"
SERVICE_COLLECTED = "oeufs_ramasses"
SERVICE_IMPORT = "importer_historique"
ATTR_ENTRY_ID = "config_entry_id"
ATTR_DATE = "date"
ATTR_COUNT = "nombre"
ATTR_REMAINING = "restants"
ATTR_ENTITY_ID = "entity_id"

# Carte Lovelace embarquée
CARD_FILENAME = "comptage-oeufs-poulailler-card.js"
CARD_URL = f"/{DOMAIN}/{CARD_FILENAME}"

MEDIA_FOLDER = DOMAIN
