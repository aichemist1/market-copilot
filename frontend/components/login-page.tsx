"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import styles from "./login-page.module.css";

async function parseJsonResponse(response: Response) {
  const text = await response.text();
  if (!text) {
    return null;
  }

  try {
    return JSON.parse(text) as { error?: string } | null;
  } catch {
    return null;
  }
}

export function LoginPage({ nextPath }: { nextPath?: string }) {
  const router = useRouter();
  const nextParam = nextPath ?? "/";
  const next = nextParam.startsWith("/") ? nextParam : "/";
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await fetch("/api/auth/login", {
        method: "POST",
        headers: {
          "content-type": "application/json",
        },
        body: JSON.stringify({ email, password }),
      });
      const payload = await parseJsonResponse(response);
      if (!response.ok) {
        throw new Error(payload?.error ?? `Unable to sign in (${response.status})`);
      }
      router.replace(next);
      router.refresh();
    } catch (nextError) {
      setError(nextError instanceof Error ? nextError.message : "Unable to sign in");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className={styles.page}>
      <section className={styles.card}>
        <div className={styles.brand}>
          <span className={styles.logo}>M</span>
          <div>
            <p className={styles.kicker}>Market Copilot</p>
            <h1 className={styles.title}>Sign in</h1>
          </div>
        </div>
        <p className={styles.subtitle}>
          Access the current release workspace for dashboard, trade exploration, research, and signals.
        </p>

        <form className={styles.form} onSubmit={onSubmit}>
          <label className={styles.field}>
            <span>Email</span>
            <input
              autoComplete="email"
              className={styles.input}
              onChange={(event) => setEmail(event.target.value)}
              type="email"
              value={email}
            />
          </label>
          <label className={styles.field}>
            <span>Password</span>
            <input
              autoComplete="current-password"
              className={styles.input}
              onChange={(event) => setPassword(event.target.value)}
              type="password"
              value={password}
            />
          </label>

          {error ? <p className={styles.error}>{error}</p> : null}

          <button className={styles.submit} disabled={loading} type="submit">
            {loading ? "Signing in…" : "Sign in"}
          </button>
        </form>

        <p className={styles.footerText}>
          Have an invite code? <Link className={styles.footerLink} href="/register">Create an account</Link>
        </p>
      </section>
    </main>
  );
}
