import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => ({
  plugins: [react()],
  base: '/',  // Vercel 배포용 base path
  define: {
    // 프로덕션 빌드에서는 정적 JSON 파일 사용
    'import.meta.env.VITE_USE_STATIC_DATA': mode === 'production' ? '"true"' : '"false"',
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
}))
