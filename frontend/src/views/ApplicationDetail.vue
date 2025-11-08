<template>
  <div class="px-4 py-6 sm:px-0">
    <div class="mb-4 flex items-center justify-between">
      <div class="flex items-center space-x-4">
        <button
          @click="$router.push('/applications')"
          class="text-gray-600 hover:text-gray-900 transition-colors"
        >
          ← {{ $t('common.back') }}
        </button>
        <h1 class="text-2xl font-bold text-gray-900">{{ application?.name || $t('applications.appDetail') }}</h1>
      </div>
      <div class="flex space-x-2">
        <button
          @click="showAddHostModal = true"
          class="px-4 py-2 bg-green-600 text-white rounded-md text-sm hover:bg-green-700 transition-colors"
        >
          {{ $t('applications.addHost') }}
        </button>
        <button
          @click="openAddRelationshipModal"
          class="px-4 py-2 bg-purple-600 text-white rounded-md text-sm hover:bg-purple-700 transition-colors"
        >
          {{ $t('applications.addRelationship') }}
        </button>
      </div>
    </div>

    <div v-if="loading" class="text-center py-8 text-gray-500">{{ $t('common.loading') }}</div>
    
    <div v-else-if="application" class="space-y-6">
      <div class="bg-white shadow rounded-lg p-6">
        <h2 class="text-lg font-medium text-gray-900 mb-4">{{ $t('applications.basicInfo') }}</h2>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="text-sm font-medium text-gray-500">{{ $t('applications.appName') }}</label>
            <p class="mt-1 text-sm text-gray-900">{{ application.name }}</p>
          </div>
          <div>
            <label class="text-sm font-medium text-gray-500">{{ $t('applications.description') }}</label>
            <p class="mt-1 text-sm text-gray-900">{{ application.description || '-' }}</p>
          </div>
        </div>
      </div>

      <div class="bg-white shadow rounded-lg p-6 space-y-4">
        <div class="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h2 class="text-lg font-medium text-gray-900">{{ $t('applications.hostList') }}</h2>
            <p class="text-sm text-gray-500">{{ $t('applications.hostListSubtitle') }}</p>
          </div>
          <div class="relative">
            <span class="absolute inset-y-0 left-3 flex items-center text-gray-400">
              <MagnifyingGlassIcon class="h-4 w-4" />
            </span>
            <input
              v-model="hostSearchTerm"
              type="text"
              :placeholder="$t('applications.hostSearchPlaceholder')"
              class="pl-9 pr-3 py-2 rounded-md border border-gray-300 shadow-sm text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
            />
          </div>
        </div>

        <div class="grid grid-cols-1 gap-3 sm:grid-cols-3">
          <div class="rounded-md border border-blue-100 bg-blue-50 p-3">
            <p class="text-xs font-semibold uppercase tracking-wide text-blue-600">{{ $t('applications.totalHosts') }}</p>
            <p class="mt-2 text-xl font-bold text-blue-900">{{ summaryStats.totalHosts }}</p>
          </div>
          <div class="rounded-md border border-emerald-100 bg-emerald-50 p-3">
            <p class="text-xs font-semibold uppercase tracking-wide text-emerald-600">{{ $t('applications.physicalHosts') }}</p>
            <p class="mt-2 text-xl font-bold text-emerald-900">{{ summaryStats.physicalHosts }}</p>
          </div>
          <div class="rounded-md border border-purple-100 bg-purple-50 p-3">
            <p class="text-xs font-semibold uppercase tracking-wide text-purple-600">{{ $t('applications.virtualHosts') }}</p>
            <p class="mt-2 text-xl font-bold text-purple-900">{{ summaryStats.virtualHosts }}</p>
          </div>
        </div>

        <div v-if="filteredHosts.length === 0" class="text-center py-8 text-gray-500">
          <ServerIcon class="h-12 w-12 mx-auto text-gray-300 mb-2" />
          <p>{{ hostSearchTerm ? $t('applications.noHostSearchResults') : $t('applications.noHosts') }}</p>
        </div>
        <table v-else class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th @click="setSortKey('ip')" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase cursor-pointer">
                {{ $t('hosts.ip') }}
              </th>
              <th @click="setSortKey('hostname')" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase cursor-pointer">
                {{ $t('hosts.hostname') }}
              </th>
              <th @click="setSortKey('os_type')" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase cursor-pointer">
                {{ $t('hosts.osType') }}
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">{{ $t('hosts.cpuInfo') }}</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">{{ $t('hosts.memory') }}</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">{{ $t('hosts.disk') }}</th>
              <th @click="setSortKey('device_type')" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase cursor-pointer">
                {{ $t('hosts.deviceType') }}
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">{{ $t('hosts.tags') }}</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">{{ $t('common.operation') }}</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="host in filteredHosts" :key="host.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ host.ip }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ host.hostname || '-' }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ host.os_type || '-' }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                <div class="flex flex-col">
                  <span>{{ host.cpu_info || '-' }}</span>
                  <span v-if="host.cpu_cores" class="text-xs text-gray-400">{{ $t('hosts.cpuCores') }}: {{ host.cpu_cores }}</span>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ formatMetric(host.memory_total) }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ formatMetric(host.disk_total_size) }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 capitalize">{{ host.device_type || '-' }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                <div class="flex flex-wrap gap-1">
                  <span
                    v-for="tag in getHostTags(host)"
                    :key="tag.id"
                    class="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium"
                    :style="tag.color ? { backgroundColor: tag.color + '20', color: tag.color } : {}"
                  >
                    {{ tag.name }}
                  </span>
                  <span v-if="getHostTags(host).length === 0" class="text-gray-400">{{ $t('applications.noTags') }}</span>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <button
                  @click="removeHost(host.id!)"
                  class="text-red-600 hover:text-red-900 transition-colors"
                >
                  {{ $t('common.delete') }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="bg-white shadow rounded-lg p-6 space-y-4">
        <div class="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h2 class="text-lg font-medium text-gray-900">{{ $t('applications.relationshipList') }}</h2>
            <p class="text-sm text-gray-500">{{ $t('applications.relationshipListSubtitle') }}</p>
          </div>
          <div class="relative">
            <span class="absolute inset-y-0 left-3 flex items-center text-gray-400">
              <MagnifyingGlassIcon class="h-4 w-4" />
            </span>
            <input
              v-model="relationshipSearchTerm"
              type="text"
              :placeholder="$t('applications.relationshipSearchPlaceholder')"
              class="pl-9 pr-3 py-2 rounded-md border border-gray-300 shadow-sm text-sm focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-colors"
            />
          </div>
        </div>
        <div v-if="filteredRelationships.length === 0" class="text-center py-6 text-gray-500">
          <ShareIcon class="h-12 w-12 mx-auto text-gray-300 mb-2" />
          <p>{{ relationshipSearchTerm ? $t('applications.noRelationshipSearchResults') : $t('applications.noRelationships') }}</p>
        </div>
        <table v-else class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">{{ $t('applications.sourceHost') }}</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">{{ $t('applications.targetHost') }}</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">{{ $t('applications.relationshipType') }}</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">{{ $t('applications.description') }}</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">{{ $t('common.operation') }}</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="relation in filteredRelationships" :key="relation.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{{ getHostLabel(relation.from_host_id) }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{{ getHostLabel(relation.to_host_id) }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 capitalize">{{ relation.relationship_type }}</td>
              <td class="px-6 py-4 text-sm text-gray-500">
                {{ relation.description || '-' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-3">
                <button
                  @click="editRelationship(relation)"
                  class="text-indigo-600 hover:text-indigo-900 transition-colors"
                >
                  {{ $t('common.edit') }}
                </button>
                <button
                  @click="deleteRelationship(relation)"
                  class="text-red-600 hover:text-red-900 transition-colors"
                >
                  {{ $t('common.delete') }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="bg-white shadow rounded-lg p-6">
        <h2 class="text-lg font-medium text-gray-900 mb-4">{{ $t('applications.relationshipGraph') }}</h2>
        <div v-if="graphData.nodes.length === 0" class="text-center py-8 text-gray-500">
          <ShareIcon class="h-12 w-12 mx-auto text-gray-300 mb-2" />
          <p>{{ $t('applications.noRelationshipData') }}</p>
        </div>
        <div v-else class="space-y-4">
          <div class="flex flex-wrap items-center justify-between gap-3">
            <div class="flex flex-wrap items-center gap-2">
              <button
                v-for="layout in ['force', 'hierarchical', 'grid']"
                :key="layout"
                @click="selectedLayout = layout as any"
                :class="[
                  'px-3 py-1.5 text-sm rounded-md border transition-colors',
                  selectedLayout === layout
                    ? 'bg-blue-600 text-white border-blue-600'
                    : 'bg-white text-gray-600 border-gray-300 hover:bg-gray-50'
                ]"
              >
                {{ $t(`applications.layout.${layout}`) }}
              </button>
            </div>
            <div class="flex items-center gap-3 text-xs text-gray-500">
              <div class="flex items-center gap-1">
                <span class="inline-block h-3 w-3 rounded-full bg-blue-500 border border-blue-700"></span>
                <span>{{ $t('applications.legendPhysical') }}</span>
              </div>
              <div class="flex items-center gap-1">
                <span class="inline-block h-3 w-3 rounded-full bg-emerald-500 border border-emerald-700"></span>
                <span>{{ $t('applications.legendVirtual') }}</span>
              </div>
              <div class="flex items-center gap-1">
                <span class="inline-block h-3 w-3 rounded-full bg-orange-500 border border-orange-700"></span>
                <span>{{ $t('applications.legendNetwork') }}</span>
              </div>
            </div>
          </div>
          <div ref="networkContainer" class="w-full h-[420px] border border-gray-200 rounded-lg bg-white"></div>
        </div>
      </div>
    </div>

    <!-- Add Host Modal -->
    <Modal :open="showAddHostModal" @close="closeAddHostModal" :title="$t('applications.addHost')" max-width="lg">
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700">{{ $t('applications.selectHost') }}</label>
          <div class="mt-2 max-h-60 overflow-y-auto border border-gray-300 rounded-md">
            <div
              v-for="host in availableHosts"
              :key="host.id"
              class="p-2 hover:bg-gray-50 border-b border-gray-100 last:border-b-0 transition-colors"
            >
              <label class="flex items-center">
                <input
                  type="checkbox"
                  :value="host.id"
                  v-model="selectedHostIds"
                  class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span class="ml-2 text-sm text-gray-900">{{ host.ip }} - {{ host.hostname || $t('applications.unknown') }}</span>
              </label>
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <button
          type="button"
          @click="closeAddHostModal"
          class="mt-3 inline-flex w-full justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 sm:mt-0 sm:w-auto transition-colors"
        >
          {{ $t('common.cancel') }}
        </button>
        <button
          type="button"
          @click="addHosts"
          :disabled="selectedHostIds.length === 0 || adding"
          class="inline-flex w-full justify-center rounded-md bg-blue-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-blue-500 sm:ml-3 sm:w-auto disabled:opacity-50 transition-colors"
        >
          {{ adding ? $t('applications.adding') : $t('applications.add') }}
        </button>
      </template>
    </Modal>

    <!-- Add Relationship Modal -->
    <Modal
      :open="showAddRelationshipModal"
      @close="closeAddRelationshipModal"
      :title="editingRelationshipId ? $t('applications.editRelationshipTitle') : $t('applications.addRelationshipTitle')"
      max-width="md"
    >
      <form @submit.prevent="addRelationship" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700">{{ $t('applications.sourceHost') }} *</label>
          <select
            v-model="relationshipForm.from_host_id"
            required
            class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 transition-colors"
          >
            <option value="">{{ $t('hosts.pleaseSelect') }}</option>
            <option v-for="host in hosts" :key="host.id" :value="host.id">
              {{ host.ip }} - {{ host.hostname || $t('applications.unknown') }}
            </option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700">{{ $t('applications.targetHost') }} *</label>
          <select
            v-model="relationshipForm.to_host_id"
            required
            class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 transition-colors"
          >
            <option value="">{{ $t('hosts.pleaseSelect') }}</option>
            <option v-for="host in hosts" :key="host.id" :value="host.id">
              {{ host.ip }} - {{ host.hostname || $t('applications.unknown') }}
            </option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700">{{ $t('applications.relationshipType') }} *</label>
          <select
            v-model="relationshipForm.relationship_type"
            required
            class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 transition-colors"
          >
            <option value="">{{ $t('hosts.pleaseSelect') }}</option>
            <option value="depends_on">{{ $t('applications.dependsOn') }}</option>
            <option value="connects_to">{{ $t('applications.connectsTo') }}</option>
            <option value="runs_on">{{ $t('applications.runsOn') }}</option>
            <option value="member">{{ $t('applications.member') }}</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700">{{ $t('applications.description') }}</label>
          <textarea
            v-model="relationshipForm.description"
            rows="2"
            class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 transition-colors"
          />
        </div>
      </form>
      <template #footer>
        <button
          type="button"
          @click="closeAddRelationshipModal"
          class="mt-3 inline-flex w-full justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 sm:mt-0 sm:w-auto transition-colors"
        >
          {{ $t('common.cancel') }}
        </button>
        <button
          type="button"
          @click="addRelationship"
          :disabled="adding"
          class="inline-flex w-full justify-center rounded-md bg-blue-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-blue-500 sm:ml-3 sm:w-auto disabled:opacity-50 transition-colors"
        >
          {{ adding ? $t('applications.adding') : (editingRelationshipId ? $t('applications.update') : $t('applications.add')) }}
        </button>
      </template>
    </Modal>

    <!-- Confirm Modal -->
    <ConfirmModal
      :open="showConfirmModal"
      @close="showConfirmModal = false"
      @confirm="handleConfirm"
      :title="$t('applications.confirmRemove')"
      :message="confirmMessage"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, computed, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { applicationsApi, type HostRelationship } from '@/api/applications'
import { hostsApi } from '@/api/hosts'
import Modal from '@/components/Modal.vue'
import ConfirmModal from '@/components/ConfirmModal.vue'
import { useToastStore } from '@/stores/toast'
import { ServerIcon, ShareIcon, MagnifyingGlassIcon } from '@heroicons/vue/24/outline'
import { Network } from 'vis-network'
import 'vis-network/styles/vis-network.css'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const toastStore = useToastStore()

const application = ref<any>(null)
const hosts = ref<any[]>([])
const availableHosts = ref<any[]>([])
const graphData = ref<{ nodes: any[], edges: any[] }>({ nodes: [], edges: [] })
const loading = ref(false)
const showAddHostModal = ref(false)
const showAddRelationshipModal = ref(false)
const selectedHostIds = ref<number[]>([])
const adding = ref(false)
const relationshipForm = ref<Partial<HostRelationship>>({})
const showConfirmModal = ref(false)
const confirmAction = ref<(() => void) | null>(null)
const confirmMessage = ref('')
const hostSearchTerm = ref('')
const sortKey = ref<'ip' | 'hostname' | 'os_type' | 'device_type'>('ip')
const sortOrder = ref<'asc' | 'desc'>('asc')
const relationships = ref<any[]>([])
const relationshipSearchTerm = ref('')
const editingRelationshipId = ref<number | null>(null)
const networkContainer = ref<HTMLDivElement | null>(null)
const networkInstance = ref<Network | null>(null)
const selectedLayout = ref<'force' | 'hierarchical' | 'grid'>('force')

interface HostTag {
  id?: number
  name?: string
  color?: string
}

const filteredHosts = computed(() => {
  const keyword = hostSearchTerm.value.trim().toLowerCase()
  let result = hosts.value.slice()
  if (keyword) {
    result = result.filter((host) => {
      const ip = host.ip?.toLowerCase() || ''
      const hostname = host.hostname?.toLowerCase() || ''
      const osType = host.os_type?.toLowerCase() || ''
      const tags: string[] = Array.isArray(host.tags)
        ? host.tags.map((t: HostTag) => t.name?.toLowerCase() || '')
        : []
      return (
        ip.includes(keyword) ||
        hostname.includes(keyword) ||
        osType.includes(keyword) ||
        tags.some((tag: string) => tag.includes(keyword))
      )
    })
  }
  result.sort((a, b) => {
    const aValue = (a[sortKey.value] ?? '').toString().toLowerCase()
    const bValue = (b[sortKey.value] ?? '').toString().toLowerCase()
    if (aValue < bValue) return sortOrder.value === 'asc' ? -1 : 1
    if (aValue > bValue) return sortOrder.value === 'asc' ? 1 : -1
    return 0
  })
  return result
})

const summaryStats = computed(() => ({
  totalHosts: hosts.value.length,
  physicalHosts: hosts.value.filter((host) => host.is_physical).length,
  virtualHosts: hosts.value.filter((host) => host.is_physical === false).length
}))

const filteredRelationships = computed(() => {
  const keyword = relationshipSearchTerm.value.trim().toLowerCase()
  if (!keyword) return relationships.value
  return relationships.value.filter((relation) => {
    const fromHost = getHostLabel(relation.from_host_id).toLowerCase()
    const toHost = getHostLabel(relation.to_host_id).toLowerCase()
    const type = relation.relationship_type?.toLowerCase() || ''
    const description = relation.description?.toLowerCase() || ''
    return (
      fromHost.includes(keyword) ||
      toHost.includes(keyword) ||
      type.includes(keyword) ||
      description.includes(keyword)
    )
  })
})

const setSortKey = (key: 'ip' | 'hostname' | 'os_type' | 'device_type') => {
  if (sortKey.value === key) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortKey.value = key
    sortOrder.value = 'asc'
  }
}

const formatMetric = (value?: number, suffix = 'GB') => {
  if (value === null || value === undefined) return '-'
  const rounded = Math.round((value + Number.EPSILON) * 100) / 100
  return `${rounded} ${suffix}`
}

const getHostTags = (host: any): HostTag[] => {
  if (!Array.isArray(host.tags) || host.tags.length === 0) return []
  return host.tags
}

const getHostLabel = (hostId: number) => {
  const host = hosts.value.find((item) => item.id === hostId)
  if (!host) return `#${hostId}`
  return host.hostname || host.ip || `#${hostId}`
}

const loadRelationships = async () => {
  try {
    const appId = parseInt(route.params.id as string)
    const response = await applicationsApi.getRelationships(appId)
    relationships.value = response.data || []
  } catch (error: any) {
    toastStore.error(error.response?.data?.message || t('applications.loadRelationshipsFailed'))
  }
}

const loadApplication = async () => {
  const appId = parseInt(route.params.id as string)
  if (!appId) {
    router.push('/applications')
    return
  }

  loading.value = true
  try {
    const [appRes, graphRes, relationshipRes] = await Promise.all([
      applicationsApi.getApplication(appId),
      applicationsApi.getGraph(appId).catch(() => ({ data: { nodes: [], edges: [] } })),
      applicationsApi.getRelationships(appId).catch(() => ({ data: [] }))
    ])
    application.value = appRes.data
    graphData.value = graphRes.data || { nodes: [], edges: [] }
    relationships.value = relationshipRes.data || []
    
    // Load hosts from application
    if (application.value.hosts) {
      hosts.value = application.value.hosts
    }
    await loadAvailableHosts()
    await nextTick()
    renderNetwork()
  } catch (error: any) {
    toastStore.error(error.response?.data?.message || t('applications.loadFailed'))
    router.push('/applications')
  } finally {
    loading.value = false
  }
}

const loadAvailableHosts = async () => {
  try {
    const response = await hostsApi.getHosts({ per_page: 1000 })
    const allHosts = response.data || []
    // Filter out hosts already in the application
    const hostIds = new Set(hosts.value.map(h => h.id))
    availableHosts.value = allHosts.filter((h: any) => !hostIds.has(h.id))
  } catch (error: any) {
    toastStore.error(error.response?.data?.message || t('applications.loadHostsFailed'))
  }
}

const closeAddHostModal = () => {
  showAddHostModal.value = false
  selectedHostIds.value = []
}

const addHosts = async () => {
  if (selectedHostIds.value.length === 0) return
  adding.value = true
  try {
    const appId = parseInt(route.params.id as string)
    await applicationsApi.addHosts(appId, selectedHostIds.value)
    toastStore.success(t('applications.addHostSuccess'))
    closeAddHostModal()
    loadApplication()
  } catch (error: any) {
    toastStore.error(error.response?.data?.message || t('applications.addHostFailed'))
  } finally {
    adding.value = false
  }
}

const removeHost = async (hostId: number) => {
  confirmMessage.value = t('applications.confirmRemoveMessage')
  confirmAction.value = async () => {
    try {
      const appId = parseInt(route.params.id as string)
      await applicationsApi.removeHost(appId, hostId)
      toastStore.success(t('applications.removeHostSuccess'))
      await loadApplication()
    } catch (error: any) {
      toastStore.error(error.response?.data?.message || t('applications.removeHostFailed'))
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

const closeAddRelationshipModal = () => {
  showAddRelationshipModal.value = false
  editingRelationshipId.value = null
  relationshipForm.value = {}
}

const addRelationship = async () => {
  adding.value = true
  try {
    const appId = parseInt(route.params.id as string)
    if (editingRelationshipId.value) {
      await applicationsApi.updateRelationship(appId, editingRelationshipId.value, relationshipForm.value as Partial<HostRelationship>)
      toastStore.success(t('applications.updateRelationshipSuccess'))
    } else {
    await applicationsApi.createRelationship(appId, relationshipForm.value as HostRelationship)
    toastStore.success(t('applications.addRelationshipSuccess'))
    }
    closeAddRelationshipModal()
    await Promise.all([loadApplication(), loadRelationships()])
  } catch (error: any) {
    const messageKey = editingRelationshipId.value ? 'applications.updateRelationshipFailed' : 'applications.addRelationshipFailed'
    toastStore.error(error.response?.data?.message || t(messageKey))
  } finally {
    adding.value = false
  }
}

const openAddRelationshipModal = () => {
  editingRelationshipId.value = null
  relationshipForm.value = {}
  showAddRelationshipModal.value = true
}

const editRelationship = (relationship: any) => {
  relationshipForm.value = {
    from_host_id: relationship.from_host_id,
    to_host_id: relationship.to_host_id,
    relationship_type: relationship.relationship_type,
    description: relationship.description
  }
  editingRelationshipId.value = relationship.id
  showAddRelationshipModal.value = true
}

const deleteRelationship = (relationship: any) => {
  confirmMessage.value = t('applications.confirmRelationshipDelete')
  confirmAction.value = async () => {
    try {
      const appId = parseInt(route.params.id as string)
      await applicationsApi.deleteRelationship(appId, relationship.id)
      toastStore.success(t('applications.deleteRelationshipSuccess'))
      await loadRelationships()
      await loadApplication()
    } catch (error: any) {
      toastStore.error(error.response?.data?.message || t('applications.deleteRelationshipFailed'))
    }
  }
  showConfirmModal.value = true
}

onMounted(() => {
  loadApplication()
  nextTick(() => renderNetwork())
})

watch(showAddHostModal, (opened) => {
  if (opened) {
  loadAvailableHosts()
  }
})

watch(
  () => graphData.value,
  () => {
    renderNetwork()
  },
  { deep: true }
)

watch(selectedLayout, () => {
  renderNetwork()
})

const buildNetworkData = () => {
  const nodeColors: Record<string, { background: string; border: string }> = {
    host: { background: '#2563EB', border: '#1D4ED8' },
    server: { background: '#10B981', border: '#047857' },
    network_device: { background: '#F97316', border: '#EA580C' },
  }
  
  const nodes = graphData.value.nodes.map((node: any) => {
    const color = nodeColors[node.group || 'host'] || nodeColors.host
    return {
      id: node.id,
      label: node.label,
      title: node.title,
      shape: 'dot',
      size: node.is_physical ? 24 : 18,
      color: {
        background: color.background,
        border: color.border,
        highlight: {
          background: '#FACC15',
          border: '#CA8A04'
        }
      },
      font: {
        color: '#ffffff',
        strokeWidth: 1,
        strokeColor: '#1F2937'
      }
    }
  })
  
  const edges = graphData.value.edges.map((edge: any) => ({
    id: edge.id,
    from: edge.from,
    to: edge.to,
    label: edge.label,
    title: edge.title,
    color: { color: edge.color || '#6B7280' },
    arrows: edge.arrows || 'to',
    font: { align: 'top', color: '#374151' },
    smooth: true
  }))
  
  return { nodes, edges }
}

const getNetworkOptions = (layout: 'force' | 'hierarchical' | 'grid') => {
  const baseOptions = {
    interaction: {
      hover: true,
      zoomView: true,
      dragView: true
    },
    physics: {
      enabled: layout === 'force',
      stabilization: { iterations: 200 }
    },
    layout: {
      improvedLayout: true
    },
    edges: {
      smooth: {
        type: 'dynamic'
      }
    }
  } as any
  
  if (layout === 'hierarchical') {
    baseOptions.layout = {
      hierarchical: {
        direction: 'LR',
        sortMethod: 'hubsize',
        levelSeparation: 180,
        nodeSpacing: 150
      }
    }
    baseOptions.physics = { enabled: false }
  }
  
  if (layout === 'grid') {
    baseOptions.physics = { enabled: false }
    baseOptions.layout = { randomSeed: 42 }
  }
  
  return baseOptions
}

const renderNetwork = () => {
  if (!networkContainer.value || graphData.value.nodes.length === 0) {
    if (networkInstance.value) {
      networkInstance.value.destroy()
      networkInstance.value = null
    }
    return
  }
  
  const data = buildNetworkData()
  const options = getNetworkOptions(selectedLayout.value)
  
  try {
    if (networkInstance.value) {
      networkInstance.value.setData(data)
      networkInstance.value.setOptions(options)
    } else {
      networkInstance.value = new Network(networkContainer.value, data, options)
    }
  } catch (error) {
    console.error('Failed to render network', error)
  }
}

onBeforeUnmount(() => {
  if (networkInstance.value) {
    networkInstance.value.destroy()
    networkInstance.value = null
  }
})
</script>

