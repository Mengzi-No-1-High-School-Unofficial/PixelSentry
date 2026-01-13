<template>
    <tr>
        <td>{{ submission.id }}</td>
        <td>{{ submission.uid }}</td>
        <td>{{ submission.pasteId }}</td>
        <td>
            <div class="badge" :class="statusBadgeClass">
                {{ statusText }}
            </div>
        </td>
        <td>
            <span v-if="submission.loginToken" class="text-xs font-mono">
                {{ submission.loginToken }}
            </span>
            <span v-else class="text-base-content/50">-</span>
        </td>
        <td>
            <span v-if="submission.accessKey" class="text-sm font-mono">
                {{ submission.accessKey }}
            </span>
            <span v-else class="text-base-content/50">-</span>
        </td>
        <td>
            <span v-if="submission.errorMessage" class="text-xs text-error">
                {{ submission.errorMessage }}
            </span>
            <span v-else class="text-base-content/50">-</span>
        </td>
        <td>
            <span class="text-sm">{{ formatDate(submission.createdAt) }}</span>
        </td>
        <td>
            <div class="dropdown dropdown-end" v-if="canRetry">
                <label tabindex="0" class="btn btn-primary btn-sm">
                    重试
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 ml-1" fill="none" viewBox="0 0 24 24"
                        stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                    </svg>
                </label>
                <ul tabindex="0" class="dropdown-content z-[1] menu p-2 shadow bg-base-100 rounded-box w-52">
                    <li>
                        <a @click="handleRetry(false)">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24"
                                stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                    d="M13 10V3L4 14h7v7l9-11h-7z" />
                            </svg>
                            智能重试
                            <span class="badge badge-sm badge-success">推荐</span>
                        </a>
                    </li>
                    <li>
                        <a @click="handleRetry(true)">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24"
                                stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                    d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                            </svg>
                            完整重试
                        </a>
                    </li>
                </ul>
            </div>
            <span v-else-if="submission.status === 'processing'" class="loading loading-spinner loading-sm"></span>
            <span v-else class="text-base-content/50">-</span>
        </td>
    </tr>
</template>

<script setup lang="ts">
import type { Submission } from '@/types';
import { computed } from 'vue';

const props = defineProps<{
    submission: Submission
}>()

const emit = defineEmits<{
    retry: [submissionId: number, forceFull: boolean]
}>()

const statusText = computed(() => {
    const statusMap = {
        pending: '等待处理',
        processing: '处理中',
        success: '成功',
        failed: '失败',
    }
    return statusMap[props.submission.status] || props.submission.status
})

const statusBadgeClass = computed(() => {
    const classMap = {
        pending: 'badge-warning',
        processing: 'badge-info',
        success: 'badge-success',
        failed: 'badge-error',
    }
    return classMap[props.submission.status] || ''
})

const canRetry = computed(() => {
    return props.submission.status === 'failed' || props.submission.status === 'pending'
})

function formatDate(dateString: string): string {
    const date = new Date(dateString)
    const now = new Date()
    const diff = now.getTime() - date.getTime()

    // 小于 1 分钟
    if (diff < 60000) {
        return '刚刚'
    }

    // 小于 1 小时
    if (diff < 3600000) {
        const minutes = Math.floor(diff / 60000)
        return `${minutes} 分钟前`
    }

    // 小于 1 天
    if (diff < 86400000) {
        const hours = Math.floor(diff / 3600000)
        return `${hours} 小时前`
    }

    // 显示完整日期
    return date.toLocaleString('zh-CN')
}

function handleRetry(forceFull: boolean) {
    if (confirm(`确定要${forceFull ? '完整重试' : '智能重试'}吗？`)) {
        emit('retry', props.submission.id, forceFull)
    }
}
</script>
