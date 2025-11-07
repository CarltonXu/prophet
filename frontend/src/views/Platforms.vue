<template>
  <div class="px-4 py-6 sm:px-0">
    <div class="mb-4 flex justify-between items-center">
      <div>
        <h1 class="text-2xl font-bold text-gray-900 flex items-center">
          <CloudIcon class="h-7 w-7 mr-2 text-gray-700" />
          {{ $t('platforms.title') }}
        </h1>
        <p class="mt-1 text-sm text-gray-500">{{ $t('platforms.subtitle') }}</p>
      </div>
          <button
            @click="loadPlatforms"
            :disabled="loading"
            class="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
          >
            <ArrowPathIcon :class="{ 'animate-spin': loading }" class="h-4 w-4 mr-2" />
            {{ $t('common.refresh') }}
          </button>
          <button
            @click="openCreateModal"
            class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <PlusIcon class="h-4 w-4 mr-2" />
            {{ $t('platforms.addPlatform') }}
          </button>
        </div>
    
    <div class="grid grid-cols-1 gap-6 lg:grid-cols-2 relative">
      <LoadingOverlay :loading="loading" :text="$t('common.loading')" />
      <transition-group
        name="fade"
        tag="div"
        class="grid grid-cols-1 gap-6 lg:grid-cols-2 col-span-full"
      >
        <div
          v-for="platform in platforms"
          :key="platform.id"
          class="bg-white shadow rounded-lg overflow-hidden transition-opacity"
        >
        <!-- Platform Header -->
        <div class="px-6 py-4 bg-gradient-to-r from-blue-50 to-indigo-50 border-b border-gray-200">
          <div class="flex items-center justify-between">
            <div class="flex items-center">
              <CloudIcon class="h-6 w-6 text-blue-600 mr-2" />
              <h3 class="text-lg font-semibold text-gray-900">{{ platform.name }}</h3>
            </div>
            <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
              {{ platform.type.toUpperCase() }}
            </span>
          </div>
          <div class="mt-2 flex items-center text-sm text-gray-600">
            <ServerIcon class="h-4 w-4 mr-1" />
            <span>{{ platform.host }}:{{ platform.port || 443 }}</span>
            <span class="mx-2">•</span>
            <UserIcon class="h-4 w-4 mr-1" />
            <span>{{ platform.username }}</span>
            <span v-if="platform.region" class="mx-2">•</span>
            <span v-if="platform.region">{{ platform.region }}</span>
          </div>
        </div>
        
        <!-- Statistics -->
        <div v-if="platform.statistics" class="px-6 py-4">
          <h4 class="text-sm font-medium text-gray-700 mb-3 flex items-center">
            <ChartBarIcon class="h-4 w-4 mr-1" />
            {{ $t('platforms.resourceStats') }}
          </h4>
          <div class="grid grid-cols-2 gap-4">
            <div class="bg-blue-50 p-3 rounded-lg">
              <div class="flex items-center">
                <ServerIcon class="h-6 w-6 text-blue-600" />
                <div class="ml-2">
                  <p class="text-xs text-blue-600 font-medium">{{ $t('platforms.esxiHosts') }}</p>
                  <p class="text-xl font-bold text-blue-900">{{ platform.statistics.esxi_count || 0 }}</p>
                </div>
              </div>
            </div>
            <div class="bg-purple-50 p-3 rounded-lg">
              <div class="flex items-center">
                <CpuChipIcon class="h-6 w-6 text-purple-600" />
                <div class="ml-2">
                  <p class="text-xs text-purple-600 font-medium">{{ $t('platforms.vms') }}</p>
                  <p class="text-xl font-bold text-purple-900">{{ platform.statistics.vm_count || 0 }}</p>
                </div>
              </div>
            </div>
            <div class="bg-green-50 p-3 rounded-lg">
              <div class="flex items-center">
                <CpuChipIcon class="h-6 w-6 text-green-600" />
                <div class="ml-2">
                  <p class="text-xs text-green-600 font-medium">{{ $t('platforms.cpuCores') }}</p>
                  <p class="text-xl font-bold text-green-900">{{ platform.statistics.total_cpu_cores || 0 }}</p>
                </div>
              </div>
            </div>
            <div class="bg-yellow-50 p-3 rounded-lg">
              <div class="flex items-center">
                <Battery100Icon class="h-6 w-6 text-yellow-600" />
                <div class="ml-2">
                  <p class="text-xs text-yellow-600 font-medium">{{ $t('platforms.memoryGB') }}</p>
                  <p class="text-xl font-bold text-yellow-900">{{ platform.statistics.total_memory_gb || 0 }}</p>
                </div>
              </div>
            </div>
          </div>
          <div class="mt-3 bg-gray-50 p-3 rounded-lg">
            <div class="flex items-center">
              <CircleStackIcon class="h-5 w-5 text-gray-600" />
              <div class="ml-2">
                <p class="text-xs text-gray-600 font-medium">{{ $t('platforms.storageGB') }}</p>
                <p class="text-lg font-bold text-gray-900">{{ platform.statistics.total_storage_gb || 0 }}</p>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Actions -->
        <div class="px-6 py-4 bg-gray-50 border-t border-gray-200">
          <div class="flex flex-wrap gap-2">
            <button
              v-if="platform.id"
              @click="viewPlatform(platform.id)"
              class="inline-flex items-center px-3 py-1.5 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              <EyeIcon class="h-4 w-4 mr-1" />
              {{ $t('platforms.view') }}
            </button>
            <button
              @click="editPlatform(platform)"
              class="inline-flex items-center px-3 py-1.5 text-sm font-medium text-indigo-700 bg-indigo-50 border border-indigo-200 rounded-md hover:bg-indigo-100 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              <PencilIcon class="h-4 w-4 mr-1" />
              {{ $t('common.edit') }}
            </button>
            <button
              v-if="platform.id"
              @click="testPlatform(platform.id)"
              :disabled="testingPlatformId === platform.id"
              class="inline-flex items-center px-3 py-1.5 text-sm font-medium text-blue-700 bg-blue-50 border border-blue-200 rounded-md hover:bg-blue-100 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
            >
              <SignalIcon class="h-4 w-4 mr-1" />
              {{ testingPlatformId === platform.id ? $t('platforms.testing') : $t('platforms.testConnection') }}
            </button>
            <button
              v-if="platform.id"
              @click="syncPlatform(platform.id)"
              :disabled="syncingPlatformId === platform.id"
              class="inline-flex items-center px-3 py-1.5 text-sm font-medium text-white bg-green-600 border border-transparent rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50"
            >
              <ArrowPathIcon class="h-4 w-4 mr-1" />
              {{ syncingPlatformId === platform.id ? $t('platforms.syncing') : $t('platforms.syncResources') }}
            </button>
            <button
              @click="showSyncSettings(platform)"
              class="inline-flex items-center px-3 py-1.5 text-sm font-medium text-purple-700 bg-purple-50 border border-purple-200 rounded-md hover:bg-purple-100 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500"
            >
              <Cog6ToothIcon class="h-4 w-4 mr-1" />
              {{ $t('platforms.syncSettings') }}
            </button>
            <button
              v-if="platform.id"
              @click="deletePlatform(platform.id)"
              class="inline-flex items-center px-3 py-1.5 text-sm font-medium text-white bg-red-600 border border-transparent rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
            >
              <TrashIcon class="h-4 w-4 mr-1" />
              {{ $t('common.delete') }}
            </button>
          </div>
        </div>
        </div>
      </transition-group>
      <div v-if="platforms.length === 0 && !loading" class="col-span-full text-center py-12 text-gray-500">
        <CloudIcon class="h-16 w-16 mx-auto text-gray-300 mb-4" />
        <p class="text-lg font-medium">{{ $t('platforms.noPlatforms') }}</p>
        <p class="text-sm mt-1">{{ $t('platforms.addPlatformHint') }}</p>
      </div>
    </div>

    <!-- Create/Edit Platform Modal -->
    <Modal :open="showCreateModal" @close="closeCreateModal" :title="editingPlatformId ? $t('platforms.editPlatformTitle') : $t('platforms.addPlatformTitle')" max-width="lg">
      <form @submit.prevent="savePlatform" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700">{{ $t('platforms.platformName') }} *</label>
          <input
            v-model="platformForm.name"
            type="text"
            required
            class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700">{{ $t('platforms.platformType') }} *</label>
          <select
            v-model="platformForm.type"
            required
            class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="">{{ $t('hosts.pleaseSelect') }}</option>
            <option value="vmware">VMware</option>
            <option value="openstack">OpenStack</option>
            <option value="aliyun">{{ $t('platforms.aliyun') }}</option>
            <option value="huaweicloud">{{ $t('platforms.huaweicloud') }}</option>
          </select>
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700">{{ $t('platforms.host') }} *</label>
            <input
              v-model="platformForm.host"
              type="text"
              required
              class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700">{{ $t('platforms.port') }}</label>
            <input
              v-model.number="platformForm.port"
              type="number"
              class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700">{{ $t('platforms.username') }} *</label>
            <input
              v-model="platformForm.username"
              type="text"
              required
              class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700">
              {{ $t('platforms.password') }} {{ editingPlatformId ? `(${$t('platforms.passwordHint')})` : '*' }}
            </label>
            <input
              v-model="platformForm.password"
              type="password"
              :required="!editingPlatformId"
              :placeholder="editingPlatformId ? $t('platforms.passwordHint') : ''"
              class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700">{{ $t('platforms.region') }}</label>
          <input
            v-model="platformForm.region"
            type="text"
            class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          />
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
          @click="savePlatform"
          :disabled="saving"
          class="inline-flex w-full justify-center rounded-md bg-blue-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-blue-500 sm:ml-3 sm:w-auto disabled:opacity-50"
        >
          {{ saving ? $t('settings.saving') : $t('common.save') }}
        </button>
      </template>
    </Modal>

    <!-- Platform Details Modal -->
    <Modal :open="showDetailModal" @close="closeDetailModal" :title="$t('platforms.platformDetails')" max-width="lg">
      <div v-if="platformDetail" class="space-y-6">
        <!-- Basic Info -->
        <div>
          <h3 class="text-sm font-medium text-gray-700 mb-3">{{ $t('platforms.basicInfo') }}</h3>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="text-sm font-medium text-gray-500">{{ $t('platforms.platformName') }}</label>
              <p class="mt-1 text-sm text-gray-900">{{ platformDetail.name }}</p>
            </div>
            <div>
              <label class="text-sm font-medium text-gray-500">{{ $t('platforms.platformType') }}</label>
              <p class="mt-1 text-sm text-gray-900">{{ platformDetail.type.toUpperCase() }}</p>
            </div>
            <div>
              <label class="text-sm font-medium text-gray-500">{{ $t('platforms.host') }}</label>
              <p class="mt-1 text-sm text-gray-900">{{ platformDetail.host }}</p>
            </div>
            <div>
              <label class="text-sm font-medium text-gray-500">{{ $t('platforms.port') }}</label>
              <p class="mt-1 text-sm text-gray-900">{{ platformDetail.port || 443 }}</p>
            </div>
            <div>
              <label class="text-sm font-medium text-gray-500">{{ $t('platforms.username') }}</label>
              <p class="mt-1 text-sm text-gray-900">{{ platformDetail.username }}</p>
            </div>
            <div>
              <label class="text-sm font-medium text-gray-500">{{ $t('platforms.region') }}</label>
              <p class="mt-1 text-sm text-gray-900">{{ platformDetail.region || '-' }}</p>
            </div>
          </div>
        </div>
        
        <!-- Sync Result -->
        <div v-if="platformDetail.last_sync_result && platformDetail.last_sync_result.failed_items && platformDetail.last_sync_result.failed_items.length > 0">
          <h3 class="text-sm font-medium text-red-700 mb-3 flex items-center">
            <XCircleIcon class="h-4 w-4 mr-1" />
            {{ $t('platforms.syncFailedItems') }}
          </h3>
          <div class="bg-red-50 border border-red-200 rounded-lg p-4">
            <div class="max-h-48 overflow-y-auto">
              <table class="min-w-full divide-y divide-red-200">
                <thead class="bg-red-100">
                  <tr>
                    <th class="px-3 py-2 text-left text-xs font-medium text-red-800">{{ $t('platforms.type') }}</th>
                    <th class="px-3 py-2 text-left text-xs font-medium text-red-800">{{ $t('platforms.name') }}</th>
                    <th class="px-3 py-2 text-left text-xs font-medium text-red-800">{{ $t('hosts.ip') }}</th>
                    <th class="px-3 py-2 text-left text-xs font-medium text-red-800">{{ $t('platforms.error') }}</th>
                  </tr>
                </thead>
                <tbody class="bg-white divide-y divide-red-100">
                  <tr v-for="(item, idx) in platformDetail.last_sync_result.failed_items" :key="idx">
                    <td class="px-3 py-2 text-sm text-red-700">{{ item.type === 'esxi' ? $t('platforms.esxiHost') : $t('platforms.vm') }}</td>
                    <td class="px-3 py-2 text-sm text-red-700">{{ item.name }}</td>
                    <td class="px-3 py-2 text-sm text-red-700">{{ item.ip || '-' }}</td>
                    <td class="px-3 py-2 text-sm text-red-600">{{ item.error }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
        
        <!-- Statistics -->
        <div v-if="platformDetail.statistics">
          <h3 class="text-sm font-medium text-gray-700 mb-3">{{ $t('platforms.resourceStats') }}</h3>
          <div class="grid grid-cols-2 md:grid-cols-3 gap-4">
            <div class="bg-blue-50 p-4 rounded-lg">
              <div class="flex items-center">
                <ServerIcon class="h-8 w-8 text-blue-600" />
                <div class="ml-3">
                  <p class="text-xs text-blue-600 font-medium">{{ $t('platforms.esxiHosts') }}</p>
                  <p class="text-2xl font-bold text-blue-900">{{ platformDetail.statistics.esxi_count || 0 }}</p>
                </div>
              </div>
            </div>
            <div class="bg-purple-50 p-4 rounded-lg">
              <div class="flex items-center">
                <CpuChipIcon class="h-8 w-8 text-purple-600" />
                <div class="ml-3">
                  <p class="text-xs text-purple-600 font-medium">{{ $t('platforms.vms') }}</p>
                  <p class="text-2xl font-bold text-purple-900">{{ platformDetail.statistics.vm_count || 0 }}</p>
                </div>
              </div>
            </div>
            <div class="bg-green-50 p-4 rounded-lg">
              <div class="flex items-center">
                <CpuChipIcon class="h-8 w-8 text-green-600" />
                <div class="ml-3">
                  <p class="text-xs text-green-600 font-medium">{{ $t('platforms.cpuCores') }}</p>
                  <p class="text-2xl font-bold text-green-900">{{ platformDetail.statistics.total_cpu_cores || 0 }}</p>
                </div>
              </div>
            </div>
            <div class="bg-yellow-50 p-4 rounded-lg">
              <div class="flex items-center">
                <Battery100Icon class="h-8 w-8 text-yellow-600" />
                <div class="ml-3">
                  <p class="text-xs text-yellow-600 font-medium">{{ $t('platforms.memoryGB') }}</p>
                  <p class="text-2xl font-bold text-yellow-900">{{ platformDetail.statistics.total_memory_gb || 0 }}</p>
                </div>
              </div>
            </div>
            <div class="bg-indigo-50 p-4 rounded-lg">
              <div class="flex items-center">
                <CircleStackIcon class="h-8 w-8 text-indigo-600" />
                <div class="ml-3">
                  <p class="text-xs text-indigo-600 font-medium">{{ $t('platforms.storageGB') }}</p>
                  <p class="text-2xl font-bold text-indigo-900">{{ platformDetail.statistics.total_storage_gb || 0 }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <button
          type="button"
          @click="closeDetailModal"
          class="mt-3 inline-flex w-full justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 sm:mt-0 sm:w-auto"
        >
          {{ $t('common.close') }}
        </button>
      </template>
    </Modal>

    <!-- Sync Settings Modal -->
    <Modal :open="showSyncSettingsModal" @close="closeSyncSettingsModal" :title="$t('platforms.syncSettings')" max-width="md">
      <div v-if="syncSettingsPlatform" class="space-y-4">
        <div>
          <label class="flex items-center">
            <input
              v-model="syncSettings.auto_sync"
              type="checkbox"
              class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span class="ml-2 text-sm text-gray-700">{{ $t('platforms.autoSync') }}</span>
          </label>
          <p class="mt-1 text-xs text-gray-500">{{ $t('platforms.autoSyncHint') }}</p>
        </div>
        <div v-if="syncSettings.auto_sync">
          <label class="block text-sm font-medium text-gray-700">{{ $t('platforms.syncFrequency') }}</label>
          <select
            v-model="syncSettings.sync_frequency"
            class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="daily">{{ $t('platforms.daily') }}</option>
            <option value="weekly">{{ $t('platforms.weekly') }}</option>
            <option value="monthly">{{ $t('platforms.monthly') }}</option>
          </select>
        </div>
        <div v-if="syncSettings.auto_sync">
          <label class="block text-sm font-medium text-gray-700">{{ $t('platforms.syncTime') }}</label>
          <input
            v-model="syncSettings.sync_time"
            type="time"
            class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
      </div>
      <template #footer>
        <button
          type="button"
          @click="closeSyncSettingsModal"
          class="mt-3 inline-flex w-full justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 sm:mt-0 sm:w-auto"
        >
          {{ $t('common.cancel') }}
        </button>
        <button
          type="button"
          @click="saveSyncSettings"
          class="inline-flex w-full justify-center rounded-md bg-blue-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-blue-500 sm:ml-3 sm:w-auto"
        >
          {{ $t('common.save') }}
        </button>
      </template>
    </Modal>

    <!-- Confirm Modal -->
    <ConfirmModal
      :open="showConfirmModal"
      @close="showConfirmModal = false"
      @confirm="handleConfirm"
      :title="$t('platforms.confirmDelete')"
      :message="confirmMessage"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { platformsApi, type Platform } from '@/api/platforms'
import Modal from '@/components/Modal.vue'
import ConfirmModal from '@/components/ConfirmModal.vue'
import LoadingOverlay from '@/components/LoadingOverlay.vue'
import { useToastStore } from '@/stores/toast'
import { useI18n } from 'vue-i18n'
import {
  CloudIcon,
  PlusIcon,
  ServerIcon,
  UserIcon,
  ChartBarIcon,
  CpuChipIcon,
  Battery100Icon,
  CircleStackIcon,
  EyeIcon,
  PencilIcon,
  SignalIcon,
  Cog6ToothIcon,
  TrashIcon,
  ArrowPathIcon,
  XCircleIcon,
  } from '@heroicons/vue/24/outline'

const { t } = useI18n()
const toastStore = useToastStore()

const platforms = ref<Platform[]>([])
const loading = ref(false)
const showCreateModal = ref(false)
const showDetailModal = ref(false)
const platformForm = ref<Partial<Platform>>({})
const platformDetail = ref<Platform | null>(null)
const editingPlatformId = ref<number | null>(null)
const saving = ref(false)
const testingPlatformId = ref<number | null>(null)
const syncingPlatformId = ref<number | null>(null)
const showConfirmModal = ref(false)
const confirmAction = ref<(() => void) | null>(null)
const confirmMessage = ref('')
const showSyncSettingsModal = ref(false)
const syncSettingsPlatform = ref<Platform | null>(null)
const syncSettings = ref({
  auto_sync: false,
  sync_frequency: 'daily',
  sync_time: '02:00',
})

const loadPlatforms = async () => {
  loading.value = true
  try {
    const response: any = await platformsApi.getPlatforms()
    // API client interceptor returns response.data, so response is already { code: 200, data: [...] }
    let platformsData: Platform[] = []
    if (response && response.code === 200) {
      platformsData = response.data || []
    } else if (Array.isArray(response)) {
      platformsData = response
    } else if (response && response.data && Array.isArray(response.data)) {
      platformsData = response.data
    }
    
    platforms.value = platformsData
    
    // Load statistics for each platform (optional, can be done lazily)
    if (platforms.value.length > 0) {
      for (const platform of platforms.value) {
        if (platform.id) {
          try {
            const detailRes: any = await platformsApi.getPlatform(platform.id)
            if (detailRes && detailRes.code === 200 && detailRes.data?.statistics) {
              platform.statistics = detailRes.data.statistics
            }
          } catch (e) {
            // Ignore errors loading statistics - not critical
            console.warn(`Failed to load statistics for platform ${platform.id}:`, e)
          }
        }
      }
    }
  } catch (error: any) {
    console.error('Failed to load platforms:', error)
    toastStore.error(error.response?.data?.message || error.message || t('messages.loadFailed'))
  } finally {
    loading.value = false
  }
}

const openCreateModal = () => {
  platformForm.value = {
    port: 443,
  }
  editingPlatformId.value = null
  showCreateModal.value = true
}

const editPlatform = (platform: Platform) => {
  // Copy platform data but don't include password (for security)
  // User needs to re-enter password if they want to change it
  platformForm.value = {
    ...platform,
    password: '', // Clear password field - user must enter new password if changing
  }
  editingPlatformId.value = platform.id!
  showCreateModal.value = true
}

const closeCreateModal = () => {
  showCreateModal.value = false
  platformForm.value = {}
  editingPlatformId.value = null
}

const savePlatform = async () => {
  saving.value = true
  try {
    if (editingPlatformId.value) {
      // For updates, only send password if it's provided (not empty)
      const updateData = { ...platformForm.value }
      if (!updateData.password || updateData.password.trim() === '') {
        // Remove password field if empty - don't update password
        delete updateData.password
      }
      await platformsApi.updatePlatform(editingPlatformId.value, updateData)
      toastStore.success(t('platforms.updateSuccess'))
    } else {
      await platformsApi.createPlatform(platformForm.value as Platform)
      toastStore.success(t('platforms.createSuccess'))
    }
    closeCreateModal()
    loadPlatforms()
  } catch (error: any) {
    toastStore.error(error.response?.data?.message || t('messages.saveFailed'))
  } finally {
    saving.value = false
  }
}

const viewPlatform = async (id: number) => {
  try {
    const response: any = await platformsApi.getPlatform(id)
    if (response && response.code === 200) {
      platformDetail.value = response.data
      showDetailModal.value = true
    }
  } catch (error: any) {
    toastStore.error(error.response?.data?.message || t('messages.loadFailed'))
  }
}

const showSyncSettings = (platform: Platform) => {
  syncSettingsPlatform.value = platform
  // Load sync settings from platform extra_config
  const extraConfig = platform.extra_config || {}
  syncSettings.value = {
    auto_sync: extraConfig.auto_sync || false,
    sync_frequency: extraConfig.sync_frequency || 'daily',
    sync_time: extraConfig.sync_time || '02:00',
  }
  showSyncSettingsModal.value = true
}

const closeSyncSettingsModal = () => {
  showSyncSettingsModal.value = false
  syncSettingsPlatform.value = null
  syncSettings.value = {
    auto_sync: false,
    sync_frequency: 'daily',
    sync_time: '02:00',
  }
}

const saveSyncSettings = async () => {
  if (!syncSettingsPlatform.value) return
  
  try {
    const extraConfig = {
      ...(syncSettingsPlatform.value.extra_config || {}),
      ...syncSettings.value,
    }
    await platformsApi.updatePlatform(syncSettingsPlatform.value.id!, {
      extra_config: extraConfig,
    })
    toastStore.success(t('platforms.settingsSaved'))
    closeSyncSettingsModal()
    loadPlatforms()
  } catch (error: any) {
    toastStore.error(error.response?.data?.message || t('messages.saveFailed'))
  }
}

const closeDetailModal = () => {
  showDetailModal.value = false
  platformDetail.value = null
}

const testPlatform = async (id: number) => {
  testingPlatformId.value = id
  try {
    await platformsApi.testPlatform(id)
    toastStore.success(t('platforms.testSuccess'))
  } catch (error: any) {
    toastStore.error(error.response?.data?.message || t('platforms.testFailed'))
  } finally {
    testingPlatformId.value = null
  }
}

const syncPlatform = async (id: number) => {
  syncingPlatformId.value = id
  try {
    const response: any = await platformsApi.syncPlatform(id)
    if (response && response.code === 200 && response.data) {
      const result = response.data
      if (result.failed_items && result.failed_items.length > 0) {
        toastStore.warning(t('platforms.syncWithErrors', { count: result.failed_items.length }))
        // Store sync result in platform detail for display
        if (platformDetail.value && platformDetail.value.id === id) {
          platformDetail.value.last_sync_result = result
        }
      } else {
        toastStore.success(t('platforms.syncSuccess'))
      }
    } else {
      toastStore.success(t('platforms.syncSuccess'))
    }
    loadPlatforms()
  } catch (error: any) {
    toastStore.error(error.response?.data?.message || t('platforms.syncFailed'))
  } finally {
    syncingPlatformId.value = null
  }
}

const deletePlatform = async (id: number) => {
  confirmMessage.value = t('platforms.confirmDeleteMessage')
  confirmAction.value = async () => {
    try {
      await platformsApi.deletePlatform(id)
      toastStore.success(t('platforms.deleteSuccess'))
      loadPlatforms()
    } catch (error: any) {
      toastStore.error(error.response?.data?.message || t('messages.deleteFailed'))
    }
  }
  showConfirmModal.value = true
}

const handleConfirm = () => {
  if (confirmAction.value) {
    confirmAction.value()
  }
  showConfirmModal.value = false
  confirmAction.value = null
}

onMounted(() => {
  loadPlatforms()
})
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
