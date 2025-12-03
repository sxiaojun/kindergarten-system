<template>
  <div class="layout-container">
    <!-- 顶部导航 -->
    <header class="header">
      <div class="header-left">
        <div class="logo">
          <el-icon><School /></el-icon>
          <span>幼儿园管理系统</span>
        </div>
      </div>
      <div class="header-right">
        <el-dropdown>
          <span class="user-info">
            <el-avatar :size="32" :src="userAvatar || defaultAvatar">
              {{ userInitial }}
            </el-avatar>
            <span>{{ userNickname }}</span>
            <el-icon class="el-icon--right"><ArrowDown /></el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="handleProfile">
                <el-icon><User /></el-icon>
                <span>个人中心</span>
              </el-dropdown-item>
              <el-dropdown-item @click="handleChangePassword">
                <el-icon><Lock /></el-icon>
                <span>修改密码</span>
              </el-dropdown-item>
              <el-dropdown-item divided @click="handleLogout">
                <el-icon><SwitchButton /></el-icon>
                <span>退出登录</span>
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </header>
    
    <!-- 主体内容 -->
    <div class="main">
      <!-- 左侧菜单 -->
      <aside class="sidebar">
        <el-scrollbar height="100%">
          <el-menu
            :default-active="activeMenu"
            class="el-menu-vertical"
            router
            @select="handleMenuSelect"
          >
            <template v-for="route in sidebarRoutes" :key="route.path">
              <el-sub-menu
                v-if="route.children && route.children.length > 0"
                :index="route.path"
              >
                <template #title>
                  <el-icon>
                    <component :is="route.meta.icon || 'Menu'" />
                  </el-icon>
                  <span>{{ route.meta.title }}</span>
                </template>
                <template v-for="child in route.children" :key="child.path">
                  <el-menu-item
                    :index="resolvePath(route.path, child.path)"
                  >
                    <el-icon>
                      <component :is="child.meta.icon || 'Menu'" />
                    </el-icon>
                    <span>{{ child.meta.title }}</span>
                  </el-menu-item>
                </template>
              </el-sub-menu>
              <el-menu-item v-else :index="route.path">
                <el-icon>
                  <component :is="route.meta.icon || 'Menu'" />
                </el-icon>
                <span>{{ route.meta.title }}</span>
              </el-menu-item>
            </template>
          </el-menu>
        </el-scrollbar>
      </aside>
      
      <!-- 右侧内容区 -->
      <main class="content">
        <el-breadcrumb separator="/" class="breadcrumb">
          <el-breadcrumb-item
            v-for="(item, index) in breadcrumbList"
            :key="index"
            :to="item.path"
          >
            {{ item.title }}
          </el-breadcrumb-item>
        </el-breadcrumb>
        <div class="content-wrapper">
          <router-view />
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/store/modules/user'
import { ArrowDown, Menu, User, Lock, SwitchButton, School } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

// 路由和状态管理
const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

// 默认头像
const defaultAvatar = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAiIGhlaWdodD0iMjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIgdmlld0JveD0iMCAwIDIwIDIwIj48Y2lyY2xlIGN4PSIxMCUiIGN5PSIxMCUiIHI9IjcuNSUiIGZpbGw9IiNlY2ZmMDYiLz48cGF0aCBkPSJNMTAgMTIuNSUiIGZpbGw9IiNmZmVmZjAiIGZpbGwtb3BhY2l0eT0iMC4yIi8+PC9zdmc+'

// 计算属性
const userAvatar = computed(() => userStore.userInfo.avatar)
const userNickname = computed(() => userStore.userInfo.nickname || userStore.userInfo.username || '用户')
const userInitial = computed(() => {
  const name = userNickname.value
  return name ? name.charAt(0).toUpperCase() : 'U'
})

// 路径解析函数
function resolvePath(basePath, relativePath) {
  // 如果relativePath是绝对路径，直接返回
  if (relativePath.startsWith('/')) {
    return relativePath
  }
  // 否则拼接路径
  if (basePath.endsWith('/')) {
    return basePath + relativePath
  }
  return basePath + '/' + relativePath
}

// 侧边栏路由
const sidebarRoutes = computed(() => {
  // 获取所有路由并过滤掉不需要显示在菜单中的路由
  const allRoutes = router.getRoutes()
  console.log('Layout - 所有路由:', allRoutes)
  
  // 查找Home路由
  const homeRoute = allRoutes.find(route => route.name === 'Home')
  console.log('Layout - Home路由:', homeRoute)
  
  // 获取Home路由的子路由作为主要的侧边栏路由
  let routes = []
  if (homeRoute && homeRoute.children) {
    routes = homeRoute.children.filter(child => 
      child.meta && child.meta.title
    )
    console.log('Layout - Home子路由:', routes)
  }
  
  console.log('Layout - 最终侧边栏路由:', routes)
  return routes
})

// 当前激活的菜单
const activeMenu = computed(() => {
  const path = route.path
  const menu = sidebarRoutes.value.find(item => {
    if (item.path === path) return true
    return item.children && item.children.some(child => child.path === path)
  })
  return menu ? menu.path : ''
})

// 面包屑列表
const breadcrumbList = ref([])

// 监听路由变化
watch(() => route.path, () => {
  generateBreadcrumb()
}, { immediate: true })

// 生成面包屑
function generateBreadcrumb() {
  const matched = route.matched
  const breadcrumbs = []
  
  matched.forEach(item => {
    if (item.meta && item.meta.title) {
      breadcrumbs.push({
        title: item.meta.title,
        path: item.path
      })
    }
  })
  
  breadcrumbList.value = breadcrumbs
}

// 菜单选择处理
function handleMenuSelect(key, keyPath) {
  console.log('菜单选择:', key, keyPath)
}

// 个人中心
function handleProfile() {
  router.push('/profile')
}

// 修改密码
function handleChangePassword() {
  router.push('/change-password')
}

// 退出登录
async function handleLogout() {
  try {
    await userStore.logout()
  } catch (error) {
    ElMessage.error('退出失败')
  }
}

onMounted(() => {
  // 初始化时生成面包屑
  generateBreadcrumb()
})
</script>

<style scoped>
.layout-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f5f7fa;
}

/* 顶部导航 */
.header {
  height: 60px;
  background-color: #fff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  z-index: 100;
}

.header-left {
  display: flex;
  align-items: center;
}

.logo {
  display: flex;
  align-items: center;
  font-size: 18px;
  font-weight: 600;
  color: #1890ff;
}

.logo .el-icon {
  font-size: 24px;
  margin-right: 8px;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.user-info:hover {
  background-color: #f0f0f0;
}

.user-info .el-avatar {
  margin-right: 8px;
}

.user-info .el-icon--right {
  margin-left: 8px;
}

/* 主体内容 */
.main {
  flex: 1;
  display: flex;
  overflow: hidden;
}

/* 左侧菜单 */
.sidebar {
  width: 240px;
  background-color: #fff;
  border-right: 1px solid #e8e8e8;
  overflow-y: auto;
}

.el-menu-vertical {
  border-right: none;
}

/* 右侧内容区 */
.content {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.breadcrumb {
  margin-bottom: 20px;
}

.content-wrapper {
  background-color: #fff;
  padding: 24px;
  border-radius: 8px;
  min-height: calc(100vh - 140px);
}
</style>