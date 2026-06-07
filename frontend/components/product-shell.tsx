"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import styles from "./product-shell.module.css";

const navigationItems = [
  { href: "/", label: "Dashboard" },
  { href: "/trade-explorer", label: "Trade Explorer" },
  { href: "/research", label: "Research" },
  { href: "/signals", label: "Signals" },
];

export function ProductShell({
  title,
  subtitle,
  compactHero = false,
  children,
}: {
  title: string;
  subtitle: string;
  compactHero?: boolean;
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const [isAdmin, setIsAdmin] = useState(false);

  useEffect(() => {
    let cancelled = false;

    async function loadSession() {
      try {
        const response = await fetch("/api/auth/me", {
          cache: "no-store",
        });
        if (!response.ok) {
          if (!cancelled) {
            setIsAdmin(false);
          }
          return;
        }

        const payload = (await response.json()) as {
          session?: { profile?: string } | null;
        };

        if (!cancelled) {
          setIsAdmin(payload.session?.profile === "admin");
        }
      } catch {
        if (!cancelled) {
          setIsAdmin(false);
        }
      }
    }

    loadSession();
    return () => {
      cancelled = true;
    };
  }, []);

  async function handleSignOut() {
    await fetch("/api/auth/logout", {
      method: "POST",
    });
    window.location.href = "/login";
  }

  return (
    <main className={styles.page}>
      <div className={styles.shell}>
        <header className={styles.header}>
          <div className={styles.headerTop}>
            <div className={styles.logoWrap}>
              <span className={styles.logoMark}>M</span>
              <span className={styles.logoText}>market copilot</span>
            </div>
            <div className={styles.headerActions}>
              {isAdmin ? (
                <>
                  <Link className={styles.adminLink} href="/admin/invites">
                    Invite Codes
                  </Link>
                  <Link className={styles.adminLink} href="/admin/review">
                    Review Queue
                  </Link>
                </>
              ) : null}
              <button className={styles.accountButton} onClick={handleSignOut} type="button">
                Sign out
              </button>
            </div>
          </div>
          <div className={styles.headerBottom}>
            <nav className={styles.nav} aria-label="Primary">
              {navigationItems.map((item) => {
                const isActive = pathname === item.href;

                return (
                  <Link
                    key={item.href}
                    className={isActive ? styles.navActive : styles.navLink}
                    href={item.href}
                  >
                    {item.label}
                  </Link>
                );
              })}
            </nav>
          </div>
          <div className={compactHero ? styles.headlineBlockCompact : styles.headlineBlock}>
            <h1 className={compactHero ? styles.titleCompact : styles.title}>{title}</h1>
            <p className={compactHero ? styles.subtitleCompact : styles.subtitle}>{subtitle}</p>
          </div>
        </header>

        {children}
      </div>
    </main>
  );
}
