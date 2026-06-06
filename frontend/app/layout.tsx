import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Market Intelligence Copilot",
  description: "Signals, trade exploration, and alerts built from market intelligence data",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
