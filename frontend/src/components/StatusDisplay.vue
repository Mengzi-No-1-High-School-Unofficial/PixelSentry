<template>
    <div class="card bg-base-100 shadow-xl">
        <div class="card-body">
            <div class="flex justify-between items-center mb-4">
                <h2 class="card-title">处理状态</h2>
                <button @click="refresh" class="btn btn-ghost btn-sm btn-circle" :class="{ loading: loading }">
                    <svg v-if="!loading" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none"
                        viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                    </svg>
                </button>
            </div>

            <div v-if="status" class="space-y-4">
                <!-- 状态标签 -->
                <div class="flex items-center gap-2">
                    <span class="text-sm font-medium">状态：</span>
                    <div class="badge" :class="statusBadgeClass">
                        {{ statusText }}
                    </div>
                </div>

                <!-- 处理中动画 -->
                <div v-if="status.status === 'processing'" class="flex items-center gap-3">
                    <span class="loading loading-spinner loading-md"></span>
                    <span class="text-sm">正在处理中，请稍候...</span>
                </div>

                <!-- Access Key 显示 -->
                <div v-if="status.status === 'success' && status.accessKey" class="space-y-2">
                    <div class="form-control">
                        <label class="label">
                            <span class="label-text font-medium">Access Key</span>
                            <span v-if="status.isValid !== undefined" class="badge"
                                :class="status.isValid ? 'badge-success' : 'badge-error'">
                                {{ status.isValid ? '有效' : '无效' }}
                            </span>
                        </label>
                        <div class="flex gap-2">
                            <input :value="status.accessKey" type="text" class="input input-bordered flex-1 font-mono"
                                readonly />
                            <button @click="copyToClipboard(status.accessKey)" class="btn btn-square btn-outline">
                                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24"
                                    stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                        d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                                </svg>
                            </button>
                        </div>
                    </div>
                </div>

                <!-- 错误信息 -->
                <div v-if="status.status === 'failed' && status.errorMessage" class="alert alert-error">
                    <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none"
                        viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <span>{{ status.errorMessage }}</span>
                </div>

                <!-- 创建时间 -->
                <div class="text-sm text-base-content/70">
                    提交时间：{{ formatDate(status.createdAt) }}
                </div>
            </div>

            <div v-else-if="loading" class="flex justify-center py-8">
                <span class="loading loading-spinner loading-lg"></span>
            </div>

            <div v-else class="text-center py-8 text-base-content/50">
                暂无数据
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { userApi } from '@/api/user';
import type { SubmissionStatus } from '@/types';
import { computed, onMounted, onUnmounted, ref } from 'vue';

const props = defineProps<{
    submissionId: number
}>()

const status = ref<SubmissionStatus | null>(null)
const loading = ref(false)
let intervalId: number | null = null

const statusText = computed(() => {
    if (!status.value) return ''

    const statusMap = {
        pending: '等待处理',
        processing: '处理中',
        success: '成功',
        failed: '失败',
    }

    return statusMap[status.value.status] || status.value.status
})

const statusBadgeClass = computed(() => {
    if (!status.value) return ''

    const classMap = {
        pending: 'badge-warning',
        processing: 'badge-info',
        success: 'badge-success',
        failed: 'badge-error',
    }

    return classMap[status.value.status] || ''
})

async function refresh() {
    loading.value = true
    try {
        const response = await userApi.getSubmissionStatus(props.submissionId)
        if (response.success && response.data) {
            status.value = response.data

            // 如果已完成（成功或失败），停止轮询
            if (status.value.status === 'success' || status.value.status === 'failed') {
                stopPolling()
            }
        }
    } catch (err) {
        console.error('获取状态失败:', err)
    } finally {
        loading.value = false
    }
}

function startPolling() {
    // 每 3 秒轮询一次
    intervalId = window.setInterval(refresh, 3000)
}

function stopPolling() {
    if (intervalId !== null) {
        clearInterval(intervalId)
        intervalId = null
    }
}

function formatDate(dateString: string): string {
    const date = new Date(dateString)
    return date.toLocaleString('zh-CN')
}

async function copyToClipboard(text: string) {
    try {
        await navigator.clipboard.writeText(text)
        alert('已复制到剪贴板')
    } catch (err) {
        console.error('复制失败:', err)
    }
}

onMounted(() => {
    refresh()
    startPolling()
})

onUnmounted(() => {
    stopPolling()
})
</script>
