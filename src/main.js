import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import { createI18n } from 'vue-i18n'
import router from './router'
import App from './App.vue'
import './style.css'
import 'flag-icons/css/flag-icons.min.css'

// Import locales
import ru from './locales/ru.js'
import en from './locales/en.js'

// Устанавливаем русский язык по умолчанию
const defaultLocale = 'ru'
const savedLocale = localStorage.getItem('locale')
const initialLocale = savedLocale && (savedLocale === 'ru' || savedLocale === 'en') ? savedLocale : defaultLocale

// Если в localStorage был неверный язык, устанавливаем русский
if (initialLocale !== defaultLocale && !savedLocale) {
  localStorage.setItem('locale', defaultLocale)
}

const i18n = createI18n({
  legacy: false,
  locale: initialLocale,
  fallbackLocale: 'ru',
  messages: {
    ru,
    en
  }
})

const app = createApp(App)

// Регистрируем все иконки Element Plus
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(router)
app.use(ElementPlus)
app.use(i18n)

// Глобальная обработка ошибок для предотвращения ошибок в консоли
window.addEventListener('error', (event) => {
  // Игнорируем ошибки от расширений браузера
  if (event.message && event.message.includes('listener') && event.message.includes('message channel')) {
    event.preventDefault()
    return false
  }
})

// Обработка необработанных промисов
window.addEventListener('unhandledrejection', (event) => {
  // Игнорируем ошибки от расширений браузера
  if (event.reason && typeof event.reason === 'string' && event.reason.includes('message channel')) {
    event.preventDefault()
    return false
  }
})

app.mount('#app')
