"""Runtime texts (journal, notifications, AI prompt) in several languages.

Home Assistant translation files only cover the UI (config flow, entity names,
services, errors). Texts generated at runtime live here. To add a language,
copy the "en" block, translate the values and keep the {placeholders}.
"""

from __future__ import annotations

from datetime import date
from typing import Any

FALLBACK = "en"

TEXTS: dict[str, dict[str, str]] = {
    "en": {
        "default_name": "Chicken coop",
        "date_format": "%Y-%m-%d",
        "source_auto": "automatic",
        "source_final": "final",
        "source_manual": "manual",
        "source_retry": "retry of the final count",
        "reading": "Reading {r}",
        "cycle_start": "Count started ({source})",
        "already_running": "A count is already running: request ignored",
        "unexpected_error": "Unexpected error: {error}",
        "reading_failed": "{reading} failed: nothing validated",
        "init": "Initialisation: {n} egg(s) already in the nests, not counted as laid today",
        "same": "{reading}: {n} egg(s), same as before: nothing new",
        "hen_keep": "{reading}: {n} egg(s) but a hen is on a nest: keeping {base}",
        "rise_wait": "{reading}: {n} egg(s) for {base} known: confirming in {delay} min",
        "drop_wait": "{reading}: {n} egg(s) for {base} known (collected?): confirming in {delay} min",
        "paused_abort": "Automatic counting paused while waiting: cancelled",
        "confirmed": "{reading}: {n} egg(s): confirmed, +{new} → {today} egg(s) today",
        "not_confirmed": "{reading}: {n} egg(s): not confirmed, nothing validated",
        "collect_confirmed": "Collection confirmed: {n} egg(s) left in the nests",
        "drop_not_confirmed": "{reading}: {n} egg(s): drop not confirmed, keeping {base}",
        "camera_unavailable": "{reading}: camera unavailable ({error})",
        "unchanged": "{reading}: image unchanged ({pct} of pixels changed), AI not called: {n} egg(s)",
        "ai_retry": "{reading}: the AI did not answer ({reason}), retrying in {s} s",
        "ai_failed": "{reading}: the AI did not answer ({reason})",
        "hen_seen": "{reading}: {n} egg(s) seen, a hen is on a nest",
        "final_retry": "Final count failed: new attempt in {min} min",
        "notify_failed": "Notification {service} failed: {error}",
        "corrected": "Correction: {date} = {n} egg(s)",
        "collected": "Eggs collected: {n} egg(s) left in the nests",
        "imported": "History imported from {entity}: {n} day(s)",
        "reason_overloaded": "AI service overloaded",
        "reason_quota": "AI quota reached",
        "reason_timeout": "no answer in time",
        "reason_invalid": "unreadable answer",
        "notify_one": "🥚 {name}: new egg! Total today: {today}",
        "notify_many": "🥚 {name}: {new} new eggs! Total today: {today}",
        "task_name": "Egg count – {name}",
        "prompt": (
            "This image comes from a camera filming {pondoirs} nesting box(es) of a chicken coop. "
            "Count the total number of eggs visible in all the nesting boxes. "
            "Do not count anything that is not an egg (straw, feather, wood shavings…). "
            "Also say whether a hen is sitting in a nesting box or hiding part of a nest."
        ),
        "field_eggs": "Total number of eggs visible in all the nesting boxes",
        "field_hen": "Is a hen in a nesting box or hiding part of a nest?",
    },
    "fr": {
        "default_name": "Poulailler",
        "date_format": "%d/%m/%y",
        "source_auto": "automatique",
        "source_final": "final",
        "source_manual": "manuel",
        "source_retry": "nouvel essai du comptage final",
        "reading": "Lecture {r}",
        "cycle_start": "Début du comptage ({source})",
        "already_running": "Un comptage est déjà en cours : demande ignorée",
        "unexpected_error": "Erreur inattendue : {error}",
        "reading_failed": "{reading} en échec : rien de validé",
        "init": "Initialisation : {n} œuf(s) déjà dans les pondoirs, ils ne sont pas comptés comme pondus aujourd'hui",
        "same": "{reading} : {n} œuf(s), comme avant : rien de nouveau",
        "hen_keep": "{reading} : {n} œuf(s) mais une poule est sur un nid : on garde {base}",
        "rise_wait": "{reading} : {n} œuf(s) pour {base} connu(s) : confirmation dans {delay} min",
        "drop_wait": "{reading} : {n} œuf(s) pour {base} connu(s) (ramassage ?) : confirmation dans {delay} min",
        "paused_abort": "Comptage automatique mis en pause pendant l'attente : abandon",
        "confirmed": "{reading} : {n} œuf(s) : confirmé, +{new} → {today} œuf(s) aujourd'hui",
        "not_confirmed": "{reading} : {n} œuf(s) : non confirmé, rien de validé",
        "collect_confirmed": "Ramassage confirmé : {n} œuf(s) restent dans les pondoirs",
        "drop_not_confirmed": "{reading} : {n} œuf(s) : baisse non confirmée, on garde {base}",
        "camera_unavailable": "{reading} : caméra indisponible ({error})",
        "unchanged": "{reading} : image inchangée ({pct} de pixels modifiés), IA non sollicitée : {n} œuf(s)",
        "ai_retry": "{reading} : l'IA n'a pas répondu ({reason}), nouvel essai dans {s} s",
        "ai_failed": "{reading} : l'IA n'a pas répondu ({reason})",
        "hen_seen": "{reading} : {n} œuf(s) vu(s), poule présente sur un nid",
        "final_retry": "Comptage final en échec : nouvel essai dans {min} min",
        "notify_failed": "Notification {service} en échec : {error}",
        "corrected": "Correction : {date} = {n} œuf(s)",
        "collected": "Œufs ramassés : {n} œuf(s) laissé(s) dans les pondoirs",
        "imported": "Historique importé depuis {entity} : {n} jour(s)",
        "reason_overloaded": "service d'IA surchargé",
        "reason_quota": "quota d'IA atteint",
        "reason_timeout": "pas de réponse à temps",
        "reason_invalid": "réponse illisible",
        "notify_one": "🥚 {name} : nouvel œuf ! Total aujourd'hui : {today}",
        "notify_many": "🥚 {name} : {new} nouveaux œufs ! Total aujourd'hui : {today}",
        "task_name": "Comptage des œufs – {name}",
        "prompt": (
            "Cette image vient d'une caméra qui filme {pondoirs} pondoir(s) (nids de paille) "
            "d'un poulailler. Compte le nombre total d'œufs visibles dans tous les pondoirs. "
            "Ne compte pas ce qui n'est pas un œuf (paille, plume, pastille, copeaux…). "
            "Indique aussi si une poule est présente dans un pondoir ou cache une partie d'un nid."
        ),
        "field_eggs": "Nombre total d'œufs visibles dans tous les pondoirs",
        "field_hen": "Une poule est-elle dans un pondoir ou cache-t-elle une partie d'un nid ?",
    },
    "de": {
        "default_name": "Hühnerstall",
        "date_format": "%d.%m.%y",
        "source_auto": "automatisch",
        "source_final": "abschließend",
        "source_manual": "manuell",
        "source_retry": "erneuter Versuch der Abschlusszählung",
        "reading": "Messung {r}",
        "cycle_start": "Zählung gestartet ({source})",
        "already_running": "Es läuft bereits eine Zählung: Anfrage ignoriert",
        "unexpected_error": "Unerwarteter Fehler: {error}",
        "reading_failed": "{reading} fehlgeschlagen: nichts übernommen",
        "init": "Initialisierung: {n} Ei(er) bereits in den Nestern, nicht als heute gelegt gezählt",
        "same": "{reading}: {n} Ei(er), wie zuvor: nichts Neues",
        "hen_keep": "{reading}: {n} Ei(er), aber ein Huhn sitzt auf einem Nest: {base} bleibt",
        "rise_wait": "{reading}: {n} Ei(er) bei {base} bekannten: Bestätigung in {delay} min",
        "drop_wait": "{reading}: {n} Ei(er) bei {base} bekannten (eingesammelt?): Bestätigung in {delay} min",
        "paused_abort": "Automatische Zählung während der Wartezeit pausiert: abgebrochen",
        "confirmed": "{reading}: {n} Ei(er): bestätigt, +{new} → {today} Ei(er) heute",
        "not_confirmed": "{reading}: {n} Ei(er): nicht bestätigt, nichts übernommen",
        "collect_confirmed": "Einsammeln bestätigt: {n} Ei(er) bleiben in den Nestern",
        "drop_not_confirmed": "{reading}: {n} Ei(er): Rückgang nicht bestätigt, {base} bleibt",
        "camera_unavailable": "{reading}: Kamera nicht verfügbar ({error})",
        "unchanged": "{reading}: Bild unverändert ({pct} der Pixel geändert), KI nicht abgefragt: {n} Ei(er)",
        "ai_retry": "{reading}: Die KI hat nicht geantwortet ({reason}), neuer Versuch in {s} s",
        "ai_failed": "{reading}: Die KI hat nicht geantwortet ({reason})",
        "hen_seen": "{reading}: {n} Ei(er) gesehen, ein Huhn sitzt auf einem Nest",
        "final_retry": "Abschlusszählung fehlgeschlagen: neuer Versuch in {min} min",
        "notify_failed": "Benachrichtigung {service} fehlgeschlagen: {error}",
        "corrected": "Korrektur: {date} = {n} Ei(er)",
        "collected": "Eier eingesammelt: {n} Ei(er) in den Nestern gelassen",
        "imported": "Verlauf importiert aus {entity}: {n} Tag(e)",
        "reason_overloaded": "KI-Dienst überlastet",
        "reason_quota": "KI-Kontingent erreicht",
        "reason_timeout": "keine Antwort in der Zeit",
        "reason_invalid": "unlesbare Antwort",
        "notify_one": "🥚 {name}: neues Ei! Heute insgesamt: {today}",
        "notify_many": "🥚 {name}: {new} neue Eier! Heute insgesamt: {today}",
        "task_name": "Eierzählung – {name}",
        "prompt": (
            "Dieses Bild stammt von einer Kamera, die {pondoirs} Legenest(er) eines Hühnerstalls filmt. "
            "Zähle die Gesamtzahl der in allen Legenestern sichtbaren Eier. "
            "Zähle nichts, was kein Ei ist (Stroh, Federn, Hobelspäne…). "
            "Gib außerdem an, ob ein Huhn in einem Legenest sitzt oder einen Teil eines Nests verdeckt."
        ),
        "field_eggs": "Gesamtzahl der in allen Legenestern sichtbaren Eier",
        "field_hen": "Sitzt ein Huhn in einem Legenest oder verdeckt es einen Teil eines Nests?",
    },
    "es": {
        "default_name": "Gallinero",
        "date_format": "%d/%m/%y",
        "source_auto": "automático",
        "source_final": "final",
        "source_manual": "manual",
        "source_retry": "nuevo intento del recuento final",
        "reading": "Lectura {r}",
        "cycle_start": "Inicio del recuento ({source})",
        "already_running": "Ya hay un recuento en curso: solicitud ignorada",
        "unexpected_error": "Error inesperado: {error}",
        "reading_failed": "{reading} fallida: nada validado",
        "init": "Inicialización: {n} huevo(s) ya en los nidos, no se cuentan como puestos hoy",
        "same": "{reading}: {n} huevo(s), igual que antes: nada nuevo",
        "hen_keep": "{reading}: {n} huevo(s) pero hay una gallina en un nido: se mantiene {base}",
        "rise_wait": "{reading}: {n} huevo(s) para {base} conocido(s): confirmación en {delay} min",
        "drop_wait": "{reading}: {n} huevo(s) para {base} conocido(s) (¿recogida?): confirmación en {delay} min",
        "paused_abort": "Recuento automático en pausa durante la espera: cancelado",
        "confirmed": "{reading}: {n} huevo(s): confirmado, +{new} → {today} huevo(s) hoy",
        "not_confirmed": "{reading}: {n} huevo(s): no confirmado, nada validado",
        "collect_confirmed": "Recogida confirmada: quedan {n} huevo(s) en los nidos",
        "drop_not_confirmed": "{reading}: {n} huevo(s): bajada no confirmada, se mantiene {base}",
        "camera_unavailable": "{reading}: cámara no disponible ({error})",
        "unchanged": "{reading}: imagen sin cambios ({pct} de píxeles modificados), IA no consultada: {n} huevo(s)",
        "ai_retry": "{reading}: la IA no respondió ({reason}), nuevo intento en {s} s",
        "ai_failed": "{reading}: la IA no respondió ({reason})",
        "hen_seen": "{reading}: {n} huevo(s) vistos, hay una gallina en un nido",
        "final_retry": "Recuento final fallido: nuevo intento en {min} min",
        "notify_failed": "Notificación {service} fallida: {error}",
        "corrected": "Corrección: {date} = {n} huevo(s)",
        "collected": "Huevos recogidos: {n} huevo(s) dejados en los nidos",
        "imported": "Historial importado desde {entity}: {n} día(s)",
        "reason_overloaded": "servicio de IA saturado",
        "reason_quota": "cuota de IA alcanzada",
        "reason_timeout": "sin respuesta a tiempo",
        "reason_invalid": "respuesta ilegible",
        "notify_one": "🥚 {name}: ¡nuevo huevo! Total hoy: {today}",
        "notify_many": "🥚 {name}: ¡{new} huevos nuevos! Total hoy: {today}",
        "task_name": "Recuento de huevos – {name}",
        "prompt": (
            "Esta imagen proviene de una cámara que graba {pondoirs} nido(s) de puesta de un gallinero. "
            "Cuenta el número total de huevos visibles en todos los nidos. "
            "No cuentes nada que no sea un huevo (paja, plumas, virutas…). "
            "Indica también si hay una gallina en un nido o si tapa una parte de un nido."
        ),
        "field_eggs": "Número total de huevos visibles en todos los nidos",
        "field_hen": "¿Hay una gallina en un nido o tapa una parte de un nido?",
    },
    "it": {
        "default_name": "Pollaio",
        "date_format": "%d/%m/%y",
        "source_auto": "automatico",
        "source_final": "finale",
        "source_manual": "manuale",
        "source_retry": "nuovo tentativo del conteggio finale",
        "reading": "Lettura {r}",
        "cycle_start": "Inizio del conteggio ({source})",
        "already_running": "Un conteggio è già in corso: richiesta ignorata",
        "unexpected_error": "Errore imprevisto: {error}",
        "reading_failed": "{reading} non riuscita: nulla convalidato",
        "init": "Inizializzazione: {n} uovo/a già nei nidi, non contate come deposte oggi",
        "same": "{reading}: {n} uovo/a, come prima: nulla di nuovo",
        "hen_keep": "{reading}: {n} uovo/a ma una gallina è su un nido: si mantiene {base}",
        "rise_wait": "{reading}: {n} uovo/a per {base} note: conferma tra {delay} min",
        "drop_wait": "{reading}: {n} uovo/a per {base} note (raccolta?): conferma tra {delay} min",
        "paused_abort": "Conteggio automatico in pausa durante l'attesa: annullato",
        "confirmed": "{reading}: {n} uovo/a: confermato, +{new} → {today} uovo/a oggi",
        "not_confirmed": "{reading}: {n} uovo/a: non confermato, nulla convalidato",
        "collect_confirmed": "Raccolta confermata: {n} uovo/a restano nei nidi",
        "drop_not_confirmed": "{reading}: {n} uovo/a: calo non confermato, si mantiene {base}",
        "camera_unavailable": "{reading}: telecamera non disponibile ({error})",
        "unchanged": "{reading}: immagine invariata ({pct} di pixel modificati), IA non interpellata: {n} uovo/a",
        "ai_retry": "{reading}: l'IA non ha risposto ({reason}), nuovo tentativo tra {s} s",
        "ai_failed": "{reading}: l'IA non ha risposto ({reason})",
        "hen_seen": "{reading}: {n} uovo/a viste, una gallina è su un nido",
        "final_retry": "Conteggio finale non riuscito: nuovo tentativo tra {min} min",
        "notify_failed": "Notifica {service} non riuscita: {error}",
        "corrected": "Correzione: {date} = {n} uovo/a",
        "collected": "Uova raccolte: {n} uovo/a lasciate nei nidi",
        "imported": "Cronologia importata da {entity}: {n} giorno/i",
        "reason_overloaded": "servizio IA sovraccarico",
        "reason_quota": "quota IA raggiunta",
        "reason_timeout": "nessuna risposta in tempo",
        "reason_invalid": "risposta illeggibile",
        "notify_one": "🥚 {name}: nuovo uovo! Totale oggi: {today}",
        "notify_many": "🥚 {name}: {new} nuove uova! Totale oggi: {today}",
        "task_name": "Conteggio uova – {name}",
        "prompt": (
            "Questa immagine proviene da una telecamera che riprende {pondoirs} nido/i di deposizione di un pollaio. "
            "Conta il numero totale di uova visibili in tutti i nidi. "
            "Non contare nulla che non sia un uovo (paglia, piume, trucioli…). "
            "Indica anche se una gallina è in un nido o ne copre una parte."
        ),
        "field_eggs": "Numero totale di uova visibili in tutti i nidi",
        "field_hen": "C'è una gallina in un nido o ne copre una parte?",
    },
    "nl": {
        "default_name": "Kippenhok",
        "date_format": "%d-%m-%y",
        "source_auto": "automatisch",
        "source_final": "laatste",
        "source_manual": "handmatig",
        "source_retry": "nieuwe poging van de laatste telling",
        "reading": "Meting {r}",
        "cycle_start": "Telling gestart ({source})",
        "already_running": "Er loopt al een telling: verzoek genegeerd",
        "unexpected_error": "Onverwachte fout: {error}",
        "reading_failed": "{reading} mislukt: niets bevestigd",
        "init": "Initialisatie: {n} ei(eren) al in de nesten, niet geteld als vandaag gelegd",
        "same": "{reading}: {n} ei(eren), zoals eerder: niets nieuws",
        "hen_keep": "{reading}: {n} ei(eren) maar er zit een kip op een nest: {base} blijft",
        "rise_wait": "{reading}: {n} ei(eren) bij {base} bekend: bevestiging over {delay} min",
        "drop_wait": "{reading}: {n} ei(eren) bij {base} bekend (geraapt?): bevestiging over {delay} min",
        "paused_abort": "Automatisch tellen gepauzeerd tijdens het wachten: geannuleerd",
        "confirmed": "{reading}: {n} ei(eren): bevestigd, +{new} → {today} ei(eren) vandaag",
        "not_confirmed": "{reading}: {n} ei(eren): niet bevestigd, niets bevestigd",
        "collect_confirmed": "Rapen bevestigd: {n} ei(eren) blijven in de nesten",
        "drop_not_confirmed": "{reading}: {n} ei(eren): daling niet bevestigd, {base} blijft",
        "camera_unavailable": "{reading}: camera niet beschikbaar ({error})",
        "unchanged": "{reading}: beeld ongewijzigd ({pct} van de pixels gewijzigd), AI niet gevraagd: {n} ei(eren)",
        "ai_retry": "{reading}: de AI antwoordde niet ({reason}), nieuwe poging over {s} s",
        "ai_failed": "{reading}: de AI antwoordde niet ({reason})",
        "hen_seen": "{reading}: {n} ei(eren) gezien, er zit een kip op een nest",
        "final_retry": "Laatste telling mislukt: nieuwe poging over {min} min",
        "notify_failed": "Melding {service} mislukt: {error}",
        "corrected": "Correctie: {date} = {n} ei(eren)",
        "collected": "Eieren geraapt: {n} ei(eren) in de nesten gelaten",
        "imported": "Geschiedenis geïmporteerd uit {entity}: {n} dag(en)",
        "reason_overloaded": "AI-dienst overbelast",
        "reason_quota": "AI-quotum bereikt",
        "reason_timeout": "geen antwoord op tijd",
        "reason_invalid": "onleesbaar antwoord",
        "notify_one": "🥚 {name}: nieuw ei! Totaal vandaag: {today}",
        "notify_many": "🥚 {name}: {new} nieuwe eieren! Totaal vandaag: {today}",
        "task_name": "Eieren tellen – {name}",
        "prompt": (
            "Deze afbeelding komt van een camera die {pondoirs} legnest(en) van een kippenhok filmt. "
            "Tel het totale aantal zichtbare eieren in alle legnesten. "
            "Tel niets wat geen ei is (stro, veren, houtkrullen…). "
            "Geef ook aan of er een kip in een legnest zit of een deel van een nest bedekt."
        ),
        "field_eggs": "Totaal aantal zichtbare eieren in alle legnesten",
        "field_hen": "Zit er een kip in een legnest of bedekt ze een deel van een nest?",
    },
    "pt": {
        "default_name": "Galinheiro",
        "date_format": "%d/%m/%y",
        "source_auto": "automática",
        "source_final": "final",
        "source_manual": "manual",
        "source_retry": "nova tentativa da contagem final",
        "reading": "Leitura {r}",
        "cycle_start": "Início da contagem ({source})",
        "already_running": "Já existe uma contagem em curso: pedido ignorado",
        "unexpected_error": "Erro inesperado: {error}",
        "reading_failed": "{reading} falhou: nada validado",
        "init": "Inicialização: {n} ovo(s) já nos ninhos, não contados como postos hoje",
        "same": "{reading}: {n} ovo(s), como antes: nada de novo",
        "hen_keep": "{reading}: {n} ovo(s) mas há uma galinha num ninho: mantém-se {base}",
        "rise_wait": "{reading}: {n} ovo(s) para {base} conhecido(s): confirmação em {delay} min",
        "drop_wait": "{reading}: {n} ovo(s) para {base} conhecido(s) (recolha?): confirmação em {delay} min",
        "paused_abort": "Contagem automática pausada durante a espera: cancelada",
        "confirmed": "{reading}: {n} ovo(s): confirmado, +{new} → {today} ovo(s) hoje",
        "not_confirmed": "{reading}: {n} ovo(s): não confirmado, nada validado",
        "collect_confirmed": "Recolha confirmada: ficam {n} ovo(s) nos ninhos",
        "drop_not_confirmed": "{reading}: {n} ovo(s): descida não confirmada, mantém-se {base}",
        "camera_unavailable": "{reading}: câmara indisponível ({error})",
        "unchanged": "{reading}: imagem inalterada ({pct} de píxeis alterados), IA não consultada: {n} ovo(s)",
        "ai_retry": "{reading}: a IA não respondeu ({reason}), nova tentativa em {s} s",
        "ai_failed": "{reading}: a IA não respondeu ({reason})",
        "hen_seen": "{reading}: {n} ovo(s) vistos, há uma galinha num ninho",
        "final_retry": "Contagem final falhou: nova tentativa em {min} min",
        "notify_failed": "Notificação {service} falhou: {error}",
        "corrected": "Correção: {date} = {n} ovo(s)",
        "collected": "Ovos recolhidos: {n} ovo(s) deixados nos ninhos",
        "imported": "Histórico importado de {entity}: {n} dia(s)",
        "reason_overloaded": "serviço de IA sobrecarregado",
        "reason_quota": "quota de IA atingida",
        "reason_timeout": "sem resposta a tempo",
        "reason_invalid": "resposta ilegível",
        "notify_one": "🥚 {name}: novo ovo! Total hoje: {today}",
        "notify_many": "🥚 {name}: {new} novos ovos! Total hoje: {today}",
        "task_name": "Contagem de ovos – {name}",
        "prompt": (
            "Esta imagem vem de uma câmara que filma {pondoirs} ninho(s) de postura de um galinheiro. "
            "Conta o número total de ovos visíveis em todos os ninhos. "
            "Não contes nada que não seja um ovo (palha, penas, aparas…). "
            "Indica também se há uma galinha num ninho ou se ela tapa parte de um ninho."
        ),
        "field_eggs": "Número total de ovos visíveis em todos os ninhos",
        "field_hen": "Há uma galinha num ninho ou ela tapa parte de um ninho?",
    },
}

LANGUAGES = tuple(TEXTS)


def lang_of(language: str | None) -> str:
    """'fr', 'pt-BR', 'en_GB'… → supported base language (English otherwise)."""
    base = (language or FALLBACK).replace("_", "-").split("-")[0].lower()
    return base if base in TEXTS else FALLBACK


def text(language: str | None, key: str, **params: Any) -> str:
    """Translated text with its placeholders filled in (never raises)."""
    lang = lang_of(language)
    template = TEXTS[lang].get(key) or TEXTS[FALLBACK].get(key) or key
    params = {k: _localise(lang, v) for k, v in params.items()}
    try:
        return template.format(**params)
    except (KeyError, IndexError, ValueError):
        return template


def _localise(lang: str, value: Any) -> Any:
    if isinstance(value, dict) and "key" in value:  # nested translated text
        return text(lang, value["key"], **value.get("params", {}))
    if isinstance(value, date):
        return value.strftime(TEXTS[lang]["date_format"])
    if isinstance(value, float):
        return f"{value:.1%}"
    return value


def render_line(language: str | None, line: Any) -> str:
    """Journal line → text. Lines from 1.0.x were stored as plain strings."""
    if isinstance(line, str):
        return line
    params = dict(line.get("p", {}))
    if "date" in params and isinstance(params["date"], str):
        try:
            params["date"] = date.fromisoformat(params["date"])
        except ValueError:
            pass
    marker = "▶ " if line.get("c") else ""
    return f"{line.get('t', '')} {marker}{text(language, line['k'], **params)}"
