"""
admin/dashboard.py — Web Dashboard HTML 页面

提供一个自包含的 HTML 管理面板，无需任何前端构建工具或外部依赖。
所有 CSS/JS 内嵌，通过 fetch 调用 /admin/* JSON API 获取数据并渲染。
"""
from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

dashboard_router = APIRouter(tags=["dashboard"])

DASHBOARD_HTML = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Bug Analysis Daemon - Dashboard</title>
<style>
  :root {
    --bg: #0f172a;
    --card: #1e293b;
    --border: #334155;
    --text: #e2e8f0;
    --text-dim: #94a3b8;
    --accent: #38bdf8;
    --accent2: #818cf8;
    --green: #22c55e;
    --red: #ef4444;
    --orange: #f97316;
    --yellow: #eab308;
  }
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: var(--bg);
    color: var(--text);
    min-height: 100vh;
  }
  .header {
    background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
    border-bottom: 1px solid var(--border);
    padding: 20px 32px;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  .header h1 {
    font-size: 22px;
    font-weight: 600;
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }
  .header .refresh-info {
    font-size: 13px;
    color: var(--text-dim);
    display: flex;
    align-items: center;
    gap: 10px;
  }
  .header .refresh-info button {
    background: var(--card);
    border: 1px solid var(--border);
    color: var(--accent);
    padding: 6px 14px;
    border-radius: 6px;
    cursor: pointer;
    font-size: 13px;
    transition: all 0.2s;
  }
  .header .refresh-info button:hover {
    background: var(--border);
  }

  .container { max-width: 1400px; margin: 0 auto; padding: 24px; }

  /* Tabs */
  .tabs {
    display: flex;
    gap: 4px;
    margin-bottom: 24px;
    border-bottom: 1px solid var(--border);
    padding-bottom: 0;
  }
  .tab {
    padding: 10px 20px;
    cursor: pointer;
    color: var(--text-dim);
    font-size: 14px;
    font-weight: 500;
    border-bottom: 2px solid transparent;
    transition: all 0.2s;
    user-select: none;
  }
  .tab:hover { color: var(--text); }
  .tab.active {
    color: var(--accent);
    border-bottom-color: var(--accent);
  }

  .tab-content { display: none; }
  .tab-content.active { display: block; }

  /* Status Cards */
  .status-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 16px;
    margin-bottom: 28px;
  }
  .stat-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 20px;
    position: relative;
    overflow: hidden;
  }
  .stat-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, var(--accent), var(--accent2));
  }
  .stat-card.green::before { background: var(--green); }
  .stat-card.red::before { background: var(--red); }
  .stat-card.orange::before { background: var(--orange); }
  .stat-card .label {
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: var(--text-dim);
    margin-bottom: 8px;
  }
  .stat-card .value {
    font-size: 28px;
    font-weight: 700;
    font-variant-numeric: tabular-nums;
  }
  .stat-card .sub {
    font-size: 12px;
    color: var(--text-dim);
    margin-top: 4px;
  }

  /* Badge */
  .badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: 600;
  }
  .badge-green  { background: rgba(34,197,94,0.15); color: var(--green); }
  .badge-red    { background: rgba(239,68,68,0.15); color: var(--red); }
  .badge-orange { background: rgba(249,115,22,0.15); color: var(--orange); }
  .badge-blue   { background: rgba(56,189,248,0.15); color: var(--accent); }
  .badge-gray   { background: rgba(148,163,184,0.15); color: var(--text-dim); }

  /* Table */
  .card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px;
    overflow: hidden;
    margin-bottom: 20px;
  }
  .card-header {
    padding: 16px 20px;
    border-bottom: 1px solid var(--border);
    font-weight: 600;
    font-size: 15px;
    display: flex;
    align-items: center;
    gap: 8px;
  }
  table {
    width: 100%;
    border-collapse: collapse;
  }
  th {
    text-align: left;
    padding: 12px 20px;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: var(--text-dim);
    border-bottom: 1px solid var(--border);
    background: rgba(0,0,0,0.2);
  }
  td {
    padding: 12px 20px;
    font-size: 14px;
    border-bottom: 1px solid rgba(51,65,85,0.5);
  }
  tr:last-child td { border-bottom: none; }
  tr:hover td { background: rgba(56,189,248,0.03); }

  .empty-state {
    padding: 48px 20px;
    text-align: center;
    color: var(--text-dim);
  }
  .empty-state .icon { font-size: 40px; margin-bottom: 12px; }

  /* Config */
  .config-section {
    margin-bottom: 16px;
  }
  .config-section-title {
    padding: 12px 20px;
    background: rgba(0,0,0,0.2);
    font-weight: 600;
    font-size: 14px;
    color: var(--accent);
    border-bottom: 1px solid var(--border);
    cursor: pointer;
    user-select: none;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  .config-section-title:hover { background: rgba(0,0,0,0.3); }
  .config-section-title .arrow { transition: transform 0.2s; }
  .config-section-title.collapsed .arrow { transform: rotate(-90deg); }
  .config-table { display: block; }
  .config-table.hidden { display: none; }
  .config-key { font-family: 'Cascadia Code', 'Fira Code', monospace; color: var(--accent2); font-size: 13px; }
  .config-val { font-family: 'Cascadia Code', 'Fira Code', monospace; font-size: 13px; }
  .config-val.secret { color: var(--text-dim); font-style: italic; }
  .config-val.mutable {
    color: var(--green);
    cursor: pointer;
    text-decoration: underline;
    text-decoration-style: dashed;
    text-underline-offset: 3px;
  }
  .config-val.mutable:hover { color: #4ade80; }

  /* Edit dialog */
  .modal-overlay {
    display: none;
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background: rgba(0,0,0,0.6);
    z-index: 100;
    justify-content: center;
    align-items: center;
  }
  .modal-overlay.show { display: flex; }
  .modal {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 24px;
    min-width: 400px;
    max-width: 500px;
  }
  .modal h3 { margin-bottom: 16px; font-size: 16px; }
  .modal label { display: block; font-size: 13px; color: var(--text-dim); margin-bottom: 6px; }
  .modal input {
    width: 100%;
    padding: 10px 12px;
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 8px;
    color: var(--text);
    font-size: 14px;
    font-family: 'Cascadia Code', 'Fira Code', monospace;
    margin-bottom: 16px;
  }
  .modal input:focus { outline: none; border-color: var(--accent); }
  .modal .btn-row { display: flex; gap: 10px; justify-content: flex-end; }
  .modal button {
    padding: 8px 18px;
    border-radius: 8px;
    font-size: 14px;
    cursor: pointer;
    border: none;
  }
  .modal .btn-cancel { background: var(--border); color: var(--text); }
  .modal .btn-save { background: var(--accent); color: #0f172a; font-weight: 600; }
  .modal .btn-cancel:hover { background: #475569; }
  .modal .btn-save:hover { background: #7dd3fc; }
  .toast {
    position: fixed;
    bottom: 24px;
    right: 24px;
    padding: 12px 20px;
    border-radius: 8px;
    font-size: 14px;
    z-index: 200;
    transition: opacity 0.3s;
    opacity: 0;
  }
  .toast.show { opacity: 1; }
  .toast.success { background: rgba(34,197,94,0.9); color: #fff; }
  .toast.error { background: rgba(239,68,68,0.9); color: #fff; }

  /* Confluence Download Form */
  .dl-form { padding: 20px; display: flex; flex-direction: column; gap: 14px; }
  .dl-form .form-row { display: flex; gap: 12px; align-items: flex-end; flex-wrap: wrap; }
  .dl-form label { font-size: 13px; color: var(--text-dim); display: block; margin-bottom: 4px; }
  .dl-form input[type="text"], .dl-form input[type="number"] {
    padding: 8px 12px;
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 6px;
    color: var(--text);
    font-size: 14px;
    font-family: 'Cascadia Code', 'Fira Code', monospace;
  }
  .dl-form input[type="text"] { flex: 1; min-width: 300px; }
  .dl-form input[type="number"] { width: 80px; }
  .dl-form .btn-start {
    padding: 8px 20px;
    background: var(--accent);
    color: #0f172a;
    border: none;
    border-radius: 6px;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    white-space: nowrap;
  }
  .dl-form .btn-start:hover { background: #7dd3fc; }
  .dl-form .btn-start:disabled { opacity: 0.5; cursor: not-allowed; }
  .dl-form .options-row { display: flex; gap: 16px; align-items: center; }
  .dl-form .options-row label { margin-bottom: 0; display: flex; align-items: center; gap: 4px; cursor: pointer; }
  .progress-bar-bg { background: var(--border); border-radius: 4px; height: 6px; overflow: hidden; }
  .progress-bar-fill { height: 100%; background: var(--accent); border-radius: 4px; transition: width 0.3s; }
  .btn-cancel-task {
    padding: 4px 12px;
    background: transparent;
    border: 1px solid var(--red);
    color: var(--red);
    border-radius: 4px;
    font-size: 12px;
    cursor: pointer;
  }
  .btn-cancel-task:hover { background: rgba(239,68,68,0.1); }

  @media (max-width: 768px) {
    .container { padding: 12px; }
    .status-grid { grid-template-columns: repeat(2, 1fr); }
    .header { padding: 16px; }
    .header h1 { font-size: 18px; }
    td, th { padding: 8px 12px; }
  }
</style>
</head>
<body>
<div class="header">
  <h1>Bug Analysis Daemon</h1>
  <div class="refresh-info">
    <span id="lastUpdate"></span>
    <button onclick="refreshAll()">Refresh</button>
    <label style="display:flex;align-items:center;gap:4px;cursor:pointer">
      <input type="checkbox" id="autoRefresh" checked style="cursor:pointer"> Auto (10s)
    </label>
  </div>
</div>

<div class="container">
  <div class="tabs">
    <div class="tab active" data-tab="status">Status</div>
    <div class="tab" data-tab="history">History</div>
    <div class="tab" data-tab="errors">Errors</div>
    <div class="tab" data-tab="confluence">Confluence</div>
    <div class="tab" data-tab="config">Config</div>
  </div>

  <!-- ========== STATUS TAB ========== -->
  <div id="tab-status" class="tab-content active">
    <div class="status-grid" id="statusGrid"></div>
    <div class="card">
      <div class="card-header">Active Analyses</div>
      <div id="activeList"></div>
    </div>
  </div>

  <!-- ========== HISTORY TAB ========== -->
  <div id="tab-history" class="tab-content">
    <div class="card">
      <div class="card-header">Analysis History (recent 50)</div>
      <div id="historyTable"></div>
    </div>
  </div>

  <!-- ========== ERRORS TAB ========== -->
  <div id="tab-errors" class="tab-content">
    <div class="card">
      <div class="card-header">Error Log (recent 50)</div>
      <div id="errorsTable"></div>
    </div>
  </div>

  <!-- ========== CONFLUENCE TAB ========== -->
  <div id="tab-confluence" class="tab-content">
    <div class="card">
      <div class="card-header">Download Confluence Pages</div>
      <div class="dl-form">
        <div class="form-row">
          <div style="flex:1">
            <label>Page URL or Page ID</label>
            <input type="text" id="confUrl" placeholder="https://confluence.example.com/spaces/SPACE/pages/12345/Title or just 12345" />
          </div>
        </div>
        <div class="form-row">
          <div>
            <label>Max Depth</label>
            <input type="number" id="confDepth" value="10" min="0" max="50" />
          </div>
          <div>
            <label>Output Dir (optional)</label>
            <input type="text" id="confOutput" placeholder="./confluence_downloads" style="min-width:200px" />
          </div>
          <div class="options-row">
            <label><input type="checkbox" id="confAttach" checked> Download Attachments</label>
            <label><input type="checkbox" id="confResume" checked> Resume Mode</label>
          </div>
          <button class="btn-start" id="confStartBtn" onclick="startConfDownload()">Start Download</button>
        </div>
      </div>
    </div>
    <div class="card">
      <div class="card-header">Download Tasks</div>
      <div id="confTasks"></div>
    </div>
  </div>

  <!-- ========== CONFIG TAB ========== -->
  <div id="tab-config" class="tab-content">
    <div class="card" id="configCard">
      <div class="card-header">Runtime Configuration
        <span style="flex:1"></span>
        <span style="font-size:12px;color:var(--text-dim);font-weight:400">
          Click <span style="color:var(--green)">green</span> values to edit
        </span>
      </div>
      <div id="configBody"></div>
    </div>
  </div>
</div>

<!-- Edit Modal -->
<div class="modal-overlay" id="editModal">
  <div class="modal">
    <h3 id="editTitle">Edit Config</h3>
    <label id="editLabel"></label>
    <input id="editInput" type="text" />
    <div class="btn-row">
      <button class="btn-cancel" onclick="closeModal()">Cancel</button>
      <button class="btn-save" id="editSave">Save</button>
    </div>
  </div>
</div>

<!-- Toast -->
<div class="toast" id="toast"></div>

<script>
const API = '';  // same origin
let mutableFields = {};

// ── Tabs ──
document.querySelectorAll('.tab').forEach(tab => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
    tab.classList.add('active');
    document.getElementById('tab-' + tab.dataset.tab).classList.add('active');
  });
});

// ── Fetch helpers ──
async function api(path) {
  const r = await fetch(API + path);
  if (!r.ok) throw new Error(`${r.status} ${r.statusText}`);
  return r.json();
}

function fmtTime(iso) {
  if (!iso) return '-';
  const d = new Date(iso);
  return d.toLocaleString('zh-CN', { hour12: false });
}

function fmtDuration(sec) {
  if (sec < 60) return sec.toFixed(1) + 's';
  return (sec / 60).toFixed(1) + 'min';
}

function statusBadge(s) {
  const m = {
    success: 'badge-green', failed: 'badge-red', partial: 'badge-orange',
    running: 'badge-blue', unknown: 'badge-gray',
  };
  return `<span class="badge ${m[s] || 'badge-gray'}">${s}</span>`;
}

// ── Status ──
async function loadStatus() {
  const s = await api('/admin/status');
  document.getElementById('statusGrid').innerHTML = `
    <div class="stat-card ${s.is_healthy ? 'green' : 'red'}">
      <div class="label">Health</div>
      <div class="value">${s.is_healthy ? 'Healthy' : 'Unhealthy'}</div>
      <div class="sub">${s.mode.toUpperCase()} mode</div>
    </div>
    <div class="stat-card">
      <div class="label">Uptime</div>
      <div class="value">${fmtDuration(s.uptime_seconds)}</div>
      <div class="sub">since ${fmtTime(s.started_at)}</div>
    </div>
    <div class="stat-card green">
      <div class="label">Total Analyzed</div>
      <div class="value">${s.total_analyzed}</div>
      <div class="sub">${s.total_success} success / ${s.total_failed} failed</div>
    </div>
    <div class="stat-card">
      <div class="label">Active Now</div>
      <div class="value">${s.active_analyses.length}</div>
      <div class="sub">${s.poller_running ? 'Poller running (' + s.poller_processed_count + ' processed)' : 'Poller idle'}</div>
    </div>
  `;

  if (s.active_analyses.length === 0) {
    document.getElementById('activeList').innerHTML = `
      <div class="empty-state"><div class="icon">-</div>No active analyses</div>`;
  } else {
    document.getElementById('activeList').innerHTML = `<table>
      <tr><th>Bug Key</th><th>Status</th></tr>
      ${s.active_analyses.map(k => `<tr><td>${k}</td><td>${statusBadge('running')}</td></tr>`).join('')}
    </table>`;
  }
}

// ── History ──
async function loadHistory() {
  const h = await api('/admin/history?limit=50');
  if (h.total === 0) {
    document.getElementById('historyTable').innerHTML =
      `<div class="empty-state"><div class="icon">-</div>No analysis records yet</div>`;
    return;
  }
  document.getElementById('historyTable').innerHTML = `<table>
    <tr><th>Bug Key</th><th>Status</th><th>Root Cause</th><th>Duration</th><th>Started</th><th>Finished</th></tr>
    ${h.records.map(r => `<tr>
      <td><strong>${r.bug_key}</strong></td>
      <td>${statusBadge(r.status)}</td>
      <td>${r.root_cause_level || '-'}</td>
      <td>${fmtDuration(r.duration_seconds)}</td>
      <td>${fmtTime(r.started_at)}</td>
      <td>${fmtTime(r.finished_at)}</td>
    </tr>`).join('')}
  </table>`;
}

// ── Errors ──
async function loadErrors() {
  const e = await api('/admin/errors?limit=50');
  if (e.total === 0) {
    document.getElementById('errorsTable').innerHTML =
      `<div class="empty-state"><div class="icon">-</div>No errors recorded</div>`;
    return;
  }
  document.getElementById('errorsTable').innerHTML = `<table>
    <tr><th>Time</th><th>Source</th><th>Bug Key</th><th>Message</th></tr>
    ${e.errors.map(r => `<tr>
      <td style="white-space:nowrap">${fmtTime(r.timestamp)}</td>
      <td><span class="badge badge-red">${r.source}</span></td>
      <td>${r.bug_key || '-'}</td>
      <td style="font-size:13px;color:var(--text-dim);max-width:500px;overflow:hidden;text-overflow:ellipsis">${escHtml(r.message)}</td>
    </tr>`).join('')}
  </table>`;
}

// ── Config ──
async function loadConfig() {
  const [cfg, mf] = await Promise.all([
    api('/admin/config'),
    api('/admin/config/mutable-fields'),
  ]);
  mutableFields = mf;

  let html = '';
  for (const [section, values] of Object.entries(cfg)) {
    if (typeof values !== 'object' || values === null) continue;
    const rows = renderConfigRows(section, values, '');
    html += `<div class="config-section">
      <div class="config-section-title" onclick="toggleSection(this)">
        ${section}
        <span class="arrow">&#9660;</span>
      </div>
      <table class="config-table"><tbody>${rows}</tbody></table>
    </div>`;
  }
  document.getElementById('configBody').innerHTML = html;
}

function renderConfigRows(section, obj, prefix) {
  let rows = '';
  for (const [k, v] of Object.entries(obj)) {
    const fullKey = prefix ? prefix + '.' + k : k;
    if (typeof v === 'object' && v !== null && !Array.isArray(v)) {
      rows += renderConfigRows(section, v, fullKey);
    } else {
      const isMutable = mutableFields[section] && mutableFields[section].includes(k);
      const isSecret = (v === '***');
      let cls = 'config-val';
      if (isSecret) cls += ' secret';
      if (isMutable) cls += ' mutable';
      const displayVal = Array.isArray(v) ? JSON.stringify(v) : String(v);
      const onclick = isMutable
        ? `onclick="openEdit('${section}','${k}','${escAttr(String(v))}')"` : '';
      rows += `<tr>
        <td class="config-key" style="width:40%">${fullKey}</td>
        <td class="${cls}" ${onclick}>${escHtml(displayVal)}</td>
      </tr>`;
    }
  }
  return rows;
}

function toggleSection(el) {
  el.classList.toggle('collapsed');
  el.nextElementSibling.classList.toggle('hidden');
}

// ── Edit Modal ──
let editState = {};
function openEdit(section, key, currentValue) {
  editState = { section, key };
  document.getElementById('editTitle').textContent = `Edit ${section}.${key}`;
  document.getElementById('editLabel').textContent = `${section}.${key}`;
  document.getElementById('editInput').value = currentValue;
  document.getElementById('editModal').classList.add('show');
  document.getElementById('editInput').focus();
}

function closeModal() {
  document.getElementById('editModal').classList.remove('show');
}

document.getElementById('editSave').addEventListener('click', async () => {
  const val = document.getElementById('editInput').value;
  let parsed = val;
  if (!isNaN(Number(val)) && val.trim() !== '') parsed = Number(val);
  else if (val === 'true') parsed = true;
  else if (val === 'false') parsed = false;

  try {
    const r = await fetch(API + '/admin/config', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ section: editState.section, updates: { [editState.key]: parsed } }),
    });
    const data = await r.json();
    if (!r.ok) throw new Error(data.detail || 'Update failed');
    closeModal();
    showToast('success', `Updated ${editState.section}.${editState.key}`);
    loadConfig();
  } catch (e) {
    showToast('error', e.message);
  }
});

document.getElementById('editInput').addEventListener('keydown', e => {
  if (e.key === 'Enter') document.getElementById('editSave').click();
  if (e.key === 'Escape') closeModal();
});

document.getElementById('editModal').addEventListener('click', e => {
  if (e.target === document.getElementById('editModal')) closeModal();
});

// ── Toast ──
function showToast(type, msg) {
  const t = document.getElementById('toast');
  t.className = `toast ${type} show`;
  t.textContent = msg;
  setTimeout(() => t.classList.remove('show'), 3000);
}

// ── Utils ──
function escHtml(s) { const d = document.createElement('div'); d.textContent = s; return d.innerHTML; }
function escAttr(s) { return s.replace(/'/g, "\\'").replace(/"/g, '&quot;'); }

// ── Confluence ──
async function startConfDownload() {
  const url = document.getElementById('confUrl').value.trim();
  if (!url) { showToast('error', 'Please enter a URL or Page ID'); return; }

  const body = { resume: document.getElementById('confResume').checked };
  const depth = parseInt(document.getElementById('confDepth').value);
  if (!isNaN(depth)) body.max_depth = depth;

  const output = document.getElementById('confOutput').value.trim();
  if (output) body.output_dir = output;

  body.download_attachments = document.getElementById('confAttach').checked;

  // Detect if URL or page ID
  if (url.startsWith('http')) {
    body.page_url = url;
  } else {
    body.page_id = url;
  }

  document.getElementById('confStartBtn').disabled = true;
  try {
    const r = await fetch(API + '/admin/confluence/download', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    const data = await r.json();
    if (!r.ok) throw new Error(data.detail || 'Failed to start');
    showToast('success', `Download started: ${data.task_id}`);
    document.getElementById('confUrl').value = '';
    loadConfluence();
  } catch(e) {
    showToast('error', e.message);
  } finally {
    document.getElementById('confStartBtn').disabled = false;
  }
}

async function cancelConfTask(taskId) {
  try {
    const r = await fetch(API + '/admin/confluence/cancel/' + taskId, { method: 'POST' });
    if (!r.ok) { const d = await r.json(); throw new Error(d.detail); }
    showToast('success', 'Cancellation requested');
    loadConfluence();
  } catch(e) {
    showToast('error', e.message);
  }
}

async function loadConfluence() {
  try {
    const p = await api('/admin/confluence/progress');
    const tasks = p.tasks || [];
    if (tasks.length === 0) {
      document.getElementById('confTasks').innerHTML =
        '<div class="empty-state"><div class="icon">-</div>No download tasks yet</div>';
      return;
    }
    document.getElementById('confTasks').innerHTML = `<table>
      <tr><th>Task ID</th><th>Root Page</th><th>Status</th><th>Progress</th><th>Attachments</th><th>Elapsed</th><th>Action</th></tr>
      ${tasks.map(t => {
        const total = t.total_pages_discovered || 1;
        const done = t.pages_downloaded + t.pages_skipped;
        const pct = Math.round((done / total) * 100);
        const isRunning = t.status === 'running';
        return `<tr>
          <td style="font-size:12px;font-family:monospace">${escHtml(t.task_id)}</td>
          <td><strong>${escHtml(t.root_page_title || t.root_page_id)}</strong></td>
          <td>${statusBadge(t.status === 'cancelled' ? 'failed' : t.status === 'completed' ? 'success' : t.status)}</td>
          <td style="min-width:180px">
            <div style="display:flex;align-items:center;gap:8px">
              <div class="progress-bar-bg" style="flex:1">
                <div class="progress-bar-fill" style="width:${pct}%"></div>
              </div>
              <span style="font-size:12px;white-space:nowrap">${done}/${total} (${t.pages_failed} err)</span>
            </div>
          </td>
          <td>${t.attachments_downloaded}${t.attachments_failed ? ' <span style="color:var(--red)">(' + t.attachments_failed + ' err)</span>' : ''}</td>
          <td>${fmtDuration(t.elapsed_seconds)}</td>
          <td>${isRunning ? '<button class="btn-cancel-task" onclick="cancelConfTask(\'' + escAttr(t.task_id) + '\')">Cancel</button>' : '-'}</td>
        </tr>`;
      }).join('')}
    </table>`;
  } catch(e) {
    // Confluence not configured -- show info
    document.getElementById('confTasks').innerHTML =
      '<div class="empty-state"><div class="icon">-</div>Confluence not configured</div>';
  }
}

// ── Refresh ──
async function refreshAll() {
  try {
    await Promise.all([loadStatus(), loadHistory(), loadErrors(), loadConfluence(), loadConfig()]);
    document.getElementById('lastUpdate').textContent = 'Updated: ' + new Date().toLocaleTimeString('zh-CN', { hour12: false });
  } catch(e) {
    showToast('error', 'Failed to fetch: ' + e.message);
  }
}

// Auto-refresh
let timer;
function startAutoRefresh() {
  timer = setInterval(() => {
    if (document.getElementById('autoRefresh').checked) refreshAll();
  }, 10000);
}

// Init
refreshAll();
startAutoRefresh();
</script>
</body>
</html>
"""


@dashboard_router.get("/", response_class=HTMLResponse)
async def dashboard_page() -> HTMLResponse:
    """返回管理面板 HTML 页面。"""
    return HTMLResponse(content=DASHBOARD_HTML)
