<template>
  <div class="selections-container">
    <div class="page-header">
      <h2>选区管理</h2>
      <p>管理系统中的选区信息</p>
    </div>
    
    <el-card class="search-card">
      <el-form :model="searchForm" label-width="80px" inline @submit.prevent>
        <el-form-item label="选区名称">
          <el-input v-model="searchForm.name" placeholder="请输入选区名称" clearable />
        </el-form-item>
        <el-form-item label="所属班级">
          <el-select v-model="searchForm.class_id" placeholder="请选择班级" clearable class="selections-class-select">
            <el-option
              v-for="item in classList"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <el-card class="content-card">
      <template #header>
        <div class="card-header">
          <span>选区列表</span>
          <div class="card-actions">
            <el-button type="primary" @click="handleCreate">新增选区</el-button>
            <!-- 已删除批量删除按钮 -->
          </div>
        </div>
      </template>
      
      <el-table
        v-loading="loading"
        :data="selectionAreasData"
        stripe
      >
        <!-- 已删除选择列 -->
        <el-table-column prop="name" label="选区名称" min-width="120" />
        <el-table-column prop="class_name" label="所属班级" min-width="120" />
        <el-table-column label="选区图片" min-width="120">
          <template #default="{ row }">
            <el-image
              v-if="row.image"
              :src="row.image"
              class="selection-image"
              fit="cover"
              :preview-src-list="[row.image]"
              preview-teleported
            />
            <span v-else>暂无图片</span>
          </template>
        </el-table-column>
        <!-- 已删除最大容量和当前人数列 -->
        <el-table-column prop="description" label="描述" min-width="150" />
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <!-- 已删除查看幼儿按钮 -->
            <el-popconfirm
              title="确定要删除这个选区吗？"
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
      width="500px"
      @close="handleDialogClose"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="选区名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入选区名称" />
        </el-form-item>
        <el-form-item label="所属班级" prop="class_id">
          <el-select v-model="formData.class_id" placeholder="请选择班级" style="width: 100%">
            <el-option
              v-for="item in classList"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="描述" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="3"
            placeholder="请输入描述信息"
          />
        </el-form-item>
        
        <el-form-item label="选区图片">
          <el-upload
            class="avatar-uploader"
            :action="uploadUrl"
            :show-file-list="false"
            :on-success="handleAvatarSuccess"
            :before-upload="beforeAvatarUpload"
            :data="uploadData"
            :headers="uploadHeaders"
          >
            <img v-if="formData.image && typeof formData.image === 'string'" :src="formData.image" class="avatar" />
            <el-icon v-else-if="!formData.image" class="avatar-uploader-icon"><Plus /></el-icon>
            <div v-else class="file-name">{{ formData.image.name }}</div>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="handleDialogClose">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { 
  getSelectionAreas,
  createSelectionArea,
  updateSelectionArea,
  deleteSelectionArea,
  getSelectionArea
} from '@/api/selections'
import classApi from '@/api/classes'

// 状态管理
const loading = ref(false)
const dialogVisible = ref(false)
const dialogTitle = ref('')
const formRef = ref(null)
const selectionAreasData = ref([])
const classList = ref([])

// 上传相关
const uploadUrl = `${import.meta.env.VITE_API_BASE_URL || ''}/selections/selection-areas/`
const uploadData = ref({})
const uploadHeaders = {
  'Authorization': `Bearer ${localStorage.getItem('token')}`
}

// 查询条件
const searchForm = reactive({
  name: '',
  class_id: ''
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
  class_id: '',
  description: '',
  image: ''
})

// 表单验证规则
const formRules = reactive({
  name: [
    { required: true, message: '请输入选区名称', trigger: 'blur' },
    { min: 1, max: 50, message: '选区名称长度在 1 到 50 个字符', trigger: 'blur' }
  ],
  class_id: [
    { required: true, message: '请选择所属班级', trigger: 'change' }
  ],

})

// 获取选区列表
const getSelectionAreasList = async () => {
  loading.value = true
  try {
    // 构造查询参数，只传递有值的参数
    const params = {
      page: pagination.currentPage,
      page_size: pagination.pageSize
    }
    
    // 只有当搜索条件有值时才添加到参数中
    if (searchForm.name) {
      params.name = searchForm.name
    }
    if (searchForm.class_id) {
      params.class_id = searchForm.class_id
    }
    
    const res = await getSelectionAreas(params)
    // 处理分页数据结构的变化
    if (res.results) {
      // DRF默认分页格式
      selectionAreasData.value = res.results.items || res.results
      pagination.total = res.count || res.results.total
    } else {
      // 兼容旧格式
      selectionAreasData.value = res.items
      pagination.total = res.total
    }
  } catch (error) {
    ElMessage.error('获取选区列表失败')
  } finally {
    loading.value = false
  }
}

// 获取班级列表
const getClassList = async () => {
  try {
    const res = await classApi.getClassList({ page_size: 100 })
    // 处理分页数据结构的变化
    if (res && res.results) {
      // DRF默认分页格式
      classList.value = res.results.items || res.results
    } else {
      // 兼容旧格式
      classList.value = res.items || res
    }
  } catch (error) {
    ElMessage.error('获取班级列表失败')
  }
}

// 处理搜索
const handleSearch = () => {
  pagination.currentPage = 1
  getSelectionAreasList()
}

// 重置搜索
const resetSearch = () => {
  Object.keys(searchForm).forEach(key => {
    searchForm[key] = ''
  })
  pagination.currentPage = 1
  getSelectionAreasList()
}

// 处理分页大小变化
const handleSizeChange = (size) => {
  pagination.pageSize = size
  getSelectionAreasList()
}

// 处理页码变化
const handleCurrentChange = (current) => {
  pagination.currentPage = current
  getSelectionAreasList()
}

// 处理创建
const handleCreate = () => {
  dialogTitle.value = '新增选区'
  // 清空表单数据，确保不回填之前的编辑数据
  formData.id = ''
  formData.name = ''
  formData.class_id = ''
  formData.description = ''
  formData.image = ''
  dialogVisible.value = true
}

// 处理编辑
const handleEdit = async (row) => {
  dialogTitle.value = '编辑选区'
  try {
    // 获取选区详情以确保获取到正确的class_id
    const res = await getSelectionArea(row.id)
    console.log('选区详情响应:', res) // 调试日志
    // 直接检查响应是否有必要的字段，而不是检查 res.data
    if (res && res.id !== undefined && res.name !== undefined) {
      formData.id = res.id || ''
      formData.name = res.name || ''
      // 现在可以直接从响应中获取class_id
      formData.class_id = res.class_id || ''
      formData.description = res.description || ''
      formData.image = res.image || ''
      dialogVisible.value = true
    } else {
      console.error('选区详情响应结构不正确:', res)
      ElMessage.error('获取选区详情失败：响应数据格式不正确')
    }
  } catch (error) {
    console.error('获取选区详情失败:', error)
    ElMessage.error('获取选区详情失败：' + (error.message || '未知错误'))
  }
}

// 处理删除
const handleDelete = async (id) => {
  try {
    await deleteSelectionArea(id)
    ElMessage.success('删除成功')
    getSelectionAreasList()
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

// 查看幼儿
const viewChildren = (id) => {
  // 可以跳转到幼儿列表页面或打开对话框
  ElMessage.info('查看幼儿功能待实现')
}

// 重置表单
const resetForm = () => {
  formData.id = ''
  formData.name = ''
  formData.class_id = ''
  formData.description = ''
  formData.image = ''
  originalImageFile.value = null // 同时重置文件引用
  if (formRef.value) {
    formRef.value.resetFields()
  }
}

// 处理对话框关闭
const handleDialogClose = () => {
  resetForm()
  dialogVisible.value = false
}

// 处理提交
const handleSubmit = async () => {
  if (!formRef.value) return
  try {
    await formRef.value.validate()
    
    let data;
    let isFormData = false;
    
    // 如果有图片文件，则使用 FormData
    if (originalImageFile.value) {
      data = new FormData()
      data.append('name', formData.name)
      data.append('class_id', formData.class_id)
      data.append('description', formData.description)
      data.append('image', originalImageFile.value) // 使用原始文件对象
      isFormData = true;
    } else {
      // 否则使用普通对象
      data = {
        name: formData.name,
        class_id: formData.class_id,
        description: formData.description
      }
      
      // 如果有图片URL，则也添加到数据中
      if (formData.image) {
        data.image = formData.image;
      }
    }

    if (formData.id) {
      // 更新
      await updateSelectionArea(formData.id, data, isFormData)
      ElMessage.success('更新成功')
    } else {
      // 创建
      await createSelectionArea(data, isFormData)
      ElMessage.success('创建成功')
    }
    
    dialogVisible.value = false
    getSelectionAreasList()
  } catch (error) {
    // 检查是否是重复数据错误
    if (error.response && error.response.status === 400) {
      const errorMsg = error.response.data.detail || '选区名称和所属班级不能重复';
      ElMessage.error(errorMsg);
    } else {
      ElMessage.error('操作失败：' + (error.message || '未知错误'))
    }
    console.error('提交失败:', error)
  }
}

// 添加一个新的变量来存储原始文件对象
const originalImageFile = ref(null);

// 图片上传相关方法
const handleAvatarSuccess = (response, uploadFile) => {
  // 仅用于前端预览，不调用后端接口
  if (response && response.image) {
    formData.image = response.image;
  } else {
    formData.image = URL.createObjectURL(uploadFile.raw);
  }
  originalImageFile.value = uploadFile.raw; // 保存原始文件对象用于提交
}

const beforeAvatarUpload = (rawFile) => {
  // 检查文件类型
  if (rawFile.type !== 'image/jpeg' && rawFile.type !== 'image/png') {
    ElMessage.error('图片必须是 JPG 或 PNG 格式!')
    return false
  }
  // 检查文件大小 (2MB)
  if (rawFile.size / 1024 / 1024 > 2) {
    ElMessage.error('图片大小不能超过 2MB!')
    return false
  }
  
  // 仅用于前端预览，创建预览URL
  formData.image = URL.createObjectURL(rawFile);
  originalImageFile.value = rawFile; // 保存原始文件对象用于提交
  return false; // 返回 false 阻止自动上传
}

// 组件挂载时获取数据
onMounted(() => {
  getClassList()
  getSelectionAreasList()
})
</script>

<style scoped>
.selections-container {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0 0 10px 0;
  font-size: 24px;
  color: #303133;
}

.page-header p {
  margin: 0;
  color: #606266;
  font-size: 14px;
}

.search-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-actions {
  display: flex;
  gap: 10px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

/* 设置搜索输入框固定宽度 */
.search-card :deep(.el-form-item .el-input) {
  width: 150px;
}

.selections-class-select {
  width: 150px;
}

.selection-image {
  width: 80px;
  height: 80px;
  border-radius: 6px;
}

.avatar-uploader .avatar {
  width: 120px;
  height: 120px;
  display: block;
}

.file-name {
  width: 120px;
  height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  font-size: 12px;
  color: #666;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  padding: 4px;
}

.avatar-uploader .el-upload {
  border: 1px dashed var(--el-border-color);
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
</style>