<template>
  <footer class="relative bg-gray-800 text-white">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <!-- Main Content -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
        <!-- Column 1: Useful Links -->
        <div>
          <h3 class="text-lg font-bold text-white mb-4 relative">
            Полезные ссылки
            <div class="absolute bottom-0 left-0 w-12 h-0.5 bg-red-500" />
          </h3>
          <ul class="space-y-3">
            <li class="flex items-center">
              <span class="text-gray-400 mr-2">></span>
              <a
                href="#about"
                class="text-gray-400 hover:text-white transition-colors"
              >О нас</a>
            </li>
            <li class="flex items-center">
              <span class="text-gray-400 mr-2">></span>
              <a
                href="/courses"
                class="text-gray-400 hover:text-white transition-colors"
              >Обучение</a>
            </li>
            <li class="flex items-center">
              <span class="text-gray-400 mr-2">></span>
              <a
                href="/stations"
                class="text-gray-400 hover:text-white transition-colors"
              >Станции</a>
            </li>
            <li class="flex items-center">
              <span class="text-gray-400 mr-2">></span>
              <a
                href="#contact"
                class="text-gray-400 hover:text-white transition-colors"
              >Контакты</a>
            </li>
          </ul>
        </div>

        <!-- Column 2: Contact Information -->
        <div>
          <h3 class="text-lg font-bold text-white mb-4 relative">
            Контактные данные
            <div class="absolute bottom-0 left-0 w-12 h-0.5 bg-red-500" />
          </h3>
          <ul class="space-y-3">
            <li class="flex items-center">
              <svg
                class="w-4 h-4 text-white mr-3 flex-shrink-0"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path
                  fill-rule="evenodd"
                  d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z"
                  clip-rule="evenodd"
                />
              </svg>
              <span class="text-gray-400">Ташкент, Узбекистан</span>
            </li>
            <li class="flex items-center">
              <svg
                class="w-4 h-4 text-white mr-3 flex-shrink-0"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path d="M2.003 5.884L10 9.882l7.997-3.998A2 2 0 0016 4H4a2 2 0 00-1.997 1.884z" />
                <path d="M18 8.118l-8 4-8-4V14a2 2 0 002 2h12a2 2 0 002-2V8.118z" />
              </svg>
              <span class="text-gray-400">info@asiatransgas.uz</span>
            </li>
            <li class="flex items-center">
              <svg
                class="w-4 h-4 text-white mr-3 flex-shrink-0"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path d="M2 3a1 1 0 011-1h2.153a1 1 0 01.986.836l.74 4.435a1 1 0 01-.54 1.06l-1.548.773a11.037 11.037 0 006.105 6.105l.774-1.548a1 1 0 011.059-.54l4.435.74a1 1 0 01.836.986V17a1 1 0 01-1 1h-2C7.82 18 2 12.18 2 5V3z" />
              </svg>
              <span class="text-gray-400">+998 71 123 45 67</span>
            </li>
            <li class="flex items-center">
              <svg
                class="w-4 h-4 text-white mr-3 flex-shrink-0"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path
                  fill-rule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z"
                  clip-rule="evenodd"
                />
              </svg>
              <span class="text-gray-400">Пн-Пт: 9:00-18:00</span>
            </li>
          </ul>
        </div>

        <!-- Column 3: Company Information -->
        <div>
          <h3 class="text-lg font-bold text-white mb-4 relative">
            Информация о компании
            <div class="absolute bottom-0 left-0 w-12 h-0.5 bg-red-500" />
          </h3>
          <ul class="space-y-3">
            <li class="text-gray-400">
              СП ООО «Asia Trans Gas»
            </li>
            <li class="text-gray-400">
              Основана: 20 сентября 2024
            </li>
            <li class="text-gray-400">
              География: Узбекистан, СНГ
            </li>
            <li class="text-gray-400">
              Деятельность: Нефтегазовое оборудование
            </li>
          </ul>
        </div>
      </div>

      <!-- Bottom Section -->
      <div class="border-t border-gray-600 pt-6">
        <div class="flex flex-col sm:flex-row justify-between items-center text-gray-400 text-sm">
          <p>Asia Trans Gas © Все права защищены</p>
          <p class="mt-2 sm:mt-0">
            <a
              href="#"
              class="hover:text-white transition-colors"
            >Условия обработки персональных данных</a>
          </p>
        </div>
      </div>
    </div>
  </footer>
</template>

<script>
import { useI18n } from 'vue-i18n'

export default {
  name: 'Footer',
  setup() {
    const { t } = useI18n()
    
    const handleLogoError = (event) => {
      // Fallback to text logo if image fails to load
      event.target.style.display = 'none'
      const parent = event.target.parentElement
      const fallback = document.createElement('div')
      fallback.className = 'w-10 h-10 bg-gradient-to-br from-blue-600 to-blue-800 rounded-lg flex items-center justify-center'
      fallback.innerHTML = '<span class="text-white font-bold text-sm">ATG</span>'
      parent.insertBefore(fallback, event.target)
    }
    
    return {
      handleLogoError
    }
  }
}
</script>
