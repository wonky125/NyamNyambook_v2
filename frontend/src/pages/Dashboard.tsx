import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { useRecipes, useSearch, useMarkCooked, useDeleteRecipe, useTags } from '../hooks/useRecipes';

const COOKED_FILTERS = [
  { label: '전체', min: 0 },
  { label: '도전 예정', min: 0, max: 0 },
  { label: '1회+', min: 1 },
  { label: '3회+', min: 3 },
] as const;

type CookedFilter = typeof COOKED_FILTERS[number];

export default function Dashboard() {
  const { signOut } = useAuth();
  const navigate = useNavigate();
  const [query, setQuery] = useState('');
  const [selectedTagId, setSelectedTagId] = useState<number | null>(null);
  const [cookedFilter, setCookedFilter] = useState<CookedFilter>(COOKED_FILTERS[0]);

  const { data: recipes, isLoading, isError } = useRecipes(
    selectedTagId ? { tag_id: selectedTagId } : undefined
  );
  const { data: searchResults } = useSearch(query);
  const { data: tags } = useTags();
  const markCooked = useMarkCooked();
  const deleteRecipe = useDeleteRecipe();

  const toggleTag = (id: number) => setSelectedTagId(prev => prev === id ? null : id);

  // 검색 중이면 검색 결과, 아니면 태그필터+요리횟수 필터 적용
  const baseItems = query.trim() ? (searchResults ?? []) : (recipes ?? []);
  const items = query.trim() ? baseItems : baseItems.filter(r => {
    if ('max' in cookedFilter && cookedFilter.max === 0) return r.cooked_count === 0;
    return r.cooked_count >= cookedFilter.min;
  });

  return (
    <div style={{ maxWidth: 900, margin: '0 auto', padding: 20 }}>
      {/* 헤더 */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
        <h1 style={{ margin: 0 }}>🍚 냠냠북</h1>
        <div style={{ display: 'flex', gap: 8 }}>
          <button onClick={() => navigate('/add')}>+ 레시피 추가</button>
          <button onClick={() => signOut()}>로그아웃</button>
        </div>
      </div>

      {/* 검색창 */}
      <input
        placeholder="레시피 또는 재료 검색"
        value={query}
        onChange={e => setQuery(e.target.value)}
        style={{ width: '100%', padding: '10px 12px', fontSize: 16, marginBottom: 12, boxSizing: 'border-box' }}
      />

      {/* 태그 필터 */}
      {tags && tags.length > 0 && (
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginBottom: 10 }}>
          {tags.map(tag => (
            <span
              key={tag.id}
              onClick={() => toggleTag(tag.id)}
              style={{
                padding: '4px 12px', borderRadius: 16, fontSize: 13, cursor: 'pointer',
                background: selectedTagId === tag.id ? '#f5a623' : '#f0f0f0',
                color: selectedTagId === tag.id ? '#fff' : '#444',
                userSelect: 'none',
              }}
            >
              {tag.name}
            </span>
          ))}
        </div>
      )}

      {/* 요리횟수 필터 */}
      <div style={{ display: 'flex', gap: 6, marginBottom: 20 }}>
        {COOKED_FILTERS.map(f => (
          <button
            key={f.label}
            onClick={() => setCookedFilter(f)}
            style={{
              padding: '4px 12px', fontSize: 13, borderRadius: 16, cursor: 'pointer',
              background: cookedFilter.label === f.label ? '#555' : '#f0f0f0',
              color: cookedFilter.label === f.label ? '#fff' : '#444',
              border: 'none',
            }}
          >
            {f.label}
          </button>
        ))}
      </div>

      {isLoading && <p>불러오는 중...</p>}

      {isError && (
        <p style={{ textAlign: 'center', color: '#e53e3e', marginTop: 40 }}>
          레시피를 불러오지 못했습니다. 새로고침 해주세요.
        </p>
      )}

      {items.length === 0 && !isLoading && !isError && (
        <p style={{ textAlign: 'center', color: '#888', marginTop: 60 }}>
          {query ? '검색 결과가 없습니다' : '레시피를 추가해보세요!'}
        </p>
      )}

      {/* 레시피 카드 그리드 */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))', gap: 16 }}>
        {items.map(recipe => (
          <div key={recipe.id} style={{ border: '1px solid #ddd', borderRadius: 8, overflow: 'hidden', cursor: 'pointer' }}>
            {recipe.image_url && (
              <img src={recipe.image_url} alt={recipe.title} style={{ width: '100%', height: 160, objectFit: 'cover' }} />
            )}
            <div style={{ padding: 12 }}>
              <h3
                style={{ margin: '0 0 6px', fontSize: 15 }}
                onClick={() => navigate(`/recipes/${recipe.id}`)}
              >
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
                <button
                  onClick={() => { if (confirm('삭제할까요?')) deleteRecipe.mutate(recipe.id); }}
                  style={{ fontSize: 12 }}
                >
                  삭제
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
