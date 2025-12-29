<template>
  <AppLayout>
    <!-- Hero Section с фото станции -->
    <div class="relative h-[80vh] min-h-[600px] overflow-hidden">
      <!-- Изображение станции -->
      <div class="absolute inset-0">
        <img 
          :src="stationImageUrl || ''" 
          :alt="station?.name"
          class="w-full h-full object-cover"
        >
        <!-- Градиентный оверлей -->
        <div class="absolute inset-0 bg-gradient-to-b from-black/70 via-black/50 to-gray-900/90" />
      </div>

      <!-- Контент хедера -->
      <div class="relative h-full page-container flex flex-col justify-between">
        <!-- Навигация в верхней части -->
        <div class="pt-20">
          <button 
            class="inline-flex items-center bg-white/20 backdrop-blur-sm text-white hover:bg-white/30 transition-all duration-300 group px-4 py-2 rounded-lg border border-white/30 hover:border-white/50"
            @click="$router.push('/stations')"
          >
            <svg
              class="w-5 h-5 mr-2 transition-transform group-hover:-translate-x-1"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M15 19l-7-7 7-7"
              />
            </svg>
            <span class="text-sm font-semibold">Назад к станциям</span>
          </button>
        </div>

        <!-- Основная информация в нижней части -->
        <div class="pb-12">
          <!-- Основная информация -->
          <div class="max-w-4xl">
            <h1 class="text-3xl md:text-5xl font-bold text-white mb-4 leading-tight">
              {{ station?.name }}
            </h1>
          
            <p class="text-lg md:text-xl text-gray-200 mb-6 max-w-3xl">
              {{ station?.description }}
            </p>

            <!-- Краткие характеристики -->
            <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div class="bg-white/10 backdrop-blur-sm rounded-lg p-4 border border-white/20">
                <div class="text-gray-300 text-xs font-medium mb-1">
                  Ввод в эксплуатацию
                </div>
                <div class="text-white text-lg font-bold">
                  {{ station?.commissionDate }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Основной контент -->
    <div class="bg-gray-50">
      <div class="page-container section-padding">
        <!-- Техническая информация по ГОСТ -->
        <div class="max-w-7xl mx-auto mb-12">
          <!-- Заголовок секции -->
          <div class="mb-8">
            <h2 class="text-3xl font-bold text-gray-900 mb-2">
              Техническая информация
            </h2>
            <div class="h-1 w-24 bg-gradient-to-r from-blue-600 to-blue-400 rounded-full" />
          </div>

          <!-- Документ ГОСТ стайл -->
          <div class="bg-white rounded-2xl shadow-xl border-2 border-gray-200 overflow-hidden">
            <!-- Шапка документа -->
            <div class="bg-gradient-to-r from-blue-600 to-blue-700 text-white px-8 py-6">
              <div class="flex items-center justify-between">
                <div>
                  <div class="text-sm opacity-90 mb-1">
                    СП ООО «ASIA TRANS GAS»
                  </div>
                  <h3 class="text-2xl font-bold">
                    Паспорт компрессорной станции
                  </h3>
                </div>
                <div class="text-right">
                  <div class="text-sm opacity-90">
                    Регистрационный номер
                  </div>
                  <div class="text-xl font-bold">
                    {{ station?.shortName }}-2024
                  </div>
                </div>
              </div>
            </div>

            <!-- Содержимое документа -->
            <div class="p-8 md:p-12">
              <!-- Общие сведения -->
              <section class="mb-10">
                <h4 class="text-xl font-bold text-gray-900 mb-6 pb-3 border-b-2 border-blue-600">
                  1. ОБЩИЕ СВЕДЕНИЯ
                </h4>
                
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div class="space-y-4">
                    <div class="flex border-b border-gray-200 pb-3">
                      <span class="font-semibold text-gray-700 min-w-[180px]">Наименование:</span>
                      <span class="text-gray-900">{{ station?.name }}</span>
                    </div>
                    <div class="flex border-b border-gray-200 pb-3">
                      <span class="font-semibold text-gray-700 min-w-[180px]">Краткое название:</span>
                      <span class="text-gray-900 font-bold">{{ station?.shortName }}</span>
                    </div>
                    <div class="flex border-b border-gray-200 pb-3">
                      <span class="font-semibold text-gray-700 min-w-[180px]">Местоположение:</span>
                      <span class="text-gray-900">{{ station?.location }}</span>
                    </div>
                    <div class="flex border-b border-gray-200 pb-3">
                      <span class="font-semibold text-gray-700 min-w-[180px]">Тип станции:</span>
                      <span class="text-gray-900">{{ station?.type }}</span>
                    </div>
                  </div>
                  
                  <div class="space-y-4">
                    <div class="flex border-b border-gray-200 pb-3">
                      <span class="font-semibold text-gray-700 min-w-[180px]">Дата ввода:</span>
                      <span class="text-gray-900">{{ station?.commissionDate }}</span>
                    </div>
                    <div class="flex border-b border-gray-200 pb-3">
                      <span class="font-semibold text-gray-700 min-w-[180px]">Проектная мощность:</span>
                      <span class="text-gray-900">{{ station?.designCapacity }}</span>
                    </div>
                    <div class="flex border-b border-gray-200 pb-3">
                      <span class="font-semibold text-gray-700 min-w-[180px]">Давление газа:</span>
                      <span class="text-gray-900">{{ station?.gasPressure }}</span>
                    </div>
                  </div>
                </div>

                <!-- Дополнительная информация для WKC1 -->
                <div
                  v-if="station?.gasSupplySources"
                  class="mt-8 grid grid-cols-1 md:grid-cols-2 gap-6"
                >
                  <!-- Источники поставки газа -->
                  <div class="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-6 border-2 border-blue-200">
                    <div class="flex items-center mb-4">
                      <svg
                        class="w-6 h-6 text-blue-600 mr-3"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          stroke-linecap="round"
                          stroke-linejoin="round"
                          stroke-width="2"
                          d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
                        />
                      </svg>
                      <h5 class="text-lg font-bold text-gray-900">
                        Источники поставки газа
                      </h5>
                    </div>
                    <ul class="space-y-3">
                      <li
                        v-for="(source, idx) in station.gasSupplySources"
                        :key="idx"
                        class="flex items-start"
                      >
                        <span class="inline-flex items-center justify-center w-6 h-6 bg-blue-600 text-white rounded-full text-xs font-bold mr-3 flex-shrink-0 mt-0.5">{{ idx + 1 }}</span>
                        <span class="text-sm text-gray-800">{{ source }}</span>
                      </li>
                    </ul>
                  </div>

                  <!-- Характеристики трубопровода -->
                  <div class="bg-gradient-to-br from-amber-50 to-amber-100 rounded-xl p-6 border-2 border-amber-200">
                    <div class="flex items-center mb-4">
                      <svg
                        class="w-6 h-6 text-amber-600 mr-3"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          stroke-linecap="round"
                          stroke-linejoin="round"
                          stroke-width="2"
                          d="M13 10V3L4 14h7v7l9-11h-7z"
                        />
                      </svg>
                      <h5 class="text-lg font-bold text-gray-900">
                        Характеристики магистрали
                      </h5>
                    </div>
                    <div class="space-y-3">
                      <div
                        v-if="station.pipelineDiameter"
                        class="flex items-start"
                      >
                        <svg
                          class="w-5 h-5 text-amber-600 mr-2 flex-shrink-0 mt-0.5"
                          fill="currentColor"
                          viewBox="0 0 20 20"
                        >
                          <path
                            fill-rule="evenodd"
                            d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                            clip-rule="evenodd"
                          />
                        </svg>
                        <div>
                          <div class="text-xs text-gray-600 font-medium">
                            Диаметр трубопровода
                          </div>
                          <div class="text-sm font-bold text-gray-900">
                            {{ station.pipelineDiameter }}
                          </div>
                        </div>
                      </div>
                      <div
                        v-if="station.distanceFromBorder"
                        class="flex items-start"
                      >
                        <svg
                          class="w-5 h-5 text-amber-600 mr-2 flex-shrink-0 mt-0.5"
                          fill="currentColor"
                          viewBox="0 0 20 20"
                        >
                          <path
                            fill-rule="evenodd"
                            d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z"
                            clip-rule="evenodd"
                          />
                        </svg>
                        <div>
                          <div class="text-xs text-gray-600 font-medium">
                            Расположение
                          </div>
                          <div class="text-sm font-bold text-gray-900">
                            {{ station.distanceFromBorder }}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </section>

              <!-- Основное оборудование -->
              <section
                v-if="station?.equipment && station.equipment.length > 0"
                class="mb-10"
              >
                <h4 class="text-xl font-bold text-gray-900 mb-6 pb-3 border-b-2 border-blue-600">
                  2. ОСНОВНОЕ ОБОРУДОВАНИЕ
                </h4>
                
                <!-- Десктопная таблица (скрыта на мобильных) -->
                <div class="hidden md:block overflow-x-auto">
                  <table class="w-full border-collapse bg-white rounded-lg shadow-lg">
                    <thead>
                      <tr class="bg-gradient-to-r from-blue-600 to-blue-700 text-white">
                        <th class="border border-blue-500 px-4 py-4 text-left text-sm font-bold">
                          №
                        </th>
                        <th class="border border-blue-500 px-4 py-4 text-left text-sm font-bold">
                          Наименование
                        </th>
                        <th class="border border-blue-500 px-4 py-4 text-left text-sm font-bold">
                          Тип/Модель
                        </th>
                        <th class="border border-blue-500 px-4 py-4 text-left text-sm font-bold">
                          Производитель
                        </th>
                        <th class="border border-blue-500 px-4 py-4 text-center text-sm font-bold">
                          Кол-во
                        </th>
                        <th class="border border-blue-500 px-4 py-4 text-center text-sm font-bold">
                          Мощность
                        </th>
                        <th class="border border-blue-500 px-4 py-4 text-left text-sm font-bold">
                          Описание
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr
                        v-for="(equipment, index) in station?.equipment"
                        :key="index" 
                        class="hover:bg-blue-50 transition-colors duration-200"
                      >
                        <td class="border border-gray-300 px-4 py-4 text-sm font-bold text-blue-600 text-center">
                          {{ index + 1 }}
                        </td>
                        <td class="border border-gray-300 px-4 py-4 text-sm font-semibold text-gray-900">
                          {{ equipment.name }}
                        </td>
                        <td class="border border-gray-300 px-4 py-4 text-sm text-gray-700">
                          {{ equipment.model }}
                        </td>
                        <td class="border border-gray-300 px-4 py-4 text-sm text-gray-700">
                          {{ equipment.manufacturer }}
                        </td>
                        <td class="border border-gray-300 px-4 py-4 text-sm text-center font-bold text-blue-600">
                          {{ equipment.quantity }} шт.
                        </td>
                        <td class="border border-gray-300 px-4 py-4 text-sm text-center font-bold text-amber-600">
                          {{ equipment.power || '-' }}
                        </td>
                        <td class="border border-gray-300 px-4 py-4 text-sm text-gray-600 italic">
                          {{ equipment.description || '-' }}
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>

                <!-- Мобильные карточки (показаны только на мобильных) -->
                <div class="md:hidden space-y-4">
                  <div
                    v-for="(equipment, index) in station?.equipment"
                    :key="index"
                    class="bg-white rounded-lg shadow-lg border border-gray-200 p-4 hover:shadow-xl transition-shadow duration-300"
                  >
                    <!-- Заголовок карточки -->
                    <div class="flex items-center justify-between mb-3 pb-3 border-b border-gray-200">
                      <div class="flex items-center">
                        <div class="w-8 h-8 bg-blue-600 text-white rounded-lg flex items-center justify-center font-bold text-sm mr-3">
                          {{ index + 1 }}
                        </div>
                        <h5 class="font-bold text-gray-900 text-base">
                          {{ equipment.name }}
                        </h5>
                      </div>
                    </div>
                    
                    <!-- Содержимое карточки -->
                    <div class="space-y-3">
                      <div class="flex items-center">
                        <svg
                          class="w-4 h-4 text-blue-600 mr-3 flex-shrink-0"
                          fill="currentColor"
                          viewBox="0 0 20 20"
                        >
                          <path
                            fill-rule="evenodd"
                            d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z"
                            clip-rule="evenodd"
                          />
                        </svg>
                        <span class="text-gray-600 text-sm">Модель:</span>
                        <span class="ml-2 font-semibold text-gray-900 text-sm">{{ equipment.model }}</span>
                      </div>
                      
                      <div class="flex items-center">
                        <svg
                          class="w-4 h-4 text-blue-600 mr-3 flex-shrink-0"
                          fill="currentColor"
                          viewBox="0 0 20 20"
                        >
                          <path d="M9 6a3 3 0 11-6 0 3 3 0 016 0zM17 6a3 3 0 11-6 0 3 3 0 016 0zM12.93 17c.046-.327.07-.66.07-1a6.97 6.97 0 00-1.5-4.33A5 5 0 0119 16v1h-6.07zM6 11a5 5 0 015 5v1H1v-1a5 5 0 015-5z" />
                        </svg>
                        <span class="text-gray-600 text-sm">Производитель:</span>
                        <span class="ml-2 font-semibold text-gray-900 text-sm">{{ equipment.manufacturer }}</span>
                      </div>
                      
                      <div class="flex items-center">
                        <svg
                          class="w-4 h-4 text-blue-600 mr-3 flex-shrink-0"
                          fill="currentColor"
                          viewBox="0 0 20 20"
                        >
                          <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
                          <path
                            fill-rule="evenodd"
                            d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z"
                            clip-rule="evenodd"
                          />
                        </svg>
                        <span class="text-gray-600 text-sm">Количество:</span>
                        <span class="ml-2 font-bold text-blue-600 text-sm">{{ equipment.quantity }} шт.</span>
                      </div>
                      
                      <div
                        v-if="equipment.power"
                        class="flex items-center"
                      >
                        <svg
                          class="w-4 h-4 text-amber-600 mr-3 flex-shrink-0"
                          fill="currentColor"
                          viewBox="0 0 20 20"
                        >
                          <path
                            fill-rule="evenodd"
                            d="M11.3 1.046A1 1 0 0112 2v5h4a1 1 0 01.82 1.573l-7 10A1 1 0 018 18v-5H4a1 1 0 01-.82-1.573l7-10a1 1 0 011.12-.38z"
                            clip-rule="evenodd"
                          />
                        </svg>
                        <span class="text-gray-600 text-sm">Мощность:</span>
                        <span class="ml-2 font-bold text-amber-600 text-sm">{{ equipment.power }}</span>
                      </div>
                      
                      <div
                        v-if="equipment.description"
                        class="mt-3 pt-3 border-t border-gray-100"
                      >
                        <div class="flex items-start">
                          <svg
                            class="w-4 h-4 text-blue-600 mr-2 flex-shrink-0 mt-0.5"
                            fill="currentColor"
                            viewBox="0 0 20 20"
                          >
                            <path
                              fill-rule="evenodd"
                              d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
                              clip-rule="evenodd"
                            />
                          </svg>
                          <div>
                            <span class="text-gray-600 text-xs font-medium">Описание:</span>
                            <p class="text-gray-700 text-sm italic mt-1">
                              {{ equipment.description }}
                            </p>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </section>

              <!-- Технические характеристики -->
              <section
                v-if="station?.specifications && station.specifications.length > 0"
                class="mb-10"
              >
                <h4 class="text-xl font-bold text-gray-900 mb-6 pb-3 border-b-2 border-blue-600">
                  3. ТЕХНИЧЕСКИЕ ХАРАКТЕРИСТИКИ
                </h4>
                 
                <!-- Десктопная таблица (скрыта на мобильных) -->
                <div class="hidden md:block overflow-x-auto">
                  <table class="w-full border-collapse bg-white rounded-lg shadow-lg">
                    <thead>
                      <tr class="bg-gradient-to-r from-blue-600 to-blue-700 text-white">
                        <th class="border border-blue-500 px-4 py-4 text-left text-sm font-bold">
                          Параметр
                        </th>
                        <th class="border border-blue-500 px-4 py-4 text-center text-sm font-bold">
                          Значение
                        </th>
                        <th class="border border-blue-500 px-4 py-4 text-center text-sm font-bold">
                          Единица
                        </th>
                        <th class="border border-blue-500 px-4 py-4 text-left text-sm font-bold">
                          Описание
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr
                        v-for="(spec, index) in station?.specifications"
                        :key="index" 
                        class="hover:bg-blue-50 transition-colors duration-200"
                      >
                        <td class="border border-gray-300 px-4 py-4 text-sm font-semibold text-gray-900">
                          {{ spec.category }}
                        </td>
                        <td class="border border-gray-300 px-4 py-4 text-sm font-bold text-blue-600 text-center">
                          {{ spec.value }}
                        </td>
                        <td class="border border-gray-300 px-4 py-4 text-sm text-gray-700 text-center">
                          {{ spec.unit }}
                        </td>
                        <td class="border border-gray-300 px-4 py-4 text-sm text-gray-600">
                          {{ spec.description }}
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>

                <!-- Мобильные карточки (показаны только на мобильных) -->
                <div class="md:hidden space-y-4">
                  <div
                    v-for="(spec, index) in station?.specifications"
                    :key="index"
                    class="bg-white rounded-lg shadow-lg border border-gray-200 p-4 hover:shadow-xl transition-shadow duration-300"
                  >
                    <!-- Заголовок карточки -->
                    <div class="flex items-center justify-between mb-3 pb-3 border-b border-gray-200">
                      <div class="flex items-center">
                        <div class="w-8 h-8 bg-blue-600 text-white rounded-lg flex items-center justify-center font-bold text-sm mr-3">
                          {{ index + 1 }}
                        </div>
                        <h5 class="font-bold text-gray-900 text-base">
                          {{ spec.category }}
                        </h5>
                      </div>
                    </div>
                     
                    <!-- Содержимое карточки -->
                    <div class="space-y-3">
                      <div class="flex items-center justify-between">
                        <span class="text-gray-600 text-sm">Значение:</span>
                        <span class="font-bold text-blue-600 text-lg">{{ spec.value }}</span>
                      </div>
                       
                      <div class="flex items-center justify-between">
                        <span class="text-gray-600 text-sm">Единица:</span>
                        <span class="font-semibold text-gray-900 text-sm">{{ spec.unit }}</span>
                      </div>
                       
                      <div class="mt-3 pt-3 border-t border-gray-100">
                        <div class="flex items-start">
                          <svg
                            class="w-4 h-4 text-blue-600 mr-2 flex-shrink-0 mt-0.5"
                            fill="currentColor"
                            viewBox="0 0 20 20"
                          >
                            <path
                              fill-rule="evenodd"
                              d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
                              clip-rule="evenodd"
                            />
                          </svg>
                          <div>
                            <span class="text-gray-600 text-xs font-medium">Описание:</span>
                            <p class="text-gray-700 text-sm mt-1">
                              {{ spec.description }}
                            </p>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </section>

              <!-- Технологические процессы -->
              <section
                v-if="station?.id === 1"
                class="mb-10"
              >
                <h4 class="text-xl font-bold text-gray-900 mb-6 pb-3 border-b-2 border-blue-600">
                  4. ТЕХНОЛОГИЧЕСКИЕ ПРОЦЕССЫ
                </h4>
                
                <div class="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-6 mb-6">
                  <h5 class="text-lg font-semibold text-gray-900 mb-4">
                    Основные технологические операции:
                  </h5>
                  <div class="grid md:grid-cols-2 gap-6">
                    <div class="space-y-3">
                      <div class="flex items-start">
                        <div class="w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-xs font-bold mr-3 mt-0.5">
                          1
                        </div>
                        <div>
                          <span class="font-semibold text-gray-900">Прием газа</span>
                          <p class="text-gray-600 text-sm">
                            От ТКС и ТАС по трубопроводу Ø1067 мм
                          </p>
                        </div>
                      </div>
                      <div class="flex items-start">
                        <div class="w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-xs font-bold mr-3 mt-0.5">
                          2
                        </div>
                        <div>
                          <span class="font-semibold text-gray-900">Анализ параметров</span>
                          <p class="text-gray-600 text-sm">
                            Физико-химические характеристики газа
                          </p>
                        </div>
                      </div>
                      <div class="flex items-start">
                        <div class="w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-xs font-bold mr-3 mt-0.5">
                          3
                        </div>
                        <div>
                          <span class="font-semibold text-gray-900">Очистка газа</span>
                          <p class="text-gray-600 text-sm">
                            8 линий очистки (5 для нитки А, 3 для нитки В)
                          </p>
                        </div>
                      </div>
                    </div>
                    <div class="space-y-3">
                      <div class="flex items-start">
                        <div class="w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-xs font-bold mr-3 mt-0.5">
                          4
                        </div>
                        <div>
                          <span class="font-semibold text-gray-900">Измерение объема</span>
                          <p class="text-gray-600 text-sm">
                            9 линий узла замера газа (DANIEL 3400)
                          </p>
                        </div>
                      </div>
                      <div class="flex items-start">
                        <div class="w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-xs font-bold mr-3 mt-0.5">
                          5
                        </div>
                        <div>
                          <span class="font-semibold text-gray-900">Компримирование</span>
                          <p class="text-gray-600 text-sm">
                            5 ГПА (2 Solar + 3 GE)
                          </p>
                        </div>
                      </div>
                      <div class="flex items-start">
                        <div class="w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-xs font-bold mr-3 mt-0.5">
                          6
                        </div>
                        <div>
                          <span class="font-semibold text-gray-900">Охлаждение и транспортировка</span>
                          <p class="text-gray-600 text-sm">
                            22 линии АВО-газа, выход по двум ниткам
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Дополнительная информация -->
                <div class="grid md:grid-cols-2 gap-6">
                  <div class="bg-white rounded-lg shadow-lg p-6 border border-gray-200">
                    <h6 class="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                      <svg
                        class="w-5 h-5 text-blue-600 mr-2"
                        fill="currentColor"
                        viewBox="0 0 20 20"
                      >
                        <path
                          fill-rule="evenodd"
                          d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z"
                          clip-rule="evenodd"
                        />
                      </svg>
                      Параметры давления
                    </h6>
                    <div class="space-y-2">
                      <div class="flex justify-between">
                        <span class="text-gray-600">Входное давление:</span>
                        <span class="font-semibold text-blue-600">7.0 МПа</span>
                      </div>
                      <div class="flex justify-between">
                        <span class="text-gray-600">Выходное давление:</span>
                        <span class="font-semibold text-blue-600">9.81 МПа</span>
                      </div>
                      <div class="flex justify-between">
                        <span class="text-gray-600">Диаметр трубопровода:</span>
                        <span class="font-semibold text-blue-600">1067 мм</span>
                      </div>
                    </div>
                  </div>

                  <div class="bg-white rounded-lg shadow-lg p-6 border border-gray-200">
                    <h6 class="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                      <svg
                        class="w-5 h-5 text-green-600 mr-2"
                        fill="currentColor"
                        viewBox="0 0 20 20"
                      >
                        <path
                          fill-rule="evenodd"
                          d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                          clip-rule="evenodd"
                        />
                      </svg>
                      Энергоснабжение
                    </h6>
                    <div class="space-y-2">
                      <div class="flex justify-between">
                        <span class="text-gray-600">Газогенераторы:</span>
                        <span class="font-semibold text-green-600">3 × 1451 кВт</span>
                      </div>
                      <div class="flex justify-between">
                        <span class="text-gray-600">Дизель-генератор:</span>
                        <span class="font-semibold text-green-600">260 кВт</span>
                      </div>
                      <div class="flex justify-between">
                        <span class="text-gray-600">Компрессоры воздуха:</span>
                        <span class="font-semibold text-green-600">2 × 1242 м³/ч</span>
                      </div>
                    </div>
                  </div>
                </div>
              </section>

              <!-- Системы безопасности -->
              <section
                v-if="station?.safetySystems && station.safetySystems.length > 0"
                class="mb-10"
              >
                <h4 class="text-xl font-bold text-gray-900 mb-6 pb-3 border-b-2 border-blue-600">
                  5. СИСТЕМЫ БЕЗОПАСНОСТИ И КОНТРОЛЯ
                </h4>
                
                <div class="space-y-3">
                  <div
                    v-for="(system, index) in station?.safetySystems"
                    :key="index"
                    class="bg-gradient-to-r from-green-50 to-emerald-50 rounded-xl p-5 border-l-4 border-green-600 hover:shadow-md transition-all duration-300"
                  >
                    <div class="flex items-start">
                      <div class="flex-shrink-0">
                        <div class="w-10 h-10 bg-green-600 rounded-lg flex items-center justify-center">
                          <svg
                            class="w-6 h-6 text-white"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                          >
                            <path
                              stroke-linecap="round"
                              stroke-linejoin="round"
                              stroke-width="2"
                              d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
                            />
                          </svg>
                        </div>
                      </div>
                      <div class="ml-4 flex-grow">
                        <div class="flex items-center justify-between mb-2">
                          <h5 class="font-bold text-gray-900 text-base">
                            {{ system.name }}
                          </h5>
                          <span
                            v-if="system.manufacturer"
                            class="text-xs bg-green-600 text-white px-3 py-1 rounded-full font-semibold"
                          >
                            {{ system.manufacturer }}
                          </span>
                        </div>
                        <p class="text-sm text-gray-700 mb-3 leading-relaxed">
                          {{ system.description }}
                        </p>
                        <div
                          v-if="system.features && system.features.length > 0"
                          class="flex flex-wrap gap-2"
                        >
                          <span
                            v-for="(feature, fIdx) in system.features"
                            :key="fIdx" 
                            class="inline-flex items-center text-xs bg-white text-green-700 px-3 py-1.5 rounded-lg border border-green-200 font-medium"
                          >
                            <svg
                              class="w-3 h-3 mr-1.5 text-green-600"
                              fill="currentColor"
                              viewBox="0 0 20 20"
                            >
                              <path
                                fill-rule="evenodd"
                                d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                                clip-rule="evenodd"
                              />
                            </svg>
                            {{ feature }}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </section>


              <!-- Подпись документа -->
              <div class="mt-12 pt-8 border-t-2 border-gray-300">
                <div class="flex justify-between items-end">
                  <div>
                    <div class="text-sm text-gray-600 mb-2">
                      Документ действителен
                    </div>
                    <div class="text-xs text-gray-500">
                      Последнее обновление: {{ new Date().toLocaleDateString('ru-RU') }}
                    </div>
                  </div>
                  <div class="text-right">
                    <div class="inline-block px-6 py-3 bg-blue-600 text-white rounded-lg">
                      <div class="text-xs opacity-90">
                        Утверждено
                      </div>
                      <div class="font-bold">
                        СП ООО «ATG»
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Технологическая карта -->
        <div
          v-if="techMapImageUrl"
          class="max-w-7xl mx-auto mb-12"
        >
          <div class="mb-8">
            <h2 class="text-3xl font-bold text-gray-900 mb-2">
              Технологическая карта
            </h2>
            <div class="h-1 w-24 bg-gradient-to-r from-blue-600 to-blue-400 rounded-full" />
            <p class="text-gray-600 mt-4">
              Схема технологического процесса компрессорной станции {{ station?.shortName }}
            </p>
          </div>

          <!-- Карточка с технологической схемой -->
          <div class="bg-white rounded-2xl shadow-xl overflow-hidden border-2 border-gray-200">
            <div class="bg-gradient-to-r from-gray-800 to-gray-700 text-white px-6 py-4">
              <div class="flex items-center justify-between">
                <h3 class="text-lg font-bold">
                  Process Flow Diagram - {{ station?.shortName }}
                </h3>
                <button 
                  class="px-4 py-2 bg-white/10 hover:bg-white/20 rounded-lg transition-colors text-sm font-medium"
                  @click="openImageModal"
                >
                  <svg
                    class="w-5 h-5 inline mr-2"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v3m0 0v3m0-3h3m-3 0H7"
                    />
                  </svg>
                  Увеличить
                </button>
              </div>
            </div>
            
            <div class="p-6 bg-gray-50">
              <div
                class="relative group cursor-pointer"
                @click="openImageModal"
              >
                <img 
                  :src="techMapImageUrl" 
                  :alt="`Технологическая карта ${station?.shortName}`"
                  loading="lazy"
                  decoding="async"
                  class="w-full h-auto rounded-lg shadow-lg border-4 border-white transition-transform duration-300 group-hover:scale-[1.02]"
                >
                <div class="absolute inset-0 bg-black/0 group-hover:bg-black/10 transition-all duration-300 rounded-lg flex items-center justify-center">
                  <div class="opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                    <div class="bg-white rounded-full p-4 shadow-2xl">
                      <svg
                        class="w-8 h-8 text-blue-600"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          stroke-linecap="round"
                          stroke-linejoin="round"
                          stroke-width="2"
                          d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v3m0 0v3m0-3h3m-3 0H7"
                        />
                      </svg>
                    </div>
                  </div>
                </div>
              </div>
              
              <div class="mt-6 bg-yellow-50 border-l-4 border-yellow-400 p-4 rounded">
                <div class="flex">
                  <svg
                    class="w-5 h-5 text-yellow-600 mr-3 flex-shrink-0"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path
                      fill-rule="evenodd"
                      d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
                      clip-rule="evenodd"
                    />
                  </svg>
                  <div>
                    <p class="text-sm text-yellow-800 font-medium">
                      Внимание!
                    </p>
                    <p class="text-sm text-yellow-700 mt-1">
                      Технологическая схема содержит конфиденциальную информацию. Использование только для учебных целей.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Доступные тренинги -->
        <div class="max-w-7xl mx-auto">
          <div class="mb-8">
            <h2 class="text-3xl font-bold text-gray-900 mb-2">
              Доступные тренинги
            </h2>
            <div class="h-1 w-24 bg-gradient-to-r from-blue-600 to-blue-400 rounded-full" />
          </div>

          <div class="bg-gradient-to-br from-blue-600 to-blue-700 rounded-2xl p-8 md:p-12 text-white shadow-2xl">
            <div class="flex flex-col md:flex-row items-center justify-between">
              <div class="mb-6 md:mb-0 md:mr-8">
                <h3 class="text-2xl md:text-3xl font-bold mb-3">
                  {{ station?.coursesCount }} обучающих программ
                </h3>
                <p class="text-blue-100 text-lg">
                  Профессиональная подготовка персонала по эксплуатации и обслуживанию {{ station?.shortName }}
                </p>
                <ul class="mt-4 space-y-2">
                  <li class="flex items-center text-blue-100">
                    <svg
                      class="w-5 h-5 mr-2"
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <path
                        fill-rule="evenodd"
                        d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                        clip-rule="evenodd"
                      />
                    </svg>
                    Сертифицированные программы
                  </li>
                  <li class="flex items-center text-blue-100">
                    <svg
                      class="w-5 h-5 mr-2"
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <path
                        fill-rule="evenodd"
                        d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                        clip-rule="evenodd"
                      />
                    </svg>
                    Практические занятия
                  </li>
                  <li class="flex items-center text-blue-100">
                    <svg
                      class="w-5 h-5 mr-2"
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <path
                        fill-rule="evenodd"
                        d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                        clip-rule="evenodd"
                      />
                    </svg>
                    Опытные инструкторы
                  </li>
                </ul>
              </div>
              <div class="flex-shrink-0">
                <button 
                  class="px-8 py-4 bg-white text-blue-600 font-bold text-lg rounded-xl shadow-xl hover:shadow-2xl transition-all duration-300 transform hover:scale-105 hover:-translate-y-1"
                  @click="$router.push(`/station/${station?.id}/courses`)"
                >
                  Посмотреть тренинги
                  <svg
                    class="w-5 h-5 inline ml-2"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M13 7l5 5m0 0l-5 5m5-5H6"
                    />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal для просмотра изображений -->
    <vue-easy-lightbox
      :visible="lightboxVisible"
      :imgs="lightboxImages"
      :index="lightboxIndex"
      @hide="lightboxVisible = false"
    />
  </AppLayout>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import AppLayout from '@/components/layout/AppLayout.vue'
import VueEasyLightbox from 'vue-easy-lightbox'
import stationService from '@/services/stationService'
import minioService from '@/services/minioService'
import { resolveStationMedia } from '@/utils/stationsMedia'

export default {
  name: 'StationDetail',
  components: {
    AppLayout,
    VueEasyLightbox
  },
  setup() {
    const route = useRoute()
    const stationId = computed(() => parseInt(route.params.id))
    
    const lightboxVisible = ref(false)
    const lightboxIndex = ref(0)

    const station = ref(null)
    const stationImageUrl = ref('')
    const techMapImageUrl = ref('')
    const loading = ref(false)
    const error = ref('')

    const lightboxImages = computed(() => {
      return techMapImageUrl.value ? [techMapImageUrl.value] : []
    })

    const openImageModal = () => {
      lightboxIndex.value = 0
      lightboxVisible.value = true
    }

    const openGallery = (index) => {
      lightboxIndex.value = 0
      lightboxVisible.value = true
    }

    const mapStationToView = (data) => {
      const s = data?.station || data || {}
      return {
        id: s.id,
        name: s.name || '',
        shortName: s.short_name || s.shortName || '',
        description: s.description || '',
        image: s.image || '',
        techMapImage: s.tech_map_image || s.techMapImage || '',
        power: s.power || '',
        commissionDate: s.commission_date || s.commissionDate || '',
        coursesCount: s.courses_count ?? s.coursesCount ?? 0,
        status: s.status || 'active',
        location: s.location || '',
        type: s.type || '',
        designCapacity: s.design_capacity || s.designCapacity || '',
        gasPressure: s.gas_pressure || s.gasPressure || '',
        distanceFromBorder: s.distance_from_border || s.distanceFromBorder || '',
        pipelineDiameter: s.pipeline_diameter || s.pipelineDiameter || '',
        inputPressure: s.input_pressure || s.inputPressure || '',
        outputPressure: s.output_pressure || s.outputPressure || '',
        parallelLines: s.parallel_lines || s.parallelLines || '',
        gasSupplySources: (data?.gas_sources || []).map(x => x.source_name || x.sourceName).filter(Boolean),
        equipment: (data?.equipment || []).map(eq => ({
          name: eq.name,
          model: eq.model,
          manufacturer: eq.manufacturer,
          quantity: eq.quantity,
          power: eq.power,
          description: eq.description,
        })),
        specifications: (data?.specs || data?.specifications || []).map(sp => ({
          category: sp.category,
          value: sp.value,
          unit: sp.unit,
          description: sp.description,
        })),
        safetySystems: (data?.safety || []).map(ss => ({
          name: ss.name,
          manufacturer: ss.manufacturer,
          description: ss.description,
          features: ss.features || [],
        })),
      }
    }

    const loadMediaUrls = async (stationView, photos = []) => {
      // Find photos by view type from StationPhoto
      const stationImagePhoto = photos.find(p => p.view === 'station_image')
      const techMapPhoto = photos.find(p => p.view === 'tech_map_image')

      // Station image - use StationPhoto if available, fallback to Station.image
      stationImageUrl.value = ''
      const stationImagePath = stationImagePhoto?.image_url || stationView?.image || ''
      
      if (stationImagePath) {
        const img = resolveStationMedia(stationImagePath, { defaultFolder: 'stations' })
        if (img.kind === 'url' || img.kind === 'public') {
          stationImageUrl.value = img.url
        } else if (img.kind === 'minio') {
          // Show a fast, non-signed URL immediately (dev proxy will rewrite it),
          // then upgrade to a presigned URL when ready.
          stationImageUrl.value = minioService.getFileUrl(img.objectKey)
          try {
            stationImageUrl.value = await minioService.getPresignedDownloadUrl(
              img.objectKey,
              7 * 24 * 60 * 60,
              img.contentType
            )
          } catch (e) {
            stationImageUrl.value = img.fallbackPublicPath || minioService.getFileUrl(img.objectKey)
          }
        }
      }

      // Tech map image - use StationPhoto if available, fallback to Station.tech_map_image
      techMapImageUrl.value = ''
      const techMapPath = techMapPhoto?.image_url || stationView?.techMapImage || ''
      
      if (techMapPath) {
        const tech = resolveStationMedia(techMapPath, { defaultFolder: 'tex_kart' })
        if (tech.kind === 'url' || tech.kind === 'public') {
          techMapImageUrl.value = tech.url
        } else if (tech.kind === 'minio') {
          techMapImageUrl.value = minioService.getFileUrl(tech.objectKey)
          try {
            techMapImageUrl.value = await minioService.getPresignedDownloadUrl(
              tech.objectKey,
              7 * 24 * 60 * 60,
              tech.contentType
            )
          } catch (e) {
            techMapImageUrl.value = tech.fallbackPublicPath || minioService.getFileUrl(tech.objectKey)
          }
        }
      }
    }

    const loadStation = async () => {
      loading.value = true
      error.value = ''
      try {
        const data = await stationService.getStation(stationId.value)
        const view = mapStationToView(data)
        station.value = view
        
        // Get photos from StationPhoto
        const photos = data.photos || []
        
        // Load media URLs using photos from StationPhoto with fallback to old fields
        await loadMediaUrls(view, photos)
      } catch (e) {
        error.value = e?.message || 'Не удалось загрузить станцию'
        station.value = null
        stationImageUrl.value = ''
        techMapImageUrl.value = ''
      } finally {
        loading.value = false
      }
    }

    watch(stationId, () => {
      loadStation()
    })

    onMounted(() => {
      loadStation()
    })

    return {
      station,
      stationImageUrl,
      techMapImageUrl,
      loading,
      error,
      lightboxVisible,
      lightboxIndex,
      lightboxImages,
      openImageModal,
      openGallery
    }
  }
}
</script>

<style scoped>
.section-padding {
  padding: 4rem 1rem;
}

@media (min-width: 640px) {
  .section-padding {
    padding: 5rem 1.5rem;
  }
}

@media (min-width: 1024px) {
  .section-padding {
    padding: 6rem 2rem;
  }
}
</style>

