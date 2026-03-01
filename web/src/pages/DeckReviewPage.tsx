import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { apiRequest } from "../api";

type QueueItem = {
  word_id: number;
  word: string;
  definition: string | null;
  due_at: string | null;
  repetition: number;
  interval: number;
  ease_factor: number;
  is_new: boolean;
};

type DeckInfo = {
  id: number;
  name: string;
};

export function DeckReviewPage() {
  const params = useParams();
  const deckId = params.deckId ?? params.id ?? "";
  const [deckName, setDeckName] = useState("");
  const [queue, setQueue] = useState<QueueItem[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [showDefinition, setShowDefinition] = useState(false);
  const [reviewedCount, setReviewedCount] = useState(0);
  const [roundTotal, setRoundTotal] = useState(0);
  const [roundCompleted, setRoundCompleted] = useState(false);

  async function loadQueue() {
    if (!deckId) {
      setError("无效的单词本 id");
      return;
    }
    setError("");
    setLoading(true);
    try {
      const data = await apiRequest<QueueItem[]>(`/reviews/queue?deck_id=${deckId}&limit=20`);
      setQueue(data);
      setShowDefinition(false);
      if (reviewedCount === 0) {
        setRoundTotal(data.length);
      }
      if (data.length === 0) {
        setRoundCompleted(reviewedCount > 0);
      } else {
        setRoundCompleted(false);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "加载复习队列失败");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadQueue();
  }, [deckId, reviewedCount]);

  useEffect(() => {
    async function loadDeckName() {
      if (!deckId) {
        return;
      }
      try {
        const data = await apiRequest<DeckInfo>(`/decks/${deckId}`);
        setDeckName(data.name);
      } catch (err) {
        console.error("[DeckReviewPage] load deck name failed:", err);
      }
    }
    void loadDeckName();
  }, [deckId]);

  useEffect(() => {
    setReviewedCount(0);
    setRoundTotal(0);
    setRoundCompleted(false);
    setShowDefinition(false);
  }, [deckId]);

  async function submitGrade(grade: number) {
    if (!queue[0]) {
      return;
    }
    setError("");
    setSubmitting(true);
    try {
      await apiRequest(`/reviews/${queue[0].word_id}`, {
        method: "POST",
        bodyJson: { grade },
      });
      setReviewedCount((prev) => prev + 1);
    } catch (err) {
      setError(err instanceof Error ? err.message : "提交评分失败");
    } finally {
      setSubmitting(false);
    }
  }

  const current = queue[0];
  const doneCount = Math.min(reviewedCount, roundTotal);
  const progressPercent = roundTotal > 0 ? Math.min(100, Math.round((doneCount / roundTotal) * 100)) : 0;

  return (
    <section>
      <h1>开始复习（{deckName || `单词本 ${deckId}`}）</h1>
      {loading && <p>加载中...</p>}
      {error && <p className="error">{error}</p>}

      {!loading && !current && !roundCompleted ? <p>暂无需要复习的单词。</p> : null}

      {!loading && !current && roundCompleted ? (
        <div className="card">
          <h2>本轮复习已完成</h2>
          <p>当前没有需要复习的单词。</p>
        </div>
      ) : null}

      {current && (
        <div className="card">
          <h2>{current.word}</h2>
          {!showDefinition ? (
            <button className="btn btn-ghost review-reveal-btn" onClick={() => setShowDefinition(true)}>
              显示释义
            </button>
          ) : (
            <p>释义：{current.definition ?? "（无释义）"}</p>
          )}
          <p className="muted review-grade-hint">你的掌握程度：</p>
          <div className="actions review-grade-group">
            <button className="btn btn-primary" onClick={() => submitGrade(0)} disabled={submitting}>
              忘记
            </button>
            <button className="btn btn-primary" onClick={() => submitGrade(1)} disabled={submitting}>
              困难
            </button>
            <button className="btn btn-primary" onClick={() => submitGrade(2)} disabled={submitting}>
              一般
            </button>
            <button className="btn btn-primary" onClick={() => submitGrade(3)} disabled={submitting}>
              简单
            </button>
          </div>
          {roundTotal > 0 ? (
            <div className="review-progress">
              <div className="review-progress-track" aria-hidden="true">
                <div className="review-progress-fill" style={{ width: `${progressPercent}%` }} />
              </div>
              <p className="muted review-progress-text">
                进度：{doneCount} / {roundTotal}
              </p>
            </div>
          ) : null}
        </div>
      )}
      <p>
        <Link to="/decks">返回单词本</Link>
      </p>
    </section>
  );
}
