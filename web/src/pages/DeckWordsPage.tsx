import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import { Link, useParams } from "react-router-dom";
import { apiRequest } from "../api";
import { AlertMessage } from "../components/AlertMessage";

type Word = {
  id: number;
  deck_id: number;
  user_id: number;
  word: string;
  definition: string | null;
  created_at: string;
};

type WordListResponse = {
  items: Word[];
  page: number;
  size: number;
  total: number;
};

type DeckInfo = {
  id: number;
  name: string;
};

export function DeckWordsPage() {
  const { deckId } = useParams();
  const [deckName, setDeckName] = useState("");
  const [items, setItems] = useState<Word[]>([]);
  const [word, setWord] = useState("");
  const [definition, setDefinition] = useState("");
  const [error, setError] = useState("");
  const [errorDetail, setErrorDetail] = useState("");
  const [loading, setLoading] = useState(false);
  const [creating, setCreating] = useState(false);
  const [deletingWordId, setDeletingWordId] = useState<number | null>(null);

  async function loadWords() {
    if (!deckId) {
      setError("无效的单词本 id");
      setErrorDetail("");
      return;
    }
    setError("");
    setErrorDetail("");
    setLoading(true);
    try {
      const data = await apiRequest<WordListResponse>(`/decks/${deckId}/words?page=1&size=100`);
      setItems(data.items);
    } catch (err) {
      const raw = err instanceof Error ? err.message : "加载单词失败";
      setError("加载单词失败，请稍后重试。");
      setErrorDetail(raw);
      console.error("[DeckWordsPage] load words failed:", err);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadWords();
  }, [deckId]);

  useEffect(() => {
    async function loadDeckName() {
      if (!deckId) {
        return;
      }
      try {
        const data = await apiRequest<DeckInfo>(`/decks/${deckId}`);
        setDeckName(data.name);
      } catch (err) {
        console.error("[DeckWordsPage] load deck name failed:", err);
      }
    }
    void loadDeckName();
  }, [deckId]);

  async function handleCreateWord(e: FormEvent) {
    e.preventDefault();
    if (!deckId) {
      setError("无效的单词本 id");
      setErrorDetail("");
      return;
    }
    const normalizedWord = word.trim();
    if (!normalizedWord) {
      setError("单词不能为空。");
      setErrorDetail("");
      return;
    }

    setError("");
    setErrorDetail("");
    setCreating(true);
    try {
      await apiRequest(`/decks/${deckId}/words`, {
        method: "POST",
        bodyJson: {
          word: normalizedWord,
          definition: definition.trim() || null,
        },
      });
      setWord("");
      setDefinition("");
      await loadWords();
    } catch (err) {
      const raw = err instanceof Error ? err.message : "创建单词失败";
      if (raw.includes("已存在") || raw.toLowerCase().includes("conflict")) {
        setError("该单词已存在，无需重复添加");
      } else {
        setError("创建单词失败，请检查输入后重试。");
      }
      setErrorDetail(raw);
      console.error("[DeckWordsPage] create word failed:", err);
    } finally {
      setCreating(false);
    }
  }

  async function handleDeleteWord(wordId: number) {
    const confirmed = window.confirm("确认删除这个单词吗？");
    if (!confirmed) {
      return;
    }
    setError("");
    setErrorDetail("");
    setDeletingWordId(wordId);
    try {
      await apiRequest<void>(`/words/${wordId}`, {
        method: "DELETE",
      });
      await loadWords();
    } catch (err) {
      const raw = err instanceof Error ? err.message : "删除单词失败";
      setError("删除单词失败，请稍后重试。");
      setErrorDetail(raw);
      console.error("[DeckWordsPage] delete word failed:", err);
    } finally {
      setDeletingWordId(null);
    }
  }

  return (
    <section className="page">
      <h1>单词列表（{deckName || `单词本 ${deckId}`}）</h1>

      <div className="card">
        <form onSubmit={handleCreateWord} className="stack">
          <label className="field">
            <span>单词</span>
            <input
              value={word}
              onChange={(e) => setWord(e.target.value)}
              placeholder="例如：apple"
              required
            />
          </label>
          <label className="field">
            <span>释义</span>
            <input
              value={definition}
              onChange={(e) => setDefinition(e.target.value)}
              placeholder="例如：苹果（可选）"
            />
          </label>
          <button type="submit" className="btn btn-primary" disabled={creating}>
            {creating ? "添加中..." : "添加单词"}
          </button>
        </form>
      </div>

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

      <div className="card">
        <h2 className="section-title">单词列表</h2>
        {loading ? <p className="muted">加载中...</p> : null}
        {!loading && items.length === 0 ? <p className="muted">当前单词本还没有单词。</p> : null}
        <ul className="list">
          {items.map((item) => (
            <li key={item.id} className="list-row">
              <div>
                <strong>{item.word}</strong>
                <div className="muted">{item.definition || "(无释义)"}</div>
              </div>
              <div className="actions">
                <button
                  className="btn btn-ghost"
                  onClick={() => void handleDeleteWord(item.id)}
                  disabled={deletingWordId === item.id}
                >
                  {deletingWordId === item.id ? "删除中..." : "删除"}
                </button>
              </div>
            </li>
          ))}
        </ul>
      </div>

      <p className="muted">
        <Link to="/decks">返回单词本</Link>
      </p>
    </section>
  );
}
