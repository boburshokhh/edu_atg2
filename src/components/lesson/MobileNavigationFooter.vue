<template>
  <footer
    class="mobile-navigation-footer"
    :class="{ 'footer-visible': isVisible }"
  >
    <div class="footer-content">
      <!-- Previous Button -->
      <el-button
        :disabled="!hasPrevious"
        :icon="ArrowLeft"
        size="default"
        class="nav-btn nav-btn-prev"
        aria-label="Предыдущий урок"
        @click="handlePrevious"
      >
        <span class="nav-btn-text">Назад</span>
      </el-button>

      <!-- Center: Complete Status or Button -->
      <div class="nav-center">
        <el-button
          v-if="!isCompleted"
          type="success"
          :icon="Check"
          size="default"
          class="nav-btn nav-btn-complete"
          aria-label="Завершить урок"
          @click="handleComplete"
        >
          <span class="nav-btn-text">Завершить</span>
        </el-button>
        <el-tag
          v-else
          type="success"
          size="default"
          class="completed-tag"
          role="status"
          aria-label="Урок завершен"
        >
          <el-icon><Check /></el-icon>
          <span class="completed-text">Завершено</span>
        </el-tag>
      </div>

      <!-- Next Button -->
      <el-button
        :disabled="!hasNext"
        type="primary"
        size="default"
        class="nav-btn nav-btn-next"
        aria-label="Следующий урок"
        @click="handleNext"
      >
        <span class="nav-btn-text">Далее</span>
        <el-icon class="nav-icon">
          <ArrowRight />
        </el-icon>
      </el-button>
    </div>
  </footer>
</template>

<script setup>
import { ArrowLeft, ArrowRight, Check } from '@element-plus/icons-vue'

const props = defineProps({
  hasPrevious: {
    type: Boolean,
    default: false
  },
  hasNext: {
    type: Boolean,
    default: false
  },
  isCompleted: {
    type: Boolean,
    default: false
  },
  isVisible: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['previous', 'next', 'complete'])

const handlePrevious = () => {
  if (props.hasPrevious) {
    emit('previous')
  }
}

const handleNext = () => {
  if (props.hasNext) {
    emit('next')
  }
}

const handleComplete = () => {
  if (!props.isCompleted) {
    emit('complete')
  }
}
</script>

<style scoped>
.mobile-navigation-footer {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 100;
  background: #ffffff;
  border-top: 1px solid #e5e7eb;
  box-shadow: 0 -4px 6px -1px rgba(0, 0, 0, 0.1), 0 -2px 4px -1px rgba(0, 0, 0, 0.06);
  padding-bottom: env(safe-area-inset-bottom);
  transform: translateY(100%);
  transition: transform 0.3s ease-out;
}

.mobile-navigation-footer.footer-visible {
  transform: translateY(0);
}

.footer-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  gap: 0.75rem;
  max-width: 100%;
}

.nav-btn {
  flex: 1;
  min-width: 0;
  font-size: 0.875rem;
  height: 2.75rem;
}

.nav-btn-prev {
  max-width: 30%;
}

.nav-btn-next {
  max-width: 30%;
}

.nav-btn-complete {
  max-width: 40%;
}

.nav-btn-text {
  display: inline;
  font-weight: 500;
}

.nav-center {
  display: flex;
  align-items: center;
  justify-content: center;
  flex: 1;
  min-width: 0;
}

.completed-tag {
  font-size: 0.875rem;
  padding: 0.5rem 0.75rem;
  display: flex;
  align-items: center;
  gap: 0.375rem;
}

.completed-text {
  font-weight: 500;
}

.nav-icon {
  margin-left: 0.375rem;
}

/* Ensure buttons are accessible on mobile */
@media (max-width: 768px) {
  .mobile-navigation-footer {
    padding-bottom: max(0.75rem, env(safe-area-inset-bottom));
  }

  .footer-content {
    padding: 0.875rem 1rem;
  }

  .nav-btn {
    height: 3rem;
    font-size: 0.875rem;
  }
}

/* Hide on desktop */
@media (min-width: 1024px) {
  .mobile-navigation-footer {
    display: none;
  }
}
</style>

