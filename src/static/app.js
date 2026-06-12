'use strict';

// ── Constants ──────────────────────────────────────────────────────────────────

const CARE_LABELS = {
  watering:    'Giessen',
  fertilizing: 'Duengen',
  repotting:   'Umtopfen',
};

const CARE_TYPES = Object.keys(CARE_LABELS);

// ── State ──────────────────────────────────────────────────────────────────────

let selectedPlantId = null;
let modalCallback   = null;

// ── API helpers ────────────────────────────────────────────────────────────────

async function apiFetch(method, path, body = null) {
  const opts = { method, headers: {} };
  if (body !== null) {
    opts.headers['Content-Type'] = 'application/json';
    opts.body = JSON.stringify(body);
  }
  const res = await fetch(`/api${path}`, opts);
  if (!res.ok) throw new Error(`Fehler ${res.status}: ${await res.text()}`);
  if (res.status === 204) return null;
  return res.json();
}

// ── DOM helpers ────────────────────────────────────────────────────────────────

const el = id => document.getElementById(id);

function escHtml(str) {
  const d = document.createElement('div');
  d.textContent = String(str ?? '');
  return d.innerHTML;
}

function formatDate(iso) {
  const [y, m, d] = iso.split('-');
  return `${d}.${m}.${y}`;
}

function daysLabel(days) {
  if (days === 0)  return 'Heute faellig';
  if (days === 1)  return 'Morgen faellig';
  if (days === -1) return '1 Tag ueberfaellig';
  if (days < 0)    return `${Math.abs(days)} Tage ueberfaellig`;
  return `In ${days} Tagen`;
}

function rowClass(days) {
  if (days < 0)  return 'overdue';
  if (days <= 3) return 'soon';
  return 'ok';
}

// ── Plant grid ─────────────────────────────────────────────────────────────────

async function loadPlants() {
  const plants = await apiFetch('GET', '/plants');
  const grid   = el('plants-grid');
  const empty  = el('plants-empty');
  grid.innerHTML = '';

  if (plants.length === 0) {
    grid.classList.add('hidden');
    empty.classList.remove('hidden');
    updateOverdueBadge(0);
    return;
  }

  grid.classList.remove('hidden');
  empty.classList.add('hidden');

  let overdueCount = 0;
  for (const p of plants) {
    if (p.status === 'overdue') overdueCount++;

    // Fetch next actions for card preview (parallel)
    const card = document.createElement('div');
    card.className = `plant-card${selectedPlantId === p.id ? ' selected' : ''}`;
    card.dataset.id = p.id;

    const badgeClass = { ok: 'badge-ok', soon: 'badge-soon', overdue: 'badge-overdue' }[p.status] || 'badge-ok';
    const statusText = { ok: 'Ok', soon: 'Bald faellig', overdue: 'Ueberfaellig' }[p.status] || p.status;

    card.innerHTML = `
      <div class="card-head">
        <h3>${escHtml(p.name)}</h3>
        <span class="status-badge ${badgeClass}">${statusText}</span>
      </div>
      <p class="card-species">${escHtml(p.species)}</p>
      <p class="card-location">Standort: ${escHtml(p.location)}</p>
      <div class="card-actions-preview" id="preview-${p.id}"></div>
    `;
    card.addEventListener('click', () => selectPlant(p.id));
    grid.appendChild(card);

    // Async preview load — fire and forget
    apiFetch('GET', `/plants/${p.id}/next-actions`).then(actions => {
      const preview = el(`preview-${p.id}`);
      if (!preview) return;
      if (actions.length === 0) {
        const btn = document.createElement('button');
        btn.className = 'card-add-plan-btn';
        btn.textContent = '+ Pflegeplan anlegen';
        btn.addEventListener('click', e => {
          e.stopPropagation();
          selectedPlantId = p.id;
          showAddScheduleModal(p.id);
        });
        preview.appendChild(btn);
        return;
      }
      preview.innerHTML = actions.slice(0, 3).map(a => {
        const cls = rowClass(a.days_until);
        return `<div class="preview-row ${cls}">
          <span>${escHtml(CARE_LABELS[a.care_type] || a.care_type)}</span>
          <span>${daysLabel(a.days_until)}</span>
        </div>`;
      }).join('');
    });
  }

  updateOverdueBadge(overdueCount);
}

// ── Overdue tab ────────────────────────────────────────────────────────────────

async function loadOverdue() {
  const items = await apiFetch('GET', '/overdue');
  const list  = el('overdue-list');
  const empty = el('overdue-empty');
  list.innerHTML = '';

  updateOverdueBadge(items.length);

  if (items.length === 0) {
    list.classList.add('hidden');
    empty.classList.remove('hidden');
    return;
  }

  list.classList.remove('hidden');
  empty.classList.add('hidden');

  for (const item of items) {
    const div = document.createElement('div');
    div.className = 'overdue-card';
    div.innerHTML = `
      <div class="overdue-info">
        <div class="overdue-plant">${escHtml(item.plant_name)}</div>
        <div class="overdue-detail">
          ${escHtml(CARE_LABELS[item.care_type] || item.care_type)}
          &mdash; faellig seit ${formatDate(item.next_due)}
          &mdash; ${escHtml(item.plant_location)}
        </div>
      </div>
      <div class="overdue-days">${item.days_overdue} T.</div>
      <button class="btn-primary btn-sm">Jetzt erledigen</button>
    `;
    div.querySelector('button').addEventListener('click', () =>
      quickLog(item.plant_id, item.care_type)
    );
    list.appendChild(div);
  }
}

async function quickLog(plantId, careType) {
  const today = new Date().toISOString().split('T')[0];
  await apiFetch('POST', `/plants/${plantId}/logs`, { care_type: careType, performed_at: today, notes: '' });
  await loadOverdue();
  await loadPlants();
  if (selectedPlantId === plantId) await refreshDetail(plantId);
}

async function confirmNextAction(plantId, careType) {
  const today = new Date().toISOString().split('T')[0];
  await apiFetch('POST', `/plants/${plantId}/logs`, { care_type: careType, performed_at: today, notes: '' });
  await Promise.all([refreshDetail(plantId), loadPlants()]);
}

function updateOverdueBadge(count) {
  const badge = el('overdue-badge');
  if (count > 0) {
    badge.textContent = count;
    badge.classList.remove('hidden');
  } else {
    badge.classList.add('hidden');
  }
}

// ── Detail panel ───────────────────────────────────────────────────────────────

async function selectPlant(id) {
  selectedPlantId = id;
  document.querySelectorAll('.plant-card').forEach(c =>
    c.classList.toggle('selected', +c.dataset.id === id)
  );
  el('main-content').classList.add('panel-open');
  const panel = el('detail-panel');
  panel.classList.remove('hidden');
  requestAnimationFrame(() => panel.classList.add('open'));
  await refreshDetail(id);
}

async function refreshDetail(id) {
  const [plant, nextActions, logs] = await Promise.all([
    apiFetch('GET', `/plants/${id}`),
    apiFetch('GET', `/plants/${id}/next-actions`),
    apiFetch('GET', `/plants/${id}/logs`),
  ]);
  renderDetail(plant, nextActions, logs);
}

function renderDetail(plant, nextActions, logs) {
  el('detail-name').textContent     = plant.name;
  el('detail-species').textContent  = plant.species;
  el('detail-location').textContent = plant.location;

  // Schedules
  const sBox = el('schedules-container');
  if (plant.schedules.length === 0) {
    sBox.innerHTML = '<p class="muted" style="font-size:.85rem">Keine Pflegeplaene konfiguriert.</p>';
  } else {
    sBox.innerHTML = plant.schedules.map(s => `
      <div class="schedule-row">
        <span class="schedule-type">${escHtml(CARE_LABELS[s.care_type] || s.care_type)}</span>
        <span class="schedule-interval">alle ${s.interval_days} Tage</span>
        <button class="btn-icon btn-danger" data-ct="${s.care_type}" title="Entfernen">&#10005;</button>
      </div>
    `).join('');
    sBox.querySelectorAll('[data-ct]').forEach(btn =>
      btn.addEventListener('click', () => deleteSchedule(plant.id, btn.dataset.ct))
    );
  }

  // Next actions
  const nBox = el('next-actions-container');
  if (nextActions.length === 0) {
    nBox.innerHTML = '<p class="muted" style="font-size:.85rem">Keine Pflegeplaene vorhanden.</p>';
  } else {
    nBox.innerHTML = nextActions.map(a => {
      const cls = rowClass(a.days_until);
      return `<div class="next-row ${cls}">
        <span class="next-type">${escHtml(CARE_LABELS[a.care_type] || a.care_type)}</span>
        <span class="next-date">${formatDate(a.next_due)}</span>
        <span class="next-days">${daysLabel(a.days_until)}</span>
        <button class="btn-confirm" data-ct="${a.care_type}" title="Heute als erledigt markieren">&#10003;</button>
      </div>`;
    }).join('');
    nBox.querySelectorAll('.btn-confirm').forEach(btn =>
      btn.addEventListener('click', () => confirmNextAction(plant.id, btn.dataset.ct))
    );
  }

  // Action log
  const lBox = el('log-container');
  if (logs.length === 0) {
    lBox.innerHTML = '<p class="muted" style="font-size:.85rem">Noch keine Aktionen protokolliert.</p>';
  } else {
    lBox.innerHTML = logs.slice(0, 30).map(l => `
      <div class="log-row">
        <div class="log-head">
          <span class="log-type">${escHtml(CARE_LABELS[l.care_type] || l.care_type)}</span>
          <span class="log-date">${formatDate(l.performed_at)}</span>
        </div>
        ${l.notes ? `<div class="log-notes">${escHtml(l.notes)}</div>` : ''}
      </div>
    `).join('');
  }
}

function closeDetail() {
  selectedPlantId = null;
  const panel = el('detail-panel');
  panel.classList.remove('open');
  el('main-content').classList.remove('panel-open');
  document.querySelectorAll('.plant-card.selected').forEach(c => c.classList.remove('selected'));
  setTimeout(() => panel.classList.add('hidden'), 300);
}

// ── Schedules ──────────────────────────────────────────────────────────────────

async function deleteSchedule(plantId, careType) {
  await apiFetch('DELETE', `/plants/${plantId}/schedules/${careType}`);
  await refreshDetail(plantId);
  await loadPlants();
}

function showAddScheduleModal(plantId) {
  apiFetch('GET', `/plants/${plantId}/schedules`).then(existing => {
    const taken     = existing.map(s => s.care_type);
    const available = CARE_TYPES.filter(t => !taken.includes(t));

    if (available.length === 0) {
      alert('Alle Pflegetypen sind bereits konfiguriert.');
      return;
    }

    openModal('Pflegeplan hinzufuegen', `
      <div class="field">
        <label>Pflegetyp</label>
        <select id="f-ct">
          ${available.map(t => `<option value="${t}">${CARE_LABELS[t]}</option>`).join('')}
        </select>
      </div>
      <div class="field">
        <label>Intervall (Tage)</label>
        <input type="number" id="f-iv" min="1" max="365" value="7">
      </div>
    `, async () => {
      const ct = el('f-ct').value;
      const iv = parseInt(el('f-iv').value, 10);
      if (!iv || iv < 1) throw new Error('Ungueltige Anzahl Tage');
      await apiFetch('POST', `/plants/${plantId}/schedules`, { care_type: ct, interval_days: iv });
      await refreshDetail(plantId);
      await loadPlants();
    });
  });
}

// ── Action logging ─────────────────────────────────────────────────────────────

function showLogModal(plantId) {
  const today = new Date().toISOString().split('T')[0];
  openModal('Aktion protokollieren', `
    <div class="field">
      <label>Pflegetyp</label>
      <select id="f-lct">
        ${CARE_TYPES.map(t => `<option value="${t}">${CARE_LABELS[t]}</option>`).join('')}
      </select>
    </div>
    <div class="field">
      <label>Datum</label>
      <input type="date" id="f-ldate" value="${today}">
    </div>
    <div class="field">
      <label>Notizen (optional)</label>
      <textarea id="f-lnotes" placeholder="z.B. Volldünger verwendet, 200ml..."></textarea>
    </div>
  `, async () => {
    const ct    = el('f-lct').value;
    const dt    = el('f-ldate').value;
    const notes = el('f-lnotes').value.trim();
    if (!dt) throw new Error('Bitte ein Datum angeben');
    await apiFetch('POST', `/plants/${plantId}/logs`, { care_type: ct, performed_at: dt, notes });
    await refreshDetail(plantId);
    await loadPlants();
  });
}

// ── Plant CRUD ─────────────────────────────────────────────────────────────────

function showAddPlantModal() {
  openModal('Pflanze hinzufuegen', plantFormHTML(), async () => {
    const data = readPlantForm();
    await apiFetch('POST', '/plants', data);
    await loadPlants();
  });
}

async function showEditPlantModal() {
  if (!selectedPlantId) return;
  const plant = await apiFetch('GET', `/plants/${selectedPlantId}`);
  openModal('Pflanze bearbeiten', plantFormHTML(plant), async () => {
    const data = readPlantForm();
    await apiFetch('PUT', `/plants/${plant.id}`, data);
    await refreshDetail(plant.id);
    await loadPlants();
  });
}

async function deletePlant() {
  if (!selectedPlantId) return;
  if (!confirm('Pflanze wirklich loeschen? Alle Pflegeplaene und Protokolle werden mitgeloescht.')) return;
  await apiFetch('DELETE', `/plants/${selectedPlantId}`);
  closeDetail();
  await loadPlants();
}

function plantFormHTML(p = {}) {
  return `
    <div class="field">
      <label>Name</label>
      <input type="text" id="f-name" value="${escHtml(p.name || '')}" placeholder="z.B. Mein Gummibaum">
    </div>
    <div class="field">
      <label>Art / Gattung</label>
      <input type="text" id="f-species" value="${escHtml(p.species || '')}" placeholder="z.B. Ficus elastica">
    </div>
    <div class="field">
      <label>Standort</label>
      <input type="text" id="f-location" value="${escHtml(p.location || '')}" placeholder="z.B. Wohnzimmer Suedfenster">
    </div>
  `;
}

function readPlantForm() {
  const name     = el('f-name').value.trim();
  const species  = el('f-species').value.trim();
  const location = el('f-location').value.trim();
  if (!name || !species || !location) throw new Error('Bitte alle Felder ausfuellen');
  return { name, species, location };
}

// ── Modal system ───────────────────────────────────────────────────────────────

function openModal(title, bodyHtml, onConfirm) {
  el('modal-title').textContent = title;
  el('modal-body').innerHTML    = bodyHtml;
  el('modal-overlay').classList.remove('hidden');
  modalCallback = onConfirm;
  const first = el('modal-body').querySelector('input, select, textarea');
  if (first) setTimeout(() => first.focus(), 40);
}

function closeModal() {
  el('modal-overlay').classList.add('hidden');
  modalCallback = null;
}

async function confirmModal() {
  if (!modalCallback) return;
  try {
    await modalCallback();
    closeModal();
  } catch (err) {
    alert(err.message);
  }
}

// ── Tab switching ──────────────────────────────────────────────────────────────

function switchTab(tab) {
  document.querySelectorAll('.tab-btn').forEach(b =>
    b.classList.toggle('active', b.dataset.tab === tab)
  );
  document.querySelectorAll('.tab').forEach(t =>
    t.classList.toggle('active', t.id === `tab-${tab}`)
  );
  if (tab === 'overdue') loadOverdue();
}

// ── Boot ───────────────────────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
  // Tabs
  document.querySelectorAll('.tab-btn').forEach(btn =>
    btn.addEventListener('click', () => switchTab(btn.dataset.tab))
  );

  // Add plant
  el('btn-add-plant').addEventListener('click', showAddPlantModal);
  el('btn-add-plant-empty').addEventListener('click', showAddPlantModal);

  // Detail panel controls
  el('btn-close-detail').addEventListener('click', closeDetail);
  el('btn-edit-plant').addEventListener('click', showEditPlantModal);
  el('btn-delete-plant').addEventListener('click', deletePlant);
  el('btn-add-schedule').addEventListener('click', () => {
    if (selectedPlantId) showAddScheduleModal(selectedPlantId);
  });
  el('btn-log-action').addEventListener('click', () => {
    if (selectedPlantId) showLogModal(selectedPlantId);
  });

  // Overdue tab
  el('btn-refresh-overdue').addEventListener('click', loadOverdue);

  // Modal
  el('modal-close').addEventListener('click', closeModal);
  el('modal-cancel').addEventListener('click', closeModal);
  el('modal-confirm').addEventListener('click', confirmModal);
  el('modal-overlay').addEventListener('click', e => {
    if (e.target === el('modal-overlay')) closeModal();
  });

  // Keyboard
  document.addEventListener('keydown', e => {
    if (e.key !== 'Escape') return;
    if (!el('modal-overlay').classList.contains('hidden')) closeModal();
    else closeDetail();
  });

  loadPlants();
});
