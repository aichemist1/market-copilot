"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
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
            <button className={styles.accountButton} onClick={handleSignOut} type="button">
              Sign out
            </button>
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
