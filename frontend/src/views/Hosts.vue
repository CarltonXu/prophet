<template>
  <div class="px-4 py-6 sm:px-0">
    <div class="mb-4 flex justify-between items-center">
      <div>
        <h1 class="text-2xl font-bold text-gray-900 flex items-center">
          <ServerIcon class="h-7 w-7 mr-2 text-gray-700" />
          {{ $t('hosts.title') }}
        </h1>
        <p class="mt-1 text-sm text-gray-500">{{ $t('hosts.subtitle') }}</p>
      </div>
      <div class="flex flex-wrap items-center gap-2">
        <!-- View Toggle -->
        <div class="flex items-center border border-gray-300 rounded-md overflow-hidden">
          <button
            @click="viewMode = 'list'"
            :class="viewMode === 'list' ? 'bg-blue-600 text-white' : 'bg-white text-gray-700 hover:bg-gray-50'"
            class="px-3 py-2 text-sm font-medium focus:outline-none focus:ring-2 focus:ring-blue-500"
            :title="$t('hosts.listView')"
          >
            <Bars3Icon class="h-4 w-4" />
          </button>
          <button
            @click="viewMode = 'tree'"
            :class="viewMode === 'tree' ? 'bg-blue-600 text-white' : 'bg-white text-gray-700 hover:bg-gray-50'"
            class="px-3 py-2 text-sm font-medium focus:outline-none focus:ring-2 focus:ring-blue-500 border-l border-gray-300"
            :title="$t('hosts.treeView')"
          >
            <Squares2X2Icon class="h-4 w-4" />
          </button>
        </div>
        
        <!-- Search -->
        <div class="relative flex-1 min-w-[200px]">
          <MagnifyingGlassIcon class="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
          <input
            v-model="searchQuery"
            type="text"
            :placeholder="$t('hosts.searchPlaceholder')"
            class="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            @input="debouncedSearch"
          />
        </div>
        
        <!-- Primary Actions -->
        <div class="flex items-center gap-2">
          <button
            @click="loadHosts(1)"
            :disabled="loading"
            class="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            :title="$t('common.refresh')"
          >
            <ArrowPathIcon :class="{ 'animate-spin': loading }" class="h-4 w-4" />
          </button>
          
          <button
            @click="openCreateModal"
            class="inline-flex items-center px-3 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
            :title="$t('hosts.addHost')"
          >
            <PlusIcon class="h-4 w-4" />
          </button>
          
          <!-- Batch Actions Menu (when hosts selected) -->
          <div v-if="selectedHosts.length > 0" class="relative">
            <Menu as="div" class="relative inline-block text-left">
              <MenuButton class="inline-flex items-center px-3 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500">
                <span class="mr-2">{{ $t('common.batchOperation') }} ({{ selectedHosts.length }})</span>
                <ChevronDownIcon class="h-4 w-4" />
              </MenuButton>
              <transition
                enter-active-class="transition ease-out duration-100"
                enter-from-class="transform opacity-0 scale-95"
                enter-to-class="transform opacity-100 scale-100"
                leave-active-class="transition ease-in duration-75"
                leave-from-class="transform opacity-100 scale-100"
                leave-to-class="transform opacity-0 scale-95"
              >
                <MenuItems class="absolute right-0 z-10 mt-2 w-56 origin-top-right rounded-md bg-white shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none">
                  <div class="py-1">
                    <MenuItem v-slot="{ active }">
                      <button
                        @click="openBatchCredentialsModal"
                        :class="[active ? 'bg-gray-100' : '', 'flex items-center w-full px-4 py-2 text-sm text-gray-700']"
                      >
                        <PencilIcon class="h-4 w-4 mr-3 text-gray-400" />
                        {{ $t('hosts.batchUpdateCredentials') }}
                      </button>
                    </MenuItem>
                    <MenuItem v-slot="{ active }">
                      <button
                        @click="handleBatchCollect"
                        :class="[active ? 'bg-gray-100' : '', 'flex items-center w-full px-4 py-2 text-sm text-gray-700']"
                      >
                        <CpuChipIcon class="h-4 w-4 mr-3 text-gray-400" />
                        {{ $t('hosts.batchCollect') }}
                      </button>
                    </MenuItem>
                  </div>
                </MenuItems>
              </transition>
            </Menu>
          </div>
          
          <!-- More Actions Menu -->
          <Menu as="div" class="relative inline-block text-left">
            <MenuButton class="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
              <EllipsisVerticalIcon class="h-5 w-5" />
            </MenuButton>
            <transition
              enter-active-class="transition ease-out duration-100"
              enter-from-class="transform opacity-0 scale-95"
              enter-to-class="transform opacity-100 scale-100"
              leave-active-class="transition ease-in duration-75"
              leave-from-class="transform opacity-100 scale-100"
              leave-to-class="transform opacity-0 scale-95"
            >
              <MenuItems class="absolute right-0 z-10 mt-2 w-56 origin-top-right rounded-md bg-white shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none">
                <div class="py-1">
                  <MenuItem v-slot="{ active }">
                    <button
                      @click="handleExportCSV"
                      :class="[active ? 'bg-gray-100' : '', 'flex items-center w-full px-4 py-2 text-sm text-gray-700']"
                    >
                      <ArrowDownTrayIcon class="h-4 w-4 mr-3 text-gray-400" />
                      {{ $t('hosts.exportCSV') }}
                    </button>
                  </MenuItem>
                  <MenuItem v-slot="{ active }">
                    <button
                      @click="showImportModal = true"
                      :class="[active ? 'bg-gray-100' : '', 'flex items-center w-full px-4 py-2 text-sm text-gray-700']"
                    >
                      <ArrowUpTrayIcon class="h-4 w-4 mr-3 text-gray-400" />
                      {{ $t('hosts.importCSV') }}
                    </button>
                  </MenuItem>
                </div>
              </MenuItems>
            </transition>
          </Menu>
        </div>
      </div>
    </div>
    
    <!-- Tree View -->
    <div v-if="viewMode === 'tree'" class="bg-white shadow sm:rounded-md overflow-hidden relative">
      <LoadingOverlay :loading="loadingTree" :text="$t('common.loading')" />
      <div v-if="!loadingTree && treeData.length === 0" class="text-center py-8 text-gray-500">
        {{ $t('hosts.noPlatformHosts') }}
      </div>
      <div v-else-if="!loadingTree" class="overflow-y-auto max-h-[calc(100vh-300px)] p-4">
        <div v-for="platform in treeData" :key="platform.platform_id" class="mb-6">
          <!-- Platform Level -->
          <div class="flex items-center mb-2 p-3 bg-blue-50 rounded-lg border border-blue-200">
            <CloudIcon class="h-5 w-5 mr-2 text-blue-600" />
            <div class="flex-1">
              <h3 class="text-sm font-semibold text-blue-900">{{ platform.platform_name }}</h3>
              <p class="text-xs text-blue-600">{{ platform.platform_type.toUpperCase() }}</p>
            </div>
            <span class="text-xs text-blue-600">
              {{ platform.esxi_hosts.reduce((sum: number, esxi: any) => sum + esxi.vms.length, 0) }}{{ $t('hosts.vmCount') }}
            </span>
          </div>
          
          <!-- ESXi Hosts Level -->
          <div v-for="esxi in platform.esxi_hosts" :key="esxi.esxi_name" class="ml-4 mb-3">
            <div class="flex items-center mb-1 p-2 bg-gray-50 rounded border border-gray-200">
              <ServerIcon class="h-4 w-4 mr-2 text-gray-600" />
              <div class="flex-1">
                <h4 class="text-sm font-medium text-gray-900">{{ esxi.esxi_name }}</h4>
                <p v-if="esxi.esxi_ip" class="text-xs text-gray-500">{{ esxi.esxi_ip }}</p>
              </div>
              <span class="text-xs text-gray-600">{{ esxi.vms.length }}{{ $t('hosts.vmCount') }}</span>
            </div>
            
            <!-- VMs Level -->
            <div class="ml-6 space-y-1">
              <div
                v-for="vm in esxi.vms"
                :key="vm.id"
                class="flex items-center p-2 hover:bg-gray-50 rounded border border-gray-100 cursor-pointer transition-colors"
                :class="{ 'bg-blue-50 border-blue-200': selectedHosts.includes(vm.id!) }"
                @click.stop="toggleHostSelection(vm.id!)"
              >
                <input
                  type="checkbox"
                  :checked="selectedHosts.includes(vm.id!)"
                  @click.stop="toggleHostSelection(vm.id!)"
                  class="rounded border-gray-300 text-blue-600 focus:ring-blue-500 mr-3"
                />
                <div class="flex-1 min-w-0">
                  <div class="flex items-center space-x-2">
                    <span class="text-sm font-medium text-gray-900">{{ vm.ip }}</span>
                    <span v-if="vm.hostname" class="text-sm text-gray-500">({{ vm.hostname }})</span>
                  </div>
                  <div class="flex items-center space-x-4 mt-1 text-xs text-gray-500">
                    <span v-if="vm.os_type">{{ vm.os_type }}</span>
                    <span v-if="vm.cpu_cores">{{ vm.cpu_cores }}{{ $t('hosts.cores') }}</span>
                    <span v-if="vm.memory_total">{{ formatBytes(vm.memory_total * 1024 * 1024, 'GB') }}</span>
                  </div>
                </div>
                <div class="flex items-center space-x-1">
                  <button
                    v-if="vm.id"
                    @click.stop="viewHost(vm.id)"
                    class="text-blue-600 hover:text-blue-900 p-1 rounded hover:bg-blue-50"
                    :title="$t('hosts.viewDetails')"
                  >
                    <EyeIcon class="h-4 w-4" />
                  </button>
                  <button
                    @click.stop="editHost(vm)"
                    class="text-indigo-600 hover:text-indigo-900 p-1 rounded hover:bg-indigo-50"
                    :title="$t('common.edit')"
                  >
                    <PencilIcon class="h-4 w-4" />
                  </button>
                  <button
                    v-if="vm.id"
                    @click.stop="collectHost(vm.id)"
                    :disabled="vm.collection_status === 'collecting'"
                    class="text-green-600 hover:text-green-900 p-1 rounded hover:bg-green-50 disabled:opacity-50 disabled:cursor-not-allowed"
                    :title="$t('hosts.collect')"
                  >
                    <CpuChipIcon class="h-4 w-4" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- List View -->
    <div v-else class="bg-white shadow sm:rounded-md overflow-hidden relative">
      <LoadingOverlay :loading="loading" :text="$t('common.loading')" />
      <div class="overflow-x-auto max-h-[calc(100vh-300px)] overflow-y-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50 sticky top-0 z-20">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider sticky left-0 bg-gray-50 z-10">
                <input
                  type="checkbox"
                  :checked="allSelected"
                  @change="toggleSelectAll"
                  class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
              </th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap">{{ $t('hosts.ip') }}</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap">{{ $t('hosts.hostname') }}</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap">{{ $t('hosts.osType') }}</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap">{{ $t('hosts.osVersion') }}</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap">{{ $t('hosts.deviceType') }}</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap">{{ $t('hosts.cpuCores') }}</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap">{{ $t('hosts.memory') }}</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap">{{ $t('hosts.disk') }}</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap">{{ $t('hosts.collectionStatus') }}</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap">{{ $t('hosts.source') }}</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap">{{ $t('hosts.tags') }}</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap sticky right-0 bg-gray-50 z-10">{{ $t('common.operation') }}</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-if="!loading && hosts.length === 0" class="text-center py-8">
              <td colspan="13" class="px-4 py-4 text-gray-500">{{ $t('hosts.noHosts') }}</td>
            </tr>
            <tr 
              v-else 
              v-for="host in hosts" 
              :key="host.id" 
              class="hover:bg-gray-50 group cursor-pointer transition-colors"
              :class="{ 'bg-blue-50 hover:bg-blue-100': selectedHosts.includes(host.id!) }"
              @click="toggleHostSelection(host.id!)"
            >
              <td class="px-4 py-4 whitespace-nowrap sticky left-0 bg-white group-hover:bg-gray-50 z-10 transition-colors"
                  :class="{ 'bg-blue-50 group-hover:bg-blue-100': selectedHosts.includes(host.id!) }"
                  @click.stop
              >
                <input
                  type="checkbox"
                  :value="host.id"
                  v-model="selectedHosts"
                  class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
              </td>
              <td class="px-4 py-4 whitespace-nowrap text-sm text-gray-900 font-medium">{{ host.ip }}</td>
              <td class="px-4 py-4 whitespace-nowrap text-sm text-gray-500">{{ host.hostname || '-' }}</td>
              <td class="px-4 py-4 whitespace-nowrap text-sm text-gray-500">
                <span class="capitalize">{{ host.os_type || '-' }}</span>
              </td>
              <td class="px-4 py-4 whitespace-nowrap text-sm text-gray-500">{{ host.os_version || '-' }}</td>
              <td class="px-4 py-4 whitespace-nowrap text-sm text-gray-500">
                <span class="inline-flex items-center">
                  <ComputerDesktopIcon v-if="host.is_physical" class="h-4 w-4 mr-1 text-gray-400" />
                  <CloudIcon v-else class="h-4 w-4 mr-1 text-gray-400" />
                  {{ host.is_physical ? $t('hosts.physical') : $t('hosts.virtual') }}
                </span>
              </td>
              <td class="px-4 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ host.cpu_cores ? `${host.cpu_cores}${$t('hosts.cores')}` : '-' }}
              </td>
              <td class="px-4 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ host.memory_total ? formatBytes(host.memory_total * 1024 * 1024, 'GB') : '-' }}
              </td>
              <td class="px-4 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ host.disk_total_size ? formatBytes(host.disk_total_size * 1024 * 1024, 'GB') : '-' }}
              </td>
              <td class="px-4 py-4 whitespace-nowrap text-sm">
                <span
                  :class="getCollectionStatusClass(host.collection_status)"
                  class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                >
                  <component
                    :is="getCollectionStatusIcon(host.collection_status)"
                    class="h-3.5 w-3.5 mr-1"
                  />
                  {{ getCollectionStatusText(host.collection_status) }}
                </span>
              </td>
              <td class="px-4 py-4 whitespace-nowrap text-sm text-gray-500">
                <span class="inline-flex items-center">
                  <component
                    :is="getSourceIcon(host.source)"
                    class="h-4 w-4 mr-1"
                    :class="getSourceIconColor(host.source)"
                  />
                  {{ getSourceText(host.source) }}
                </span>
              </td>
              <td class="px-4 py-4 whitespace-nowrap text-sm">
                <div class="flex flex-wrap gap-1">
                  <span
                    v-for="tag in host.tags"
                    :key="tag.id"
                    class="inline-flex items-center px-2 py-1 text-xs font-medium rounded text-white"
                    :style="{ backgroundColor: tag.color || '#6B7280' }"
                  >
                    {{ tag.name }}
                  </span>
                </div>
              </td>
              <td class="px-4 py-4 whitespace-nowrap text-sm font-medium sticky right-0 bg-white group-hover:bg-gray-50 z-10 transition-colors"
                  :class="{ 'bg-blue-50 group-hover:bg-blue-100': selectedHosts.includes(host.id!) }"
                  @click.stop
              >
                <div class="flex items-center space-x-1">
                  <button
                    v-if="host.id"
                    @click="viewHost(host.id)"
                    class="text-blue-600 hover:text-blue-900 p-1 rounded hover:bg-blue-50"
                    :title="$t('hosts.viewDetails')"
                  >
                    <EyeIcon class="h-5 w-5" />
                  </button>
                  <button
                    @click="editHost(host)"
                    class="text-indigo-600 hover:text-indigo-900 p-1 rounded hover:bg-indigo-50"
                    :title="$t('common.edit')"
                  >
                    <PencilIcon class="h-5 w-5" />
                  </button>
                  <button
                    v-if="host.id"
                    @click="collectHost(host.id)"
                    :disabled="host.collection_status === 'collecting'"
                    class="text-green-600 hover:text-green-900 p-1 rounded hover:bg-green-50 disabled:opacity-50 disabled:cursor-not-allowed"
                    :title="$t('hosts.collect')"
                  >
                    <CpuChipIcon class="h-5 w-5" />
                  </button>
                  <button
                    v-if="host.id"
                    @click="deleteHost(host.id)"
                    class="text-red-600 hover:text-red-900 p-1 rounded hover:bg-red-50"
                    :title="$t('common.delete')"
                  >
                    <TrashIcon class="h-5 w-5" />
                  </button>
                </div>
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
              @change="loadHosts(1)"
              class="px-2 py-1 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            >
              <option :value="10">10</option>
              <option :value="20">20</option>
              <option :value="50">50</option>
              <option :value="100">100</option>
            </select>
          </div>
          <p class="text-sm text-gray-700">
            {{ $t('common.page') }} <span class="font-medium">{{ (pagination.page - 1) * pagination.per_page + 1 }}</span>
            {{ $t('common.of') }} <span class="font-medium">{{ Math.min(pagination.page * pagination.per_page, pagination.total) }}</span>
            {{ $t('common.total') }} <span class="font-medium">{{ pagination.total }}</span> {{ $t('common.items') }}
          </p>
        </div>
        <div class="flex items-center space-x-2">
          <button
            @click="loadHosts(pagination.page - 1)"
            :disabled="pagination.page <= 1"
            class="relative inline-flex items-center px-3 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ $t('common.previous') }}
          </button>
          <span class="text-sm text-gray-700">
            {{ $t('common.page') }} {{ pagination.page }} {{ $t('common.of') }} {{ pagination.pages }}
          </span>
          <button
            @click="loadHosts(pagination.page + 1)"
            :disabled="pagination.page >= pagination.pages"
            class="relative inline-flex items-center px-3 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ $t('common.next') }}
          </button>
        </div>
      </div>
    </div>

    <!-- Create/Edit Host Modal -->
    <Modal :open="showCreateModal" @close="closeCreateModal" :title="editingHostId ? $t('hosts.editHostTitle') : $t('hosts.addHostTitle')" max-width="lg">
      <form @submit.prevent="saveHost" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700">{{ $t('hosts.ip') }} *</label>
          <input
            v-model="hostForm.ip"
            type="text"
            required
            class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700">{{ $t('hosts.hostname') }}</label>
          <input
            v-model="hostForm.hostname"
            type="text"
            class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700">{{ $t('hosts.osType') }}</label>
            <select
              v-model="hostForm.os_type"
              class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">{{ $t('hosts.pleaseSelect') }}</option>
              <option value="linux">Linux</option>
              <option value="windows">Windows</option>
              <option value="vmware">VMware</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700">{{ $t('hosts.deviceType') }}</label>
            <select
              v-model="hostForm.device_type"
              class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">{{ $t('hosts.pleaseSelect') }}</option>
              <option value="server">{{ $t('hosts.server') }}</option>
              <option value="network">{{ $t('hosts.networkDevice') }}</option>
              <option value="storage">{{ $t('hosts.storageDevice') }}</option>
            </select>
          </div>
        </div>
        <div>
          <label class="flex items-center">
            <input
              v-model="hostForm.is_physical"
              type="checkbox"
              class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span class="ml-2 text-sm text-gray-700">{{ $t('hosts.physical') }}</span>
          </label>
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
          @click="saveHost"
          :disabled="saving"
          class="inline-flex w-full justify-center rounded-md bg-blue-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-blue-500 sm:ml-3 sm:w-auto disabled:opacity-50"
        >
          {{ saving ? $t('hosts.saving') : $t('common.save') }}
        </button>
      </template>
    </Modal>

    <!-- Host Details Modal -->
    <Modal :open="showDetailModal" @close="closeDetailModal" :title="$t('hosts.hostDetails')" max-width="2xl">
      <div v-if="hostDetail" class="space-y-4">
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="text-sm font-medium text-gray-500">{{ $t('hosts.ipAddress') }}</label>
            <p class="mt-1 text-sm text-gray-900">{{ hostDetail.ip }}</p>
          </div>
          <div>
            <label class="text-sm font-medium text-gray-500">{{ $t('hosts.hostname') }}</label>
            <p class="mt-1 text-sm text-gray-900">{{ hostDetail.hostname || '-' }}</p>
          </div>
          <div>
            <label class="text-sm font-medium text-gray-500">{{ $t('hosts.macAddress') }}</label>
            <p class="mt-1 text-sm text-gray-900">{{ hostDetail.mac || '-' }}</p>
          </div>
          <div>
            <label class="text-sm font-medium text-gray-500">{{ $t('hosts.osType') }}</label>
            <p class="mt-1 text-sm text-gray-900">{{ hostDetail.os_type || '-' }}</p>
          </div>
          <div>
            <label class="text-sm font-medium text-gray-500">{{ $t('hosts.osVersion') }}</label>
            <p class="mt-1 text-sm text-gray-900">{{ hostDetail.os_version || '-' }}</p>
          </div>
          <div>
            <label class="text-sm font-medium text-gray-500">{{ $t('hosts.deviceType') }}</label>
            <p class="mt-1 text-sm text-gray-900">{{ hostDetail.device_type || '-' }}</p>
          </div>
          <div>
            <label class="text-sm font-medium text-gray-500">{{ $t('hosts.cpuInfo') }}</label>
            <p class="mt-1 text-sm text-gray-900">{{ hostDetail.cpu_info || '-' }}</p>
          </div>
          <div>
            <label class="text-sm font-medium text-gray-500">{{ $t('hosts.cpuCores') }}</label>
            <p class="mt-1 text-sm text-gray-900">{{ hostDetail.cpu_cores || '-' }}</p>
          </div>
          <div>
            <label class="text-sm font-medium text-gray-500">{{ $t('hosts.memoryTotal') }}</label>
            <p class="mt-1 text-sm text-gray-900">{{ hostDetail.memory_total || '-' }}</p>
          </div>
          <div>
            <label class="text-sm font-medium text-gray-500">{{ $t('hosts.memoryFree') }}</label>
            <p class="mt-1 text-sm text-gray-900">{{ hostDetail.memory_free || '-' }}</p>
          </div>
          <div>
            <label class="text-sm font-medium text-gray-500">{{ $t('hosts.diskCount') }}</label>
            <p class="mt-1 text-sm text-gray-900">{{ hostDetail.disk_count || '-' }}</p>
          </div>
          <div>
            <label class="text-sm font-medium text-gray-500">{{ $t('hosts.diskTotalSize') }}</label>
            <p class="mt-1 text-sm text-gray-900">{{ hostDetail.disk_total_size || '-' }}</p>
          </div>
        </div>
        <div v-if="hostDetail.credentials" class="mt-4">
          <h3 class="text-sm font-medium text-gray-700 mb-2">{{ $t('hosts.credentials') }}</h3>
          <div class="bg-gray-50 p-3 rounded">
            <p class="text-sm"><span class="font-medium">{{ $t('hosts.username') }}:</span> {{ hostDetail.credentials.username }}</p>
            <p v-if="hostDetail.credentials.password" class="text-sm"><span class="font-medium">{{ $t('auth.password') }}:</span> {{ hostDetail.credentials.password }}</p>
            <p v-if="hostDetail.credentials.ssh_port" class="text-sm"><span class="font-medium">{{ $t('hosts.sshPort') }}:</span> {{ hostDetail.credentials.ssh_port }}</p>
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

    <!-- CSV Import Modal -->
    <Modal :open="showImportModal" @close="closeImportModal" :title="$t('hosts.csvImportTitle')" max-width="md">
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700">{{ $t('hosts.selectCSVFile') }}</label>
          <input
            ref="fileInput"
            type="file"
            accept=".csv"
            @change="handleFileSelect"
            class="mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
          />
          <p class="mt-2 text-xs text-gray-500">
            {{ $t('hosts.csvFormatHint') }}
          </p>
        </div>
        <div v-if="importResult" class="p-3 rounded" :class="importResult.errors?.length > 0 ? 'bg-yellow-50' : 'bg-green-50'">
          <p class="text-sm font-medium" :class="importResult.errors?.length > 0 ? 'text-yellow-800' : 'text-green-800'">
            {{ importResult.message }}
          </p>
          <p v-if="importResult.data" class="text-xs mt-1" :class="importResult.errors?.length > 0 ? 'text-yellow-700' : 'text-green-700'">
            {{ $t('hosts.created') }}: {{ importResult.data.created }}, {{ $t('hosts.updated') }}: {{ importResult.data.updated }}, {{ $t('hosts.errors') }}: {{ importResult.data.errors?.length || 0 }}
          </p>
        </div>
      </div>
      <template #footer>
        <button
          type="button"
          @click="closeImportModal"
          class="mt-3 inline-flex w-full justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 sm:mt-0 sm:w-auto"
        >
          {{ $t('common.close') }}
        </button>
        <button
          type="button"
          @click="handleImport"
          :disabled="!selectedFile || importing"
          class="inline-flex w-full justify-center rounded-md bg-blue-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-blue-500 sm:ml-3 sm:w-auto disabled:opacity-50"
        >
          {{ importing ? $t('common.loading') : $t('common.import') }}
        </button>
      </template>
    </Modal>

    <!-- Missing Credentials Modal -->
    <Modal :open="showMissingCredentialsModal" @close="showMissingCredentialsModal = false" :title="$t('hosts.missingCredentials')" max-width="md">
      <div class="space-y-4">
        <p class="text-sm text-gray-600">{{ $t('hosts.missingCredentialsMessage') }}</p>
        <div class="max-h-60 overflow-y-auto">
          <ul class="list-disc list-inside space-y-2">
            <li v-for="host in missingCredentialsHosts" :key="host.id" class="text-sm text-gray-700">
              {{ host.ip }} ({{ host.hostname || '-' }})
            </li>
          </ul>
        </div>
      </div>
      <template #footer>
        <button
          type="button"
          @click="showMissingCredentialsModal = false"
          class="mt-3 inline-flex w-full justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 sm:mt-0 sm:w-auto"
        >
          {{ $t('common.close') }}
        </button>
        <button
          type="button"
          @click="openBatchCredentialsModalFromMissing"
          class="inline-flex w-full justify-center rounded-md bg-blue-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-blue-500 sm:ml-3 sm:w-auto"
        >
          {{ $t('hosts.updateNow') }}
        </button>
      </template>
    </Modal>

    <!-- Batch Update Credentials Modal -->
    <Modal :open="showBatchCredentialsModal" @close="closeBatchCredentialsModal" :title="$t('hosts.batchUpdateCredentials')" max-width="md">
      <form @submit.prevent="saveBatchCredentials" class="space-y-4">
        <div v-if="selectedHosts.length > 0 || missingCredentialsHosts.length > 0">
          <label class="block text-sm font-medium text-gray-700">{{ $t('hosts.selectedHosts') }}</label>
          <div class="mt-1 max-h-32 overflow-y-auto bg-gray-50 p-2 rounded text-sm">
            <div v-for="hostId in (missingCredentialsHosts.length > 0 ? missingCredentialsHosts.map(h => h.id) : selectedHosts)" :key="hostId" class="text-gray-600">
              {{ hosts.find(h => h.id === hostId)?.ip || hostId }}
            </div>
          </div>
        </div>
        <div>
          <label class="flex items-center">
            <input
              v-model="batchCredentialsForm.applyToAll"
              type="checkbox"
              class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span class="ml-2 text-sm text-gray-700">{{ $t('hosts.applyToAll') }}</span>
          </label>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700">{{ $t('hosts.username') }} *</label>
          <input
            v-model="batchCredentialsForm.username"
            type="text"
            required
            class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700">{{ $t('auth.password') }}</label>
          <input
            v-model="batchCredentialsForm.password"
            type="password"
            class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700">{{ $t('hosts.sshPort') }}</label>
            <input
              v-model.number="batchCredentialsForm.ssh_port"
              type="number"
              class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700">{{ $t('hosts.keyPath') }}</label>
            <input
              v-model="batchCredentialsForm.key_path"
              type="text"
              class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
        </div>
      </form>
      <template #footer>
        <button
          type="button"
          @click="closeBatchCredentialsModal"
          class="mt-3 inline-flex w-full justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 sm:mt-0 sm:w-auto"
        >
          {{ $t('common.cancel') }}
        </button>
        <button
          type="button"
          @click="saveBatchCredentials"
          :disabled="saving"
          class="inline-flex w-full justify-center rounded-md bg-blue-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-blue-500 sm:ml-3 sm:w-auto disabled:opacity-50"
        >
          {{ saving ? $t('hosts.saving') : $t('common.save') }}
        </button>
      </template>
    </Modal>

    <!-- Confirm Modal -->
    <ConfirmModal
      :open="showConfirmModal"
      @close="showConfirmModal = false"
      @confirm="handleConfirm"
      :title="$t('hosts.confirmDelete')"
      :message="confirmMessage"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { hostsApi, type Host } from '@/api/hosts'
import { importApi } from '@/api/import'
import Modal from '@/components/Modal.vue'
import ConfirmModal from '@/components/ConfirmModal.vue'
import LoadingOverlay from '@/components/LoadingOverlay.vue'
import { useToastStore } from '@/stores/toast'
import { useSettingsStore } from '@/stores/settings'
import {
  ServerIcon,
  MagnifyingGlassIcon,
  ArrowDownTrayIcon,
  ArrowUpTrayIcon,
  PlusIcon,
  CpuChipIcon,
  ComputerDesktopIcon,
  CloudIcon,
  EyeIcon,
  PencilIcon,
  TrashIcon,
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon,
  MagnifyingGlassCircleIcon,
  CloudArrowUpIcon,
  DocumentTextIcon,
  ArrowPathIcon,
  Bars3Icon,
  Squares2X2Icon,
  EllipsisVerticalIcon,
  ChevronDownIcon,
} from '@heroicons/vue/24/outline'
import { Menu, MenuButton, MenuItem, MenuItems } from '@headlessui/vue'

const { t } = useI18n()
const toastStore = useToastStore()
const settingsStore = useSettingsStore()

const hosts = ref<Host[]>([])
const loading = ref(false)
const loadingTree = ref(false)
const searchQuery = ref('')
const selectedHosts = ref<number[]>([])
const viewMode = ref<'list' | 'tree'>('list')
const treeData = ref<any[]>([])
const showCreateModal = ref(false)
const showDetailModal = ref(false)
const showImportModal = ref(false)
const showMissingCredentialsModal = ref(false)
const showBatchCredentialsModal = ref(false)
const missingCredentialsHosts = ref<Array<{id: number, ip: string, hostname?: string}>>([])
const batchCredentialsForm = ref({
  username: '',
  password: '',
  ssh_port: 22,
  key_path: '',
  applyToAll: true
})
const hostForm = ref<Partial<Host>>({})
const hostDetail = ref<any>(null)
const editingHostId = ref<number | null>(null)
const saving = ref(false)
const pagination = ref<any>(null)
const perPage = ref(settingsStore.defaultPageSize)
const selectedFile = ref<File | null>(null)
const fileInput = ref<HTMLInputElement | null>(null)
const importing = ref(false)
const importResult = ref<any>(null)
const showConfirmModal = ref(false)
const confirmAction = ref<(() => void) | null>(null)
const confirmMessage = ref('')

const allSelected = computed(() => {
  return hosts.value.length > 0 && selectedHosts.value.length === hosts.value.length
})

let searchTimeout: ReturnType<typeof setTimeout> | null = null

const debouncedSearch = () => {
  if (searchTimeout) clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    loadHosts(1)
  }, 500)
}

const loadHosts = async (page = 1) => {
  loading.value = true
  try {
    const response: any = await hostsApi.getHosts({
      page,
      per_page: perPage.value,
      search: searchQuery.value || undefined,
    })
    if (response && response.code === 200) {
      hosts.value = response.data || []
      pagination.value = response.pagination
    } else if (Array.isArray(response)) {
      hosts.value = response
    } else if (response && response.data) {
      hosts.value = response.data
      pagination.value = response.pagination
    }
  } catch (error: any) {
    toastStore.error(error.response?.data?.message || t('messages.loadFailed'))
  } finally {
    loading.value = false
  }
}

const loadTreeData = async () => {
  loadingTree.value = true
  try {
    const response: any = await hostsApi.getHostsTree()
    if (response && response.code === 200) {
      treeData.value = response.data || []
    } else if (Array.isArray(response)) {
      treeData.value = response
    } else if (response && response.data) {
      treeData.value = response.data
    }
  } catch (error: any) {
    toastStore.error(error.response?.data?.message || t('messages.loadFailed'))
    treeData.value = []
  } finally {
    loadingTree.value = false
  }
}

const toggleHostSelection = (hostId: number) => {
  const index = selectedHosts.value.indexOf(hostId)
  if (index > -1) {
    selectedHosts.value.splice(index, 1)
  } else {
    selectedHosts.value.push(hostId)
  }
}

const toggleSelectAll = () => {
  if (allSelected.value) {
    selectedHosts.value = []
  } else {
    selectedHosts.value = hosts.value.map(h => h.id!).filter(Boolean)
  }
}

const openCreateModal = () => {
  hostForm.value = {
    is_physical: false,
  }
  editingHostId.value = null
  showCreateModal.value = true
}

const editHost = (host: Host) => {
  hostForm.value = { ...host }
  editingHostId.value = host.id!
  showCreateModal.value = true
}

const closeCreateModal = () => {
  showCreateModal.value = false
  hostForm.value = {}
  editingHostId.value = null
}

const saveHost = async () => {
  saving.value = true
  try {
    if (editingHostId.value) {
      await hostsApi.updateHost(editingHostId.value, hostForm.value)
      toastStore.success(t('hosts.updateSuccess'))
    } else {
      await hostsApi.createHost(hostForm.value as Host)
      toastStore.success(t('hosts.saveSuccess'))
    }
    closeCreateModal()
    loadHosts(pagination.value?.page || 1)
  } catch (error: any) {
    toastStore.error(error.response?.data?.message || t('messages.saveFailed'))
  } finally {
    saving.value = false
  }
}

const viewHost = async (id: number) => {
  try {
    const [hostRes, credRes] = await Promise.all([
      hostsApi.getHost(id),
      hostsApi.getCredentials(id).catch(() => null),
    ])
    hostDetail.value = {
      ...hostRes.data,
      credentials: credRes?.data || null,
    }
    showDetailModal.value = true
  } catch (error: any) {
    toastStore.error(error.response?.data?.message || t('messages.loadFailed'))
  }
}

const closeDetailModal = () => {
  showDetailModal.value = false
  hostDetail.value = null
}

const collectHost = async (id: number) => {
  try {
    await hostsApi.batchCollect([id])
    toastStore.success(t('hosts.collectTaskCreated'))
  } catch (error: any) {
    // Check if error is about missing credentials
    if (error.response?.data?.code === 400 && error.response?.data?.data?.missing_credentials) {
      const missing = error.response.data.data.missing_credentials
      showMissingCredentialsModal.value = true
      missingCredentialsHosts.value = missing
      return
    }
    toastStore.error(error.response?.data?.message || t('messages.operationFailed'))
  }
}

const handleBatchCollect = async () => {
  if (selectedHosts.value.length === 0) return
  try {
    await hostsApi.batchCollect(selectedHosts.value)
    toastStore.success(t('hosts.batchCollectSuccess', { count: selectedHosts.value.length }))
    selectedHosts.value = []
  } catch (error: any) {
    // Check if error is about missing credentials
    if (error.response?.data?.code === 400 && error.response?.data?.data?.missing_credentials) {
      const missing = error.response.data.data.missing_credentials
      showMissingCredentialsModal.value = true
      missingCredentialsHosts.value = missing
      return
    }
    toastStore.error(error.response?.data?.message || t('messages.operationFailed'))
  }
}

const deleteHost = async (id: number) => {
  confirmMessage.value = t('hosts.confirmDeleteMessage')
  confirmAction.value = async () => {
    try {
      await hostsApi.deleteHost(id)
      toastStore.success(t('hosts.deleteSuccess'))
      loadHosts(pagination.value?.page || 1)
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

const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files && target.files.length > 0) {
    selectedFile.value = target.files[0]
    importResult.value = null
  }
}

const closeImportModal = () => {
  showImportModal.value = false
  selectedFile.value = null
  importResult.value = null
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

const handleImport = async () => {
  if (!selectedFile.value) return
  importing.value = true
  try {
    const response = await importApi.importHostsFromCSV(selectedFile.value)
    importResult.value = response
    if (response.data?.errors?.length === 0) {
      const importResponse: any = response
    toastStore.success(importResponse.message || t('hosts.importSuccess'))
      loadHosts(1)
      setTimeout(() => {
        closeImportModal()
      }, 2000)
    } else {
      const importResponse: any = response
      toastStore.warning(importResponse.message || t('hosts.importWithErrors'))
    }
  } catch (error: any) {
    toastStore.error(error.response?.data?.message || t('messages.operationFailed'))
  } finally {
    importing.value = false
  }
}

const getCollectionStatusClass = (status?: string) => {
  const statusMap: Record<string, string> = {
    'not_collected': 'bg-gray-100 text-gray-800',
    'collecting': 'bg-blue-100 text-blue-800',
    'completed': 'bg-green-100 text-green-800',
    'failed': 'bg-red-100 text-red-800',
  }
  return statusMap[status || 'not_collected'] || 'bg-gray-100 text-gray-800'
}

const getCollectionStatusIcon = (status?: string) => {
  const iconMap: Record<string, any> = {
    'not_collected': ClockIcon,
    'collecting': CpuChipIcon,
    'completed': CheckCircleIcon,
    'failed': XCircleIcon,
  }
  return iconMap[status || 'not_collected'] || ClockIcon
}

const getCollectionStatusText = (status?: string) => {
  const textMap: Record<string, string> = {
    'not_collected': t('hosts.notCollected'),
    'collecting': t('hosts.collecting'),
    'completed': t('common.completed'),
    'failed': t('common.failed'),
  }
  return textMap[status || 'not_collected'] || status || ''
}

const getSourceIcon = (source?: string) => {
  const iconMap: Record<string, any> = {
    'scan': MagnifyingGlassCircleIcon,
    'platform': CloudArrowUpIcon,
    'manual': DocumentTextIcon,
  }
  return iconMap[source || 'manual'] || DocumentTextIcon
}

const getSourceIconColor = (source?: string) => {
  const colorMap: Record<string, string> = {
    'scan': 'text-blue-500',
    'platform': 'text-purple-500',
    'manual': 'text-gray-500',
  }
  return colorMap[source || 'manual'] || 'text-gray-500'
}

const getSourceText = (source?: string) => {
  const textMap: Record<string, string> = {
    'scan': t('hosts.scan'),
    'platform': t('hosts.platform'),
    'manual': t('hosts.manual'),
  }
  return textMap[source || 'manual'] || source || ''
}

const formatBytes = (bytes: number, unit: 'GB' | 'MB' = 'GB'): string => {
  if (!bytes || bytes === 0) return '-'
  if (unit === 'GB') {
    const gb = bytes / (1024 * 1024 * 1024)
    return gb >= 1 ? `${gb.toFixed(2)}GB` : `${(gb * 1024).toFixed(2)}MB`
  } else {
    const mb = bytes / (1024 * 1024)
    return `${mb.toFixed(2)}MB`
  }
}

const handleExportCSV = async () => {
  try {
    const includeCredentials = confirm(t('hosts.credentials'))
    const response = await hostsApi.exportHostsCSV({
      include_credentials: includeCredentials,
      search: searchQuery.value || undefined,
    })
    
    // Create blob and download
    const blob = new Blob([response.data], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    const url = URL.createObjectURL(blob)
    link.setAttribute('href', url)
    link.setAttribute('download', `hosts_export_${new Date().toISOString().split('T')[0]}.csv`)
    link.style.visibility = 'hidden'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    
    toastStore.success(t('hosts.exportSuccess'))
  } catch (error: any) {
    toastStore.error(error.response?.data?.message || t('messages.operationFailed'))
  }
}

const openBatchCredentialsModal = () => {
  if (selectedHosts.value.length === 0) return
  batchCredentialsForm.value = {
    username: '',
    password: '',
    ssh_port: 22,
    key_path: '',
    applyToAll: true
  }
  showBatchCredentialsModal.value = true
}

const openBatchCredentialsModalFromMissing = () => {
  showMissingCredentialsModal.value = false
  batchCredentialsForm.value = {
    username: '',
    password: '',
    ssh_port: 22,
    key_path: '',
    applyToAll: true
  }
  showBatchCredentialsModal.value = true
}

const closeBatchCredentialsModal = () => {
  showBatchCredentialsModal.value = false
  batchCredentialsForm.value = {
    username: '',
    password: '',
    ssh_port: 22,
    key_path: '',
    applyToAll: true
  }
  missingCredentialsHosts.value = []
}

const saveBatchCredentials = async () => {
  saving.value = true
  try {
    const hostIds = missingCredentialsHosts.value.length > 0 
      ? missingCredentialsHosts.value.map(h => h.id)
      : selectedHosts.value
    
    if (hostIds.length === 0) {
      toastStore.error(t('hosts.selectedHosts'))
      return
    }
    
    const credentials: any = {}
    if (batchCredentialsForm.value.username) {
      credentials.username = batchCredentialsForm.value.username
    }
    if (batchCredentialsForm.value.password) {
      credentials.password = batchCredentialsForm.value.password
    }
    if (batchCredentialsForm.value.ssh_port) {
      credentials.ssh_port = batchCredentialsForm.value.ssh_port
    }
    if (batchCredentialsForm.value.key_path) {
      credentials.key_path = batchCredentialsForm.value.key_path
    }
    
    await hostsApi.batchUpdateCredentials(hostIds, credentials)
    toastStore.success(t('hosts.credentialsUpdated', { count: hostIds.length }))
    closeBatchCredentialsModal()
    if (missingCredentialsHosts.value.length > 0) {
      // Retry collection after updating credentials
      try {
        await hostsApi.batchCollect(hostIds)
        toastStore.success(t('hosts.collectTaskCreated'))
      } catch (error: any) {
        toastStore.error(error.response?.data?.message || t('messages.operationFailed'))
      }
    }
    selectedHosts.value = []
    loadHosts(pagination.value?.page || 1)
  } catch (error: any) {
    toastStore.error(error.response?.data?.message || t('messages.operationFailed'))
  } finally {
    saving.value = false
  }
}

// Watch view mode changes
watch(viewMode, (newMode) => {
  if (newMode === 'tree') {
    loadTreeData()
  }
})

onMounted(() => {
  loadHosts()
  if (viewMode.value === 'tree') {
    loadTreeData()
  }
})
</script>
