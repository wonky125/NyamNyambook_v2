import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { useRecipes, useSearch, useMarkCooked, useDeleteRecipe } from '../hooks/useRecipes';

export default function Dashboard() {
  const { signOut } = useAuth();
  const navigate = useNavigate();
  const [query, setQuery] = useState('');

  const { data: recipes, isLoading } = useRecipes();
  const { data: searchResults } = useSearch(query);
  const markCooked = useMarkCooked();
  const deleteRecipe = useDeleteRecipe();

  const items = query.trim() ? searchResults ?? [] : recipes ?? [];

  return (
    <div style={{ maxWidth: 900, margin: '0 auto', padding: 20 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
        <h1 style={{ margin: 0 }}>🍚 냠냠북</h1>
        <div style={{ display: 'flex', gap: 8 }}>
          <button onClick={() => navigate('/add')}>+ 레시피 추가</button>
          <button onClick={() => signOut()}>로그아웃</button>
        </div>
      </div>

      <input
        placeholder="레시피 또는 재료 검색"
        value={query}
        onChange={e => setQuery(e.target.value)}
        style={{ width: '100%', padding: '10px 12px', fontSize: 16, marginBottom: 20, boxSizing: 'border-box' }}
      />

      {isLoading && <p>불러오는 중...</p>}

      {items.length === 0 && !isLoading && (
        <p style={{ textAlign: 'center', color: '#888', marginTop: 60 }}>
          {query ? '검색 결과가 없습니다' : '레시피를 추가해보세요!'}
        </p>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))', gap: 16 }}>
        {items.map(recipe => (
          <div key={recipe.id} style={{ border: '1px solid #ddd', borderRadius: 8, overflow: 'hidden', cursor: 'pointer' }}>
            {recipe.image_url && (
              <img src={recipe.image_url} alt={recipe.title} style={{ width: '100%', height: 160, objectFit: 'cover' }} />
            )}
            <div style={{ padding: 12 }}>
              <h3 style={{ margin: '0 0 6px', fontSize: 15 }} onClick={() => navigate(`/recipes/${recipe.id}`)}>
                {recipe.title}
              </h3>
              <div style={{ fontSize: 13, color: '#666', marginBottom: 8 }}>
                {recipe.total_time && <span>⏱ {recipe.total_time}분 · </span>}
                <span>🍳 {recipe.cooked_count}회</span>
              </div>
              {recipe.tags.length > 0 && (
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4, marginBottom: 8 }}>
                  {recipe.tags.slice(0, 3).map(t => (
                    <span key={t.id} style={{ background: '#f0f0f0', padding: '2px 8px', borderRadius: 12, fontSize: 12 }}>
                      {t.name}
                    </span>
                  ))}
                </div>
              )}
              <div style={{ display: 'flex', gap: 6 }}>
                <button onClick={() => markCooked.mutate(recipe.id)} style={{ flex: 1, fontSize: 12 }}>요리했어요</button>
                <button onClick={() => navigate(`/recipes/${recipe.id}/edit`)} style={{ fontSize: 12 }}>편집</button>
                <button onClick={() => { if (confirm('삭제할까요?')) deleteRecipe.mutate(recipe.id); }} style={{ fontSize: 12 }}>삭제</button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
