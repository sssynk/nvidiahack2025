import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: 'standalone',
  experimental: {
    turbo: {
      // Ensure Turbopack resolves the '@' alias if you re-enable it later
      resolveAlias: {
        '@': './src',
      },
    },
  },
};

export default nextConfig;
