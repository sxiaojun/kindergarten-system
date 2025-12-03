<template>
  <div class="app-container">
    <!-- 搜索表单 -->
    <el-card class="search-card">
      <el-form :model="searchForm" label-width="80px" inline>
        <el-form-item label="用户名">
          <el-input
            v-model="searchForm.username"
            placeholder="请输入用户名"
            clearable
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="姓名">
          <el-input
            v-model="searchForm.first_name"
            placeholder="请输入姓名"
            clearable
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="角色">
          <el-select
            v-model="searchForm.role"
            placeholder="请选择角色"
            clearable
            @change="handleSearch"
            class="system-users-role-select"
          >
            <el-option label="系统所有者" value="owner" />
            <el-option label="园长" value="principal" />
            <el-option label="教师" value="teacher" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 操作按钮 -->
    <div class="toolbar">
      <el-button v-if="userStore.role === 'owner' || userStore.role === 'principal'" type="primary" @click="handleAdd">新增用户</el-button>
    </div>

    <!-- 用户列表 -->
    <el-card>
      <el-table
        v-loading="loading"
        :data="userList"
        border
        style="width: 100%"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户名" />
        <el-table-column prop="first_name" label="姓名" />
        <el-table-column prop="role" label="角色">
          <template #default="scope">
            <el-tag v-if="scope.row.role === 'owner'" type="danger">系统所有者</el-tag>
            <el-tag v-else-if="scope.row.role === 'principal'" type="warning">园长</el-tag>
            <el-tag v-else-if="scope.row.role === 'teacher'" type="success">教师</el-tag>
            <span v-else>{{ scope.row.role }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="kindergarten_name" label="所属幼儿园" />
        <el-table-column prop="teacher_name" label="关联教师">
          <template #default="scope">
            <span v-if="scope.row.teacher_name">{{ scope.row.teacher_name }}</span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="phone" label="手机号" />
        <el-table-column prop="created_at" label="创建时间" width="160" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="scope">
            <el-button
              size="small"
              type="primary"
              @click="handleEdit(scope.row)"
              :disabled="scope.row.role === 'owner' && userStore.role !== 'owner'"
            >
              编辑
            </el-button>
            <el-popconfirm
              title="确定要删除该用户吗？"
              @confirm="handleDelete(scope.row)"
            >
              <template #reference>
                <el-button
                  size="small"
                  type="danger"
                  :disabled="scope.row.role === 'owner'"
                >
                  删除
                </el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-model:current-page="pagination.currentPage"
        v-model:page-size="pagination.pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="pagination.total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
        class="pagination"
      />
    </el-card>

    <!-- 用户编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="500px"
      @close="handleDialogClose"
    >
      <el-form
        ref="userFormRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="formData.username"
            placeholder="请输入用户名"
          />
        </el-form-item>
        <el-form-item label="姓名" prop="first_name">
          <el-input
            v-model="formData.first_name"
            placeholder="请输入姓名"
          />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select
            v-model="formData.role"
            placeholder="请选择角色"
            style="width: 100%"
            :disabled="isEditingOwner"
            @change="handleRoleChange"
          >
            <el-option 
              v-if="userStore.role === 'owner'" 
              label="系统所有者" 
              value="owner" 
            />
            <el-option label="园长" value="principal" />
            <el-option label="教师" value="teacher" />
          </el-select>
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input
            v-model="formData.phone"
            placeholder="请输入手机号"
          />
        </el-form-item>
        <el-form-item v-if="!formData.id" label="密码" prop="password">
          <el-input
            v-model="formData.password"
            type="password"
            placeholder="请输入密码"
            show-password
          />
        </el-form-item>
        <el-form-item v-if="!formData.id" label="确认密码" prop="passwordConfirm">
          <el-input
            v-model="formData.passwordConfirm"
            type="password"
            placeholder="请再次输入密码"
            show-password
          />
        </el-form-item>
        <el-form-item label="所属幼儿园" prop="kindergarten">
          <el-select
            v-model="formData.kindergarten"
            placeholder="请选择所属幼儿园"
            style="width: 100%"
            clearable
            :disabled="shouldDisableKindergarten()"
          >
            <el-option
              v-for="item in kindergartenList"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item v-if="formData.role === 'teacher'" label="关联教师" prop="teacher">
          <el-select
            v-model="formData.teacher"
            placeholder="请选择关联的教师"
            style="width: 100%"
            clearable
            filterable
          >
            <el-option
              v-for="item in teacherList"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
          <div class="el-form-item-tip">选择关联的教师后，该用户将可以访问对应教师的数据</div>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import userApi from '@/api/users.js'
import { getKindergartenList } from '@/api/kindergarten.js'
import { getTeacherList } from '@/api/teachers.js'
import { useUserStore } from '@/store/modules/user.js'

// 表格数据
const userList = ref([])
const loading = ref(false)
const kindergartenList = ref([])
const teacherList = ref([])
const userStore = useUserStore()

// 搜索表单
const searchForm = reactive({
  username: '',
  first_name: '',
  role: ''
})

// 分页参数
const pagination = reactive({
  currentPage: 1,
  pageSize: 10,
  total: 0
})

// 对话框相关
const dialogVisible = ref(false)
const dialogTitle = ref('')
const formData = reactive({
  id: '',
  username: '',
  first_name: '',
  role: '',
  phone: '',
  password: '',
  passwordConfirm: '',
  kindergarten: '',
  teacher: ''
})
const isEditingOwner = ref(false)

// 判断是否应该禁用幼儿园选择框
const shouldDisableKindergarten = () => {
  // 如果是编辑状态且正在编辑系统管理员，则禁用
  if (isEditingOwner.value) {
    return true
  }
  
  // 任何时候都不禁用幼儿园选择框，园长可以自由选择
  return false
}

// 表单验证规则
const formRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  first_name: [
    { required: true, message: '请输入姓名', trigger: 'blur' }
  ],
  role: [
    { required: true, message: '请选择角色', trigger: 'change' }
  ],
  kindergarten: [
    { 
      required: true, 
      message: '请选择所属幼儿园', 
      trigger: 'change'
    }
  ],
  teacher: [
    { required: false, message: '请选择关联的教师', trigger: 'change' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ],
  passwordConfirm: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== formData.password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

// 表单引用
const userFormRef = ref()

// 生命周期钩子
onMounted(() => {
  loadUserList()
  loadKindergartenList()
  loadTeacherList()
  console.log('组件挂载完成') // 调试信息
})

// 获取用户列表
const loadUserList = async () => {
  loading.value = true
  try {
    const params = {
      ...searchForm,
      page: pagination.currentPage,
      page_size: pagination.pageSize
    }

    const res = await userApi.getUserList(params)
    console.log('用户列表响应数据:', res) // 调试信息
    
    // 初始化默认值
    let users = []
    let total = 0
    
    // 根据后端实际返回格式处理数据
    if (res && typeof res === 'object') {
      // 处理各种可能的响应格式
      if (Array.isArray(res)) {
        // 直接返回数组
        users = res
        total = res.length
      } else if (res.results && Array.isArray(res.results)) {
        // 分页格式 { results: [...], count: ... }
        users = res.results
        total = res.count || res.results.length
      } else if (res.data && Array.isArray(res.data)) {
        // 包含data字段的格式 { data: [...] }
        users = res.data
        total = res.total || res.count || res.data.length
      } else if (res.data && res.data.results && Array.isArray(res.data.results)) {
        // 嵌套data的分页格式 { data: { results: [...], count: ... } }
        users = res.data.results
        total = res.data.count || res.data.total || res.data.results.length
      } else {
        // 其他情况
        users = []
        total = 0
      }
    }

    // 设置用户列表和分页信息
    userList.value = users
    pagination.total = total
    
    console.log(`解析后的用户列表: ${users.length}个用户`, users)
  } catch (error) {
    ElMessage.error('获取用户列表失败')
    console.error('获取用户列表错误:', error)
  } finally {
    loading.value = false
  }
}

// 获取幼儿园列表
const loadKindergartenList = async () => {
  try {
    const res = await getKindergartenList({ page: 1, page_size: 1000 })
    if (res && Array.isArray(res)) {
      kindergartenList.value = res
    } else if (res && res.results && Array.isArray(res.results)) {
      kindergartenList.value = res.results
    } else if (res && res.data && Array.isArray(res.data)) {
      kindergartenList.value = res.data
    } else if (res && res.data && res.data.results && Array.isArray(res.data.results)) {
      kindergartenList.value = res.data.results
    } else {
      kindergartenList.value = []
    }
    console.log('幼儿园列表:', kindergartenList.value) // 调试信息
  } catch (error) {
    ElMessage.error('获取幼儿园列表失败')
    console.error('获取幼儿园列表错误:', error)
  }
}

// 获取教师列表
const loadTeacherList = async () => {
  try {
    const res = await getTeacherList({ page: 1, page_size: 1000 })
    if (res && Array.isArray(res)) {
      teacherList.value = res
    } else if (res && res.results && Array.isArray(res.results)) {
      teacherList.value = res.results
    } else if (res && res.data && Array.isArray(res.data)) {
      teacherList.value = res.data
    } else if (res && res.data && res.data.results && Array.isArray(res.data.results)) {
      teacherList.value = res.data.results
    } else {
      teacherList.value = []
    }
    console.log('教师列表:', teacherList.value) // 调试信息
  } catch (error) {
    ElMessage.error('获取教师列表失败')
    console.error('获取教师列表错误:', error)
  }
}

// 搜索
const handleSearch = () => {
  pagination.currentPage = 1
  loadUserList()
}

// 重置搜索
const resetSearch = () => {
  searchForm.username = ''
  searchForm.first_name = ''
  searchForm.role = ''
  pagination.currentPage = 1
  loadUserList()
}

// 分页大小改变
const handleSizeChange = (size) => {
  pagination.pageSize = size
  loadUserList()
}

// 页码改变
const handleCurrentChange = (current) => {
  pagination.currentPage = current
  loadUserList()
}

// 角色改变时的处理
const handleRoleChange = (value) => {
  // 如果角色不是教师，清空教师关联
  if (value !== 'teacher') {
    formData.teacher = ''
  }
  
  // 不再自动填充或清空幼儿园字段，让用户自由选择
}

// 新增用户
const handleAdd = () => {
  dialogTitle.value = '新增用户'
  isEditingOwner.value = false
  // 重置表单数据
  Object.keys(formData).forEach(key => {
    formData[key] = ''
  })
  
  // 设置默认角色为教师
  formData.role = 'teacher'
  
  // 不再自动填充幼儿园字段，让用户自由选择
  
  dialogVisible.value = true
}

// 编辑用户
const handleEdit = (row) => {
  // 检查是否有权限编辑系统管理员
  if (row.role === 'owner' && userStore.role !== 'owner') {
    ElMessage.warning('您没有权限编辑系统管理员')
    return
  }
  
  // 非系统管理员不能编辑系统管理员
  if (row.role === 'owner' && userStore.role !== 'owner') {
    ElMessage.warning('您没有权限编辑系统管理员')
    return
  }
  
  dialogTitle.value = '编辑用户'
  isEditingOwner.value = row.role === 'owner'
  Object.assign(formData, row)
  // 清空密码字段
  formData.password = ''
  formData.passwordConfirm = ''
  console.log('编辑用户数据:', formData) // 调试信息
  dialogVisible.value = true
}

// 删除用户
const handleDelete = async (row) => {
  // 检查是否尝试删除系统管理员
  if (row.role === 'owner') {
    ElMessage.warning('无法删除系统管理员')
    return
  }
  
  try {
    await userApi.deleteUser(row.id)
    ElMessage.success('删除成功')
    loadUserList()
  } catch (error) {
    ElMessage.error('删除失败')
    console.error(error)
  }
}

// 提交表单
const handleSubmit = async () => {
  userFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        // 检查是否尝试修改系统管理员角色
        if (isEditingOwner.value && formData.role !== 'owner') {
          try {
            await ElMessageBox.confirm(
              '您正在修改系统管理员的角色，确定要继续吗？',
              '警告',
              {
                confirmButtonText: '确定',
                cancelButtonText: '取消',
                type: 'warning'
              }
            )
          } catch {
            // 取消操作
            return
          }
        }
        
        // 非系统管理员不能创建系统管理员
        if (formData.role === 'owner' && userStore.role !== 'owner') {
          ElMessage.warning('您没有权限创建系统管理员')
          return
        }
        
        const data = {
          username: formData.username,
          first_name: formData.first_name,
          role: formData.role,
          phone: formData.phone
        }
        
        // 处理幼儿园字段 - 直接使用用户选择的幼儿园
        if (formData.kindergarten) {
          data.kindergarten = formData.kindergarten
        } else {
          ElMessage.error('请选择所属幼儿园')
          return
        }

        // 如果有密码则添加密码字段
        if (formData.password) {
          data.password = formData.password
        }

        // 如果是教师角色，则添加教师字段（无论是否选择了关联教师）
        if (formData.role === 'teacher') {
          data.teacher = formData.teacher || null
        }

        await submitUser(data)
      } catch (error) {
        ElMessage.error(formData.id ? '更新失败' : '新增失败')
        console.error(error)
      }
    }
  })
}

// 对话框关闭事件
const handleDialogClose = () => {
  userFormRef.value.resetFields()
}

// 提交用户数据的辅助函数
const submitUser = async (data) => {
  try {
    if (formData.id) {
      // 更新用户
      await userApi.updateUser(formData.id, data)
      ElMessage.success('更新成功')
    } else {
      // 新增用户
      if (!formData.password || !formData.passwordConfirm) {
        ElMessage.error('请填写密码和确认密码')
        return
      }
      await userApi.createUser(data)
      ElMessage.success('新增成功')
    }

    dialogVisible.value = false
    loadUserList()
  } catch (error) {
    ElMessage.error(formData.id ? '更新失败' : '新增失败')
    console.error(error)
  }
}

</script>

<style scoped>
.search-card {
  margin-bottom: 20px;
}

/* 设置搜索输入框固定宽度 */
.search-card :deep(.el-form-item .el-input) {
  width: 150px;
}

.system-users-role-select {
  width: 150px;
}

.toolbar {
  margin-bottom: 20px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.el-form-item-tip {
  font-size: 12px;
  color: #999;
  margin-top: 5px;
}

</style>
