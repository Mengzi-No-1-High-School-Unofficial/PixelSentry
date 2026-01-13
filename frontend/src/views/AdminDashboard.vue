<template>
  <div class="min-h-screen bg-base-200">
    <div class="navbar bg-base-100 shadow-lg">
      <div class="flex-1">
        <a class="btn btn-ghost normal-case text-xl">PixelSentry 管理面板</a>
      </div>
      <div class="flex-none">
        <button @click="handleLogout" class="btn btn-ghost btn-sm">
          登出
        </button>
      </div>
    </div>

    <div class="container mx-auto px-4 py-8">
      <!-- 统计面板 -->
      <StatsPanel class="mb-8" />

      <!-- Access Key 列表 -->
      <div class="card bg-base-100 shadow-xl">
        <div class="card-body">
          <div class="flex justify-between items-center mb-4">
            <h2 class="card-title">Access Key 列表</h2>
            <button 
              @click="refreshKeys" 
              class="btn btn-primary btn-sm"
              :class="{ loading: adminStore.loading }"
            >
              刷新
            </button>
          </div>

          <KeyList />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useAdminStore } from '@/stores/admin'
import StatsPanel from '@/components/StatsPanel.vue'
import KeyList from '@/components/KeyList.vue'

const router = useRouter()
const authStore = useAuthStore()
const adminStore = useAdminStore()

onMounted(async () => {
  await refreshKeys()
})

async function refreshKeys() {
  await Promise.all([
    adminStore.fetchKeys(),
    adminStore.fetchStats(),
  ])
}

async function handleLogout() {
  await authStore.logout()
  router.push('/admin/login')
}
</script>
