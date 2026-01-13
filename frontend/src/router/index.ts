import { useAuthStore } from '@/stores/auth'
import AdminDashboard from '@/views/AdminDashboard.vue'
import AdminLogin from '@/views/AdminLogin.vue'
import Home from '@/views/Home.vue'
import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
    history: createWebHistory(),
    routes: [
        {
            path: '/',
            name: 'home',
            component: Home,
        },
        {
            path: '/admin/login',
            name: 'admin-login',
            component: AdminLogin,
        },
        {
            path: '/admin/dashboard',
            name: 'admin-dashboard',
            component: AdminDashboard,
            meta: { requiresAuth: true },
        },
    ],
})

// 路由守卫
router.beforeEach((to, from, next) => {
    const authStore = useAuthStore()

    if (to.meta.requiresAuth && !authStore.isAuthenticated) {
        // 需要认证但未登录，跳转到登录页
        next({ name: 'admin-login' })
    } else if (to.name === 'admin-login' && authStore.isAuthenticated) {
        // 已登录但访问登录页，跳转到仪表板
        next({ name: 'admin-dashboard' })
    } else {
        next()
    }
})

export default router
