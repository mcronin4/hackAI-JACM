import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Chameleon",
  description: "Automate your social media marketing with content repurposing",
  icons: {
    icon: '/favicon.ico',
    shortcut: '/favicon-16x16.png',
    apple: '/apple-touch-icon.png',
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}
