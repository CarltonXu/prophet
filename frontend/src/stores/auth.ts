import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi, type LoginRequest, type RegisterRequest } from '@/api/auth'
import router from '@/router'

interface User {
  id: number
  username: string
  email: string
  is_admin: boolean
}

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('access_token'))
  const isLoading = ref(false)
  
  const isAuthenticated = computed(() => !!token.value)
  
  const login = async (data: LoginRequest) => {
    try {
      const response = await authApi.login(data) as any
      if (response.code === 200) {
        token.value = response.data.access_token
        user.value = response.data.user
        localStorage.setItem('access_token', response.data.access_token)
        router.push('/')
        return true
      }
      return false
    } catch (error: any) {
      throw error.response?.data?.message || 'Login failed'
    }
  }
  
  const register = async (data: RegisterRequest) => {
    try {
      const response = await authApi.register(data) as any
      if (response.code === 200) {
        return true
      }
      return false
    } catch (error: any) {
      throw error.response?.data?.message || 'Registration failed'
    }
  }
  
  const logout = async () => {
    try {
      await authApi.logout()
    } catch (error) {
      // Ignore errors
    } finally {
      token.value = null
      user.value = null
      localStorage.removeItem('access_token')
      router.push('/login')
    }
  }
  
  const fetchCurrentUser = async () => {
    if (!token.value) {
      return false
    }
    isLoading.value = true
    try {
      const response = await authApi.getCurrentUser() as any
      if (response.code === 200) {
        user.value = response.data
        return true
      }
      return false
    } catch (error) {
      token.value = null
      user.value = null
      localStorage.removeItem('access_token')
      return false
    } finally {
      isLoading.value = false
    }
  }
  
  // Initialize user if token exists
  if (token.value) {
    fetchCurrentUser()
  }
  
  return {
    user,
    token,
    isLoading,
    isAuthenticated,
    login,
    register,
    logout,
    fetchCurrentUser,
  }
})

