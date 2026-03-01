import { useMemo } from "react";

type AlertMessageProps = {
  type?: "error" | "success" | "info";
  message: string;
  rawDetail?: string;
  onClose?: () => void;
};

export function AlertMessage({ type = "info", message, rawDetail, onClose }: AlertMessageProps) {
  const className = useMemo(() => {
    if (type === "error") return "alert alert-error";
    if (type === "success") return "alert alert-success";
    return "alert alert-info";
  }, [type]);

  return (
    <div className={className} role={type === "error" ? "alert" : "status"} aria-live="polite">
      <div className="alert-main">
        <p className="alert-text">{message}</p>
        {onClose ? (
          <button type="button" className="alert-close" onClick={onClose} aria-label="关闭提示">
            ×
          </button>
        ) : null}
      </div>
      {rawDetail ? (
        <details className="alert-details">
          <summary>查看技术细节</summary>
          <pre>{rawDetail}</pre>
        </details>
      ) : null}
    </div>
  );
}
