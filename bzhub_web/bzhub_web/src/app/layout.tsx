import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "BizHub ERP",
  description: "BizHub — Complete ERP Suite for Small Businesses",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="bg-surface min-h-screen">{children}</body>
    </html>
  );
}
