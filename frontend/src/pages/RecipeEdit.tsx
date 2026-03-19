import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useRecipe, useUpdateRecipe } from '../hooks/useRecipes';

export default function RecipeEdit() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data: recipe } = useRecipe(Number(id));
  const update = useUpdateRecipe(Number(id));

  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [servings, setServings] = useState('');
  const [notes, setNotes] = useState('');

  useEffect(() => {
    if (recipe) {
      setTitle(recipe.title);
      setDescription(recipe.description ?? '');
      setServings(recipe.servings ?? '');
      setNotes(recipe.notes ?? '');
    }
  }, [recipe]);

  const handleSave = async () => {
    if (!title.trim()) return alert('레시피 이름을 입력해주세요');
    await update.mutateAsync({
      title,
      description: description || null,
      servings: servings || null,
      notes: notes || null,
    });
    navigate(`/recipes/${id}`);
  };

  return (
    <div style={{ maxWidth: 600, margin: '0 auto', padding: 20 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 24 }}>
        <button onClick={() => navigate(-1)}>← 뒤로</button>
        <h2 style={{ margin: 0 }}>레시피 편집</h2>
      </div>

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
          <textarea value={notes} onChange={e => setNotes(e.target.value)} rows={3} style={{ width: '100%', padding: '8px 12px', boxSizing: 'border-box' }} />
        </div>
        <button onClick={handleSave} disabled={update.isPending} style={{ padding: '12px', fontSize: 16, marginTop: 8 }}>
          {update.isPending ? '저장 중...' : '저장'}
        </button>
      </div>
    </div>
  );
}
