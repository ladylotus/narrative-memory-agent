import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Narrative Memory Agent",
  description: "Talk to your characters",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <link rel="preconnect" href="https://fonts.googleapis.com" />
      <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
      <link
        href="https://fonts.googleapis.com/css2?family=Onest:wght@400;500;600;700&display=swap"
        rel="stylesheet"
      />
      <body>
        <script dangerouslySetInnerHTML={{
          __html: `if(typeof crypto.randomUUID!=="function"){crypto.randomUUID=function(){return"10000000-1000-4000-8000-100000000000".replace(/[018]/g,c=>(c^crypto.getRandomValues(new Uint8Array(1))[0]&15>>c/4).toString(16))}}`
        }} />
        {children}</body>
    </html>
  );
}
