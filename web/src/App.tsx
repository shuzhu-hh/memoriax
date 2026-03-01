import type { ReactElement } from "react";
import { NavLink, Navigate, Route, Routes, useNavigate } from "react-router-dom";
import { useAuth } from "./auth";
import { DeckImportPage } from "./pages/DeckImportPage";
import { DeckReviewPage } from "./pages/DeckReviewPage";
import { DeckStatsPage } from "./pages/DeckStatsPage";
import { DeckWordsPage } from "./pages/DeckWordsPage";
import { DecksPage } from "./pages/DecksPage";
import { LoginPage } from "./pages/LoginPage";
import { RegisterPage } from "./pages/RegisterPage";

function ProtectedRoute({ children }: { children: ReactElement }) {
  const { isAuthenticated } = useAuth();
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  return children;
}

function NavBar() {
  const navigate = useNavigate();
  const { isAuthenticated, userEmail, logout } = useAuth();

  function handleLogout() {
    logout();
    navigate("/login");
  }

  return (
    <nav className="nav">
      <div className="nav-brand" aria-label="MemoriaX">
        <span>Memoria</span>
        <span className="nav-brand-accent">X</span>
      </div>
      <div className="nav-links" aria-label="主导航">
        {isAuthenticated ? (
          <NavLink
            to="/decks"
            className={({ isActive }) => `nav-link${isActive ? " active" : ""}`}
          >
            单词本
          </NavLink>
        ) : (
          <>
            <NavLink to="/login" className={({ isActive }) => `nav-link${isActive ? " active" : ""}`}>
              登录
            </NavLink>
            <NavLink
              to="/register"
              className={({ isActive }) => `nav-link${isActive ? " active" : ""}`}
            >
              注册
            </NavLink>
          </>
        )}
      </div>
      <div className="nav-right">
        {isAuthenticated ? <span className="user-chip">{userEmail || "已登录用户"}，你好</span> : null}
        {isAuthenticated ? (
          <button className="btn btn-ghost" onClick={handleLogout}>
            退出
          </button>
        ) : null}
      </div>
    </nav>
  );
}

export default function App() {
  return (
    <div className="app-shell">
      <NavBar />
      <main className="content">
        <Routes>
          <Route path="/" element={<Navigate to="/decks" replace />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route
            path="/decks"
            element={
              <ProtectedRoute>
                <DecksPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/decks/:deckId/words"
            element={
              <ProtectedRoute>
                <DeckWordsPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/deck/:id/import"
            element={
              <ProtectedRoute>
                <DeckImportPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/decks/:deckId/review"
            element={
              <ProtectedRoute>
                <DeckReviewPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/deck/:id/review"
            element={
              <ProtectedRoute>
                <DeckReviewPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/deck/:id/stats"
            element={
              <ProtectedRoute>
                <DeckStatsPage />
              </ProtectedRoute>
            }
          />
        </Routes>
      </main>
    </div>
  );
}
