import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useScrape, useCreateRecipe } from '../hooks/useRecipes';
import type { ScrapeResult } from '../types';

export default function RecipeAdd() {
  const navigate = useNavigate();
  const scrape = useScrape();
  const createRecipe = useCreateRecipe();

  const [url, setUrl] = useState('');
  const [scraped, setScraped] = useState<ScrapeResult | null>(null);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [servings, setServings] = useState('');
  const [notes, setNotes] = useState('');

  const handleScrape = async () => {
    const result = await scrape.mutateAsync(url);
    setScraped(result);
    if (result.scrape_success) {
      setTitle(result.title ?? '');
      setDescription(result.description ?? '');
      setServings(result.servings ?? '');
    }
  };

  const handleSave = async () => {
    if (!title.trim()) return alert('레시피 이름을 입력해주세요');
    await createRecipe.mutateAsync({
      title,
      description: description || null,
      servings: servings || null,
      notes: notes || null,
      source_url: scraped?.source_url ?? (url || null),
      source_type: scraped?.source_type ?? null,
      image_url: scraped?.image_url ?? null,
      prep_time: scraped?.prep_time ?? null,
      cook_time: scraped?.cook_time ?? null,
      total_time: scraped?.total_time ?? null,
      steps: scraped?.steps.map((s, i) => ({ step_number: i + 1, instruction: s.instruction })) ?? [],
      ingredients: scraped?.ingredients.map((ing, i) => ({ name: ing.name, amount: ing.amount, unit: ing.unit, sort_order: i })) ?? [],
      tag_ids: [],
    });
    navigate('/');
  };

  return (
    <div style={{ maxWidth: 600, margin: '0 auto', padding: 20 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 24 }}>
        <button onClick={() => navigate('/')}>← 뒤로</button>
        <h2 style={{ margin: 0 }}>레시피 추가</h2>
      </div>

      {/* URL 스크래핑 */}
      <div style={{ background: '#f9f9f9', padding: 16, borderRadius: 8, marginBottom: 20 }}>
        <p style={{ margin: '0 0 8px', fontWeight: 'bold' }}>URL로 불러오기</p>
        <div style={{ display: 'flex', gap: 8 }}>
          <input
            placeholder="https://10000recipe.com/..."
            value={url}
            onChange={e => setUrl(e.target.value)}
            style={{ flex: 1, padding: '8px 12px' }}
            onKeyDown={e => e.key === 'Enter' && handleScrape()}
          />
          <button onClick={handleScrape} disabled={scrape.isPending || !url.trim()}>
            {scrape.isPending ? '불러오는 중...' : '불러오기'}
          </button>
        </div>
        {scraped && (
          <p style={{ margin: '8px 0 0', fontSize: 13, color: scraped.scrape_success ? 'green' : 'orange' }}>
            {scraped.scrape_success ? `✓ 불러오기 성공: ${scraped.title}` : '스크래핑 실패 — 직접 입력해주세요'}
          </p>
        )}
      </div>

      {/* 직접 입력 */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
        <div>
          <label style={{ display: 'block', marginBottom: 4, fontSize: 14 }}>레시피 이름 *</label>
          <input value={title} onChange={e => setTitle(e.target.value)} style={{ width: '100%', padding: '8px 12px', boxSizing: 'border-box' }} />
        </div>
        <div>
          <label style={{ display: 'block', marginBottom: 4, fontSize: 14 }}>설명</label>
          <textarea value={description} onChange={e => setDescription(e.target.value)} rows={3} style={{ width: '100%', padding: '8px 12px', boxSizing: 'border-box' }} />
        </div>
        <div>
          <label style={{ display: 'block', marginBottom: 4, fontSize: 14 }}>인분</label>
          <input value={servings} onChange={e => setServings(e.target.value)} style={{ width: '100%', padding: '8px 12px', boxSizing: 'border-box' }} />
        </div>
        <div>
          <label style={{ display: 'block', marginBottom: 4, fontSize: 14 }}>메모</label>
          <textarea value={notes} onChange={e => setNotes(e.target.value)} rows={2} style={{ width: '100%', padding: '8px 12px', boxSizing: 'border-box' }} />
        </div>

        {/* 스크래핑된 재료/단계 미리보기 */}
        {scraped?.ingredients && scraped.ingredients.length > 0 && (
          <div style={{ background: '#f0f7ff', padding: 12, borderRadius: 6 }}>
            <p style={{ margin: '0 0 6px', fontWeight: 'bold', fontSize: 14 }}>재료 ({scraped.ingredients.length}개)</p>
            {scraped.ingredients.slice(0, 5).map((ing, i) => (
              <p key={i} style={{ margin: '2px 0', fontSize: 13 }}>{ing.name} {ing.amount} {ing.unit}</p>
            ))}
            {scraped.ingredients.length > 5 && <p style={{ margin: '2px 0', fontSize: 13, color: '#888' }}>...외 {scraped.ingredients.length - 5}개</p>}
          </div>
        )}

        {scraped?.steps && scraped.steps.length > 0 && (
          <div style={{ background: '#f0f7ff', padding: 12, borderRadius: 6 }}>
            <p style={{ margin: '0 0 6px', fontWeight: 'bold', fontSize: 14 }}>조리 단계 ({scraped.steps.length}단계)</p>
            {scraped.steps.slice(0, 3).map((s, i) => (
              <p key={i} style={{ margin: '2px 0', fontSize: 13 }}>{s.step_number}. {s.instruction.slice(0, 60)}...</p>
            ))}
          </div>
        )}

        <button onClick={handleSave} disabled={createRecipe.isPending} style={{ padding: '12px', fontSize: 16, marginTop: 8 }}>
          {createRecipe.isPending ? '저장 중...' : '저장'}
        </button>
      </div>
    </div>
  );
}
