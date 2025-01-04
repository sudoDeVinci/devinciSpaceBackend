import path from 'path'

export default {
  root: './src',
  base: '/',
  publicDir: '../public',
  build: {
    outDir: '../static',
    emptyOutDir: true,
    target: 'esnext'
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src/css')
    }
  }
}
