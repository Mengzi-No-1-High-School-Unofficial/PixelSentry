<template>
    <div class="card bg-base-100 shadow-xl">
        <div class="card-body">
            <h2 class="card-title">提交剪贴板信息</h2>

            <form @submit.prevent="handleSubmit">
                <div class="form-control">
                    <label class="label">
                        <span class="label-text">洛谷用户 ID（可选）</span>
                    </label>
                    <input v-model="uid" type="text" placeholder="例如: 111（留空将自动从剪贴板解析）" class="input input-bordered" />
                    <label class="label">
                        <span class="label-text-alt">如不填写，系统将自动从剪贴板解析 UID</span>
                    </label>
                </div>

                <div class="form-control mt-4">
                    <label class="label">
                        <span class="label-text">剪贴板 ID</span>
                    </label>
                    <input v-model="pasteId" type="text" placeholder="例如: ilovecz6" class="input input-bordered"
                        required />
                    <label class="label">
                        <span class="label-text-alt">云剪贴板的 ID</span>
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

                <div v-if="success" class="alert alert-success mt-4">
                    <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none"
                        viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <span>{{ success }}</span>
                </div>

                <div class="form-control mt-6">
                    <button type="submit" class="btn btn-primary" :class="{ loading: loading }" :disabled="loading">
                        {{ loading ? '提交中...' : '提交' }}
                    </button>
                </div>
            </form>

            <div class="divider"></div>

            <div class="text-sm text-base-content/70">
                <p class="mb-2">📝 <strong>使用说明：</strong></p>
                <ul class="list-disc list-inside space-y-1 ml-2">
                    <li>填写云剪贴板 ID（必填）</li>
                    <li>UID 可选填，留空将自动从剪贴板解析</li>
                    <li>系统将自动获取 Access Key</li>
                    <li>处理过程可能需要 10-30 秒</li>
                    <li>提交后可在下方查看处理状态</li>
                </ul>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { userApi } from '@/api/user';
import { ref } from 'vue';

const emit = defineEmits<{
    submitted: [id: number]
}>()

const uid = ref('')
const pasteId = ref('')
const loading = ref(false)
const error = ref('')
const success = ref('')

async function handleSubmit() {
    loading.value = true
    error.value = ''
    success.value = ''

    try {
        const response = await userApi.submit({
            uid: uid.value.trim() || undefined,  // 空字符串转为 undefined
            pasteId: pasteId.value,
        })

        if (response.success && response.submissionId) {
            success.value = response.message || '提交成功！'
            emit('submitted', response.submissionId)

            // 清空表单
            uid.value = ''
            pasteId.value = ''
        } else {
            error.value = response.message || '提交失败'
        }
    } catch (err: any) {
        error.value = err.response?.data?.detail || err.message || '提交失败，请稍后重试'
    } finally {
        loading.value = false
    }
}
</script>
