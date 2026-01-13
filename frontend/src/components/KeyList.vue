<template>
    <div class="overflow-x-auto">
        <table class="table table-zebra">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>UID</th>
                    <th>Access Key</th>
                    <th>提交人</th>
                    <th>洛谷用户</th>
                    <th>状态</th>
                    <th>验证次数</th>
                    <th>最后验证</th>
                    <th>操作</th>
                </tr>
            </thead>
            <tbody>
                <tr v-if="adminStore.loading && keys.length === 0">
                    <td colspan="10" class="text-center py-8">
                        <span class="loading loading-spinner loading-lg"></span>
                    </td>
                </tr>
                <tr v-else-if="keys.length === 0">
                    <td colspan="10" class="text-center py-8 text-base-content/50">
                        暂无数据
                    </td>
                </tr>
                <KeyItem v-else v-for="key in keys" :key="key.id" :key-info="key" @validate="handleValidate" />
            </tbody>
        </table>
    </div>
</template>

<script setup lang="ts">
import { useAdminStore } from '@/stores/admin'
import { computed } from 'vue'
import KeyItem from './KeyItem.vue'

const adminStore = useAdminStore()

const keys = computed(() => adminStore.keys)

async function handleValidate(keyId: number) {
    try {
        await adminStore.validateKey(keyId)
    } catch (err) {
        console.error('验证失败:', err)
        alert('验证失败，请稍后重试')
    }
}
</script>
