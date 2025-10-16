import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: 'standalone',
  // Fix workspace root detection for Docker builds
  outputFileTracingRoot: '/app',
  // Remove experimental webpack config that can cause issues in Docker
  // TypeScript paths in tsconfig.json will handle the @ alias
};

export default nextConfig;
