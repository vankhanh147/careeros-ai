import type { Metadata } from "next";
import type { ReactNode } from "react";

import { Providers } from "./providers";
import "./globals.css";

export const metadata: Metadata = {
  title: "CareerOS AI",
  description: "Nền tảng AI hỗ trợ định hướng và phát triển nghề nghiệp công nghệ"
};

export default function RootLayout({ children }: Readonly<{ children: ReactNode }>) {
  return (
    <html lang="vi">
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
