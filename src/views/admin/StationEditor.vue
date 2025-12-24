<template>
  <div class="container mx-auto px-4 py-8">
    <div class="flex items-center mb-6">
      <el-button
        class="mr-4"
        @click="$router.push('/admin/stations')"
      >
        <el-icon><ArrowLeft /></el-icon>
      </el-button>
      <h1 class="text-2xl font-bold text-gray-800">
        {{ isEditing ? `Редактирование станции: ${station.name || 'Загрузка...'}` : 'Новая станция' }}
      </h1>
    </div>

    <el-tabs
      v-model="activeTab"
      v-loading="loading"
      class="bg-white p-6 rounded-lg shadow"
    >
      <!-- General Info -->
      <el-tab-pane
        label="Общая информация"
        name="general"
      >
        <el-form
          :model="station"
          label-width="200px"
          class="max-w-4xl"
        >
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item
                label="Название"
                required
              >
                <el-input v-model="station.name" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item
                label="Короткое название"
                required
              >
                <el-input v-model="station.short_name" />
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-form-item label="Описание">
            <el-input
              v-model="station.description"
              type="textarea"
              rows="4"
            />
          </el-form-item>
          
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="Тип">
                <el-input v-model="station.type" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="Статус">
                <el-select
                  v-model="station.status"
                  style="width: 100%"
                >
                  <el-option
                    label="Активен"
                    value="active"
                  />
                  <el-option
                    label="На обслуживании"
                    value="maintenance"
                  />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-form-item label="Местоположение">
            <el-input
              v-model="station.location"
              type="textarea"
              rows="2"
            />
          </el-form-item>
          
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="Мощность">
                <el-input
                  v-model="station.power"
                  placeholder="например: 30 МВт"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="Дата ввода в эксплуатацию">
                <el-input
                  v-model="station.commission_date"
                  placeholder="например: 2009"
                />
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="Проектная мощность">
                <el-input
                  v-model="station.design_capacity"
                  placeholder="например: 30 млрд м³/год"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="Количество курсов">
                <el-input-number
                  v-model="station.courses_count"
                  :min="0"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-form-item label="Давление газа">
            <el-input
              v-model="station.gas_pressure"
              placeholder="например: 7.0 МПа (вход) / 9.81 МПа (выход)"
            />
          </el-form-item>
          
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="Давление входное">
                <el-input
                  v-model="station.input_pressure"
                  placeholder="например: 7.0 МПа"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="Давление выходное">
                <el-input
                  v-model="station.output_pressure"
                  placeholder="например: 9.81 МПа"
                />
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="Диаметр трубопровода">
                <el-input
                  v-model="station.pipeline_diameter"
                  placeholder="например: 1067 мм"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="Параллельные линии">
                <el-input
                  v-model="station.parallel_lines"
                  placeholder="например: Две нитки (А, В)"
                />
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-form-item label="Расстояние от границы">
            <el-input
              v-model="station.distance_from_border"
              placeholder="например: 10.6 км от границы с Туркменистаном"
            />
          </el-form-item>
          
          <el-form-item label="Основное изображение">
            <el-input
              v-model="station.image"
              placeholder="Путь к изображению или Minio key"
            />
            <div class="mt-2">
              <input
                ref="mainImageInput"
                type="file"
                class="hidden"
                accept="image/*"
                @change="handleMainImageUpload"
              >
              <el-button
                size="small"
                @click="$refs.mainImageInput.click()"
              >
                Загрузить изображение
              </el-button>
            </div>
          </el-form-item>
          
          <el-form-item label="Техническая карта">
            <el-input
              v-model="station.tech_map_image"
              placeholder="Путь к технической карте или Minio key"
            />
            <div class="mt-2">
              <input
                ref="techMapInput"
                type="file"
                class="hidden"
                accept="image/*"
                @change="handleTechMapUpload"
              >
              <el-button
                size="small"
                @click="$refs.techMapInput.click()"
              >
                Загрузить техническую карту
              </el-button>
            </div>
          </el-form-item>
          
          <el-form-item>
            <el-button
              type="primary"
              :loading="saving"
              @click="saveGeneral"
            >
              Сохранить
            </el-button>
          </el-form-item>
        </el-form>
      </el-tab-pane>

      <!-- Course Program -->
      <el-tab-pane
        label="Программа обучения"
        name="program"
        :disabled="!isEditing"
      >
        <div class="max-w-5xl">
          <div class="flex items-center justify-between mb-4">
            <div class="text-xs text-gray-500">
              <span v-if="courseProgram.id">Program ID: {{ courseProgram.id }}</span>
              <span v-else>Программа еще не создана</span>
            </div>
            <el-button
              type="primary"
              :loading="savingCourseProgram"
              @click="saveCourseProgram"
            >
              Сохранить программу
            </el-button>
          </div>

          <el-form
            :model="courseProgram"
            label-width="200px"
          >
            <el-form-item
              label="Название"
              required
            >
              <el-input v-model="courseProgram.title" />
            </el-form-item>
            <el-form-item label="Описание">
              <el-input
                v-model="courseProgram.description"
                type="textarea"
                rows="4"
              />
            </el-form-item>
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="Длительность">
                  <el-input
                    v-model="courseProgram.duration"
                    placeholder="например: 10 академических часов"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="Формат">
                  <el-input
                    v-model="courseProgram.format"
                    placeholder="Онлайн"
                  />
                </el-form-item>
              </el-col>
            </el-row>
            <el-form-item label="Активна">
              <el-switch v-model="courseProgram.isActive" />
            </el-form-item>
          </el-form>

          <el-divider />

          <!-- Promo video -->
          <div class="mb-6">
            <div class="flex items-center justify-between mb-2">
              <h3 class="text-lg font-bold text-gray-800">
                Короткое видео о станции
              </h3>
              <div class="flex gap-2">
                <input
                  ref="promoVideoInput"
                  type="file"
                  class="hidden"
                  accept="video/*"
                  @change="handlePromoVideoUpload"
                >
                <el-button
                  type="primary"
                  size="small"
                  :loading="uploadingPromoVideo"
                  @click="$refs.promoVideoInput.click()"
                >
                  <el-icon class="mr-2">
                    <Upload />
                  </el-icon> Загрузить видео
                </el-button>
                <el-popconfirm
                  title="Удалить видео?"
                  @confirm="deletePromoVideo({ deleteObject: false })"
                >
                  <template #reference>
                    <el-button
                      size="small"
                      type="danger"
                      :disabled="!promoVideo"
                    >
                      Удалить
                    </el-button>
                  </template>
                </el-popconfirm>
              </div>
            </div>

            <div
              v-if="promoVideoUrl"
              class="bg-gray-50 border border-gray-200 rounded-xl p-3"
            >
              <div class="text-sm text-gray-600 mb-2">
                <span class="font-semibold">Файл:</span> {{ promoVideo?.title || promoVideo?.objectKey }}
              </div>
              <video
                class="w-full rounded-lg bg-black"
                style="max-height: 260px;"
                :src="promoVideoUrl"
                controls
                playsinline
                preload="metadata"
                crossorigin="anonymous"
              />
              <div class="text-xs text-gray-500 mt-2">
                Видео проигрывается через presigned URL (Range requests), поэтому работает и на телефонах.
              </div>
            </div>
            <div
              v-else
              class="text-sm text-gray-500"
            >
              Видео не загружено.
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <!-- Learning outcomes -->
            <div>
              <h3 class="font-bold text-gray-800 mb-2">
                Что вы изучите
              </h3>
              <div
                v-for="(item, idx) in courseProgram.learningOutcomes"
                :key="`lo-${idx}`"
                class="flex gap-2 mb-2"
              >
                <el-input v-model="courseProgram.learningOutcomes[idx]" />
                <el-button
                  type="danger"
                  link
                  @click="courseProgram.learningOutcomes.splice(idx, 1)"
                >
                  Удалить
                </el-button>
              </div>
              <el-button
                size="small"
                @click="courseProgram.learningOutcomes.push('')"
              >
                + Добавить
              </el-button>
            </div>

            <!-- Requirements -->
            <div>
              <h3 class="font-bold text-gray-800 mb-2">
                Требования
              </h3>
              <div
                v-for="(item, idx) in courseProgram.requirements"
                :key="`req-${idx}`"
                class="flex gap-2 mb-2"
              >
                <el-input v-model="courseProgram.requirements[idx]" />
                <el-button
                  type="danger"
                  link
                  @click="courseProgram.requirements.splice(idx, 1)"
                >
                  Удалить
                </el-button>
              </div>
              <el-button
                size="small"
                @click="courseProgram.requirements.push('')"
              >
                + Добавить
              </el-button>
            </div>

            <!-- Target audience -->
            <div>
              <h3 class="font-bold text-gray-800 mb-2">
                Целевая аудитория
              </h3>
              <div
                v-for="(item, idx) in courseProgram.targetAudience"
                :key="`aud-${idx}`"
                class="flex gap-2 mb-2"
              >
                <el-input v-model="courseProgram.targetAudience[idx]" />
                <el-button
                  type="danger"
                  link
                  @click="courseProgram.targetAudience.splice(idx, 1)"
                >
                  Удалить
                </el-button>
              </div>
              <el-button
                size="small"
                @click="courseProgram.targetAudience.push('')"
              >
                + Добавить
              </el-button>
            </div>
          </div>

          <el-divider />

          <div class="flex items-center justify-between mb-3">
            <h3 class="text-lg font-bold text-gray-800">
              Уроки и темы
            </h3>
            <el-button
              type="primary"
              size="small"
              @click="addLesson"
            >
              <el-icon class="mr-2">
                <Plus />
              </el-icon> Добавить урок
            </el-button>
          </div>

          <el-collapse accordion>
            <el-collapse-item
              v-for="(lesson, lessonIdx) in courseProgram.lessons"
              :key="lesson.lessonKey || lesson.id || lessonIdx"
              :name="lesson.lessonKey || lessonIdx"
            >
              <template #title>
                <div class="flex items-center gap-3">
                  <span class="font-semibold">{{ lessonIdx + 1 }}.</span>
                  <span class="font-semibold">{{ lesson.title || 'Новый урок' }}</span>
                  <span
                    v-if="lesson.lessonKey"
                    class="text-xs text-gray-500"
                  >key: {{ lesson.lessonKey }}</span>
                </div>
              </template>

              <div class="p-2">
                <el-form label-width="160px">
                  <el-form-item label="Название урока">
                    <el-input v-model="lesson.title" />
                  </el-form-item>
                  <el-row :gutter="20">
                    <el-col :span="12">
                      <el-form-item label="Длительность">
                        <el-input
                          v-model="lesson.duration"
                          placeholder="например: 2.5 часа"
                        />
                      </el-form-item>
                    </el-col>
                    <el-col :span="12">
                      <el-form-item label="Порядок">
                        <el-input-number
                          v-model="lesson.orderIndex"
                          :min="0"
                          style="width: 100%"
                        />
                      </el-form-item>
                    </el-col>
                  </el-row>
                </el-form>

                <div class="flex items-center justify-between mb-2">
                  <h4 class="font-semibold text-gray-700">
                    Темы
                  </h4>
                  <div class="flex gap-2">
                    <el-button
                      size="small"
                      @click="addTopic(lesson)"
                    >
                      <el-icon class="mr-1">
                        <Plus />
                      </el-icon> Добавить тему
                    </el-button>
                    <el-popconfirm
                      title="Удалить урок?"
                      @confirm="removeLesson(lessonIdx)"
                    >
                      <template #reference>
                        <el-button
                          size="small"
                          type="danger"
                        >
                          Удалить урок
                        </el-button>
                      </template>
                    </el-popconfirm>
                  </div>
                </div>

                <el-table
                  :data="lesson.topics || []"
                  stripe
                  border
                >
                  <el-table-column
                    label="Key"
                    min-width="220"
                  >
                    <template #default="{ row }">
                      <span class="text-xs text-gray-500">{{ row.topicKey }}</span>
                    </template>
                  </el-table-column>
                  <el-table-column
                    label="Код"
                    width="140"
                  >
                    <template #default="{ row }">
                      <el-input v-model="row.code" />
                    </template>
                  </el-table-column>
                  <el-table-column
                    label="Название"
                    min-width="240"
                  >
                    <template #default="{ row }">
                      <el-input v-model="row.title" />
                    </template>
                  </el-table-column>
                  <el-table-column
                    label="Длительность"
                    width="140"
                  >
                    <template #default="{ row }">
                      <el-input v-model="row.duration" />
                    </template>
                  </el-table-column>
                  <el-table-column
                    label="Порядок"
                    width="120"
                  >
                    <template #default="{ row }">
                      <el-input-number
                        v-model="row.orderIndex"
                        :min="0"
                        style="width: 100%"
                      />
                    </template>
                  </el-table-column>
                  <el-table-column
                    label="Файлы"
                    width="140"
                  >
                    <template #default="{ row }">
                      <el-button
                        size="small"
                        @click="openTopicFiles(row)"
                      >
                        Файлы ({{ (row.files || []).length }})
                      </el-button>
                    </template>
                  </el-table-column>
                  <el-table-column
                    label="Действия"
                    width="120"
                    fixed="right"
                  >
                    <template #default="{ $index }">
                      <el-button
                        type="danger"
                        link
                        @click="lesson.topics.splice($index, 1)"
                      >
                        Удалить
                      </el-button>
                    </template>
                  </el-table-column>
                </el-table>
              </div>
            </el-collapse-item>
          </el-collapse>
        </div>
      </el-tab-pane>

      <!-- Equipment -->
      <el-tab-pane
        label="Оборудование"
        name="equipment"
        :disabled="!isEditing"
      >
        <div class="mb-4">
          <el-button
            type="primary"
            @click="showEquipmentDialog = true"
          >
            <el-icon class="mr-2">
              <Plus />
            </el-icon> Добавить оборудование
          </el-button>
        </div>
        
        <el-table
          :data="equipment"
          stripe
          border
        >
          <el-table-column
            prop="name"
            label="Название"
            min-width="200"
          />
          <el-table-column
            prop="model"
            label="Модель"
            width="150"
          />
          <el-table-column
            prop="manufacturer"
            label="Производитель"
            width="180"
          />
          <el-table-column
            prop="quantity"
            label="Количество"
            width="100"
            align="center"
          />
          <el-table-column
            prop="power"
            label="Мощность"
            width="150"
          />
          <el-table-column
            prop="description"
            label="Описание"
            min-width="200"
            show-overflow-tooltip
          />
          <el-table-column
            label="Действия"
            width="150"
            fixed="right"
          >
            <template #default="{ row }">
              <el-button
                size="small"
                @click="editEquipment(row)"
              >
                Редактировать
              </el-button>
              <el-popconfirm
                title="Удалить оборудование?"
                @confirm="deleteEquipment(row)"
              >
                <template #reference>
                  <el-button
                    size="small"
                    type="danger"
                  >
                    Удалить
                  </el-button>
                </template>
              </el-popconfirm>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <!-- Specifications -->
      <el-tab-pane
        label="Технические характеристики"
        name="specs"
        :disabled="!isEditing"
      >
        <div class="mb-4">
          <el-button
            type="primary"
            @click="showSpecDialog = true"
          >
            <el-icon class="mr-2">
              <Plus />
            </el-icon> Добавить характеристику
          </el-button>
        </div>
        
        <el-table
          :data="specs"
          stripe
          border
        >
          <el-table-column
            prop="category"
            label="Категория"
            min-width="200"
          />
          <el-table-column
            prop="value"
            label="Значение"
            width="120"
          />
          <el-table-column
            prop="unit"
            label="Единица"
            width="100"
          />
          <el-table-column
            prop="description"
            label="Описание"
            min-width="250"
            show-overflow-tooltip
          />
          <el-table-column
            label="Действия"
            width="150"
            fixed="right"
          >
            <template #default="{ row }">
              <el-button
                size="small"
                @click="editSpec(row)"
              >
                Редактировать
              </el-button>
              <el-popconfirm
                title="Удалить характеристику?"
                @confirm="deleteSpec(row)"
              >
                <template #reference>
                  <el-button
                    size="small"
                    type="danger"
                  >
                    Удалить
                  </el-button>
                </template>
              </el-popconfirm>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <!-- Safety Systems -->
      <el-tab-pane
        label="Системы безопасности"
        name="safety"
        :disabled="!isEditing"
      >
        <div class="mb-4">
          <el-button
            type="primary"
            @click="showSafetyDialog = true"
          >
            <el-icon class="mr-2">
              <Plus />
            </el-icon> Добавить систему безопасности
          </el-button>
        </div>
        
        <el-table
          :data="safetySystems"
          stripe
          border
        >
          <el-table-column
            prop="name"
            label="Название"
            min-width="200"
          />
          <el-table-column
            prop="description"
            label="Описание"
            min-width="250"
            show-overflow-tooltip
          />
          <el-table-column
            prop="manufacturer"
            label="Производитель"
            width="150"
          />
          <el-table-column
            label="Особенности"
            min-width="200"
          >
            <template #default="{ row }">
              <el-tag
                v-for="(feature, idx) in (row.feature_names || row.features || [])"
                :key="idx"
                class="mr-1 mb-1"
                size="small"
              >
                {{ typeof feature === 'string' ? feature : feature.feature_name }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column
            label="Действия"
            width="150"
            fixed="right"
          >
            <template #default="{ row }">
              <el-button
                size="small"
                @click="editSafetySystem(row)"
              >
                Редактировать
              </el-button>
              <el-popconfirm
                title="Удалить систему?"
                @confirm="deleteSafetySystem(row)"
              >
                <template #reference>
                  <el-button
                    size="small"
                    type="danger"
                  >
                    Удалить
                  </el-button>
                </template>
              </el-popconfirm>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <!-- Gas Supply Sources -->
      <el-tab-pane
        label="Источники подачи газа"
        name="gasSources"
        :disabled="!isEditing"
      >
        <div class="mb-4">
          <el-button
            type="primary"
            @click="showGasSourceDialog = true"
          >
            <el-icon class="mr-2">
              <Plus />
            </el-icon> Добавить источник
          </el-button>
        </div>
        
        <el-table
          :data="gasSources"
          stripe
          border
        >
          <el-table-column
            prop="source_name"
            label="Название источника"
            min-width="300"
          />
          <el-table-column
            label="Действия"
            width="150"
            fixed="right"
          >
            <template #default="{ row }">
              <el-button
                size="small"
                @click="editGasSource(row)"
              >
                Редактировать
              </el-button>
              <el-popconfirm
                title="Удалить источник?"
                @confirm="deleteGasSource(row)"
              >
                <template #reference>
                  <el-button
                    size="small"
                    type="danger"
                  >
                    Удалить
                  </el-button>
                </template>
              </el-popconfirm>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <!-- Photos -->
      <el-tab-pane
        label="Фотографии"
        name="photos"
        :disabled="!isEditing"
      >
        <div class="mb-4">
          <input
            ref="photoInput"
            type="file"
            class="hidden"
            accept="image/*"
            @change="handlePhotoUpload"
          >
          <el-button
            type="primary"
            :loading="uploadingPhoto"
            @click="$refs.photoInput.click()"
          >
            <el-icon class="mr-2">
              <Upload />
            </el-icon> Загрузить фото
          </el-button>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <el-card
            v-for="photo in photos"
            :key="photo.id"
            :body-style="{ padding: '0px' }"
          >
            <img
              :src="photo.displayUrl || photo.image_url"
              class="w-full h-48 object-cover"
            >
            <div class="p-4">
              <div class="mb-2">
                <el-input
                  v-model="photo.title"
                  placeholder="Название"
                  size="small"
                  @change="updatePhoto(photo)"
                />
              </div>
              <div class="mb-2">
                <el-select
                  v-model="photo.view"
                  placeholder="Вид"
                  size="small"
                  style="width: 100%"
                  @change="updatePhoto(photo)"
                >
                  <el-option
                    label="Общий вид"
                    value="general"
                  />
                  <el-option
                    label="Машинный зал"
                    value="machine-hall"
                  />
                  <el-option
                    label="Компрессоры"
                    value="compressors"
                  />
                  <el-option
                    label="Охлаждение"
                    value="cooling"
                  />
                  <el-option
                    label="Другое"
                    value="other"
                  />
                </el-select>
              </div>
              <div class="flex justify-between items-center mt-2">
                <el-button
                  type="danger"
                  link
                  size="small"
                  @click="deletePhoto(photo)"
                >
                  Удалить
                </el-button>
              </div>
            </div>
          </el-card>
        </div>
      </el-tab-pane>

      <!-- Normative Docs -->
      <el-tab-pane
        label="Документы"
        name="docs"
        :disabled="!isEditing"
      >
        <div class="mb-4">
          <input
            ref="docInput"
            type="file"
            class="hidden"
            @change="handleDocUpload"
          >
          <el-button
            type="primary"
            :loading="uploadingDoc"
            @click="$refs.docInput.click()"
          >
            <el-icon class="mr-2">
              <DocumentAdd />
            </el-icon> Загрузить документ
          </el-button>
        </div>
        <el-table
          :data="docs"
          stripe
          border
        >
          <el-table-column
            prop="title"
            label="Название"
            min-width="200"
          />
          <el-table-column label="Файл">
            <template #default="{ row }">
              <a
                :href="row.downloadUrl || row.file_url"
                target="_blank"
                class="text-blue-600 hover:underline"
              >Скачать</a>
            </template>
          </el-table-column>
          <el-table-column
            label="Действия"
            width="120"
          >
            <template #default="{ row }">
              <el-popconfirm
                title="Удалить документ?"
                @confirm="deleteDoc(row)"
              >
                <template #reference>
                  <el-button
                    type="danger"
                    size="small"
                  >
                    Удалить
                  </el-button>
                </template>
              </el-popconfirm>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>

    <!-- Equipment Dialog -->
    <el-dialog
      v-model="showEquipmentDialog"
      :title="editingEquipment ? 'Редактировать оборудование' : 'Добавить оборудование'"
      width="600px"
    >
      <el-form
        :model="equipmentForm"
        label-width="150px"
      >
        <el-form-item
          label="Название"
          required
        >
          <el-input v-model="equipmentForm.name" />
        </el-form-item>
        <el-form-item label="Модель">
          <el-input v-model="equipmentForm.model" />
        </el-form-item>
        <el-form-item label="Производитель">
          <el-input v-model="equipmentForm.manufacturer" />
        </el-form-item>
        <el-form-item label="Количество">
          <el-input-number
            v-model="equipmentForm.quantity"
            :min="1"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="Мощность">
          <el-input v-model="equipmentForm.power" />
        </el-form-item>
        <el-form-item label="Описание">
          <el-input
            v-model="equipmentForm.description"
            type="textarea"
            rows="3"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEquipmentDialog = false">
          Отмена
        </el-button>
        <el-button
          type="primary"
          @click="saveEquipment"
        >
          Сохранить
        </el-button>
      </template>
    </el-dialog>

    <!-- Specification Dialog -->
    <el-dialog
      v-model="showSpecDialog"
      :title="editingSpec ? 'Редактировать характеристику' : 'Добавить характеристику'"
      width="600px"
    >
      <el-form
        :model="specForm"
        label-width="150px"
      >
        <el-form-item
          label="Категория"
          required
        >
          <el-input v-model="specForm.category" />
        </el-form-item>
        <el-form-item label="Значение">
          <el-input v-model="specForm.value" />
        </el-form-item>
        <el-form-item label="Единица измерения">
          <el-input v-model="specForm.unit" />
        </el-form-item>
        <el-form-item label="Описание">
          <el-input
            v-model="specForm.description"
            type="textarea"
            rows="3"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showSpecDialog = false">
          Отмена
        </el-button>
        <el-button
          type="primary"
          @click="saveSpec"
        >
          Сохранить
        </el-button>
      </template>
    </el-dialog>

    <!-- Safety System Dialog -->
    <el-dialog
      v-model="showSafetyDialog"
      :title="editingSafetySystem ? 'Редактировать систему безопасности' : 'Добавить систему безопасности'"
      width="700px"
    >
      <el-form
        :model="safetyForm"
        label-width="150px"
      >
        <el-form-item
          label="Название"
          required
        >
          <el-input v-model="safetyForm.name" />
        </el-form-item>
        <el-form-item label="Описание">
          <el-input
            v-model="safetyForm.description"
            type="textarea"
            rows="3"
          />
        </el-form-item>
        <el-form-item label="Производитель">
          <el-input v-model="safetyForm.manufacturer" />
        </el-form-item>
        <el-form-item label="Особенности">
          <div
            v-for="(feature, idx) in safetyForm.features"
            :key="idx"
            class="mb-2 flex items-center"
          >
            <el-input
              v-model="safetyForm.features[idx]"
              class="flex-1 mr-2"
            />
            <el-button
              type="danger"
              link
              @click="safetyForm.features.splice(idx, 1)"
            >
              Удалить
            </el-button>
          </div>
          <el-button
            size="small"
            @click="safetyForm.features.push('')"
          >
            + Добавить особенность
          </el-button>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showSafetyDialog = false">
          Отмена
        </el-button>
        <el-button
          type="primary"
          @click="saveSafetySystem"
        >
          Сохранить
        </el-button>
      </template>
    </el-dialog>

    <!-- Gas Source Dialog -->
    <el-dialog
      v-model="showGasSourceDialog"
      :title="editingGasSource ? 'Редактировать источник' : 'Добавить источник'"
      width="500px"
    >
      <el-form
        :model="gasSourceForm"
        label-width="150px"
      >
        <el-form-item
          label="Название источника"
          required
        >
          <el-input v-model="gasSourceForm.source_name" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showGasSourceDialog = false">
          Отмена
        </el-button>
        <el-button
          type="primary"
          @click="saveGasSource"
        >
          Сохранить
        </el-button>
      </template>
    </el-dialog>

    <!-- Topic Files Dialog -->
    <el-dialog
      v-model="showTopicFilesDialog"
      title="Файлы темы"
      width="900px"
    >
      <div v-if="activeTopic">
        <div class="mb-3 text-sm text-gray-600">
          <div><span class="font-semibold">Тема:</span> {{ activeTopic.code }} — {{ activeTopic.title }}</div>
          <div class="text-xs text-gray-500">
            topic_id: {{ activeTopic.id }} | topicKey: {{ activeTopic.topicKey }}
          </div>
        </div>

        <div class="flex items-center justify-between mb-3">
          <div class="flex items-center gap-3">
            <el-select
              v-model="newTopicFileType"
              placeholder="Тип"
              style="width: 180px"
            >
              <el-option
                label="PDF"
                value="pdf"
              />
              <el-option
                label="Видео"
                value="video"
              />
              <el-option
                label="Документ"
                value="document"
              />
            </el-select>
            <el-checkbox
              v-model="newTopicFileIsMain"
              :disabled="newTopicFileType !== 'pdf'"
            >
              Главный PDF
            </el-checkbox>
          </div>
          <div class="flex gap-2">
            <input
              ref="topicFileInput"
              type="file"
              class="hidden"
              @change="handleTopicFileUpload"
            >
            <el-button
              type="primary"
              :loading="uploadingTopicFile"
              @click="$refs.topicFileInput.click()"
            >
              <el-icon class="mr-2">
                <Upload />
              </el-icon> Загрузить файл
            </el-button>
          </div>
        </div>

        <el-table
          :data="topicFiles"
          stripe
          border
        >
          <el-table-column
            prop="fileType"
            label="Тип"
            width="110"
          />
          <el-table-column
            prop="isMain"
            label="Main"
            width="90"
          >
            <template #default="{ row }">
              <el-switch
                v-model="row.isMain"
                :disabled="row.fileType !== 'pdf'"
                @change="() => updateTopicFile(row, { isMain: row.isMain })"
              />
            </template>
          </el-table-column>
          <el-table-column
            label="Название"
            min-width="240"
          >
            <template #default="{ row }">
              <el-input
                v-model="row.title"
                @change="() => updateTopicFile(row, { title: row.title })"
              />
            </template>
          </el-table-column>
          <el-table-column
            label="Order"
            width="120"
          >
            <template #default="{ row }">
              <el-input-number
                v-model="row.orderIndex"
                :min="0"
                style="width: 100%"
                @change="() => updateTopicFile(row, { orderIndex: row.orderIndex })"
              />
            </template>
          </el-table-column>
          <el-table-column
            label="Preview"
            width="140"
          >
            <template #default="{ row }">
              <el-button
                size="small"
                @click="previewTopicFile(row)"
              >
                Открыть
              </el-button>
            </template>
          </el-table-column>
          <el-table-column
            label="Действия"
            width="140"
            fixed="right"
          >
            <template #default="{ row }">
              <el-popconfirm
                title="Удалить файл?"
                @confirm="deleteTopicFile(row)"
              >
                <template #reference>
                  <el-button
                    size="small"
                    type="danger"
                  >
                    Удалить
                  </el-button>
                </template>
              </el-popconfirm>
            </template>
          </el-table-column>
        </el-table>
      </div>
      <template #footer>
        <el-button @click="showTopicFilesDialog = false">
          Закрыть
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, Upload, DocumentAdd, Plus } from '@element-plus/icons-vue'
import stationService from '@/services/stationService'
import minioService from '@/services/minioService'

const route = useRoute()
const router = useRouter()
const activeTab = ref('general')
const loading = ref(false)
const saving = ref(false)
const uploadingPhoto = ref(false)
const uploadingDoc = ref(false)

const station = ref({
  name: '',
  short_name: '',
  status: 'active',
  courses_count: 0
})

const photos = ref([])
const docs = ref([])
const equipment = ref([])
const specs = ref([])
const safetySystems = ref([])
const gasSources = ref([])

const isEditing = computed(() => route.params.id !== 'new')

// ==================== Course Program (StationCourses) ====================
const savingCourseProgram = ref(false)
const courseProgram = ref({
  id: null,
  title: '',
  description: '',
  duration: '',
  format: 'Онлайн',
  isActive: true,
  orderIndex: 0,
  learningOutcomes: [],
  requirements: [],
  targetAudience: [],
  lessons: []
})

const genStableKey = (prefix) => {
  try {
    if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') {
      return `${prefix}_${crypto.randomUUID()}`
    }
  } catch {}
  return `${prefix}_${Date.now()}_${Math.random().toString(16).slice(2)}`
}

const normalizeCourseProgram = (p) => {
  const program = p || {}
  return {
    id: program.id || null,
    title: program.title || '',
    description: program.description || '',
    duration: program.duration || '',
    format: program.format || 'Онлайн',
    isActive: program.isActive !== undefined ? !!program.isActive : true,
    orderIndex: program.orderIndex || 0,
    learningOutcomes: Array.isArray(program.learningOutcomes) ? program.learningOutcomes : [],
    requirements: Array.isArray(program.requirements) ? program.requirements : [],
    targetAudience: Array.isArray(program.targetAudience) ? program.targetAudience : [],
    lessons: Array.isArray(program.lessons)
      ? program.lessons.map(l => ({
          id: l.id || null,
          lessonKey: l.lessonKey || l.lesson_key || genStableKey('lesson'),
          title: l.title || '',
          duration: l.duration || '',
          orderIndex: l.orderIndex ?? l.order_index ?? 0,
          topics: Array.isArray(l.topics)
            ? l.topics.map(t => ({
                id: t.id || null,
                topicKey: t.topicKey || t.topic_key || genStableKey('topic'),
                code: t.code || '',
                title: t.title || '',
                duration: t.duration || '',
                orderIndex: t.orderIndex ?? t.order_index ?? 0,
                files: Array.isArray(t.files) ? t.files : []
              }))
            : []
        }))
      : []
  }
}

const loadCourseProgram = async () => {
  if (!isEditing.value) return
  try {
    const p = await stationService.getStationCourseProgram(route.params.id)
    if (p) {
      courseProgram.value = normalizeCourseProgram(p)
    } else {
      courseProgram.value = normalizeCourseProgram({
        title: station.value?.name ? `Программа онлайн-тренинга \"${station.value.name}\"` : 'Программа онлайн-тренинга',
        format: 'Онлайн',
        isActive: true
      })
    }
  } catch (e) {
    console.error('[StationEditor] Failed to load course program:', e)
    courseProgram.value = normalizeCourseProgram(null)
  }
}

const addLesson = () => {
  courseProgram.value.lessons.push({
    id: null,
    lessonKey: genStableKey('lesson'),
    title: '',
    duration: '',
    orderIndex: courseProgram.value.lessons.length,
    topics: []
  })
}

const removeLesson = (lessonIdx) => {
  courseProgram.value.lessons.splice(lessonIdx, 1)
}

const addTopic = (lesson) => {
  if (!lesson.topics) lesson.topics = []
  lesson.topics.push({
    id: null,
    topicKey: genStableKey('topic'),
    code: '',
    title: '',
    duration: '',
    orderIndex: lesson.topics.length
  })
}

// ==================== Topic files (per topic materials) ====================
const showTopicFilesDialog = ref(false)
const activeTopic = ref(null)
const topicFiles = ref([])
const uploadingTopicFile = ref(false)

const newTopicFileType = ref('pdf') // pdf|video|document
const newTopicFileIsMain = ref(false)

const openTopicFiles = async (topic) => {
  activeTopic.value = topic
  showTopicFilesDialog.value = true
  topicFiles.value = []
  newTopicFileType.value = 'pdf'
  newTopicFileIsMain.value = false

  if (!topic?.id) {
    ElMessage.warning('Сначала сохраните программу (чтобы темы получили ID).')
    return
  }

  try {
    const rows = await stationService.getCourseProgramTopicFiles(route.params.id, topic.id)
    topicFiles.value = rows
  } catch (e) {
    ElMessage.error('Ошибка загрузки файлов темы: ' + (e?.message || e))
  }
}

const handleTopicFileUpload = async (event) => {
  const file = event.target.files?.[0]
  if (!file) return

  if (!activeTopic.value?.id) {
    ElMessage.warning('Тема не сохранена')
    event.target.value = ''
    return
  }

  uploadingTopicFile.value = true
  try {
    const folder = `stations/${station.value.id}/course_program/topics/${activeTopic.value.topicKey || activeTopic.value.id}`
    const objectKey = await stationService.uploadFile(file, folder)

    const fileType = newTopicFileType.value
    const isMain = fileType === 'pdf' ? !!newTopicFileIsMain.value : false

    const resp = await stationService.createCourseProgramTopicFile(route.params.id, activeTopic.value.id, {
      title: file.name,
      originalName: file.name,
      objectKey,
      fileType,
      isMain,
      orderIndex: topicFiles.value.length,
      fileSize: file.size,
      mimeType: file.type || null,
    })

    const created = resp?.data
    if (created) {
      // Refresh list to enforce main flag consistency
      topicFiles.value = await stationService.getCourseProgramTopicFiles(route.params.id, activeTopic.value.id)
      // Also keep topic object updated in-memory (for file counts)
      activeTopic.value.files = topicFiles.value.filter(f => f.isActive !== false)
    }
    ElMessage.success('Файл добавлен')
  } catch (e) {
    ElMessage.error('Ошибка загрузки файла: ' + (e?.message || e))
  } finally {
    uploadingTopicFile.value = false
    event.target.value = ''
  }
}

const updateTopicFile = async (row, patch) => {
  if (!activeTopic.value?.id) return
  try {
    await stationService.updateCourseProgramTopicFile(route.params.id, activeTopic.value.id, row.id, patch)
    // Reload list (main pdf uniqueness)
    topicFiles.value = await stationService.getCourseProgramTopicFiles(route.params.id, activeTopic.value.id)
    activeTopic.value.files = topicFiles.value.filter(f => f.isActive !== false)
  } catch (e) {
    ElMessage.error('Ошибка обновления: ' + (e?.message || e))
  }
}

const deleteTopicFile = async (row) => {
  if (!activeTopic.value?.id) return
  try {
    await stationService.deleteCourseProgramTopicFile(route.params.id, activeTopic.value.id, row.id, { deleteObject: false })
    topicFiles.value = await stationService.getCourseProgramTopicFiles(route.params.id, activeTopic.value.id)
    activeTopic.value.files = topicFiles.value.filter(f => f.isActive !== false)
    ElMessage.success('Удалено')
  } catch (e) {
    ElMessage.error('Ошибка удаления: ' + (e?.message || e))
  }
}

const previewTopicFile = async (row) => {
  try {
    const url = await minioService.getPresignedDownloadUrl(row.objectKey, 7 * 24 * 60 * 60, row.mimeType || null)
    window.open(url, '_blank')
  } catch (e) {
    ElMessage.error('Не удалось открыть файл: ' + (e?.message || e))
  }
}

const saveCourseProgram = async () => {
  if (!isEditing.value) return
  savingCourseProgram.value = true
  try {
    const payload = {
      id: courseProgram.value.id,
      title: courseProgram.value.title,
      description: courseProgram.value.description,
      duration: courseProgram.value.duration,
      format: courseProgram.value.format,
      isActive: courseProgram.value.isActive,
      orderIndex: courseProgram.value.orderIndex || 0,
      learningOutcomes: (courseProgram.value.learningOutcomes || []).filter(x => String(x || '').trim()),
      requirements: (courseProgram.value.requirements || []).filter(x => String(x || '').trim()),
      targetAudience: (courseProgram.value.targetAudience || []).filter(x => String(x || '').trim()),
      lessons: (courseProgram.value.lessons || []).map(l => ({
        lessonKey: l.lessonKey,
        title: l.title,
        duration: l.duration || null,
        orderIndex: l.orderIndex || 0,
        isActive: true,
        topics: (l.topics || []).map(t => ({
          topicKey: t.topicKey,
          code: t.code || null,
          title: t.title,
          duration: t.duration || null,
          orderIndex: t.orderIndex || 0,
          isActive: true
        }))
      }))
    }

    const resp = await stationService.updateStationCourseProgram(route.params.id, payload)
    courseProgram.value = normalizeCourseProgram(resp?.courseProgram)
    ElMessage.success('Программа обучения сохранена')
  } catch (e) {
    ElMessage.error('Ошибка сохранения программы: ' + (e?.message || e))
  } finally {
    savingCourseProgram.value = false
  }
}

// Equipment Dialog
const showEquipmentDialog = ref(false)
const editingEquipment = ref(null)
const equipmentForm = ref({
  name: '',
  model: '',
  manufacturer: '',
  quantity: 1,
  power: '',
  description: ''
})

// Spec Dialog
const showSpecDialog = ref(false)
const editingSpec = ref(null)
const specForm = ref({
  category: '',
  value: '',
  unit: '',
  description: ''
})

// Safety System Dialog
const showSafetyDialog = ref(false)
const editingSafetySystem = ref(null)
const safetyForm = ref({
  name: '',
  description: '',
  manufacturer: '',
  features: ['']
})

// Gas Source Dialog
const showGasSourceDialog = ref(false)
const editingGasSource = ref(null)
const gasSourceForm = ref({
  source_name: ''
})

// ==================== Promo video ====================
const promoVideo = ref(null) // { id, title, objectKey }
const promoVideoUrl = ref('')
const uploadingPromoVideo = ref(false)

const loadPromoVideo = async () => {
  if (!isEditing.value) return
  promoVideoUrl.value = ''
  try {
    promoVideo.value = await stationService.getStationPromoVideo(route.params.id)
    if (promoVideo.value?.objectKey) {
      // Presigned URL allows <video> playback (Range requests supported by browser/MinIO)
      promoVideoUrl.value = await minioService.getPresignedDownloadUrl(
        promoVideo.value.objectKey,
        7 * 24 * 60 * 60,
        'video/mp4'
      )
    }
  } catch (e) {
    console.error('[StationEditor] Failed to load promo video:', e)
    promoVideo.value = null
    promoVideoUrl.value = ''
  }
}

const handlePromoVideoUpload = async (event) => {
  const file = event.target.files?.[0]
  if (!file) return
  uploadingPromoVideo.value = true
  try {
    const key = await stationService.uploadFile(file, `stations/${station.value.id}/promo_video`)
    const payload = {
      title: file.name,
      objectKey: key
    }
    const resp = await stationService.updateStationPromoVideo(route.params.id, payload)
    promoVideo.value = resp?.video || null
    promoVideoUrl.value = await minioService.getPresignedDownloadUrl(key, 7 * 24 * 60 * 60, file.type || 'video/mp4')
    ElMessage.success('Видео загружено')
  } catch (e) {
    ElMessage.error('Ошибка загрузки видео: ' + (e?.message || e))
  } finally {
    uploadingPromoVideo.value = false
    event.target.value = ''
  }
}

const deletePromoVideo = async ({ deleteObject = false } = {}) => {
  try {
    await stationService.deleteStationPromoVideo(route.params.id, { deleteObject })
    promoVideo.value = null
    promoVideoUrl.value = ''
    ElMessage.success('Видео удалено')
  } catch (e) {
    ElMessage.error('Ошибка удаления видео: ' + (e?.message || e))
  }
}

const loadData = async () => {
  if (!isEditing.value) return
  
  loading.value = true
  try {
    const data = await stationService.getStation(route.params.id)
    station.value = { ...data.station }
    photos.value = data.photos || []
    docs.value = data.normativeDocs || []
    equipment.value = data.equipment || []
    specs.value = data.specs || []
    safetySystems.value = (data.safety || []).map(s => ({
      ...s,
      features: Array.isArray(s.features) ? s.features : [],
      feature_names: s.feature_names || (Array.isArray(s.features) ? s.features.map(f => typeof f === 'string' ? f : f.feature_name) : [])
    }))
    gasSources.value = data.gas_sources || []
    await loadCourseProgram()
    
    // Convert Minio keys to URLs for photos
    const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'
    for (const photo of photos.value) {
      if (photo.image_url && !photo.image_url.startsWith('http')) {
        photo.displayUrl = `${API_BASE_URL}/files/stream/${encodeURIComponent(photo.image_url)}`
      } else {
        photo.displayUrl = photo.image_url
      }
    }
    
    // Convert Minio keys to URLs for docs
    for (const doc of docs.value) {
      if (doc.file_url && !doc.file_url.startsWith('http')) {
        doc.downloadUrl = `${API_BASE_URL}/files/stream/${encodeURIComponent(doc.file_url)}`
      } else {
        doc.downloadUrl = doc.file_url
      }
    }

    await loadPromoVideo()
  } catch (error) {
    ElMessage.error('Ошибка загрузки данных: ' + error.message)
  } finally {
    loading.value = false
  }
}

const saveGeneral = async () => {
  saving.value = true
  try {
    // Ensure all fields are properly formatted
    const stationData = {
      ...station.value,
      // Convert snake_case to camelCase for API if needed, or keep as is
      short_name: station.value.short_name,
      commission_date: station.value.commission_date,
      courses_count: station.value.courses_count || 0,
      design_capacity: station.value.design_capacity,
      gas_pressure: station.value.gas_pressure,
      distance_from_border: station.value.distance_from_border,
      pipeline_diameter: station.value.pipeline_diameter,
      input_pressure: station.value.input_pressure,
      output_pressure: station.value.output_pressure,
      parallel_lines: station.value.parallel_lines,
      tech_map_image: station.value.tech_map_image
    }
    
    if (isEditing.value) {
      await stationService.updateStation(station.value.id, stationData)
      ElMessage.success('Сохранено')
      loadData() // Reload to get updated data
    } else {
      const newStation = await stationService.createStation(stationData)
      ElMessage.success('Станция создана')
      router.push(`/admin/stations/${newStation.id}`)
    }
  } catch (error) {
    ElMessage.error('Ошибка сохранения: ' + error.message)
  } finally {
    saving.value = false
  }
}

const handleMainImageUpload = async (event) => {
  const file = event.target.files[0]
  if (!file) return
  try {
    const key = await stationService.uploadFile(file, `stations/${station.value.id}/images`)
    station.value.image = key
    await saveGeneral()
    ElMessage.success('Изображение загружено')
  } catch (error) {
    ElMessage.error('Ошибка загрузки изображения: ' + error.message)
  } finally {
    event.target.value = ''
  }
}

const handleTechMapUpload = async (event) => {
  const file = event.target.files[0]
  if (!file) return
  try {
    const key = await stationService.uploadFile(file, `stations/${station.value.id}/tech_maps`)
    station.value.tech_map_image = key
    await saveGeneral()
    ElMessage.success('Техническая карта загружена')
  } catch (error) {
    ElMessage.error('Ошибка загрузки технической карты: ' + error.message)
  } finally {
    event.target.value = ''
  }
}

// Equipment CRUD
const editEquipment = (item) => {
  editingEquipment.value = item
  equipmentForm.value = { ...item }
  showEquipmentDialog.value = true
}

const saveEquipment = async () => {
  try {
    if (editingEquipment.value) {
      await stationService.updateEquipment(station.value.id, editingEquipment.value.id, equipmentForm.value)
      ElMessage.success('Оборудование обновлено')
    } else {
      await stationService.createEquipment(station.value.id, equipmentForm.value)
      ElMessage.success('Оборудование добавлено')
    }
    showEquipmentDialog.value = false
    editingEquipment.value = null
    equipmentForm.value = { name: '', model: '', manufacturer: '', quantity: 1, power: '', description: '' }
    loadData()
  } catch (error) {
    ElMessage.error('Ошибка: ' + error.message)
  }
}

const deleteEquipment = async (item) => {
  try {
    await stationService.deleteEquipment(station.value.id, item.id)
    ElMessage.success('Оборудование удалено')
    loadData()
  } catch (error) {
    ElMessage.error('Ошибка удаления: ' + error.message)
  }
}

// Specs CRUD
const editSpec = (item) => {
  editingSpec.value = item
  specForm.value = { ...item }
  showSpecDialog.value = true
}

const saveSpec = async () => {
  try {
    if (editingSpec.value) {
      await stationService.updateSpecification(station.value.id, editingSpec.value.id, specForm.value)
      ElMessage.success('Характеристика обновлена')
    } else {
      await stationService.createSpecification(station.value.id, specForm.value)
      ElMessage.success('Характеристика добавлена')
    }
    showSpecDialog.value = false
    editingSpec.value = null
    specForm.value = { category: '', value: '', unit: '', description: '' }
    loadData()
  } catch (error) {
    ElMessage.error('Ошибка: ' + error.message)
  }
}

const deleteSpec = async (item) => {
  try {
    await stationService.deleteSpecification(station.value.id, item.id)
    ElMessage.success('Характеристика удалена')
    loadData()
  } catch (error) {
    ElMessage.error('Ошибка удаления: ' + error.message)
  }
}

// Safety Systems CRUD
const editSafetySystem = (item) => {
  editingSafetySystem.value = item
  const featureNames = item.feature_names || (Array.isArray(item.features) ? item.features.map(f => typeof f === 'string' ? f : f.feature_name) : [])
  safetyForm.value = {
    name: item.name,
    description: item.description || '',
    manufacturer: item.manufacturer || '',
    features: featureNames.length > 0 ? [...featureNames] : [''],
    featureIds: Array.isArray(item.features) ? item.features.map(f => typeof f === 'object' ? f.id : null).filter(id => id !== null) : []
  }
  showSafetyDialog.value = true
}

const saveSafetySystem = async () => {
  try {
    const features = safetyForm.value.features.filter(f => f && f.trim())
    
    if (editingSafetySystem.value) {
      // Update safety system
      await stationService.updateSafetySystem(station.value.id, editingSafetySystem.value.id, {
        name: safetyForm.value.name,
        description: safetyForm.value.description,
        manufacturer: safetyForm.value.manufacturer
      })
      
      // Delete old features
      const existingFeatures = editingSafetySystem.value.features || []
      for (const feature of existingFeatures) {
        if (typeof feature === 'object' && feature.id) {
          try {
            await stationService.deleteSafetySystemFeature(station.value.id, editingSafetySystem.value.id, feature.id)
          } catch (e) {
            console.warn('Failed to delete feature:', e)
          }
        }
      }
      
      // Create new features
      for (const featureName of features) {
        if (featureName.trim()) {
          await stationService.createSafetySystemFeature(station.value.id, editingSafetySystem.value.id, {
            feature_name: featureName.trim()
          })
        }
      }
      
      ElMessage.success('Система безопасности обновлена')
    } else {
      const newSystem = await stationService.createSafetySystem(station.value.id, {
        name: safetyForm.value.name,
        description: safetyForm.value.description,
        manufacturer: safetyForm.value.manufacturer
      })
      
      for (const featureName of features) {
        if (featureName.trim()) {
          await stationService.createSafetySystemFeature(station.value.id, newSystem.id, {
            feature_name: featureName.trim()
          })
        }
      }
      
      ElMessage.success('Система безопасности добавлена')
    }
    
    showSafetyDialog.value = false
    editingSafetySystem.value = null
    safetyForm.value = { name: '', description: '', manufacturer: '', features: [''], featureIds: [] }
    loadData()
  } catch (error) {
    ElMessage.error('Ошибка: ' + error.message)
  }
}

const deleteSafetySystem = async (item) => {
  try {
    await stationService.deleteSafetySystem(station.value.id, item.id)
    ElMessage.success('Система безопасности удалена')
    loadData()
  } catch (error) {
    ElMessage.error('Ошибка удаления: ' + error.message)
  }
}

// Gas Sources CRUD
const editGasSource = (item) => {
  editingGasSource.value = item
  gasSourceForm.value = { source_name: item.source_name }
  showGasSourceDialog.value = true
}

const saveGasSource = async () => {
  try {
    if (editingGasSource.value) {
      await stationService.updateGasSupplySource(station.value.id, editingGasSource.value.id, gasSourceForm.value)
      ElMessage.success('Источник обновлен')
    } else {
      await stationService.createGasSupplySource(station.value.id, gasSourceForm.value)
      ElMessage.success('Источник добавлен')
    }
    showGasSourceDialog.value = false
    editingGasSource.value = null
    gasSourceForm.value = { source_name: '' }
    loadData()
  } catch (error) {
    ElMessage.error('Ошибка: ' + error.message)
  }
}

const deleteGasSource = async (item) => {
  try {
    await stationService.deleteGasSupplySource(station.value.id, item.id)
    ElMessage.success('Источник удален')
    loadData()
  } catch (error) {
    ElMessage.error('Ошибка удаления: ' + error.message)
  }
}

// Photos
const handlePhotoUpload = async (event) => {
  const file = event.target.files[0]
  if (!file) return
  uploadingPhoto.value = true
  try {
    const key = await stationService.uploadFile(file, `stations/${station.value.id}/photos`)
    await stationService.createPhoto(station.value.id, {
      title: file.name,
      view: 'other',
      image_url: key
    })
    ElMessage.success('Фото загружено')
    loadData()
  } catch (error) {
    ElMessage.error('Ошибка загрузки фото: ' + error.message)
  } finally {
    uploadingPhoto.value = false
    event.target.value = ''
  }
}

const updatePhoto = async (photo) => {
  try {
    await stationService.updatePhoto(station.value.id, photo.id, photo)
    ElMessage.success('Фото обновлено')
  } catch (error) {
    ElMessage.error('Ошибка обновления: ' + error.message)
  }
}

const deletePhoto = async (photo) => {
  try {
    await stationService.deletePhoto(station.value.id, photo.id)
    ElMessage.success('Фото удалено')
    photos.value = photos.value.filter(p => p.id !== photo.id)
  } catch (error) {
    ElMessage.error('Ошибка удаления: ' + error.message)
  }
}

// Docs
const handleDocUpload = async (event) => {
  const file = event.target.files[0]
  if (!file) return
  uploadingDoc.value = true
  try {
    const key = await stationService.uploadFile(file, `stations/${station.value.id}/docs`)
    await stationService.createNormativeDoc(station.value.id, {
      title: file.name,
      file_url: key
    })
    ElMessage.success('Документ загружен')
    loadData()
  } catch (error) {
    ElMessage.error('Ошибка загрузки документа: ' + error.message)
  } finally {
    uploadingDoc.value = false
    event.target.value = ''
  }
}

const deleteDoc = async (doc) => {
  try {
    await stationService.deleteNormativeDoc(station.value.id, doc.id)
    ElMessage.success('Документ удален')
    docs.value = docs.value.filter(d => d.id !== doc.id)
  } catch (error) {
    ElMessage.error('Ошибка удаления: ' + error.message)
  }
}

onMounted(() => {
  loadData()
})
</script>
