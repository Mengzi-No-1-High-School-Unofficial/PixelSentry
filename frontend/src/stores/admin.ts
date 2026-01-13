/**
 * 管理面板状态管理
 */
import { adminApi } from '@/api/admin'
import type { AccessKeyInfo, StatsData } from '@/types'
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAdminStore = defineStore('admin', () => {
    // 状态
    const keys = ref<AccessKeyInfo[]>([])
    const stats = ref<StatsData | null>(null)
    const loading = ref(false)

    // 获取所有 Key
    async function fetchKeys() {
        loading.value = true
        try {
            const response = await adminApi.getKeys()
            if (response.success) {
                keys.value = response.data
            }
        } finally {
            loading.value = false
        }
    }

    // 验证 Key
    async function validateKey(keyId: number) {
        const response = await adminApi.validateKey(keyId)
        if (response.success) {
            // 更新本地状态
            const key = keys.value.find(k => k.id === keyId)
            if (key) {
                key.isValid = response.data.isValid
                key.validationCount += 1
                key.lastValidatedAt = new Date().toISOString()
            }
        }
        return response
    }

    // 获取统计信息
    async function fetchStats() {
        const response = await adminApi.getStats()
        if (response.success) {
            stats.value = response.data
        }
    }

    return {
        keys,
        stats,
        loading,
        fetchKeys,
        validateKey,
        fetchStats,
    }
})
