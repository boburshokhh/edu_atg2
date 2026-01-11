<template>
  <div>
    <h2 class="text-3xl font-bold text-gray-900 mb-6">
      О программе
    </h2>
    
    <!-- Learning Outcomes -->
    <div class="mb-10">
      <h3 class="text-xl font-bold text-gray-900 mb-5 flex items-center">
        <div class="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center mr-3">
          <svg
            class="w-5 h-5 text-green-600"
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path
              fill-rule="evenodd"
              d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
              clip-rule="evenodd"
            />
          </svg>
        </div>
        Что вы изучите
      </h3>
      <div class="grid md:grid-cols-2 gap-4">
        <div
          v-for="(item, index) in courseProgram?.learningOutcomes"
          :key="index" 
          class="flex items-start p-4 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors"
        >
          <svg
            class="w-6 h-6 text-green-500 mr-3 flex-shrink-0 mt-0.5"
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path
              fill-rule="evenodd"
              d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
              clip-rule="evenodd"
            />
          </svg>
          <span class="text-gray-700">{{ item }}</span>
        </div>
      </div>
    </div>

    <!-- Requirements -->
    <div class="mb-10">
      <h3 class="text-xl font-bold text-gray-900 mb-5 flex items-center">
        <div class="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center mr-3">
          <svg
            class="w-5 h-5 text-blue-600"
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path
              fill-rule="evenodd"
              d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
              clip-rule="evenodd"
            />
          </svg>
        </div>
        Требования
      </h3>
      <ul class="space-y-3">
        <li
          v-for="(req, index) in courseProgram?.requirements"
          :key="index" 
          class="flex items-start p-4 bg-blue-50 rounded-xl"
        >
          <svg
            class="w-5 h-5 text-blue-600 mr-3 flex-shrink-0 mt-0.5"
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path
              fill-rule="evenodd"
              d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
              clip-rule="evenodd"
            />
          </svg>
          <span class="text-gray-700">{{ req }}</span>
        </li>
      </ul>
    </div>

    <!-- Target Audience -->
    <div>
      <h3 class="text-xl font-bold text-gray-900 mb-5 flex items-center">
        <div class="w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center mr-3">
          <svg
            class="w-5 h-5 text-purple-600"
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path
              fill-rule="evenodd"
              d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z"
              clip-rule="evenodd"
            />
          </svg>
        </div>
        Целевая аудитория
      </h3>
      <div class="grid md:grid-cols-2 gap-4">
        <div
          v-for="(audience, index) in courseProgram?.targetAudience"
          :key="index" 
          class="flex items-center space-x-3 p-4 bg-purple-50 rounded-xl hover:bg-purple-100 transition-colors"
        >
          <div class="w-10 h-10 bg-purple-200 rounded-full flex items-center justify-center flex-shrink-0">
            <svg
              class="w-5 h-5 text-purple-700"
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path
                fill-rule="evenodd"
                d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z"
                clip-rule="evenodd"
              />
            </svg>
          </div>
          <span class="font-medium text-gray-900">{{ audience }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CourseAboutTab',
  props: {
    courseProgram: {
      type: Object,
      default: null
    }
  }
}
</script>

