import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { useInfiniteRecipes, useSearch, useMarkCooked, useDeleteRecipe, useTags } from '../hooks/useRecipes';

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

  const {
    data: recipesData,
    isLoading,
    isError,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
  } = useInfiniteRecipes(selectedTagId ? { tag_id: selectedTagId } : undefined);

  const { data: searchResults } = useSearch(query);
  const { data: tags } = useTags();
  const markCooked = useMarkCooked();
  const deleteRecipe = useDeleteRecipe();

  const toggleTag = (id: number) => setSelectedTagId(prev => prev === id ? null : id);

  const allRecipes = recipesData?.pages.flatMap(p => p.items) ?? [];
  const baseItems = query.trim() ? (searchResults ?? []) : allRecipes;
  const items = query.trim() ? baseItems : baseItems.filter(r => {
    if ('max' in cookedFilter && cookedFilter.max === 0) return r.cooked_count === 0;
    return r.cooked_count >= cookedFilter.min;
  });

  return (
    <div className="page--wide">
      {/* 헤더 */}
      <div className="page-header">
        <h1 style={{ fontSize: 26 }}>🍚 냠냠북</h1>
        <div className="flex gap-sm">
          <button className="btn btn--primary" onClick={() => navigate('/add')}>+ 레시피 추가</button>
          <button className="btn" onClick={() => navigate('/shopping')}>🛒 장보기</button>
          <button className="btn" onClick={() => signOut()}>로그아웃</button>
        </div>
      </div>

      {/* 검색 */}
      <input
        className="input mb-md"
        style={{ fontSize: 16 }}
        placeholder="레시피 또는 재료 검색"
        value={query}
        onChange={e => setQuery(e.target.value)}
      />

      {/* 태그 필터 */}
      {tags && tags.length > 0 && (
        <div className="flex flex-wrap gap-xs mb-sm">
          {tags.map(tag => (
            <span
              key={tag.id}
              onClick={() => toggleTag(tag.id)}
              className={`chip chip--clickable chip--filter ${selectedTagId === tag.id ? 'chip--active' : ''}`}
            >
              {tag.name}
            </span>
          ))}
        </div>
      )}

      {/* 요리횟수 필터 */}
      <div className="flex gap-xs mb-xl">
        {COOKED_FILTERS.map(f => (
          <button
            key={f.label}
            onClick={() => setCookedFilter(f)}
            className={`btn btn--sm btn--pill ${cookedFilter.label === f.label ? 'btn--accent' : ''}`}
          >
            {f.label}
          </button>
        ))}
      </div>

      {isLoading && <p className="text-muted text-center mt-xl">불러오는 중...</p>}

      {isError && (
        <p className="text-danger text-center mt-xl">
          레시피를 불러오지 못했습니다. 새로고침 해주세요.
        </p>
      )}

      {items.length === 0 && !isLoading && !isError && (
        <p className="text-muted text-center" style={{ marginTop: 60 }}>
          {query ? '검색 결과가 없습니다' : '레시피를 추가해보세요!'}
        </p>
      )}

      {/* 레시피 카드 그리드 */}
      <div className="recipe-grid">
        {items.map(recipe => (
          <div
            key={recipe.id}
            className="card"
            onClick={() => navigate(`/recipes/${recipe.id}`)}
          >
            {recipe.image_url && (
              <img className="card__img" src={recipe.image_url} alt={recipe.title} />
            )}
            <div className="card__body">
              <h3 className="card__title">{recipe.title}</h3>
              <div className="card__meta">
                {recipe.total_time && <span>⏱ {recipe.total_time}분 · </span>}
                <span>🍳 {recipe.cooked_count}회</span>
              </div>
              {recipe.tags.length > 0 && (
                <div className="card__tags">
                  {recipe.tags.slice(0, 3).map(t => (
                    <span key={t.id} className="chip">{t.name}</span>
                  ))}
                </div>
              )}
              <div className="card__actions">
                <button
                  className="btn btn--sm"
                  style={{ flex: 1 }}
                  onClick={e => { e.stopPropagation(); markCooked.mutate(recipe.id); }}
                >
                  요리했어요
                </button>
                <button
                  className="btn btn--sm"
                  onClick={e => { e.stopPropagation(); navigate(`/recipes/${recipe.id}/edit`); }}
                >
                  편집
                </button>
                <button
                  className="btn btn--sm"
                  onClick={e => { e.stopPropagation(); if (confirm('삭제할까요?')) deleteRecipe.mutate(recipe.id); }}
                >
                  삭제
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {!query.trim() && hasNextPage && (
        <div className="text-center mt-xl">
          <button
            className="btn btn--lg"
            onClick={() => fetchNextPage()}
            disabled={isFetchingNextPage}
          >
            {isFetchingNextPage ? '불러오는 중...' : '더 보기'}
          </button>
        </div>
      )}
    </div>
  );
}
