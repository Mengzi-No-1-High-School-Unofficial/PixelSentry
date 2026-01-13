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
        <SubmitForm @submitted="handleSubmitted" />
        
        <StatusDisplay 
          v-if="submissionId" 
          :submission-id="submissionId" 
          class="mt-8"
        />
      </div>

      <div class="text-center mt-12">
        <router-link to="/admin/login" class="btn btn-ghost btn-sm">
          管理员登录
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import SubmitForm from '@/components/SubmitForm.vue'
import StatusDisplay from '@/components/StatusDisplay.vue'

const submissionId = ref<number | null>(null)

function handleSubmitted(id: number) {
  submissionId.value = id
}
</script>
