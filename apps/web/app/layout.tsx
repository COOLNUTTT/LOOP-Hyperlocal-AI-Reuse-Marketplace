// Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
import type { Metadata, Viewport } from "next";
import Link from "next/link";
import { PlusCircle } from "lucide-react";
import "./globals.css";

export const metadata: Metadata = {
  title: "LOOP | Hyperlocal AI Reuse Marketplace",
  description: "Hyperlocal reuse marketplace for Electronics, Furniture, Books, and Hobbies.",
  manifest: "/manifest.webmanifest",
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 5,
  themeColor: "#0f172a",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-slate-50 text-slate-900 antialiased flex flex-col">
        <header className="sticky top-0 z-30 border-b border-slate-200 bg-white/95 backdrop-blur px-4 py-3">
          <div className="mx-auto flex max-w-4xl items-center justify-between">
            <Link href="/" className="flex items-center gap-2">
              <span className="text-xl font-bold tracking-tight text-slate-900">LOOP</span>
              <span className="text-[11px] font-medium text-slate-500 bg-slate-100 rounded-full px-2 py-0.5">
                Campus Reuse
              </span>
            </Link>

            <nav className="flex items-center gap-2 text-xs font-semibold">
              <Link
                href="/sell"
                className="flex items-center gap-1.5 rounded-lg bg-emerald-600 px-3 py-1.5 text-white hover:bg-emerald-700 transition-colors shadow-sm"
              >
                <PlusCircle className="h-3.5 w-3.5" />
                <span>Sell Item</span>
              </Link>
              <Link
                href="/login"
                className="rounded-lg px-2.5 py-1.5 text-slate-700 hover:bg-slate-100 transition-colors"
              >
                Sign In
              </Link>
              <Link
                href="/register"
                className="rounded-lg bg-slate-900 px-3 py-1.5 text-white hover:bg-slate-800 transition-colors"
              >
                Join
              </Link>
              <Link
                href="/profile"
                className="hidden sm:inline-block rounded-lg border border-slate-200 px-2.5 py-1.5 text-slate-700 hover:bg-slate-100 transition-colors"
              >
                Profile
              </Link>
            </nav>
          </div>
        </header>
        <main className="flex-1 mx-auto w-full max-w-4xl px-3 py-4 sm:px-4 sm:py-6">{children}</main>
        <footer className="border-t border-slate-200 bg-white py-4 text-center text-xs text-slate-500">
          <div className="flex flex-wrap justify-center gap-4 mb-1">
            <Link href="/sell" className="hover:underline">
              Sell / Donate / Swap
            </Link>
            <span>•</span>
            <Link href="/consent" className="hover:underline">
              DPDP Privacy Notice
            </Link>
            <span>•</span>
            <Link href="/profile" className="hover:underline">
              Settings & Data Export
            </Link>
          </div>
          <p>LOOP - Human-in-the-loop, privacy-preserving reuse marketplace.</p>
        </footer>
      </body>
    </html>
  );
}
