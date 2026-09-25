import type { Metadata, Viewport } from 'next';
import '../index.css';
import React from 'react';

export const metadata: Metadata = {
  title: 'docta | African Multimodal Dietary Intelligence',
  description: 'Multimodal African food identification and conventional portion scaling intelligence.',
  manifest: '/manifest.json',
  icons: {
    icon: '/favicon.svg',
  },
};

export const viewport: Viewport = {
  themeColor: '#5B50E5',
  width: 'device-width',
  initialScale: 1,
  maximumScale: 1,
  userScalable: false,
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="bg-slate-50 text-gray-900 antialiased selection:bg-indigo-100 selection:text-indigo-700 min-h-screen">
        {children}
      </body>
    </html>
  );
}
