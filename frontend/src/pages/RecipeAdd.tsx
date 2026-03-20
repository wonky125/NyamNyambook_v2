import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useScrape, useCreateRecipe } from '../hooks/useRecipes';
import api from '../lib/api';
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
  const [selectedTagNames, setSelectedTagNames] = useState<string[]>([]);

  const handleScrape = async () => {
    const result = await scrape.mutateAsync(url);
    setScraped(result);
    setSelectedTagNames([]);
    if (result.scrape_success) {
      setTitle(result.title ?? '');
      setDescription(result.description ?? '');
      setServings(result.servings ?? '');
    }
  };

  const toggleTag = (name: string) => {
    setSelectedTagNames(prev =>
      prev.includes(name) ? prev.filter(t => t !== name) : [...prev, name]
    );
  };

  const handleSave = async () => {
    if (!title.trim()) return alert('레시피 이름을 입력해주세요');

    const tagResults = await Promise.all(
      selectedTagNames.map(name => api.post('/tags', { name }).then(r => r.data.id as number))
    );

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
      tag_ids: tagResults,
    });
    navigate('/');
  };

  return (
    <div className="page--narrow">
      <div className="page-header">
        <button className="btn" onClick={() => navigate('/')}>← 뒤로</button>
        <h2>레시피 추가</h2>
      </div>

      {/* URL 스크래핑 */}
      <div className="box box--subtle mb-xl">
        <p className="text-bold mb-sm">URL로 불러오기</p>
        <div className="flex gap-sm">
          <input
            className="input"
            placeholder="https://10000recipe.com/..."
            value={url}
            onChange={e => setUrl(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleScrape()}
          />
          <button
            className="btn btn--primary"
            onClick={handleScrape}
            disabled={scrape.isPending || !url.trim()}
          >
            {scrape.isPending ? '불러오는 중...' : '불러오기'}
          </button>
        </div>
        {scraped && (
          <p className={`text-sm mt-sm ${scraped.scrape_success ? 'text-success' : ''}`} style={{ color: scraped.scrape_success ? undefined : 'orange' }}>
            {scraped.scrape_success ? `✓ 불러오기 성공: ${scraped.title}` : '스크래핑 실패 — 직접 입력해주세요'}
          </p>
        )}
      </div>

      {/* 직접 입력 */}
      <div className="form">
        <div className="form-group">
          <label className="label">레시피 이름 *</label>
          <input className="input" value={title} onChange={e => setTitle(e.target.value)} />
        </div>

        <div className="form-group">
          <label className="label">설명</label>
          <textarea className="textarea" value={description} onChange={e => setDescription(e.target.value)} rows={3} />
        </div>

        <div className="form-group">
          <label className="label">인분</label>
          <input className="input" value={servings} onChange={e => setServings(e.target.value)} />
        </div>

        <div className="form-group">
          <label className="label">메모</label>
          <textarea className="textarea textarea--note" value={notes} onChange={e => setNotes(e.target.value)} rows={2} />
        </div>

        {/* 태그 제안 */}
        {scraped?.suggested_tags && scraped.suggested_tags.length > 0 && (
          <div className="box box--accent">
            <p className="box__title">태그 제안 (클릭해서 선택)</p>
            <div className="flex flex-wrap gap-xs">
              {scraped.suggested_tags.map(tag => (
                <span
                  key={tag}
                  onClick={() => toggleTag(tag)}
                  className={`chip chip--clickable ${selectedTagNames.includes(tag) ? 'chip--active' : ''}`}
                >
                  {tag}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* 스크래핑 결과 미리보기 */}
        {scraped?.ingredients && scraped.ingredients.length > 0 && (
          <div className="box box--info">
            <p className="box__title">재료 ({scraped.ingredients.length}개)</p>
            {scraped.ingredients.slice(0, 5).map((ing, i) => (
              <p key={i} className="text-sm">{ing.name} {ing.amount} {ing.unit}</p>
            ))}
            {scraped.ingredients.length > 5 && (
              <p className="text-sm text-muted">...외 {scraped.ingredients.length - 5}개</p>
            )}
          </div>
        )}

        {scraped?.steps && scraped.steps.length > 0 && (
          <div className="box box--info">
            <p className="box__title">조리 단계 ({scraped.steps.length}단계)</p>
            {scraped.steps.slice(0, 3).map((s, i) => (
              <p key={i} className="text-sm">{s.step_number}. {s.instruction.slice(0, 60)}...</p>
            ))}
          </div>
        )}

        <button
          className="btn btn--primary btn--block btn--lg mt-sm"
          onClick={handleSave}
          disabled={createRecipe.isPending}
        >
          {createRecipe.isPending ? '저장 중...' : '저장'}
        </button>
      </div>
    </div>
  );
}
