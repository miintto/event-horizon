import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // 정적 export (out/ 디렉토리로 순수 정적 파일 생성, Node 런타임 불필요)
  output: "export",
  // 좌측 하단 개발 인디케이터가 사이드바를 가린다. 에러 오버레이는 그대로 뜬다
  devIndicators: false,
};

export default nextConfig;
