import { createBrowserRouter, Navigate, Outlet } from 'react-router-dom';
import AppLayout from '@/components/Layout';
import LandingPage from '@/pages/LandingPage';
import LoginPage from '@/pages/LoginPage';
import HomePage from '@/pages/HomePage';
import KnowledgeBasePage from '@/pages/KnowledgeBasePage';
import ChatPage from '@/pages/ChatPage';
import StatsPage from '@/pages/StatsPage';

function RequireAuth() {
  const token = localStorage.getItem('token');
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  return <Outlet />;
}

const router = createBrowserRouter([
  {
    path: '/',
    element: <LandingPage />,
  },
  {
    path: '/login',
    element: <LoginPage />,
  },
  {
    path: '/',
    element: <RequireAuth />,
    children: [
      {
        element: <AppLayout />,
        children: [
          { path: 'home', element: <HomePage /> },
          { path: 'kb/:id', element: <KnowledgeBasePage /> },
          { path: 'kb/:id/chat', element: <ChatPage /> },
          { path: 'stats', element: <StatsPage /> },
        ],
      },
    ],
  },
  {
    path: '*',
    element: <Navigate to="/" replace />,
  },
]);

export default router;
