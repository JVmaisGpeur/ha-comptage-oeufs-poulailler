/*
 * Lovelace card « Comptage Œufs Poulailler » (Chicken Coop Egg Counter)
 * Shipped and loaded automatically by the comptage_oeufs_poulailler integration.
 * MIT License – JVmaisGpeur
 */
const DOMAIN = "comptage_oeufs_poulailler";
const CARD_VERSION = "1.1.0";

const DEFAULTS = {
  // language: "en", // force a language (default: the user's Home Assistant language)
  days: 14, // barres du graphique
  history_days: 60, // lignes de l'historique
  events: 12, // photos d'événements affichées
  show_live_camera: false, // true = flux caméra (réveille une caméra sur batterie)
  show_camera: true,
  show_journal: true,
  show_chart: true,
  show_history: true,
  show_photos: true,
  show_settings: true,
};

const esc = (s) =>
  String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);

const iso = (d) =>
  `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;

const parseIso = (s) => {
  const [y, m, d] = s.split("-").map(Number);
  return new Date(y, m - 1, d, 12);
};


// ---------------------------------------------------------------- translations
// Add a language: copy the "en" block, translate the values, keep {placeholders}.
const I18N = {
  en: {
    loading: "Loading…", error_hint: "Is the “Comptage Œufs Poulailler” integration configured?",
    status_counting: "⏳ Counting", status_paused: "⏸ Paused",
    eggs_today_one: "egg laid today", eggs_today_other: "eggs laid today",
    in_nests: "in the nests", yesterday: "yesterday", days7: "7 days", this_month: "this month",
    count_now: "📷 Count now", collect: "🧺 Eggs collected", confirm: "Confirm?", pause: "⏸ Pause", resume: "▶ Resume",
    count_started: "Count started…", invalid_number: "Invalid number", choose_date: "Choose a date and a number",
    camera: "Camera", no_photo_yet: "No photo analysed yet.", last_photo: "Last analysed photo",
    last_analysis: "Last analysis {time} · {n} egg(s)", hen_on_nest: "🐔 hen on a nest",
    per_day: "Eggs per day", average: "average {mean}/day over {n} d", today: "today",
    save: "Save", cancel: "Cancel", edit: "Correct", in_progress: "(in progress)",
    history: "📅 History", year_total: "{year} this year · {total} total", no_history: "No history",
    correct_other: "Correct another day:", eggs_ph: "eggs", apply: "Apply",
    ev_confirme: "New egg confirmed", ev_rejete: "Rise not confirmed", ev_ramassage: "Collection detected",
    reading: "Reading {n}", nests: "nests", no_photo: "No photo",
    photos: "🖼️ Detection photos", recent: "{n} recent", photos_empty: "Photos of new eggs (and of unconfirmed readings) will appear here.",
    settings: "⚙️ Settings", start: "Counting starts", end: "Counting ends", every: "Count every (min)", delay: "Delay before the 2nd reading (min)",
    settings_hint: "Camera, AI, notification, AI instructions and photo retention: Settings › Devices & services › Comptage Œufs Poulailler › Configure.",
    card_desc: "Egg counter, editable history, chart and detection photos.",
  },
  fr: {
    loading: "Chargement…", error_hint: "L'intégration « Comptage Œufs Poulailler » est-elle configurée ?",
    status_counting: "⏳ Comptage en cours", status_paused: "⏸ En pause",
    eggs_today_one: "œuf pondu aujourd'hui", eggs_today_other: "œufs pondus aujourd'hui",
    in_nests: "dans les pondoirs", yesterday: "hier", days7: "7 jours", this_month: "ce mois",
    count_now: "📷 Compter maintenant", collect: "🧺 Œufs ramassés", confirm: "Confirmer ?", pause: "⏸ Pause", resume: "▶ Reprendre",
    count_started: "Comptage lancé…", invalid_number: "Nombre invalide", choose_date: "Choisissez une date et un nombre",
    camera: "Caméra", no_photo_yet: "Aucune photo analysée pour l'instant.", last_photo: "Dernière photo analysée",
    last_analysis: "Dernière analyse {time} · {n} œuf(s)", hen_on_nest: "🐔 poule sur un nid",
    per_day: "Œufs par jour", average: "moyenne {mean}/jour sur {n} j", today: "aujourd'hui",
    save: "Enregistrer", cancel: "Annuler", edit: "Corriger", in_progress: "(en cours)",
    history: "📅 Historique", year_total: "{year} cette année · {total} au total", no_history: "Aucun historique",
    correct_other: "Corriger un autre jour :", eggs_ph: "œufs", apply: "Appliquer",
    ev_confirme: "Nouvel œuf confirmé", ev_rejete: "Hausse non confirmée", ev_ramassage: "Ramassage détecté",
    reading: "Lecture {n}", nests: "pondoirs", no_photo: "Pas de photo",
    photos: "🖼️ Photos des détections", recent: "{n} récente(s)", photos_empty: "Les photos des nouveaux œufs (et des lectures non confirmées) apparaîtront ici.",
    settings: "⚙️ Réglages", start: "Début du comptage", end: "Fin du comptage", every: "Comptage toutes les (min)", delay: "Délai avant la 2ᵉ lecture (min)",
    settings_hint: "Caméra, IA, notification, consigne et conservation des photos : Paramètres › Appareils et services › Comptage Œufs Poulailler › Configurer.",
    card_desc: "Compteur d'œufs, historique corrigeable, graphique et photos des détections.",
  },
  de: {
    loading: "Wird geladen…", error_hint: "Ist die Integration „Comptage Œufs Poulailler“ eingerichtet?",
    status_counting: "⏳ Zählung läuft", status_paused: "⏸ Pausiert",
    eggs_today_one: "Ei heute gelegt", eggs_today_other: "Eier heute gelegt",
    in_nests: "in den Nestern", yesterday: "gestern", days7: "7 Tage", this_month: "diesen Monat",
    count_now: "📷 Jetzt zählen", collect: "🧺 Eier eingesammelt", confirm: "Bestätigen?", pause: "⏸ Pause", resume: "▶ Fortsetzen",
    count_started: "Zählung gestartet…", invalid_number: "Ungültige Zahl", choose_date: "Datum und Anzahl wählen",
    camera: "Kamera", no_photo_yet: "Noch kein Foto analysiert.", last_photo: "Zuletzt analysiertes Foto",
    last_analysis: "Letzte Analyse {time} · {n} Ei(er)", hen_on_nest: "🐔 Huhn auf einem Nest",
    per_day: "Eier pro Tag", average: "Durchschnitt {mean}/Tag über {n} T.", today: "heute",
    save: "Speichern", cancel: "Abbrechen", edit: "Korrigieren", in_progress: "(läuft)",
    history: "📅 Verlauf", year_total: "{year} dieses Jahr · {total} insgesamt", no_history: "Kein Verlauf",
    correct_other: "Anderen Tag korrigieren:", eggs_ph: "Eier", apply: "Übernehmen",
    ev_confirme: "Neues Ei bestätigt", ev_rejete: "Anstieg nicht bestätigt", ev_ramassage: "Einsammeln erkannt",
    reading: "Messung {n}", nests: "Nester", no_photo: "Kein Foto",
    photos: "🖼️ Erkennungsfotos", recent: "{n} neueste", photos_empty: "Fotos neuer Eier (und nicht bestätigter Messungen) erscheinen hier.",
    settings: "⚙️ Einstellungen", start: "Beginn der Zählung", end: "Ende der Zählung", every: "Zählen alle (min)", delay: "Wartezeit vor der 2. Messung (min)",
    settings_hint: "Kamera, KI, Benachrichtigung, KI-Anweisung und Fotoaufbewahrung: Einstellungen › Geräte & Dienste › Comptage Œufs Poulailler › Konfigurieren.",
    card_desc: "Eierzähler, korrigierbarer Verlauf, Diagramm und Erkennungsfotos.",
  },
  es: {
    loading: "Cargando…", error_hint: "¿Está configurada la integración «Comptage Œufs Poulailler»?",
    status_counting: "⏳ Contando", status_paused: "⏸ En pausa",
    eggs_today_one: "huevo puesto hoy", eggs_today_other: "huevos puestos hoy",
    in_nests: "en los nidos", yesterday: "ayer", days7: "7 días", this_month: "este mes",
    count_now: "📷 Contar ahora", collect: "🧺 Huevos recogidos", confirm: "¿Confirmar?", pause: "⏸ Pausa", resume: "▶ Reanudar",
    count_started: "Recuento iniciado…", invalid_number: "Número no válido", choose_date: "Elige una fecha y un número",
    camera: "Cámara", no_photo_yet: "Aún no se ha analizado ninguna foto.", last_photo: "Última foto analizada",
    last_analysis: "Último análisis {time} · {n} huevo(s)", hen_on_nest: "🐔 gallina en un nido",
    per_day: "Huevos por día", average: "media {mean}/día en {n} d", today: "hoy",
    save: "Guardar", cancel: "Cancelar", edit: "Corregir", in_progress: "(en curso)",
    history: "📅 Historial", year_total: "{year} este año · {total} en total", no_history: "Sin historial",
    correct_other: "Corregir otro día:", eggs_ph: "huevos", apply: "Aplicar",
    ev_confirme: "Nuevo huevo confirmado", ev_rejete: "Subida no confirmada", ev_ramassage: "Recogida detectada",
    reading: "Lectura {n}", nests: "nidos", no_photo: "Sin foto",
    photos: "🖼️ Fotos de detecciones", recent: "{n} reciente(s)", photos_empty: "Aquí aparecerán las fotos de los huevos nuevos (y de las lecturas no confirmadas).",
    settings: "⚙️ Ajustes", start: "Inicio del recuento", end: "Fin del recuento", every: "Contar cada (min)", delay: "Espera antes de la 2.ª lectura (min)",
    settings_hint: "Cámara, IA, notificación, instrucciones y conservación de fotos: Ajustes › Dispositivos y servicios › Comptage Œufs Poulailler › Configurar.",
    card_desc: "Contador de huevos, historial editable, gráfico y fotos de detecciones.",
  },
  it: {
    loading: "Caricamento…", error_hint: "L'integrazione «Comptage Œufs Poulailler» è configurata?",
    status_counting: "⏳ Conteggio in corso", status_paused: "⏸ In pausa",
    eggs_today_one: "uovo deposto oggi", eggs_today_other: "uova deposte oggi",
    in_nests: "nei nidi", yesterday: "ieri", days7: "7 giorni", this_month: "questo mese",
    count_now: "📷 Conta ora", collect: "🧺 Uova raccolte", confirm: "Confermare?", pause: "⏸ Pausa", resume: "▶ Riprendi",
    count_started: "Conteggio avviato…", invalid_number: "Numero non valido", choose_date: "Scegli una data e un numero",
    camera: "Telecamera", no_photo_yet: "Nessuna foto analizzata per ora.", last_photo: "Ultima foto analizzata",
    last_analysis: "Ultima analisi {time} · {n} uovo/a", hen_on_nest: "🐔 gallina su un nido",
    per_day: "Uova al giorno", average: "media {mean}/giorno su {n} g", today: "oggi",
    save: "Salva", cancel: "Annulla", edit: "Correggi", in_progress: "(in corso)",
    history: "📅 Cronologia", year_total: "{year} quest'anno · {total} in totale", no_history: "Nessuna cronologia",
    correct_other: "Correggi un altro giorno:", eggs_ph: "uova", apply: "Applica",
    ev_confirme: "Nuovo uovo confermato", ev_rejete: "Aumento non confermato", ev_ramassage: "Raccolta rilevata",
    reading: "Lettura {n}", nests: "nidi", no_photo: "Nessuna foto",
    photos: "🖼️ Foto dei rilevamenti", recent: "{n} recenti", photos_empty: "Qui appariranno le foto delle nuove uova (e delle letture non confermate).",
    settings: "⚙️ Impostazioni", start: "Inizio del conteggio", end: "Fine del conteggio", every: "Conta ogni (min)", delay: "Attesa prima della 2ª lettura (min)",
    settings_hint: "Telecamera, IA, notifica, istruzioni e conservazione delle foto: Impostazioni › Dispositivi e servizi › Comptage Œufs Poulailler › Configura.",
    card_desc: "Contatore di uova, cronologia modificabile, grafico e foto dei rilevamenti.",
  },
  nl: {
    loading: "Laden…", error_hint: "Is de integratie ‘Comptage Œufs Poulailler’ ingesteld?",
    status_counting: "⏳ Bezig met tellen", status_paused: "⏸ Gepauzeerd",
    eggs_today_one: "ei vandaag gelegd", eggs_today_other: "eieren vandaag gelegd",
    in_nests: "in de nesten", yesterday: "gisteren", days7: "7 dagen", this_month: "deze maand",
    count_now: "📷 Nu tellen", collect: "🧺 Eieren geraapt", confirm: "Bevestigen?", pause: "⏸ Pauze", resume: "▶ Hervatten",
    count_started: "Telling gestart…", invalid_number: "Ongeldig getal", choose_date: "Kies een datum en een aantal",
    camera: "Camera", no_photo_yet: "Nog geen foto geanalyseerd.", last_photo: "Laatst geanalyseerde foto",
    last_analysis: "Laatste analyse {time} · {n} ei(eren)", hen_on_nest: "🐔 kip op een nest",
    per_day: "Eieren per dag", average: "gemiddeld {mean}/dag over {n} d", today: "vandaag",
    save: "Opslaan", cancel: "Annuleren", edit: "Corrigeren", in_progress: "(bezig)",
    history: "📅 Geschiedenis", year_total: "{year} dit jaar · {total} totaal", no_history: "Geen geschiedenis",
    correct_other: "Andere dag corrigeren:", eggs_ph: "eieren", apply: "Toepassen",
    ev_confirme: "Nieuw ei bevestigd", ev_rejete: "Stijging niet bevestigd", ev_ramassage: "Rapen gedetecteerd",
    reading: "Meting {n}", nests: "nesten", no_photo: "Geen foto",
    photos: "🖼️ Detectiefoto's", recent: "{n} recent", photos_empty: "Foto's van nieuwe eieren (en van niet-bevestigde metingen) verschijnen hier.",
    settings: "⚙️ Instellingen", start: "Start van de telling", end: "Einde van de telling", every: "Tellen elke (min)", delay: "Wachttijd vóór de 2e meting (min)",
    settings_hint: "Camera, AI, melding, AI-instructies en bewaartermijn van foto's: Instellingen › Apparaten & diensten › Comptage Œufs Poulailler › Configureren.",
    card_desc: "Eierteller, aanpasbare geschiedenis, grafiek en detectiefoto's.",
  },
  pt: {
    loading: "A carregar…", error_hint: "A integração «Comptage Œufs Poulailler» está configurada?",
    status_counting: "⏳ A contar", status_paused: "⏸ Em pausa",
    eggs_today_one: "ovo posto hoje", eggs_today_other: "ovos postos hoje",
    in_nests: "nos ninhos", yesterday: "ontem", days7: "7 dias", this_month: "este mês",
    count_now: "📷 Contar agora", collect: "🧺 Ovos recolhidos", confirm: "Confirmar?", pause: "⏸ Pausa", resume: "▶ Retomar",
    count_started: "Contagem iniciada…", invalid_number: "Número inválido", choose_date: "Escolha uma data e um número",
    camera: "Câmara", no_photo_yet: "Ainda nenhuma foto analisada.", last_photo: "Última foto analisada",
    last_analysis: "Última análise {time} · {n} ovo(s)", hen_on_nest: "🐔 galinha num ninho",
    per_day: "Ovos por dia", average: "média {mean}/dia em {n} d", today: "hoje",
    save: "Guardar", cancel: "Cancelar", edit: "Corrigir", in_progress: "(em curso)",
    history: "📅 Histórico", year_total: "{year} este ano · {total} no total", no_history: "Sem histórico",
    correct_other: "Corrigir outro dia:", eggs_ph: "ovos", apply: "Aplicar",
    ev_confirme: "Novo ovo confirmado", ev_rejete: "Subida não confirmada", ev_ramassage: "Recolha detetada",
    reading: "Leitura {n}", nests: "ninhos", no_photo: "Sem foto",
    photos: "🖼️ Fotos das deteções", recent: "{n} recente(s)", photos_empty: "As fotos dos ovos novos (e das leituras não confirmadas) aparecerão aqui.",
    settings: "⚙️ Definições", start: "Início da contagem", end: "Fim da contagem", every: "Contar a cada (min)", delay: "Espera antes da 2.ª leitura (min)",
    settings_hint: "Câmara, IA, notificação, instruções e conservação das fotos: Definições › Dispositivos e serviços › Comptage Œufs Poulailler › Configurar.",
    card_desc: "Contador de ovos, histórico editável, gráfico e fotos das deteções.",
  },
};

const langOf = (lang) => {
  const base = String(lang || "en").toLowerCase().split(/[-_]/)[0];
  return I18N[base] ? base : "en";
};

const translate = (lang, key, params = {}) => {
  const template = I18N[langOf(lang)][key] ?? I18N.en[key] ?? key;
  return template.replace(/\{(\w+)\}/g, (m, k) => (k in params ? params[k] : m));
};

const EVENT_STYLES = { confirme: ["✅", "ok"], rejete: ["❌", "ko"], ramassage: ["🧺", "info"] };

class ComptageOeufsPoulaillerCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._data = null;
    this._error = null;
    this._open = new Set(["history"]);
    this._editing = null;
    this._confirmCollect = false;
    this._pending = false;
    this._watchKey = "";
    this._fetching = false;
    this._timer = null;
    this.shadowRoot.addEventListener("click", (ev) => this._onClick(ev));
    this.shadowRoot.addEventListener("change", (ev) => this._onChange(ev));
    this.shadowRoot.addEventListener("keydown", (ev) => {
      if (ev.key === "Enter" && ev.target.dataset.enter) {
        this._run(ev.target.dataset.enter, ev.target);
      }
    });
    this.shadowRoot.addEventListener("focusout", () =>
      setTimeout(() => {
        if (this._pending && !this._hasFocus()) this._render();
      }, 150)
    );
    this.shadowRoot.addEventListener(
      "toggle",
      (ev) => {
        const id = ev.target.dataset?.section;
        if (!id) return;
        ev.target.open ? this._open.add(id) : this._open.delete(id);
      },
      true
    );
  }

  static getStubConfig() {
    return {};
  }

  setConfig(config) {
    this._config = { ...DEFAULTS, ...(config || {}) };
    this._data = null;
    if (this._hass) this._fetch();
  }

  getCardSize() {
    return 14;
  }

  getGridOptions() {
    return { columns: 12, min_columns: 6 };
  }

  connectedCallback() {
    this._timer = setInterval(() => this._fetch(), 5 * 60 * 1000);
  }

  disconnectedCallback() {
    clearInterval(this._timer);
  }

  set hass(hass) {
    const first = !this._hass;
    this._hass = hass;
    if (first || !this._data) {
      if (!this._fetching && !this._error) this._fetch();
      return;
    }
    const ids = Object.values(this._data.entities || {});
    const key = ids.map((id) => hass.states[id]?.last_updated || "").join("|");
    if (key !== this._watchKey) {
      this._watchKey = key;
      clearTimeout(this._debounce);
      this._debounce = setTimeout(() => this._fetch(), 400);
    } else if (this._config.show_live_camera && this._config.show_camera) {
      const img = this.shadowRoot.querySelector("img.photo.live");
      const src = hass.states[this._data.camera]?.attributes?.entity_picture;
      if (img && src && img.dataset.src !== src) {
        img.dataset.src = src;
        img.src = src;
      }
    }
  }

  async _fetch() {
    if (!this._hass || this._fetching) return;
    this._fetching = true;
    try {
      const msg = {
        type: `${DOMAIN}/data`,
        days: Math.max(this._config.days, this._config.history_days),
        events: this._config.events,
        language: this._lang,
      };
      if (this._config.entry_id) msg.entry_id = this._config.entry_id;
      this._data = await this._hass.callWS(msg);
      this._error = null;
      const ids = Object.values(this._data.entities || {});
      this._watchKey = ids.map((id) => this._hass.states[id]?.last_updated || "").join("|");
    } catch (err) {
      this._error = err?.message || String(err);
    } finally {
      this._fetching = false;
    }
    this._render();
  }

  _hasFocus() {
    const el = this.shadowRoot.activeElement;
    return el && ["INPUT", "SELECT", "TEXTAREA"].includes(el.tagName);
  }

  get _lang() {
    return langOf(this._config?.language || this._hass?.locale?.language || this._hass?.language);
  }

  _t(key, params) {
    return translate(this._lang, key, params);
  }

  _entity(key) {
    return this._data?.entities?.[key];
  }

  _service(domain, service, data) {
    return this._hass.callService(domain, service, data).catch((err) => this._toast(err?.message || String(err)));
  }

  _toast(message) {
    this.dispatchEvent(new CustomEvent("hass-notification", { detail: { message }, bubbles: true, composed: true }));
  }

  // ------------------------------------------------------------------ actions
  _onClick(ev) {
    const el = ev.target.closest("[data-action]");
    if (!el) return;
    this._run(el.dataset.action, el);
  }

  _run(action, el) {
    const entry = { config_entry_id: this._data.entry_id };
    switch (action) {
      case "count":
        this._service(DOMAIN, "compter_maintenant", entry);
        this._toast(this._t("count_started"));
        break;
      case "collect":
        if (!this._confirmCollect) {
          this._confirmCollect = true;
          this._render();
          setTimeout(() => {
            this._confirmCollect = false;
            this._render();
          }, 4000);
          return;
        }
        this._confirmCollect = false;
        this._service(DOMAIN, "oeufs_ramasses", { ...entry, restants: 0 });
        break;
      case "toggle-auto": {
        const id = this._entity("comptage_automatique");
        if (id) this._service("switch", this._data.auto ? "turn_off" : "turn_on", { entity_id: id });
        break;
      }
      case "edit":
        this._editing = el.dataset.date;
        this._render();
        this.shadowRoot.querySelector("input.edit")?.focus();
        break;
      case "cancel":
        this._editing = null;
        this._render();
        break;
      case "save": {
        const input = this.shadowRoot.querySelector("input.edit");
        const n = parseInt(input?.value, 10);
        if (Number.isNaN(n) || n < 0) return this._toast(this._t("invalid_number"));
        this._service(DOMAIN, "corriger", { ...entry, date: this._editing, nombre: n });
        this._editing = null;
        break;
      }
      case "correct": {
        const date = this.shadowRoot.querySelector("#corr-date")?.value;
        const n = parseInt(this.shadowRoot.querySelector("#corr-n")?.value, 10);
        if (!date || Number.isNaN(n) || n < 0) return this._toast(this._t("choose_date"));
        this._service(DOMAIN, "corriger", { ...entry, date, nombre: n });
        break;
      }
      case "zoom": {
        const box = this.shadowRoot.querySelector(".lightbox");
        box.querySelector("img").src = el.dataset.src;
        box.querySelector(".caption").textContent = el.dataset.caption || "";
        box.hidden = false;
        break;
      }
      case "close-zoom":
        this.shadowRoot.querySelector(".lightbox").hidden = true;
        break;
    }
  }

  _onChange(ev) {
    const el = ev.target;
    const setting = el.dataset.setting;
    if (!setting) return;
    const id = this._entity(setting);
    if (!id) return;
    if (el.type === "time") {
      if (el.value) this._service("time", "set_value", { entity_id: id, time: `${el.value}:00` });
    } else {
      const v = Number(el.value);
      if (!Number.isNaN(v)) this._service("number", "set_value", { entity_id: id, value: v });
    }
  }

  // ------------------------------------------------------------------ rendu
  _fmtDate(isoDate, opts) {
    const lang = this._config?.language || this._hass?.locale?.language || this._hass?.language || "en";
    return parseIso(isoDate).toLocaleDateString(lang, opts);
  }

  _fmtTime(isoDateTime) {
    if (!isoDateTime) return "";
    const lang = this._config?.language || this._hass?.locale?.language || "en";
    const d = new Date(isoDateTime);
    const sameDay = iso(d) === this._data.today_date;
    return sameDay
      ? d.toLocaleTimeString(lang, { hour: "2-digit", minute: "2-digit" })
      : d.toLocaleString(lang, { day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit" });
  }

  _render() {
    if (!this._config) return;
    if (this._hasFocus()) {
      this._pending = true;
      return;
    }
    this._pending = false;
    const c = this._config;
    let body;
    if (this._error) {
      body = `<div class="empty">⚠️ ${esc(this._error)}<br><small>${esc(this._t("error_hint"))}</small></div>`;
    } else if (!this._data) {
      body = `<div class="empty">${this._t("loading")}</div>`;
    } else {
      body = [
        this._renderHero(),
        c.show_camera ? this._renderPhoto() : "",
        c.show_journal ? this._renderJournal() : "",
        c.show_chart ? this._renderChart() : "",
        c.show_history ? this._renderHistory() : "",
        c.show_photos ? this._renderEvents() : "",
        c.show_settings ? this._renderSettings() : "",
      ].join("");
    }
    this.shadowRoot.innerHTML = `<style>${STYLE}</style><ha-card>${body}</ha-card>
      <div class="lightbox" hidden data-action="close-zoom"><img alt=""><div class="caption"></div></div>`;
  }

  _renderHero() {
    const d = this._data;
    const s = d.stats || {};
    const title = this._config.title ?? d.title;
    const status = d.counting
      ? `<span class="chip busy">${this._t("status_counting")}</span>`
      : d.auto
        ? `<span class="chip on">● Auto ${esc(d.settings.start.slice(0, 5))}–${esc(d.settings.end.slice(0, 5))}</span>`
        : `<span class="chip off">${this._t("status_paused")}</span>`;
    return `
      <div class="head"><div class="title">🥚 ${esc(title)}</div>${status}</div>
      <div class="hero">
        <div class="big">${d.today}</div>
        <div class="big-label">${this._t(d.today === 1 ? "eggs_today_one" : "eggs_today_other")}</div>
        <div class="kpis">
          <div><b>${d.baseline ?? "–"}</b><span>${this._t("in_nests")}</span></div>
          <div><b>${s.hier ?? 0}</b><span>${this._t("yesterday")}</span></div>
          <div><b>${s["7_jours"] ?? 0}</b><span>${this._t("days7")}</span></div>
          <div><b>${s.ce_mois ?? 0}</b><span>${this._t("this_month")}</span></div>
        </div>
      </div>
      <div class="actions">
        <button class="primary" data-action="count" ${d.counting ? "disabled" : ""}>${this._t("count_now")}</button>
        <button class="${this._confirmCollect ? "warn" : ""}" data-action="collect">${this._t(this._confirmCollect ? "confirm" : "collect")}</button>
        <button data-action="toggle-auto">${this._t(d.auto ? "pause" : "resume")}</button>
      </div>`;
  }

  _renderPhoto() {
    const d = this._data;
    const last = d.last_reading || {};
    if (this._config.show_live_camera) {
      const src = this._hass.states[d.camera]?.attributes?.entity_picture;
      return src ? `<img class="photo live" data-src="${esc(src)}" src="${esc(src)}" alt="${esc(this._t("camera"))}">` : "";
    }
    if (!d.last_image_url) return `<div class="empty small">${this._t("no_photo_yet")}</div>`;
    const cap = this._t("last_analysis", { time: this._fmtTime(last.time), n: last.eggs }) + (last.hen ? ` · ${this._t("hen_on_nest")}` : "");
    return `<figure>
        <img class="photo" src="${esc(d.last_image_url)}" alt="${esc(this._t("last_photo"))}" data-action="zoom" data-src="${esc(d.last_image_url)}" data-caption="${esc(cap)}">
        <figcaption>${esc(cap)}</figcaption></figure>`;
  }

  _renderJournal() {
    const lines = (this._data.journal || []).slice(-8);
    if (!lines.length) return "";
    return `<div class="journal">${lines.map((l) => `<div class="${l.includes("▶") ? "start" : ""}">${esc(l)}</div>`).join("")}</div>`;
  }

  _renderChart() {
    const d = this._data;
    const n = this._config.days;
    const map = Object.fromEntries(d.history.map((h) => [h.date, h.count]));
    const today = parseIso(d.today_date);
    const days = [];
    for (let i = n - 1; i >= 0; i--) {
      const day = new Date(today);
      day.setDate(day.getDate() - i);
      const key = iso(day);
      days.push({ key, day, value: key === d.today_date ? d.today : (map[key] ?? null) });
    }
    const max = Math.max(1, ...days.map((x) => x.value || 0));
    const W = 28;
    const H = 110;
    const top = 16;
    const bars = days
      .map((x, i) => {
        const v = x.value || 0;
        const h = (v / max) * H;
        const xPos = i * W + 4;
        const isToday = x.key === d.today_date;
        const label = x.value == null ? "" : String(v);
        const dom = x.day.getDate();
        return `<g>
          <title>${esc(this._fmtDate(x.key, { weekday: "long", day: "numeric", month: "long" }))} : ${x.value ?? "–"}</title>
          <rect x="${xPos}" y="${top + H - h}" width="${W - 8}" height="${Math.max(h, v ? 2 : 0)}" rx="4" class="${isToday ? "bar today" : "bar"}"/>
          <text x="${xPos + (W - 8) / 2}" y="${top + H - h - 4}" class="val">${label}</text>
          <text x="${xPos + (W - 8) / 2}" y="${top + H + 14}" class="day ${dom === 1 ? "month" : ""}">${dom}</text>
        </g>`;
      })
      .join("");
    const avg = days.filter((x) => x.key !== d.today_date && x.value != null);
    const mean = avg.length ? (avg.reduce((a, x) => a + x.value, 0) / avg.length).toFixed(1) : "–";
    return `<div class="section">
        <div class="section-title">${this._t("per_day")} <small>${this._t("average", { mean, n: avg.length })} · <span class="dot today"></span> ${this._t("today")}</small></div>
        <svg viewBox="0 0 ${n * W} ${top + H + 20}" preserveAspectRatio="xMidYMid meet">${bars}</svg>
      </div>`;
  }

  _renderHistory() {
    const d = this._data;
    const rows = [...d.history]
      .sort((a, b) => (a.date < b.date ? 1 : -1))
      .slice(0, this._config.history_days)
      .map((h) => {
        const label = this._fmtDate(h.date, { weekday: "short", day: "2-digit", month: "2-digit", year: "2-digit" });
        const isToday = h.date === d.today_date;
        const count = isToday ? d.today : h.count;
        if (this._editing === h.date) {
          return `<tr class="editing"><td>${esc(label)}</td><td class="num">
              <input class="edit" type="number" min="0" max="999" value="${count}" data-enter="save">
              <button class="icon" data-action="save" title="${esc(this._t("save"))}">✓</button>
              <button class="icon" data-action="cancel" title="${esc(this._t("cancel"))}">✕</button></td></tr>`;
        }
        return `<tr class="${isToday ? "today" : ""}"><td>${esc(label)}${isToday ? ` <em>${this._t("in_progress")}</em>` : ""}</td>
            <td class="num">${count}<button class="icon ghost" data-action="edit" data-date="${h.date}" title="${esc(this._t("edit"))}">✏️</button></td></tr>`;
      })
      .join("");
    const s = d.stats || {};
    return `<details class="section" data-section="history" ${this._open.has("history") ? "open" : ""}>
        <summary>${this._t("history")} <small>${this._t("year_total", { year: s.cette_annee ?? 0, total: s.total ?? 0 })}</small></summary>
        <div class="scroll"><table>${rows || `<tr><td>${this._t("no_history")}</td></tr>`}</table></div>
        <div class="correct">
          <span>${this._t("correct_other")}</span>
          <input id="corr-date" type="date" max="${d.today_date}">
          <input id="corr-n" type="number" min="0" max="999" placeholder="${esc(this._t("eggs_ph"))}" data-enter="correct">
          <button data-action="correct">${this._t("apply")}</button>
        </div>
      </details>`;
  }

  _renderEvents() {
    const events = this._data.events || [];
    const items = events
      .map((e) => {
        const [icon, cls] = EVENT_STYLES[e.type] || ["•", ""];
        const label = this._t(`ev_${e.type}`);
        const r1 = this._t("reading", { n: 1 });
        const r2 = this._t("reading", { n: 2 });
        const when = this._fmtTime(e.time);
        const detail = `${r1}: ${e.lecture1}${e.poule1 ? " 🐔" : ""} · ${r2}: ${e.lecture2}${e.poule2 ? " 🐔" : ""} · ${this._t("nests")} ${e.avant} → ${e.apres}`;
        const imgs = (e.urls || [])
          .filter(Boolean)
          .map(
            (u, i) =>
              `<img loading="lazy" src="${esc(u)}" alt="${esc(i ? r2 : r1)}" data-action="zoom" data-src="${esc(u)}" data-caption="${esc(`${when} – ${label} – ${i ? r2 : r1}`)}">`
          )
          .join("");
        return `<div class="event ${cls}">
            <div class="event-head"><span>${icon} ${esc(label)}</span><small>${esc(when)}</small></div>
            <div class="event-detail">${esc(detail)}</div>
            <div class="thumbs">${imgs || `<small>${this._t("no_photo")}</small>`}</div>
          </div>`;
      })
      .join("");
    return `<details class="section" data-section="photos" ${this._open.has("photos") ? "open" : ""}>
        <summary>${this._t("photos")} <small>${this._t("recent", { n: events.length })}</small></summary>
        ${items || `<div class="empty small">${this._t("photos_empty")}</div>`}
      </details>`;
  }

  _renderSettings() {
    const s = this._data.settings;
    return `<details class="section" data-section="settings" ${this._open.has("settings") ? "open" : ""}>
        <summary>${this._t("settings")}</summary>
        <div class="settings">
          <label>${this._t("start")} <input type="time" data-setting="heure_de_debut" value="${esc(s.start.slice(0, 5))}"></label>
          <label>${this._t("end")} <input type="time" data-setting="heure_de_fin" value="${esc(s.end.slice(0, 5))}"></label>
          <label>${this._t("every")} <input type="number" min="5" max="120" step="5" data-setting="intervalle_de_comptage" value="${s.interval}"></label>
          <label>${this._t("delay")} <input type="number" min="1" max="15" data-setting="delai_de_confirmation" value="${s.delay}"></label>
        </div>
        <small class="hint">${this._t("settings_hint")}</small>
      </details>`;
  }
}

const STYLE = `
  :host { --egg: #F2A93B; --today: #4F8FDB; }
  ha-card { padding: 16px; display: flex; flex-direction: column; gap: 14px; }
  .head { display: flex; justify-content: space-between; align-items: center; gap: 8px; }
  .title { font-size: 1.25em; font-weight: 600; }
  .chip { font-size: .8em; padding: 3px 10px; border-radius: 12px; background: var(--secondary-background-color); white-space: nowrap; }
  .chip.on { color: var(--success-color, #43a047); }
  .chip.off { color: var(--warning-color, #ffa000); }
  .chip.busy { color: var(--today); }
  .hero { text-align: center; }
  .big { font-size: 4em; font-weight: 700; line-height: 1; color: var(--egg); }
  .big-label { color: var(--secondary-text-color); margin-top: 4px; }
  .kpis { display: grid; grid-template-columns: repeat(4, 1fr); gap: 6px; margin-top: 12px; }
  .kpis div { background: var(--secondary-background-color); border-radius: 10px; padding: 6px 4px; display: flex; flex-direction: column; }
  .kpis b { font-size: 1.2em; }
  .kpis span { font-size: .75em; color: var(--secondary-text-color); }
  .actions { display: flex; gap: 8px; flex-wrap: wrap; }
  button { font: inherit; cursor: pointer; border: 1px solid var(--divider-color); background: var(--card-background-color); color: var(--primary-text-color); border-radius: 10px; padding: 8px 12px; flex: 1 1 auto; }
  button:hover { background: var(--secondary-background-color); }
  button.primary { background: var(--egg); border-color: var(--egg); color: #000; font-weight: 600; }
  button.warn { background: var(--error-color, #db4437); color: #fff; border-color: transparent; }
  button:disabled { opacity: .5; cursor: default; }
  button.icon { flex: none; padding: 2px 8px; margin-left: 6px; }
  button.ghost { border-color: transparent; opacity: .5; }
  button.ghost:hover { opacity: 1; }
  figure { margin: 0; }
  img.photo { width: 100%; border-radius: 12px; display: block; cursor: zoom-in; background: var(--secondary-background-color); }
  figcaption { font-size: .8em; color: var(--secondary-text-color); margin-top: 4px; text-align: center; }
  .journal { font-family: var(--code-font-family, monospace); font-size: .78em; background: var(--secondary-background-color); border-radius: 10px; padding: 8px 10px; max-height: 150px; overflow: auto; }
  .journal .start { margin-top: 4px; font-weight: 600; }
  .section-title, summary { font-weight: 600; cursor: pointer; }
  .section-title small, summary small { font-weight: normal; color: var(--secondary-text-color); margin-left: 6px; }
  details > summary { padding: 6px 0; }
  svg { width: 100%; height: auto; margin-top: 6px; }
  svg .bar { fill: var(--egg); }
  svg .bar.today { fill: var(--today); }
  svg text { font-size: 10px; text-anchor: middle; fill: var(--secondary-text-color); }
  svg text.val { fill: var(--primary-text-color); font-weight: 600; }
  svg text.month { font-weight: 700; fill: var(--primary-text-color); }
  .dot { display: inline-block; width: 9px; height: 9px; border-radius: 2px; background: var(--today); vertical-align: middle; }
  .scroll { max-height: 320px; overflow: auto; }
  table { width: 100%; border-collapse: collapse; }
  td { padding: 5px 4px; border-bottom: 1px solid var(--divider-color); }
  td.num { text-align: right; white-space: nowrap; font-weight: 600; }
  tr.today td { color: var(--today); }
  input { font: inherit; padding: 4px 6px; border-radius: 8px; border: 1px solid var(--divider-color); background: var(--card-background-color); color: var(--primary-text-color); }
  input.edit { width: 60px; }
  .correct { display: flex; flex-wrap: wrap; gap: 6px; align-items: center; margin-top: 10px; font-size: .9em; }
  .correct input[type=number] { width: 70px; }
  .correct button { flex: none; }
  .event { border: 1px solid var(--divider-color); border-left-width: 4px; border-radius: 10px; padding: 8px; margin-top: 8px; }
  .event.ok { border-left-color: var(--success-color, #43a047); }
  .event.ko { border-left-color: var(--error-color, #db4437); }
  .event.info { border-left-color: var(--today); }
  .event-head { display: flex; justify-content: space-between; font-weight: 600; }
  .event-detail { font-size: .8em; color: var(--secondary-text-color); margin: 2px 0 6px; }
  .thumbs { display: grid; grid-template-columns: 1fr 1fr; gap: 6px; }
  .thumbs img { width: 100%; border-radius: 8px; cursor: zoom-in; }
  .settings { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px; margin-top: 6px; }
  .settings label { display: flex; flex-direction: column; gap: 4px; font-size: .85em; color: var(--secondary-text-color); }
  .hint { display: block; margin-top: 8px; color: var(--secondary-text-color); }
  .empty { text-align: center; color: var(--secondary-text-color); padding: 16px; }
  .empty.small { padding: 8px; font-size: .9em; }
  .lightbox { position: fixed; inset: 0; background: rgba(0,0,0,.85); display: flex; flex-direction: column; align-items: center; justify-content: center; z-index: 999; cursor: zoom-out; padding: 16px; }
  .lightbox[hidden] { display: none; }
  .lightbox img { max-width: 100%; max-height: 85vh; border-radius: 8px; }
  .lightbox .caption { color: #fff; margin-top: 8px; text-align: center; }
`;

if (!customElements.get("comptage-oeufs-poulailler-card")) {
  customElements.define("comptage-oeufs-poulailler-card", ComptageOeufsPoulaillerCard);
  window.customCards = window.customCards || [];
  window.customCards.push({
    type: "comptage-oeufs-poulailler-card",
    name: "Comptage Œufs Poulailler",
    description: translate(navigator.language, "card_desc"),
    preview: false,
    documentationURL: "https://github.com/JVmaisGpeur/ha-comptage-oeufs-poulailler",
  });
  console.info(`%c🥚 COMPTAGE-OEUFS-POULAILLER-CARD %c v${CARD_VERSION}`, "color:#F2A93B;font-weight:700", "color:inherit");
}
