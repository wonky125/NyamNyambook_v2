import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useRecipe, useUpdateRecipe, useUploadImage } from '../hooks/useRecipes';
import api from '../lib/api';

export default function RecipeEdit() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data: recipe } = useRecipe(Number(id));
  const update = useUpdateRecipe(Number(id));
  const uploadImage = useUploadImage();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [servings, setServings] = useState('');
  const [notes, setNotes] = useState('');
  const [ingredientsText, setIngredientsText] = useState('');
  const [stepsText, setStepsText] = useState('');
  const [imageUrl, setImageUrl] = useState('');
  const [selectedTagNames, setSelectedTagNames] = useState<string[]>([]);
  const [allTags, setAllTags] = useState<{ id: number; name: string }[]>([]);
  const [newTagInput, setNewTagInput] = useState('');

  useEffect(() => {
    if (recipe) {
      setTitle(recipe.title);
      setDescription(recipe.description ?? '');
      setServings(recipe.servings ?? '');
      setNotes(recipe.notes ?? '');
      setImageUrl(recipe.image_url ?? '');

      // 재료: "이름 수량 단위" 한 줄씩
      const ingLines = recipe.ingredients.map(ing => {
        const parts = [ing.ingredient.name, ing.amount, ing.unit].filter(Boolean);
        return parts.join(' ');
      });
      setIngredientsText(ingLines.join('\n'));

      // 조리 단계: 한 줄씩
      const stepLines = recipe.steps
        .sort((a, b) => a.step_number - b.step_number)
        .map(s => s.instruction);
      setStepsText(stepLines.join('\n'));

      // 현재 태그
      setSelectedTagNames(recipe.tags.map(t => t.name));
    }
  }, [recipe]);

  useEffect(() => {
    api.get('/tags').then(r => setAllTags(r.data));
  }, []);

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

    // 재료: 비어있지 않은 줄만
    const ingredients = ingredientsText
      .split('\n')
      .map(l => l.trim())
      .filter(Boolean)
      .map((name, i) => ({ name, sort_order: i }));

    // 조리 단계: 비어있지 않은 줄만
    const steps = stepsText
      .split('\n')
      .map(l => l.trim())
      .filter(Boolean)
      .map((instruction, i) => ({ step_number: i + 1, instruction }));

    // 태그: 이름 → ID (get_or_create)
    const tagResults = await Promise.all(
      selectedTagNames.map(name => api.post('/tags', { name }).then(r => r.data.id as number))
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
    <div style={{ maxWidth: 600, margin: '0 auto', padding: 20 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 24 }}>
        <button onClick={() => navigate(-1)}>← 취소하고 돌아가기</button>
        <h2 style={{ margin: 0 }}>레시피 수정</h2>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
        {/* 대표 이미지 */}
        <div>
          <label style={{ display: 'block', marginBottom: 6, fontSize: 14, fontWeight: 'bold' }}>대표 이미지</label>
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={handleImageChange}
            style={{ display: 'none' }}
          />
          {imageUrl ? (
            <div style={{ position: 'relative', display: 'inline-block' }}>
              <img
                src={imageUrl}
                alt="대표 이미지"
                style={{ width: '100%', maxHeight: 200, objectFit: 'cover', borderRadius: 6, display: 'block' }}
              />
              <div style={{ display: 'flex', gap: 8, marginTop: 6 }}>
                <button onClick={() => fileInputRef.current?.click()} disabled={uploadImage.isPending} style={{ fontSize: 13 }}>
                  {uploadImage.isPending ? '업로드 중...' : '이미지 변경'}
                </button>
                <button onClick={() => setImageUrl('')} style={{ fontSize: 13 }}>이미지 삭제</button>
              </div>
            </div>
          ) : (
            <div
              onClick={() => fileInputRef.current?.click()}
              style={{
                border: '2px dashed #ccc', borderRadius: 6, padding: '24px 0',
                textAlign: 'center', cursor: 'pointer', color: '#888', fontSize: 14,
              }}
            >
              {uploadImage.isPending ? '업로드 중...' : '+ 이미지 추가'}
            </div>
          )}
        </div>

        {/* 기본 정보 */}
        <div>
          <label style={{ display: 'block', marginBottom: 4, fontSize: 14, fontWeight: 'bold' }}>레시피 이름 *</label>
          <input value={title} onChange={e => setTitle(e.target.value)} style={{ width: '100%', padding: '8px 12px', boxSizing: 'border-box' }} />
        </div>

        <div style={{ display: 'flex', gap: 12 }}>
          <div style={{ flex: 1 }}>
            <label style={{ display: 'block', marginBottom: 4, fontSize: 14 }}>인분</label>
            <input value={servings} onChange={e => setServings(e.target.value)} style={{ width: '100%', padding: '8px 12px', boxSizing: 'border-box' }} />
          </div>
        </div>

        <div>
          <label style={{ display: 'block', marginBottom: 4, fontSize: 14 }}>설명</label>
          <textarea value={description} onChange={e => setDescription(e.target.value)} rows={2} style={{ width: '100%', padding: '8px 12px', boxSizing: 'border-box' }} />
        </div>

        {/* 태그 */}
        <div>
          <label style={{ display: 'block', marginBottom: 6, fontSize: 14, fontWeight: 'bold' }}>태그</label>
          {/* 기존 태그 칩 */}
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginBottom: 8 }}>
            {allTags.map(tag => (
              <span
                key={tag.id}
                onClick={() => toggleTag(tag.name)}
                style={{
                  padding: '4px 12px', borderRadius: 16, fontSize: 13, cursor: 'pointer',
                  background: selectedTagNames.includes(tag.name) ? '#f5a623' : '#f0f0f0',
                  color: selectedTagNames.includes(tag.name) ? '#fff' : '#333',
                  userSelect: 'none',
                }}
              >
                {tag.name}
              </span>
            ))}
          </div>
          {/* 새 태그 추가 */}
          <div style={{ display: 'flex', gap: 8 }}>
            <input
              placeholder="새 태그 추가"
              value={newTagInput}
              onChange={e => setNewTagInput(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && (e.preventDefault(), addNewTag())}
              style={{ flex: 1, padding: '6px 10px', fontSize: 13 }}
            />
            <button onClick={addNewTag} style={{ fontSize: 13 }}>추가</button>
          </div>
          {/* 선택된 태그 중 기존 목록에 없는 것 표시 */}
          {selectedTagNames.filter(n => !allTags.find(t => t.name === n)).map(name => (
            <span
              key={name}
              onClick={() => toggleTag(name)}
              style={{
                display: 'inline-block', marginTop: 6, marginRight: 6,
                padding: '4px 12px', borderRadius: 16, fontSize: 13, cursor: 'pointer',
                background: '#f5a623', color: '#fff', userSelect: 'none',
              }}
            >
              {name} ✕
            </span>
          ))}
        </div>

        {/* 재료 */}
        <div>
          <label style={{ display: 'block', marginBottom: 4, fontSize: 14, fontWeight: 'bold' }}>
            재료 목록 <span style={{ fontWeight: 'normal', color: '#888' }}>(한 줄에 하나)</span>
          </label>
          <textarea
            value={ingredientsText}
            onChange={e => setIngredientsText(e.target.value)}
            rows={8}
            placeholder={'양파 1개\n간장 2큰술\n참기름 1작은술'}
            style={{ width: '100%', padding: '8px 12px', boxSizing: 'border-box', fontFamily: 'inherit', lineHeight: 1.7 }}
          />
        </div>

        {/* 조리 순서 */}
        <div>
          <label style={{ display: 'block', marginBottom: 4, fontSize: 14, fontWeight: 'bold' }}>
            조리 순서 <span style={{ fontWeight: 'normal', color: '#888' }}>(줄바꿈으로 구분)</span>
          </label>
          <textarea
            value={stepsText}
            onChange={e => setStepsText(e.target.value)}
            rows={10}
            placeholder={'냄비에 물을 끓인다.\n재료를 넣고 10분간 졸인다.\n불을 끄고 참기름을 두른다.'}
            style={{ width: '100%', padding: '8px 12px', boxSizing: 'border-box', fontFamily: 'inherit', lineHeight: 1.7 }}
          />
        </div>

        {/* 메모 */}
        <div>
          <label style={{ display: 'block', marginBottom: 4, fontSize: 14, fontWeight: 'bold' }}>나만의 메모</label>
          <textarea
            value={notes}
            onChange={e => setNotes(e.target.value)}
            rows={3}
            style={{ width: '100%', padding: '8px 12px', boxSizing: 'border-box', background: '#fffde7' }}
          />
        </div>

        <div style={{ display: 'flex', gap: 12, marginTop: 8 }}>
          <button onClick={() => navigate(-1)} style={{ flex: 1, padding: '12px', fontSize: 15 }}>취소</button>
          <button
            onClick={handleSave}
            disabled={update.isPending}
            style={{ flex: 2, padding: '12px', fontSize: 15, background: '#f5a623', color: '#fff', border: 'none', borderRadius: 6, cursor: 'pointer' }}
          >
            {update.isPending ? '저장 중...' : '저장하기'}
          </button>
        </div>
      </div>
    </div>
  );
}
