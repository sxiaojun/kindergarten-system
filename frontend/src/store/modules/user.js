import { defineStore } from 'pinia'
import { login, logout, getUserInfo } from '@/api/auth'
import router, { resetRouter } from '@/router'
import { ElMessage } from 'element-plus'

export const useUserStore = defineStore('user', {
  state: () => ({
    // 用户信息
    userInfo: {},
    // 用户角色
    role: '',
    // 权限列表
    permissions: [],
    // 登录时间
    loginTime: 0,
    // token
    token: localStorage.getItem('token') || ''
  }),

  getters: {
    // 是否已登录
    isLoggedIn: (state) => !!state.token,
    // 是否为系统管理员
    isSystemOwner: (state) => state.role === 'owner',
    // 是否为园长
    isKindergartenOwner: (state) => state.role === 'principal',
    // 是否为教师
    isTeacher: (state) => state.role === 'teacher'
  },

  actions: {
    // 登录
    async login(userInfo) {
      try {
        const res = await login(userInfo)
        // 检查业务状态码
        if (res.code !== 200) {
          throw new Error(res.msg || '登录失败')
        }
        
        const { token, user } = res.data
        
        // 保存token到localStorage
        localStorage.setItem('token', token)
        
        // 更新状态
        this.token = token
        this.userInfo = user
        this.role = user.role
        this.loginTime = Date.now()
        
        // 保存权限信息
        this.permissions = user.permissions || []
        
        // 加载用户路由
        await this.generateRoutes()
        
        return res
      } catch (error) {
        console.error('登录失败:', error)
        // 不再在store中显示错误信息，让request.js统一处理
        throw error
      }
    },

    // 获取用户信息
    async getUserInfo() {
      try {
        if (!this.token) return
        
        const res = await getUserInfo()
        // 检查业务状态码
        if (res.code !== 200) {
          throw new Error(res.msg || '获取用户信息失败')
        }
        
        const user = res.data
        
        // 更新用户信息
        this.userInfo = user
        this.role = user.role
        this.permissions = user.permissions || []
        
        console.log('获取到的用户信息:', user)
        
        return user
      } catch (error) {
        // 获取用户信息失败，清除登录状态但不调用logout接口
        this.clearUserInfo()
        throw error
      }
    },

    // 生成路由
    async generateRoutes() {
      // 设置路由已加载标志
      window.routesLoaded = true
      
      // 不再动态添加路由，因为在router/index.js中已经预定义了所有路由
      console.log('路由已预定义，无需动态添加')
    },

    // 登出
    async logout() {
      try {
        // 调用登出接口
        await logout()
        
        // 清除用户信息
        this.clearUserInfo()
        
        // 重置路由加载状态而不是清除路由
        window.routesLoaded = false
        
        // 跳转到登录页
        router.push('/login')
      } catch (error) {
        console.error('登出失败:', error)
        // 即使登出接口调用失败，也要清除本地状态
        this.clearUserInfo()
        window.routesLoaded = false
        router.push('/login')
      }
    },

    // 清除用户信息
    clearUserInfo() {
      this.userInfo = {}
      this.role = ''
      this.permissions = []
      this.loginTime = 0
      this.token = ''
      localStorage.removeItem('token')
    }
  }
})