<template>
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
</template>

<script setup>
import { useStationEditorContext } from '../context'

const {
  station,
  saving,
  saveGeneral,
  handleMainImageUpload,
  handleTechMapUpload
} = useStationEditorContext()
</script>

