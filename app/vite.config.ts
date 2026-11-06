import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// Relative base so the static build works at https://<user>.github.io/<repo>/ and locally.
export default defineConfig({
  plugins: [react()],
  base: './',
  build: { chunkSizeWarningLimit: 1500 },
  test: { environment: 'node', include: ['src/**/*.test.ts'] },
});
