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
  const [stepIndex, setStepIndex] = useState(-1);
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
  const isIngredients = stepIndex === -1;
  const progress = isIngredients ? 0 : ((stepIndex + 1) / total) * 100;
  const isLast = stepIndex === total - 1;

  const toggleCheck = (i: number) =>
    setChecked(prev => prev.map((v, idx) => idx === i ? !v : v));

  return (
    <div style={{
      position: 'fixed', inset: 0, background: '#fff', zIndex: 1000,
      display: 'flex', flexDirection: 'column',
    }}>
      {/* 헤더 */}
      <div style={{
        background: '#1a1a2e', color: '#fff', padding: '16px 20px',
        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
      }}>
        {isIngredients
          ? <span style={{ fontSize: 22, fontWeight: 700, color: '#4caf50' }}>🥗 재료 준비</span>
          : <span style={{ fontSize: 20, fontWeight: 700, color: 'var(--color-accent)' }}>
              STEP {stepIndex + 1} <span style={{ fontSize: 14, color: '#aaa' }}>/ {total}</span>
            </span>
        }
        <button
          onClick={onClose}
          className="btn btn--sm"
          style={{ background: 'none', border: '1px solid #555', color: '#fff' }}
        >
          닫기 ✕
        </button>
      </div>

      {/* 진행바 */}
      <div style={{ height: 4, background: '#eee' }}>
        <div style={{ height: '100%', background: 'var(--color-accent)', width: `${progress}%`, transition: 'width 0.3s' }} />
      </div>

      {/* 본문 */}
      <div className="flex-center" style={{ flex: 1, overflowY: 'auto', padding: 24 }}>
        {isIngredients ? (
          <div style={{ width: '100%', maxWidth: 500 }}>
            {ingredients.map((ing, i) => (
              <div
                key={i}
                onClick={() => toggleCheck(i)}
                className="flex items-center gap-md"
                style={{
                  padding: '14px 0',
                  borderBottom: '1px solid var(--color-border-light)',
                  cursor: 'pointer',
                  opacity: checked[i] ? 0.4 : 1,
                }}
              >
                <div style={{
                  width: 28, height: 28, borderRadius: '50%', flexShrink: 0,
                  border: `2px solid ${checked[i] ? '#4caf50' : 'var(--color-border)'}`,
                  background: checked[i] ? '#4caf50' : 'transparent',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  color: '#fff', fontSize: 16,
                }}>
                  {checked[i] ? '✓' : ''}
                </div>
                <span style={{ fontSize: 17, flex: 1, textDecoration: checked[i] ? 'line-through' : 'none' }}>
                  {ing.name}
                  {ing.amount && (
                    <span className="text-muted" style={{ marginLeft: 8 }}>
                      {ing.amount}{ing.unit ? ` ${ing.unit}` : ''}
                    </span>
                  )}
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
      <div className="flex gap-md" style={{ borderTop: '1px solid var(--color-border-light)', padding: '16px 20px' }}>
        <button
          className="btn"
          style={{ flex: 1 }}
          onClick={() => setStepIndex(i => i - 1)}
          disabled={isIngredients}
        >
          ← 이전
        </button>
        <button
          className={`btn ${isLast ? 'btn--success' : 'btn--accent'}`}
          style={{ flex: 2, fontSize: 16 }}
          onClick={() => {
            if (!isLast) setStepIndex(i => i + 1);
            else onClose();
          }}
        >
          {isIngredients ? '조리 시작 →' : isLast ? '완료! 🎉' : '다음 →'}
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

      <div className="page">
        {/* 버튼 바 */}
        <div className="flex flex-wrap gap-sm mb-xl">
          <button className="btn" onClick={() => navigate('/dashboard')}>← 뒤로</button>
          <button className="btn" onClick={() => navigate(`/recipes/${recipe.id}/edit`)}>편집</button>
          <button className="btn" onClick={handleDelete}>삭제</button>
          <button
            className="btn btn--pill btn--warn"
            style={{ background: 'var(--color-bg-warn)', border: '1px solid #ffb74d' }}
            onClick={() => markCooked.mutate(recipe.id)}
          >
            🍳 요리했어요!
          </button>
          {recipe.steps.length > 0 && (
            <button className="btn btn--accent btn--pill" onClick={() => setCookMode(true)}>
              👨‍🍳 조리 시작
            </button>
          )}
        </div>

        {recipe.image_url && (
          <img
            src={recipe.image_url}
            alt={recipe.title}
            style={{ width: '100%', maxHeight: 300, objectFit: 'cover', borderRadius: 8, marginBottom: 16, display: 'block' }}
          />
        )}

        <h1 style={{ fontSize: 24, marginBottom: 8 }}>{recipe.title}</h1>

        {recipe.tags.length > 0 && (
          <div className="flex flex-wrap gap-xs mb-md">
            {recipe.tags.map(t => <span key={t.id} className="chip">{t.name}</span>)}
          </div>
        )}

        <div className="flex gap-lg text-sm text-muted mb-xl">
          {recipe.total_time && <span>⏱ {recipe.total_time}분</span>}
          <span>🍳 {recipe.cooked_count}회 요리함</span>
        </div>

        {recipe.description && <p style={{ color: '#444', lineHeight: 1.6, marginBottom: 16 }}>{recipe.description}</p>}

        {recipe.source_url && (
          <a href={recipe.source_url} target="_blank" rel="noreferrer" className="text-sm mb-xl" style={{ display: 'block' }}>
            📎 원본 레시피 보기
          </a>
        )}

        {/* 재료 + 인분 계산기 */}
        {recipe.ingredients.length > 0 && (
          <div className="mt-xl">
            <div className="flex items-center mb-md">
              <h3 style={{ fontSize: 18, margin: 0 }}>재료</h3>
              <div className="serving-ctrl" style={{ marginLeft: 'auto' }}>
                <button
                  className="serving-btn"
                  onClick={() => setServings(s => Math.max(1, (s ?? baseServings) - 1))}
                >−</button>
                <span className="serving-label">{currentServings}인분</span>
                <button
                  className="serving-btn"
                  onClick={() => setServings(s => (s ?? baseServings) + 1)}
                >+</button>
              </div>
            </div>
            <table className="ing-table">
              <tbody>
                {scaledIngredients.map((ing, i) => (
                  <tr key={i}>
                    <td>{ing.name}</td>
                    <td>
                      {ing.amount} {ing.unit}
                      {ing.note && <span className="text-xs text-muted" style={{ marginLeft: 6 }}>({ing.note})</span>}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* 조리 단계 */}
        {recipe.steps.length > 0 && (
          <div className="mt-xl">
            <h3 style={{ fontSize: 18, marginBottom: 16 }}>조리 순서</h3>
            {recipe.steps.map(step => (
              <div key={step.id} className="step-item">
                <div className="step-num">{step.step_number}</div>
                <p className="step-text">{step.instruction}</p>
              </div>
            ))}
          </div>
        )}

        {recipe.notes && (
          <div className="box box--note mt-xl">
            <h3 className="box__title">메모</h3>
            <p>{recipe.notes}</p>
          </div>
        )}
      </div>
    </>
  );
}
