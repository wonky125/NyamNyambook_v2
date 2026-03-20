import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useRecipe, useUpdateRecipe, useUploadImage } from '../hooks/useRecipes';
import { useTags } from '../hooks/useRecipes';

export default function RecipeEdit() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data: recipe } = useRecipe(Number(id));
  const update = useUpdateRecipe(Number(id));
  const uploadImage = useUploadImage();
  const { data: allTagsData } = useTags();
  const fileInputRef = useRef<HTMLInputElement>(null);

  // 이미지 버그 fix: 한 번만 초기화 (recipe 재조회로 덮어쓰기 방지)
  const hasInitialized = useRef(false);

  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [servings, setServings] = useState('');
  const [notes, setNotes] = useState('');
  const [ingredientsText, setIngredientsText] = useState('');
  const [stepsText, setStepsText] = useState('');
  const [imageUrl, setImageUrl] = useState('');
  const [selectedTagNames, setSelectedTagNames] = useState<string[]>([]);
  const [newTagInput, setNewTagInput] = useState('');

  useEffect(() => {
    if (recipe && !hasInitialized.current) {
      hasInitialized.current = true;
      setTitle(recipe.title);
      setDescription(recipe.description ?? '');
      setServings(recipe.servings ?? '');
      setNotes(recipe.notes ?? '');
      setImageUrl(recipe.image_url ?? '');
      setSelectedTagNames(recipe.tags.map(t => t.name));

      const ingLines = recipe.ingredients.map(ing => {
        const parts = [ing.ingredient.name, ing.amount, ing.unit].filter(Boolean);
        return parts.join(' ');
      });
      setIngredientsText(ingLines.join('\n'));

      const stepLines = recipe.steps
        .sort((a, b) => a.step_number - b.step_number)
        .map(s => s.instruction);
      setStepsText(stepLines.join('\n'));
    }
  }, [recipe]);

  const allTags = allTagsData ?? [];

  const toggleTag = (name: string) => {
    setSelectedTagNames(prev =>
      prev.includes(name) ? prev.filter(t => t !== name) : [...prev, name]
    );
  };

  const handleImageChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const url = await uploadImage.mutateAsync(file);
    setImageUrl(url);
  };

  const addNewTag = () => {
    const name = newTagInput.trim();
    if (!name || selectedTagNames.includes(name)) return;
    setSelectedTagNames(prev => [...prev, name]);
    setNewTagInput('');
  };

  const handleSave = async () => {
    if (!title.trim()) return alert('레시피 이름을 입력해주세요');

    const ingredients = ingredientsText
      .split('\n').map(l => l.trim()).filter(Boolean)
      .map((name, i) => ({ name, sort_order: i }));

    const steps = stepsText
      .split('\n').map(l => l.trim()).filter(Boolean)
      .map((instruction, i) => ({ step_number: i + 1, instruction }));

    const tagResults = await Promise.all(
      selectedTagNames.map(name =>
        import('../lib/api').then(m => m.default.post('/tags', { name }).then(r => r.data.id as number))
      )
    );

    await update.mutateAsync({
      title,
      description: description || null,
      servings: servings || null,
      notes: notes || null,
      image_url: imageUrl || null,
      ingredients,
      steps,
      tag_ids: tagResults,
    });
    navigate(`/recipes/${id}`);
  };

  if (!recipe) return <p style={{ padding: 20 }}>불러오는 중...</p>;

  return (
    <div className="page--narrow">
      <div className="page-header">
        <button className="btn" onClick={() => navigate(-1)}>← 취소하고 돌아가기</button>
        <h2>레시피 수정</h2>
      </div>

      <div className="form">
        {/* 대표 이미지 */}
        <div className="form-group">
          <label className="label">대표 이미지</label>
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={handleImageChange}
            style={{ display: 'none' }}
          />
          {imageUrl ? (
            <div>
              <img
                src={imageUrl}
                alt="대표 이미지"
                style={{ width: '100%', maxHeight: 200, objectFit: 'cover', borderRadius: 6, display: 'block' }}
              />
              <div className="flex gap-sm mt-sm">
                <button className="btn btn--sm" onClick={() => fileInputRef.current?.click()} disabled={uploadImage.isPending}>
                  {uploadImage.isPending ? '업로드 중...' : '이미지 변경'}
                </button>
                <button className="btn btn--sm" onClick={() => setImageUrl('')}>이미지 삭제</button>
              </div>
            </div>
          ) : (
            <div
              onClick={() => fileInputRef.current?.click()}
              className="box box--subtle text-center text-muted"
              style={{ cursor: 'pointer', padding: '24px 0', border: '2px dashed var(--color-border)' }}
            >
              {uploadImage.isPending ? '업로드 중...' : '+ 이미지 추가'}
            </div>
          )}
        </div>

        {/* 기본 정보 */}
        <div className="form-group">
          <label className="label">레시피 이름 *</label>
          <input className="input" value={title} onChange={e => setTitle(e.target.value)} />
        </div>

        <div className="form-group">
          <label className="label">인분</label>
          <input className="input" value={servings} onChange={e => setServings(e.target.value)} />
        </div>

        <div className="form-group">
          <label className="label">설명</label>
          <textarea className="textarea" value={description} onChange={e => setDescription(e.target.value)} rows={2} />
        </div>

        {/* 태그 */}
        <div className="form-group">
          <label className="label">태그</label>
          <div className="flex flex-wrap gap-xs mb-sm">
            {allTags.map(tag => (
              <span
                key={tag.id}
                onClick={() => toggleTag(tag.name)}
                className={`chip chip--clickable ${selectedTagNames.includes(tag.name) ? 'chip--active' : ''}`}
              >
                {tag.name}
              </span>
            ))}
          </div>
          <div className="flex gap-sm">
            <input
              className="input"
              placeholder="새 태그 추가"
              value={newTagInput}
              onChange={e => setNewTagInput(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && (e.preventDefault(), addNewTag())}
            />
            <button className="btn btn--sm" onClick={addNewTag}>추가</button>
          </div>
          <div className="flex flex-wrap gap-xs mt-sm">
            {selectedTagNames.filter(n => !allTags.find(t => t.name === n)).map(name => (
              <span
                key={name}
                onClick={() => toggleTag(name)}
                className="chip chip--clickable chip--active"
              >
                {name} ✕
              </span>
            ))}
          </div>
        </div>

        {/* 재료 */}
        <div className="form-group">
          <label className="label">
            재료 목록 <span className="label--hint">(한 줄에 하나)</span>
          </label>
          <textarea
            className="textarea"
            value={ingredientsText}
            onChange={e => setIngredientsText(e.target.value)}
            rows={8}
            placeholder={'양파 1개\n간장 2큰술\n참기름 1작은술'}
          />
        </div>

        {/* 조리 순서 */}
        <div className="form-group">
          <label className="label">
            조리 순서 <span className="label--hint">(줄바꿈으로 구분)</span>
          </label>
          <textarea
            className="textarea"
            value={stepsText}
            onChange={e => setStepsText(e.target.value)}
            rows={10}
            placeholder={'냄비에 물을 끓인다.\n재료를 넣고 10분간 졸인다.\n불을 끄고 참기름을 두른다.'}
          />
        </div>

        {/* 메모 */}
        <div className="form-group">
          <label className="label">나만의 메모</label>
          <textarea className="textarea textarea--note" value={notes} onChange={e => setNotes(e.target.value)} rows={3} />
        </div>

        <div className="flex gap-md mt-sm">
          <button className="btn" style={{ flex: 1 }} onClick={() => navigate(-1)}>취소</button>
          <button
            className="btn btn--primary"
            style={{ flex: 2 }}
            onClick={handleSave}
            disabled={update.isPending}
          >
            {update.isPending ? '저장 중...' : '저장하기'}
          </button>
        </div>
      </div>
    </div>
  );
}
