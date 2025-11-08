import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "LifeLine - Your Personal Timeline Assistant",
  description: "Capture, organize, and reflect on the meaningful moments of your life with AI",
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

