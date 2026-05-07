// If the API is on the same origin, use a relative path.
// Otherwise you can set window.API_URL to the backend host, e.g. http://157.230.222.82
const API_URL = window.API_URL || '';
const API_PREFIX = `${API_URL}/api`;

function showToast(msg) {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 2500);
}

function showError(msg) {
  const el = document.getElementById('error');
  el.style.display = msg ? 'block' : 'none';
  el.textContent = msg;
}

async function loadItems() {
  try {
    const res = await fetch(`${API_PREFIX}/data`);
    if (!res.ok) throw new Error('Ошибка сервера');
    const items = await res.json();
    showError('');
    renderItems(items);
    document.getElementById('totalCount').textContent = items.length;
  } catch (e) {
    showError('Не удалось подключиться к серверу: ' + e.message);
    document.getElementById('list').innerHTML = '<div class="empty"><div class="icon">⚠️</div><p>Ошибка загрузки</p></div>';
  }
}

function renderItems(items) {
  const list = document.getElementById('list');
  if (!items.length) {
    list.innerHTML = '<div class="empty"><div class="icon">📋</div><p>Задач пока нет. Добавьте первую!</p></div>';
    return;
  }
  list.innerHTML = '';
  items.forEach((item, i) => {
    const div = document.createElement('div');
    div.className = 'item-card';
    const date = item.created_at ? new Date(item.created_at).toLocaleDateString('ru-RU') : '';
    div.innerHTML = `
      <div class="item-num">${i + 1}</div>
      <div class="item-text">${escapeHtml(item.text)}</div>
      <div class="item-date">${date}</div>
      <button class="btn-del" onclick="deleteItem(${item.id})" title="Удалить">🗑</button>
    `;
    list.appendChild(div);
  });
}

function escapeHtml(text) {
  return text.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

async function addItem() {
  const input = document.getElementById('newItem');
  const text = input.value.trim();
  if (!text) return;
  const btn = document.getElementById('addBtn');
  btn.disabled = true;
  btn.textContent = '...';
  try {
    const res = await fetch(`${API_PREFIX}/data`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({text})
    });
    if (!res.ok) throw new Error('Ошибка добавления');
    input.value = '';
    showToast('✓ Задача добавлена');
    await loadItems();
  } catch(e) {
    showError(e.message);
  } finally {
    btn.disabled = false;
    btn.textContent = '+ Добавить';
  }
}

async function deleteItem(id) {
  try {
    await fetch(`${API_PREFIX}/data/${id}`, {method: 'DELETE'});
    showToast('Задача удалена');
    await loadItems();
  } catch(e) {
    showError(e.message);
  }
}

loadItems();