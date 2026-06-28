"use client";

import { Suspense, useEffect, useState } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import Link from "next/link";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

function VerifyContent() {
  const params = useSearchParams();
  const router = useRouter();
  const token = params.get("token");
  const [status, setStatus] = useState<"loading" | "success" | "error">("loading");
  const [message, setMessage] = useState("");

  useEffect(() => {
    if (!token) {
      setStatus("error");
      setMessage("No verification token found in the URL.");
      return;
    }

    fetch(`${API_BASE}/api/auth/verify?token=${token}`, { credentials: "include" })
      .then(async (res) => {
        const data = await res.json();
        if (res.ok) {
          setStatus("success");
          setMessage(data.message);
          setTimeout(() => router.push("/"), 2500);
        } else {
          setStatus("error");
          setMessage(data.detail || "Verification failed.");
        }
      })
      .catch(() => {
        setStatus("error");
        setMessage("Something went wrong. Please try again.");
      });
  }, [token, router]);

  return (
    <>
      {status === "loading" && (
        <>
          <h2 style={{ marginBottom: 12 }}>Verifying your email...</h2>
          <p style={{ color: "var(--text-secondary)" }}>Please wait a moment.</p>
        </>
      )}

      {status === "success" && (
        <div className="auth-success">
          <strong>✅ Email verified!</strong><br />
          {message}<br />
          <span style={{ fontSize: "0.8rem", marginTop: "8px", display: "block" }}>Redirecting to the leaderboard...</span>
        </div>
      )}

      {status === "error" && (
        <>
          <div className="auth-error" style={{ marginBottom: "20px" }}>
            ❌ {message}
          </div>
          <Link href="/auth/register" style={{ color: "var(--gold)", fontWeight: 600 }}>
            Try registering again
          </Link>
        </>
      )}
    </>
  );
}

export default function VerifyPage() {
  return (
    <div className="auth-page">
      <div className="auth-bg" />
      <div className="auth-card" style={{ textAlign: "center" }}>
        <div style={{ width: 56, height: 56, borderRadius: 16, background: "linear-gradient(135deg, var(--gold), var(--purple))", display: "flex", alignItems: "center", justifyContent: "center", fontSize: "1.6rem", margin: "0 auto 20px" }}>
          🎌
        </div>
        <Suspense fallback={<p style={{ color: "var(--text-secondary)" }}>Loading...</p>}>
          <VerifyContent />
        </Suspense>
      </div>
    </div>
  );
}
