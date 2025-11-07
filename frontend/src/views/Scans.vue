<template>
  <div class="px-4 py-6 sm:px-0">
    <div class="mb-4 flex justify-between items-center">
      <h1 class="text-2xl font-bold text-gray-900 flex items-center">
        <MagnifyingGlassIcon class="h-7 w-7 mr-2 text-gray-700" />
        {{ $t('scans.title') }}
      </h1>
      <div class="flex items-center space-x-2">
        <button
          @click="loadTasks(1)"
          :disabled="loading"
          class="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
        >
          <ArrowPathIcon :class="{ 'animate-spin': loading }" class="h-4 w-4 mr-2" />
          {{ $t('common.refresh') }}
        </button>
        <button
          @click="openCreateModal"
          class="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md text-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          <PlusIcon class="h-4 w-4 mr-2" />
          {{ $t('scans.createTask') }}
        </button>
      </div>
    </div>
    
    <div class="bg-white shadow overflow-hidden sm:rounded-md relative">
      <LoadingOverlay :loading="loading" :text="$t('common.loading')" />
      <div class="overflow-x-auto max-h-[calc(100vh-300px)] overflow-y-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50 sticky top-0 z-20">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap">{{ $t('scans.taskName') }}</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap">{{ $t('scans.target') }}</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap">{{ $t('common.status') }}</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap">{{ $t('scans.progress') }}</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap">{{ $t('scans.resultCount') }}</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap">{{ $t('scans.createdAt') }}</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap sticky right-0 bg-gray-50 z-10">{{ $t('common.operation') }}</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-if="!loading && tasks.length === 0" class="text-center py-8">
              <td colspan="7" class="px-4 py-4 text-gray-500">{{ $t('scans.noTasks') }}</td>
            </tr>
            <tr 
              v-else 
              v-for="task in tasks" 
              :key="task.id" 
              class="hover:bg-gray-50 cursor-pointer transition-colors"
              :class="{ 'bg-blue-50 hover:bg-blue-100': selectedTaskId === task.id }"
              @click="selectedTaskId = task.id"
            >
              <td class="px-4 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{{ task.name }}</td>
              <td class="px-4 py-4 whitespace-nowrap text-sm text-gray-500">{{ task.target }}</td>
              <td class="px-4 py-4 whitespace-nowrap">
                <span class="px-2 py-1 text-xs font-medium rounded-full" :class="getStatusClass(task.status)">
                  {{ getStatusText(task.status) }}
                </span>
              </td>
              <td class="px-4 py-4 whitespace-nowrap text-sm text-gray-500">
                <div class="flex items-center">
                  <div class="w-16 bg-gray-200 rounded-full h-2 mr-2">
                    <div
                      class="bg-blue-600 h-2 rounded-full transition-all"
                      :style="{ width: `${task.progress || 0}%` }"
                    ></div>
                  </div>
                  <span>{{ task.progress || 0 }}%</span>
                </div>
              </td>
              <td class="px-4 py-4 whitespace-nowrap text-sm text-gray-500">{{ task.result_count || 0 }}</td>
              <td class="px-4 py-4 whitespace-nowrap text-sm text-gray-500">{{ formatDate(task.created_at) }}</td>
              <td class="px-4 py-4 whitespace-nowrap text-sm font-medium sticky right-0 bg-white z-10 transition-colors"
                  :class="{ 'bg-blue-50 hover:bg-blue-100': selectedTaskId === task.id }"
                  @click.stop
              >
                <button
                  @click="viewResults(task.id)"
                  class="text-blue-600 hover:text-blue-900 p-1 rounded hover:bg-blue-50"
                  :title="$t('scans.viewResults')"
                >
                  <EyeIcon class="h-5 w-5" />
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <div v-if="pagination && pagination.total > 0" class="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6">
        <div class="flex items-center space-x-4">
          <div class="flex items-center space-x-2">
            <label class="text-sm text-gray-700">{{ $t('common.perPage') }}:</label>
            <select
              v-model.number="perPage"
              @change="loadTasks(1)"
              class="px-2 py-1 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            >
              <option :value="10">10</option>
              <option :value="20">20</option>
              <option :value="50">50</option>
              <option :value="100">100</option>
            </select>
          </div>
          <p class="text-sm text-gray-700">
            {{ $t('common.showing') }} <span class="font-medium">{{ (pagination.page - 1) * pagination.per_page + 1 }}</span>
            {{ $t('common.to') }} <span class="font-medium">{{ Math.min(pagination.page * pagination.per_page, pagination.total) }}</span>
            {{ $t('common.of') }} <span class="font-medium">{{ pagination.total }}</span> {{ $t('common.items') }}
          </p>
        </div>
        <div class="flex items-center space-x-2">
          <button
            @click="loadTasks(pagination.page - 1)"
            :disabled="pagination.page <= 1"
            class="relative inline-flex items-center px-3 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {{ $t('common.previousPage') }}
          </button>
          <span class="text-sm text-gray-700">
            {{ $t('common.page') }} {{ pagination.page }} / {{ pagination.pages }} {{ $t('common.pages') }}
          </span>
          <button
            @click="loadTasks(pagination.page + 1)"
            :disabled="pagination.page >= pagination.pages"
            class="relative inline-flex items-center px-3 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {{ $t('common.nextPage') }}
          </button>
        </div>
      </div>
    </div>

    <!-- Create Scan Task Modal -->
    <Modal :open="showCreateModal" @close="closeCreateModal" :title="$t('scans.createTaskTitle')" max-width="md">
      <form @submit.prevent="createTask" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700">{{ $t('scans.taskName') }} *</label>
          <input
            v-model="taskForm.name"
            type="text"
            required
            class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700">{{ $t('scans.target') }} *</label>
          <input
            v-model="taskForm.target"
            type="text"
            required
            :placeholder="$t('scans.targetPlaceholder')"
            class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          />
          <p class="mt-1 text-xs text-gray-500">{{ $t('scans.targetHint') }}</p>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700">{{ $t('scans.nmapArgs') }}</label>
          <input
            v-model="taskForm.nmap_args"
            type="text"
            :placeholder="$t('scans.nmapArgsPlaceholder')"
            class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          />
          <p class="mt-1 text-xs text-gray-500">{{ $t('scans.nmapArgsHint') }}</p>
        </div>
      </form>
      <template #footer>
        <button
          type="button"
          @click="closeCreateModal"
          class="mt-3 inline-flex w-full justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 sm:mt-0 sm:w-auto"
        >
          {{ $t('common.cancel') }}
        </button>
        <button
          type="button"
          @click="createTask"
          :disabled="creating"
          class="inline-flex w-full justify-center rounded-md bg-blue-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-blue-500 sm:ml-3 sm:w-auto disabled:opacity-50"
        >
          {{ creating ? $t('scans.creating') : $t('scans.createTaskButton') }}
        </button>
      </template>
    </Modal>

    <!-- Results Modal -->
    <Modal :open="showResultsModal" @close="closeResultsModal" :title="$t('scans.resultsTitle')" max-width="2xl">
      <div v-if="scanResults" class="space-y-4">
        <div class="text-sm text-gray-600">
          {{ $t('scans.foundHosts', { count: scanResults.length }) }}
        </div>
        <div class="max-h-96 overflow-y-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50 sticky top-0 z-10">
              <tr>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">{{ $t('hosts.ip') }}</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">{{ $t('hosts.hostname') }}</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">MAC</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">{{ $t('scans.vendor') }}</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">OS</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">{{ $t('common.operation') }}</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="(result, index) in scanResults" :key="index" class="hover:bg-gray-50">
                <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-900">{{ result.ip }}</td>
                <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-500">{{ result.hostname || '-' }}</td>
                <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-500">{{ result.mac || '-' }}</td>
                <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-500">{{ result.vendor || '-' }}</td>
                <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-500">{{ result.os || '-' }}</td>
                <td class="px-4 py-3 whitespace-nowrap text-sm font-medium">
                  <button
                    @click="addToHosts(result)"
                    class="text-blue-600 hover:text-blue-900"
                  >
                    {{ $t('scans.addToHosts') }}
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      <template #footer>
        <button
          type="button"
          @click="closeResultsModal"
          class="mt-3 inline-flex w-full justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 sm:mt-0 sm:w-auto"
        >
          {{ $t('common.close') }}
        </button>
        <button
          v-if="scanResults && scanResults.length > 0"
          type="button"
          @click="batchAddToHosts"
          class="inline-flex w-full justify-center rounded-md bg-blue-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-blue-500 sm:ml-3 sm:w-auto"
        >
          {{ $t('scans.batchAddToHosts') }}
        </button>
      </template>
    </Modal>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { scansApi, type ScanTask } from '@/api/scans'
import { hostsApi } from '@/api/hosts'
import Modal from '@/components/Modal.vue'
import LoadingOverlay from '@/components/LoadingOverlay.vue'
import { useToastStore } from '@/stores/toast'
import { useSettingsStore } from '@/stores/settings'
import { EyeIcon, MagnifyingGlassIcon, PlusIcon, ArrowPathIcon } from '@heroicons/vue/24/outline'

const { t } = useI18n()

const toastStore = useToastStore()
const settingsStore = useSettingsStore()

const tasks = ref<any[]>([])
const loading = ref(false)
const showCreateModal = ref(false)
const showResultsModal = ref(false)
const taskForm = ref<Partial<ScanTask>>({})
const creating = ref(false)
const scanResults = ref<any[]>([])
const currentTaskId = ref<number | null>(null)
const selectedTaskId = ref<number | null>(null)
const pagination = ref<any>(null)
const perPage = ref(settingsStore.defaultPageSize)

let pollInterval: ReturnType<typeof setInterval> | null = null

const getStatusClass = (status: string) => {
  const classes: Record<string, string> = {
    completed: 'bg-green-100 text-green-800',
    running: 'bg-blue-100 text-blue-800',
    pending: 'bg-yellow-100 text-yellow-800',
    failed: 'bg-red-100 text-red-800',
  }
  return classes[status] || 'bg-gray-100 text-gray-800'
}

const getStatusText = (status: string) => {
  const texts: Record<string, string> = {
    completed: t('common.completed'),
    running: t('common.running'),
    pending: t('common.pending'),
    failed: t('common.failed'),
  }
  return texts[status] || status
}

const formatDate = (date: string) => {
  if (!date) return '-'
  return new Date(date).toLocaleString('zh-CN')
}

const loadTasks = async (page = 1) => {
  loading.value = true
  try {
    const response: any = await scansApi.getScanTasks({ page, per_page: perPage.value })
    if (response && response.code === 200) {
      tasks.value = response.data || []
      pagination.value = response.pagination
    } else if (Array.isArray(response)) {
      tasks.value = response
    } else if (response && response.data) {
      tasks.value = response.data
      pagination.value = response.pagination
    }
  } catch (error: any) {
    toastStore.error(error.response?.data?.message || t('messages.loadFailed'))
  } finally {
    loading.value = false
  }
}

const openCreateModal = () => {
  taskForm.value = {
    nmap_args: '-sS -O',
  }
  showCreateModal.value = true
}

const closeCreateModal = () => {
  showCreateModal.value = false
  taskForm.value = {}
}

const createTask = async () => {
  creating.value = true
  try {
    await scansApi.createScanTask(taskForm.value as ScanTask)
    toastStore.success(t('scans.createTaskButton'))
    closeCreateModal()
    loadTasks()
  } catch (error: any) {
    toastStore.error(error.response?.data?.message || t('messages.operationFailed'))
  } finally {
    creating.value = false
  }
}

const viewResults = async (id: number) => {
  currentTaskId.value = id
  try {
    const response = await scansApi.getScanResults(id)
    scanResults.value = response.data || []
    showResultsModal.value = true
  } catch (error: any) {
    toastStore.error(error.response?.data?.message || t('messages.loadFailed'))
  }
}

const closeResultsModal = () => {
  showResultsModal.value = false
  scanResults.value = []
  currentTaskId.value = null
}

const addToHosts = async (result: any) => {
  try {
    await hostsApi.createHost({
      ip: result.ip,
      hostname: result.hostname,
      mac: result.mac,
      vendor: result.vendor,
      os_type: result.os?.toLowerCase(),
    })
    toastStore.success(t('scans.addSuccess'))
  } catch (error: any) {
    toastStore.error(error.response?.data?.message || t('scans.addFailed'))
  }
}

const batchAddToHosts = async () => {
  if (!scanResults.value || scanResults.value.length === 0) return
  try {
    const hosts = scanResults.value.map((result: any) => ({
      ip: result.ip,
      hostname: result.hostname,
      mac: result.mac,
      vendor: result.vendor,
      os_type: result.os?.toLowerCase(),
    }))
    await hostsApi.batchCreateHosts(hosts)
    toastStore.success(t('scans.batchAddSuccess', { count: hosts.length }))
    closeResultsModal()
  } catch (error: any) {
    toastStore.error(error.response?.data?.message || t('scans.batchAddFailed'))
  }
}

onMounted(() => {
  loadTasks()
  // Poll for updates every 5 seconds
  pollInterval = setInterval(() => {
    loadTasks()
  }, 5000)
})

onUnmounted(() => {
  if (pollInterval) {
    clearInterval(pollInterval)
  }
})
</script>
