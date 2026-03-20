import { useState } from 'react';
import type { KeyboardEvent } from 'react';
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
    <div className="page--narrow">
      <div className="page-header">
        <button className="btn" onClick={() => navigate('/dashboard')}>← 돌아가기</button>
        <h2>🛒 장보기 리스트</h2>
      </div>

      {/* 입력 */}
      <div className="flex gap-sm mb-xl">
        <input
          className="input"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="재료 입력 (예: 소고기 200g)"
          style={{ fontSize: 15 }}
        />
        <button
          className="btn btn--primary"
          onClick={handleAdd}
          disabled={!input.trim() || addItem.isPending}
        >
          추가
        </button>
      </div>

      {isLoading && <p className="text-muted text-center">불러오는 중...</p>}

      {/* 미체크 항목 */}
      {unchecked.length > 0 && (
        <ul style={{ listStyle: 'none', padding: 0, margin: '0 0 24px' }}>
          {unchecked.map(item => (
            <li
              key={item.id}
              className="flex items-center gap-md"
              style={{ padding: '10px 0', borderBottom: '1px solid var(--color-border-light)' }}
            >
              <input
                type="checkbox"
                checked={false}
                onChange={() => toggleItem.mutate({ id: item.id, is_checked: true })}
                style={{ width: 18, height: 18, cursor: 'pointer' }}
              />
              <span style={{ flex: 1, fontSize: 15 }}>{item.name}</span>
              <button
                className="btn--ghost text-sm text-muted"
                onClick={() => deleteItem.mutate(item.id)}
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
          <div className="flex justify-between items-center mb-sm">
            <span className="text-sm text-muted">완료 {checked.length}개</span>
            <button
              className="btn--ghost text-sm text-danger"
              onClick={() => clearChecked.mutate()}
            >
              완료 항목 삭제
            </button>
          </div>
          <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
            {checked.map(item => (
              <li
                key={item.id}
                className="flex items-center gap-md"
                style={{
                  padding: '10px 0',
                  borderBottom: '1px solid var(--color-border-light)',
                  opacity: 0.5,
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
                  className="btn--ghost text-sm text-muted"
                  onClick={() => deleteItem.mutate(item.id)}
                >
                  삭제
                </button>
              </li>
            ))}
          </ul>
        </>
      )}

      {!isLoading && items.length === 0 && (
        <p className="text-muted text-center" style={{ marginTop: 60 }}>
          장보기 항목을 추가해보세요
        </p>
      )}
    </div>
  );
}
