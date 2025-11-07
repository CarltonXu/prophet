<template>
  <div class="px-4 py-6 sm:px-0">
    <div class="mb-4 flex justify-between items-center">
      <h1 class="text-2xl font-bold text-gray-900 flex items-center">
        <TagIcon class="h-7 w-7 mr-2 text-gray-700" />
        {{ $t('tags.title') }}
      </h1>
      <div class="flex items-center space-x-2">
        <button
          @click="loadTags"
          :disabled="loading"
          class="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
        >
          <ArrowPathIcon :class="{ 'animate-spin': loading }" class="h-4 w-4 mr-2" />
          {{ $t('common.refresh') }}
        </button>
        <button
          @click="openCreateModal"
          class="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md text-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
        >
          <PlusIcon class="h-4 w-4 mr-2" />
          {{ $t('tags.createTag') }}
        </button>
      </div>
    </div>
    
    <div class="bg-white shadow overflow-hidden sm:rounded-md relative">
      <LoadingOverlay :loading="loading" :text="$t('common.loading')" />
      <div class="grid grid-cols-1 gap-4 p-4 sm:grid-cols-2 lg:grid-cols-3">
        <transition-group
          name="fade"
          tag="div"
          class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 col-span-full"
        >
          <div
            v-for="tag in tags"
            :key="tag.id"
            class="border border-gray-200 rounded-lg p-4 transition-opacity"
          >
            <div class="flex items-center justify-between">
              <div class="flex-1">
                <span
                  class="inline-block px-2 py-1 text-xs font-medium rounded text-white"
                  :style="{ backgroundColor: tag.color || '#6B7280' }"
                >
                  {{ tag.name }}
                </span>
                <p class="text-sm text-gray-500 mt-1">{{ tag.description || $t('tags.noDescription') }}</p>
              </div>
              <div class="flex space-x-2 ml-2">
                <button
                  @click="editTag(tag)"
                  class="text-indigo-600 hover:text-indigo-900 transition-colors"
                >
                  {{ $t('common.edit') }}
                </button>
                <button
                  @click="deleteTag(tag.id!)"
                  class="text-red-600 hover:text-red-900 transition-colors"
                >
                  {{ $t('common.delete') }}
                </button>
              </div>
            </div>
          </div>
        </transition-group>
        <div v-if="tags.length === 0 && !loading" class="col-span-full text-center py-8 text-gray-500">
          {{ $t('tags.noTags') }}
        </div>
      </div>
    </div>

    <!-- Create/Edit Tag Modal -->
    <Modal :open="showCreateModal" @close="closeCreateModal" :title="editingTagId ? $t('tags.editTagTitle') : $t('tags.createTagTitle')" max-width="md">
      <form @submit.prevent="saveTag" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700">{{ $t('tags.tagName') }} *</label>
          <input
            v-model="tagForm.name"
            type="text"
            required
            class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 transition-colors"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700">{{ $t('tags.description') }}</label>
          <textarea
            v-model="tagForm.description"
            rows="3"
            class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 transition-colors"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700">{{ $t('tags.color') }}</label>
          <div class="mt-2 flex space-x-2">
            <input
              v-model="tagForm.color"
              type="color"
              class="h-10 w-20 border border-gray-300 rounded cursor-pointer transition-colors"
            />
            <input
              v-model="tagForm.color"
              type="text"
              placeholder="#6B7280"
              pattern="^#[0-9A-Fa-f]{6}$"
              class="flex-1 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 transition-colors"
            />
          </div>
          <p class="mt-1 text-xs text-gray-500">{{ $t('tags.colorHint') }}</p>
        </div>
      </form>
      <template #footer>
        <button
          type="button"
          @click="closeCreateModal"
          class="mt-3 inline-flex w-full justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 sm:mt-0 sm:w-auto transition-colors"
        >
          {{ $t('common.cancel') }}
        </button>
        <button
          type="button"
          @click="saveTag"
          :disabled="saving"
          class="inline-flex w-full justify-center rounded-md bg-blue-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-blue-500 sm:ml-3 sm:w-auto disabled:opacity-50 transition-colors"
        >
          {{ saving ? $t('common.loading') : $t('common.save') }}
        </button>
      </template>
    </Modal>

    <!-- Confirm Modal -->
    <ConfirmModal
      :open="showConfirmModal"
      @close="showConfirmModal = false"
      @confirm="handleConfirm"
      :title="$t('tags.confirmDelete')"
      :message="confirmMessage"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { tagsApi, type Tag } from '@/api/tags'
import Modal from '@/components/Modal.vue'
import ConfirmModal from '@/components/ConfirmModal.vue'
import LoadingOverlay from '@/components/LoadingOverlay.vue'
import { useToastStore } from '@/stores/toast'
import { TagIcon, PlusIcon, ArrowPathIcon } from '@heroicons/vue/24/outline'

const { t } = useI18n()
const toastStore = useToastStore()

const tags = ref<Tag[]>([])
const loading = ref(false)
const showCreateModal = ref(false)
const tagForm = ref<Partial<Tag>>({})
const editingTagId = ref<number | null>(null)
const saving = ref(false)
const deletingTagId = ref<number | null>(null)
const showConfirmModal = ref(false)
const confirmAction = ref<(() => void) | null>(null)
const confirmMessage = ref('')

const loadTags = async () => {
  loading.value = true
  try {
    const response = await tagsApi.getTags()
    tags.value = response.data || []
  } catch (error: any) {
    toastStore.error(error.response?.data?.message || t('messages.loadFailed'))
  } finally {
    loading.value = false
  }
}

const openCreateModal = () => {
  tagForm.value = {
    color: '#6B7280',
  }
  editingTagId.value = null
  showCreateModal.value = true
}

const editTag = (tag: Tag) => {
  tagForm.value = { ...tag }
  editingTagId.value = tag.id!
  showCreateModal.value = true
}

const closeCreateModal = () => {
  showCreateModal.value = false
  tagForm.value = {}
  editingTagId.value = null
}

const saveTag = async () => {
  saving.value = true
  try {
    if (editingTagId.value) {
      await tagsApi.updateTag(editingTagId.value, tagForm.value)
      toastStore.success(t('tags.updateSuccess'))
    } else {
      await tagsApi.createTag(tagForm.value as Tag)
      toastStore.success(t('tags.createSuccess'))
    }
    closeCreateModal()
    loadTags()
  } catch (error: any) {
    toastStore.error(error.response?.data?.message || t('messages.saveFailed'))
  } finally {
    saving.value = false
  }
}

const deleteTag = async (id: number) => {
  confirmMessage.value = t('tags.confirmDeleteMessage')
  confirmAction.value = async () => {
    deletingTagId.value = id
    try {
      await tagsApi.deleteTag(id)
      toastStore.success(t('tags.deleteSuccess'))
      loadTags()
    } catch (error: any) {
      toastStore.error(error.response?.data?.message || t('messages.deleteFailed'))
    } finally {
      deletingTagId.value = null
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
  loadTags()
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
