<template>
  <footer class="bg-gray-900 text-white">
    <div class="page-container section-padding">
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 lg:gap-8">
        <div class="col-span-1 sm:col-span-2 lg:col-span-2">
          <div class="flex items-center space-x-3 mb-4">
            <img 
              src="/logo.e75fb66.svg" 
              alt="Asia Trans Gas Logo" 
              class="w-8 h-8 sm:w-10 sm:h-10"
              @error="handleLogoError"
            />
            <div class="flex flex-col">
              <span class="text-base sm:text-lg font-bold">{{ $t('nav.companyName') }}</span>
              <span class="text-xs text-gray-400 -mt-1">{{ $t('nav.corporateTraining') }}</span>
            </div>
          </div>
          <p class="text-gray-400 mb-4 text-sm sm:text-base">
            {{ $t('footer.description') }}
          </p>
          <div class="text-xs sm:text-sm text-gray-400 space-y-1">
            <p>📍 {{ $t('footer.location') }}</p>
            <p>📧 {{ $t('footer.email') }}</p>
            <p>🌐 <a href="https://asiatransgas.uz" target="_blank" class="hover:text-white">{{ $t('footer.website') }}</a></p>
          </div>
        </div>
        
        <div>
          <h3 class="text-base sm:text-lg font-semibold mb-3 sm:mb-4">{{ $t('footer.training') }}</h3>
          <ul class="space-y-2 text-gray-400 text-sm">
            <li><a href="#" class="hover:text-white transition-colors">{{ $t('courses.categories.stations') }}</a></li>
            <li><a href="#" class="hover:text-white transition-colors">{{ $t('courses.categories.safety') }}</a></li>
            <li><a href="#" class="hover:text-white transition-colors">{{ $t('courses.categories.maintenance') }}</a></li>
            <li><a href="#" class="hover:text-white transition-colors">{{ $t('courses.categories.operation') }}</a></li>
          </ul>
        </div>
        
        <div>
          <h3 class="text-base sm:text-lg font-semibold mb-3 sm:mb-4">{{ $t('footer.support') }}</h3>
          <ul class="space-y-2 text-gray-400 text-sm">
            <li><a href="#" class="hover:text-white transition-colors">Техническая поддержка</a></li>
            <li><a href="#" class="hover:text-white transition-colors">Контакты</a></li>
            <li><a href="#" class="hover:text-white transition-colors">FAQ</a></li>
            <li><a href="#" class="hover:text-white transition-colors">Документация</a></li>
          </ul>
        </div>
      </div>
      
      <div class="border-t border-gray-800 mt-6 sm:mt-8 pt-6 sm:pt-8 text-center text-gray-400">
        <p class="text-sm">&copy; 2024 {{ $t('footer.copyright') }}</p>
        <p class="mt-2 text-xs sm:text-sm">{{ $t('footer.pipeline') }}</p>
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
