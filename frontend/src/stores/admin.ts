import { adminApi } from '@/api/admin'
import type { AccessKeyInfo, Stats, Submission } from '@/types'
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAdminStore = defineStore('admin', () => {
    const keys = ref<AccessKeyInfo[]>([])
    const submissions = ref<Submission[]>([])
    const stats = ref<Stats | null>(null)
    const loading = ref(false)

    async function fetchKeys() {
        loading.value = true
        try {
            const response = await adminApi.getKeys()
            if (response.success) {
                keys.value = response.data
            }
        } catch (error) {
            console.error('获取 Keys 失败:', error)
            throw error
        } finally {
            loading.value = false
        }
    }

    async function fetchSubmissions() {
        loading.value = true
        try {
            const response = await adminApi.getSubmissions()
            if (response.success) {
                submissions.value = response.data
            }
        } catch (error) {
            console.error('获取提交记录失败:', error)
            throw error
        } finally {
            loading.value = false
        }
    }

    async function fetchStats() {
        try {
            const response = await adminApi.getStats()
            if (response.success) {
                stats.value = response.data
            }
        } catch (error) {
            console.error('获取统计信息失败:', error)
            throw error
        }
    }

    async function validateKey(keyId: number) {
        try {
            const response = await adminApi.validateKey(keyId)
            if (response.success) {
                // 重新获取列表
                await fetchKeys()
            }
            return response
        } catch (error) {
            console.error('验证 Key 失败:', error)
            throw error
        }
    }

    async function retrySubmission(submissionId: number, forceFull: boolean = false) {
        try {
            const response = await adminApi.retrySubmission(submissionId, forceFull)
            if (response.success) {
                // 重新获取提交列表
                await fetchSubmissions()
            }
            return response
        } catch (error) {
            console.error('重试提交失败:', error)
            throw error
        }
    }

    return {
        keys,
        submissions,
        stats,
        loading,
        fetchKeys,
        fetchSubmissions,
        fetchStats,
        validateKey,
        retrySubmission,
    }
})
