<template>
  <div class="login-container">
    <div class="login-wrapper">
      <div class="login-header">
        <h2>幼儿园管理系统</h2>
        <p class="subtitle">Welcome to Kindergarten Management System</p>
      </div>
      
      <!-- 登录表单 -->
      <transition name="form-fade" mode="out-in">
        <el-form 
          v-if="!showChangePassword"
          ref="loginFormRef"
          :model="form" 
          :rules="rules" 
          class="login-form"
          @keyup.enter="handleLogin"
          key="login-form"
        >
          <el-form-item prop="username">
            <el-input 
              v-model="form.username" 
              type="text" 
              placeholder="请输入用户名"
              clearable
            />
          </el-form-item>
          
          <el-form-item prop="password">
            <el-input 
              v-model="form.password" 
              type="password" 
              placeholder="请输入密码"
              show-password
            />
          </el-form-item>
          
          <el-form-item prop="captcha" class="captcha-item">
            <el-input
              v-model="form.captcha"
              type="text"
              placeholder="请输入验证码"
              clearable
            />
            <div class="captcha-image" @click="refreshCaptcha">
              <img v-if="captchaUrl" :src="captchaUrl" alt="验证码" />
              <div v-else class="captcha-loading">加载中...</div>
            </div>
          </el-form-item>
          
          <el-form-item>
            <el-checkbox v-model="form.remember">记住密码</el-checkbox>
          </el-form-item>
          
          <el-form-item>
            <el-button 
              type="primary" 
              class="login-btn"
              :loading="loading"
              @click="handleLogin"
            >
              登录
            </el-button>
          </el-form-item>
          
          <div class="form-footer">
            <el-button type="text" class="forgot-password-link" @click="showChangePasswordForm">
              忘记密码？
            </el-button>
          </div>
        </el-form>
        
        <!-- 修改密码表单 -->
        <el-form 
          v-else
          ref="changePasswordFormRef"
          :model="changePasswordForm" 
          :rules="changePasswordRules" 
          class="login-form"
          @keyup.enter="handleChangePassword"
          key="change-password-form"
        >
          <div class="form-title">
            <h3>修改密码</h3>
            <el-button type="text" class="back-to-login" @click="showLoginForm">
              ← 返回登录
            </el-button>
          </div>
          
          <el-form-item prop="username">
            <el-input 
              v-model="changePasswordForm.username" 
              type="text" 
              placeholder="请输入用户名"
              clearable
            />
          </el-form-item>
          
          <el-form-item prop="newPassword">
            <el-input 
              v-model="changePasswordForm.newPassword" 
              type="password" 
              placeholder="请输入新密码"
              show-password
            />
          </el-form-item>
          
          <el-form-item prop="confirmPassword">
            <el-input 
              v-model="changePasswordForm.confirmPassword" 
              type="password" 
              placeholder="请确认新密码"
              show-password
            />
          </el-form-item>
          
          <el-form-item prop="captcha" class="captcha-item">
            <el-input
              v-model="changePasswordForm.captcha"
              type="text"
              placeholder="请输入验证码"
              clearable
            />
            <div class="captcha-image" @click="refreshCaptcha">
              <img v-if="captchaUrl" :src="captchaUrl" alt="验证码" />
              <div v-else class="captcha-loading">加载中...</div>
            </div>
          </el-form-item>
          
          <el-form-item>
            <el-button 
              type="primary" 
              class="login-btn"
              :loading="loading"
              @click="handleChangePassword"
            >
              修改密码
            </el-button>
          </el-form-item>
        </el-form>
      </transition>
    </div>
  </div>
</template>

<script>
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/store/modules/user'
import { getCaptcha, changePassword } from '@/api/auth'

export default {
  name: 'Login',
  data() {
    // 确认密码验证规则
    const validateConfirmPassword = (rule, value, callback) => {
      if (value !== this.changePasswordForm.newPassword) {
        callback(new Error('两次输入的密码不一致'))
      } else {
        callback()
      }
    }
    
    return {
      showChangePassword: false, // 是否显示修改密码表单
      form: {
        username: '',
        password: '',
        captcha: '',
        captchaKey: '',
        remember: false
      },
      changePasswordForm: {
        username: '',
        newPassword: '',
        confirmPassword: '',
        captcha: '',
        captchaKey: ''
      },
      rules: {
        username: [
          { required: true, message: '请输入用户名', trigger: 'blur' }
        ],
        password: [
          { required: true, message: '请输入密码', trigger: 'blur' }
        ],
        captcha: [
          { required: true, message: '请输入验证码', trigger: 'blur' }
        ]
      },
      changePasswordRules: {
        username: [
          { required: true, message: '请输入用户名', trigger: 'blur' }
        ],
        newPassword: [
          { required: true, message: '请输入新密码', trigger: 'blur' },
          { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
        ],
        confirmPassword: [
          { required: true, message: '请确认新密码', trigger: 'blur' },
          { validator: validateConfirmPassword, trigger: 'blur' }
        ],
        captcha: [
          { required: true, message: '请输入验证码', trigger: 'blur' }
        ]
      },
      captchaUrl: '',
      loading: false
    }
  },
  mounted() {
    // 页面加载时获取验证码
    this.refreshCaptcha()
    
    // 尝试从localStorage恢复记住的用户名和密码
    const savedUsername = localStorage.getItem('savedUsername')
    const savedPassword = localStorage.getItem('savedPassword')
    if (savedUsername && savedPassword) {
      this.form.username = savedUsername
      this.form.password = savedPassword
      this.form.remember = true
    }
  },
  methods: {
    // 获取验证码
    async refreshCaptcha() {
      try {
        const res = await getCaptcha()
        // 检查业务状态码
        if (res.code !== 200) {
          throw new Error(res.msg || '获取验证码失败')
        }
        
        // 使用统一的数据格式
        this.form.captchaKey = res.data.key
        this.changePasswordForm.captchaKey = res.data.key
        this.captchaUrl = res.data.image
      } catch (error) {
        ElMessage.error('获取验证码失败')
        console.error('获取验证码失败:', error)
      }
    },
    
    // 显示修改密码表单
    showChangePasswordForm() {
      this.showChangePassword = true
      this.changePasswordForm.username = this.form.username
      this.refreshCaptcha()
    },
    
    // 显示登录表单
    showLoginForm() {
      this.showChangePassword = false
      this.refreshCaptcha()
    },
    
    handleLogin() {
      this.$refs.loginFormRef.validate(async (valid) => {
        if (valid) {
          try {
            // 设置加载状态
            this.loading = true
            
            // 获取用户存储实例
            const userStore = useUserStore()
            
            // 准备登录数据
            const loginData = {
              username: this.form.username,
              password: this.form.password,
              captcha: this.form.captcha,
              captchaKey: this.form.captchaKey
            }
            
            // 调用登录接口
            await userStore.login(loginData)
            
            // 获取用户信息并生成路由
            await userStore.getUserInfo()
            
            // 处理记住密码
            if (this.form.remember) {
              localStorage.setItem('savedUsername', this.form.username)
              localStorage.setItem('savedPassword', this.form.password)
            } else {
              localStorage.removeItem('savedUsername')
              localStorage.removeItem('savedPassword')
            }
            
            ElMessage.success('登录成功')
            
            // 跳转到首页
            this.$router.push('/')
            
          } catch (error) {
            // 登录失败，刷新验证码
            this.refreshCaptcha()
            console.error('登录失败:', error)
            // 不再显示额外的错误信息，让request.js统一处理
          } finally {
            // 重置加载状态
            this.loading = false
          }
        } else {
          console.log('表单验证失败')
          return false
        }
      })
    },
    
    // 修改密码
    handleChangePassword() {
      this.$refs.changePasswordFormRef.validate(async (valid) => {
        if (valid) {
          try {
            // 设置加载状态
            this.loading = true
            
            // 准备修改密码数据
            const changePasswordData = {
              username: this.changePasswordForm.username,
              new_password: this.changePasswordForm.newPassword,
              captcha: this.changePasswordForm.captcha,
              captcha_key: this.changePasswordForm.captchaKey
            }
            
            // 调用修改密码接口
            const res = await changePassword(changePasswordData)
            
            if (res.code === 200) {
              ElMessage.success('密码修改成功，请使用新密码登录')
              // 清空表单
              this.changePasswordForm = {
                username: '',
                newPassword: '',
                confirmPassword: '',
                captcha: '',
                captchaKey: ''
              }
              // 切换回登录表单
              this.showLoginForm()
            } else {
              ElMessage.error(res.msg || '密码修改失败')
            }
          } catch (error) {
            ElMessage.error('密码修改失败')
            console.error('密码修改失败:', error)
          } finally {
            // 重置加载状态
            this.loading = false
            // 刷新验证码
            this.refreshCaptcha()
          }
        } else {
          console.log('表单验证失败')
          return false
        }
      })
    }
  }
}
</script>

<style scoped>
.login-container {
  height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
}

.login-wrapper {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  padding: 40px;
  width: 100%;
  max-width: 420px;
  position: relative;
  overflow: hidden;
}

.login-wrapper::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #667eea, #764ba2);
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.login-header h2 {
  margin: 0;
  color: #303133;
  font-size: 24px;
}

.subtitle {
  color: #909399;
  font-size: 14px;
  margin: 0;
}

.login-form {
  width: 100%;
}

.form-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.form-title h3 {
  margin: 0;
  color: #303133;
  font-size: 20px;
}

.back-to-login {
  font-size: 14px;
  color: #1890ff;
  padding: 0;
}

.back-to-login:hover {
  color: #40a9ff;
}

.captcha-item {
  display: flex;
  gap: 10px;
}

.captcha-image {
  width: 100px;
  height: 40px;
  cursor: pointer;
  border-radius: 4px;
  overflow: hidden;
  border: 1px solid #dcdfe6;
  display: flex;
  align-items: center;
  justify-content: center;
}

.captcha-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.captcha-loading {
  font-size: 12px;
  color: #999;
}

.form-footer {
  text-align: center;
  margin-top: 10px;
}

.forgot-password-link {
  font-size: 14px;
  color: #1890ff;
  padding: 0;
}

.forgot-password-link:hover {
  color: #40a9ff;
}

.login-btn {
  width: 100%;
  padding: 12px 0;
  font-size: 16px;
}

/* 表单切换动画 */
.form-fade-enter-active,
.form-fade-leave-active {
  transition: all 0.3s ease;
}

.form-fade-enter-from {
  opacity: 0;
  transform: translateX(30px);
}

.form-fade-leave-to {
  opacity: 0;
  transform: translateX(-30px);
}

/* 响应式设计 */
@media (max-width: 480px) {
  .login-wrapper {
    padding: 30px 20px;
  }
  
  .login-header h2 {
    font-size: 20px;
  }
}
</style>