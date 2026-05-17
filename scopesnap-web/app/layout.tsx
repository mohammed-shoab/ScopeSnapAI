import type { Metadata, Viewport } from "next";
import { ClerkProvider } from "@clerk/nextjs";
import { PostHogProvider } from "@/providers/PostHogProvider";
import "./globals.css";

export const metadata: Metadata = {
  title: "SnapAI — AI-Powered HVAC Estimation",
  description:
    "Photograph any HVAC unit. Get an instant AI assessment with Good/Better/Best estimates. Send the homeowner a beautiful report in 90 seconds.",
  manifest: "/manifest.json",
  icons: {
    icon: [
      { url: "/favicon.ico", sizes: "any" },
      { url: "/favicon.svg", type: "image/svg+xml" },
      { url: "/favicon-32.png", sizes: "32x32", type: "image/png" },
      { url: "/favicon-16.png", sizes: "16x16", type: "image/png" },
    ],
    apple: [
      { url: "/apple-touch-icon.png", sizes: "180x180", type: "image/png" },
    ],
    other: [
      { rel: "mask-icon", url: "/favicon.svg", color: "#1a8754" },
    ],
  },
  appleWebApp: {
    capable: true,
    statusBarStyle: "default",
    title: "SnapAI",
  },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
  themeColor: "#1a8754",  viewportFit: "cover",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <head>
        <link
          href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=IBM+Plex+Mono:wght@400;500;600&family=Noto+Nastaliq+Urdu:wght@400;600;700&display=swap"
          rel="stylesheet"
        />
        <link rel="apple-touch-icon" href="/apple-touch-icon.png" />
        <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
        <link rel="icon" type="image/x-icon" href="/favicon.ico" />
        <meta name="mobile-web-app-capable" content="yes" />
      </head>
      <body className="bg-surface-bg text-text-primary font-sans antialiased">
        <PostHogProvider>
          <ClerkProvider>
          {children}
          </ClerkProvider>
        </PostHogProvider>
        {/* PWA Service Worker Registration */}
        <script
          dangerouslySetInnerHTML={{
            __html: `
              if ('serviceWorker' in navigator) {
                window.addEventListener('load', function() {
                  navigator.serviceWorker.register('/sw.js').catch(function() {});
                });
              }
            `,
          }}
        />
      </body>
    </html>
  );
}

 