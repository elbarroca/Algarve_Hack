import type { Metadata } from "next";
import { Inter, Space_Grotesk } from "next/font/google";
import "./globals.css";

const primaryFont = Inter({
  variable: "--primary-font",
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700"],
});

const accentFont = Space_Grotesk({
  variable: "--accent-font",
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
});

export const metadata: Metadata = {
  title: "Algarve Hack - Inovação & Tecnologia",
  description: "Plataforma de inovação e desenvolvimento tecnológico no Algarve",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="pt" suppressHydrationWarning>
      <body
        className={`${primaryFont.variable} ${accentFont.variable} antialiased overflow-x-hidden`}
      >
        {children}
      </body>
    </html>
  );
}
