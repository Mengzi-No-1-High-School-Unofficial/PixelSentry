<template>
  <div class="min-h-screen bg-base-200">
    <div class="navbar bg-base-100 shadow-lg">
      <div class="flex-1">
        <a class="btn btn-ghost normal-case text-xl">PixelSentry 管理面板</a>
      </div>
      <div class="flex-none gap-2">
        <button @click="router.push('/help')" class="btn btn-ghost btn-sm">
          使用帮助
        </button>
        <button @click="router.push('/')" class="btn btn-ghost btn-sm">
          回到首页
        </button>
        <button @click="handleLogout" class="btn btn-ghost btn-sm">
          登出
        </button>
      </div>
    </div>

    <div class="container mx-auto px-4 py-8">
      <!-- 统计面板 -->
      <StatsPanel class="mb-8" />

      <!-- 标签页 -->
      <div class="tabs tabs-boxed mb-4">
        <a class="tab" :class="{ 'tab-active': activeTab === 'keys' }" @click="activeTab = 'keys'">
          Access Key 列表
        </a>
        <a class="tab" :class="{ 'tab-active': activeTab === 'submissions' }" @click="activeTab = 'submissions'">
          提交记录
        </a>
      </div>

      <!-- Access Key 列表 -->
      <div v-show="activeTab === 'keys'" class="card bg-base-100 shadow-xl">
        <div class="card-body">
          <div class="flex justify-between items-center mb-4">
            <h2 class="card-title">Access Key 列表</h2>
            <div class="flex gap-2">
              <button @click="showExportDialog = true" class="btn btn-secondary btn-sm"
                :disabled="adminStore.keys.length === 0">
                导出配置
              </button>
              <button @click="refreshKeys" class="btn btn-primary btn-sm" :class="{ loading: adminStore.loading }">
                刷新
              </button>
            </div>
          </div>

          <KeyList />
        </div>
      </div>

      <!-- 提交记录列表 -->
      <div v-show="activeTab === 'submissions'" class="card bg-base-100 shadow-xl">
        <div class="card-body">
          <div class="flex justify-between items-center mb-4">
            <h2 class="card-title">提交记录</h2>
            <button @click="refreshSubmissions" class="btn btn-primary btn-sm" :class="{ loading: adminStore.loading }">
              刷新
            </button>
          </div>

          <SubmissionList />
        </div>
      </div>
    </div>

    <!-- 导出对话框 -->
    <ExportDialog v-model="showExportDialog" :keys="adminStore.keys" />
  </div>
</template>

<script setup lang="ts">
import ExportDialog from '@/components/ExportDialog.vue'
import KeyList from '@/components/KeyList.vue'
import StatsPanel from '@/components/StatsPanel.vue'
import SubmissionList from '@/components/SubmissionList.vue'
import { useAdminStore } from '@/stores/admin'
import { useAuthStore } from '@/stores/auth'
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const authStore = useAuthStore()
const adminStore = useAdminStore()

const activeTab = ref<'keys' | 'submissions'>('keys')
const showExportDialog = ref(false)

onMounted(async () => {
  await refreshAll()
})

async function refreshKeys() {
  await Promise.all([
    adminStore.fetchKeys(),
    adminStore.fetchStats(),
  ])
}

async function refreshSubmissions() {
  await Promise.all([
    adminStore.fetchSubmissions(),
    adminStore.fetchStats(),
  ])
}

async function refreshAll() {
  await Promise.all([
    adminStore.fetchKeys(),
    adminStore.fetchSubmissions(),
    adminStore.fetchStats(),
  ])
}

async function handleLogout() {
  await authStore.logout()
  router.push('/admin/login')
}
</script>
