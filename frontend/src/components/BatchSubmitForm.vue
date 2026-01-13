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
                    <label class="label">
                        <span class="label-text-alt">用于标识提交人</span>
                    </label>
                </div>

                <div class="form-control mt-4">
                    <label class="label">
                        <span class="label-text">剪贴板链接（每行一个）</span>
                    </label>
                    <textarea v-model="pasteUrls" rows="10"
                        placeholder="https://www.luogu.com/paste/abc123&#10;https://www.luogu.com/paste/def456&#10;https://www.luogu.com/paste/ghi789"
                        class="textarea textarea-bordered font-mono text-sm" required></textarea>
                    <label class="label">
                        <span class="label-text-alt">共 {{ urlCount }} 个链接</span>
                    </label>
                </div>

                <div v-if="error" class="alert alert-error mt-4">
                    <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none"
                        viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <span>{{ error }}</span>
                </div>

                <div class="form-control mt-6">
                    <button type="submit" class="btn btn-primary" :class="{ loading: loading }" :disabled="loading">
                        {{ loading ? '提交中...' : '批量提交' }}
                    </button>
                </div>
            </form>

            <!-- 结果显示 -->
            <div v-if="results" class="mt-6">
                <div class="stats stats-vertical lg:stats-horizontal shadow w-full">
                    <div class="stat">
                        <div class="stat-title">总数</div>
                        <div class="stat-value">{{ results.total }}</div>
                    </div>
                    <div class="stat">
                        <div class="stat-title">成功</div>
                        <div class="stat-value text-success">{{ results.succeeded }}</div>
                    </div>
                    <div class="stat">
                        <div class="stat-title">失败</div>
                        <div class="stat-value text-error">{{ results.failed }}</div>
                    </div>
                </div>

                <!-- 详细结果 -->
                <div class="overflow-x-auto mt-4">
                    <table class="table table-zebra table-sm">
                        <thead>
                            <tr>
                                <th>剪贴板 ID</th>
                                <th>状态</th>
                                <th>提交 ID</th>
                                <th>错误信息</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="(result, index) in results.results" :key="index">
                                <td class="font-mono text-xs">{{ result.pasteId }}</td>
                                <td>
                                    <span
                                        :class="result.success ? 'badge badge-success badge-sm' : 'badge badge-error badge-sm'">
                                        {{ result.success ? '成功' : '失败' }}
                                    </span>
                                </td>
                                <td>{{ result.submissionId || '-' }}</td>
                                <td class="text-xs text-error">{{ result.error || '-' }}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <div class="divider"></div>

            <div class="text-sm text-base-content/70">
                <p class="mb-2">📝 <strong>使用说明：</strong></p>
                <ul class="list-disc list-inside space-y-1 ml-2">
                    <li>每行输入一个剪贴板链接或 ID</li>
                    <li>支持完整 URL 或纯 ID</li>
                    <li>系统将自动解析每个剪贴板的 UID 和用户名</li>
                    <li>处理完成后显示详细结果</li>
                </ul>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { userApi } from '@/api/user'
import { computed, ref } from 'vue'

const submitterName = ref('')
const pasteUrls = ref('')
const loading = ref(false)
const error = ref('')
const results = ref<any>(null)

const urlCount = computed(() => {
    if (!pasteUrls.value.trim()) return 0
    return pasteUrls.value.trim().split('\n').filter(line => line.trim()).length
})

async function handleSubmit() {
    loading.value = true
    error.value = ''
    results.value = null

    try {
        // 解析每行，提取链接
        const lines = pasteUrls.value.trim().split('\n')
        const pasteIds = lines
            .map(line => line.trim())
            .filter(line => line.length > 0)

        if (pasteIds.length === 0) {
            error.value = '请至少输入一个剪贴板链接'
            return
        }

        const response = await userApi.submitBatch({
            pasteIds,
            submitterName: submitterName.value.trim() || undefined,
        })

        if (response.success) {
            results.value = response
            // 清空表单
            pasteUrls.value = ''
        } else {
            error.value = response.message || '批量提交失败'
        }
    } catch (err: any) {
        error.value = err.response?.data?.detail || err.message || '批量提交失败，请稍后重试'
    } finally {
        loading.value = false
    }
}
</script>
