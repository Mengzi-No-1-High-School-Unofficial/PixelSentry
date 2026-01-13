<template>
    <tr>
        <td>{{ keyInfo.id }}</td>
        <td>{{ keyInfo.uid }}</td>
        <td>
            <div class="flex items-center gap-2">
                <code class="text-sm">{{ keyInfo.accessKey }}</code>
                <button @click="copyToClipboard" class="btn btn-ghost btn-xs" title="复制">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24"
                        stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                    </svg>
                </button>
            </div>
        </td>
        <td>
            <div v-if="keyInfo.paintToken" class="flex items-center gap-2">
                <code class="text-sm text-success">{{ keyInfo.paintToken.substring(0, 8) }}...</code>
                <button @click="copyPaintToken" class="btn btn-ghost btn-xs" title="复制 Paint Token">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24"
                        stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                    </svg>
                </button>
            </div>
            <span v-else class="text-base-content/50 text-sm">未换取</span>
        </td>
        <td>{{ keyInfo.submitterName || '-' }}</td>
        <td>{{ keyInfo.username || '-' }}</td>
        <td>
            <div class="badge" :class="keyInfo.isValid ? 'badge-success' : 'badge-error'">
                {{ keyInfo.isValid ? '有效' : '无效' }}
            </div>
        </td>
        <td>{{ keyInfo.validationCount }}</td>
        <td>
            <span v-if="keyInfo.lastValidatedAt" class="text-sm">
                {{ formatDate(keyInfo.lastValidatedAt) }}
            </span>
            <span v-else class="text-base-content/50">未验证</span>
        </td>
        <td>
            <button @click="handleValidate" class="btn btn-primary btn-sm" :class="{ loading: validating }"
                :disabled="validating">
                换取 Token
            </button>
        </td>
    </tr>
</template>

<script setup lang="ts">
import type { AccessKeyInfo } from '@/types';
import { ref } from 'vue';

const props = defineProps<{
    keyInfo: AccessKeyInfo
}>()

const emit = defineEmits<{
    validate: [keyId: number]
}>()

const validating = ref(false)

async function handleValidate() {
    validating.value = true
    try {
        emit('validate', props.keyInfo.id)
    } finally {
        // 延迟重置状态，避免闪烁
        setTimeout(() => {
            validating.value = false
        }, 500)
    }
}

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

async function copyToClipboard() {
    try {
        await navigator.clipboard.writeText(props.keyInfo.accessKey)
        alert('Access Key 已复制到剪贴板')
    } catch (err) {
        console.error('复制失败:', err)
    }
}

async function copyPaintToken() {
    if (!props.keyInfo.paintToken) return
    try {
        await navigator.clipboard.writeText(props.keyInfo.paintToken)
        alert('Paint Token 已复制到剪贴板')
    } catch (err) {
        console.error('复制失败:', err)
    }
}

</script>
