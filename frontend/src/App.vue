<template>
  <div class="app">
    <!-- 路由视图 -->
    <router-view v-slot="{ Component }">
      <transition name="fade" mode="out-in">
        <component :is="Component" />
      </transition>
    </router-view>
  </div>
</template>

<script>
import { watch, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'

export default {
  name: 'App',
  setup() {
    const router = useRouter()
    const route = useRoute()
    
    // 监听路由变化，确保在需要时加载用户信息
    watch(() => route.path, async (newPath) => {
      const token = localStorage.getItem('token')
      if (token && newPath !== '/login') {
        // 延迟导入 userStore 以避免循环依赖
        const { useUserStore } = await import('@/store/modules/user')
        const userStore = useUserStore()
        // 添加一个检查，避免重复加载
        if (userStore.token && !window.routesLoaded) {
          try {
            // 只在必要时加载路由，避免重复加载
            await userStore.generateRoutes()
            window.routesLoaded = true
          } catch (error) {
            console.error('路由变化时加载用户信息失败:', error)
          }
        }
      }
    })
    
    // 页面加载时检查路由是否已加载
    onMounted(() => {
      console.log('App.vue mounted, routesLoaded:', window.routesLoaded)
      
      // 添加一个定时器定期检查路由加载状态
      const interval = setInterval(() => {
        if (window.routesLoaded) {
          console.log('检测到路由已加载')
          clearInterval(interval)
          // 触发窗口大小改变事件，促使组件重新渲染
          window.dispatchEvent(new Event('resize'))
        }
      }, 200)
      
      // 5秒后停止检查
      setTimeout(() => {
        clearInterval(interval)
      }, 5000)
    })
    
    return {}
  }
}
</script>

<style>
/* 全局样式 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  font-size: 14px;
  line-height: 1.5;
  color: #333;
  background-color: #f5f7fa;
}

#app {
  height: 100vh;
  width: 100vw;
  overflow: hidden;
}

/* 过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 滚动条样式 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
}

::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #555;
}

/* 增大筛选框尺寸 */
.el-select,
.el-input {
  min-width: 150px;
}

/* 特殊处理用户管理角色筛选框 */
.system-users-role-select .el-select {
  min-width: 150px;
}

/* 特殊处理班级列表班级类型筛选框 */
.classes-class-type-select .el-select {
  min-width: 150px;
}

/* 特殊处理教师管理职位筛选框 */
.teachers-position-select .el-select {
  min-width: 150px;
}

/* 特殊处理幼儿列表班级筛选框 */
.children-class-select .el-select {
  min-width: 150px;
}

/* 特殊处理选区列表所属班级筛选框 */
.selections-class-select .el-select {
  min-width: 150px;
}

/* 特殊处理选区记录选区筛选框 */
.records-selection-area-select .el-select {
  min-width: 150px;
}

/* 特殊处理选区统计统计类型筛选框 */
.selection-statistics-type-select .el-select {
  min-width: 150px;
}

/* 特殊处理统计报表是否公开筛选框 */
.reports-public-select .el-select {
  min-width: 150px;
}
</style>