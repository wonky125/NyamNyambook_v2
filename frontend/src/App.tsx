import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useAuth } from './hooks/useAuth';
import Landing from './pages/Landing';
import Dashboard from './pages/Dashboard';
import RecipeAdd from './pages/RecipeAdd';
import RecipeDetail from './pages/RecipeDetail';
import RecipeEdit from './pages/RecipeEdit';
import Shopping from './pages/Shopping';

const queryClient = new QueryClient();

function AppRoutes() {
  const { session, loading } = useAuth();

  if (loading) return <div style={{ padding: 40, textAlign: 'center' }}>로딩 중...</div>;

  return (
    <Routes>
      <Route path="/" element={session ? <Navigate to="/dashboard" /> : <Landing />} />
      <Route path="/dashboard" element={session ? <Dashboard /> : <Navigate to="/" />} />
      <Route path="/add" element={session ? <RecipeAdd /> : <Navigate to="/" />} />
      <Route path="/recipes/:id" element={session ? <RecipeDetail /> : <Navigate to="/" />} />
      <Route path="/recipes/:id/edit" element={session ? <RecipeEdit /> : <Navigate to="/" />} />
      <Route path="/shopping" element={session ? <Shopping /> : <Navigate to="/" />} />
    </Routes>
  );
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AppRoutes />
      </BrowserRouter>
    </QueryClientProvider>
  );
}
