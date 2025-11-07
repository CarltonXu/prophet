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
        
        <!-- Enhanced Search with Field Selector -->
        <div class="relative flex-1 min-w-[300px] max-w-lg" ref="searchContainer">
          <div 
            class="relative w-full"
            @click="handleSearchContainerClick"
          >
            <!-- Search Input Container -->
            <div 
              class="flex items-center w-full px-3 py-2 border border-gray-300 rounded-md bg-white shadow-sm focus-within:ring-2 focus-within:ring-blue-500 focus-within:border-blue-500 transition-all cursor-text"
              :class="{ 'ring-2 ring-blue-500 border-blue-500': showFieldDropdown || showValueDropdown }"
            >
              <!-- Field Tag (if selected) -->
              <div v-if="searchField !== 'all'" class="flex items-center mr-2 px-2 py-0.5 bg-blue-100 text-blue-800 rounded text-xs font-medium">
                <span>{{ getFieldLabel(searchField) }}</span>
                <button
                  @click.stop="clearField"
                  class="ml-1.5 hover:bg-blue-200 rounded-full p-0.5"
                >
                  <XMarkIcon class="h-3 w-3" />
                </button>
              </div>
              
              <!-- Search Icon -->
              <MagnifyingGlassIcon class="h-5 w-5 text-gray-400 flex-shrink-0" />
              
              <!-- Input or Value Selector -->
              <div class="flex-1 ml-2 min-w-0">
          <input
                  v-if="searchField === 'all' || searchField !== 'tag'"
            v-model="searchQuery"
            type="text"
                  :placeholder="getSearchPlaceholder()"
                  class="w-full border-0 p-0 text-sm focus:outline-none focus:ring-0"
            @input="debouncedSearch"
                  @keyup.enter="loadHosts(1)"
                  @focus="handleInputFocus"
                  @keydown.escape="showFieldDropdown = false; showValueDropdown = false"
                />
                <div
                  v-else-if="searchField === 'tag'"
                  @click.stop="showValueDropdown = !showValueDropdown"
                  class="flex items-center justify-between cursor-pointer min-h-[20px]"
                >
                  <span class="text-sm" :class="searchQuery ? 'text-gray-900' : 'text-gray-400'">
                    {{ searchQuery || $t('hosts.selectTag') }}
                  </span>
                  <ChevronDownIcon 
                    class="h-4 w-4 text-gray-400 transition-transform flex-shrink-0"
                    :class="{ 'rotate-180': showValueDropdown }"
                  />
                </div>
              </div>
              
              <!-- Clear Button -->
              <button
                v-if="searchQuery || searchField !== 'all'"
                @click.stop="clearSearch"
                class="ml-2 text-gray-400 hover:text-gray-600 focus:outline-none flex-shrink-0"
                type="button"
              >
                <XMarkIcon class="h-4 w-4" />
              </button>
            </div>
            
            <!-- Field Selection Dropdown -->
            <div
              v-if="showFieldDropdown && searchField === 'all'"
              class="absolute z-50 w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg max-h-60 overflow-auto"
            >
              <div class="py-1">
                <button
                  v-for="field in searchFields"
                  :key="field.value"
                  @click="selectField(field.value)"
                  class="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100 flex items-center"
                >
                  <div class="w-2 h-2 rounded-full bg-orange-500 mr-3 flex-shrink-0"></div>
                  <span>{{ field.label }}</span>
                </button>
              </div>
            </div>
            
            <!-- Value Selection Dropdown (for tag) -->
            <div
              v-if="showValueDropdown && searchField === 'tag'"
              class="absolute z-50 w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg max-h-60 overflow-auto"
            >
              <div class="py-1">
                <button
                  @click="selectTagValue('')"
                  class="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100"
                >
                  {{ $t('hosts.all') }}
                </button>
                <button
                  v-for="tag in availableTags"
                  :key="tag.id"
                  @click="selectTagValue(tag.name)"
                  class="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100 flex items-center"
                >
                  <div class="w-2 h-2 rounded-full mr-3 flex-shrink-0" :style="{ backgroundColor: tag.color || '#6B7280' }"></div>
                  <span>{{ tag.name }}</span>
                </button>
              </div>
            </div>
          </div>
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
          <div v-if="selectedHosts.length > 0" class="relative z-30">
            <Menu as="div" class="relative inline-block text-left">
              <MenuButton class="inline-flex items-center px-3 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500">
                <span class="mr-2">{{ $t('common.batchOperation') }} ({{ selectedHosts.length }})</span>
                <ChevronDownIcon class="h-4 w-4" />
              </MenuButton>
              <MenuItems class="absolute right-0 z-50 mt-2 w-56 origin-top-right rounded-md bg-white shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none">
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
                  <MenuItem v-slot="{ active }">
                    <button
                      @click="openBatchTagManagementModal"
                      :class="[active ? 'bg-gray-100' : '', 'flex items-center w-full px-4 py-2 text-sm text-gray-700']"
                    >
                      <TagIcon class="h-4 w-4 mr-3 text-gray-400" />
                      {{ $t('hosts.batchManageTags') }}
                    </button>
                  </MenuItem>
                  <div class="border-t border-gray-200 my-1"></div>
                  <MenuItem v-slot="{ active }">
                    <button
                      @click="openBatchDeleteModal"
                      :class="[active ? 'bg-red-50' : '', 'flex items-center w-full px-4 py-2 text-sm text-red-700']"
                    >
                      <TrashIcon class="h-4 w-4 mr-3 text-red-400" />
                      {{ $t('hosts.batchDelete') }}
                    </button>
                  </MenuItem>
                  </div>
                </MenuItems>
            </Menu>
          </div>
          
          <!-- More Actions Menu -->
          <Menu as="div" class="relative inline-block text-left">
            <MenuButton class="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
              <EllipsisVerticalIcon class="h-5 w-5" />
            </MenuButton>
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
          </Menu>
        </div>
      </div>
    </div>
    
    <!-- Filters Panel -->
    <div v-if="viewMode === 'list'" class="mb-4 bg-white shadow sm:rounded-md">
      <!-- Active Filters Tags -->
      <div v-if="hasActiveFilters" class="px-4 pt-3 pb-2 border-b border-gray-200">
        <div class="flex items-center flex-wrap gap-2">
          <span class="text-xs font-medium text-gray-500">{{ $t('hosts.activeFilters') }}:</span>
          <span
            v-for="filter in activeFilters"
            :key="filter.key"
            class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
          >
            {{ filter.label }}: {{ filter.value }}
            <button
              @click="removeFilter(filter.key)"
              class="ml-1.5 inline-flex items-center justify-center w-4 h-4 rounded-full hover:bg-blue-200 focus:outline-none"
            >
              <XMarkIcon class="w-3 h-3" />
            </button>
          </span>
          <button
            @click="clearFilters"
            class="text-xs text-gray-600 hover:text-gray-900 underline"
          >
            {{ $t('hosts.clearAll') }}
          </button>
        </div>
      </div>
      
      <!-- Filter Controls -->
      <div class="p-4">
        <div class="flex items-center justify-between mb-3">
          <button
            @click="showFilters = !showFilters"
            class="flex items-center text-sm font-medium text-gray-700 hover:text-gray-900"
          >
            <FunnelIcon class="h-4 w-4 mr-2" />
            {{ $t('hosts.filters') }}
            <ChevronDownIcon 
              :class="['ml-2 h-4 w-4 transition-transform', showFilters ? 'rotate-180' : '']" 
            />
          </button>
          <div class="flex items-center gap-2">
            <!-- Quick Filters -->
            <div class="flex items-center gap-1">
              <button
                @click="applyQuickFilter('not_collected')"
                class="px-2 py-1 text-xs font-medium text-gray-700 bg-gray-100 rounded hover:bg-gray-200"
              >
                {{ $t('hosts.notCollected') }}
              </button>
              <button
                @click="applyQuickFilter('collecting')"
                class="px-2 py-1 text-xs font-medium text-blue-700 bg-blue-100 rounded hover:bg-blue-200"
              >
                {{ $t('hosts.collecting') }}
              </button>
              <button
                @click="applyQuickFilter('completed')"
                class="px-2 py-1 text-xs font-medium text-green-700 bg-green-100 rounded hover:bg-green-200"
              >
                {{ $t('common.completed') }}
              </button>
            </div>
          </div>
        </div>
        
        <!-- Collapsible Filter Options -->
        <div v-show="showFilters" class="mt-4 space-y-4">
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
            <!-- OS Type Filter -->
            <div>
              <label class="block text-xs font-medium text-gray-700 mb-1">{{ $t('hosts.osType') }}</label>
              <select
                v-model="filters.os_type"
                @change="loadHosts(1)"
                class="w-full px-2 py-1.5 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">{{ $t('hosts.all') }}</option>
                <option value="linux">Linux</option>
                <option value="windows">Windows</option>
                <option value="vmware">VMware</option>
              </select>
            </div>
            
            <!-- Device Type Filter -->
            <div>
              <label class="block text-xs font-medium text-gray-700 mb-1">{{ $t('hosts.deviceType') }}</label>
              <select
                v-model="filters.device_type"
                @change="loadHosts(1)"
                class="w-full px-2 py-1.5 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">{{ $t('hosts.all') }}</option>
                <option value="host">{{ $t('hosts.host') }}</option>
                <option value="network_device">{{ $t('hosts.networkDevice') }}</option>
              </select>
            </div>
            
            <!-- Collection Status Filter -->
            <div>
              <label class="block text-xs font-medium text-gray-700 mb-1">{{ $t('hosts.collectionStatus') }}</label>
              <select
                v-model="filters.collection_status"
                @change="loadHosts(1)"
                class="w-full px-2 py-1.5 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">{{ $t('hosts.all') }}</option>
                <option value="not_collected">{{ $t('hosts.notCollected') }}</option>
                <option value="collecting">{{ $t('hosts.collecting') }}</option>
                <option value="completed">{{ $t('common.completed') }}</option>
                <option value="failed">{{ $t('common.failed') }}</option>
              </select>
            </div>
            
            <!-- Source Filter -->
            <div>
              <label class="block text-xs font-medium text-gray-700 mb-1">{{ $t('hosts.source') }}</label>
              <select
                v-model="filters.source"
                @change="loadHosts(1)"
                class="w-full px-2 py-1.5 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">{{ $t('hosts.all') }}</option>
                <option value="scan">{{ $t('hosts.scan') }}</option>
                <option value="platform">{{ $t('hosts.platform') }}</option>
                <option value="manual">{{ $t('hosts.manual') }}</option>
              </select>
            </div>
            
            <!-- Physical/Virtual Filter -->
            <div>
              <label class="block text-xs font-medium text-gray-700 mb-1">{{ $t('hosts.deviceNature') }}</label>
              <select
                v-model="filters.is_physical"
                @change="loadHosts(1)"
                class="w-full px-2 py-1.5 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">{{ $t('hosts.all') }}</option>
                <option value="true">{{ $t('hosts.physical') }}</option>
                <option value="false">{{ $t('hosts.virtual') }}</option>
              </select>
            </div>
            
            <!-- Tag Filter -->
            <div>
              <label class="block text-xs font-medium text-gray-700 mb-1">{{ $t('hosts.tags') }}</label>
              <select
                v-model="filters.tag_id"
                @change="loadHosts(1)"
                class="w-full px-2 py-1.5 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">{{ $t('hosts.all') }}</option>
                <option v-for="tag in availableTags" :key="tag.id" :value="tag.id">
                  {{ tag.name }}
                </option>
              </select>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Tree View -->
    <div v-if="viewMode === 'tree'" class="bg-white shadow sm:rounded-md overflow-hidden relative">
      <LoadingOverlay :loading="loadingTree" :text="$t('common.loading')" />
      <div v-if="!loadingTree && treeData.length === 0" class="text-center py-8 text-gray-500">
        <ServerIcon class="h-12 w-12 mx-auto text-gray-300 mb-2" />
        <p>{{ $t('hosts.noPlatformHosts') }}</p>
      </div>
      <div v-else-if="!loadingTree" class="overflow-y-auto max-h-[calc(100vh-300px)] p-4">
        <div v-for="platform in treeData" :key="platform.platform_id" class="mb-4">
          <!-- Platform Level -->
          <div class="flex items-center mb-2 p-3 bg-blue-50 rounded-lg border border-blue-200 hover:bg-blue-100 transition-colors">
            <!-- Expand/Collapse Button -->
            <button
              @click="togglePlatformExpand(platform.platform_id!)"
              class="mr-2 p-1 hover:bg-blue-200 rounded transition-colors"
              :title="expandedPlatforms.has(platform.platform_id!) ? $t('hosts.collapse') : $t('hosts.expand')"
            >
              <ChevronDownIcon 
                v-if="expandedPlatforms.has(platform.platform_id!)"
                class="h-4 w-4 text-blue-700"
              />
              <ChevronRightIcon 
                v-else
                class="h-4 w-4 text-blue-700"
              />
            </button>
            
            <!-- Platform Checkbox -->
            <input
              type="checkbox"
              :ref="(el: any) => {
                if (el && platform.platform_id) {
                  platformCheckboxRefs.set(platform.platform_id, el)
                  el.indeterminate = isPlatformPartiallySelected(platform)
                }
              }"
              :checked="isPlatformAllSelected(platform)"
              @click.stop="togglePlatformSelection(platform)"
              class="rounded border-gray-300 text-blue-600 focus:ring-blue-500 mr-2"
            />
            
            <CloudIcon class="h-5 w-5 mr-2 text-blue-600" />
            <div class="flex-1">
              <h3 class="text-sm font-semibold text-blue-900">{{ platform.platform_name }}</h3>
              <p class="text-xs text-blue-600">{{ platform.platform_type.toUpperCase() }}</p>
            </div>
            <span class="text-xs text-blue-600 mr-2">
              {{ platform.esxi_hosts.reduce((sum: number, esxi: any) => sum + esxi.vms.length, 0) }}{{ $t('hosts.vmCount') }}
            </span>
          </div>
          
          <!-- ESXi Hosts Level (only show if platform is expanded) -->
          <div v-if="expandedPlatforms.has(platform.platform_id!)" v-for="esxi in platform.esxi_hosts" :key="esxi.esxi_name" class="ml-6 mb-3">
            <div class="flex items-center mb-1 p-2 bg-gray-50 rounded border border-gray-200 hover:bg-gray-100 transition-colors">
              <!-- Expand/Collapse Button -->
              <button
                @click="toggleESXiExpand(esxi.esxi_name)"
                class="mr-2 p-1 hover:bg-gray-200 rounded transition-colors"
                :title="expandedESXiHosts.has(esxi.esxi_name) ? $t('hosts.collapse') : $t('hosts.expand')"
              >
                <ChevronDownIcon 
                  v-if="expandedESXiHosts.has(esxi.esxi_name)"
                  class="h-4 w-4 text-gray-600"
                />
                <ChevronRightIcon 
                  v-else
                  class="h-4 w-4 text-gray-600"
                />
              </button>
              
              <!-- ESXi Checkbox -->
              <input
                type="checkbox"
                :ref="(el: any) => {
                  if (el && esxi.esxi_name) {
                    esxiCheckboxRefs.set(esxi.esxi_name, el)
                    el.indeterminate = isESXiPartiallySelected(esxi)
                  }
                }"
                :checked="isESXiAllSelected(esxi)"
                @click.stop="toggleESXiSelection(esxi)"
                class="rounded border-gray-300 text-blue-600 focus:ring-blue-500 mr-2"
              />
              
              <ServerIcon class="h-4 w-4 mr-2 text-gray-600" />
              <div class="flex-1">
                <h4 class="text-sm font-medium text-gray-900">{{ esxi.esxi_name }}</h4>
                <p v-if="esxi.esxi_ip" class="text-xs text-gray-500">{{ esxi.esxi_ip }}</p>
              </div>
              <span class="text-xs text-gray-600">{{ esxi.vms.length }}{{ $t('hosts.vmCount') }}</span>
            </div>
            
            <!-- VMs Level (only show if ESXi is expanded) -->
            <div v-if="expandedESXiHosts.has(esxi.esxi_name)" class="ml-8 space-y-1">
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
              <td colspan="13" class="px-4 py-4 text-gray-500">
                <ServerIcon class="h-12 w-12 mx-auto text-gray-300 mb-2" />
                <p>{{ $t('hosts.noHosts') }}</p>
              </td>
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
              <td class="px-4 py-4 whitespace-nowrap text-sm" @click.stop>
                <div class="flex flex-wrap gap-1 items-center">
                  <span
                    v-for="tag in host.tags"
                    :key="tag.id"
                    class="inline-flex items-center px-2 py-1 text-xs font-medium rounded text-white group/tag relative"
                    :style="{ backgroundColor: tag.color || '#6B7280' }"
                  >
                    {{ tag.name }}
                    <button
                      v-if="host.id"
                      @click.stop="removeHostTag(host.id, tag.id!)"
                      class="ml-1 opacity-0 group-hover/tag:opacity-100 hover:bg-black/20 rounded p-0.5 transition-opacity"
                      :title="$t('hosts.removeTag')"
                    >
                      <XMarkIcon class="h-3 w-3" />
                    </button>
                  </span>
                  <button
                    v-if="host.id"
                    @click.stop="showHostTagManagementModal(host)"
                    class="inline-flex items-center px-2 py-1 text-xs font-medium text-gray-600 bg-gray-100 hover:bg-gray-200 rounded transition-colors"
                    :title="$t('hosts.manageTags')"
                  >
                    <TagIcon class="h-3 w-3 mr-1" />
                    {{ $t('hosts.manageTags') }}
                  </button>
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
    <Modal :open="showDetailModal" @close="closeDetailModal" :title="$t('hosts.hostDetails')" max-width="4xl">
      <div v-if="hostDetail" class="space-y-6 max-h-[calc(100vh-200px)] overflow-y-auto">
        <!-- Basic Information -->
          <div>
          <h3 class="text-sm font-medium text-gray-700 mb-3 flex items-center">
            <InformationCircleIcon class="h-4 w-4 mr-2" />
            {{ $t('hosts.basicInfo') }}
          </h3>
          <div class="grid grid-cols-2 md:grid-cols-3 gap-4">
            <div>
              <label class="text-xs font-medium text-gray-500">{{ $t('hosts.ipAddress') }}</label>
            <p class="mt-1 text-sm text-gray-900">{{ hostDetail.ip }}</p>
          </div>
          <div>
              <label class="text-xs font-medium text-gray-500">{{ $t('hosts.hostname') }}</label>
            <p class="mt-1 text-sm text-gray-900">{{ hostDetail.hostname || '-' }}</p>
          </div>
          <div>
              <label class="text-xs font-medium text-gray-500">{{ $t('hosts.macAddress') }}</label>
            <p class="mt-1 text-sm text-gray-900">{{ hostDetail.mac || '-' }}</p>
          </div>
          <div>
              <label class="text-xs font-medium text-gray-500">{{ $t('hosts.osType') }}</label>
            <p class="mt-1 text-sm text-gray-900">{{ hostDetail.os_type || '-' }}</p>
          </div>
          <div>
              <label class="text-xs font-medium text-gray-500">{{ $t('hosts.osVersion') }}</label>
            <p class="mt-1 text-sm text-gray-900">{{ hostDetail.os_version || '-' }}</p>
          </div>
          <div>
              <label class="text-xs font-medium text-gray-500">{{ $t('hosts.deviceType') }}</label>
            <p class="mt-1 text-sm text-gray-900">{{ hostDetail.device_type || '-' }}</p>
          </div>
          <div>
              <label class="text-xs font-medium text-gray-500">{{ $t('hosts.cpuInfo') }}</label>
            <p class="mt-1 text-sm text-gray-900">{{ hostDetail.cpu_info || '-' }}</p>
          </div>
          <div>
              <label class="text-xs font-medium text-gray-500">{{ $t('hosts.cpuCores') }}</label>
            <p class="mt-1 text-sm text-gray-900">{{ hostDetail.cpu_cores || '-' }}</p>
          </div>
          <div>
              <label class="text-xs font-medium text-gray-500">{{ $t('hosts.memoryTotal') }}</label>
              <p class="mt-1 text-sm text-gray-900">{{ hostDetail.memory_total ? formatBytes(hostDetail.memory_total * 1024 * 1024, 'GB') : '-' }}</p>
          </div>
          <div>
              <label class="text-xs font-medium text-gray-500">{{ $t('hosts.memoryFree') }}</label>
              <p class="mt-1 text-sm text-gray-900">{{ hostDetail.memory_free ? formatBytes(hostDetail.memory_free * 1024 * 1024, 'GB') : '-' }}</p>
          </div>
          <div>
              <label class="text-xs font-medium text-gray-500">{{ $t('hosts.vendor') }}</label>
              <p class="mt-1 text-sm text-gray-900">{{ hostDetail.vendor || '-' }}</p>
          </div>
          <div>
              <label class="text-xs font-medium text-gray-500">{{ $t('hosts.source') }}</label>
              <p class="mt-1 text-sm text-gray-900">{{ getSourceText(hostDetail.source) }}</p>
          </div>
        </div>
        </div>
        
        <!-- Network Interfaces -->
        <div v-if="hostDetail.network_interfaces && hostDetail.network_interfaces.length > 0">
          <h3 class="text-sm font-medium text-gray-700 mb-3 flex items-center">
            <GlobeAltIcon class="h-4 w-4 mr-2" />
            {{ $t('hosts.networkInterfaces') }}
          </h3>
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">{{ $t('hosts.interface') }}</th>
                  <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">{{ $t('hosts.macAddress') }}</th>
                  <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">IPv4</th>
                  <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">IPv6</th>
                  <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">{{ $t('hosts.gateway') }}</th>
                  <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">MTU</th>
                  <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">{{ $t('hosts.status') }}</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="nic in hostDetail.network_interfaces" :key="nic.id">
                  <td class="px-3 py-2 whitespace-nowrap text-sm text-gray-900">
                    {{ nic.interface }}
                    <span v-if="nic.is_default" class="ml-1 text-xs text-blue-600">({{ $t('hosts.default') }})</span>
                  </td>
                  <td class="px-3 py-2 whitespace-nowrap text-sm text-gray-500">{{ nic.macaddress || '-' }}</td>
                  <td class="px-3 py-2 whitespace-nowrap text-sm text-gray-500">{{ nic.ipv4_address || '-' }}</td>
                  <td class="px-3 py-2 whitespace-nowrap text-sm text-gray-500">{{ nic.ipv6_address || '-' }}</td>
                  <td class="px-3 py-2 whitespace-nowrap text-sm text-gray-500">{{ nic.gateway || '-' }}</td>
                  <td class="px-3 py-2 whitespace-nowrap text-sm text-gray-500">{{ nic.mtu || '-' }}</td>
                  <td class="px-3 py-2 whitespace-nowrap text-sm">
                    <span :class="nic.active ? 'text-green-600' : 'text-gray-400'">
                      {{ nic.active ? $t('hosts.active') : $t('hosts.inactive') }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        
        <!-- Disks -->
        <div v-if="hostDetail.disks && hostDetail.disks.length > 0">
          <h3 class="text-sm font-medium text-gray-700 mb-3 flex items-center">
            <CircleStackIcon class="h-4 w-4 mr-2" />
            {{ $t('hosts.disks') }}
          </h3>
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">{{ $t('hosts.device') }}</th>
                  <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">{{ $t('hosts.vendor') }}</th>
                  <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">{{ $t('hosts.model') }}</th>
                  <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">{{ $t('hosts.size') }}</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="disk in hostDetail.disks" :key="disk.id">
                  <td class="px-3 py-2 whitespace-nowrap text-sm text-gray-900">{{ disk.device }}</td>
                  <td class="px-3 py-2 whitespace-nowrap text-sm text-gray-500">{{ disk.vendor || '-' }}</td>
                  <td class="px-3 py-2 whitespace-nowrap text-sm text-gray-500">{{ disk.model || '-' }}</td>
                  <td class="px-3 py-2 whitespace-nowrap text-sm text-gray-500">{{ disk.size_gb ? `${disk.size_gb} GB` : '-' }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        
        <!-- Partitions -->
        <div v-if="hostDetail.partitions && hostDetail.partitions.length > 0">
          <h3 class="text-sm font-medium text-gray-700 mb-3 flex items-center">
            <Squares2X2Icon class="h-4 w-4 mr-2" />
            {{ $t('hosts.partitions') }}
          </h3>
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">{{ $t('hosts.device') }}</th>
                  <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">{{ $t('hosts.filesystem') }}</th>
                  <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">{{ $t('hosts.totalSize') }}</th>
                  <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">{{ $t('hosts.availableSize') }}</th>
                  <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">{{ $t('hosts.usedSize') }}</th>
                  <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">{{ $t('hosts.usage') }}</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="partition in hostDetail.partitions" :key="partition.id">
                  <td class="px-3 py-2 whitespace-nowrap text-sm text-gray-900">{{ partition.device }}</td>
                  <td class="px-3 py-2 whitespace-nowrap text-sm text-gray-500">{{ partition.fstype || '-' }}</td>
                  <td class="px-3 py-2 whitespace-nowrap text-sm text-gray-500">{{ partition.size_total_gb ? `${partition.size_total_gb} GB` : '-' }}</td>
                  <td class="px-3 py-2 whitespace-nowrap text-sm text-gray-500">{{ partition.size_available_gb ? `${partition.size_available_gb} GB` : '-' }}</td>
                  <td class="px-3 py-2 whitespace-nowrap text-sm text-gray-500">{{ partition.size_used_gb ? `${partition.size_used_gb} GB` : '-' }}</td>
                  <td class="px-3 py-2 whitespace-nowrap text-sm">
                    <div class="flex items-center">
                      <div class="w-16 bg-gray-200 rounded-full h-2 mr-2">
                        <div
                          class="h-2 rounded-full"
                          :class="getUsageColor(partition.size_available_ratio)"
                          :style="{ width: `${(1 - (partition.size_available_ratio || 0)) * 100}%` }"
                        ></div>
                      </div>
                      <span class="text-xs text-gray-600">{{ Math.round((1 - (partition.size_available_ratio || 0)) * 100) }}%</span>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        
        <!-- Credentials -->
        <div v-if="hostDetail.credentials" class="mt-4">
          <h3 class="text-sm font-medium text-gray-700 mb-2 flex items-center">
            <LockClosedIcon class="h-4 w-4 mr-2" />
            {{ $t('hosts.credentials') }}
          </h3>
          <div class="bg-gray-50 p-3 rounded">
            <p class="text-sm"><span class="font-medium">{{ $t('hosts.username') }}:</span> {{ hostDetail.credentials.username }}</p>
            <p v-if="hostDetail.credentials.password" class="text-sm"><span class="font-medium">{{ $t('auth.password') }}:</span> {{ hostDetail.credentials.password }}</p>
            <p v-if="hostDetail.credentials.ssh_port" class="text-sm"><span class="font-medium">{{ $t('hosts.sshPort') }}:</span> {{ hostDetail.credentials.ssh_port }}</p>
            <p v-if="hostDetail.credentials.key_path" class="text-sm"><span class="font-medium">{{ $t('hosts.keyPath') }}:</span> {{ hostDetail.credentials.key_path }}</p>
          </div>
        </div>
        
        <!-- Scan Ports -->
        <div v-if="hostDetail.scan_ports && (hostDetail.scan_ports.tcp?.length > 0 || hostDetail.scan_ports.udp?.length > 0)">
          <h3 class="text-sm font-medium text-gray-700 mb-2 flex items-center">
            <GlobeAltIcon class="h-4 w-4 mr-2" />
            {{ $t('hosts.scanPorts') }}
          </h3>
          <div class="bg-gray-50 p-3 rounded">
            <div v-if="hostDetail.scan_ports.tcp && hostDetail.scan_ports.tcp.length > 0" class="mb-2">
              <span class="text-xs font-medium text-blue-600">TCP:</span>
              <span class="text-sm text-gray-700 ml-2">{{ hostDetail.scan_ports.tcp.join(', ') }}</span>
            </div>
            <div v-if="hostDetail.scan_ports.udp && hostDetail.scan_ports.udp.length > 0">
              <span class="text-xs font-medium text-green-600">UDP:</span>
              <span class="text-sm text-gray-700 ml-2">{{ hostDetail.scan_ports.udp.join(', ') }}</span>
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
            <div v-for="hostId in (missingCredentialsHosts.length > 0 ? missingCredentialsHosts.map((h: any) => h.id) : selectedHosts)" :key="hostId" class="text-gray-600">
              {{ hosts.find((h: Host) => h.id === hostId)?.ip || hostId }}
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

    <!-- Tag Management Modal -->
    <Modal :open="showTagManagementModal" @close="closeTagManagementModal" :title="$t('hosts.manageTags')" max-width="md">
      <div v-if="tagManagementTarget" class="space-y-4">
        <div>
          <p class="text-sm text-gray-600 mb-3">
            {{ $t('hosts.manageTagsFor') }}: <span class="font-semibold">{{ tagManagementTarget.ip }} {{ tagManagementTarget.hostname ? `(${tagManagementTarget.hostname})` : '' }}</span>
          </p>
  </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">{{ $t('hosts.selectTags') }}</label>
          <div class="max-h-60 overflow-y-auto border border-gray-300 rounded-md p-3 space-y-2">
            <label
              v-for="tag in availableTags"
              :key="tag.id"
              class="flex items-center space-x-2 cursor-pointer hover:bg-gray-50 p-2 rounded"
            >
              <input
                type="checkbox"
                :value="tag.id"
                v-model="selectedTagIds"
                class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <div class="flex items-center flex-1">
                <div class="w-3 h-3 rounded-full mr-2 flex-shrink-0" :style="{ backgroundColor: tag.color || '#6B7280' }"></div>
                <span class="text-sm text-gray-900">{{ tag.name }}</span>
              </div>
            </label>
          </div>
        </div>
        <div v-if="tagManagementTarget.tags && tagManagementTarget.tags.length > 0">
          <label class="block text-sm font-medium text-gray-700 mb-2">{{ $t('hosts.currentTags') }}</label>
          <div class="flex flex-wrap gap-2">
            <span
              v-for="tag in tagManagementTarget.tags"
              :key="tag.id"
              class="inline-flex items-center px-2 py-1 text-xs font-medium rounded text-white"
              :style="{ backgroundColor: tag.color || '#6B7280' }"
            >
              {{ tag.name }}
            </span>
          </div>
        </div>
      </div>
      <template #footer>
        <button
          type="button"
          @click="closeTagManagementModal"
          class="mt-3 inline-flex w-full justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 sm:mt-0 sm:w-auto"
        >
          {{ $t('common.cancel') }}
        </button>
        <button
          type="button"
          @click="saveHostTags"
          :disabled="saving"
          class="inline-flex w-full justify-center rounded-md bg-blue-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-blue-500 sm:ml-3 sm:w-auto disabled:opacity-50"
        >
          {{ saving ? $t('settings.saving') : $t('common.save') }}
        </button>
      </template>
    </Modal>

    <!-- Batch Tag Management Modal -->
    <Modal :open="showBatchTagManagementModal" @close="closeBatchTagManagementModal" :title="$t('hosts.batchManageTags')" max-width="md">
      <div class="space-y-4">
        <div>
          <p class="text-sm text-gray-600 mb-3">
            {{ $t('hosts.batchManageTagsFor') }}: <span class="font-semibold">{{ selectedHosts.length }} {{ $t('hosts.selectedHosts') }}</span>
          </p>
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">{{ $t('hosts.selectTags') }}</label>
          <div class="max-h-60 overflow-y-auto border border-gray-300 rounded-md p-3 space-y-2">
            <label
              v-for="tag in availableTags"
              :key="tag.id"
              class="flex items-center space-x-2 cursor-pointer hover:bg-gray-50 p-2 rounded"
            >
              <input
                type="checkbox"
                :value="tag.id"
                v-model="batchSelectedTagIds"
                class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <div class="flex items-center flex-1">
                <div class="w-3 h-3 rounded-full mr-2 flex-shrink-0" :style="{ backgroundColor: tag.color || '#6B7280' }"></div>
                <span class="text-sm text-gray-900">{{ tag.name }}</span>
                <span v-if="batchHostTagsMap.has(tag.id)" class="ml-2 text-xs text-gray-500">({{ $t('hosts.currentTags') }})</span>
              </div>
            </label>
          </div>
        </div>
        
        <div class="bg-blue-50 border border-blue-200 rounded-md p-3">
          <p class="text-xs text-blue-800">
            {{ $t('hosts.batchTagManageHint') }}
          </p>
        </div>
      </div>
      <template #footer>
        <button
          type="button"
          @click="closeBatchTagManagementModal"
          class="mt-3 inline-flex w-full justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 sm:mt-0 sm:w-auto"
        >
          {{ $t('common.cancel') }}
        </button>
        <button
          type="button"
          @click="saveBatchHostTags"
          :disabled="saving"
          class="inline-flex w-full justify-center rounded-md bg-blue-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-blue-500 sm:ml-3 sm:w-auto disabled:opacity-50"
        >
          {{ saving ? $t('settings.saving') : $t('common.save') }}
        </button>
      </template>
    </Modal>

    <!-- Batch Delete Confirmation Modal -->
    <Modal :open="showBatchDeleteModal" @close="closeBatchDeleteModal" :title="$t('hosts.batchDelete')" max-width="md">
      <div class="space-y-4">
        <div class="bg-red-50 border border-red-200 rounded-md p-4">
          <div class="flex">
            <div class="flex-shrink-0">
              <ExclamationTriangleIcon class="h-5 w-5 text-red-400" />
            </div>
            <div class="ml-3">
              <h3 class="text-sm font-medium text-red-800">
                {{ $t('hosts.batchDeleteWarning') }}
              </h3>
              <div class="mt-2 text-sm text-red-700">
                <p>{{ $t('hosts.batchDeleteMessage', { count: selectedHosts.length }) }}</p>
              </div>
            </div>
          </div>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            {{ $t('hosts.batchDeleteConfirmLabel') }}
          </label>
          <input
            type="text"
            v-model="batchDeleteConfirmText"
            :placeholder="$t('hosts.batchDeleteConfirmPlaceholder')"
            class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-red-500 focus:border-red-500"
            @keyup.enter="batchDeleteConfirmText === 'DELETE' && handleBatchDelete()"
          />
          <p class="mt-1 text-xs text-gray-500">
            {{ $t('hosts.batchDeleteConfirmHint') }}
          </p>
        </div>

        <div class="bg-yellow-50 border border-yellow-200 rounded-md p-3">
          <p class="text-xs text-yellow-800">
            {{ $t('hosts.batchDeleteIrreversible') }}
          </p>
        </div>
      </div>
      <template #footer>
        <button
          type="button"
          @click="closeBatchDeleteModal"
          class="mt-3 inline-flex w-full justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 sm:mt-0 sm:w-auto"
        >
          {{ $t('common.cancel') }}
        </button>
        <button
          type="button"
          @click="handleBatchDelete"
          :disabled="saving || batchDeleteConfirmText !== 'DELETE'"
          class="inline-flex w-full justify-center rounded-md bg-red-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-red-500 sm:ml-3 sm:w-auto disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {{ saving ? $t('common.deleting') : $t('hosts.batchDeleteButton') }}
        </button>
      </template>
    </Modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import { hostsApi, type Host } from '@/api/hosts'
import { importApi } from '@/api/import'
import { tagsApi } from '@/api/tags'
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
  ChevronRightIcon,
  FunnelIcon,
  InformationCircleIcon,
  GlobeAltIcon,
  CircleStackIcon,
  LockClosedIcon,
  XMarkIcon,
  TagIcon,
  ExclamationTriangleIcon,
} from '@heroicons/vue/24/outline'
import { Menu, MenuButton, MenuItem, MenuItems } from '@headlessui/vue'

const { t } = useI18n()
const toastStore = useToastStore()
const settingsStore = useSettingsStore()

const hosts = ref<Host[]>([])
const loading = ref(false)
const loadingTree = ref(false)
const searchQuery = ref('')
const searchField = ref('all')
const selectedHosts = ref<number[]>([])
const viewMode = ref<'list' | 'tree'>('list')
const treeData = ref<any[]>([])
// Track expanded/collapsed state for platforms and ESXi hosts
const expandedPlatforms = ref<Set<number>>(new Set())
const expandedESXiHosts = ref<Set<string>>(new Set())
const showCreateModal = ref(false)
const showDetailModal = ref(false)
const showImportModal = ref(false)
const showMissingCredentialsModal = ref(false)
const showBatchCredentialsModal = ref(false)
const showTagManagementModal = ref(false)
const tagManagementTarget = ref<Host | null>(null)
const selectedTagIds = ref<number[]>([])
const showBatchTagManagementModal = ref(false)
const batchSelectedTagIds = ref<number[]>([])
const batchHostTagsMap = ref<Map<number, boolean>>(new Map()) // Track which tags are currently on hosts
const showBatchDeleteModal = ref(false)
const batchDeleteConfirmText = ref('')
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
const filters = ref({
  os_type: '',
  device_type: '',
  collection_status: '',
  source: '',
  is_physical: '',
  tag_id: '',
})
const availableTags = ref<Array<{id: number, name: string, color?: string}>>([])
const showFilters = ref(false)
const showFieldDropdown = ref(false)
const showValueDropdown = ref(false)
const searchContainer = ref<HTMLElement | null>(null)

const searchFields = computed(() => [
  { value: 'all', label: t('hosts.searchAll') },
  { value: 'ip', label: t('hosts.ip') },
  { value: 'hostname', label: t('hosts.hostname') },
  { value: 'mac', label: t('hosts.macAddress') },
  { value: 'vendor', label: t('hosts.vendor') },
  { value: 'tag', label: t('hosts.tags') },
])

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
    const params: any = {
      page,
      per_page: perPage.value,
    }
    
    // Add search with field
    if (searchQuery.value) {
      if (searchField.value === 'tag') {
        // For tag search, find tag ID by name
        const tag = availableTags.value.find(t => t.name === searchQuery.value)
        if (tag) {
          params.tag_id = tag.id
        }
      } else if (searchField.value === 'all') {
        // Search all fields
        params.search = searchQuery.value
      } else {
        // Search specific field
        params.search = searchQuery.value
        params.search_field = searchField.value
      }
    }
    
    // Add filters
    if (filters.value.os_type) params.os_type = filters.value.os_type
    if (filters.value.device_type) params.device_type = filters.value.device_type
    if (filters.value.collection_status) params.collection_status = filters.value.collection_status
    if (filters.value.source) params.source = filters.value.source
    if (filters.value.is_physical) params.is_physical = filters.value.is_physical
    if (filters.value.tag_id) params.tag_id = parseInt(filters.value.tag_id)
    
    const response: any = await hostsApi.getHosts(params)
    
    // API client interceptor returns response.data directly
    // So response is already the data object: { code: 200, data: [...], pagination: {...} }
    if (response && response.code === 200) {
      hosts.value = Array.isArray(response.data) ? response.data : []
      pagination.value = response.pagination || null
    } else {
      // Fallback: handle unexpected response format
      hosts.value = []
      pagination.value = null
      console.warn('Unexpected response format from getHosts:', response)
    }
  } catch (error: any) {
    toastStore.error(error.response?.data?.message || t('messages.loadFailed'))
  } finally {
    loading.value = false
  }
}

const getSearchPlaceholder = () => {
  if (searchField.value === 'all') {
    return t('hosts.searchPlaceholder')
  }
  const fieldMap: Record<string, string> = {
    'ip': t('hosts.searchIPPlaceholder'),
    'hostname': t('hosts.searchHostnamePlaceholder'),
    'mac': t('hosts.searchMACPlaceholder'),
    'vendor': t('hosts.searchVendorPlaceholder'),
  }
  return fieldMap[searchField.value] || t('hosts.searchPlaceholder')
}

const getFieldLabel = (field: string) => {
  const fieldMap: Record<string, string> = {
    'ip': t('hosts.ip'),
    'hostname': t('hosts.hostname'),
    'mac': t('hosts.macAddress'),
    'vendor': t('hosts.vendor'),
    'tag': t('hosts.tags'),
  }
  return fieldMap[field] || field
}

const selectField = (field: string) => {
  searchField.value = field
  searchQuery.value = ''
  showFieldDropdown.value = false
  
  // If tag field, automatically show value dropdown after a short delay
  if (field === 'tag') {
    // Use nextTick to ensure DOM is updated
    setTimeout(() => {
      showValueDropdown.value = true
    }, 150)
  }
}

const selectTagValue = (tagName: string) => {
  searchQuery.value = tagName
  showValueDropdown.value = false
  loadHosts(1)
}

const clearField = () => {
  searchField.value = 'all'
  searchQuery.value = ''
  loadHosts(1)
}

const clearSearch = () => {
  if (searchQuery.value) {
    // Clear search value only
    searchQuery.value = ''
    if (searchField.value === 'tag') {
      showValueDropdown.value = false
    }
    loadHosts(1)
  } else {
    // Clear field selection
    clearField()
  }
}

const handleInputFocus = () => {
  if (searchField.value === 'all') {
    showFieldDropdown.value = true
  }
}

const handleSearchContainerClick = () => {
  // If clicking on the input or container, show field dropdown if field is 'all'
  if (searchField.value === 'all' && !showFieldDropdown.value) {
    showFieldDropdown.value = true
  }
}

const clearFilters = () => {
  filters.value = {
    os_type: '',
    device_type: '',
    collection_status: '',
    source: '',
    is_physical: '',
    tag_id: '',
  }
  loadHosts(1)
}

const removeFilter = (key: string) => {
  if (key === 'tag_id') {
    filters.value.tag_id = ''
  } else {
    (filters.value as any)[key] = ''
  }
  loadHosts(1)
}

const applyQuickFilter = (status: string) => {
  filters.value.collection_status = status
  showFilters.value = false
  loadHosts(1)
}

const activeFilters = computed(() => {
  const result: Array<{key: string, label: string, value: string}> = []
  
  if (filters.value.os_type) {
    result.push({
      key: 'os_type',
      label: t('hosts.osType'),
      value: filters.value.os_type.charAt(0).toUpperCase() + filters.value.os_type.slice(1)
    })
  }
  
  if (filters.value.device_type) {
    result.push({
      key: 'device_type',
      label: t('hosts.deviceType'),
      value: filters.value.device_type === 'host' ? t('hosts.host') : t('hosts.networkDevice')
    })
  }
  
  if (filters.value.collection_status) {
    const statusMap: Record<string, string> = {
      'not_collected': t('hosts.notCollected'),
      'collecting': t('hosts.collecting'),
      'completed': t('common.completed'),
      'failed': t('common.failed'),
    }
    result.push({
      key: 'collection_status',
      label: t('hosts.collectionStatus'),
      value: statusMap[filters.value.collection_status] || filters.value.collection_status
    })
  }
  
  if (filters.value.source) {
    result.push({
      key: 'source',
      label: t('hosts.source'),
      value: getSourceText(filters.value.source)
    })
  }
  
  if (filters.value.is_physical) {
    result.push({
      key: 'is_physical',
      label: t('hosts.deviceNature'),
      value: filters.value.is_physical === 'true' ? t('hosts.physical') : t('hosts.virtual')
    })
  }
  
  if (filters.value.tag_id) {
    const tag = availableTags.value.find(t => t.id === parseInt(filters.value.tag_id))
    if (tag) {
      result.push({
        key: 'tag_id',
        label: t('hosts.tags'),
        value: tag.name
      })
    }
  }
  
  return result
})

const hasActiveFilters = computed(() => {
  return activeFilters.value.length > 0
})

const getUsageColor = (ratio: number | null | undefined) => {
  if (!ratio) return 'bg-gray-400'
  const usage = 1 - ratio
  if (usage >= 0.9) return 'bg-red-500'
  if (usage >= 0.7) return 'bg-yellow-500'
  return 'bg-green-500'
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
    
    // Auto-expand all platforms and ESXi hosts by default
    if (treeData.value.length > 0) {
      treeData.value.forEach((platform: any) => {
        if (platform.platform_id) {
          expandedPlatforms.value.add(platform.platform_id)
        }
        if (platform.esxi_hosts) {
          platform.esxi_hosts.forEach((esxi: any) => {
            if (esxi.esxi_name) {
              expandedESXiHosts.value.add(esxi.esxi_name)
            }
          })
        }
      })
    }
    
    // Update checkbox indeterminate states after loading
    nextTick(() => {
      updateCheckboxIndeterminateStates()
    })
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
  
  // Update indeterminate state after selection change
  nextTick(() => {
    updateCheckboxIndeterminateStates()
  })
}

const toggleSelectAll = () => {
  if (allSelected.value) {
    selectedHosts.value = []
  } else {
    selectedHosts.value = hosts.value.map(h => h.id!).filter(Boolean)
  }
}

// Platform expand/collapse
const togglePlatformExpand = (platformId: number) => {
  if (expandedPlatforms.value.has(platformId)) {
    expandedPlatforms.value.delete(platformId)
  } else {
    expandedPlatforms.value.add(platformId)
  }
}

// ESXi host expand/collapse
const toggleESXiExpand = (esxiName: string) => {
  if (expandedESXiHosts.value.has(esxiName)) {
    expandedESXiHosts.value.delete(esxiName)
  } else {
    expandedESXiHosts.value.add(esxiName)
  }
}

// Get all VM IDs from a platform
const getPlatformVMIds = (platform: any): number[] => {
  const vmIds: number[] = []
  for (const esxi of platform.esxi_hosts || []) {
    for (const vm of esxi.vms || []) {
      if (vm.id) {
        vmIds.push(vm.id)
      }
    }
  }
  return vmIds
}

// Get all VM IDs from an ESXi host
const getESXiVMIds = (esxi: any): number[] => {
  const vmIds: number[] = []
  for (const vm of esxi.vms || []) {
    if (vm.id) {
      vmIds.push(vm.id)
    }
  }
  return vmIds
}

// Check if all VMs in a platform are selected
const isPlatformAllSelected = (platform: any): boolean => {
  const vmIds = getPlatformVMIds(platform)
  if (vmIds.length === 0) return false
  return vmIds.every(id => selectedHosts.value.includes(id))
}

// Check if some (but not all) VMs in a platform are selected
const isPlatformPartiallySelected = (platform: any): boolean => {
  const vmIds = getPlatformVMIds(platform)
  if (vmIds.length === 0) return false
  const selectedCount = vmIds.filter(id => selectedHosts.value.includes(id)).length
  return selectedCount > 0 && selectedCount < vmIds.length
}

// Toggle selection for all VMs in a platform
const togglePlatformSelection = (platform: any) => {
  const vmIds = getPlatformVMIds(platform)
  const allSelected = isPlatformAllSelected(platform)
  
  if (allSelected) {
    // Deselect all
    vmIds.forEach(id => {
      const index = selectedHosts.value.indexOf(id)
      if (index > -1) {
        selectedHosts.value.splice(index, 1)
      }
    })
  } else {
    // Select all
    vmIds.forEach(id => {
      if (!selectedHosts.value.includes(id)) {
        selectedHosts.value.push(id)
      }
    })
  }
  
  // Update indeterminate state after selection change
  nextTick(() => {
    updateCheckboxIndeterminateStates()
  })
}

// Check if all VMs in an ESXi host are selected
const isESXiAllSelected = (esxi: any): boolean => {
  const vmIds = getESXiVMIds(esxi)
  if (vmIds.length === 0) return false
  return vmIds.every(id => selectedHosts.value.includes(id))
}

// Check if some (but not all) VMs in an ESXi host are selected
const isESXiPartiallySelected = (esxi: any): boolean => {
  const vmIds = getESXiVMIds(esxi)
  if (vmIds.length === 0) return false
  const selectedCount = vmIds.filter(id => selectedHosts.value.includes(id)).length
  return selectedCount > 0 && selectedCount < vmIds.length
}

// Toggle selection for all VMs in an ESXi host
const toggleESXiSelection = (esxi: any) => {
  const vmIds = getESXiVMIds(esxi)
  const allSelected = isESXiAllSelected(esxi)
  
  if (allSelected) {
    // Deselect all
    vmIds.forEach(id => {
      const index = selectedHosts.value.indexOf(id)
      if (index > -1) {
        selectedHosts.value.splice(index, 1)
      }
    })
  } else {
    // Select all
    vmIds.forEach(id => {
      if (!selectedHosts.value.includes(id)) {
        selectedHosts.value.push(id)
      }
    })
  }
  
  // Update indeterminate state after selection change
  nextTick(() => {
    updateCheckboxIndeterminateStates()
  })
}

// Store checkbox refs for updating indeterminate state
const platformCheckboxRefs = new Map<number, HTMLInputElement>()
const esxiCheckboxRefs = new Map<string, HTMLInputElement>()

// Update all checkbox indeterminate states
const updateCheckboxIndeterminateStates = () => {
  // Update platform checkboxes
  treeData.value.forEach((platform: any) => {
    if (platform.platform_id) {
      const checkbox = platformCheckboxRefs.get(platform.platform_id)
      if (checkbox) {
        checkbox.indeterminate = isPlatformPartiallySelected(platform)
      }
    }
  })
  
  // Update ESXi checkboxes
  treeData.value.forEach((platform: any) => {
    if (platform.esxi_hosts) {
      platform.esxi_hosts.forEach((esxi: any) => {
        if (esxi.esxi_name) {
          const checkbox = esxiCheckboxRefs.get(esxi.esxi_name)
          if (checkbox) {
            checkbox.indeterminate = isESXiPartiallySelected(esxi)
          }
        }
      })
    }
  })
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
    // getHost returns data with include_details=true, so it should have disks, partitions, network_interfaces
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

const loadTags = async () => {
  try {
    const response: any = await tagsApi.getTags()
    if (response && response.code === 200) {
      availableTags.value = response.data || []
    } else if (Array.isArray(response)) {
      availableTags.value = response
    } else if (response && response.data) {
      availableTags.value = response.data
    }
  } catch (error: any) {
    // Silently fail - tags are optional
    console.warn('Failed to load tags:', error)
  }
}

const showHostTagManagementModal = (host: Host) => {
  tagManagementTarget.value = host
  selectedTagIds.value = host.tags?.map(tag => tag.id!).filter(Boolean) || []
  showTagManagementModal.value = true
}

const closeTagManagementModal = () => {
  showTagManagementModal.value = false
  tagManagementTarget.value = null
  selectedTagIds.value = []
}

const saveHostTags = async () => {
  if (!tagManagementTarget.value || !tagManagementTarget.value.id) return
  
  saving.value = true
  try {
    const hostId = tagManagementTarget.value.id
    const currentTagIds = tagManagementTarget.value.tags?.map(tag => tag.id!).filter(Boolean) || []
    
    // Remove tags that are not in selectedTagIds
    for (const tagId of currentTagIds) {
      if (!selectedTagIds.value.includes(tagId)) {
        await tagsApi.removeHostTag(hostId, tagId)
      }
    }
    
    // Add tags that are in selectedTagIds but not in currentTagIds
    const tagsToAdd = selectedTagIds.value.filter(tagId => !currentTagIds.includes(tagId))
    if (tagsToAdd.length > 0) {
      await tagsApi.addHostTags(hostId, tagsToAdd)
    }
    
    toastStore.success(t('hosts.tagsUpdated'))
    closeTagManagementModal()
    loadHosts(pagination.value?.page || 1)
  } catch (error: any) {
    toastStore.error(error.response?.data?.message || t('messages.saveFailed'))
  } finally {
    saving.value = false
  }
}

const removeHostTag = async (hostId: number, tagId: number) => {
  try {
    await tagsApi.removeHostTag(hostId, tagId)
    toastStore.success(t('hosts.tagRemoved'))
    loadHosts(pagination.value?.page || 1)
  } catch (error: any) {
    toastStore.error(error.response?.data?.message || t('messages.operationFailed'))
  }
}

const openBatchTagManagementModal = async () => {
  if (selectedHosts.value.length === 0) {
    toastStore.warning(t('hosts.noHostsSelected'))
    return
  }
  
  // Load current tags from selected hosts and pre-select them
  await loadBatchHostCurrentTags()
  showBatchTagManagementModal.value = true
}

const closeBatchTagManagementModal = () => {
  showBatchTagManagementModal.value = false
  batchSelectedTagIds.value = []
  batchHostTagsMap.value.clear()
}

const loadBatchHostCurrentTags = async () => {
  try {
    // Get all tags from selected hosts
    const hostTagsSet = new Set<number>()
    batchHostTagsMap.value.clear()
    
    for (const hostId of selectedHosts.value) {
      try {
        const host = hosts.value.find(h => h.id === hostId)
        if (host && host.tags) {
          for (const tag of host.tags) {
            if (tag.id) {
              hostTagsSet.add(tag.id)
              // If tag exists on at least one host, mark it
              if (!batchHostTagsMap.value.has(tag.id)) {
                batchHostTagsMap.value.set(tag.id, true)
              }
            }
          }
        }
      } catch (error) {
        console.error(`Failed to load tags for host ${hostId}:`, error)
      }
    }
    
    // Pre-select tags that exist on any selected host
    batchSelectedTagIds.value = Array.from(hostTagsSet)
  } catch (error: any) {
    console.error('Failed to load batch host current tags:', error)
    batchSelectedTagIds.value = []
  }
}

const saveBatchHostTags = async () => {
  if (selectedHosts.value.length === 0) {
    return
  }
  
  saving.value = true
  try {
    let addSuccessCount = 0
    let removeSuccessCount = 0
    let failCount = 0
    
    // Get tags that need to be added and removed
    // Add: tags selected but not currently on hosts
    const tagsToAdd = batchSelectedTagIds.value.filter(tagId => !batchHostTagsMap.value.has(tagId))
    // Remove: tags currently on hosts but not selected
    const tagsToRemove = Array.from(batchHostTagsMap.value.keys()).filter(tagId => !batchSelectedTagIds.value.includes(tagId))
    
    // Process each host
    for (const hostId of selectedHosts.value) {
      try {
        // Add new tags
        if (tagsToAdd.length > 0) {
          try {
            await tagsApi.addHostTags(hostId, tagsToAdd)
          } catch (error: any) {
            console.error(`Failed to add tags to host ${hostId}:`, error)
          }
        }
        
        // Remove unselected tags
        for (const tagId of tagsToRemove) {
          try {
            await tagsApi.removeHostTag(hostId, tagId)
          } catch (error: any) {
            // Ignore errors if tag doesn't exist on host
            console.warn(`Failed to remove tag ${tagId} from host ${hostId}:`, error)
          }
        }
        
        addSuccessCount++
        removeSuccessCount++
      } catch (error: any) {
        console.error(`Failed to update tags for host ${hostId}:`, error)
        failCount++
      }
    }
    
    // Show success messages only if there were changes
    if (tagsToAdd.length === 0 && tagsToRemove.length === 0) {
      toastStore.info(t('hosts.noTagChanges'))
    } else {
      const messages: string[] = []
      if (tagsToAdd.length > 0 && addSuccessCount > 0) {
        messages.push(t('hosts.batchTagsAdded', { count: addSuccessCount }))
      }
      if (tagsToRemove.length > 0 && removeSuccessCount > 0) {
        messages.push(t('hosts.batchTagsRemoved', { count: removeSuccessCount }))
      }
      if (messages.length > 0) {
        toastStore.success(messages.join(', '))
      }
    }
    if (failCount > 0) {
      toastStore.error(t('hosts.batchTagsFailed', { count: failCount }))
    }
    
    closeBatchTagManagementModal()
    selectedHosts.value = []
    loadHosts(pagination.value?.page || 1)
  } catch (error: any) {
    toastStore.error(error.response?.data?.message || t('messages.operationFailed'))
  } finally {
    saving.value = false
  }
}

const openBatchDeleteModal = () => {
  if (selectedHosts.value.length === 0) {
    toastStore.warning(t('hosts.noHostsSelected'))
    return
  }
  batchDeleteConfirmText.value = ''
  showBatchDeleteModal.value = true
}

const closeBatchDeleteModal = () => {
  showBatchDeleteModal.value = false
  batchDeleteConfirmText.value = ''
}

const handleBatchDelete = async () => {
  if (selectedHosts.value.length === 0) {
    return
  }
  
  if (batchDeleteConfirmText.value !== 'DELETE') {
    toastStore.error(t('hosts.batchDeleteConfirmError'))
    return
  }
  
  saving.value = true
  try {
    const response: any = await hostsApi.batchDeleteHosts(selectedHosts.value)
    
    if (response && response.code === 200) {
      const deletedCount = response.data?.deleted_count || 0
      const failedIds = response.data?.failed_ids || []
      
      if (deletedCount > 0) {
        toastStore.success(t('hosts.batchDeleteSuccess', { count: deletedCount }))
      }
      if (failedIds.length > 0) {
        toastStore.error(t('hosts.batchDeleteFailed', { count: failedIds.length }))
      }
      
      closeBatchDeleteModal()
      selectedHosts.value = []
      loadHosts(pagination.value?.page || 1)
    } else {
      toastStore.error(response?.message || t('messages.operationFailed'))
    }
  } catch (error: any) {
    toastStore.error(error.response?.data?.message || t('messages.operationFailed'))
  } finally {
    saving.value = false
  }
}

// Close dropdowns when clicking outside
const handleClickOutside = (e: MouseEvent) => {
  if (searchContainer.value && !searchContainer.value.contains(e.target as Node)) {
    showFieldDropdown.value = false
    showValueDropdown.value = false
  }
}

onMounted(() => {
  loadHosts()
  loadTags()
  if (viewMode.value === 'tree') {
    loadTreeData()
  }
  
  // Setup click outside handler for search dropdowns
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>
