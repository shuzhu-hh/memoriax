import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import { Link, useParams } from "react-router-dom";
import { apiRequest } from "../api";
import { AlertMessage } from "../components/AlertMessage";

type ImportResult = {
  imported_count: number;
  skipped_count: number;
};

type DeckInfo = {
  id: number;
  name: string;
};

function normalizeImportContent(raw: string): string {
  return raw
    .split(/\r?\n/)
    .map((line) => {
      const trimmed = line.trim();
      if (!trimmed) {
        return "";
      }
      const firstSpaceIndex = trimmed.search(/\s/);
      if (firstSpaceIndex === -1) {
        return trimmed;
      }
      const word = trimmed.slice(0, firstSpaceIndex).trim();
      const definition = trimmed.slice(firstSpaceIndex).trim();
      if (!word) {
        return "";
      }
      if (!definition) {
        return word;
      }
      return `${word}\t${definition}`;
    })
    .filter((line) => line.length > 0)
    .join("\n");
}

export function DeckImportPage() {
  const { id } = useParams();
  const [deckName, setDeckName] = useState("");
  const [content, setContent] = useState("");
  const [result, setResult] = useState<ImportResult | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    async function loadDeckName() {
      if (!id) {
        return;
      }
      try {
        const data = await apiRequest<DeckInfo>(`/decks/${id}`);
        setDeckName(data.name);
      } catch (err) {
        console.error("[DeckImportPage] load deck name failed:", err);
      }
    }
    void loadDeckName();
  }, [id]);

  async function handleImport(e: FormEvent) {
    e.preventDefault();
    if (!id) {
      setError("无效的单词本 id");
      return;
    }
    setError("");
    setResult(null);
    setLoading(true);
    try {
      const normalizedContent = normalizeImportContent(content);
      const data = await apiRequest<ImportResult>(`/decks/${id}/words/import`, {
        method: "POST",
        bodyJson: { content: normalizedContent },
      });
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "批量导入失败");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section>
      <h1>批量导入单词（{deckName || `单词本 ${id}`}）</h1>
      <p>
        格式：每行一个单词，或 <code>单词 + 空格 + 释义</code>（支持空格/Tab）
      </p>
      <form onSubmit={handleImport} className="stack">
        <textarea
          rows={10}
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder={"apple 苹果\nhot\t热\nbanana"}
          required
        />
        <button type="submit" disabled={loading}>
          {loading ? "导入中..." : "开始导入"}
        </button>
      </form>
      {error ? <AlertMessage type="error" message={error} onClose={() => setError("")} /> : null}
      {result ? (
        <AlertMessage
          type="success"
          message={
            result.imported_count > 0
              ? result.skipped_count > 0
                ? `有 ${result.skipped_count} 个单词已存在，成功导入 ${result.imported_count} 个单词`
                : `成功导入 ${result.imported_count} 个单词`
              : `没有导入新的单词（${result.skipped_count} 个已存在）`
          }
          onClose={() => setResult(null)}
        />
      ) : null}
      <p>
        <Link to="/decks">返回单词本</Link>
      </p>
    </section>
  );
}
