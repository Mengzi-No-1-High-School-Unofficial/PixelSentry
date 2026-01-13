<template>
  <div class="min-h-screen bg-base-200 flex items-center justify-center px-4">
    <div class="card w-full max-w-md bg-base-100 shadow-2xl">
      <div class="card-body">
        <h2 class="card-title text-2xl justify-center mb-4">管理员登录</h2>
        
        <form @submit.prevent="handleLogin">
          <div class="form-control">
            <label class="label">
              <span class="label-text">用户名</span>
            </label>
            <input 
              v-model="username" 
              type="text" 
              placeholder="请输入用户名" 
              class="input input-bordered" 
              required
            />
          </div>
          
          <div class="form-control mt-4">
            <label class="label">
              <span class="label-text">密码</span>
            </label>
            <input 
              v-model="password" 
              type="password" 
              placeholder="请输入密码" 
              class="input input-bordered" 
              required
            />
          </div>

          <div v-if="error" class="alert alert-error mt-4">
            <span>{{ error }}</span>
          </div>
          
          <div class="form-control mt-6">
            <button 
              type="submit" 
              class="btn btn-primary" 
              :class="{ loading: loading }"
              :disabled="loading"
            >
              {{ loading ? '登录中...' : '登录' }}
            </button>
          </div>
        </form>

        <div class="divider">或</div>
        
        <router-link to="/" class="btn btn-ghost btn-sm">
          返回首页
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const username = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

async function handleLogin() {
  loading.value = true
  error.value = ''
  
  try {
    await authStore.login({
      username: username.value,
      password: password.value,
    })
    
    router.push('/admin/dashboard')
  } catch (err: any) {
    error.value = err.message || '登录失败，请检查用户名和密码'
  } finally {
    loading.value = false
  }
}
</script>
