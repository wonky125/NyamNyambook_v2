import { useParams, useNavigate } from 'react-router-dom';
import { useRecipe, useMarkCooked, useDeleteRecipe } from '../hooks/useRecipes';

export default function RecipeDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data: recipe, isLoading } = useRecipe(Number(id));
  const markCooked = useMarkCooked();
  const deleteRecipe = useDeleteRecipe();

  if (isLoading) return <p style={{ padding: 20 }}>불러오는 중...</p>;
  if (!recipe) return <p style={{ padding: 20 }}>레시피를 찾을 수 없습니다.</p>;

  const handleDelete = async () => {
    if (!confirm('삭제할까요?')) return;
    await deleteRecipe.mutateAsync(recipe.id);
    navigate('/');
  };

  return (
    <div style={{ maxWidth: 700, margin: '0 auto', padding: 20 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 20 }}>
        <button onClick={() => navigate('/')}>← 뒤로</button>
        <button onClick={() => navigate(`/recipes/${recipe.id}/edit`)}>편집</button>
        <button onClick={handleDelete}>삭제</button>
      </div>

      {recipe.image_url && (
        <img src={recipe.image_url} alt={recipe.title} style={{ width: '100%', maxHeight: 300, objectFit: 'cover', borderRadius: 8, marginBottom: 16 }} />
      )}

      <h1 style={{ margin: '0 0 8px' }}>{recipe.title}</h1>

      {/* 태그 */}
      {recipe.tags.length > 0 && (
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginBottom: 12 }}>
          {recipe.tags.map(t => (
            <span key={t.id} style={{ background: '#f0f0f0', padding: '3px 10px', borderRadius: 12, fontSize: 13 }}>{t.name}</span>
          ))}
        </div>
      )}

      {/* 메타 */}
      <div style={{ display: 'flex', gap: 16, fontSize: 14, color: '#666', marginBottom: 16 }}>
        {recipe.servings && <span>👥 {recipe.servings}</span>}
        {recipe.total_time && <span>⏱ {recipe.total_time}분</span>}
        <span>🍳 {recipe.cooked_count}회 요리함</span>
      </div>

      {/* 요리했어요 */}
      <button
        onClick={() => markCooked.mutate(recipe.id)}
        style={{ padding: '10px 20px', marginBottom: 20, background: '#fff3e0', border: '1px solid #ffb74d', borderRadius: 20, cursor: 'pointer' }}
      >
        🍳 요리했어요!
      </button>

      {recipe.description && <p style={{ color: '#444', lineHeight: 1.6, marginBottom: 16 }}>{recipe.description}</p>}

      {recipe.source_url && (
        <a href={recipe.source_url} target="_blank" rel="noreferrer" style={{ fontSize: 13, color: '#1976d2' }}>
          📎 원본 레시피 보기
        </a>
      )}

      {/* 재료 */}
      {recipe.ingredients.length > 0 && (
        <div style={{ marginTop: 24 }}>
          <h3>재료</h3>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <tbody>
              {recipe.ingredients.map(ing => (
                <tr key={ing.id} style={{ borderBottom: '1px solid #f0f0f0' }}>
                  <td style={{ padding: '6px 0' }}>{ing.ingredient.name}</td>
                  <td style={{ padding: '6px 0', color: '#666', textAlign: 'right' }}>
                    {ing.amount} {ing.unit}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* 조리 단계 */}
      {recipe.steps.length > 0 && (
        <div style={{ marginTop: 24 }}>
          <h3>조리 순서</h3>
          {recipe.steps.map(step => (
            <div key={step.id} style={{ display: 'flex', gap: 12, marginBottom: 16 }}>
              <div style={{ width: 28, height: 28, borderRadius: '50%', background: '#ff7043', color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0, fontSize: 14 }}>
                {step.step_number}
              </div>
              <p style={{ margin: 0, lineHeight: 1.6 }}>{step.instruction}</p>
            </div>
          ))}
        </div>
      )}

      {recipe.notes && (
        <div style={{ marginTop: 24, background: '#fffde7', padding: 12, borderRadius: 6 }}>
          <h3 style={{ margin: '0 0 8px' }}>메모</h3>
          <p style={{ margin: 0 }}>{recipe.notes}</p>
        </div>
      )}
    </div>
  );
}
