<template>
  <AppLayout>
    <div class="section-padding bg-gray-50 min-h-screen">
      <div class="page-container">
        <!-- Header -->
        <div class="mb-8">
          <h1 class="text-3xl font-bold text-gray-900 mb-2">Админ-панель</h1>
          <p class="text-gray-600">Управление пользователями и файлами системы</p>
        </div>

        <!-- Tabs -->
        <el-tabs v-model="activeTab" @tab-change="handleTabChange" class="mb-8">
          <el-tab-pane label="Пользователи" name="users">
            <el-icon><User /></el-icon>
            <span class="ml-1">Пользователи</span>
          </el-tab-pane>
          <el-tab-pane label="Файлы" name="files">
            <el-icon><Folder /></el-icon>
            <span class="ml-1">Файлы</span>
          </el-tab-pane>
        </el-tabs>

        <!-- Users Tab Content -->
        <div v-show="activeTab === 'users'">

        <!-- Stats Cards -->
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-6 mb-8">
          <div class="card p-6">
            <div class="flex items-center">
              <div class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <el-icon :size="24" class="text-blue-600"><User /></el-icon>
              </div>
              <div class="ml-4">
                <p class="text-sm text-gray-600">Всего пользователей</p>
                <p class="text-2xl font-bold text-gray-900">{{ stats.totalUsers }}</p>
              </div>
            </div>
          </div>

          <div class="card p-6">
            <div class="flex items-center">
              <div class="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                <el-icon :size="24" class="text-green-600"><Check /></el-icon>
              </div>
              <div class="ml-4">
                <p class="text-sm text-gray-600">Активных</p>
                <p class="text-2xl font-bold text-gray-900">{{ stats.activeUsers }}</p>
              </div>
            </div>
          </div>

          <div class="card p-6">
            <div class="flex items-center">
              <div class="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center">
                <el-icon :size="24" class="text-orange-600"><Lock /></el-icon>
              </div>
              <div class="ml-4">
                <p class="text-sm text-gray-600">Администраторов</p>
                <p class="text-2xl font-bold text-gray-900">{{ stats.admins }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Actions -->
        <div class="mb-6">
          <el-button type="primary" @click="showCreateDialog = true" :icon="Plus">
            Создать пользователя
          </el-button>
        </div>

        <!-- Users Table -->
        <div class="card overflow-hidden">
          <div class="p-6">
            <div class="flex items-center justify-between mb-6">
              <h2 class="text-xl font-semibold text-gray-900">Пользователи</h2>
              <div class="flex items-center gap-4">
                <el-input
                  v-model="searchQuery"
                  placeholder="Поиск..."
                  class="w-64"
                  clearable
                >
                  <template #prefix>
                    <el-icon><Search /></el-icon>
                  </template>
                </el-input>
                <el-select v-model="roleFilter" placeholder="Роль" style="width: 150px" clearable>
                  <el-option label="Все" value="" />
                  <el-option label="Админ" value="admin" />
                  <el-option label="Инструктор" value="instructor" />
                  <el-option label="Пользователь" value="user" />
                </el-select>
              </div>
            </div>

            <el-table 
              :data="filteredUsers" 
              v-loading="loading"
              style="width: 100%"
            >
              <el-table-column prop="username" label="Логин" width="150" />
              <el-table-column prop="full_name" label="Полное имя" />
              <el-table-column prop="email" label="Email" />
              <el-table-column label="Роль" width="120">
                <template #default="{ row }">
                  <el-tag 
                    :type="getRoleTagType(row.role)"
                    size="small"
                  >
                    {{ getRoleText(row.role) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="Статус" width="100">
                <template #default="{ row }">
                  <el-tag 
                    :type="row.is_active ? 'success' : 'danger'"
                    size="small"
                  >
                    {{ row.is_active ? 'Активен' : 'Неактивен' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="created_at" label="Создан" width="180">
                <template #default="{ row }">
                  {{ formatDate(row.created_at) }}
                </template>
              </el-table-column>
              <el-table-column label="Действия" width="220" fixed="right">
                <template #default="{ row }">
                  <el-button 
                    size="small" 
                    type="primary" 
                    @click="editUser(row)"
                  >
                    Редактировать
                  </el-button>
                  <el-button 
                    size="small" 
                    :type="row.is_active ? 'warning' : 'success'"
                    @click="toggleUserStatus(row)"
                  >
                    {{ row.is_active ? 'Деактивировать' : 'Активировать' }}
                  </el-button>
                  <el-button 
                    size="small" 
                    type="danger"
                    @click="deleteUser(row)"
                  >
                    Удалить
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </div>
        </div>

        <!-- Files Tab Content -->
        <div v-show="activeTab === 'files'">
          <!-- Upload Section -->
          <div class="card p-6 mb-6">
            <h2 class="text-xl font-semibold text-gray-900 mb-4">Загрузка файлов</h2>
            <el-upload
              ref="uploadRef"
              class="upload-demo"
              drag
              :auto-upload="false"
              :on-change="handleFileChange"
              :file-list="fileList"
              multiple
            >
              <el-icon class="el-icon--upload"><upload-filled /></el-icon>
              <div class="el-upload__text">
                Перетащите файл сюда или <em>нажмите для загрузки</em>
              </div>
              <template #tip>
                <div class="el-upload__tip">
                  Поддерживаются файлы любого типа
                </div>
              </template>
            </el-upload>

            <div v-if="fileList.length > 0" class="mt-4">
              <el-button type="primary" @click="uploadFiles" :loading="uploading">
                Загрузить файлы
              </el-button>
              <el-button @click="clearFileList">Очистить список</el-button>
            </div>

            <!-- Upload Progress -->
            <div v-if="uploadProgress > 0 && uploadProgress < 100" class="mt-4">
              <el-progress :percentage="uploadProgress" :status="uploadStatus" />
              <p class="text-sm text-gray-600 mt-2">{{ uploadProgressText }}</p>
            </div>
          </div>

          <!-- Files List -->
          <div class="card">
            <div class="p-6">
              <div class="flex items-center justify-between mb-6">
                <div class="flex items-center gap-4">
                  <h2 class="text-xl font-semibold text-gray-900">Загруженные файлы</h2>
                  <!-- Breadcrumb -->
                  <el-breadcrumb separator="/" v-if="currentFolder">
                    <el-breadcrumb-item>
                      <el-button text size="small" @click="navigateToFolder('')">
                        <el-icon><House /></el-icon>
                        Корень
                      </el-button>
                    </el-breadcrumb-item>
                    <el-breadcrumb-item v-for="(part, index) in currentFolderParts" :key="index">
                      <el-button 
                        text 
                        size="small" 
                        @click="navigateToFolder(part.path)"
                        v-if="index < currentFolderParts.length - 1"
                      >
                        {{ part.name }}
                      </el-button>
                      <span v-else class="text-gray-600">{{ part.name }}</span>
                    </el-breadcrumb-item>
                  </el-breadcrumb>
                </div>
                <el-button :icon="Refresh" @click="loadFolderContents" circle />
              </div>

              <!-- Folders Grid -->
              <div v-if="currentFolders.length > 0" class="mb-6">
                <h3 class="text-sm font-semibold text-gray-700 mb-3">Папки</h3>
                <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                  <div
                    v-for="folder in currentFolders"
                    :key="folder.path"
                    class="folder-card p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-all cursor-pointer"
                    @click="navigateToFolder(folder.path)"
                  >
                    <div class="flex items-center gap-3">
                      <el-icon :size="48" class="text-blue-500"><Folder /></el-icon>
                      <div>
                        <h3 class="font-medium text-gray-900">{{ folder.name }}</h3>
                        <p class="text-xs text-gray-500">Папка</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Files Grid -->
              <div v-if="currentFolders.length > 0" class="mb-4">
                <h3 class="text-sm font-semibold text-gray-700 mb-3">Файлы</h3>
              </div>

              <!-- Empty State -->
              <div v-if="uploadedFiles.length === 0 && currentFolders.length === 0" class="text-center py-12">
                <el-icon :size="64" class="text-gray-300"><FolderOpened /></el-icon>
                <p class="text-gray-500 mt-4">{{ currentFolder ? 'Папка пуста' : 'Файлы еще не загружены' }}</p>
              </div>

              <!-- Files Grid -->
              <div v-else-if="uploadedFiles.length > 0" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                <div
                  v-for="file in uploadedFiles"
                  :key="file.objectName"
                  class="file-card p-4 border border-gray-200 rounded-lg hover:shadow-md transition-shadow"
                >
                  <div class="flex items-start justify-between mb-2">
                    <el-icon :size="32" class="text-blue-500"><Document /></el-icon>
                    <el-button
                      size="small"
                      text
                      type="danger"
                      :icon="Delete"
                      @click="deleteFile(file)"
                    />
                  </div>
                  <h3 class="font-medium text-sm text-gray-900 truncate mb-1在黑быдля" :title="file.original_name || file.originalName">
                    {{ file.original_name || file.originalName }}
                  </h3>
                  <p class="text-xs text-gray-500 mb-3">{{ file.sizeFormatted || (file.file_size ? formatFileSize(file.file_size) : '') }}</p>
                  <div class="flex gap-2">
                    <el-button size="small" type="primary" :icon="View" @click="previewFile(file)">
                      Просмотр
                    </el-button>
                    <el-button size="small" :icon="Download" @click="downloadFile(file)">
                      Скачать
                    </el-button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Create/Edit User Dialog -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingUser ? 'Редактировать пользователя' : 'Создать пользователя'"
      width="600px"
    >
      <el-form :model="userForm" :rules="userRules" ref="userFormRef" label-width="140px">
        <el-form-item label="Логин" prop="username">
          <el-input 
            v-model="userForm.username" 
            placeholder="Введите логин"
            :disabled="!!editingUser"
          />
        </el-form-item>

        <el-form-item label="Полное имя" prop="full_name">
          <el-input v-model="userForm.full_name" placeholder="Введите полное имя" />
        </el-form-item>

        <el-form-item label="Email" prop="email">
          <el-input v-model="userForm.email" placeholder="Введите email" />
        </el-form-item>

        <el-form-item label="Роль" prop="role">
          <el-select v-model="userForm.role" placeholder="Выберите роль" style="width: 100%">
            <el-option label="Пользователь" value="user" />
            <el-option label="Инструктор" value="instructor" />
            <el-option label="Администратор" value="admin" />
          </el-select>
        </el-form-item>

        <el-form-item v-if="!editingUser" label="Пароль" prop="password">
          <el-input 
            v-model="userForm.password" 
            type="password"
            placeholder="Введите пароль"
            show-password
          />
        </el-form-item>

        <el-form-item label="Статус">
          <el-switch v-model="userForm.is_active" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showCreateDialog = false">Отмена</el-button>
        <el-button type="primary" @click="saveUser" :loading="saving">
          {{ editingUser ? 'Сохранить' : 'Создать' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- Generate Credentials Dialog -->
    <el-dialog
      v-model="showGenerateDialog"
      title="Сгенерировать учетные данные"
      width="500px"
    >
      <el-form label-width="120px">
        <el-form-item label="Количество пользователей">
          <el-input-number v-model="generateCount" :min="1" :max="100" />
        </el-form-item>

        <el-form-item label="Роль">
          <el-select v-model="generateRole" style="width: 100%">
            <el-option label="Пользователь" value="user" />
            <el-option label="Инструктор" value="instructor" />
            <el-option label="Администратор" value="admin" />
          </el-select>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showGenerateDialog = false">Отмена</el-button>
        <el-button type="primary" @click="generateCredentials" :loading="generating">
          Сгенерировать
        </el-button>
      </template>
    </el-dialog>
  </AppLayout>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import AppLayout from '@/components/AppLayout.vue'
import { User, Check, Lock, Plus, Search, Folder, UploadFilled, Refresh, FolderOpened, Document, Delete, View, Download, House } from '@element-plus/icons-vue'
import { createClient } from '@supabase/supabase-js'
import minioService, { formatFileSize } from '@/services/minioService'

const supabase = createClient(
  'https://fusartgifhigtysskgfg.supabase.co',
  'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZ1c2FydGdpZmhpZ3R5c3NrZ2ZnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjEyMjQ1NzgsImV4cCI6MjA3NjgwMDU3OH0.l_xGpHpf4FuRmgG_Cz84lub8CLQCm-nMKGPn76CrddE'
)

export default {
  name: 'AdminPanel',
  components: {
    AppLayout,
    User,
    Check,
    Lock,
    Plus,
    Search,
    Folder,
    UploadFilled,
    Refresh,
    FolderOpened,
    Document,
    Delete,
    View,
    Download,
    House
  },
  setup() {
    const users = ref([])
    const loading = ref(false)
    const saving = ref(false)
    const generating = ref(false)
    const searchQuery = ref('')
    const roleFilter = ref('')
    const showCreateDialog = ref(false)
    const showGenerateDialog = ref(false)
    const editingUser = ref(null)
    const generateCount = ref(10)
    const generateRole = ref('user')
    const userFormRef = ref(null)

    // Files Management
    const activeTab = ref('users')
    const fileList = ref([])
    const uploadedFiles = ref([])
    const uploading = ref(false)
    const uploadProgress = ref(0)
    const uploadStatus = ref('')
    const uploadProgressText = ref('')
    const uploadRef = ref(null)
    const currentFolder = ref('')
    const currentFolders = ref([])

    const userForm = ref({
      username: '',
      full_name: '',
      email: '',
      role: 'user',
      password: '',
      is_active: true
    })

    const userRules = {
      username: [
        { required: true, message: 'Введите логин', trigger: 'blur' },
        { min: 3, message: 'Логин должен быть не менее 3 символов', trigger: 'blur' }
      ],
      full_name: [
        { required: true, message: 'Введите полное имя', trigger: 'blur' }
      ],
      email: [
        { type: 'email', message: 'Некорректный email', trigger: 'blur' }
      ],
      role: [
        { required: true, message: 'Выберите роль', trigger: 'change' }
      ],
      password: [
        { required: true, message: 'Введите пароль', trigger: 'blur' },
        { min: 6, message: 'Пароль должен быть не менее 6 символов', trigger: 'blur' }
      ]
    }

    // Генерация случайного пароля
    const generatePassword = (length = 12) => {
      const charset = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
      let password = ''
      for (let i = 0; i < length; i++) {
        password += charset.charAt(Math.floor(Math.random() * charset.length))
      }
      return password
    }

    // Генерация логина
    const generateUsername = (index) => {
      return `user${String(index).padStart(4, '0')}`
    }

    // Загрузка пользователей
    const loadUsers = async () => {
      loading.value = true
      try {
        const { data, error } = await supabase
          .from('users')
          .select('*')
          .order('created_at', { ascending: false })

        if (error) throw error
        users.value = data || []
      } catch (error) {
        console.error('Error loading users:', error)
        ElMessage.error('Ошибка загрузки пользователей')
      } finally {
        loading.value = false
      }
    }

    // Фильтрация пользователей
    const filteredUsers = computed(() => {
      let filtered = users.value

      if (searchQuery.value) {
        const query = searchQuery.value.toLowerCase()
        filtered = filtered.filter(user => 
          user.username.toLowerCase().includes(query) ||
          user.full_name?.toLowerCase().includes(query) ||
          user.email?.toLowerCase().includes(query)
        )
      }

      if (roleFilter.value) {
        filtered = filtered.filter(user => user.role === roleFilter.value)
      }

      return filtered
    })

    // Статистика
    const stats = computed(() => ({
      totalUsers: users.value.length,
      activeUsers: users.value.filter(u => u.is_active).length,
      admins: users.value.filter(u => u.role === 'admin').length
    }))

    // Сохранение пользователя
    const saveUser = async () => {
      if (!userFormRef.value) return

      try {
        await userFormRef.value.validate()
        saving.value = true

        const userData = {
          ...userForm.value,
          updated_at: new Date().toISOString()
        }

        if (editingUser.value) {
          // Редактирование
          delete userData.password
          const { error } = await supabase
            .from('users')
            .update(userData)
            .eq('id', editingUser.value.id)

          if (error) throw error
          ElMessage.success('Пользователь обновлен')
        } else {
          // Создание
          if (!userData.password) {
            ElMessage.error('Введите пароль')
            return
          }

          const { error } = await supabase
            .from('users')
            .insert(userData)

          if (error) throw error
          ElMessage.success('Пользователь создан')
        }

        showCreateDialog.value = false
        resetForm()
        await loadUsers()
      } catch (error) {
        console.error('Error saving user:', error)
        ElMessage.error(error.message || 'Ошибка сохранения пользователя')
      } finally {
        saving.value = false
      }
    }

    // Редактирование пользователя
    const editUser = (user) => {
      editingUser.value = user
      userForm.value = {
        username: user.username,
        full_name: user.full_name || '',
        email: user.email || '',
        role: user.role,
        password: '',
        is_active: user.is_active
      }
      showCreateDialog.value = true
    }

    // Сброс формы
    const resetForm = () => {
      editingUser.value = null
      userForm.value = {
        username: '',
        full_name: '',
        email: '',
        role: 'user',
        password: '',
        is_active: true
      }
    }

    // Удаление пользователя
    const deleteUser = async (user) => {
      try {
        await ElMessageBox.confirm(
          `Вы уверены, что хотите удалить пользователя ${user.username}?`,
          'Подтверждение',
          {
            confirmButtonText: 'Да',
            cancelButtonText: 'Нет',
            type: 'warning'
          }
        )

        const { error } = await supabase
          .from('users')
          .delete()
          .eq('id', user.id)

        if (error) throw error
        ElMessage.success('Пользователь удален')
        await loadUsers()
      } catch (error) {
        if (error !== 'cancel') {
          console.error('Error deleting user:', error)
          ElMessage.error('Ошибка удаления пользователя')
        }
      }
    }

    // Переключение статуса пользователя
    const toggleUserStatus = async (user) => {
      try {
        const { error } = await supabase
          .from('users')
          .update({ is_active: !user.is_active })
          .eq('id', user.id)

        if (error) throw error
        ElMessage.success(`Пользователь ${!user.is_active ? 'активирован' : 'деактивирован'}`)
        await loadUsers()
      } catch (error) {
        console.error('Error toggling user status:', error)
        ElMessage.error('Ошибка обновления статуса')
      }
    }

    // Генерация учетных данных
    const generateCredentials = async () => {
      generating.value = true
      const credentials = []
      
      try {
        // Получаем текущий максимальный номер пользователя
        const existingUsers = await supabase
          .from('users')
          .select('username')

        const existingUsernames = existingUsers.data.map(u => u.username)
        const maxNumber = Math.max(...existingUsernames.map(u => {
          const match = u.match(/user(\d+)/)
          return match ? parseInt(match[1]) : 0
        }), 0)

        // Создаем пользователей
        const usersToCreate = []
        for (let i = 1; i <= generateCount.value; i++) {
          const username = generateUsername(maxNumber + i)
          const password = generatePassword(10)
          
          credentials.push({ username, password })
          
          usersToCreate.push({
            username,
            password_hash: password, // В продакшене нужно хешировать!
            full_name: `Пользователь ${maxNumber + i}`,
            role: generateRole.value,
            is_active: true
          })
        }

        // Вставляем пользователей
        const { error } = await supabase
          .from('users')
          .insert(usersToCreate)

        if (error) throw error

        // Показываем созданные учетные данные
        const credentialsText = credentials
          .map(c => `Логин: ${c.username}, Пароль: ${c.password}`)
          .join('\n')

        await ElMessageBox.alert(
          `Создано ${generateCount.value} пользователей:\n\n${credentialsText}`,
          'Учетные данные созданы',
          {
            confirmButtonText: 'OK',
            dangerouslyUseHTMLString: false
          }
        )

        showGenerateDialog.value = false
        await loadUsers()
      } catch (error) {
        console.error('Error generating credentials:', error)
        ElMessage.error('Ошибка создания пользователей')
      } finally {
        generating.value = false
      }
    }

    // Вспомогательные функции
    const getRoleTagType = (role) => {
      const types = {
        admin: 'danger',
        instructor: 'warning',
        user: 'info'
      }
      return types[role] || 'info'
    }

    const getRoleText = (role) => {
      const texts = {
        admin: 'Админ',
        instructor: 'Инструктор',
        user: 'Пользователь'
      }
      return texts[role] || role
    }

    const formatDate = (dateString) => {
      if (!dateString) return '-'
      const date = new Date(dateString)
      return date.toLocaleDateString('ru-RU', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    }

    // File Management Functions
    const handleTabChange = (tabName) => {
      if (tabName === 'files') {
        loadFolderContents()
      }
    }

    const loadFolderContents = async () => {
      try {
        // Получаем содержимое текущей папки
        const contents = await minioService.getFolderContents(currentFolder.value)
        currentFolders.value = contents.folders
        uploadedFiles.value = contents.files
      } catch (error) {
        console.error('Ошибка загрузки содержимого папки:', error)
        ElMessage.error(`Ошибка загрузки: ${error.message}`)
      }
    }

    const navigateToFolder = (folderPath) => {
      currentFolder.value = folderPath
      loadFolderContents()
    }

    const currentFolderParts = computed(() => {
      if (!currentFolder.value) return []
      
      const parts = currentFolder.value.split('/').filter(Boolean)
      const result = []
      let currentPath = ''
      
      parts.forEach(part => {
        currentPath += (currentPath ? '/' : '') + part
        result.push({
          name: part,
          path: currentPath
        })
      })
      
      return result
    })

    const handleFileChange = (file, fileListNew) => {
      fileList.value = fileListNew
    }

    const clearFileList = () => {
      fileList.value = []
    }

    const uploadFiles = async () => {
      if (fileList.value.length === 0) {
        ElMessage.warning('Выберите файлы для загрузки')
        return
      }

      uploading.value = true
      uploadProgress.value = 0
      uploadStatus.value = ''
      uploadProgressText.value = 'Начало загрузки...'

      try {
        const totalFiles = fileList.value.length
        let successCount = 0
        let failCount = 0

        for (let i = 0; i < fileList.value.length; i++) {
          const file = fileList.value[i].raw

          uploadProgressText.value = `Загрузка файла ${i + 1} из ${totalFiles}: ${file.name}`
          uploadProgress.value = Math.round((i / totalFiles) * 90)

          try {
            const result = await minioService.uploadFile(file)
            uploadedFiles.value.push(result)
            successCount++
          } catch (error) {
            console.error('Ошибка загрузки файла:', error)
            failCount++
          }
        }

        uploadProgress.value = 100
        uploadStatus.value = 'success'

        if (successCount > 0) {
          ElMessage.success(`Успешно загружено файлов: ${successCount}${failCount > 0 ? `, ошибок: ${failCount}` : ''}`)
        } else {
          ElMessage.error('Не удалось загрузить файлы')
        }

        // Сохраняем информацию о файлах в Supabase
        if (successCount > 0) {
          await saveFilesToDatabase(uploadedFiles.value.slice(-successCount))
        }

        clearFileList()
      } catch (error) {
        console.error('Ошибка загрузки файлов:', error)
        uploadStatus.value = 'exception'
        ElMessage.error('Ошибка при загрузке файлов')
      } finally {
        uploading.value = false
      }
    }

    const saveFilesToDatabase = async (files) => {
      try {
        const { error } = await supabase
          .from('files')
          .insert(
            files.map(file => ({
              object_name: file.objectName,
              file_name: file.fileName,
              original_name: file.originalName,
              file_size: file.size,
              file_type: file.type,
              file_url: file.url,
              uploaded_at: new Date().toISOString()
            }))
          )

        if (error) throw error
      } catch (error) {
        console.error('Ошибка сохранения в БД:', error)
      }
    }

    const loadFiles = async () => {
      try {
        // Получаем список файлов напрямую из MinIO
        const files = await minioService.listFiles()
        uploadedFiles.value = files
        
        // Также загружаем из Supabase для дополнительной информации
        try {
          const { data, error } = await supabase
            .from('files')
            .select('*')
            .order('uploaded_at', { ascending: false })

          if (!error && data) {
            // Объединяем данные из MinIO и Supabase
            uploadedFiles.value = files.map(file => {
              const dbFile = data.find(f => f.object_name === file.objectName)
              return dbFile ? { ...file, id: dbFile.id } : file
            })
          }
        } catch (dbError) {
          console.log('Не удалось загрузить из БД, используем данные из MinIO')
        }
      } catch (error) {
        console.error('Ошибка загрузки файлов:', error)
        ElMessage.error(`Ошибка загрузки списка файлов: ${error.message}`)
      }
    }

    const previewFile = (file) => {
      window.open(file.file_url || file.url, '_blank')
    }

    const downloadFile = (file) => {
      const link = document.createElement('a')
      link.href = file.file_url || file.url
      link.download = file.original_name || file.originalName
      link.target = '_blank'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    }

    const deleteFile = async (file) => {
      try {
        await ElMessageBox.confirm(
          `Вы уверены, что хотите удалить файл ${file.original_name || file.originalName}?`,
          'Подтверждение',
          {
            confirmButtonText: 'Да',
            cancelButtonText: 'Нет',
            type: 'warning'
          }
        )

        // Удаляем из MinIO
        await minioService.deleteFile(file.objectName)

        // Удаляем из БД (если есть ID)
        if (file.id) {
          try {
            const { error } = await supabase
              .from('files')
              .delete()
              .eq('id', file.id)

            if (error) console.warn('Ошибка удаления из БД:', error)
          } catch (dbError) {
            console.warn('Не удалось удалить из БД:', dbError)
          }
        }

        ElMessage.success('Файл удален')
        await loadFolderContents()
      } catch (error) {
        if (error !== 'cancel') {
          console.error('Ошибка удаления файла:', error)
          ElMessage.error(`Ошибка удаления файла: ${error.message}`)
        }
      }
    }

    onMounted(() => {
      loadUsers()
    })

    return {
      users,
      loading,
      saving,
      generating,
      searchQuery,
      roleFilter,
      showCreateDialog,
      showGenerateDialog,
      editingUser,
      generateCount,
      generateRole,
      userForm,
      userRules,
      userFormRef,
      stats,
      filteredUsers,
      saveUser,
      editUser,
      deleteUser,
      toggleUserStatus,
      generateCredentials,
      getRoleTagType,
      getRoleText,
      formatDate,
      // Files
      activeTab,
      handleTabChange,
      fileList,
      uploadedFiles,
      uploading,
      uploadProgress,
      uploadStatus,
      uploadProgressText,
      uploadRef,
      handleFileChange,
      clearFileList,
      uploadFiles,
      loadFiles,
      previewFile,
      downloadFile,
      deleteFile,
      formatFileSize,
      currentFolder,
      currentFolders,
      navigateToFolder,
      loadFolderContents,
      currentFolderParts
    }
  }
}
</script>

<style scoped>
.section-padding {
  padding: 2rem 1rem;
}

@media (min-width: 640px) {
  .section-padding {
    padding: 3rem 1.5rem;
  }
}

@media (min-width: 1024px) {
  .section-padding {
    padding: 4rem 2rem;
  }
}
</style>

