import { useState, KeyboardEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  useShoppingItems,
  useAddShoppingItem,
  useToggleShoppingItem,
  useDeleteShoppingItem,
  useClearChecked,
} from '../hooks/useShopping';

export default function Shopping() {
  const navigate = useNavigate();
  const [input, setInput] = useState('');

  const { data: items = [], isLoading } = useShoppingItems();
  const addItem = useAddShoppingItem();
  const toggleItem = useToggleShoppingItem();
  const deleteItem = useDeleteShoppingItem();
  const clearChecked = useClearChecked();

  const unchecked = items.filter(i => !i.is_checked);
  const checked = items.filter(i => i.is_checked);

  const handleAdd = () => {
    const name = input.trim();
    if (!name) return;
    addItem.mutate(name);
    setInput('');
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') handleAdd();
  };

  return (
    <div style={{ maxWidth: 600, margin: '0 auto', padding: 20 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 24 }}>
        <button onClick={() => navigate('/dashboard')} style={{ fontSize: 13 }}>← 돌아가기</button>
        <h1 style={{ margin: 0, fontSize: 22 }}>🛒 장보기 리스트</h1>
      </div>

      {/* 입력 */}
      <div style={{ display: 'flex', gap: 8, marginBottom: 24 }}>
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="재료 입력 (예: 소고기 200g)"
          style={{ flex: 1, padding: '10px 12px', fontSize: 15 }}
        />
        <button onClick={handleAdd} disabled={!input.trim() || addItem.isPending}>
          추가
        </button>
      </div>

      {isLoading && <p>불러오는 중...</p>}

      {/* 미체크 항목 */}
      {unchecked.length > 0 && (
        <ul style={{ listStyle: 'none', padding: 0, margin: '0 0 24px' }}>
          {unchecked.map(item => (
            <li
              key={item.id}
              style={{
                display: 'flex', alignItems: 'center', gap: 10,
                padding: '10px 0', borderBottom: '1px solid #f0f0f0',
              }}
            >
              <input
                type="checkbox"
                checked={false}
                onChange={() => toggleItem.mutate({ id: item.id, is_checked: true })}
                style={{ width: 18, height: 18, cursor: 'pointer' }}
              />
              <span style={{ flex: 1, fontSize: 15 }}>{item.name}</span>
              <button
                onClick={() => deleteItem.mutate(item.id)}
                style={{ fontSize: 12, color: '#999', background: 'none', border: 'none', cursor: 'pointer' }}
              >
                삭제
              </button>
            </li>
          ))}
        </ul>
      )}

      {/* 체크된 항목 */}
      {checked.length > 0 && (
        <>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
            <span style={{ fontSize: 13, color: '#888' }}>완료 {checked.length}개</span>
            <button
              onClick={() => clearChecked.mutate()}
              style={{ fontSize: 12, color: '#e53e3e', background: 'none', border: 'none', cursor: 'pointer' }}
            >
              완료 항목 삭제
            </button>
          </div>
          <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
            {checked.map(item => (
              <li
                key={item.id}
                style={{
                  display: 'flex', alignItems: 'center', gap: 10,
                  padding: '10px 0', borderBottom: '1px solid #f0f0f0', opacity: 0.5,
                }}
              >
                <input
                  type="checkbox"
                  checked={true}
                  onChange={() => toggleItem.mutate({ id: item.id, is_checked: false })}
                  style={{ width: 18, height: 18, cursor: 'pointer' }}
                />
                <span style={{ flex: 1, fontSize: 15, textDecoration: 'line-through' }}>{item.name}</span>
                <button
                  onClick={() => deleteItem.mutate(item.id)}
                  style={{ fontSize: 12, color: '#999', background: 'none', border: 'none', cursor: 'pointer' }}
                >
                  삭제
                </button>
              </li>
            ))}
          </ul>
        </>
      )}

      {!isLoading && items.length === 0 && (
        <p style={{ textAlign: 'center', color: '#888', marginTop: 60 }}>
          장보기 항목을 추가해보세요
        </p>
      )}
    </div>
  );
}
