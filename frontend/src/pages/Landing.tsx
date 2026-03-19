import { useAuth } from '../hooks/useAuth';

export default function Landing() {
  const { signInWithGoogle } = useAuth();

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100vh', gap: 16 }}>
      <h1>🍚 냠냠북</h1>
      <p style={{ color: '#666' }}>URL 하나로 레시피를 저장하세요</p>
      <button onClick={() => signInWithGoogle()} style={{ padding: '12px 24px', fontSize: 16, cursor: 'pointer' }}>
        Google로 시작하기
      </button>
    </div>
  );
}
