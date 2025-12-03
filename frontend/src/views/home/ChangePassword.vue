<template>
  <el-dialog
    v-model="visible"
    title="修改密码"
    width="500px"
    @close="handleClose"
  >
    <el-form
      ref="formRef"
      :model="formData"
      :rules="formRules"
      label-width="100px"
    >
      <el-form-item label="新密码" prop="newPassword">
        <el-input
          v-model="formData.newPassword"
          type="password"
          placeholder="请输入新密码"
          show-password
        />
      </el-form-item>
      
      <el-form-item label="确认密码" prop="confirmPassword">
        <el-input
          v-model="formData.confirmPassword"
          type="password"
          placeholder="请再次输入新密码"
          show-password
        />
      </el-form-item>
    </el-form>
    
    <template #footer>
      <el-button @click="close">取消</el-button>
      <el-button type="primary" @click="submit" :loading="loading">确定</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/store/modules/user'
import { changeCurrentUserPassword } from '@/api/auth'

// 定义属性
const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  }
})

// 定义事件
const emits = defineEmits(['update:modelValue', 'success'])

// 响应式数据
const visible = ref(false)
const loading = ref(false)
const formRef = ref()
const userStore = useUserStore()

// 表单数据
const formData = reactive({
  newPassword: '',
  confirmPassword: ''
})

// 表单验证规则
const formRules = {
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== formData.newPassword) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

// 监听modelValue变化
watch(
  () => props.modelValue,
  (val) => {
    visible.value = val
  }
)

// 关闭对话框
function handleClose() {
  emits('update:modelValue', false)
  // 重置表单
  formRef.value?.resetFields()
  formData.newPassword = ''
  formData.confirmPassword = ''
}

// 关闭方法
function close() {
  handleClose()
}

// 提交表单
async function submit() {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    
    loading.value = true
    
    // 准备提交数据
    const data = {
      new_password: formData.newPassword
    }
    
    // 调用修改密码接口
    const res = await changeCurrentUserPassword(data)
    
    if (res.code === 200) {
      ElMessage.success('密码修改成功，请重新登录')
      handleClose()
      emits('success')
    } else {
      ElMessage.error(res.msg || '密码修改失败')
    }
  } catch (error) {
    ElMessage.error('密码修改失败')
    console.error('密码修改失败:', error)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* 可以在这里添加样式 */
</style>