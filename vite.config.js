import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'
import { visualizer } from 'rollup-plugin-visualizer'
import viteCompression from 'vite-plugin-compression'

export default defineConfig({
  plugins: [
    vue({
      script: {
        defineModel: true,
        propsDestructure: true
      }
    }),
    // Gzip compression
    viteCompression({
      verbose: true,
      disable: false,
      threshold: 10240, // 10kb
      algorithm: 'gzip',
      ext: '.gz',
    }),
    // Brotli compression
    viteCompression({
      verbose: true,
      disable: false,
      threshold: 10240,
      algorithm: 'brotliCompress',
      ext: '.br',
    }),
    // Bundle analyzer (только для разработки)
    process.env.ANALYZE && visualizer({
      open: true,
      gzipSize: true,
      brotliSize: true,
    }),
  ].filter(Boolean),
  
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
  
  server: {
    port: 3000,
    open: true,
    proxy: {
      '/api/minio': {
        target: 'https://minio.dmed.gubkin.uz',
        changeOrigin: true,
        secure: true,
        rewrite: (path) => path.replace(/^\/api\/minio/, ''),
        configure: (proxy, options) => {
          proxy.on('proxyReq', (proxyReq, req, res) => {
            proxyReq.setHeader('Host', 'minio.dmed.gubkin.uz')
          })
        }
      }
    }
  },
  
  // Оптимизация зависимостей
  optimizeDeps: {
    include: [
      'vue',
      'vue-router',
      'pinia',
      'element-plus',
      '@element-plus/icons-vue',
      'axios'
    ],
    exclude: ['pdfjs-dist/build/pdf.worker.min.js'],
  },
  
  build: {
    outDir: 'dist',
    sourcemap: false,
    minify: 'terser', // Лучшая минификация
    target: 'es2015',
    cssCodeSplit: true,
    
    // Настройки терминификации
    terserOptions: {
      compress: {
        drop_console: true, // Удаляем console.log в production
        drop_debugger: true,
        pure_funcs: ['console.log', 'console.info', 'console.debug', 'console.warn'],
        passes: 2,
      },
      format: {
        comments: false, // Удаляем комментарии
      },
    },
    
    // Увеличиваем chunk size warning limit
    chunkSizeWarningLimit: 1000,
    
    // Оптимизированный code splitting
    rollupOptions: {
      output: {
        manualChunks: (id) => {
          // Vue core
          if (id.includes('node_modules/vue') || id.includes('node_modules/@vue')) {
            return 'vue-core'
          }
          
          // Element Plus
          if (id.includes('node_modules/element-plus')) {
            return 'element-plus'
          }
          
          // Icons
          if (id.includes('@element-plus/icons-vue') || id.includes('@heroicons')) {
            return 'icons'
          }
          
          // Video players - ЕДИНЫЙ чанк для всех видео библиотек
          if (id.includes('plyr') || id.includes('video.js') || id.includes('hls.js')) {
            return 'video-player'
          }
          
          // PDF
          if (id.includes('pdfjs-dist') || id.includes('vue-pdf-embed')) {
            return 'pdf-viewer'
          }
          
          // AWS SDK (Minio)
          if (id.includes('@aws-sdk')) {
            return 'aws-sdk'
          }
          
          // Supabase
          if (id.includes('@supabase')) {
            return 'supabase'
          }
          
          // Router & State Management
          if (id.includes('vue-router') || id.includes('pinia')) {
            return 'router-store'
          }
          
          // Остальные node_modules
          if (id.includes('node_modules')) {
            return 'vendor'
          }
        },
        
        // Оптимизированные имена файлов
        chunkFileNames: 'assets/js/[name]-[hash].js',
        entryFileNames: 'assets/js/[name]-[hash].js',
        assetFileNames: (assetInfo) => {
          const info = assetInfo.name.split('.')
          const extType = info[info.length - 1]
          
          if (/\.(png|jpe?g|svg|gif|webp|avif)$/i.test(assetInfo.name)) {
            return `assets/images/[name]-[hash][extname]`
          }
          
          if (/\.(woff2?|eot|ttf|otf)$/i.test(assetInfo.name)) {
            return `assets/fonts/[name]-[hash][extname]`
          }
          
          if (/\.css$/i.test(assetInfo.name)) {
            return `assets/css/[name]-[hash][extname]`
          }
          
          return `assets/[ext]/[name]-[hash][extname]`
        },
      },
    },
    
    // Оптимизация ресурсов
    assetsInlineLimit: 4096, // 4kb - меньше будет inline
    reportCompressedSize: false, // Быстрее сборка
  },
  
  // Performance hints
  performance: {
    maxEntrypointSize: 512000,
    maxAssetSize: 512000,
  },
  
  worker: {
    format: 'es',
    rollupOptions: {
      output: {
        format: 'es',
      },
    },
  },
})
