/*
 * Carte Lovelace « Comptage Œufs Poulailler »
 * Fournie et chargée automatiquement par l'intégration comptage_oeufs_poulailler.
 * Licence MIT – JVmaisGpeur
 */
const DOMAIN = "comptage_oeufs_poulailler";
const CARD_VERSION = "1.0.0";

const DEFAULTS = {
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

const EVENT_LABELS = {
  confirme: ["✅", "Nouvel œuf confirmé", "ok"],
  rejete: ["❌", "Hausse non confirmée", "ko"],
  ramassage: ["🧺", "Ramassage détecté", "info"],
};

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
        this._toast("Comptage lancé…");
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
        if (Number.isNaN(n) || n < 0) return this._toast("Nombre invalide");
        this._service(DOMAIN, "corriger", { ...entry, date: this._editing, nombre: n });
        this._editing = null;
        break;
      }
      case "correct": {
        const date = this.shadowRoot.querySelector("#corr-date")?.value;
        const n = parseInt(this.shadowRoot.querySelector("#corr-n")?.value, 10);
        if (!date || Number.isNaN(n) || n < 0) return this._toast("Choisissez une date et un nombre");
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
    const lang = this._hass?.locale?.language || this._hass?.language || "fr";
    return parseIso(isoDate).toLocaleDateString(lang, opts);
  }

  _fmtTime(isoDateTime) {
    if (!isoDateTime) return "";
    const lang = this._hass?.locale?.language || "fr";
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
      body = `<div class="empty">⚠️ ${esc(this._error)}<br><small>L'intégration « Comptage Œufs Poulailler » est-elle configurée ?</small></div>`;
    } else if (!this._data) {
      body = `<div class="empty">Chargement…</div>`;
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
      ? `<span class="chip busy">⏳ Comptage en cours</span>`
      : d.auto
        ? `<span class="chip on">● Auto ${esc(d.settings.start.slice(0, 5))}–${esc(d.settings.end.slice(0, 5))}</span>`
        : `<span class="chip off">⏸ En pause</span>`;
    return `
      <div class="head"><div class="title">🥚 ${esc(title)}</div>${status}</div>
      <div class="hero">
        <div class="big">${d.today}</div>
        <div class="big-label">œuf${d.today > 1 ? "s" : ""} pondu${d.today > 1 ? "s" : ""} aujourd'hui</div>
        <div class="kpis">
          <div><b>${d.baseline ?? "–"}</b><span>dans les pondoirs</span></div>
          <div><b>${s.hier ?? 0}</b><span>hier</span></div>
          <div><b>${s["7_jours"] ?? 0}</b><span>7 jours</span></div>
          <div><b>${s.ce_mois ?? 0}</b><span>ce mois</span></div>
        </div>
      </div>
      <div class="actions">
        <button class="primary" data-action="count" ${d.counting ? "disabled" : ""}>📷 Compter maintenant</button>
        <button class="${this._confirmCollect ? "warn" : ""}" data-action="collect">${this._confirmCollect ? "Confirmer ?" : "🧺 Œufs ramassés"}</button>
        <button data-action="toggle-auto">${d.auto ? "⏸ Pause" : "▶ Reprendre"}</button>
      </div>`;
  }

  _renderPhoto() {
    const d = this._data;
    const last = d.last_reading || {};
    if (this._config.show_live_camera) {
      const src = this._hass.states[d.camera]?.attributes?.entity_picture;
      return src ? `<img class="photo live" data-src="${esc(src)}" src="${esc(src)}" alt="Caméra">` : "";
    }
    if (!d.last_image_url) return `<div class="empty small">Aucune photo analysée pour l'instant.</div>`;
    const cap = `Dernière analyse ${this._fmtTime(last.time)} · ${last.eggs} œuf(s)${last.hen ? " · 🐔 poule sur un nid" : ""}`;
    return `<figure>
        <img class="photo" src="${esc(d.last_image_url)}" alt="Dernière photo analysée" data-action="zoom" data-src="${esc(d.last_image_url)}" data-caption="${esc(cap)}">
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
        <div class="section-title">Œufs par jour <small>moyenne ${mean}/jour sur ${avg.length} j · <span class="dot today"></span> aujourd'hui</small></div>
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
              <button class="icon" data-action="save" title="Enregistrer">✓</button>
              <button class="icon" data-action="cancel" title="Annuler">✕</button></td></tr>`;
        }
        return `<tr class="${isToday ? "today" : ""}"><td>${esc(label)}${isToday ? " <em>(en cours)</em>" : ""}</td>
            <td class="num">${count}<button class="icon ghost" data-action="edit" data-date="${h.date}" title="Corriger">✏️</button></td></tr>`;
      })
      .join("");
    const s = d.stats || {};
    return `<details class="section" data-section="history" ${this._open.has("history") ? "open" : ""}>
        <summary>📅 Historique <small>${s.cette_annee ?? 0} cette année · ${s.total ?? 0} au total</small></summary>
        <div class="scroll"><table>${rows || `<tr><td>Aucun historique</td></tr>`}</table></div>
        <div class="correct">
          <span>Corriger un autre jour :</span>
          <input id="corr-date" type="date" max="${d.today_date}">
          <input id="corr-n" type="number" min="0" max="999" placeholder="œufs" data-enter="correct">
          <button data-action="correct">Appliquer</button>
        </div>
      </details>`;
  }

  _renderEvents() {
    const events = this._data.events || [];
    const items = events
      .map((e) => {
        const [icon, label, cls] = EVENT_LABELS[e.type] || ["•", e.type, ""];
        const when = this._fmtTime(e.time);
        const detail = `Lecture 1 : ${e.lecture1}${e.poule1 ? " 🐔" : ""} · Lecture 2 : ${e.lecture2}${e.poule2 ? " 🐔" : ""} · pondoirs ${e.avant} → ${e.apres}`;
        const imgs = (e.urls || [])
          .filter(Boolean)
          .map(
            (u, i) =>
              `<img loading="lazy" src="${esc(u)}" alt="Lecture ${i + 1}" data-action="zoom" data-src="${esc(u)}" data-caption="${esc(`${when} – ${label} – lecture ${i + 1}`)}">`
          )
          .join("");
        return `<div class="event ${cls}">
            <div class="event-head"><span>${icon} ${esc(label)}</span><small>${esc(when)}</small></div>
            <div class="event-detail">${esc(detail)}</div>
            <div class="thumbs">${imgs || "<small>Pas de photo</small>"}</div>
          </div>`;
      })
      .join("");
    return `<details class="section" data-section="photos" ${this._open.has("photos") ? "open" : ""}>
        <summary>🖼️ Photos des détections <small>${events.length} récente(s)</small></summary>
        ${items || `<div class="empty small">Les photos des nouveaux œufs (et des lectures non confirmées) apparaîtront ici.</div>`}
      </details>`;
  }

  _renderSettings() {
    const s = this._data.settings;
    return `<details class="section" data-section="settings" ${this._open.has("settings") ? "open" : ""}>
        <summary>⚙️ Réglages</summary>
        <div class="settings">
          <label>Début du comptage <input type="time" data-setting="heure_de_debut" value="${esc(s.start.slice(0, 5))}"></label>
          <label>Fin du comptage <input type="time" data-setting="heure_de_fin" value="${esc(s.end.slice(0, 5))}"></label>
          <label>Comptage toutes les (min) <input type="number" min="5" max="120" step="5" data-setting="intervalle_de_comptage" value="${s.interval}"></label>
          <label>Délai avant la 2ᵉ lecture (min) <input type="number" min="1" max="15" data-setting="delai_de_confirmation" value="${s.delay}"></label>
        </div>
        <small class="hint">Caméra, IA, notification, consigne et conservation des photos : Paramètres › Appareils et services › Comptage Œufs Poulailler › Configurer.</small>
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
    description: "Compteur d'œufs, historique corrigeable, graphique et photos des détections.",
    preview: false,
    documentationURL: "https://github.com/JVmaisGpeur/ha-comptage-oeufs-poulailler",
  });
  console.info(`%c🥚 COMPTAGE-OEUFS-POULAILLER-CARD %c v${CARD_VERSION}`, "color:#F2A93B;font-weight:700", "color:inherit");
}
