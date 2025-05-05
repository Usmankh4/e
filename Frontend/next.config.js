/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    domains: ['t3.ftcdn.net', 'media.istockphoto.com', 'img.global.news.samsung.com', 'www.shutterstock.com', 'fdn2.gsmarena.com', 'cdn.discordapp.com', 'localhost', '127.0.0.1'],
  },
  modularizeImports: {
    "react-bootstrap": {
      transform: "react-bootstrap/{{member}}",
    },
    lodash: {
      transform: "lodash/{{member}}",
    },
  },
  port: 3000,
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://127.0.0.1:8000/myapp/api/:path*',
      },
    ];
  },
}

module.exports = nextConfig
