import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { apiRequest } from "../api";
import { AlertMessage } from "../components/AlertMessage";

type Deck = {
  id: number;
  user_id: number;
  name: string;
  created_at: string;
};

type DeckListResponse = {
  items: Deck[];
  page: number;
  size: number;
  total: number;
};

export function DecksPage() {
  const navigate = useNavigate();
  const [decks, setDecks] = useState<Deck[]>([]);
  const [name, setName] = useState("");
  const [error, setError] = useState("");
  const [errorDetail, setErrorDetail] = useState("");
  const [loading, setLoading] = useState(false);
  const [creating, setCreating] = useState(false);
  const [deletingDeckId, setDeletingDeckId] = useState<number | null>(null);

  async function loadDecks() {
    setError("");
    setErrorDetail("");
    setLoading(true);
    try {
      const data = await apiRequest<DeckListResponse>("/decks?page=1&size=50");
      setDecks(data.items);
    } catch (err) {
      const raw = err instanceof Error ? err.message : "加载单词本失败";
      setError("无法加载单词本列表，请稍后重试。");
      setErrorDetail(raw);
      console.error("[DecksPage] load decks failed:", err);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadDecks();
  }, []);

  async function handleCreateDeck(e: FormEvent) {
    e.preventDefault();
    const deckName = name.trim();
    if (!deckName) {
      setError("单词本名称不能为空。");
      setErrorDetail("");
      return;
    }
    setError("");
    setErrorDetail("");
    setCreating(true);
    try {
      await apiRequest<Deck>("/decks", {
        method: "POST",
        bodyJson: { name: deckName },
      });
      setName("");
      await loadDecks();
    } catch (err) {
      const raw = err instanceof Error ? err.message : "创建单词本失败";
      setError("创建单词本失败，请检查名称后重试。");
      setErrorDetail(raw);
      console.error("[DecksPage] create deck failed:", err);
    } finally {
      setCreating(false);
    }
  }

  async function handleDeleteDeck(deckId: number) {
    const confirmed = window.confirm("确认删除这个单词本吗？该操作不可撤销。");
    if (!confirmed) {
      return;
    }
    setError("");
    setErrorDetail("");
    setDeletingDeckId(deckId);
    try {
      await apiRequest<void>(`/decks/${deckId}`, { method: "DELETE" });
      await loadDecks();
    } catch (err) {
      const raw = err instanceof Error ? err.message : "删除单词本失败";
      setError("删除单词本失败，请稍后重试。");
      setErrorDetail(raw);
      console.error("[DecksPage] delete deck failed:", err);
    } finally {
      setDeletingDeckId(null);
    }
  }

  return (
    <section className="page">
      <h1>单词本</h1>
      <div className="card">
        <form onSubmit={handleCreateDeck} className="inline-form">
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="输入新的单词本名称"
            required
          />
          <button type="submit" className="btn btn-primary" disabled={creating}>
            {creating ? "创建中..." : "创建单词本"}
          </button>
        </form>
        {error ? (
          <AlertMessage
            type="error"
            message={error}
            rawDetail={errorDetail}
            onClose={() => {
              setError("");
              setErrorDetail("");
            }}
          />
        ) : null}
      </div>
      <div className="card">
        <h2 className="section-title">我的单词本</h2>
        {loading ? <p className="muted">加载中...</p> : null}
        {!loading && decks.length === 0 ? <p className="muted">还没有单词本，先创建一个吧。</p> : null}
        <ul className="list">
          {decks.map((deck) => (
            <li key={deck.id} className="list-row">
              <div>
                <strong>{deck.name}</strong>
              </div>
              <div className="actions">
                <button className="btn btn-ghost" onClick={() => navigate(`/decks/${deck.id}/words`)}>
                  单词列表
                </button>
                <button className="btn btn-ghost" onClick={() => navigate(`/deck/${deck.id}/import`)}>
                  批量导入
                </button>
                <button className="btn btn-ghost" onClick={() => navigate(`/decks/${deck.id}/review`)}>
                  开始复习
                </button>
                <button className="btn btn-ghost" onClick={() => navigate(`/deck/${deck.id}/stats`)}>
                  学习统计
                </button>
                <button
                  className="btn btn-ghost"
                  onClick={() => void handleDeleteDeck(deck.id)}
                  disabled={deletingDeckId === deck.id}
                >
                  {deletingDeckId === deck.id ? "删除中..." : "删除"}
                </button>
              </div>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
