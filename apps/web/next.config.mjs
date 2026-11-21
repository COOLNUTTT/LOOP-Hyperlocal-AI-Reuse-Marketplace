// Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: "standalone",
  async rewrites() {
    const apiBase = (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000").replace(
      /\/api\/v1\/?$/,
      ""
    );
    return [
      {
        source: "/api/v1/:path*",
        destination: `${apiBase}/api/v1/:path*`,
      },
    ];
  },
};

export default nextConfig;
