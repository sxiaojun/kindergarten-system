<template>
  <div class="children-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>幼儿管理</span>
          <div>
            <el-button type="primary" @click="handleExportTemplate">
              <el-icon><Download /></el-icon>
              下载模板
            </el-button>
            <el-button type="primary" @click="handleImport">
              <el-icon><Upload /></el-icon>
              导入幼儿
            </el-button>
            <el-button type="primary" @click="handleAdd">
              <el-icon><Plus /></el-icon>
              新增幼儿
            </el-button>
            <el-button type="danger" @click="handleBatchDelete" :disabled="multipleSelection.length === 0">
              <el-icon><Delete /></el-icon>
              批量删除
            </el-button>
          </div>
        </div>
      </template>
      
      <!-- 搜索栏 -->
      <div class="search-bar">
        <el-form :inline="true" :model="searchForm" size="small" @submit.prevent>
          <el-form-item label="幼儿姓名">
            <el-input v-model="searchForm.name" placeholder="请输入幼儿姓名" clearable />
          </el-form-item>
          <el-form-item label="班级">
            <el-select v-model="searchForm.class_id" placeholder="请选择班级" clearable class="children-class-select">
              <el-option 
                v-for="cls in classList" 
                :key="cls.id" 
                :label="cls.name" 
                :value="cls.id" 
              />
            </el-select>
          </el-form-item>
          <el-form-item label="家长姓名">
            <el-input v-model="searchForm.parent_name" placeholder="请输入家长姓名" clearable />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">搜索</el-button>
            <el-button @click="resetSearch">重置</el-button>
          </el-form-item>
        </el-form>
      </div>
      
      <!-- 幼儿列表 -->
      <el-table
        v-loading="loading"
        :data="childrenList"
        border
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="student_id" label="学号" width="120" />
        <el-table-column prop="name" label="幼儿姓名" />
        <el-table-column prop="gender" label="性别" width="80">
          <template #default="scope">
            <el-tag :type="scope.row.gender === 'male' ? 'primary' : 'danger'">
              {{ scope.row.gender === 'male' ? '男' : '女' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="age" label="年龄" width="80" />
        <el-table-column prop="class_info.name" label="班级" />
        <el-table-column prop="parent_name" label="家长姓名" />
        <el-table-column prop="parent_phone" label="家长电话" />
        <el-table-column prop="admission_date" label="入园日期" width="120">
          <template #default="scope">
            {{ scope.row.admission_date }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-popconfirm
              title="确定要删除这个幼儿吗？"
              @confirm="handleDelete(row.id)"
            >
              <template #reference>
                <el-button type="danger" link>删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.currentPage"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
    
    <!-- 编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      @close="handleDialogClose"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="幼儿姓名" prop="name">
              <el-input v-model="formData.name" placeholder="请输入幼儿姓名" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="性别" prop="gender">
              <el-select v-model="formData.gender" placeholder="请选择性别" style="width: 100%">
                <el-option label="男" value="male" />
                <el-option label="女" value="female" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="出生日期" prop="birth_date">
              <el-date-picker
                v-model="formData.birth_date"
                type="date"
                placeholder="请选择出生日期"
                style="width: 100%"
                value-format="YYYY-MM-DD"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="班级" prop="class_id">
              <el-select v-model="formData.class_id" placeholder="请选择班级" style="width: 100%">
                <el-option 
                  v-for="cls in classList" 
                  :key="cls.id" 
                  :label="cls.name" 
                  :value="cls.id" 
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="入园日期" prop="admission_date">
              <el-date-picker
                v-model="formData.admission_date"
                type="date"
                placeholder="请选择入园日期"
                style="width: 100%"
                value-format="YYYY-MM-DD"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="学号" prop="student_id">
              <el-input v-model="formData.student_id" placeholder="请输入学号" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="家长姓名" prop="parent_name">
              <el-input v-model="formData.parent_name" placeholder="请输入家长姓名" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="家长电话" prop="parent_phone">
              <el-input v-model="formData.parent_phone" placeholder="请输入家长电话" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="家长邮箱" prop="parent_email">
              <el-input v-model="formData.parent_email" placeholder="请输入家长邮箱" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="家庭地址" prop="home_address">
              <el-input v-model="formData.home_address" placeholder="请输入家庭地址" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="健康备注" prop="health_notes">
          <el-input 
            v-model="formData.health_notes" 
            placeholder="请输入健康备注信息，如过敏史等" 
            type="textarea" 
            :rows="3" 
          />
        </el-form-item>
        <el-form-item label="备注" prop="notes">
          <el-input v-model="formData.notes" placeholder="请输入备注信息" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="头像" prop="avatar" :rules="avatarRules">
          <el-upload
            class="avatar-uploader"
            :action="avatarUploadUrl"
            :show-file-list="false"
            :before-upload="beforeAvatarUpload"
            :on-success="handleAvatarSuccess"
            :disabled="avatarUploadDisabled"
            :auto-upload="false"
            :on-change="handleAvatarChange"
            ref="avatarUploadRef"
          >
            <img v-if="formData.avatar" :src="formData.avatar" class="avatar" />
            <el-icon v-else class="avatar-uploader-icon"><Plus /></el-icon>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
    
    <!-- 导入对话框 -->
    <el-dialog v-model="importDialogVisible" title="导入幼儿" width="500px">
      <el-form ref="importFormRef" :model="importFormData" :rules="importFormRules" label-width="100px">
        <el-form-item label="选择文件" prop="file">
          <el-upload
            ref="uploadRef"
            class="upload-demo"
            action=""
            :auto-upload="false"
            :show-file-list="true"
            :on-change="handleFileChange"
            accept=".xlsx,.xls"
          >
            <el-button type="primary">选择文件</el-button>
            <template #tip>
              <div class="el-upload__tip">
                请上传Excel文件 (.xlsx 或 .xls)
              </div>
            </template>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="importDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleImportSubmit" :loading="importLoading">导入</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Upload, Download } from '@element-plus/icons-vue'
import { 
  getChildrenList, 
  createChild, 
  updateChild, 
  deleteChild, 
  getClassList, 
  importChildren,
  exportChildTemplate
} from '@/api/children'
import { saveAs } from 'file-saver'

export default {
  name: 'ChildManagement',
  components: {
    Plus,
    Upload,
    Download
  },
  setup() {
    // 状态定义
    const loading = ref(false)
    const dialogVisible = ref(false)
    const importDialogVisible = ref(false)
    const importLoading = ref(false)
    const dialogTitle = ref('')
    const formRef = ref()
    const importFormRef = ref()
    const uploadRef = ref()
    const avatarUploadRef = ref() // 添加这一行
    const childrenList = ref([])
    const classList = ref([])
    // 批量删除相关状态
    const multipleSelection = ref([])
    
    // 搜索表单
    const searchForm = reactive({
      name: '',
      class_id: '',
      parent_name: '',
      parent_phone: ''
    })
    
    // 分页信息
    const pagination = reactive({
      currentPage: 1,
      pageSize: 10,
      total: 0
    })
    
    // 表单数据
    const formData = reactive({
      id: '',
      name: '',
      gender: 'male',
      birth_date: '',
      class_id: '',
      student_id: '',
      admission_date: '',
      parent_name: '',
      parent_phone: '',
      parent_email: '',
      home_address: '',
      health_notes: '',
      notes: '',
      avatar: '',
      avatarFile: null // 添加这一行用于存储头像文件
    })
    
    // 新增状态标识
    const isEditing = computed(() => !!formData.id)
    
    // 头像上传URL
    const avatarUploadUrl = computed(() => {
      if (formData.id) {
        return `/api/children/${formData.id}/upload_avatar/`
      }
      // 对于新创建的幼儿，不需要单独的上传URL
      return ''
    })
    
    // 头像上传禁用状态
    const avatarUploadDisabled = computed(() => {
      // 编辑模式下启用上传功能
      if (formData.id) {
        return false
      }
      // 创建模式下使用表单提交方式
      return true
    })
    
    // 头像验证规则
    const avatarRules = computed(() => {
      return [{ required: true, message: '请上传头像', trigger: 'change' }]
    })
    
    // 导入表单数据
    const importFormData = reactive({
      file: null
    })
    
    // 表单验证规则
    const formRules = {
      name: [
        { required: true, message: '请输入幼儿姓名', trigger: 'blur' },
        { min: 1, max: 20, message: '长度在 1 到 20 个字符', trigger: 'blur' }
      ],
      gender: [
        { required: true, message: '请选择性别', trigger: 'change' }
      ],
      birth_date: [
        { required: true, message: '请选择出生日期', trigger: 'change' }
      ],
      class_id: [
        { required: true, message: '请选择班级', trigger: 'change' }
      ],
      parent_name: [
        { message: '请输入家长姓名', trigger: 'blur' }
      ],
      parent_phone: [
        { message: '请输入联系电话', trigger: 'blur' }
      ]
    }
    
    // 导入表单验证规则
    const importFormRules = {
      file: [
        { required: true, message: '请选择要导入的文件', trigger: 'change' }
      ]
    }
    
    // 获取幼儿列表
    const loadChildrenList = async () => {
      loading.value = true
      try {
        const params = {
          page: pagination.currentPage,
          page_size: pagination.pageSize,
          name: searchForm.name,
          class_id: searchForm.class_id,
          parent_name: searchForm.parent_name,
          parent_phone: searchForm.parent_phone
        }
        const res = await getChildrenList(params)
        
        // 根据后端实际返回格式处理数据
        if (res && Array.isArray(res)) {
          // 如果是数组格式，直接使用
          childrenList.value = res
          pagination.total = res.length
        } else if (res && res.results && Array.isArray(res.results)) {
          // 如果是分页格式，使用分页数据
          childrenList.value = res.results
          pagination.total = res.count || res.results.length
        } else if (res && res.data && Array.isArray(res.data)) {
          // 兼容之前的处理方式
          childrenList.value = res.data
          pagination.total = res.data.length
        } else if (res && res.data && res.data.results && Array.isArray(res.data.results)) {
          // 兼容之前的分页格式
          childrenList.value = res.data.results
          pagination.total = res.data.count || res.data.results.length
        } else if (res && res.data && Array.isArray(res.data.items)) {
          // 如果是带有items字段的对象格式
          childrenList.value = res.data.items
          pagination.total = res.data.total || res.data.items.length
        } else {
          // 如果没有返回数据，设置为空数组
          childrenList.value = []
          pagination.total = 0
        }
      } catch (error) {
        ElMessage.error('获取幼儿列表失败')
      } finally {
        loading.value = false
      }
    }
    
    // 获取班级列表
    const loadClassList = async () => {
      try {
        const res = await getClassList()
        
        // 根据后端实际返回格式处理数据
        if (res && Array.isArray(res)) {
          // 如果是数组格式，直接使用
          classList.value = res
        } else if (res && res.results && Array.isArray(res.results)) {
          // 如果是分页格式，使用分页数据
          classList.value = res.results
        } else if (res && res.data && Array.isArray(res.data)) {
          // 兼容之前的处理方式
          classList.value = res.data
        } else if (res && res.data && res.data.results && Array.isArray(res.data.results)) {
          // 兼容之前的分页格式
          classList.value = res.data.results
        } else if (res && res.data && Array.isArray(res.data.items)) {
          // 如果是带有items字段的对象格式
          classList.value = res.data.items
        } else {
          // 如果没有返回数据，设置为空数组
          classList.value = []
        }
      } catch (error) {
        ElMessage.error('获取班级列表失败')
      }
    }
    
    // 处理搜索
    const handleSearch = () => {
      pagination.currentPage = 1
      loadChildrenList()
    }
    
    // 重置搜索
    const resetSearch = () => {
      Object.keys(searchForm).forEach(key => {
        searchForm[key] = ''
      })
      pagination.currentPage = 1
      loadChildrenList()
    }
    
    // 处理分页大小变化
    const handleSizeChange = (size) => {
      pagination.pageSize = size
      loadChildrenList()
    }
    
    // 处理页码变化
    const handleCurrentChange = (current) => {
      pagination.currentPage = current
      loadChildrenList()
    }
    
    // 处理新增
    const handleAdd = () => {
      dialogTitle.value = '新增幼儿'
      resetForm()
      dialogVisible.value = true
    }
    
    // 处理编辑
    const handleEdit = (row) => {
      dialogTitle.value = '编辑幼儿'
      // 填充表单数据
      Object.keys(formData).forEach(key => {
        if (key === 'class_id' && row.class_info) {
          // 特殊处理班级ID字段，从class_info对象中提取
          formData[key] = row.class_info.id || ''
        } else {
          formData[key] = row[key] || ''
        }
      })
      dialogVisible.value = true
    }
    
    // 处理删除
    const handleDelete = async (id) => {
      try {
        await ElMessageBox.confirm('确定要删除这个幼儿吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        
        await deleteChild(id)
        ElMessage.success('删除成功')
        loadChildrenList()
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error('删除失败: ' + (error.message || error))
        }
      }
    }
    // 处理多选
    const handleSelectionChange = (selection) => {
      multipleSelection.value = selection
    }

    // 批量删除
    const handleBatchDelete = async () => {
      if (multipleSelection.value.length === 0) {
        ElMessage.warning('请至少选择一个幼儿')
        return
      }

      try {
        await ElMessageBox.confirm(
          `确定要删除选中的 ${multipleSelection.value.length} 个幼儿吗？`,
          '提示',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )

        // 执行批量删除
        const deletePromises = multipleSelection.value.map(item =>
          deleteChild(item.id)
        )

        await Promise.all(deletePromises)
        ElMessage.success('删除成功')
        loadChildrenList() // 重新加载列表
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error('删除失败: ' + (error.message || error))
        }
      }
    }

    
    // 重置表单
    const resetForm = () => {
      Object.keys(formData).forEach(key => {
        if (key === 'gender') {
          formData[key] = 'male'
        } else {
          formData[key] = ''
        }
      })
      if (formRef.value) {
        formRef.value.resetFields()
      }
    }
    
    // 处理对话框关闭
    const handleDialogClose = () => {
      resetForm()
      dialogVisible.value = false
    }
    
    // 提交表单
    const handleSubmit = async () => {
      if (!formRef.value) return
      await formRef.value.validate(async (valid) => {
        if (valid) {
          try {
            let childId = formData.id;
            if (childId) {
              // 编辑（支持上传头像）
              // 创建FormData对象来同时发送幼儿信息和头像
              const formDataToSend = new FormData()
              
              // 添加所有幼儿信息到FormData
              Object.keys(formData).forEach(key => {
                if (key !== 'avatar' && key !== 'avatarFile' && formData[key] !== '') {
                  formDataToSend.append(key, formData[key])
                }
              })
              
              // 添加头像文件（如果有）
              if (formData.avatarFile) {
                formDataToSend.append('avatar', formData.avatarFile)
              }
              
              await updateChild(childId, formDataToSend)
              ElMessage.success('更新成功')
            } else {
              // 新增（支持上传头像）
              // 创建FormData对象来同时发送幼儿信息和头像
              const formDataToSend = new FormData()
              
              // 添加所有幼儿信息到FormData
              Object.keys(formData).forEach(key => {
                if (key !== 'avatar' && key !== 'avatarFile' && formData[key] !== '') {
                  formDataToSend.append(key, formData[key])
                }
              })
              
              // 添加头像文件
              if (formData.avatarFile) {
                formDataToSend.append('avatar', formData.avatarFile)
              }
              
              const response = await createChild(formDataToSend)
              childId = response.id
              ElMessage.success('创建成功')
            }
            dialogVisible.value = false
            loadChildrenList()
          } catch (error) {
            ElMessage.error('操作失败: ' + (error.message || error))
          }
        }
      })
    }
    
    // 处理导入
    const handleImport = () => {
      importDialogVisible.value = true
      importFormData.file = null
      if (uploadRef.value) {
        uploadRef.value.clearFiles()
      }
    }
    
    // 处理文件选择
    const handleFileChange = (file) => {
      importFormData.file = file.raw
    }
    
    // 提交导入
    const handleImportSubmit = async () => {
      if (!importFormRef.value) return
      try {
        await importFormRef.value.validate()
        
        if (!importFormData.file) {
          ElMessage.error('请选择要导入的文件')
          return
        }
        
        importLoading.value = true
        
        // 创建FormData对象
        const formData = new FormData()
        formData.append('file', importFormData.file)
        
        // 调用导入API
        const response = await importChildren(formData)
        
        if (response) {
          // 检查是否有错误信息
          if (response.errors && response.errors.length > 0) {
            // 显示详细的错误信息
            let errorMsg = `导入完成，但有 ${response.errors.length} 个错误:\n`
            response.errors.forEach(error => {
              errorMsg += `${error}\n`
            })
            ElMessage.error(errorMsg)
          } else {
            ElMessage.success(`导入成功！共导入${response.created_count}条记录`)
          }
          importDialogVisible.value = false
          loadChildrenList() // 重新加载列表
        } else {
          ElMessage.error('导入失败')
        }
      } catch (error) {
        // 特别处理包含错误信息的响应
        if (error.response && error.response.data && error.response.data.errors) {
          let errorMsg = `导入失败，有 ${error.response.data.errors.length} 个错误:\n`
          error.response.data.errors.forEach(err => {
            errorMsg += `${err}\n`
          })
          ElMessage.error(errorMsg)
        } else {
          ElMessage.error('导入失败: ' + (error.message || '网络错误'))
        }
      } finally {
        importLoading.value = false
      }
    }
    
    // 处理导出模板
    const handleExportTemplate = async () => {
      try {
        const response = await exportChildTemplate()
        const blob = new Blob([response], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
        saveAs(blob, `幼儿导入模板.xlsx`)
        ElMessage.success('模板下载成功')
      } catch (error) {
        ElMessage.error('模板下载失败: ' + (error.message || '网络错误'))
      }
    }
    
    // 头像相关函数
    const handleAvatarSuccess = (response, file) => {
      formData.avatar = response.url
    }
    
    const beforeAvatarUpload = (file) => {
      const isJPG = file.type === 'image/jpeg' || file.type === 'image/png'
      const isLt2M = file.size / 1024 / 1024 < 2
      
      if (!isJPG) {
        ElMessage.error('头像图片只能是 JPG 或 PNG 格式!')
      }
      if (!isLt2M) {
        ElMessage.error('头像图片大小不能超过 2MB!')
      }
      return isJPG && isLt2M
    }
    
    // 新增处理头像变更的方法
    const handleAvatarChange = (file) => {
      formData.avatarFile = file.raw
      // 创建预览URL
      formData.avatar = URL.createObjectURL(file.raw)
    }
    
    // 查看成长记录
    const viewGrowthRecords = (row) => {
      ElMessage.info('查看成长记录功能待实现')
    }
    
    // 初始加载
    onMounted(async () => {
      await Promise.all([
        loadChildrenList(),
        loadClassList()
      ])
    })
    
    return {
      loading,
      dialogVisible,
      importDialogVisible,
      importLoading,
      dialogTitle,
      formRef,
      importFormRef,
      uploadRef,
      avatarUploadRef, // 添加这一行
      childrenList,
      classList,
      searchForm,
      pagination,
      formData,
      importFormData,
      formRules,
      importFormRules,
      handleSearch,
      resetSearch,
      handleSizeChange,
      handleCurrentChange,
      handleAdd,
      handleEdit,
      handleDelete,
      handleDialogClose,
      handleSubmit,
      handleImport,
      handleFileChange,
      handleImportSubmit,
      handleExportTemplate,
      handleAvatarSuccess,
      beforeAvatarUpload,
      handleAvatarChange, // 添加这一行
      viewGrowthRecords,
      handleSelectionChange,
      handleBatchDelete,
      multipleSelection
    }
  }
}
</script>

<style scoped>
.children-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-bar {
  margin-bottom: 20px;
}

/* 设置搜索输入框固定宽度 */
.search-bar :deep(.el-form-item .el-input) {
  width: 150px;
}

.search-bar :deep(.el-select) {
  width: 150px;
}

.children-class-select {
  width: 150px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.avatar-uploader .avatar {
  width: 120px;
  height: 120px;
  display: block;
}

.avatar-uploader .el-upload {
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: var(--el-transition-duration-fast);
}

.avatar-uploader .el-upload:hover {
  border-color: var(--el-color-primary);
}

.el-icon.avatar-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 120px;
  height: 120px;
  text-align: center;
}

.avatar-placeholder {
  display: none;
}

.avatar-text {
  font-size: 12px;
  color: #8c939d;
  margin-top: 8px;
}
</style>