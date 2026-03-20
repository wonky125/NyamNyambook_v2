import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useRecipe, useMarkCooked, useDeleteRecipe } from '../hooks/useRecipes';

// ─── 인분 계산 ───────────────────────────────────────────────
function evalFraction(str: string): number {
  const mixed = str.trim().match(/^(\d+)\s+(\d+)\/(\d+)$/);
  if (mixed) return parseFloat(mixed[1]) + parseFloat(mixed[2]) / parseFloat(mixed[3]);
  const frac = str.trim().match(/^(\d+)\/(\d+)$/);
  if (frac) return parseFloat(frac[1]) / parseFloat(frac[2]);
  return parseFloat(str);
}

function scaleAmount(amount: string | null, ratio: number): string {
  if (!amount || ratio === 1) return amount ?? '';
  return amount.replace(/(\d+\s+\d+\/\d+|\d+\/\d+|\d+(?:\.\d+)?)/g, (match) => {
    const scaled = evalFraction(match) * ratio;
    // 소수점 2자리, 불필요한 0 제거
    return parseFloat(scaled.toFixed(2)).toString();
  });
}

function parseBaseServings(servings: string | null | undefined): number {
  if (!servings) return 1;
  const n = parseInt(servings.replace(/[^0-9]/g, ''), 10);
  return n > 0 ? n : 1;
}

// ─── 조리모드 ────────────────────────────────────────────────
interface CookModeProps {
  steps: { step_number: number; instruction: string }[];
  ingredients: { name: string; amount: string | null; unit: string | null }[];
  onClose: () => void;
}

function CookMode({ steps, ingredients, onClose }: CookModeProps) {
  const [stepIndex, setStepIndex] = useState(-1); // -1 = 재료 준비
  const [checked, setChecked] = useState<boolean[]>(ingredients.map(() => false));
  const wakeLockRef = useRef<WakeLockSentinel | null>(null);

  useEffect(() => {
    document.body.style.overflow = 'hidden';
    (async () => {
      try {
        if ('wakeLock' in navigator) {
          wakeLockRef.current = await navigator.wakeLock.request('screen');
        }
      } catch { /* wake lock 미지원 무시 */ }
    })();
    return () => {
      document.body.style.overflow = '';
      wakeLockRef.current?.release().catch(() => {});
    };
  }, []);

  const total = steps.length;
  const isIngredientScreen = stepIndex === -1;
  const progress = isIngredientScreen ? 0 : ((stepIndex + 1) / total) * 100;

  const toggleCheck = (i: number) =>
    setChecked(prev => prev.map((v, idx) => idx === i ? !v : v));

  return (
    <div style={{
      position: 'fixed', inset: 0, background: '#fff', zIndex: 1000,
      display: 'flex', flexDirection: 'column',
    }}>
      {/* 헤더 */}
      <div style={{
        background: '#1a1a2e', color: '#fff',
        padding: '16px 20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center',
      }}>
        {isIngredientScreen ? (
          <span style={{ fontSize: 22, fontWeight: 700, color: '#4caf50' }}>🥗 재료 준비</span>
        ) : (
          <span style={{ fontSize: 20, fontWeight: 700, color: '#ff7043' }}>
            STEP {stepIndex + 1} <span style={{ fontSize: 14, color: '#aaa' }}>/ {total}</span>
          </span>
        )}
        <button
          onClick={onClose}
          style={{ background: 'none', border: '1px solid #555', color: '#fff', padding: '6px 14px', borderRadius: 6, cursor: 'pointer' }}
        >
          닫기 ✕
        </button>
      </div>

      {/* 진행바 */}
      <div style={{ height: 4, background: '#eee' }}>
        <div style={{ height: '100%', background: '#ff7043', width: `${progress}%`, transition: 'width 0.3s' }} />
      </div>

      {/* 본문 */}
      <div style={{ flex: 1, overflowY: 'auto', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 24 }}>
        {isIngredientScreen ? (
          <div style={{ width: '100%', maxWidth: 500 }}>
            {ingredients.map((ing, i) => (
              <div
                key={i}
                onClick={() => toggleCheck(i)}
                style={{
                  display: 'flex', alignItems: 'center', gap: 14, padding: '14px 0',
                  borderBottom: '1px solid #f0f0f0', cursor: 'pointer',
                  opacity: checked[i] ? 0.4 : 1,
                }}
              >
                <div style={{
                  width: 28, height: 28, borderRadius: '50%', flexShrink: 0,
                  border: `2px solid ${checked[i] ? '#4caf50' : '#ccc'}`,
                  background: checked[i] ? '#4caf50' : 'transparent',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  color: '#fff', fontSize: 16,
                }}>
                  {checked[i] ? '✓' : ''}
                </div>
                <span style={{
                  fontSize: 17, flex: 1,
                  textDecoration: checked[i] ? 'line-through' : 'none',
                }}>
                  {ing.name}
                  {ing.amount && <span style={{ color: '#888', marginLeft: 8 }}>{ing.amount}{ing.unit ? ` ${ing.unit}` : ''}</span>}
                </span>
              </div>
            ))}
          </div>
        ) : (
          <p style={{
            fontSize: 'clamp(20px, 4vw, 28px)', lineHeight: 1.7,
            textAlign: 'center', maxWidth: 600, margin: 0,
          }}>
            {steps[stepIndex]?.instruction}
          </p>
        )}
      </div>

      {/* 하단 버튼 */}
      <div style={{
        borderTop: '1px solid #eee', padding: '16px 20px',
        display: 'flex', justifyContent: 'space-between', gap: 12,
      }}>
        <button
          onClick={() => setStepIndex(i => i - 1)}
          disabled={isIngredientScreen}
          style={{
            flex: 1, padding: '14px 0', fontSize: 16, borderRadius: 8,
            border: '1px solid #ddd', cursor: isIngredientScreen ? 'default' : 'pointer',
            opacity: isIngredientScreen ? 0.3 : 1, background: '#f5f5f5',
          }}
        >
          ← 이전
        </button>
        <button
          onClick={() => {
            if (stepIndex < total - 1) setStepIndex(i => i + 1);
            else onClose();
          }}
          style={{
            flex: 2, padding: '14px 0', fontSize: 16, borderRadius: 8,
            background: stepIndex === total - 1 ? '#4caf50' : '#ff7043',
            color: '#fff', border: 'none', cursor: 'pointer', fontWeight: 600,
          }}
        >
          {isIngredientScreen ? '조리 시작 →' : stepIndex === total - 1 ? '완료! 🎉' : '다음 →'}
        </button>
      </div>
    </div>
  );
}

// ─── 메인 ────────────────────────────────────────────────────
export default function RecipeDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data: recipe, isLoading } = useRecipe(Number(id));
  const markCooked = useMarkCooked();
  const deleteRecipe = useDeleteRecipe();

  const baseServings = parseBaseServings(recipe?.servings);
  const [servings, setServings] = useState<number | null>(null);
  const [cookMode, setCookMode] = useState(false);

  // recipe 로드 후 초기 인분 세팅
  useEffect(() => {
    if (recipe) setServings(parseBaseServings(recipe.servings));
  }, [recipe?.id]);

  if (isLoading) return <p style={{ padding: 20 }}>불러오는 중...</p>;
  if (!recipe) return <p style={{ padding: 20 }}>레시피를 찾을 수 없습니다.</p>;

  const currentServings = servings ?? baseServings;
  const ratio = baseServings > 0 ? currentServings / baseServings : 1;

  const scaledIngredients = recipe.ingredients.map(ing => ({
    name: ing.ingredient.name,
    amount: scaleAmount(ing.amount, ratio),
    unit: ing.unit,
    note: ing.note,
  }));

  const handleDelete = async () => {
    if (!confirm('삭제할까요?')) return;
    await deleteRecipe.mutateAsync(recipe.id);
    navigate('/');
  };

  return (
    <>
      {cookMode && (
        <CookMode
          steps={recipe.steps}
          ingredients={scaledIngredients}
          onClose={() => setCookMode(false)}
        />
      )}

      <div style={{ maxWidth: 700, margin: '0 auto', padding: 20 }}>
        {/* 상단 버튼 */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 20, flexWrap: 'wrap' }}>
          <button onClick={() => navigate('/dashboard')}>← 뒤로</button>
          <button onClick={() => navigate(`/recipes/${recipe.id}/edit`)}>편집</button>
          <button onClick={handleDelete}>삭제</button>
          <button
            onClick={() => markCooked.mutate(recipe.id)}
            style={{ background: '#fff3e0', border: '1px solid #ffb74d', borderRadius: 20, padding: '6px 16px', cursor: 'pointer' }}
          >
            🍳 요리했어요!
          </button>
          {recipe.steps.length > 0 && (
            <button
              onClick={() => setCookMode(true)}
              style={{ background: '#ff7043', color: '#fff', border: 'none', borderRadius: 20, padding: '6px 16px', cursor: 'pointer', fontWeight: 600 }}
            >
              👨‍🍳 조리 시작
            </button>
          )}
        </div>

        {recipe.image_url && (
          <img src={recipe.image_url} alt={recipe.title} style={{ width: '100%', maxHeight: 300, objectFit: 'cover', borderRadius: 8, marginBottom: 16 }} />
        )}

        <h1 style={{ margin: '0 0 8px' }}>{recipe.title}</h1>

        {recipe.tags.length > 0 && (
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginBottom: 12 }}>
            {recipe.tags.map(t => (
              <span key={t.id} style={{ background: '#f0f0f0', padding: '3px 10px', borderRadius: 12, fontSize: 13 }}>{t.name}</span>
            ))}
          </div>
        )}

        <div style={{ display: 'flex', gap: 16, fontSize: 14, color: '#666', marginBottom: 20 }}>
          {recipe.total_time && <span>⏱ {recipe.total_time}분</span>}
          <span>🍳 {recipe.cooked_count}회 요리함</span>
        </div>

        {recipe.description && <p style={{ color: '#444', lineHeight: 1.6, marginBottom: 16 }}>{recipe.description}</p>}

        {recipe.source_url && (
          <a href={recipe.source_url} target="_blank" rel="noreferrer" style={{ fontSize: 13, color: '#1976d2', display: 'block', marginBottom: 20 }}>
            📎 원본 레시피 보기
          </a>
        )}

        {/* 인분 계산기 */}
        {recipe.ingredients.length > 0 && (
          <div style={{ marginTop: 24 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 12 }}>
              <h3 style={{ margin: 0 }}>재료</h3>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginLeft: 'auto' }}>
                <button
                  onClick={() => setServings(s => Math.max(1, (s ?? baseServings) - 1))}
                  style={{ width: 28, height: 28, borderRadius: '50%', border: '1px solid #ddd', cursor: 'pointer', fontSize: 16, background: '#fff' }}
                >−</button>
                <span style={{ fontSize: 15, minWidth: 48, textAlign: 'center' }}>
                  {currentServings}인분
                </span>
                <button
                  onClick={() => setServings(s => (s ?? baseServings) + 1)}
                  style={{ width: 28, height: 28, borderRadius: '50%', border: '1px solid #ddd', cursor: 'pointer', fontSize: 16, background: '#fff' }}
                >+</button>
              </div>
            </div>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <tbody>
                {scaledIngredients.map((ing, i) => (
                  <tr key={i} style={{ borderBottom: '1px solid #f0f0f0' }}>
                    <td style={{ padding: '7px 0' }}>{ing.name}</td>
                    <td style={{ padding: '7px 0', color: '#666', textAlign: 'right' }}>
                      {ing.amount} {ing.unit}
                      {ing.note && <span style={{ color: '#aaa', fontSize: 12, marginLeft: 6 }}>({ing.note})</span>}
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
                <div style={{
                  width: 28, height: 28, borderRadius: '50%', background: '#ff7043', color: 'white',
                  display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0, fontSize: 14,
                }}>
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
    </>
  );
}
