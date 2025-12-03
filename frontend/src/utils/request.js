import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/store/modules/user'

// 创建axios实例
const service = axios.create({
  baseURL: '/api', // api的base_url
  timeout: 15000 // 请求超时时间
})

// 请求拦截器
service.interceptors.request.use(
  config => {
    // 获取token
    const userStore = useUserStore()
    const token = userStore.token
    
    // 如果token存在，添加到请求头
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    
    return config
  },
  error => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
service.interceptors.response.use(
  response => {
    const { data } = response
    
    // 如果后端返回的是二进制数据，直接返回
    if (response.config.responseType === 'blob' || response.config.responseType === 'arraybuffer') {
      return data
    }
    
    // 对于验证码这类特殊接口，直接返回响应数据
    if (response.config.url && response.config.url.includes('/auth/inter_captcha/')) {
      return response.data
    }
    
    // 对于登录接口，直接返回响应数据
    if (response.config.url && response.config.url.includes('/auth/login/')) {
      return data
    }
    
    // 对于统计接口，直接返回响应数据
    if (response.config.url && response.config.url.includes('/stats/')) {
      return data
    }
    
    // 判断业务状态码（仅对有code字段的响应进行处理）
    if (data && typeof data === 'object' && 'code' in data) {
      if (data.code !== 200) {
        // 错误提示
        ElMessage.error(data.msg || '请求失败')
        
        // 处理特殊错误码
        if (data.code === 401) {
          // 未授权，清除登录状态并跳转到登录页
          const userStore = useUserStore()
          userStore.clearUserInfo()
          
          // 跳转到登录页
          window.location.href = '/login'
        }
        
        return Promise.reject(new Error(data.msg || '请求失败'))
      }
      
      return data
    }
    
    // 特殊处理207状态码（多状态响应），这种情况通常用于导入等批量操作
    if (response.status === 207) {
      return data
    }
    
    // 对于没有code字段的响应（如统计接口），直接返回数据
    return data
  },
  error => {
    console.error('响应错误:', error)
    
    // 处理网络错误 - 只显示友好的中文提示
    if (!error.response) {
      ElMessage.error('网络连接失败，请检查网络设置')
      return Promise.reject(new Error('网络连接失败'))
    }
    
    const { status, data } = error.response
    
    // 特殊处理400状态码，如果包含errors字段，则不显示默认错误消息
    if (status === 400 && data && data.errors) {
      // 让调用方处理errors
      return Promise.reject(error)
    }
    
    // 优先使用后端返回的错误信息
    if (data && typeof data === 'object' && data.msg) {
      ElMessage.error(data.msg)
      return Promise.reject(new Error(data.msg))
    }
    
    // 根据状态码显示友好提示
    let message = '请求失败'
    switch (status) {
      case 400:
        message = '请求参数错误'
        break
      case 401:
        message = '未授权，请重新登录'
        // 未授权，清除登录状态并跳转到登录页
        const userStore = useUserStore()
        userStore.clearUserInfo()
        window.location.href = '/login'
        break
      case 403:
        message = '拒绝访问，权限不足'
        break
      case 404:
        message = '请求的资源不存在'
        break
      case 408:
        message = '请求超时，请稍后重试'
        break
      case 500:
        message = '服务器内部错误，请联系管理员'
        break
      case 501:
        message = '服务未实现'
        break
      case 502:
        message = '网关错误'
        break
      case 503:
        message = '服务不可用'
        break
      case 504:
        message = '网关超时'
        break
      default:
        message = `请求失败(${status})`
    }
    
    ElMessage.error(message)
    return Promise.reject(new Error(message))
  }
)

export default service