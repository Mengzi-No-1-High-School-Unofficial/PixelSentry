<template>
    <div class="min-h-screen bg-base-200 py-12 px-4">
        <div class="max-w-3xl mx-auto">
            <div
                class="card bg-base-100 shadow-2xl overflow-hidden animate-fade-in text-white backdrop-blur-md bg-opacity-80">
                <div class="card-body p-8 sm:p-12">
                    <div class="flex items-center gap-4 mb-8">
                        <div class="p-3 bg-primary rounded-2xl shadow-lg shadow-primary/20">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-primary-content" fill="none"
                                viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                    d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                        </div>
                        <h1 class="text-4xl font-black tracking-tight text-white drop-shadow-md">使用帮助</h1>
                    </div>

                    <div class="space-y-10">
                        <!-- 使用指南 -->
                        <section class="relative group">
                            <div
                                class="absolute -left-6 top-0 bottom-0 w-1 bg-primary rounded-full transform scale-y-0 group-hover:scale-y-100 transition-transform duration-300">
                            </div>
                            <h2 class="text-2xl font-bold mb-4 flex items-center gap-2">
                                <span class="text-primary font-mono">01.</span> 如何使用
                            </h2>
                            <div class="space-y-4 text-base-content/80 leading-relaxed">
                                <p>本程序用于快速、批量地将洛谷 Token 转换为 Access Key。请按照以下步骤操作：</p>
                                <ol class="list-decimal list-inside space-y-4 ml-2">
                                    <li class="pl-2">
                                        <span class="font-semibold text-white">获取 Token 指信：</span>
                                        在新版洛谷中，访问 <a href="https://www.luogu.com.cn/paste" target="_blank"
                                            class="link link-primary">洛谷剪贴板</a>，创建一个包含指定验证信息的剪贴板。
                                    </li>
                                    <li class="pl-2">
                                        <span class="font-semibold text-white">复制链接：</span>
                                        保存剪贴板后，复制该剪贴板的 ID（例如链接为 <code>luogu.com.cn/paste/abc12345</code>，ID 即为
                                        <code>abc12345</code>）。
                                    </li>
                                    <li class="pl-2">
                                        <span class="font-semibold text-white">进行提交：</span>
                                        在首页输入框中填入剪贴板 ID 和您的称呼，点击提交。系统将自动登录并生成 Access Key。
                                    </li>
                                    <li class="pl-2">
                                        <span class="font-semibold text-white">批量处理：</span>
                                        您也可以使用“批量提交”功能，一次性输入多个剪贴板 ID（每行一个）。
                                    </li>
                                </ol>
                            </div>
                        </section>

                        <!-- 开发者信息 -->
                        <section class="relative group">
                            <div
                                class="absolute -left-6 top-0 bottom-0 w-1 bg-secondary rounded-full transform scale-y-0 group-hover:scale-y-100 transition-transform duration-300">
                            </div>
                            <h2 class="text-2xl font-bold mb-4 flex items-center gap-2">
                                <span class="text-secondary font-mono">02.</span> 开发信息
                            </h2>
                            <div
                                class="bg-base-200/50 rounded-2xl p-6 border border-white/5 hover:border-secondary/30 transition-colors">
                                <p class="mb-4">PixelSentry 由 <span class="text-secondary font-bold">Xyber Nova</span>
                                    设计并开发。</p>
                                <div class="flex flex-wrap gap-4">
                                    <a href="mailto:xyber-nova@outlook.com"
                                        class="btn btn-sm btn-outline btn-secondary no-animation group">
                                        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none"
                                            viewBox="0 0 24 24" stroke="currentColor">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                                d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                                        </svg>
                                        xyber-nova@outlook.com
                                    </a>
                                </div>
                            </div>
                        </section>
                    </div>

                    <div class="divider opacity-20 my-10"></div>

                    <div class="card-actions justify-center">
                        <button @click="router.push('/')"
                            class="btn btn-primary btn-wide shadow-xl shadow-primary/20 hover:scale-105 transition-transform group">
                            <svg xmlns="http://www.w3.org/2000/svg"
                                class="h-5 w-5 mr-1 group-hover:-translate-x-1 transition-transform" fill="none"
                                viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                    d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                            </svg>
                            返回首页
                        </button>
                    </div>
                </div>
            </div>

            <p class="text-center mt-8 text-base-content/40 text-sm">
                © 2026 PixelSentry / Xyber Nova. All rights reserved.
            </p>
        </div>
    </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';

const router = useRouter()
</script>

<style scoped>
.animate-fade-in {
    animation: fadeIn 0.8s ease-out;
}

@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(20px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
}

:deep(.link-primary) {
    text-decoration: none;
    border-bottom: 2px solid var(--p);
    transition: all 0.2s;
}

:deep(.link-primary:hover) {
    background-color: var(--p);
    color: var(--pc);
}
</style>
