import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { apiRequest } from "../api";

type Stats = {
  total_words: number;
  total_reviews: number;
  reviews_today: number;
  due_count: number;
};

type DeckInfo = {
  id: number;
  name: string;
};

export function DeckStatsPage() {
  const { id } = useParams();
  const [deckName, setDeckName] = useState("");
  const [stats, setStats] = useState<Stats | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    async function loadStats() {
      if (!id) {
        setError("无效的单词本 id");
        return;
      }
      setError("");
      setLoading(true);
      try {
        const data = await apiRequest<Stats>(`/decks/${id}/stats`);
        setStats(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "加载统计失败");
      } finally {
        setLoading(false);
      }
    }
    void loadStats();
  }, [id]);

  useEffect(() => {
    async function loadDeckName() {
      if (!id) {
        return;
      }
      try {
        const data = await apiRequest<DeckInfo>(`/decks/${id}`);
        setDeckName(data.name);
      } catch (err) {
        console.error("[DeckStatsPage] load deck name failed:", err);
      }
    }
    void loadDeckName();
  }, [id]);

  return (
    <section>
      <h1>学习统计（{deckName || `单词本 ${id}`}）</h1>
      {loading && <p>加载中...</p>}
      {error && <p className="error">{error}</p>}
      {stats && (
        <>
          <ul>
            <li>单词总数：{stats.total_words ?? 0}</li>
            <li>已复习次数：{stats.total_reviews ?? 0}</li>
            <li>今日复习次数：{stats.reviews_today ?? 0}</li>
            <li>待复习数量：{stats.due_count ?? 0}</li>
          </ul>
        </>
      )}
      <p>
        <Link to="/decks">返回单词本</Link>
      </p>
    </section>
  );
}
