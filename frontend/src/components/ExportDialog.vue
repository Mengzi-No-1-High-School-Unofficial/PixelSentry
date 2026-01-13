<template>
    <dialog id="export_modal" class="modal" :class="{ 'modal-open': modelValue }">
        <div class="modal-box w-11/12 max-w-4xl">
            <h3 class="font-bold text-lg mb-4">导出 LGS-Paintboard-Helper 兼容的配置文件</h3>

            <!-- 步骤条 -->
            <ul class="steps w-full mb-8">
                <li class="step" :class="{ 'step-primary': step >= 1 }">配置与选择</li>
                <li class="step" :class="{ 'step-primary': step >= 2 }">预览</li>
                <li class="step" :class="{ 'step-primary': step >= 3 }">下载</li>
            </ul>

            <!-- 内容区 -->
            <div class="min-h-[300px]">
                <!-- 步骤 1: 配置 -->
                <div v-if="step === 1">
                    <div class="form-control w-full max-w-xs mb-4">
                        <label class="label">
                            <span class="label-text">CD 时间 (ms)</span>
                        </label>
                        <input type="number" v-model="config.cd_time_ms" class="input input-bordered w-full max-w-xs" />
                    </div>

                    <div class="overflow-x-auto max-h-60">
                        <table class="table table-sm table-pin-rows">
                            <thead>
                                <tr>
                                    <th>
                                        <input type="checkbox" class="checkbox checkbox-sm" :checked="allSelected"
                                            @change="toggleSelectAll" />
                                    </th>
                                    <th>ID</th>
                                    <th>UID</th>
                                    <th>AccessKey</th>
                                    <th>提交人</th>
                                    <th>状态</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="key in keys" :key="key.id">
                                    <td>
                                        <input type="checkbox" class="checkbox checkbox-sm" v-model="selectedKeyIds"
                                            :value="key.id" />
                                    </td>
                                    <td>{{ key.id }}</td>
                                    <td>{{ key.uid }}</td>
                                    <td>{{ key.accessKey.substring(0, 8) }}...</td>
                                    <td>{{ key.submitterName || '-' }}</td>
                                    <td>
                                        <div class="badge badge-sm"
                                            :class="key.isValid ? 'badge-success' : 'badge-ghost'">
                                            {{ key.isValid ? '有效' : '无效' }}
                                        </div>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>

                <!-- 步骤 2: 预览 -->
                <div v-if="step === 2">
                    <div class="bg-base-300 p-4 rounded-lg overflow-auto max-h-[400px]">
                        <pre class="text-xs"><code>{{ jsonPreview }}</code></pre>
                    </div>
                </div>

                <!-- 步骤 3: 完成 -->
                <div v-if="step === 3" class="flex flex-col items-center justify-center py-12">
                    <div class="text-success mb-4 text-5xl">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16" fill="none" viewBox="0 0 24 24"
                            stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                    </div>
                    <p class="text-xl font-semibold">配置已准备就绪</p>
                    <p class="text-base-content/60 mt-2">点击下方按钮下载您的配置文件。</p>
                </div>
            </div>

            <!-- 操作区 -->
            <div class="modal-action">
                <button v-if="step > 1 && step < 3" @click="step--" class="btn btn-ghost">上一步</button>
                <button @click="close" class="btn btn-ghost">取消</button>
                <button v-if="step === 1" @click="step++" class="btn btn-primary"
                    :disabled="selectedKeyIds.length === 0">下一步：预览</button>
                <button v-if="step === 2" @click="handleExport" class="btn btn-primary">下一步：下载</button>
                <button v-if="step === 3" @click="downloadFile" class="btn btn-success">再次下载</button>
            </div>
        </div>
    </dialog>
</template>

<script setup lang="ts">
import type { AccessKeyInfo } from '@/types';
import { computed, ref, watch } from 'vue';

const props = defineProps<{
    modelValue: boolean
    keys: AccessKeyInfo[]
}>()

const emit = defineEmits(['update:modelValue'])

const step = ref(1)
const config = ref({
    cd_time_ms: 50
})
const selectedKeyIds = ref<number[]>([])

// 默认选中所有有效 Key
watch(() => props.modelValue, (val) => {
    if (val) {
        step.value = 1
        selectedKeyIds.value = props.keys
            .filter(k => k.isValid)
            .map(k => k.id)
    }
})

const allSelected = computed(() => {
    return props.keys.length > 0 && selectedKeyIds.value.length === props.keys.length
})

function toggleSelectAll() {
    if (allSelected.value) {
        selectedKeyIds.value = []
    } else {
        selectedKeyIds.value = props.keys.map(k => k.id)
    }
}

const jsonPreview = computed(() => {
    const selectedKeys = props.keys.filter(k => selectedKeyIds.value.includes(k.id))
    const data = {
        cd_time_ms: config.value.cd_time_ms,
        tokens: selectedKeys.map(k => ({
            uid: parseInt(k.uid),
            access_key: k.accessKey
        }))
    }
    return JSON.stringify(data, null, 2)
})

function close() {
    emit('update:modelValue', false)
}

function handleExport() {
    step.value = 3
    downloadFile()
}

function downloadFile() {
    const blob = new Blob([jsonPreview.value], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'config.json'
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
}
</script>
