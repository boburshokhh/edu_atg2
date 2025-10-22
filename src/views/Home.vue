<template>
  <AppLayout>
    <!-- Hero Section -->
    <HeroSection @scroll-to-features="scrollToFeatures" />

    <!-- About Section -->
    <AboutSection />

    <!-- Features Section -->
    <FeaturesSection ref="featuresSection" />

    <!-- CTA Section -->
    <CTASection />
  </AppLayout>
</template>

<script>
import { ref } from 'vue'
import AppLayout from '@/components/AppLayout.vue'
import HeroSection from '@/components/sections/HeroSection.vue'
import AboutSection from '@/components/sections/AboutSection.vue'
import FeaturesSection from '@/components/sections/FeaturesSection.vue'
import CTASection from '@/components/sections/CTASection.vue'

export default {
  name: 'Home',
  components: {
    AppLayout,
    HeroSection,
    AboutSection,
    FeaturesSection,
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
