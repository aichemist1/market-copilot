"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
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

export function RegisterPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const nextParam = searchParams.get("next") ?? "/";
  const next = nextParam.startsWith("/") ? nextParam : "/";
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [inviteCode, setInviteCode] = useState(searchParams.get("code") ?? "");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await fetch("/api/auth/register", {
        method: "POST",
        headers: {
          "content-type": "application/json",
        },
        body: JSON.stringify({ email, password, inviteCode }),
      });
      const payload = await parseJsonResponse(response);
      if (!response.ok) {
        throw new Error(payload?.error ?? `Unable to register (${response.status})`);
      }
      router.replace(next);
      router.refresh();
    } catch (nextError) {
      setError(nextError instanceof Error ? nextError.message : "Unable to register");
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
            <h1 className={styles.title}>Register</h1>
          </div>
        </div>
        <p className={styles.subtitle}>
          Use your invite code to create an account and access the current release workspace.
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
              autoComplete="new-password"
              className={styles.input}
              onChange={(event) => setPassword(event.target.value)}
              type="password"
              value={password}
            />
          </label>
          <label className={styles.field}>
            <span>Invite code</span>
            <input
              autoComplete="off"
              className={styles.input}
              onChange={(event) => setInviteCode(event.target.value.toUpperCase())}
              type="text"
              value={inviteCode}
            />
          </label>

          {error ? <p className={styles.error}>{error}</p> : null}

          <button className={styles.submit} disabled={loading} type="submit">
            {loading ? "Creating account…" : "Create account"}
          </button>
        </form>

        <p className={styles.footerText}>
          Already have an account? <Link className={styles.footerLink} href="/login">Sign in</Link>
        </p>
      </section>
    </main>
  );
}
