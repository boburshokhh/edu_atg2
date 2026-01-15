<template>
  <div class="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8 pt-20 lg:pt-24">
    <div class="max-w-6xl mx-auto space-y-6">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-semibold text-gray-900">
            Аналитика обучения
          </h1>
          <p class="text-sm text-gray-500">
            Курсы, пользователи и материалы в одном дашборде
          </p>
        </div>
        <el-button plain @click="$router.push('/admin')">
          <el-icon class="mr-1"><ArrowLeft /></el-icon>
          Назад
        </el-button>
      </div>

      <el-card>
        <el-tabs v-model="activeTab">
          <el-tab-pane label="Обзор" name="overview">
            <AdminAnalyticsOverview />
          </el-tab-pane>
          <el-tab-pane label="Курсы" name="courses">
            <AdminCourseAnalytics />
          </el-tab-pane>
          <el-tab-pane label="Станции" name="stations">
            <AdminStationAnalytics />
          </el-tab-pane>
          <el-tab-pane label="Пользователи" name="users">
            <AdminUserAnalytics />
          </el-tab-pane>
          <el-tab-pane label="Материалы" name="materials">
            <AdminMaterialAnalytics />
          </el-tab-pane>
        </el-tabs>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ArrowLeft } from '@element-plus/icons-vue'
import AdminAnalyticsOverview from './AdminAnalyticsOverview.vue'
import AdminCourseAnalytics from './AdminCourseAnalytics.vue'
import AdminUserAnalytics from './AdminUserAnalytics.vue'
import AdminStationAnalytics from './AdminStationAnalytics.vue'
import AdminMaterialAnalytics from './AdminMaterialAnalytics.vue'

const activeTab = ref('overview')
</script>
