import { useState } from "react";
import type { FormEvent } from "react";
import { Link } from "react-router-dom";
import { apiRequest } from "../api";
import { AlertMessage } from "../components/AlertMessage";

export function RegisterPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [errorDetail, setErrorDetail] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);

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
    if (lower.includes("already") || lower.includes("exists") || lower.includes("409")) {
      return "该邮箱已注册，请直接登录或更换邮箱。";
    }
    if (lower.includes("network") || lower.includes("failed to fetch")) {
      return "网络连接异常，请检查网络后重试。";
    }
    return "注册失败，请稍后重试。";
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
    setSuccess("");
    setLoading(true);
    try {
      await apiRequest("/auth/register", {
        method: "POST",
        bodyJson: { email: email.trim(), password },
      });
      setSuccess("注册成功，请前往登录。");
      setEmail("");
      setPassword("");
    } catch (err) {
      const raw = err instanceof Error ? err.message : "注册失败";
      setError(toFriendlyMessage(raw));
      setErrorDetail(raw);
      console.error("[RegisterPage] register failed:", err);
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="page page-auth">
      <h1>注册</h1>
      <div className="card auth-card">
        <form onSubmit={handleSubmit} className="stack">
          <label className="field">
            <span>Email</span>
            <input
              value={email}
              onChange={(e) => setEmail(e.target.value)}
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
              autoComplete="new-password"
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
          {success ? <AlertMessage type="success" message={success} onClose={() => setSuccess("")} /> : null}
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? "提交中..." : "注册"}
          </button>
        </form>
        <p className="muted">
          已有账号？<Link to="/login">去登录</Link>
        </p>
      </div>
    </section>
  );
}
