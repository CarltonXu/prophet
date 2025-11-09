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
        <div v-else class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
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
                <td class="px-6 py-4 text-sm text-gray-500 max-w-[200px] truncate">{{ host.hostname || '-' }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ host.os_type || '-' }}</td>
                <td class="px-6 py-4 text-sm text-gray-500">
                  <div class="flex flex-col">
                    <span class="truncate max-w-[220px]">{{ host.cpu_info || '-' }}</span>
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

      <div
        :class="[
          'bg-white shadow rounded-lg transition-all duration-200 ease-in-out',
          isCanvasFullscreen ? 'fixed inset-0 z-50 rounded-none shadow-xl flex flex-col' : ''
        ]"
      >
        <div class="flex items-center justify-between border-b border-gray-200 px-6 py-4">
          <div>
            <h2 class="text-lg font-medium text-gray-900">{{ $t('applications.relationshipCanvas') }}</h2>
            <p class="text-sm text-gray-500">{{ $t('applications.relationshipCanvasSubtitle') }}</p>
          </div>
          <div class="flex items-center gap-2 text-xs text-gray-400">
            <span class="inline-flex items-center gap-1">
              <span class="inline-block h-3 w-3 rounded-full bg-blue-500"></span>
              <span>{{ $t('applications.legendPhysical') }}</span>
            </span>
            <span class="inline-flex items-center gap-1">
              <span class="inline-block h-3 w-3 rounded-full bg-emerald-500"></span>
              <span>{{ $t('applications.legendVirtual') }}</span>
            </span>
            <span class="inline-flex items-center gap-1">
              <span class="inline-block h-3 w-3 rounded-full bg-orange-500"></span>
              <span>{{ $t('applications.legendNetwork') }}</span>
            </span>
          </div>
        </div>
        <div :class="[
            'flex flex-wrap items-center justify-between gap-3 border-b border-gray-100 px-6 py-3 text-xs text-gray-500',
            isCanvasFullscreen ? 'bg-white' : ''
          ]">
          <div class="flex items-center gap-2">
            <button
              @click="applyLayout('grid')"
              :class="[
                'rounded-md border px-3 py-1 font-medium transition',
                selectedLayout === 'grid'
                  ? 'border-blue-500 bg-blue-50 text-blue-600'
                  : 'border-gray-300 bg-white text-gray-600 hover:bg-gray-50'
              ]"
            >
              {{ $t('applications.canvasLayoutGrid') }}
            </button>
            <button
              @click="applyLayout('horizontal')"
              :class="[
                'rounded-md border px-3 py-1 font-medium transition',
                selectedLayout === 'horizontal'
                  ? 'border-blue-500 bg-blue-50 text-blue-600'
                  : 'border-gray-300 bg-white text-gray-600 hover:bg-gray-50'
              ]"
            >
              {{ $t('applications.canvasLayoutHorizontal') }}
            </button>
            <button
              @click="applyLayout('vertical')"
              :class="[
                'rounded-md border px-3 py-1 font-medium transition',
                selectedLayout === 'vertical'
                  ? 'border-blue-500 bg-blue-50 text-blue-600'
                  : 'border-gray-300 bg-white text-gray-600 hover:bg-gray-50'
              ]"
            >
              {{ $t('applications.canvasLayoutVertical') }}
            </button>
          </div>
          <div class="flex items-center gap-2">
            <button
              @click="zoomOut"
              class="rounded-md border border-gray-300 bg-white px-2 py-1 font-semibold text-gray-600 transition hover:bg-gray-50"
            >
              −
            </button>
            <button
              @click="zoomIn"
              class="rounded-md border border-gray-300 bg-white px-2 py-1 font-semibold text-gray-600 transition hover:bg-gray-50"
            >
              +
            </button>
            <button
              @click="fitView"
              class="rounded-md border border-gray-300 bg-white px-3 py-1 font-medium text-gray-600 transition hover:bg-gray-50"
            >
              {{ $t('applications.canvasFitView') }}
            </button>
            <button
              @click="resetZoom"
              class="rounded-md border border-gray-300 bg-white px-3 py-1 font-medium text-gray-600 transition hover:bg-gray-50"
            >
              {{ $t('applications.canvasResetZoom') }}
            </button>
            <button
              @click="saveCanvasLayout"
              :disabled="isSavingGraph"
              class="inline-flex items-center gap-1 rounded-md border border-blue-500 bg-blue-50 px-3 py-1 font-medium text-blue-600 transition hover:bg-blue-100 disabled:cursor-not-allowed disabled:opacity-60"
            >
              <ArrowDownOnSquareIcon class="h-4 w-4" />
              <span>{{ isSavingGraph ? $t('common.saving') : $t('applications.canvasSave') }}</span>
            </button>
            <button
              @click="exportCanvasLayout"
              :disabled="isExportingGraph"
              class="inline-flex items-center gap-1 rounded-md border border-gray-300 bg-white px-3 py-1 font-medium text-gray-600 transition hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-60"
            >
              <ArrowDownTrayIcon class="h-4 w-4" />
              <span>{{ isExportingGraph ? $t('applications.canvasExporting') : $t('applications.canvasExport') }}</span>
            </button>
            <button
              @click="exportCanvasAsImage"
              class="inline-flex items-center gap-1 rounded-md border border-gray-300 bg-white px-3 py-1 font-medium text-gray-600 transition hover:bg-gray-50"
            >
              <PhotoIcon class="h-4 w-4" />
              <span>{{ $t('applications.canvasExportImage') }}</span>
            </button>
            <button
              @click="toggleCanvasFullscreen"
              class="rounded-md border border-gray-300 bg-white px-3 py-1 font-medium text-gray-600 transition hover:bg-gray-50"
            >
              {{ isCanvasFullscreen ? $t('applications.canvasExitFullscreen') : $t('applications.canvasFullscreen') }}
            </button>
          </div>
        </div>
        <div :class="['flex', isCanvasFullscreen ? 'flex-1 min-h-0 h-full' : 'h-[560px]']">
          <aside class="w-72 border-r border-gray-200 bg-gray-50 flex flex-col">
            <div class="flex-1 overflow-y-auto p-4 space-y-6">
              <div>
                <h4 class="text-xs font-semibold uppercase tracking-wide text-gray-500">
                  {{ $t('applications.resourcePaletteTitle') }}
                </h4>
                <p class="mt-1 text-xs text-gray-500">{{ $t('applications.resourcePaletteHint') }}</p>
                <div class="mt-3 grid grid-cols-2 gap-2">
                  <button
                    v-for="item in resourceLibrary"
                    :key="item.key"
                    class="flex items-center gap-2 rounded-md border border-dashed border-gray-300 bg-white px-3 py-2 text-xs text-left transition hover:border-blue-400 hover:bg-blue-50"
                    draggable="true"
                    @dragstart="onResourceDragStart(item, $event)"
                    @dragend="onResourceDragEnd"
                    @click="createResourceNode(item)"
                  >
                    <span
                      class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-white"
                      :style="{ backgroundColor: item.color }"
                    >
                      <component :is="RESOURCE_ICON_COMPONENTS[item.key]" class="h-4 w-4" />
                    </span>
                    <span class="flex-1 min-w-0">
                      <p class="font-semibold text-gray-700 truncate">{{ item.label }}</p>
                      <p class="text-[11px] text-gray-500 truncate">{{ item.description }}</p>
                    </span>
                  </button>
                </div>
              </div>

              <div>
                <h4 class="text-xs font-semibold uppercase tracking-wide text-gray-500">
                  {{ $t('applications.currentHosts') }}
                </h4>
                <ul class="mt-2 space-y-1 text-xs text-gray-600">
                  <li
                    v-for="host in hosts"
                    :key="host.id"
                    class="flex items-center justify-between rounded-md border border-gray-200 bg-white px-3 py-2"
                  >
                    <span class="truncate">{{ host.hostname || host.ip || (`#${host.id}`) }}</span>
                    <span class="ml-2 text-[10px] uppercase text-gray-400">{{ host.device_type || 'host' }}</span>
                  </li>
                  <li v-if="hosts.length === 0" class="rounded-md border border-dashed border-gray-200 bg-white px-3 py-2 text-gray-400">
                    {{ $t('applications.noHosts') }}
                  </li>
                </ul>
              </div>
            </div>
            <div class="border-t border-gray-200 bg-white p-4">
              <div>
                <label class="text-xs font-medium text-gray-600">{{ $t('applications.searchHosts') }}</label>
                <div class="relative mt-2">
                  <MagnifyingGlassIcon class="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
                  <input
                    v-model="hostLibraryKeyword"
                    type="text"
                    :placeholder="$t('applications.hostSearchPlaceholder')"
                    class="w-full rounded-md border border-gray-300 bg-white py-2 pl-9 pr-3 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                  />
                </div>
              </div>
              <div class="mt-3 max-h-52 overflow-y-auto space-y-2 pr-1">
                <div
                  v-for="host in filteredAvailableHostsForCanvas"
                  :key="host.id"
                  class="flex items-start justify-between rounded-md border border-gray-200 bg-gray-50 px-3 py-2 text-xs"
                >
                  <div class="flex-1">
                    <p class="font-semibold text-gray-700 truncate">{{ host.ip }}</p>
                    <p class="text-gray-500 truncate">{{ host.hostname || $t('applications.unknown') }}</p>
                    <p v-if="host.vendor" class="text-[10px] uppercase text-gray-400 mt-1 truncate">{{ host.vendor }}</p>
                  </div>
                  <button
                    @click="addHostFromLibrary(host.id)"
                    :disabled="hostLibraryAddingId === host.id"
                    class="ml-3 inline-flex items-center rounded-md bg-blue-600 px-2 py-1 text-[11px] font-semibold text-white transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-60"
                  >
                    {{ hostLibraryAddingId === host.id ? $t('applications.adding') : $t('applications.add') }}
                  </button>
                </div>
                <p v-if="filteredAvailableHostsForCanvas.length === 0" class="rounded-md border border-dashed border-gray-300 bg-white px-3 py-2 text-xs text-gray-400">
                  {{ $t('applications.noAvailableHosts') }}
                </p>
              </div>
            </div>
          </aside>
          <div
            :class="['flex-1 relative', isCanvasFullscreen ? 'min-h-0' : '']"
            ref="canvasContainerRef"
            @dragover="handleCanvasDragOver"
            @drop="handleCanvasDrop"
          >
            <ApplicationCanvas
              ref="canvasRef"
              :nodes="canvasNodes"
              :edges="canvasEdges"
              @canvas:ready="handleCanvasReady"
              @node:click="handleCanvasNodeClick"
              @edge:click="handleCanvasEdgeClick"
              @node:moved="handleCanvasNodeMoved"
              @node:removed="handleCanvasNodeRemoved"
              @edge:added="handleCanvasEdgeAdded"
              @edge:removed="handleCanvasEdgeRemoved"
              @blank:click="handleCanvasBlankClick"
            />
            <div v-if="canvasNodes.length === 0" class="pointer-events-none absolute inset-0 flex items-center justify-center bg-white/70">
              <div class="text-center text-sm text-gray-500">
                <ShareIcon class="mx-auto mb-3 h-12 w-12 text-gray-300" />
                <p>{{ $t('applications.noRelationshipData') }}</p>
              </div>
            </div>
          </div>
          <aside class="w-72 border-l border-gray-200 bg-white">
            <div class="h-full overflow-y-auto p-4 space-y-4">
              <div>
                <h3 class="text-sm font-semibold text-gray-700">{{ $t('applications.canvasInspector') }}</h3>
                <p class="mt-1 text-xs text-gray-500">{{ $t('applications.canvasInspectorHint') }}</p>
              </div>
              <div v-if="selectedCanvasNode" class="space-y-4">
                <div class="rounded-md border border-blue-100 bg-blue-50 p-3">
                  <p class="text-xs font-semibold uppercase tracking-wide text-blue-600">
                    {{ $t('applications.selectedNode') }}
                  </p>
                  <p class="mt-1 text-sm font-medium text-blue-900 truncate">{{ selectedCanvasNode.label }}</p>
                  <p class="text-xs text-blue-500">
                    {{ selectedCanvasNode.data?.displayStatus || selectedCanvasNode.status || selectedCanvasNode.type }}
                  </p>
                </div>
                <div
                  v-if="selectedHostDetails.length > 0"
                  class="rounded-md border border-gray-200 bg-gray-50 p-3"
                >
                  <dl class="grid grid-cols-2 gap-x-4 gap-y-2 text-xs">
                    <div
                      v-for="detail in selectedHostDetails"
                      :key="`${detail.label}-${detail.value}`"
                      class="min-w-0"
                    >
                      <dt class="text-gray-500 font-medium truncate">{{ detail.label }}</dt>
                      <dd class="text-gray-900 truncate" :title="detail.value">
                        {{ detail.value || '-' }}
                      </dd>
                    </div>
                  </dl>
                </div>
                <div v-if="selectedCanvasNode.bindingHostId" class="space-y-2">
                  <div>
                    <label class="block text-xs font-medium text-gray-600">
                      {{ $t('applications.bindHost') }}
                    </label>
                    <select
                      v-model="nodeBindingHostId"
                      class="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                    >
                      <option value="">
                        {{ $t('applications.selectHostPlaceholder') }}
                      </option>
                      <option
                        v-for="host in selectableHosts"
                        :key="host.id"
                        :value="host.id"
                      >
                        {{ host.ip }} · {{ host.hostname || $t('applications.unknown') }}
                      </option>
                    </select>
                  </div>
                  <div class="flex flex-col gap-2">
                    <button
                      @click="updateNodeBinding"
                      :disabled="updatingNodeBinding || !canUpdateBinding"
                      class="inline-flex items-center justify-center rounded-md bg-blue-600 px-3 py-2 text-sm font-semibold text-white shadow-sm transition-colors hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-60"
                    >
                      {{ updatingNodeBinding ? $t('common.saving') : $t('applications.updateBinding') }}
                    </button>
                    <button
                      @click="deleteSelectedNode"
                      class="inline-flex items-center justify-center rounded-md border border-red-200 px-3 py-2 text-sm font-semibold text-red-600 transition-colors hover:bg-red-50"
                    >
                      {{ $t('applications.removeHostFromCanvas') }}
                    </button>
                  </div>
                </div>
                <div class="space-y-3">
                  <div>
                    <label class="block text-xs font-medium text-gray-600">{{ $t('applications.resourceName') }}</label>
                    <input
                      v-model="resourceLabel"
                      type="text"
                      class="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-purple-500 focus:outline-none focus:ring-1 focus:ring-purple-500"
                    />
                  </div>
                  <button
                    @click="updateResourceNodeLabel"
                    :disabled="!resourceLabel || resourceLabel.trim() === selectedCanvasNode.label"
                    class="inline-flex items-center justify-center rounded-md bg-purple-600 px-3 py-2 text-sm font-semibold text-white shadow-sm transition-colors hover:bg-purple-500 disabled:cursor-not-allowed disabled:opacity-60"
                  >
                    {{ $t('applications.updateResource') }}
                  </button>
                  <div>
                    <label class="block text-xs font-medium text-gray-600">
                      {{ $t('applications.resourceColor') }}
                    </label>
                    <div class="mt-2 flex flex-wrap gap-2">
                      <button
                        v-for="color in COLOR_PRESETS"
                        :key="color"
                        type="button"
                        @click="updateSelectedNodeColor(color)"
                        :class="[
                          'h-7 w-7 rounded-full border transition',
                          selectedCanvasNode.color === color ? 'ring-2 ring-offset-1 ring-blue-500 border-blue-500' : 'border-gray-200'
                        ]"
                        :style="{ backgroundColor: color }"
                        :title="color"
                      />
                    </div>
                  </div>
                  <button
                    @click="duplicateSelectedResource"
                    class="inline-flex items-center justify-center rounded-md border border-gray-300 bg-white px-3 py-2 text-sm font-semibold text-gray-700 transition hover:bg-gray-50"
                  >
                    {{ $t('applications.duplicateResource') }}
                  </button>
                  <p class="text-[11px] text-gray-500">
                    {{ $t('applications.resourceHint') }}
                  </p>
                </div>
              </div>
              <div v-else-if="selectedCanvasEdge" class="space-y-4">
                <div class="rounded-md border border-purple-100 bg-purple-50 p-3">
                  <p class="text-xs font-semibold uppercase tracking-wide text-purple-600">
                    {{ $t('applications.selectedEdge') }}
                  </p>
                  <p class="mt-1 text-sm font-medium text-purple-900 truncate">
                    {{ getHostLabel(Number(selectedCanvasEdge.source)) }} → {{ getHostLabel(Number(selectedCanvasEdge.target)) }}
                  </p>
                </div>
                <div>
                  <label class="block text-xs font-medium text-gray-600">{{ $t('applications.relationshipType') }}</label>
                  <select
                    v-model="edgeForm.relationship_type"
                    class="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-purple-500 focus:outline-none focus:ring-1 focus:ring-purple-500"
                  >
                    <option
                      v-for="option in relationshipTypeOptions"
                      :key="option.value"
                      :value="option.value"
                    >
                      {{ option.label }}
                    </option>
                  </select>
                </div>
                <div>
                  <label class="block text-xs font-medium text-gray-600">{{ $t('applications.description') }}</label>
                  <textarea
                    v-model="edgeForm.description"
                    rows="3"
                    class="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-purple-500 focus:outline-none focus:ring-1 focus:ring-purple-500"
                  />
                </div>
                <div class="flex flex-col gap-2">
                  <button
                    @click="updateEdgeProperties"
                    :disabled="updatingEdge"
                    class="inline-flex items-center justify-center rounded-md bg-purple-600 px-3 py-2 text-sm font-semibold text-white shadow-sm transition-colors hover:bg-purple-500 disabled:cursor-not-allowed disabled:opacity-60"
                  >
                    {{ updatingEdge ? $t('common.saving') : $t('applications.updateRelationship') }}
                  </button>
                  <button
                    @click="deleteSelectedEdge"
                    class="inline-flex items-center justify-center rounded-md border border-red-200 px-3 py-2 text-sm font-semibold text-red-600 transition-colors hover:bg-red-50"
                  >
                    {{ $t('applications.deleteRelationship') }}
                  </button>
                </div>
              </div>
              <div v-else class="rounded-md border border-dashed border-gray-200 bg-gray-50 p-4 text-xs text-gray-500">
                <p>{{ $t('applications.canvasInspectorEmpty') }}</p>
                <p class="mt-2">
                  {{ $t('applications.canvasInspectorTip') }}
                </p>
              </div>
            </div>
          </aside>
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

    <!-- Resource Binding Modal -->
    <Modal
      :open="showResourceBindingModal"
      @close="handleResourceBindingCancel"
      :title="$t('applications.resourceBindingTitle')"
      max-width="lg"
    >
      <div class="space-y-5">
        <div
          v-if="pendingResourceDefinition"
          class="rounded-md border border-blue-100 bg-blue-50 px-4 py-3 text-sm text-blue-700"
        >
          <strong class="font-semibold">{{ pendingResourceDefinition.label }}</strong>
          <span class="ml-1 text-blue-600">
            {{ pendingResourceDefinition.description }}
          </span>
          <p class="mt-2 text-xs text-blue-600">
            {{ $t('applications.resourceBindingDescription') }}
          </p>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700">
            {{ $t('applications.resourceBindingSelectHost') }}
          </label>
          <div class="mt-2 flex flex-col gap-3 sm:flex-row sm:items-center">
            <div class="relative flex-1">
              <MagnifyingGlassIcon class="pointer-events-none absolute left-3 top-2.5 h-4 w-4 text-gray-400" />
              <input
                v-model="resourceBindingSearch"
                type="text"
                :placeholder="$t('applications.resourceBindingSearchPlaceholder')"
                class="w-full rounded-md border border-gray-300 py-2 pl-9 pr-3 text-sm shadow-sm focus:border-purple-500 focus:outline-none focus:ring-1 focus:ring-purple-500"
              />
            </div>
          </div>
          <div class="mt-3 max-h-72 overflow-y-auto rounded-md border border-gray-200">
            <div
              v-if="filteredBindableHosts.length === 0"
              class="px-6 py-10 text-center text-sm text-gray-500"
            >
              {{ $t('applications.resourceBindingNoHosts') }}
            </div>
            <div
              v-else
              v-for="item in filteredBindableHosts"
              :key="item.host.id"
              class="border-b border-gray-100 last:border-b-0"
            >
              <label class="flex cursor-pointer items-center justify-between gap-4 px-4 py-3 transition hover:bg-gray-50">
                <div class="flex items-center gap-3">
                  <input
                    type="radio"
                    name="resource-binding-host"
                    :value="item.host.id"
                    v-model="selectedResourceHostId"
                    class="h-4 w-4 border-gray-300 text-purple-600 focus:ring-purple-500"
                  />
                  <div>
                    <p class="text-sm font-medium text-gray-900">
                      {{ item.host.ip }}
                      <span v-if="item.host.hostname" class="ml-1 text-gray-500">• {{ item.host.hostname }}</span>
                    </p>
                    <p class="text-xs text-gray-500">
                      {{ item.host.device_type || '-' }} • {{ item.host.vendor || '-' }}
                    </p>
                  </div>
                </div>
                <span
                  class="rounded-full px-2.5 py-1 text-xs font-semibold"
                  :class="item.inApplication ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'"
                >
                  {{ item.inApplication ? $t('applications.resourceBindingAlreadyInApp') : $t('applications.resourceBindingNotInApp') }}
                </span>
              </label>
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <button
          type="button"
          @click="handleResourceBindingCancel"
          class="mt-3 inline-flex w-full justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 sm:mt-0 sm:w-auto transition-colors"
        >
          {{ $t('common.cancel') }}
        </button>
        <button
          type="button"
          @click="confirmResourceBinding"
          :disabled="!selectedResourceHostId || bindingResource"
          class="inline-flex w-full justify-center rounded-md bg-purple-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-purple-500 sm:ml-3 sm:w-auto disabled:cursor-not-allowed disabled:opacity-60 transition-colors"
        >
          {{ bindingResource ? $t('common.saving') : $t('applications.resourceBindingConfirm') }}
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
import { ref, onMounted, computed, watch, reactive, nextTick, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { applicationsApi, type HostRelationship } from '@/api/applications'
import { hostsApi } from '@/api/hosts'
import Modal from '@/components/Modal.vue'
import ConfirmModal from '@/components/ConfirmModal.vue'
import { useToastStore } from '@/stores/toast'
import {
  ServerIcon,
  ShareIcon,
  MagnifyingGlassIcon,
  ComputerDesktopIcon,
  GlobeAltIcon,
  ServerStackIcon,
  CloudIcon,
  Cog6ToothIcon,
  CircleStackIcon,
  ArrowDownOnSquareIcon,
  ArrowDownTrayIcon,
  PhotoIcon
} from '@heroicons/vue/24/outline'
import ApplicationCanvas from '@/components/ApplicationCanvas.vue'
import { CanvasNodeType } from '@/components/ApplicationCanvas/types'
import type { CanvasEdgeData, CanvasNodeData } from '@/components/ApplicationCanvas/types'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const toastStore = useToastStore()

const application = ref<any>(null)
const hosts = ref<any[]>([])
const availableHosts = ref<any[]>([])
const canvasNodes = ref<CanvasNodeData[]>([])
const canvasEdges = ref<CanvasEdgeData[]>([])
const resourceNodes = ref<CanvasNodeData[]>([])
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
const canvasRef = ref<InstanceType<typeof ApplicationCanvas> | null>(null)
const canvasContainerRef = ref<HTMLElement | null>(null)
const logicFlowInstance = ref<any>(null)
const selectedCanvasNode = ref<CanvasNodeData | null>(null)
const selectedCanvasEdge = ref<CanvasEdgeData | null>(null)
const nodeBindingHostId = ref<string>('')
const updatingNodeBinding = ref(false)
const edgeForm = reactive({
  relationship_type: 'member',
  description: ''
})
const updatingEdge = ref(false)
const suppressedEdgeRemovals = new Set<string>()
const hostLibraryKeyword = ref('')
const hostLibraryAddingId = ref<number | null>(null)
const selectedLayout = ref<'grid' | 'horizontal' | 'vertical'>('grid')
const resourceLabel = ref('')
const isCanvasFullscreen = ref(false)
const draggingResourceKey = ref<string | null>(null)
const isSavingGraph = ref(false)
const isExportingGraph = ref(false)

type HostTag = {
  id?: number
  name?: string
  color?: string
}

const idsEqual = (a: string | number | undefined, b: string | number | undefined) =>
  a !== undefined && b !== undefined && String(a) === String(b)

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

const selectableHosts = computed(() => {
  const hostMap = new Map<number, any>()
  hosts.value.forEach((host) => {
    if (host?.id) {
      hostMap.set(host.id, host)
    }
  })
  availableHosts.value.forEach((host) => {
    if (host?.id && !hostMap.has(host.id)) {
      hostMap.set(host.id, host)
    }
  })
  return Array.from(hostMap.values())
})

const canUpdateBinding = computed(() => {
  if (!selectedCanvasNode.value) return false
  const target =
    nodeBindingHostId.value === '' || nodeBindingHostId.value === null
      ? null
      : Number(nodeBindingHostId.value)
  if (!target) return false
  return target !== selectedCanvasNode.value.bindingHostId
})

const relationshipTypeOptions = computed(() => [
  { value: 'member', label: t('applications.member') },
  { value: 'depends_on', label: t('applications.dependsOn') },
  { value: 'connects_to', label: t('applications.connectsTo') },
  { value: 'runs_on', label: t('applications.runsOn') }
])

const filteredAvailableHostsForCanvas = computed(() => {
  const keyword = hostLibraryKeyword.value.trim().toLowerCase()
  if (!keyword) return availableHosts.value
  return availableHosts.value.filter((host) => {
    const ip = host.ip?.toLowerCase() || ''
    const hostname = host.hostname?.toLowerCase() || ''
    const vendor = host.vendor?.toLowerCase() || ''
    return ip.includes(keyword) || hostname.includes(keyword) || vendor.includes(keyword)
  })
})

const DEFAULT_TYPE_COLORS: Record<CanvasNodeType, string> = {
  [CanvasNodeType.HOST]: '#2563eb',
  [CanvasNodeType.NETWORK]: '#0ea5e9',
  [CanvasNodeType.STORAGE]: '#a855f7',
  [CanvasNodeType.OBJECT_STORAGE]: '#f97316',
  [CanvasNodeType.DATABASE]: '#ef4444',
  [CanvasNodeType.SERVICE]: '#6366f1',
  [CanvasNodeType.CUSTOM]: '#0f172a',
}

const COLOR_PRESETS = [
  '#2563eb',
  '#0ea5e9',
  '#22c55e',
  '#a855f7',
  '#f97316',
  '#ef4444',
  '#6366f1',
  '#14b8a6',
  '#0f172a'
]

const generateNodeId = (prefix = 'resource') =>
  `${prefix}-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 6)}`

interface ResourceDefinition {
  key: 'host' | 'network' | 'storage' | 'objectStorage' | 'service' | 'database'
  type: CanvasNodeType
  icon: CanvasNodeType
  color: string
  label: string
  description: string
}

const RESOURCE_ICON_COMPONENTS = {
  host: ComputerDesktopIcon,
  network: GlobeAltIcon,
  storage: ServerStackIcon,
  objectStorage: CloudIcon,
  service: Cog6ToothIcon,
  database: CircleStackIcon,
}

const resourceLibrary = computed<ResourceDefinition[]>(() => [
  {
    key: 'host',
    type: CanvasNodeType.HOST,
    icon: CanvasNodeType.HOST,
    color: DEFAULT_TYPE_COLORS[CanvasNodeType.HOST],
    label: t('applications.resourcePalette.host'),
    description: t('applications.resourcePalette.hostDesc'),
  },
  {
    key: 'network',
    type: CanvasNodeType.NETWORK,
    icon: CanvasNodeType.NETWORK,
    color: DEFAULT_TYPE_COLORS[CanvasNodeType.NETWORK],
    label: t('applications.resourcePalette.network'),
    description: t('applications.resourcePalette.networkDesc'),
  },
  {
    key: 'storage',
    type: CanvasNodeType.STORAGE,
    icon: CanvasNodeType.STORAGE,
    color: DEFAULT_TYPE_COLORS[CanvasNodeType.STORAGE],
    label: t('applications.resourcePalette.storage'),
    description: t('applications.resourcePalette.storageDesc'),
  },
  {
    key: 'objectStorage',
    type: CanvasNodeType.OBJECT_STORAGE,
    icon: CanvasNodeType.OBJECT_STORAGE,
    color: DEFAULT_TYPE_COLORS[CanvasNodeType.OBJECT_STORAGE],
    label: t('applications.resourcePalette.objectStorage'),
    description: t('applications.resourcePalette.objectStorageDesc'),
  },
  {
    key: 'service',
    type: CanvasNodeType.SERVICE,
    icon: CanvasNodeType.SERVICE,
    color: DEFAULT_TYPE_COLORS[CanvasNodeType.SERVICE],
    label: t('applications.resourcePalette.service'),
    description: t('applications.resourcePalette.serviceDesc'),
  },
  {
    key: 'database',
    type: CanvasNodeType.DATABASE,
    icon: CanvasNodeType.DATABASE,
    color: DEFAULT_TYPE_COLORS[CanvasNodeType.DATABASE],
    label: t('applications.resourcePalette.database'),
    description: t('applications.resourcePalette.databaseDesc'),
  },
])

const resourceLibraryMap = computed<Map<string, ResourceDefinition>>(() => {
  const map = new Map<string, ResourceDefinition>()
  resourceLibrary.value.forEach((item) => {
    map.set(item.key, item)
  })
  return map
})

const getTypeColor = (type: CanvasNodeType): string => {
  return DEFAULT_TYPE_COLORS[type] || DEFAULT_TYPE_COLORS[CanvasNodeType.HOST]
}

const showResourceBindingModal = ref(false)
const pendingResourceDefinition = ref<ResourceDefinition | null>(null)
const pendingResourcePosition = ref<{ x: number; y: number } | null>(null)
const selectedResourceHostId = ref<number | null>(null)
const resourceBindingSearch = ref('')
const bindingResource = ref(false)

const filteredBindableHosts = computed(() => {
  const map = new Map<number, { host: any; inApplication: boolean }>()

  hosts.value.forEach((host) => {
    if (host?.id) {
      map.set(host.id, { host, inApplication: true })
    }
  })

  availableHosts.value.forEach((host) => {
    if (host?.id && !map.has(host.id)) {
      map.set(host.id, { host, inApplication: false })
    }
  })

  let list = Array.from(map.values())
  const keyword = resourceBindingSearch.value.trim().toLowerCase()
  if (keyword) {
    list = list.filter(({ host }) => {
      const ip = host.ip?.toLowerCase() || ''
      const hostname = host.hostname?.toLowerCase() || ''
      const vendor = host.vendor?.toLowerCase() || ''
      const tags = Array.isArray(host.tags) ? host.tags.map((tag: any) => tag.name?.toLowerCase?.()).join(' ') : ''
      return ip.includes(keyword) || hostname.includes(keyword) || vendor.includes(keyword) || tags.includes(keyword)
    })
  }

  return list.sort((a, b) => {
    if (a.inApplication === b.inApplication) {
      return (a.host.ip || '').localeCompare(b.host.ip || '')
    }
    return a.inApplication ? -1 : 1
  })
})

const selectedHostDetails = computed(() => {
  const data: any = selectedCanvasNode.value?.data || {}
  const details: Array<{ label: string; value: string }> = []

  if (data.hostname || data.ip) {
    details.push({
      label: t('hosts.hostname'),
      value: data.hostname || data.ip || '-'
    })
  }

  if (data.ip) {
    details.push({
      label: t('hosts.ip'),
      value: data.ip
    })
  }

  if (data.os_type || data.os_version) {
    details.push({
      label: t('hosts.osType'),
      value: [data.os_type, data.os_version].filter(Boolean).join(' ') || '-'
    })
  }

  if (data.device_type) {
    details.push({
      label: t('hosts.deviceType'),
      value: data.device_type
    })
  }

  if (data.platform_name) {
    details.push({
      label: t('hosts.platform'),
      value: data.platform_name
    })
  }

  if (data.cpu_info || data.cpu_cores) {
    details.push({
      label: t('hosts.cpuInfo'),
      value: [data.cpu_info, data.cpu_cores ? `${t('hosts.cpuCores')}: ${data.cpu_cores}` : ''].filter(Boolean).join(' · ') || '-'
    })
  }

  if (data.memory_total) {
    details.push({
      label: t('hosts.memory'),
      value: formatMetric(data.memory_total)
    })
  }

  if (data.disk_total_size) {
    details.push({
      label: t('hosts.disk'),
      value: formatMetric(data.disk_total_size)
    })
  }

  if (Array.isArray(data.tags) && data.tags.length > 0) {
    details.push({
      label: t('hosts.tags'),
      value: data.tags.map((tag: any) => tag.name).join(', ')
    })
  }

  return details
})

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
  const numericValue = Number(value)
  if (Number.isNaN(numericValue)) return '-'
  const rounded = Math.round((numericValue + Number.EPSILON) * 100) / 100
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

const mapGroupToNodeType = (group?: string): CanvasNodeType => {
  const normalized = (group || '').toLowerCase()
  if (['network', 'switch', 'router', 'firewall', 'load_balancer'].includes(normalized)) {
    return CanvasNodeType.NETWORK
  }
  if (['storage', 'disk', 'san', 'nas'].includes(normalized)) {
    return CanvasNodeType.STORAGE
  }
  if (['object_storage', 'oss', 'bucket', 'cos', 's3'].includes(normalized)) {
    return CanvasNodeType.OBJECT_STORAGE
  }
  if (['database', 'db', 'mysql', 'postgres', 'sql', 'mongodb'].includes(normalized)) {
    return CanvasNodeType.DATABASE
  }
  if (['service', 'application', 'middleware', 'app', 'api'].includes(normalized)) {
    return CanvasNodeType.SERVICE
  }
  return CanvasNodeType.HOST
}

const getStatusLabel = (node: any) => {
  if (typeof node?.is_physical === 'boolean') {
    return node.is_physical ? t('applications.physicalHost') : t('applications.virtualHost')
  }
  if (node?.group) {
    const key = `applications.nodeGroup.${node.group}`
    const translated = t(key)
    return translated === key ? node.group : translated
  }
  return ''
}

const getRelationshipLabel = (type?: string) => {
  switch (type) {
    case 'depends_on':
      return t('applications.dependsOn')
    case 'connects_to':
      return t('applications.connectsTo')
    case 'runs_on':
      return t('applications.runsOn')
    case 'member':
      return t('applications.member')
    default:
      return type || ''
  }
}

const computeInitialPosition = (index: number) => {
  const column = index % 4
  const row = Math.floor(index / 4)
  const paddingX = 180
  const paddingY = 150
  const gapX = 220
  const gapY = 160
  return {
    x: paddingX + column * gapX,
    y: paddingY + row * gapY
  }
}

const refreshSelections = () => {
  if (selectedCanvasNode.value) {
    const updatedNode = canvasNodes.value.find((node) => node.id === selectedCanvasNode.value?.id)
    selectedCanvasNode.value = updatedNode || null
    nodeBindingHostId.value = updatedNode?.bindingHostId ? String(updatedNode.bindingHostId) : ''
    resourceLabel.value =
      updatedNode && !updatedNode.bindingHostId ? updatedNode.label : ''
  }
  if (selectedCanvasEdge.value) {
    const updatedEdge = canvasEdges.value.find((edge) => edge.id === selectedCanvasEdge.value?.id)
    selectedCanvasEdge.value = updatedEdge || null
    edgeForm.relationship_type = updatedEdge?.relationshipType || 'member'
    edgeForm.description = updatedEdge?.description || ''
  }
}

const syncCanvasEdgesFromRelationships = () => {
  if (!relationships.value.length) return
  const relationMap = new Map<number, any>()
  relationships.value.forEach((relation) => {
    if (relation?.id) {
      relationMap.set(relation.id, relation)
    }
  })
  canvasEdges.value = canvasEdges.value.map((edge) => {
    const relation = relationMap.get(Number(edge.id))
    if (!relation) return edge
    return {
      ...edge,
      relationshipType: relation.relationship_type || edge.relationshipType,
      label: getRelationshipLabel(relation.relationship_type || edge.relationshipType),
      description: relation.description || '',
      data: {
        ...(edge.data || {}),
        relationship: relation
      }
    }
  })
  refreshSelections()
}

const normalizeResourceNode = (raw: any, index = 0): CanvasNodeData => {
  const position = computeInitialPosition(index)
  const bindingHostId =
    raw?.bindingHostId !== undefined && raw?.bindingHostId !== null
      ? Number(raw.bindingHostId)
      : undefined
  const resourceKey = raw?.data?.resourceKey || raw?.resourceKey || raw?.key
  const libraryInfo = resourceKey ? resourceLibraryMap.value.get(resourceKey) : undefined
  const nodeType = (raw?.type || libraryInfo?.type || CanvasNodeType.CUSTOM) as CanvasNodeType
  const color = raw?.color || getTypeColor(nodeType)
  const label =
    raw?.label ||
    libraryInfo?.label ||
    raw?.data?.label ||
    (bindingHostId ? `#${bindingHostId}` : t('applications.genericResource'))
  const status =
    raw?.status || raw?.data?.displayStatus || libraryInfo?.description || ''

  return {
    id: raw?.id ?? generateNodeId('resource'),
    type: nodeType,
    x: typeof raw?.x === 'number' ? raw.x : position.x,
    y: typeof raw?.y === 'number' ? raw.y : position.y,
    label,
    color,
    icon: raw?.icon || libraryInfo?.type || nodeType,
    bindingHostId,
    status,
    data: {
      ...(raw?.data || {}),
      resource: true,
      resourceKey: resourceKey || libraryInfo?.key || nodeType,
      displayStatus: status,
      color,
      label
    }
  }
}

const syncCanvasData = (graph: { nodes?: any[]; edges?: any[]; resourceNodes?: any[]; metadata?: Record<string, any> }) => {
  const nodes = Array.isArray(graph?.nodes) ? graph.nodes ?? [] : []
  const edges = Array.isArray(graph?.edges) ? graph.edges ?? [] : []
  const resourcePayload = Array.isArray(graph?.resourceNodes) ? graph.resourceNodes ?? [] : []

  if (graph?.metadata?.layout && ['grid', 'horizontal', 'vertical'].includes(graph.metadata.layout)) {
    selectedLayout.value = graph.metadata.layout
  }

  const hostIndex = new Map<number, any>()
  hosts.value.forEach((host) => {
    if (host?.id) {
      hostIndex.set(host.id, host)
    }
  })

  const normalizedResourceNodes: CanvasNodeData[] = resourcePayload.map((raw, idx) =>
    normalizeResourceNode(raw, idx)
  )
  const overlayByHostId = new Map<number, CanvasNodeData>()
  const resourceIdSet = new Set<string | number>()
  normalizedResourceNodes.forEach((node) => {
    resourceIdSet.add(node.id)
    if (node.bindingHostId) {
      overlayByHostId.set(node.bindingHostId, node)
    }
  })

  const hostNodes: CanvasNodeData[] = []
  const seenHostIds = new Set<number>()

  nodes.forEach((rawNode: any, index: number) => {
    const hostId =
      rawNode?.bindingHostId !== undefined && rawNode?.bindingHostId !== null
        ? Number(rawNode.bindingHostId)
        : typeof rawNode?.id === 'number'
          ? rawNode.id
          : undefined

    if (hostId && hostIndex.has(hostId)) {
      const hostRecord = hostIndex.get(hostId)
      const overlay = overlayByHostId.get(hostId)
      const basePosition = computeInitialPosition(index)
      const x = typeof rawNode?.x === 'number' ? rawNode.x : overlay?.x ?? basePosition.x
      const y = typeof rawNode?.y === 'number' ? rawNode.y : overlay?.y ?? basePosition.y
      const nodeType = (overlay?.type || rawNode?.type || mapGroupToNodeType(hostRecord.device_type)) as CanvasNodeType
      const color = overlay?.color || rawNode?.color || getTypeColor(nodeType)
      const label =
        overlay?.label ||
        rawNode?.label ||
        hostRecord.hostname ||
        hostRecord.ip ||
        `#${hostId}`
      const status = overlay?.status || getStatusLabel(hostRecord)
      const icon = overlay?.icon || rawNode?.icon || nodeType

      hostNodes.push({
        id: hostId,
        type: nodeType,
        x,
        y,
        label,
        bindingHostId: hostId,
        status,
        icon,
        color,
        data: {
          ...hostRecord,
          ...(rawNode?.data || {}),
          ...(overlay?.data || {}),
          resource: !!overlay,
          color
        }
      })
      seenHostIds.add(hostId)
    } else if (!resourceIdSet.has(rawNode?.id)) {
      const normalized = normalizeResourceNode(rawNode, normalizedResourceNodes.length + index)
      resourceIdSet.add(normalized.id)
      if (normalized.bindingHostId) {
        overlayByHostId.set(normalized.bindingHostId, normalized)
        seenHostIds.add(normalized.bindingHostId)
      }
      normalizedResourceNodes.push(normalized)
    }
  })

  hosts.value.forEach((host, hostIndexPosition) => {
    if (!seenHostIds.has(host.id)) {
      const position = computeInitialPosition(hostNodes.length + hostIndexPosition)
      const nodeType = mapGroupToNodeType(host.device_type)
      const color = getTypeColor(nodeType)
      hostNodes.push({
        id: host.id,
        type: nodeType,
        x: position.x,
        y: position.y,
        label: host.hostname || host.ip || `#${host.id}`,
        bindingHostId: host.id,
        status: getStatusLabel(host),
        icon: nodeType,
        color,
        data: {
          ...host,
          resource: false,
          color
        }
      })
    }
  })

  resourceNodes.value = normalizedResourceNodes.map((node) => {
    if (!node.bindingHostId) {
      return node
    }
    const hostRecord = hostIndex.get(node.bindingHostId)
    if (!hostRecord) {
      return {
        ...node,
        bindingHostId: undefined,
        data: { resource: true, label: node.label },
        status: ''
      }
    }
    const nodeType = node.type || mapGroupToNodeType(hostRecord.device_type)
    const color = node.color || getTypeColor(nodeType)
    return {
      ...node,
      type: nodeType,
      color,
      status: getStatusLabel(hostRecord),
      data: { ...hostRecord, resource: true, color }
    }
  })

  const unboundResources = resourceNodes.value.filter((node) => !node.bindingHostId)
  canvasNodes.value = [...hostNodes, ...unboundResources]

  const relationMap = new Map<number, any>()
  relationships.value.forEach((relation) => {
    if (relation?.id) {
      relationMap.set(relation.id, relation)
    }
  })

  canvasEdges.value = edges.map((edge: any) => {
    const relation = edge?.id ? relationMap.get(Number(edge.id)) : null
    const relationshipType = edge?.relationshipType || relation?.relationship_type || edge?.label
    return {
      id: edge?.id,
      source: edge?.source ?? edge?.from,
      target: edge?.target ?? edge?.to,
      relationshipType,
      label: relationshipType ? getRelationshipLabel(relationshipType) : edge?.label,
      description: edge?.description || relation?.description || '',
      data: {
        ...(edge?.data || {}),
        relationship: relation
      }
    }
  })

  refreshSelections()
}

const clearCanvasSelection = () => {
  selectedCanvasNode.value = null
  selectedCanvasEdge.value = null
  nodeBindingHostId.value = ''
  edgeForm.relationship_type = 'member'
  edgeForm.description = ''
  resourceLabel.value = ''
}

const handleCanvasReady = (lf: any) => {
  logicFlowInstance.value = lf
}

const handleCanvasNodeClick = (node: CanvasNodeData) => {
  selectedCanvasNode.value = node
  selectedCanvasEdge.value = null
  nodeBindingHostId.value = node.bindingHostId ? String(node.bindingHostId) : ''
  if (node.bindingHostId) {
    const overlay = resourceNodes.value.find((overlayNode) => overlayNode.bindingHostId === node.bindingHostId)
    resourceLabel.value = overlay?.label || node.label
  } else {
    resourceLabel.value = node.label
  }
}

const handleCanvasEdgeClick = (edge: CanvasEdgeData) => {
  selectedCanvasEdge.value = edge
  selectedCanvasNode.value = null
  edgeForm.relationship_type = edge.relationshipType || 'member'
  edgeForm.description = edge.description || ''
}

const handleCanvasBlankClick = () => {
  clearCanvasSelection()
}

const handleCanvasNodeMoved = (node: CanvasNodeData) => {
  const index = canvasNodes.value.findIndex((item) => idsEqual(item.id, node.id))
  if (index >= 0) {
    canvasNodes.value[index] = {
      ...canvasNodes.value[index],
      x: node.x,
      y: node.y
    }
  }
  canvasNodes.value = [...canvasNodes.value]
  if (node.bindingHostId) {
    const overlayIndex = resourceNodes.value.findIndex((item) => idsEqual(item.bindingHostId, node.bindingHostId))
    if (overlayIndex >= 0) {
      resourceNodes.value[overlayIndex] = {
        ...resourceNodes.value[overlayIndex],
        x: node.x,
        y: node.y
      }
      resourceNodes.value = [...resourceNodes.value]
    }
  } else {
    const resourceIndex = resourceNodes.value.findIndex((item) => idsEqual(item.id, node.id))
    if (resourceIndex >= 0) {
      resourceNodes.value[resourceIndex] = {
        ...resourceNodes.value[resourceIndex],
        x: node.x,
        y: node.y
      }
      resourceNodes.value = [...resourceNodes.value]
    }
  }
}

const updateNodeBinding = async () => {
  if (!selectedCanvasNode.value) return
  const currentBinding = selectedCanvasNode.value.bindingHostId
  const targetHostId =
    nodeBindingHostId.value === '' || nodeBindingHostId.value === null
      ? null
      : Number(nodeBindingHostId.value)

  if (!targetHostId || targetHostId === currentBinding) {
    return
  }

  updatingNodeBinding.value = true
  const selectedId = selectedCanvasNode.value.id
  try {
    const appId = parseInt(route.params.id as string)
    if (currentBinding) {
      await applicationsApi.removeHost(appId, currentBinding)
    }
    await applicationsApi.addHosts(appId, [targetHostId])
    if (!selectedCanvasNode.value.bindingHostId) {
      const overlayIndex = resourceNodes.value.findIndex((node) => node.id === selectedId)
      if (overlayIndex >= 0) {
        resourceNodes.value[overlayIndex] = {
          ...resourceNodes.value[overlayIndex],
          bindingHostId: targetHostId
        }
        resourceNodes.value = [...resourceNodes.value]
      } else {
        resourceNodes.value = [
          ...resourceNodes.value,
          {
            ...selectedCanvasNode.value,
            id: selectedId,
            bindingHostId: targetHostId,
            data: { resource: true, label: selectedCanvasNode.value.label }
          }
        ]
        resourceNodes.value = [...resourceNodes.value]
      }
    }
    toastStore.success(t('applications.updateBindingSuccess'))
    await loadApplication()
    clearCanvasSelection()
  } catch (error: any) {
    toastStore.error(error.response?.data?.message || t('applications.updateBindingFailed'))
  } finally {
    updatingNodeBinding.value = false
  }
}

const deleteSelectedNode = () => {
  if (!selectedCanvasNode.value?.bindingHostId) return
  removeHost(selectedCanvasNode.value.bindingHostId)
}

const updateEdgeProperties = async () => {
  if (!selectedCanvasEdge.value?.id) return
  const relationshipId = Number(selectedCanvasEdge.value.id)
  if (!relationshipId) return
  updatingEdge.value = true
  try {
    const appId = parseInt(route.params.id as string)
    await applicationsApi.updateRelationship(appId, relationshipId, {
      relationship_type: edgeForm.relationship_type,
      description: edgeForm.description
    })
    toastStore.success(t('applications.updateRelationshipSuccess'))
    await loadRelationships()
  } catch (error: any) {
    toastStore.error(error.response?.data?.message || t('applications.updateRelationshipFailed'))
  } finally {
    updatingEdge.value = false
  }
}

const deleteSelectedEdge = () => {
  if (!selectedCanvasEdge.value?.id) return
  const relationshipId = Number(selectedCanvasEdge.value.id)
  if (!relationshipId) return

  confirmMessage.value = t('applications.confirmRelationshipDelete')
  confirmAction.value = async () => {
    try {
      const appId = parseInt(route.params.id as string)
      await applicationsApi.deleteRelationship(appId, relationshipId)
      toastStore.success(t('applications.deleteRelationshipSuccess'))
      await loadRelationships()
      suppressedEdgeRemovals.add(String(relationshipId))
      canvasEdges.value = canvasEdges.value.filter((edge) => Number(edge.id) !== relationshipId)
      clearCanvasSelection()
    } catch (error: any) {
      toastStore.error(error.response?.data?.message || t('applications.deleteRelationshipFailed'))
    }
  }
  showConfirmModal.value = true
}

const handleCanvasEdgeAdded = async (edge: CanvasEdgeData) => {
  const appId = parseInt(route.params.id as string)
  const sourceId = Number(edge.source)
  const targetId = Number(edge.target)

  if (!sourceId || !targetId) {
    toastStore.error(t('applications.canvasEdgeMissingHost'))
    if (edge.id && canvasRef.value) {
      suppressedEdgeRemovals.add(String(edge.id))
      canvasRef.value.removeEdge(edge.id)
    }
    return
  }

  if (sourceId === targetId) {
    toastStore.error(t('applications.canvasSelfLoopNotAllowed'))
    if (edge.id && canvasRef.value) {
      suppressedEdgeRemovals.add(String(edge.id))
      canvasRef.value.removeEdge(edge.id)
    }
    return
  }

  const exists = relationships.value.some(
    (relation) => relation.from_host_id === sourceId && relation.to_host_id === targetId
  )
  if (exists) {
    toastStore.error(t('applications.addRelationshipFailed'))
    if (edge.id && canvasRef.value) {
      suppressedEdgeRemovals.add(String(edge.id))
      canvasRef.value.removeEdge(edge.id)
    }
    return
  }

  try {
    await applicationsApi.createRelationship(appId, {
      from_host_id: sourceId,
      to_host_id: targetId,
      relationship_type: 'member'
    })
    toastStore.success(t('applications.addRelationshipSuccess'))
    await loadApplication()
  } catch (error: any) {
    toastStore.error(error.response?.data?.message || t('applications.addRelationshipFailed'))
    if (edge.id && canvasRef.value) {
      suppressedEdgeRemovals.add(String(edge.id))
      canvasRef.value.removeEdge(edge.id)
    } else {
      await loadApplication()
    }
  }
}

const handleCanvasEdgeRemoved = async (edge: CanvasEdgeData) => {
  const relationshipId = edge.id ? Number(edge.id) : NaN
  const idKey = edge.id ? String(edge.id) : ''
  if (idKey && suppressedEdgeRemovals.has(idKey)) {
    suppressedEdgeRemovals.delete(idKey)
    return
  }

  if (!relationshipId || Number.isNaN(relationshipId)) {
    return
  }

  const exists = relationships.value.some((relation) => relation.id === relationshipId)
  if (!exists) {
    return
  }

  try {
    const appId = parseInt(route.params.id as string)
    await applicationsApi.deleteRelationship(appId, relationshipId)
    toastStore.success(t('applications.deleteRelationshipSuccess'))
    await loadRelationships()
    canvasEdges.value = canvasEdges.value.filter((item) => Number(item.id) !== relationshipId)
    clearCanvasSelection()
  } catch (error: any) {
    toastStore.error(error.response?.data?.message || t('applications.deleteRelationshipFailed'))
    await loadApplication()
  }
}

const handleCanvasNodeRemoved = async (node: CanvasNodeData) => {
  if (!node.bindingHostId) {
    resourceNodes.value = resourceNodes.value.filter((item) => !idsEqual(item.id, node.id))
    canvasNodes.value = canvasNodes.value.filter((item) => !idsEqual(item.id, node.id))
    clearCanvasSelection()
    return
  }

  const hostId = Number(node.bindingHostId)
  if (!hostId) {
    return
  }

  const exists = hosts.value.some((host) => host.id === hostId)
  if (!exists) {
    return
  }

  try {
    const appId = parseInt(route.params.id as string)
    await applicationsApi.removeHost(appId, hostId)
    resourceNodes.value = resourceNodes.value.filter((item) => !idsEqual(item.bindingHostId, hostId))
    toastStore.success(t('applications.removeHostSuccess'))
    await loadApplication()
  } catch (error: any) {
    toastStore.error(error.response?.data?.message || t('applications.removeHostFailed'))
    await loadApplication()
  }
}

const addHostFromLibrary = async (hostId: number) => {
  if (!hostId) return
  hostLibraryAddingId.value = hostId
  try {
    const appId = parseInt(route.params.id as string)
    await applicationsApi.addHosts(appId, [hostId])
    toastStore.success(t('applications.addHostSuccess'))
    await loadApplication()
  } catch (error: any) {
    toastStore.error(error.response?.data?.message || t('applications.addHostFailed'))
  } finally {
    hostLibraryAddingId.value = null
  }
}

const startResourceBinding = (resource: ResourceDefinition, position: { x: number; y: number } | null = null) => {
  pendingResourceDefinition.value = resource
  pendingResourcePosition.value = position
  selectedResourceHostId.value = null
  resourceBindingSearch.value = ''
  showResourceBindingModal.value = true
}

const createResourceNode = (resource: ResourceDefinition) => {
  const position = computeInitialPosition(canvasNodes.value.length)
  startResourceBinding(resource, position)
}

const updateResourceNodeLabel = () => {
  if (!selectedCanvasNode.value) return
  const trimmed = resourceLabel.value.trim()
  if (!trimmed) return

  if (selectedCanvasNode.value.bindingHostId) {
    const hostId = selectedCanvasNode.value.bindingHostId
    const index = resourceNodes.value.findIndex((node) => idsEqual(node.bindingHostId, hostId))
    if (index >= 0) {
      resourceNodes.value[index] = {
        ...resourceNodes.value[index],
        label: trimmed,
        data: { ...(resourceNodes.value[index].data || {}), label: trimmed }
      }
      resourceNodes.value = [...resourceNodes.value]
    } else {
      const resourceKey = (selectedCanvasNode.value.data?.resourceKey as string) || selectedCanvasNode.value.type
      resourceNodes.value = [
        ...resourceNodes.value,
        {
          id: `overlay-${hostId}-${Date.now().toString(36)}`,
          type: selectedCanvasNode.value.type,
          x: selectedCanvasNode.value.x,
          y: selectedCanvasNode.value.y,
          label: trimmed,
          color: selectedCanvasNode.value.color || getTypeColor(selectedCanvasNode.value.type as CanvasNodeType),
          icon: selectedCanvasNode.value.type,
          bindingHostId: hostId,
          status: selectedCanvasNode.value.status,
          data: {
            ...(selectedCanvasNode.value.data || {}),
            label: trimmed,
            resource: true,
            resourceKey,
          }
        }
      ]
    }
    canvasNodes.value = canvasNodes.value.map((node) =>
      idsEqual(node.bindingHostId, hostId) ? { ...node, label: trimmed } : node
    )
  } else {
    resourceNodes.value = resourceNodes.value.map((node) =>
      idsEqual(node.id, selectedCanvasNode.value?.id)
        ? { ...node, label: trimmed, data: { ...(node.data || {}), label: trimmed } }
        : node
    )
    resourceNodes.value = [...resourceNodes.value]
    canvasNodes.value = canvasNodes.value.map((node) =>
      idsEqual(node.id, selectedCanvasNode.value?.id)
        ? { ...node, label: trimmed, data: { ...(node.data || {}), label: trimmed } }
        : node
    )
  }

  selectedCanvasNode.value = {
    ...selectedCanvasNode.value,
    label: trimmed
  }
  resourceLabel.value = trimmed
}

const updateSelectedNodeColor = (color: string) => {
  if (!selectedCanvasNode.value) return
  const node = selectedCanvasNode.value

  if (node.bindingHostId) {
    const hostId = node.bindingHostId
    const index = resourceNodes.value.findIndex((overlay) => overlay.bindingHostId === hostId)
    if (index >= 0) {
      resourceNodes.value[index] = {
        ...resourceNodes.value[index],
        color,
        data: { ...(resourceNodes.value[index].data || {}), color }
      }
      resourceNodes.value = [...resourceNodes.value]
    } else {
      const resourceKey = (node.data?.resourceKey as string) || node.type
      resourceNodes.value = [
        ...resourceNodes.value,
        {
          id: `overlay-${hostId}-${Date.now().toString(36)}`,
          type: node.type,
          x: node.x,
          y: node.y,
          label: node.label,
          color,
          icon: node.type,
          bindingHostId: hostId,
          status: node.status,
          data: { ...(node.data || {}), color, resource: true, resourceKey }
        }
      ]
      resourceNodes.value = [...resourceNodes.value]
    }
    canvasNodes.value = canvasNodes.value.map((existing) =>
      idsEqual(existing.bindingHostId, hostId) ? { ...existing, color } : existing
    )
  } else {
    const nodeId = node.id
    canvasNodes.value = canvasNodes.value.map((existing) =>
      idsEqual(existing.id, nodeId) ? { ...existing, color } : existing
    )
    resourceNodes.value = resourceNodes.value.map((existing) =>
      idsEqual(existing.id, nodeId) ? { ...existing, color, data: { ...(existing.data || {}), color } } : existing
    )
    resourceNodes.value = [...resourceNodes.value]
  }

  selectedCanvasNode.value = {
    ...selectedCanvasNode.value,
    color
  }
}

const duplicateSelectedResource = () => {
  if (!selectedCanvasNode.value) return
  const node = selectedCanvasNode.value
  const source =
    node.bindingHostId
      ? resourceNodes.value.find((overlay) => overlay.bindingHostId === node.bindingHostId) || node
      : node

  const id = generateNodeId()
  const clone: CanvasNodeData = {
    ...source,
    id,
    bindingHostId: undefined,
    x: (source.x ?? node.x) + 48,
    y: (source.y ?? node.y) + 48,
    data: { ...(source.data || {}), resource: true }
  }

  resourceNodes.value = [...resourceNodes.value, clone]
  canvasNodes.value = [...canvasNodes.value, clone]
  selectedCanvasNode.value = clone
  selectedCanvasEdge.value = null
  nodeBindingHostId.value = ''
  resourceLabel.value = clone.label
}

const exportCanvasAsImage = async () => {
  if (!logicFlowInstance.value) {
    toastStore.error(t('applications.canvasExportImageFailed'))
    return
  }

  const appId = parseInt(route.params.id as string)

  try {
    let snapshot: any
    if (typeof logicFlowInstance.value.getSnapshot === 'function') {
      snapshot = logicFlowInstance.value.getSnapshot()
      if (snapshot instanceof Promise) {
        snapshot = await snapshot
      }
    } else if (typeof logicFlowInstance.value.getGraphSnapshot === 'function') {
      snapshot = logicFlowInstance.value.getGraphSnapshot()
      if (snapshot instanceof Promise) {
        snapshot = await snapshot
      }
    }

    if (!snapshot) {
      throw new Error('snapshot unsupported')
    }

    let dataUrl: string
    if (snapshot instanceof Blob) {
      dataUrl = URL.createObjectURL(snapshot)
    } else if (typeof snapshot === 'string' && snapshot.startsWith('data:')) {
      dataUrl = snapshot
    } else if (typeof snapshot === 'string') {
      dataUrl = `data:image/png;base64,${snapshot}`
    } else {
      throw new Error('invalid snapshot response')
    }

    const link = document.createElement('a')
    link.href = dataUrl
    link.download = appId ? `application-${appId}-graph.png` : 'application-graph.png'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)

    if (snapshot instanceof Blob) {
      URL.revokeObjectURL(dataUrl)
    }
  } catch (error) {
    console.error('Failed to export PNG', error)
    toastStore.error(t('applications.canvasExportImageFailed'))
  }
}

const applyResourceOverlay = (
  hostId: number,
  resource: ResourceDefinition,
  position: { x: number; y: number } | null,
  overridePosition = false
) => {
  const defaultPosition = position || computeInitialPosition(canvasNodes.value.length)
  let overlayNode: CanvasNodeData = {
    id: generateNodeId(resource.key),
    type: resource.type,
    x: defaultPosition.x,
    y: defaultPosition.y,
    label: resource.label,
    color: resource.color,
    icon: resource.type,
    bindingHostId: hostId,
    status: resource.description,
    data: {
      resource: true,
      resourceKey: resource.key,
      displayStatus: resource.description,
      label: resource.label,
      color: resource.color
    }
  }

  let hostFound = false
  canvasNodes.value = canvasNodes.value.map((node) => {
    if (idsEqual(node.bindingHostId, hostId)) {
      hostFound = true
      const targetX = overridePosition ? defaultPosition.x : node.x ?? defaultPosition.x
      const targetY = overridePosition ? defaultPosition.y : node.y ?? defaultPosition.y
      overlayNode = {
        ...overlayNode,
        x: targetX,
        y: targetY,
        status: getStatusLabel(node.data || {})
      }
      return {
        ...node,
        type: resource.type,
        label: resource.label,
        icon: resource.type,
        color: resource.color,
        x: targetX,
        y: targetY,
        data: {
          ...(node.data || {}),
          resource: true,
          resourceKey: resource.key,
          displayStatus: resource.description,
          label: resource.label,
          color: resource.color
        }
      }
    }
    return node
  })

  if (!hostFound) {
    canvasNodes.value = [
      ...canvasNodes.value,
      overlayNode
    ]
  } else {
    canvasNodes.value = [...canvasNodes.value]
  }

  resourceNodes.value = [
    ...resourceNodes.value.filter((node) => !idsEqual(node.bindingHostId, hostId)),
    overlayNode
  ]
  resourceNodes.value = [...resourceNodes.value]

  const selected = canvasNodes.value.find((node) => idsEqual(node.bindingHostId, hostId)) || overlayNode
  selectedCanvasNode.value = selected
  selectedCanvasEdge.value = null
  nodeBindingHostId.value = String(hostId)
  resourceLabel.value = overlayNode.label
  refreshSelections()
}

const handleCanvasDragOver = (event: DragEvent) => {
  if (!draggingResourceKey.value) return
  event.preventDefault()
  if (event.dataTransfer) {
    event.dataTransfer.dropEffect = 'copy'
  }
}

const handleCanvasDrop = (event: DragEvent) => {
  event.preventDefault()
  const resourceKey =
    event.dataTransfer?.getData('application/resource') || draggingResourceKey.value
  draggingResourceKey.value = null
  if (!resourceKey) return

  const resource = resourceLibraryMap.value.get(resourceKey)
  if (!resource) return

  let dropPosition: { x: number; y: number } | null = null
  if (logicFlowInstance.value?.getPointByClient) {
    const point = logicFlowInstance.value.getPointByClient(event.clientX, event.clientY)
    if (point?.canvasOverlayPosition) {
      dropPosition = {
        x: point.canvasOverlayPosition.x,
        y: point.canvasOverlayPosition.y
      }
    }
  }

  startResourceBinding(resource, dropPosition)
}

const onResourceDragStart = (resource: ResourceDefinition, event: DragEvent) => {
  draggingResourceKey.value = resource.key
  if (event.dataTransfer) {
    event.dataTransfer.setData('application/resource', resource.key)
    event.dataTransfer.effectAllowed = 'copy'
  }
}

const onResourceDragEnd = () => {
  draggingResourceKey.value = null
}

const sanitizeNodeForPersist = (node: CanvasNodeData) => ({
  id: node.id,
  type: node.type,
  x: node.x,
  y: node.y,
  label: node.label,
  color: node.color,
  icon: node.icon,
  status: node.status,
  bindingHostId:
    node.bindingHostId !== undefined && node.bindingHostId !== null
      ? Number(node.bindingHostId)
      : undefined,
  data: node.data || {}
})

const sanitizeEdgeForPersist = (edge: CanvasEdgeData) => ({
  id: edge.id,
  source: edge.source,
  target: edge.target,
  relationshipType: edge.relationshipType,
  label: edge.label,
  description: edge.description,
  data: edge.data || {}
})

const serializeGraph = () => ({
  nodes: canvasNodes.value.map(sanitizeNodeForPersist),
  edges: canvasEdges.value.map(sanitizeEdgeForPersist),
  resourceNodes: resourceNodes.value.map(sanitizeNodeForPersist),
  metadata: {
    layout: selectedLayout.value
  }
})

const saveCanvasLayout = async () => {
  const appId = parseInt(route.params.id as string)
  if (!appId || isSavingGraph.value) return

  isSavingGraph.value = true
  try {
    await applicationsApi.saveGraph(appId, serializeGraph())
    toastStore.success(t('applications.canvasSaveSuccess'))
  } catch (error: any) {
    toastStore.error(error.response?.data?.message || t('applications.canvasSaveFailed'))
  } finally {
    isSavingGraph.value = false
  }
}

const exportCanvasLayout = async () => {
  const appId = parseInt(route.params.id as string)
  if (!appId || isExportingGraph.value) return

  isExportingGraph.value = true
  try {
    const blob = await applicationsApi.exportGraph(appId)
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `application-${appId}-graph.json`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
    toastStore.success(t('applications.canvasExportSuccess'))
  } catch (error: any) {
    toastStore.error(error.response?.data?.message || t('applications.canvasExportFailed'))
  } finally {
    isExportingGraph.value = false
  }
}

const resetPendingResource = () => {
  pendingResourceDefinition.value = null
  pendingResourcePosition.value = null
  selectedResourceHostId.value = null
  resourceBindingSearch.value = ''
}

const handleResourceBindingCancel = () => {
  showResourceBindingModal.value = false
  resetPendingResource()
}

const confirmResourceBinding = async () => {
  if (!pendingResourceDefinition.value || !selectedResourceHostId.value) {
    toastStore.error(t('applications.resourceBindingSelectNotice'))
    return
  }

  const resourceDef = pendingResourceDefinition.value
  const hostId = selectedResourceHostId.value
  const alreadyInApplication = hosts.value.some((host) => host.id === hostId)

  bindingResource.value = true
  try {
    const appId = parseInt(route.params.id as string)
    if (!alreadyInApplication) {
      await applicationsApi.addHosts(appId, [hostId])
      await loadApplication()
    }
    applyResourceOverlay(hostId, resourceDef, pendingResourcePosition.value, !alreadyInApplication)
    toastStore.success(t('applications.resourceBindingSuccess'))
    showResourceBindingModal.value = false
    resetPendingResource()
  } catch (error: any) {
    toastStore.error(error.response?.data?.message || t('applications.resourceBindingFailed'))
  } finally {
    bindingResource.value = false
  }
}

const applyLayout = (layout: 'grid' | 'horizontal' | 'vertical') => {
  selectedLayout.value = layout
  const updatedNodes = canvasNodes.value.map((node, index) => {
    let position
    if (layout === 'grid') {
      position = computeInitialPosition(index)
    } else if (layout === 'horizontal') {
      position = { x: 160 + index * 220, y: 200 }
    } else {
      position = { x: 220, y: 140 + index * 160 }
    }
    return {
      ...node,
      x: position.x,
      y: position.y
    }
  })
  canvasNodes.value = updatedNodes
  resourceNodes.value = resourceNodes.value.map((node) => {
    if (node.bindingHostId) {
      const match = updatedNodes.find((item) => item.bindingHostId === node.bindingHostId)
      return match ? { ...node, x: match.x, y: match.y } : node
    }
    const match = updatedNodes.find((item) => item.id === node.id)
    return match ? { ...node, x: match.x, y: match.y } : node
  })
}

const zoomIn = () => {
  if (logicFlowInstance.value?.zoom) {
    logicFlowInstance.value.zoom(true)
  }
}

const zoomOut = () => {
  if (logicFlowInstance.value?.zoom) {
    logicFlowInstance.value.zoom(false)
  }
}

const resetZoom = () => {
  if (logicFlowInstance.value?.resetZoom) {
    logicFlowInstance.value.resetZoom()
  } else if (logicFlowInstance.value?.setZoom) {
    logicFlowInstance.value.setZoom(1)
  }
}

const fitView = () => {
  if (logicFlowInstance.value?.fitView) {
    logicFlowInstance.value.fitView()
  }
}

const toggleCanvasFullscreen = () => {
  isCanvasFullscreen.value = !isCanvasFullscreen.value
  if (isCanvasFullscreen.value) {
    nextTick(() => {
      fitView()
    })
  }
}

const exitCanvasFullscreen = () => {
  if (isCanvasFullscreen.value) {
    isCanvasFullscreen.value = false
  }
}

const loadRelationships = async () => {
  try {
    const appId = parseInt(route.params.id as string)
    const response = await applicationsApi.getRelationships(appId)
    relationships.value = response.data || []
    syncCanvasEdgesFromRelationships()
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
    relationships.value = relationshipRes.data || []
    
    // Load hosts from application
    if (application.value.hosts) {
      hosts.value = application.value.hosts
    }
    await loadAvailableHosts()
    syncCanvasData(graphRes.data || { nodes: [], edges: [] })
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
      clearCanvasSelection()
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
    await loadApplication()
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
      await loadApplication()
    } catch (error: any) {
      toastStore.error(error.response?.data?.message || t('applications.deleteRelationshipFailed'))
    }
  }
  showConfirmModal.value = true
}

const onFullscreenKeydown = (event: KeyboardEvent) => {
  if (event.key === 'Escape') {
    exitCanvasFullscreen()
  }
}

watch(isCanvasFullscreen, (fullscreen) => {
  const className = 'overflow-hidden'
  if (fullscreen) {
    document.body.classList.add(className)
    window.addEventListener('keydown', onFullscreenKeydown)
  } else {
    document.body.classList.remove(className)
    window.removeEventListener('keydown', onFullscreenKeydown)
  }
})

onMounted(() => {
  loadApplication()
})

watch(showAddHostModal, (opened) => {
  if (opened) {
  loadAvailableHosts()
  }
})

watch(showResourceBindingModal, (opened) => {
  if (opened) {
    loadAvailableHosts()
  } else {
    resetPendingResource()
  }
})

onBeforeUnmount(() => {
  document.body.classList.remove('overflow-hidden')
  window.removeEventListener('keydown', onFullscreenKeydown)
})

</script>