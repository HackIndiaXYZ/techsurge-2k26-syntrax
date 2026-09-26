import type { Metadata } from "next";
import "./globals.css";
import { AppProvider } from "@/lib/context";

export const metadata: Metadata = {
  title: "TerraFlux — Climate Intelligence Platform",
  description: "Autonomous climate protection, built on trusted weather intelligence. Real weather. Verified data. Fair outcomes.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet" />
        <script src="https://checkout.razorpay.com/v1/checkout.js" async></script>
      </head>
      <body>
        <AppProvider>
          {children}
        </AppProvider>
      </body>
    </html>
  );
}
