/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  images: {
    domains: [],
  },
  // Remove standalone output to fix SSR issues
  experimental: {
    serverComponentsExternalPackages: ['@apollo/client'],
  },
}

module.exports = nextConfig
