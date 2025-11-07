import apiClient from './client'

export interface Tag {
  id?: number
  name: string
  color?: string
  description?: string
}

export const tagsApi = {
  getTags: () => apiClient.get('/tags'),
  
  createTag: (data: Tag) => apiClient.post('/tags', data),
  
  updateTag: (id: number, data: Partial<Tag>) => apiClient.put(`/tags/${id}`, data),
  
  deleteTag: (id: number) => apiClient.delete(`/tags/${id}`),
  
  addHostTags: (hostId: number, tagIds: number[]) =>
    apiClient.post(`/tags/hosts/${hostId}`, { tag_ids: tagIds }),
  
  removeHostTag: (hostId: number, tagId: number) =>
    apiClient.delete(`/tags/hosts/${hostId}/${tagId}`),
}

