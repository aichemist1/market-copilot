import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Market Copilot",
  description: "Congressional transaction intelligence feed",
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
