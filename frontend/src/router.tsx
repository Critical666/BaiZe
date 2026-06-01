import { createBrowserRouter, Navigate } from 'react-router-dom';
import AppLayout from '@/components/Layout';
import LoginPage from '@/pages/LoginPage';
import HomePage from '@/pages/HomePage';
import KnowledgeBasePage from '@/pages/KnowledgeBasePage';
import ChatPage from '@/pages/ChatPage';
import StatsPage from '@/pages/StatsPage';

const router = createBrowserRouter([
  {
    path: '/login',
    element: <LoginPage />,
  },
  {
    path: '/',
    element: <AppLayout />,
    children: [
      { index: true, element: <HomePage /> },
      { path: 'kb/:id', element: <KnowledgeBasePage /> },
      { path: 'kb/:id/chat', element: <ChatPage /> },
      { path: 'stats', element: <StatsPage /> },
    ],
  },
  {
    path: '*',
    element: <Navigate to="/" replace />,
  },
]);

export default router;
