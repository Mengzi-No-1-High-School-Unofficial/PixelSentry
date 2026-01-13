<template>
    <div class="overflow-x-auto">
        <table class="table table-zebra">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>UID</th>
                    <th>剪贴板 ID</th>
                    <th>提交人</th>
                    <th>洛谷用户</th>
                    <th>状态</th>
                    <th>Login Token</th>
                    <th>Access Key</th>
                    <th>错误信息</th>
                    <th>创建时间</th>
                    <th>操作</th>
                </tr>
            </thead>
            <tbody>
                <tr v-if="adminStore.loading && submissions.length === 0">
                    <td colspan="11" class="text-center py-8">
                        <span class="loading loading-spinner loading-lg"></span>
                    </td>
                </tr>
                <tr v-else-if="submissions.length === 0">
                    <td colspan="11" class="text-center py-8 text-base-content/50">
                        暂无提交记录
                    </td>
                </tr>
                <SubmissionItem v-else v-for="submission in submissions" :key="submission.id" :submission="submission"
                    @retry="handleRetry" />
            </tbody>
        </table>
    </div>
</template>

<script setup lang="ts">
import { useAdminStore } from '@/stores/admin'
import { computed } from 'vue'
import SubmissionItem from './SubmissionItem.vue'

const adminStore = useAdminStore()

const submissions = computed(() => adminStore.submissions)

async function handleRetry(submissionId: number, forceFull: boolean) {
    try {
        await adminStore.retrySubmission(submissionId, forceFull)
        alert('重试任务已启动')
    } catch (err) {
        console.error('重试失败:', err)
        alert('重试失败，请稍后重试')
    }
}
</script>
