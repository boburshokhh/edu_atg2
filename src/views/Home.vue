<template>
  <AppLayout>
    <!-- Hero Section -->
    <HeroSection @scroll-to-features="scrollToFeatures" />

    <!-- Features Section -->
    <FeaturesSection ref="featuresSection" />

    <!-- Popular Courses Section -->
    <PopularCoursesSection />

    <!-- Stats Section -->
    <StatsSection />

    <!-- CTA Section -->
    <CTASection />
  </AppLayout>
</template>

<script>
import { ref } from 'vue'
import AppLayout from '@/components/AppLayout.vue'
import HeroSection from '@/components/sections/HeroSection.vue'
import FeaturesSection from '@/components/sections/FeaturesSection.vue'
import PopularCoursesSection from '@/components/sections/PopularCoursesSection.vue'
import StatsSection from '@/components/sections/StatsSection.vue'
import CTASection from '@/components/sections/CTASection.vue'

export default {
  name: 'Home',
  components: {
    AppLayout,
    HeroSection,
    FeaturesSection,
    PopularCoursesSection,
    StatsSection,
    CTASection
  },
  setup() {
    const featuresSection = ref(null)
    
    const scrollToFeatures = () => {
      featuresSection.value?.scrollIntoView({ 
        behavior: 'smooth' 
      })
    }
    
    return {
      featuresSection,
      scrollToFeatures
    }
  }
}
</script>
