import { createRouter, createWebHistory } from 'vue-router'
import routes from './routes'

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 全局前置守卫
router.beforeEach(async (to, from, next) => {
  const token = localStorage.getItem('token')
  
  // 如果目标路由需要认证但没有token，则跳转到登录页
  if (to.meta.requireAuth && !token) {
    next('/login')
  } else if (token && to.path === '/login') {
    // 如果已有token且访问的是登录页，则重定向到主页
    next('/')
  } else {
    next()
  }
})

// 重置路由
export function resetRouter() {
  // 获取所有路由名称
  const routeNames = router.getRoutes().map(route => route.name)
  
  // 删除所有动态添加的路由，但保留基本的路由
  routeNames.forEach(name => {
    if (name && name !== 'Home' && name !== 'Login' && name !== 'Dashboard') {
      router.removeRoute(name)
    }
  })
  
  // 重置路由加载状态
  window.routesLoaded = false
}

// 添加一个单独访问仪表盘的路由
export function addDashboardRoute() {
  // 检查是否已经添加过该路由
  const existingRoute = router.hasRoute('StandaloneDashboard')
  if (!existingRoute) {
    router.addRoute({
      path: '/standalone-dashboard',
      name: 'StandaloneDashboard',
      component: Dashboard,
      meta: { title: '仪表盘', requireAuth: true }
    })
  }
}

export default router