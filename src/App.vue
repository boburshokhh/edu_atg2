<template>
  <div id="app" class="min-h-screen bg-gray-50">
    <router-view />
    <NotificationContainer />
  </div>
</template>

<script>
import NotificationContainer from '@/components/ui/NotificationContainer.vue'

export default {
  name: 'App',
  components: {
    NotificationContainer
  }
}
</script>
