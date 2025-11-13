import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import { createI18n } from 'vue-i18n'
import VuePlyr from 'vue-plyr'
import 'vue-plyr/dist/vue-plyr.css'
import router from './router'
import App from './App.vue'
import './style.css'

// Import locales
import ru from './locales/ru.js'
import en from './locales/en.js'

const i18n = createI18n({
  legacy: false,
  locale: localStorage.getItem('locale') || 'ru',
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

app.use(createPinia())
app.use(router)
app.use(ElementPlus)
app.use(i18n)
app.use(VuePlyr, {
  plyr: {
    controls: [
      'play-large',
      'play',
      'progress',
      'current-time',
      'mute',
      'volume',
      'settings',
      'fullscreen'
    ],
    settings: ['quality', 'speed'],
    speed: {
      selected: 1,
      options: [0.5, 0.75, 1, 1.25, 1.5, 1.75, 2]
    },
    keyboard: {
      focused: true,
      global: false
    },
    tooltips: {
      controls: true,
      seek: true
    },
    clickToPlay: true,
    hideControls: true,
    resetOnEnd: false
  }
})

app.mount('#app')
