<template>
  <div 
    aria-live="assertive" 
    class="fixed inset-0 flex items-end px-4 py-6 pointer-events-none sm:p-6 sm:items-start z-[9999]"
  >
    <div class="w-full flex flex-col items-center space-y-4 sm:items-end">
      <TransitionGroup 
        enter-active-class="transform ease-out duration-300 transition" 
        enter-from-class="translate-y-2 opacity-0 sm:translate-y-0 sm:translate-x-2" 
        enter-to-class="translate-y-0 opacity-100 sm:translate-x-0" 
        leave-active-class="transition ease-in duration-100" 
        leave-from-class="opacity-100" 
        leave-to-class="opacity-0"
      >
        <NotificationToast 
          v-for="notification in notifications" 
          :key="notification.id" 
          :notification="notification"
          class="pointer-events-auto"
          @close="remove(notification.id)"
        />
      </TransitionGroup>
    </div>
  </div>
</template>

<script setup>
import useNotify from '@/composables/useNotify'
import NotificationToast from './NotificationToast.vue'

const { notifications, remove } = useNotify()
</script>


