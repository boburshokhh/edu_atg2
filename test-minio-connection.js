/**
 * Простой скрипт для проверки доступности MinIO сервера
 * Проверяет различные варианты подключения
 */

import https from 'https'
import http from 'http'

const colors = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m'
}

function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`)
}

function logSuccess(message) {
  log(`✅ ${message}`, 'green')
}

function logError(message) {
  log(`❌ ${message}`, 'red')
}

function logInfo(message) {
  log(`ℹ️  ${message}`, 'blue')
}

function logWarning(message) {
  log(`⚠️  ${message}`, 'yellow')
}

// Проверка доступности URL
function checkUrl(url, useHttps = true) {
  return new Promise((resolve) => {
    const client = useHttps ? https : http
    const startTime = Date.now()
    
    const req = client.get(url, { timeout: 5000 }, (res) => {
      const duration = Date.now() - startTime
      resolve({
        success: true,
        statusCode: res.statusCode,
        duration,
        headers: res.headers
      })
      res.destroy()
    })
    
    req.on('error', (error) => {
      const duration = Date.now() - startTime
      resolve({
        success: false,
        error: error.message,
        code: error.code,
        duration
      })
    })
    
    req.on('timeout', () => {
      req.destroy()
      resolve({
        success: false,
        error: 'Timeout',
        duration: Date.now() - startTime
      })
    })
    
    req.setTimeout(5000)
  })
}

// Основная функция проверки
async function testConnection() {
  log('\n' + '='.repeat(60), 'cyan')
  log('🔍 ПРОВЕРКА ДОСТУПНОСТИ MINIO СЕРВЕРА', 'cyan')
  log('='.repeat(60), 'cyan')
  
  const baseHost = 'minio.dmed.gubkin.uz'
  const ports = [9000, 443, 80, 9001]
  const protocols = [
    { name: 'HTTPS', useHttps: true },
    { name: 'HTTP', useHttps: false }
  ]
  
  const results = []
  
  for (const protocol of protocols) {
    for (const port of ports) {
      const url = `${protocol.useHttps ? 'https' : 'http'}://${baseHost}:${port}`
      log(`\n📡 Проверка: ${url}`, 'blue')
      
      const result = await checkUrl(url, protocol.useHttps)
      results.push({ url, ...result, protocol: protocol.name, port })
      
      if (result.success) {
        logSuccess(`Доступен! Статус: ${result.statusCode}, Время ответа: ${result.duration}ms`)
        if (result.headers && result.headers.server) {
          logInfo(`Сервер: ${result.headers.server}`)
        }
      } else {
        logError(`Недоступен: ${result.error || result.code || 'Unknown error'}`)
      }
    }
  }
  
  // Итоговый отчет
  log('\n' + '='.repeat(60), 'cyan')
  log('📊 ИТОГОВЫЙ ОТЧЕТ', 'cyan')
  log('='.repeat(60), 'cyan')
  
  const available = results.filter(r => r.success)
  const unavailable = results.filter(r => !r.success)
  
  if (available.length > 0) {
    logSuccess(`\nДоступные варианты (${available.length}):`)
    available.forEach(r => {
      log(`  ✅ ${r.url} - ${r.statusCode} (${r.duration}ms)`, 'green')
    })
    
    // Рекомендация
    const recommended = available.find(r => r.port === 9000 && r.protocol === 'HTTPS') ||
                       available.find(r => r.port === 9000 && r.protocol === 'HTTP') ||
                       available[0]
    
    if (recommended) {
      log('\n💡 РЕКОМЕНДУЕМЫЙ ENDPOINT:', 'yellow')
      log(`   ${recommended.url}`, 'cyan')
      log(`\nОбновите конфигурацию в minioService.js:`, 'yellow')
      log(`   endpoint: '${recommended.url.replace(/:\d+$/, '')}:${recommended.port}'`, 'cyan')
      log(`   tls: ${recommended.protocol === 'HTTPS'}`, 'cyan')
    }
  } else {
    logError('\n❌ Ни один вариант не доступен!')
    logWarning('Возможные причины:')
    logWarning('  1. Сервер недоступен или заблокирован файрволом')
    logWarning('  2. Неправильное имя хоста')
    logWarning('  3. Проблемы с сетью')
  }
  
  if (unavailable.length > 0) {
    log(`\n⚠️  Недоступные варианты (${unavailable.length}):`)
    unavailable.forEach(r => {
      log(`  ❌ ${r.url} - ${r.error || r.code || 'Unknown'}`, 'red')
    })
  }
  
  log('\n' + '='.repeat(60), 'cyan')
  log('')
}

// Запуск проверки
testConnection().catch(error => {
  logError(`Критическая ошибка: ${error.message}`)
  console.error(error)
  process.exit(1)
})

