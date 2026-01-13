/**
 * Axios 客户端配置
 */
import { useAuthStore } from '@/stores/auth'
import axios from 'axios'

const client = axios.create({
    baseURL: import.meta.env.VITE_API_URL || '/api',
    timeout: 30000,
    headers: {
        'Content-Type': 'application/json',
    },
})

// 请求拦截器 - 添加 JWT Token
client.interceptors.request.use(
    (config) => {
        const authStore = useAuthStore()
        if (authStore.accessToken) {
            config.headers.Authorization = `Bearer ${authStore.accessToken}`
        }
        return config
    },
    (error) => {
        return Promise.reject(error)
    }
)

// 响应拦截器 - 处理 Token 过期
client.interceptors.response.use(
    (response) => response,
    async (error) => {
        const authStore = useAuthStore()
        const originalRequest = error.config

        // 如果是 401 错误且有 refresh token，尝试刷新
        if (error.response?.status === 401 && !originalRequest._retry && authStore.refreshToken) {
            originalRequest._retry = true

            try {
                await authStore.refreshAccessToken()
                // 重试原请求
                return client(originalRequest)
            } catch (refreshError) {
                // 刷新失败，清除认证信息
                authStore.logout()
                return Promise.reject(refreshError)
            }
        }

        return Promise.reject(error)
    }
)

export default client
