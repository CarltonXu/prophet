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
          @click="showAddRelationshipModal = true"
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

      <div class="bg-white shadow rounded-lg p-6">
        <h2 class="text-lg font-medium text-gray-900 mb-4">{{ $t('applications.hostList') }}</h2>
        <div v-if="hosts.length === 0" class="text-center py-4 text-gray-500">{{ $t('applications.noHosts') }}</div>
        <table v-else class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">{{ $t('hosts.ip') }}</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">{{ $t('hosts.hostname') }}</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">{{ $t('hosts.osType') }}</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">{{ $t('common.operation') }}</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="host in hosts" :key="host.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ host.ip }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ host.hostname || '-' }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ host.os_type || '-' }}</td>
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

      <div class="bg-white shadow rounded-lg p-6">
        <h2 class="text-lg font-medium text-gray-900 mb-4">{{ $t('applications.relationshipGraph') }}</h2>
        <div v-if="graphData.nodes.length === 0" class="text-center py-8 text-gray-500">
          {{ $t('applications.noRelationshipData') }}
        </div>
        <div v-else class="border border-gray-200 rounded-lg p-4 bg-gray-50 min-h-[400px]">
          <!-- Simple graph visualization using SVG -->
          <svg :width="graphWidth" :height="graphHeight" class="w-full h-full">
            <!-- Draw edges -->
            <line
              v-for="edge in graphData.edges"
              :key="`${edge.from}-${edge.to}`"
              :x1="getNodePosition(edge.from).x"
              :y1="getNodePosition(edge.from).y"
              :x2="getNodePosition(edge.to).x"
              :y2="getNodePosition(edge.to).y"
              stroke="#6B7280"
              stroke-width="2"
              marker-end="url(#arrowhead)"
            />
            <!-- Draw nodes -->
            <g v-for="node in graphData.nodes" :key="node.id">
              <circle
                :cx="node.x"
                :cy="node.y"
                :r="30"
                fill="#3B82F6"
                stroke="#1E40AF"
                stroke-width="2"
              />
              <text
                :x="node.x"
                :y="node.y"
                text-anchor="middle"
                dominant-baseline="middle"
                class="text-xs fill-white font-medium"
              >
                {{ node.label.substring(0, 8) }}
              </text>
            </g>
            <!-- Arrow marker definition -->
            <defs>
              <marker
                id="arrowhead"
                markerWidth="10"
                markerHeight="10"
                refX="9"
                refY="3"
                orient="auto"
              >
                <polygon points="0 0, 10 3, 0 6" fill="#6B7280" />
              </marker>
            </defs>
          </svg>
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
    <Modal :open="showAddRelationshipModal" @close="closeAddRelationshipModal" :title="$t('applications.addRelationship')" max-width="md">
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
          {{ adding ? $t('applications.adding') : $t('applications.add') }}
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
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { applicationsApi, type HostRelationship } from '@/api/applications'
import { hostsApi } from '@/api/hosts'
import Modal from '@/components/Modal.vue'
import ConfirmModal from '@/components/ConfirmModal.vue'
import { useToastStore } from '@/stores/toast'

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

const graphWidth = 800
const graphHeight = 400

const getNodePosition = (hostId: number) => {
  const node = graphData.value.nodes.find(n => n.id === hostId)
  return node ? { x: node.x, y: node.y } : { x: 0, y: 0 }
}

const loadApplication = async () => {
  const appId = parseInt(route.params.id as string)
  if (!appId) {
    router.push('/applications')
    return
  }

  loading.value = true
  try {
    const [appRes, graphRes] = await Promise.all([
      applicationsApi.getApplication(appId),
      applicationsApi.getGraph(appId).catch(() => ({ data: { nodes: [], edges: [] } })),
    ])
    application.value = appRes.data
    graphData.value = graphRes.data || { nodes: [], edges: [] }
    
    // Load hosts from application
    if (application.value.hosts) {
      hosts.value = application.value.hosts
    }
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

const removeHost = async (_hostId: number) => {
  confirmMessage.value = t('applications.confirmRemoveMessage')
  confirmAction.value = async () => {
    try {
      // Note: API might need a remove endpoint, for now we'll just reload
      toastStore.info(t('common.info'))
      loadApplication()
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
  relationshipForm.value = {}
}

const addRelationship = async () => {
  adding.value = true
  try {
    const appId = parseInt(route.params.id as string)
    await applicationsApi.createRelationship(appId, relationshipForm.value as HostRelationship)
    toastStore.success(t('applications.addRelationshipSuccess'))
    closeAddRelationshipModal()
    loadApplication()
  } catch (error: any) {
    toastStore.error(error.response?.data?.message || t('applications.addRelationshipFailed'))
  } finally {
    adding.value = false
  }
}

onMounted(() => {
  loadApplication()
  loadAvailableHosts()
})
</script>

