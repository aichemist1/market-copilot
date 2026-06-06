"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import styles from "./product-shell.module.css";

const navigationItems = [
  { href: "/", label: "Dashboard" },
  { href: "/trade-explorer", label: "Trade Explorer" },
  { href: "/research", label: "Research" },
  { href: "/signals", label: "Signals" },
  { href: "/alerts", label: "Alerts" },
];

export function ProductShell({
  title,
  subtitle,
  children,
}: {
  title: string;
  subtitle: string;
  children: React.ReactNode;
}) {
  const pathname = usePathname();

  return (
    <main className={styles.page}>
      <div className={styles.shell}>
        <header className={styles.header}>
          <div className={styles.headerTop}>
            <div className={styles.logoWrap}>
              <span className={styles.logoMark}>M</span>
              <span className={styles.logoText}>market copilot</span>
            </div>
            <button className={styles.accountButton} type="button">
              Account
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
          <div className={styles.headlineBlock}>
            <h1 className={styles.title}>{title}</h1>
            <p className={styles.subtitle}>{subtitle}</p>
          </div>
        </header>

        {children}
      </div>
    </main>
  );
}
