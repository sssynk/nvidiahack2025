import type { NextConfig } from "next";
import path from "path";

const nextConfig: NextConfig = {
  output: 'standalone',
  experimental: {
    turbo: {
      // Ensure Turbopack resolves the '@' alias to the project's 'src' directory
      resolveAlias: {
        '@': './src',
      },
    },
  },
  // Fallback for Webpack builds (e.g., if you run without Turbopack)
  webpack: (config) => {
    config.resolve = config.resolve || {};
    config.resolve.alias = {
      ...(config.resolve.alias || {}),
      '@': path.resolve(__dirname, 'src'),
    };
    return config;
  },
};

export default nextConfig;
