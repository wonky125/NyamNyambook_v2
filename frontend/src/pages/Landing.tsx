import { useAuth } from '../hooks/useAuth';

export default function Landing() {
  const { signInWithGoogle } = useAuth();

  return (
    <div className="flex-center flex-col gap-lg" style={{ height: '100vh' }}>
      <h1 style={{ fontSize: 40, margin: 0 }}>🍚 냠냠북</h1>
      <p className="text-muted">URL 하나로 레시피를 저장하세요</p>
      <button className="btn btn--primary btn--lg btn--pill" onClick={() => signInWithGoogle()}>
        Google로 시작하기
      </button>
    </div>
  );
}
