const API = 'https://api.comeblom.ai-info.ru';
const PARENT_ID = 1;

function esc(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

async function loadItems() {
  const res = await fetch(`${API}/api/posts/${PARENT_ID}/comments`);
  const data = await res.json();
  document.getElementById('list').innerHTML = data.items.map(item => `
    <div>
      <strong>${esc(item.author_name)}</strong>
      <small>${esc(item.created_at)}</small>
      <p>${esc(item.body)}</p>
    </div>
  `).join('');
}

document.getElementById('btn').addEventListener('click', async () => {
  const body = document.getElementById('body').value.trim();
  if (!body) return;
  
  await fetch(`${API}/api/posts/${PARENT_ID}/comments`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({body: body})
  });
  
  document.getElementById('body').value = '';
  loadItems();
});

loadItems();
