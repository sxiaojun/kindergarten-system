<template>
  <div class="app-wrapper">
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
    <div class="main-container">
      <!-- 左侧菜单 -->
      <aside class="sidebar">
        <el-scrollbar height="100%">
          <el-menu
            :default-active="activeMenu"
            class="el-menu-vertical"
            router
            :unique-opened="true"
          >
            <!-- 根据用户角色显示不同的菜单 -->
            <template v-for="route in permissionRoutes" :key="route.path">
              <el-sub-menu 
                v-if="route.children && route.children.length > 0" 
                :index="route.path"
              >
                <template #title>
                  <el-icon v-if="route.meta && route.meta.icon">
                    <component :is="route.meta.icon" />
                  </el-icon>
                  <span>{{ route.meta.title }}</span>
                </template>
                <el-menu-item 
                  v-for="child in route.children" 
                  :key="child.path" 
                  :index="resolvePath(route.path, child.path)"
                >
                  <el-icon v-if="child.meta && child.meta.icon">
                    <component :is="child.meta.icon" />
                  </el-icon>
                  <span>{{ child.meta.title }}</span>
                </el-menu-item>
              </el-sub-menu>
              
              <el-menu-item 
                v-else
                :index="route.path"
              >
                <el-icon v-if="route.meta && route.meta.icon">
                  <component :is="route.meta.icon" />
                </el-icon>
                <template #title>
                  <span>{{ route.meta.title }}</span>
                </template>
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
    
    <!-- 修改密码弹窗 -->
    <ChangePassword 
      v-model="showChangePasswordDialog" 
      @success="handlePasswordChangeSuccess"
    />
  </div>
</template>

<script setup>
import { computed, onMounted, watch, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/store/modules/user'
import ChangePassword from './ChangePassword.vue'
import { 
  ArrowDown, 
  User, 
  Lock, 
  SwitchButton, 
  School, 
  Avatar, 
  Grid, 
  MapLocation, 
  Location, 
  Document, 
  Position,
  DataLine,
  OfficeBuilding,
  Setting
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

// 路由和状态管理
const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

// 修改密码弹窗显示状态
const showChangePasswordDialog = ref(false)

// 默认头像
const defaultAvatar = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAiIGhlaWdodD0iMjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIgdmlld0JveD0iMCAwIDIwIDIwIj48Y2lyY2xlIGN4PSIxMCUiIGN5PSIxMCUiIHI9IjcuNSUiIGZpbGw9IiNlY2ZmMDYiLz48cGF0aCBkPSJNMTAgMTIuNSUiIGZpbGw9IiNmZmVmZjAiIGZpbGwtb3BhY2l0eT0iMC4yIi8+PC9zdmc+'

// 计算属性
const userAvatar = computed(() => userStore.userInfo.avatar)
const userNickname = computed(() => userStore.userInfo.nickname || userStore.userInfo.username || '用户')
const userInitial = computed(() => {
  const name = userNickname.value
  return name ? name.charAt(0).toUpperCase() : 'U'
})

// 当前激活的菜单
const activeMenu = computed(() => {
  const path = route.path
  return path
})

// 面包屑列表
const breadcrumbList = ref([])

// 根据用户角色过滤路由
const permissionRoutes = computed(() => {
  // 获取所有路由配置
  const allRoutes = router.options.routes.find(r => r.name === 'Home')?.children || []
  
  // 根据用户角色过滤路由
  if (userStore.isSystemOwner) {
    // 系统管理员可以看到所有核心路由（不含统计报表）
    return allRoutes.filter(route => 
      route.meta?.title !== '统计报表'
    )
  } else if (userStore.isKindergartenOwner) {
    // 园长可以看到部分路由（允许访问系统管理，但只显示用户管理）
    return allRoutes.filter(route => {
      // 过滤掉统计报表
      if (route.meta?.title === '统计报表') {
        return false
      }
      
      // 对于系统管理模块，只保留用户管理
      if (route.path === '/system' && route.children) {
        // 只保留用户管理
        route.children = route.children.filter(child => child.path === 'users')
        // 确保至少有一个子项
        if (route.children.length === 0) {
          return false
        }
        // 重新设置重定向到用户管理
        route.redirect = '/system/users'
      }
      
      return true
    })
  } else if (userStore.isTeacher) {
    // 教师只能看到部分路由
    const allowedPaths = ['/dashboard', '/children', '/selections']
    return allRoutes.filter(route => allowedPaths.includes(route.path))
  }
  return []
})

// 解析完整路径
const resolvePath = (basePath, subPath) => {
  if (subPath.startsWith('/')) {
    return subPath
  }
  if (basePath.endsWith('/')) {
    return basePath + subPath
  }
  return basePath + '/' + subPath
}

// 监听路由变化
watch(() => route.path, () => {
  generateBreadcrumb()
}, { immediate: true })

// 生成面包屑
function generateBreadcrumb() {
  const matched = route.matched.filter(item => item.meta && item.meta.title)
  const breadcrumbs = matched.map(item => ({
    title: item.meta.title,
    path: item.path
  }))
  
  breadcrumbList.value = breadcrumbs
}

// 个人中心
function handleProfile() {
  router.push('/profile')
}

// 修改密码
function handleChangePassword() {
  showChangePasswordDialog.value = true
}

// 密码修改成功处理
function handlePasswordChangeSuccess() {
  // 重新登录
  userStore.logout()
}

// 退出登录
async function handleLogout() {
  try {
    await userStore.logout()
  } catch (error) {
    ElMessage.error('退出失败')
  }
}

// 页面加载时确保路由已加载
onMounted(async () => {
  // 初始化时生成面包屑
  generateBreadcrumb()
  
  // 调试路由信息
  console.log('当前路由信息:', router.currentRoute.value)
  console.log('所有路由:', router.getRoutes())
  console.log('权限路由:', permissionRoutes.value)
})
</script>

<style scoped>
.app-wrapper {
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
.main-container {
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
  min-height: 100%;
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