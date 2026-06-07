"use client";

import { useEffect, useMemo, useState } from "react";
import { ProductShell } from "@/components/product-shell";
import {
  AdminInviteCode,
  createAdminInviteCode,
  fetchAdminInviteCodes,
} from "@/lib/graphql";
import { formatDisplayDate } from "@/lib/insights";
import styles from "./admin-invites-page.module.css";

export function AdminInvitesPage() {
  const [inviteCodes, setInviteCodes] = useState<AdminInviteCode[]>([]);
  const [expiresDays, setExpiresDays] = useState("14");
  const [customCode, setCustomCode] = useState("");
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      setLoading(true);
      setError(null);

      try {
        const next = await fetchAdminInviteCodes();
        if (!cancelled) {
          setInviteCodes(next);
        }
      } catch (nextError) {
        if (!cancelled) {
          setError(nextError instanceof Error ? nextError.message : "Unable to load invite codes");
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, []);

  const activeCount = useMemo(
    () => inviteCodes.filter((invite) => invite.status === "active").length,
    [inviteCodes],
  );
  const registrationUrl = useMemo(
    () => (typeof window === "undefined" ? "/register" : `${window.location.origin}/register`),
    [],
  );

  async function handleCreateInvite(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setCreating(true);
    setError(null);
    setSuccess(null);

    try {
      const nextInvite = await createAdminInviteCode({
        expiresDays: Number.parseInt(expiresDays, 10) || 14,
        code: customCode.trim() || undefined,
      });
      setInviteCodes((current) => [nextInvite, ...current]);
      setCustomCode("");
      setSuccess(`Invite code ${nextInvite.code} is ready to share.`);
    } catch (nextError) {
      setError(nextError instanceof Error ? nextError.message : "Unable to create invite code");
    } finally {
      setCreating(false);
    }
  }

  async function handleCopy(code: string) {
    try {
      await navigator.clipboard.writeText(code);
      setSuccess(`Copied ${code}. Share it with ${registrationUrl}.`);
    } catch {
      setSuccess(`Invite code ${code} is ready to share at ${registrationUrl}.`);
    }
  }

  return (
    <ProductShell
      title="Invite Codes"
      subtitle="Generate, monitor, and share invite codes without leaving the admin surface."
      compactHero
    >
      <section className={styles.layout}>
        <article className={styles.createCard}>
          <div className={styles.cardHeader}>
            <div>
              <p className={styles.sectionLabel}>Create invite</p>
              <h2 className={styles.cardTitle}>Issue a code for a new invited user.</h2>
            </div>
            <p className={styles.count}>{activeCount} active</p>
          </div>

          <form className={styles.form} onSubmit={handleCreateInvite}>
            <label className={styles.field}>
              <span>Expires in days</span>
              <input
                className={styles.input}
                inputMode="numeric"
                min="0"
                step="1"
                value={expiresDays}
                onChange={(event) => setExpiresDays(event.target.value)}
              />
            </label>

            <label className={styles.field}>
              <span>Custom code (optional)</span>
              <input
                className={styles.input}
                placeholder="MC-YOURCODE"
                value={customCode}
                onChange={(event) => setCustomCode(event.target.value.toUpperCase())}
              />
            </label>

            <button className={styles.primaryButton} disabled={creating} type="submit">
              {creating ? "Creating…" : "Generate invite code"}
            </button>
          </form>

          <div className={styles.helperBlock}>
            <p className={styles.helperLabel}>Share with users</p>
            <p className={styles.helperText}>
              Send the code alongside <strong>{registrationUrl}</strong> so users can self-register.
            </p>
          </div>

          {error ? <p className={styles.error}>{error}</p> : null}
          {success ? <p className={styles.success}>{success}</p> : null}
        </article>

        <article className={styles.listCard}>
          <div className={styles.cardHeader}>
            <div>
              <p className={styles.sectionLabel}>Recent codes</p>
              <h2 className={styles.cardTitle}>Track active, used, and expired invites.</h2>
            </div>
            <p className={styles.count}>{inviteCodes.length}</p>
          </div>

          {loading ? <p className={styles.state}>Loading invite codes…</p> : null}
          {!loading && !error && inviteCodes.length === 0 ? (
            <p className={styles.state}>No invite codes have been created yet.</p>
          ) : null}

          {!loading && inviteCodes.length > 0 ? (
            <div className={styles.stack}>
              {inviteCodes.map((invite) => (
                <article key={`${invite.code}-${invite.created_at}`} className={styles.row}>
                  <div className={styles.rowTop}>
                    <div>
                      <strong className={styles.code}>{invite.code}</strong>
                      <p className={styles.meta}>
                        Created {formatDisplayDate(invite.created_at)}
                        {invite.created_by_email ? ` · ${invite.created_by_email}` : ""}
                      </p>
                    </div>
                    <span className={invite.status === "active" ? styles.badgeActive : styles.badgeMuted}>
                      {invite.status}
                    </span>
                  </div>
                  <div className={styles.rowBottom}>
                    <span>Expires: {formatDisplayDate(invite.expires_at)}</span>
                    <span>Used: {formatDisplayDate(invite.used_at)}</span>
                    <span>{invite.used_by_email ? `Used by ${invite.used_by_email}` : "Unused"}</span>
                    <button
                      className={styles.copyButton}
                      onClick={() => void handleCopy(invite.code)}
                      type="button"
                    >
                      Copy code
                    </button>
                  </div>
                </article>
              ))}
            </div>
          ) : null}
        </article>
      </section>
    </ProductShell>
  );
}
