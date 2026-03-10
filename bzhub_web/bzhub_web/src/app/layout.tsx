import type { Metadata } from "next";
import "./globals.css";
import { Toaster } from "@/components/ui/toast";

export const metadata: Metadata = {
  title: "BzHub ERP",
  description: "BzHub — Complete ERP Suite for Small Businesses",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="bg-surface min-h-screen">
        {children}
        <Toaster />
      </body>
    </html>
  );
}
