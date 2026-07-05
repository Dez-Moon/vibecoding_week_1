import type { NextConfig } from "next";

const isVercel = process.env.VERCEL === "true";

const nextConfig: NextConfig = {
  output: isVercel ? undefined : "export",
  images: { unoptimized: true },
  trailingSlash: true,
};

export default nextConfig;
