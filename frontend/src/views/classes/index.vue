<template>
  <div class="classes-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>班级管理</span>
          <div>
            <el-button type="primary" @click="handleExportTemplate">
              <el-icon><Download /></el-icon>
              下载模板
            </el-button>
            <el-button type="primary" @click="handleImport">
              <el-icon><Upload /></el-icon>
              导入班级
            </el-button>
            <el-button type="primary" @click="handleAdd">
              <el-icon><Plus /></el-icon>
              新增班级
            </el-button>
          </div>
        </div>
      </template>
      
      <!-- 搜索栏 -->
      <div class="search-bar">
        <el-form :inline="true" :model="searchForm" size="small" @submit.prevent>
          <el-form-item label="班级名称">
            <el-input v-model="searchForm.name" placeholder="请输入班级名称" clearable />
          </el-form-item>
          <el-form-item label="班级类型">
            <el-select v-model="searchForm.class_type" placeholder="请选择班级类型" clearable class="classes-class-type-select">
              <el-option label="托儿所" value="nursery" />
              <el-option label="小班" value="small" />
              <el-option label="中班" value="middle" />
              <el-option label="大班" value="large" />
              <el-option label="学前班" value="pre_school" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">搜索</el-button>
            <el-button @click="resetSearch">重置</el-button>
          </el-form-item>
        </el-form>
      </div>
      
      <!-- 班级列表 -->
      <el-table
        v-loading="loading"
        :data="classList"
        border
        style="width: 100%"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="班级名称" />
        <el-table-column prop="kindergarten.name" label="所属幼儿园" />
        <el-table-column prop="class_type" label="班级类型" width="100">
          <template #default="scope">
            <el-tag :type="getClassTypeTag(scope.row.class_type)">
              {{ getClassTypeText(scope.row.class_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="classroom_location" label="教室位置" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-popconfirm
              title="确定要删除这个班级吗？"
              @confirm="handleDelete(row.id)"
            >
              <template #reference>
                <el-button type="danger" link>删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="pagination">
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
      @close="handleClose"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="班级名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入班级名称" />
        </el-form-item>
        <el-form-item label="班级类型" prop="class_type">
          <el-select v-model="formData.class_type" placeholder="请选择班级类型" style="width: 100%">
            <el-option label="托儿所" value="nursery" />
            <el-option label="小班" value="small" />
            <el-option label="中班" value="middle" />
            <el-option label="大班" value="large" />
            <el-option label="学前班" value="pre_school" />
          </el-select>
        </el-form-item>
        <el-form-item label="所属幼儿园" prop="kindergarten_id">
          <el-select 
            v-model="formData.kindergarten_id" 
            placeholder="请选择所属幼儿园" 
            style="width: 100%"
            
          >
            <el-option 
              v-for="item in kindergartenList" 
              :key="item.id" 
              :label="item.name" 
              :value="item.id" 
            />
          </el-select>
        </el-form-item>
        <el-form-item label="教室位置" prop="classroom_location">
          <el-input v-model="formData.classroom_location" placeholder="请输入教室位置" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
    
    <!-- 导入对话框 -->
    <el-dialog v-model="importDialogVisible" title="导入班级" width="500px">
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
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Upload, Download } from '@element-plus/icons-vue'
import { 
  getClassList, 
  createClass, 
  updateClass, 
  deleteClass, 
  importClasses,
  exportClassTemplate
} from '@/api/classes'
import { getKindergartenList } from '@/api/kindergarten'
import router from '@/router'
import { useUserStore } from '@/store/modules/user'
import { saveAs } from 'file-saver'

export default {
  name: 'ClassManagement',
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
    const classList = ref([])
    const kindergartenList = ref([])
    const userStore = useUserStore()
    
    // 搜索表单
    const searchForm = reactive({
      name: '',
      class_type: ''
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
      class_type: '',
      kindergarten_id: '',

      classroom_location: ''
    })
    
    // 导入表单数据
    const importFormData = reactive({
      file: null
    })
    
    // 表单验证规则
    const formRules = {
      name: [
        { required: true, message: '请输入班级名称', trigger: 'blur' },
        { min: 1, max: 50, message: '长度在 1 到 50 个字符', trigger: 'blur' }
      ],
      class_type: [
        { required: true, message: '请选择班级类型', trigger: 'change' }
      ],
      kindergarten_id: [
        { required: true, message: '请选择所属幼儿园', trigger: 'change' }
      ]
    }
    
    // 导入表单验证规则
    const importFormRules = {
      file: [
        { required: true, message: '请选择要导入的文件', trigger: 'change' }
      ]
    }
    
    // 获取班级类型对应的标签类型
    const getClassTypeTag = (type) => {
      const tagMap = {
        'nursery': '',
        'small': 'primary',
        'middle': 'success',
        'large': 'warning',
        'pre_school': 'danger'
      }
      return tagMap[type] || 'info'
    }
    
    // 获取班级类型文本
    const getClassTypeText = (type) => {
      const textMap = {
        'nursery': '托儿所',
        'small': '小班',
        'middle': '中班',
        'large': '大班',
        'pre_school': '学前班'
      }
      return textMap[type] || type
    }
    
    // 获取班级列表
    const loadClassList = async () => {
      loading.value = true
      try {
        const params = {
          page: pagination.currentPage,
          page_size: pagination.pageSize,
          name: searchForm.name,
          class_type: searchForm.class_type
        }
        const res = await getClassList(params)
        
        // 根据后端实际返回格式处理数据
        if (res && Array.isArray(res)) {
          // 如果是数组格式，直接使用
          classList.value = res
          pagination.total = res.length
        } else if (res && res.results && Array.isArray(res.results)) {
          // 如果是分页格式，使用分页数据
          classList.value = res.results
          pagination.total = res.count || res.results.length
        } else if (res && res.data && Array.isArray(res.data)) {
          // 兼容之前的处理方式
          classList.value = res.data
          pagination.total = res.data.length
        } else if (res && res.data && res.data.results && Array.isArray(res.data.results)) {
          // 兼容之前的分页格式
          classList.value = res.data.results
          pagination.total = res.data.count || res.data.results.length
        } else if (res && res.data && Array.isArray(res.data.items)) {
          // 如果是带有items字段的对象格式
          classList.value = res.data.items
          pagination.total = res.data.total || res.data.items.length
        } else {
          // 如果没有返回数据，设置为空数组
          classList.value = []
          pagination.total = 0
        }
      } catch (error) {
        ElMessage.error('获取班级列表失败')
      } finally {
        loading.value = false
      }
    }
    

    
    // 获取幼儿园列表
    const loadKindergartenList = async () => {
      try {
        const res = await getKindergartenList()
        
        // 根据后端实际返回格式处理数据
        if (res && Array.isArray(res)) {
          // 如果是数组格式，直接使用
          kindergartenList.value = res
        } else if (res && res.results && Array.isArray(res.results)) {
          // 如果是分页格式，使用分页数据
          kindergartenList.value = res.results
        } else if (res && res.data && Array.isArray(res.data)) {
          // 兼容之前的处理方式
          kindergartenList.value = res.data
        } else if (res && res.data && res.data.results && Array.isArray(res.data.results)) {
          // 兼容之前的分页格式
          kindergartenList.value = res.data.results
        } else if (res && res.data && Array.isArray(res.data.items)) {
          // 如果是带有items字段的对象格式
          kindergartenList.value = res.data.items
        } else {
          // 如果没有返回数据，设置为空数组
          kindergartenList.value = []
        }
      } catch (error) {
        ElMessage.error('获取幼儿园列表失败')
      }
    }
    
    // 处理搜索
    const handleSearch = () => {
      pagination.currentPage = 1
      loadClassList()
    }
    
    // 重置搜索
    const resetSearch = () => {
      Object.keys(searchForm).forEach(key => {
        searchForm[key] = ''
      })
      pagination.currentPage = 1
      loadClassList()
    }
    
    // 处理分页大小变化
    const handleSizeChange = (size) => {
      pagination.pageSize = size
      loadClassList()
    }
    
    // 处理页码变化
    const handleCurrentChange = (current) => {
      pagination.currentPage = current
      loadClassList()
    }
    
    // 处理创建
    const handleAdd = () => {
      dialogTitle.value = '新增班级'
      // 清空表单数据，确保不回填之前的编辑数据
      formData.id = ''
      formData.name = ''
      formData.class_type = ''
      formData.kindergarten_id = ''
      formData.classroom_location = ''
      dialogVisible.value = true
    }
    
    // 处理编辑
    const handleEdit = (row) => {
      dialogTitle.value = '编辑班级'
      // 填充表单数据
      formData.id = row.id
      formData.name = row.name
      formData.class_type = row.class_type
      formData.kindergarten_id = row.kindergarten?.id || ''
      formData.classroom_location = row.classroom_location || ''
      dialogVisible.value = true
    }
    
    // 处理删除
    const handleDelete = async (id) => {
      try {
        await deleteClass(id)
        ElMessage.success('删除成功')
        loadClassList()
      } catch (error) {
        ElMessage.error('删除失败')
      }
    }
    
    // 提交表单
    const handleSubmit = async () => {
      if (!formRef.value) return
      try {
        await formRef.value.validate()
        
        // 准备提交数据
        const submitData = { ...formData }
        
        if (formData.id) {
          // 编辑
          await updateClass(formData.id, submitData)
          ElMessage.success('更新成功')
        } else {
          // 新增
          await createClass(submitData)
          ElMessage.success('创建成功')
        }
        
        dialogVisible.value = false
        loadClassList()
      } catch (error) {
        // 验证失败或请求失败
        if (error !== false) { // 排除验证失败的情况
          ElMessage.error('操作失败')
        }
      }
    }
    
    // 关闭对话框前的处理
    const handleClose = (done) => {
      // 重置表单
      if (formRef.value) {
        formRef.value.resetFields()
      }
      // 如果 done 是函数则调用它，否则直接返回
      if (typeof done === 'function') {
        done()
      }
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
        const response = await importClasses(formData)
        
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
            ElMessage.success(`导入成功！共导入${response.created_count || 0}条记录`)
          }
          importDialogVisible.value = false
          loadClassList() // 重新加载列表
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
        const response = await exportClassTemplate()
        const blob = new Blob([response], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
        saveAs(blob, `班级导入模板.xlsx`)
        ElMessage.success('模板下载成功')
      } catch (error) {
        ElMessage.error('模板下载失败: ' + (error.message || '网络错误'))
      }
    }
    
    // 初始加载
    onMounted(async () => {
      await Promise.all([
        loadClassList(),
        loadKindergartenList()
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
      classList,
      kindergartenList,
      userStore,
      searchForm,
      pagination,
      formData,
      importFormData,
      formRules,
      importFormRules,
      getClassTypeTag,
      getClassTypeText,
      handleSearch,
      resetSearch,
      handleSizeChange,
      handleCurrentChange,
      handleAdd,
      handleEdit,
      handleDelete,
      handleSubmit,
      handleClose,
      handleImport,
      handleFileChange,
      handleImportSubmit,
      handleExportTemplate
    }
  }
}
</script>

<style scoped>
.classes-container {
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

.classes-class-type-select {
  width: 150px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>