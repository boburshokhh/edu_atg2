<template>
  <div
    id="app"
    class="min-h-screen bg-gray-50"
  >
    <AppLayout>
      <router-view />
    </AppLayout>
    <NotificationContainer />
  </div>
</template>

<script>
import AppLayout from '@/components/layout/AppLayout.vue'
import NotificationContainer from '@/components/ui/NotificationContainer.vue'

export default {
  name: 'App',
  components: {
    AppLayout,
    NotificationContainer
  }
}
</script>
