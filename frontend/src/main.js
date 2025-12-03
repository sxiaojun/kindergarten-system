import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

// 创建应用实例
const app = createApp(App)

// 注册Element Plus Icons
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// 使用插件
app.use(createPinia())
app.use(router)
app.use(ElementPlus)

// 全局属性
app.config.globalProperties.window = window

// 路由准备就绪后挂载应用
router.isReady().then(async () => {
  // 如果已经有token，尝试加载用户信息
  const token = localStorage.getItem('token')
  if (token) {
    // 延迟导入 userStore 以避免循环依赖
    const { useUserStore } = await import('@/store/modules/user')
    const userStore = useUserStore()
    if (userStore.token && !window.routesLoaded) {
      try {
        await userStore.getUserInfo()
        window.routesLoaded = true
      } catch (error) {
        console.error('初始化用户信息失败:', error)
        // 如果初始化失败，清除token
        localStorage.removeItem('token')
      }
    }
  }
  
  console.log('准备挂载应用，routesLoaded:', window.routesLoaded)
  app.mount('#app')
  console.log('应用已挂载')
  
  // 挂载后触发一次全局更新
  setTimeout(() => {
    window.dispatchEvent(new Event('resize'))
  }, 100)
})
