/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    domains: ['t3.ftcdn.net', 'media.istockphoto.com', 'img.global.news.samsung.com', 'www.shutterstock.com', 'fdn2.gsmarena.com', 'cdn.discordapp.com', 'localhost', '127.0.0.1'],
    remotePatterns: [
      {
        protocol: 'http',
        hostname: '127.0.0.1',
        port: '8000',
        pathname: '/media/**',
      },
    ],
  },
  modularizeImports: {
    "react-bootstrap": {
      transform: "react-bootstrap/{{member}}",
    },
    lodash: {
      transform: "lodash/{{member}}",
    },
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://127.0.0.1:8000/myapp/api/:path*',
      },
      {
        source: '/media/:path*',
        destination: 'http://127.0.0.1:8000/media/:path*',
      },
    ];
  },
  
  
}

module.exports = nextConfig
