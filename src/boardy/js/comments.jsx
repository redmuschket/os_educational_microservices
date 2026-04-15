const { useState, useEffect } = React;
const API = 'https://api.comeblom.ai-info.ru';
const PARENT_ID = 1;

function CommentsList() {
  const [items, setItems] = useState([]);
  const [text, setText] = useState('');
  const [editId, setEditId] = useState(null);
  const [editText, setEditText] = useState('');
  const [loading, setLoading] = useState(false);

  const load = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API}/api/posts/${PARENT_ID}/comments`);
      const data = await res.json();
      setItems(data.items);
    } catch (e) {
      console.error('Ошибка загрузки:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const add = async () => {
    if (!text.trim()) return;
    await fetch(`${API}/api/posts/${PARENT_ID}/comments`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({body: text})
    });
    setText('');
    load();
  };

  const save = async (id) => {
    await fetch(`${API}/api/comments/${id}`, {
      method: 'PUT',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({body: editText})
    });
    setEditId(null);
    load();
  };

  const del = async (id) => {
    if (!confirm('Удалить комментарий?')) return;
    await fetch(`${API}/api/comments/${id}`, {method: 'DELETE'});
    load();
  };

  return (
    <div>
      {items.map(item => (
        <div key={item.id} className="card mb-2">
          <div className="card-body">
            <div className="d-flex justify-content-between">
              <strong>{item.author_name}</strong>
              <small className="text-muted">{item.created_at}</small>
            </div>
            {editId === item.id ? (
              <div className="input-group mt-2">
                <input
                  className="form-control form-control-sm"
                  value={editText}
                  onChange={e => setEditText(e.target.value)}
                />
                <button className="btn btn-sm btn-success" onClick={() => save(item.id)}>✓</button>
                <button className="btn btn-sm btn-secondary" onClick={() => setEditId(null)}>✕</button>
              </div>
            ) : (
              <div>
                <p className="mb-1">{item.body}</p>
                <button className="btn btn-sm btn-outline-secondary me-1" onClick={() => { setEditId(item.id); setEditText(item.body); }}>✏️</button>
                <button className="btn btn-sm btn-outline-danger" onClick={() => del(item.id)}>🗑️</button>
              </div>
            )}
          </div>
        </div>
      ))}

      <div className="input-group mt-3">
        <input
          className="form-control"
          placeholder="Комментарий..."
          value={text}
          onChange={e => setText(e.target.value)}
          onKeyPress={e => e.key === 'Enter' && add()}
        />
        <button className="btn btn-primary" onClick={add} disabled={loading}>
          {loading ? '...' : 'Отправить'}
        </button>
      </div>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById('app')).render(<CommentsList />);
