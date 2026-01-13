<template>
  <div class="min-h-screen bg-base-200">
    <div class="container mx-auto px-4 py-8">
      <div class="text-center mb-8">
        <h1 class="text-5xl font-bold bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
          PixelSentry
        </h1>
        <p class="text-xl mt-2 text-base-content/70">冬日绘版 Token 收集工具</p>
      </div>

      <div class="max-w-2xl mx-auto">
        <!-- 标签页 -->
        <div class="tabs tabs-boxed mb-4 justify-center">
          <a class="tab" :class="{ 'tab-active': activeTab === 'single' }" @click="activeTab = 'single'">
            单个提交
          </a>
          <a class="tab" :class="{ 'tab-active': activeTab === 'batch' }" @click="activeTab = 'batch'">
            批量提交
          </a>
        </div>

        <!-- 单个提交 -->
        <div v-show="activeTab === 'single'">
          <SubmitForm @submitted="handleSubmitted" />

          <StatusDisplay v-if="submissionId" :submission-id="submissionId" class="mt-8" />
        </div>

        <!-- 批量提交 -->
        <div v-show="activeTab === 'batch'">
          <BatchSubmitForm />
        </div>
      </div>

      <div class="text-center mt-12 flex justify-center gap-4">
        <router-link to="/help" class="btn btn-ghost btn-sm">
          使用帮助
        </router-link>
        <router-link to="/admin/login" class="btn btn-ghost btn-sm">
          管理员登录
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import BatchSubmitForm from '@/components/BatchSubmitForm.vue'
import StatusDisplay from '@/components/StatusDisplay.vue'
import SubmitForm from '@/components/SubmitForm.vue'
import { ref } from 'vue'

const activeTab = ref<'single' | 'batch'>('single')
const submissionId = ref<number | null>(null)

function handleSubmitted(id: number) {
  submissionId.value = id
}
</script>
