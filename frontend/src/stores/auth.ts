/**
 * 认证状态管理
 */
import { authApi } from '@/api/auth'
import type { LoginRequest } from '@/types'
import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

export const useAuthStore = defineStore('auth', () => {
    // 状态
    const accessToken = ref<string | null>(localStorage.getItem('accessToken'))
    const refreshToken = ref<string | null>(localStorage.getItem('refreshToken'))

    // 计算属性
    const isAuthenticated = computed(() => !!accessToken.value)

    // 登录
    async function login(credentials: LoginRequest) {
        const response = await authApi.login(credentials)

        if (response.success && response.accessToken && response.refreshToken) {
            accessToken.value = response.accessToken
            refreshToken.value = response.refreshToken

            localStorage.setItem('accessToken', response.accessToken)
            localStorage.setItem('refreshToken', response.refreshToken)

            return true
        }

        throw new Error(response.message || '登录失败')
    }

    // 刷新 Access Token
    async function refreshAccessToken() {
        if (!refreshToken.value) {
            throw new Error('No refresh token available')
        }

        const response = await authApi.refresh(refreshToken.value)

        if (response.success && response.accessToken) {
            accessToken.value = response.accessToken
            localStorage.setItem('accessToken', response.accessToken)
        } else {
            throw new Error('刷新 Token 失败')
        }
    }

    // 登出
    async function logout() {
        try {
            await authApi.logout()
        } catch (error) {
            console.error('登出请求失败:', error)
        } finally {
            accessToken.value = null
            refreshToken.value = null
            localStorage.removeItem('accessToken')
            localStorage.removeItem('refreshToken')
        }
    }

    return {
        accessToken,
        refreshToken,
        isAuthenticated,
        login,
        logout,
        refreshAccessToken,
    }
})
