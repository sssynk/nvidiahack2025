import path from "path";

const nextConfig = {
  output: 'standalone',
  // Silence workspace root warning; our project lives under `ui`
  outputFileTracingRoot: __dirname,
  turbopack: {
    resolveAlias: {
      '@/': path.resolve(__dirname, './src/'),
      // Make Turbopack resolve the common alias used in the codebase
      '@/*': path.join(__dirname, 'src', '*'),
      '@': path.resolve(__dirname, './src'),
    },
  },
  webpack: (config: any) => {
    config.resolve.alias = {
      ...config.resolve.alias,
      '@/': path.resolve(__dirname, './src/'),
      '@': path.resolve(__dirname, './src'),
    };
    return config;
  },
};

export default nextConfig;
