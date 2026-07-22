import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // 정적 export (out/ 디렉토리로 순수 정적 파일 생성, Node 런타임 불필요)
  output: "export",
};

export default nextConfig;
