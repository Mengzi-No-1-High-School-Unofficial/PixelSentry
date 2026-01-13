<template>
    <div class="card bg-base-100 shadow-xl">
        <div class="card-body">
            <h2 class="card-title">批量提交</h2>

            <form @submit.prevent="handleSubmit">
                <div class="form-control">
                    <label class="label">
                        <span class="label-text">提交人姓名（可选）</span>
                    </label>
                    <input v-model="submitterName" type="text" placeholder="例如: 张三" class="input input-bordered" />
                </div>

                <div class="form-control mt-4">
                    <label class="label">
                        <span class="label-text">剪贴板链接（每行一个）</span>
                    </label>
                    <textarea v-model="pasteUrls" rows="10"
                        placeholder="https://www.luogu.com/paste/abc123&#10;https://www.luogu.com/paste/def456"
                        class="textarea textarea-bordered font-mono text-sm" required></textarea>
                    <label class="label">
                        <span class="label-text-alt">共 {{ urlCount }} 个链接</span>
                    </label>
                </div>

                <div v-if="error" class="alert alert-error mt-4">
                    <span>{{ error }}</span>
                </div>

                <div class="form-control mt-6">
                    <button type="submit" class="btn btn-primary" :disabled="loading">
                        {{ loading ? '提交中...' : '批量提交' }}
                    </button>
                </div>
            </form>

            <!-- 结果显示 -->
            <div v-if="submissions.length > 0" class="mt-6">
                <div class="stats stats-vertical lg:stats-horizontal shadow w-full">
                    <div class="stat">
                        <div class="stat-title">总数</div>
                        <div class="stat-value">{{ stats.total }}</div>
                    </div>
                    <div class="stat">
                        <div class="stat-title">处理中</div>
                        <div class="stat-value text-warning">{{ stats.pending }}</div>
                    </div>
                    <div class="stat">
                        <div class="stat-title">成功</div>
                        <div class="stat-value text-success">{{ stats.success }}</div>
                    </div>
                    <div class="stat">
                        <div class="stat-title">失败</div>
                        <div class="stat-value text-error">{{ stats.failed }}</div>
                    </div>
                </div>

                <div v-if="polling" class="alert alert-info mt-4">
                    <span>正在实时更新状态...</span>
                </div>

                <!-- 详细结果 -->
                <div class="overflow-x-auto mt-4">
                    <table class="table table-zebra table-sm">
                        <thead>
                            <tr>
                                <th>剪贴板 ID</th>
                                <th>提交 ID</th>
                                <th>状态</th>
                                <th>Access Key</th>
                                <th>错误</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="(sub, index) in submissions" :key="index">
                                <td class="font-mono text-xs">{{ sub.pasteId }}</td>
                                <td>{{ sub.submissionId || '-' }}</td>
                                <td>
                                    <span v-if="!sub.success" class="badge badge-error badge-sm">创建失败</span>
                                    <span v-else-if="sub.status === 'pending'"
                                        class="badge badge-warning badge-sm">等待中</span>
                                    <span v-else-if="sub.status === 'processing'"
                                        class="badge badge-info badge-sm">处理中</span>
                                    <span v-else-if="sub.status === 'success'"
                                        class="badge badge-success badge-sm">成功</span>
                                    <span v-else-if="sub.status === 'failed'"
                                        class="badge badge-error badge-sm">失败</span>
                                </td>
                                <td class="font-mono text-xs">{{ sub.accessKey || '-' }}</td>
                                <td class="text-xs text-error">{{ sub.error || sub.errorMessage || '-' }}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { userApi } from '@/api/user'
import { computed, onUnmounted, ref } from 'vue'

const submitterName = ref('')
const pasteUrls = ref('')
const loading = ref(false)
const error = ref('')
const submissions = ref<any[]>([])
const polling = ref(false)
let pollingInterval: number | null = null

const urlCount = computed(() => {
    if (!pasteUrls.value.trim()) return 0
    return pasteUrls.value.trim().split('\n').filter(line => line.trim()).length
})

const stats = computed(() => {
    const total = submissions.value.length
    const pending = submissions.value.filter(s => s.success && (s.status === 'pending' || s.status === 'processing')).length
    const success = submissions.value.filter(s => s.status === 'success').length
    const failed = submissions.value.filter(s => !s.success || s.status === 'failed').length
    return { total, pending, success, failed }
})

async function handleSubmit() {
    loading.value = true
    error.value = ''
    submissions.value = []

    try {
        const lines = pasteUrls.value.trim().split('\n')
        const pasteIds = lines.map(line => line.trim()).filter(line => line.length > 0)

        if (pasteIds.length === 0) {
            error.value = '请至少输入一个剪贴板链接'
            return
        }

        const response = await userApi.submitBatch({
            pasteIds,
            submitterName: submitterName.value.trim() || undefined,
        })

        if (response.success) {
            submissions.value = response.submissions.map((s: any) => ({
                pasteId: s.pasteId,
                submissionId: s.submissionId,
                status: s.success ? 'pending' : 'failed',
                error: s.error,
                success: s.success,
                accessKey: null,
                errorMessage: null
            }))

            pasteUrls.value = ''
            startPolling()
        } else {
            error.value = response.message || '批量提交失败'
        }
    } catch (err: any) {
        error.value = err.response?.data?.detail || err.message || '批量提交失败'
    } finally {
        loading.value = false
    }
}

function startPolling() {
    polling.value = true
    pollingInterval = window.setInterval(async () => {
        await updateStatuses()
    }, 2000)
}

function stopPolling() {
    if (pollingInterval) {
        clearInterval(pollingInterval)
        pollingInterval = null
    }
    polling.value = false
}

async function updateStatuses() {
    const pendingSubmissions = submissions.value.filter(
        s => s.success && (s.status === 'pending' || s.status === 'processing')
    )

    if (pendingSubmissions.length === 0) {
        stopPolling()
        return
    }

    for (const submission of pendingSubmissions) {
        try {
            const response = await userApi.getSubmissionStatus(submission.submissionId)
            if (response.success && response.data) {
                submission.status = response.data.status
                submission.accessKey = response.data.accessKey
                submission.errorMessage = response.data.errorMessage
            }
        } catch (err) {
            console.error(`查询提交 ${submission.submissionId} 状态失败:`, err)
        }
    }
}

onUnmounted(() => {
    stopPolling()
})
</script>
