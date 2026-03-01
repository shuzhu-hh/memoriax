import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../auth";
import { apiRequest, consumeAuthError } from "../api";
import { AlertMessage } from "../components/AlertMessage";

type LoginResponse = {
  access_token: string;
  token_type: string;
};

const LAST_EMAIL_KEY = "ebbvocab_last_email";

export function LoginPage() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [email, setEmail] = useState(() => localStorage.getItem(LAST_EMAIL_KEY) ?? "");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [errorDetail, setErrorDetail] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const msg = consumeAuthError();
    if (msg) {
      setError(msg);
    }
  }, []);

  function updateEmail(value: string) {
    setEmail(value);
    localStorage.setItem(LAST_EMAIL_KEY, value);
  }

  function validateForm() {
    const normalizedEmail = email.trim();
    if (!normalizedEmail) {
      return "请输入邮箱地址。";
    }
    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailPattern.test(normalizedEmail)) {
      return "邮箱格式不正确，请检查后重试。";
    }
    if (password.length < 8) {
      return "密码至少需要 8 位。";
    }
    return "";
  }

  function toFriendlyMessage(raw: string) {
    const lower = raw.toLowerCase();
    if (lower.includes("incorrect") || lower.includes("invalid") || lower.includes("401")) {
      return "邮箱或密码错误，请确认后重试。";
    }
    if (lower.includes("network") || lower.includes("failed to fetch")) {
      return "网络连接异常，请检查网络后重试。";
    }
    return "登录失败，请稍后重试。";
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    const validationError = validateForm();
    if (validationError) {
      setError(validationError);
      setErrorDetail("");
      return;
    }
    setError("");
    setErrorDetail("");
    setLoading(true);
    try {
      localStorage.setItem(LAST_EMAIL_KEY, email.trim());
      const data = await apiRequest<LoginResponse>("/auth/login", {
        method: "POST",
        bodyJson: { email: email.trim(), password },
      });
      login(data.access_token, email.trim());
      navigate("/decks");
    } catch (err) {
      const raw = err instanceof Error ? err.message : "登录失败";
      setError(toFriendlyMessage(raw));
      setErrorDetail(raw);
      setPassword("");
      console.error("[LoginPage] login failed:", err);
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="page page-auth">
      <h1>登录</h1>
      <div className="card auth-card">
        <form onSubmit={handleSubmit} className="stack">
          <label className="field">
            <span>Email</span>
            <input
              value={email}
              onChange={(e) => updateEmail(e.target.value)}
              type="email"
              autoComplete="email"
              placeholder="you@example.com"
              required
            />
          </label>
          <label className="field">
            <span>Password</span>
            <input
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              type="password"
              autoComplete="current-password"
              placeholder="至少 8 位"
              minLength={8}
              required
            />
          </label>
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
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? "登录中..." : "登录"}
          </button>
        </form>
        <p className="muted">
          没有账号？<Link to="/register">去注册</Link>
        </p>
      </div>
    </section>
  );
}
