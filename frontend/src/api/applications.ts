import apiClient from './client'

export interface Application {
  id?: number
  name: string
  description?: string
}

export interface HostRelationship {
  from_host_id: number
  to_host_id: number
  relationship_type: string
  description?: string
}

export const applicationsApi = {
  getApplications: () => apiClient.get('/applications'),
  
  createApplication: (data: Application) => apiClient.post('/applications', data),
  
  getApplication: (id: number) => apiClient.get(`/applications/${id}`),
  
  updateApplication: (id: number, data: Partial<Application>) =>
    apiClient.put(`/applications/${id}`, data),
  
  deleteApplication: (id: number) => apiClient.delete(`/applications/${id}`),
  
  addHosts: (id: number, hostIds: number[], relationshipType?: string) =>
    apiClient.post(`/applications/${id}/hosts`, {
      host_ids: hostIds,
      relationship_type: relationshipType || 'member',
    }),
  
  getGraph: (id: number) => apiClient.get(`/applications/${id}/graph`),
  
  createRelationship: (id: number, data: HostRelationship) =>
    apiClient.post(`/applications/${id}/relationships`, data),
}

