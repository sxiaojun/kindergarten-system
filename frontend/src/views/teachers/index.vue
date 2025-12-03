<template>
  <div class="teachers-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>教师管理</span>
          <div>
            <el-button type="primary" @click="handleExportTemplate">
              <el-icon><Download /></el-icon>
              下载模板
            </el-button>
            <el-button type="primary" @click="handleImport">
              <el-icon><Upload /></el-icon>
              导入教师
            </el-button>
            <el-button type="primary" @click="handleAdd">
              <el-icon><Plus /></el-icon>
              新增教师
            </el-button>
          </div>
        </div>
      </template>
      
      <!-- 搜索栏 -->
      <div class="search-bar">
        <el-form :inline="true" :model="searchForm" size="small" @submit.prevent>
          <el-form-item label="姓名">
            <el-input v-model="searchForm.name" placeholder="请输入教师姓名" clearable />
          </el-form-item>
          <el-form-item label="工号">
            <el-input v-model="searchForm.employee_id" placeholder="请输入工号" clearable />
          </el-form-item>
          <el-form-item label="手机号码">
            <el-input v-model="searchForm.phone" placeholder="请输入手机号码" clearable />
          </el-form-item>
          <el-form-item label="职位">
            <el-select v-model="searchForm.position" placeholder="请选择职位" clearable class="teachers-position-select">
              <el-option label="班主任" value="head_teacher" />
              <el-option label="配班老师" value="assistant_teacher" />
              <el-option label="生活老师" value="life_teacher" />
              <el-option label="园长" value="principal" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">搜索</el-button>
            <el-button @click="resetSearch">重置</el-button>
          </el-form-item>
        </el-form>
      </div>
      
      <!-- 教师列表 -->
      <el-table
        v-loading="loading"
        :data="teacherList"
        border
        style="width: 100%"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="姓名" />
        <el-table-column prop="employee_id" label="工号" />
        <el-table-column prop="gender" label="性别" width="80">
          <template #default="scope">
            <el-tag :type="scope.row.gender === 'male' ? 'primary' : 'danger'">
              {{ scope.row.gender === 'male' ? '男' : '女' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="position" label="职位">
          <template #default="scope">
            <el-tag :type="getPositionTag(scope.row.position)">
              {{ getPositionText(scope.row.position) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="phone" label="手机号码" />
        <el-table-column prop="email" label="电子邮箱" />
        <el-table-column prop="hire_date" label="入职日期" width="120">
          <template #default="scope">
            {{ scope.row.hire_date }}
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="80">
          <template #default="scope">
            <el-tag :type="scope.row.is_active ? 'success' : 'danger'">
              {{ scope.row.is_active ? '在职' : '离职' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-popconfirm
              title="确定要删除这个教师吗？"
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
      width="600px"
      @close="handleClose"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="姓名" prop="name">
              <el-input v-model="formData.name" placeholder="请输入教师姓名" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="工号" prop="employee_id">
              <el-input v-model="formData.employee_id" placeholder="请输入工号" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="性别" prop="gender">
              <el-select v-model="formData.gender" placeholder="请选择性别" style="width: 100%">
                <el-option label="男" value="male" />
                <el-option label="女" value="female" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="职位" prop="position">
              <el-select v-model="formData.position" placeholder="请选择职位" style="width: 100%">
                <el-option label="园长" value="principal" />
                <el-option label="班主任" value="head_teacher" />
                <el-option label="配班老师" value="assistant_teacher" />
                <el-option label="生活老师" value="life_teacher" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="手机号码" prop="phone">
              <el-input v-model="formData.phone" placeholder="请输入手机号码" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="邮箱" prop="email">
              <el-input v-model="formData.email" placeholder="请输入邮箱" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="班级*" prop="class_id" v-if="formData.position !== 'principal'">
              <el-select v-model="formData.class_id" placeholder="请选择班级">
                <el-option 
                  v-for="cls in classList" 
                  :key="cls.id" 
                  :label="cls.name" 
                  :value="cls.id" 
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="入职日期" prop="hire_date">
              <el-date-picker
                v-model="formData.hire_date"
                type="date"
                placeholder="请选择入职日期"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="备注" prop="notes">
          <el-input v-model="formData.notes" placeholder="请输入备注信息" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
    
    <!-- 导入对话框 -->
    <el-dialog v-model="importDialogVisible" title="导入教师" width="500px">
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
import { getTeacherList, createTeacher, updateTeacher, deleteTeacher, getClassList } from '@/api/teachers'
import { useUserStore } from '@/store/modules/user'
import { saveAs } from 'file-saver'
import { exportTeacherTemplate, importTeachers } from '@/api/teachers'

export default {
  name: 'TeacherManagement',
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
    const teacherList = ref([])
    const classList = ref([])
    const userStore = useUserStore()
    
    // 搜索表单
    const searchForm = reactive({
      name: '',
      employee_id: '',
      phone: '',
      position: ''
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
      employee_id: '',
      gender: 'female',
      position: '',
      phone: '',
      email: '',
      class_id: '',
      hire_date: '',
      notes: ''
    })
    
    // 导入表单数据
    const importFormData = reactive({
      file: null
    })
    
    // 表单验证规则
    const formRules = {
      name: [
        { required: true, message: '请输入教师姓名', trigger: 'blur' },
        { min: 1, max: 20, message: '长度在 1 到 20 个字符', trigger: 'blur' }
      ],
      gender: [
        { required: true, message: '请选择性别', trigger: 'change' }
      ],
      position: [
        { required: true, message: '请选择职位', trigger: 'change' }
      ],
      class_id: [
        { required: true, message: '请选择班级', trigger: 'change' }
      ],
      phone: [
        { pattern: /^1[3-9]\d{9}$/, message: '手机号码格式不正确', trigger: 'blur' }
      ]
    }
    
    // 导入表单验证规则
    const importFormRules = {
      file: [
        { required: true, message: '请选择要导入的文件', trigger: 'change' }
      ]
    }
    
    // 获取职位对应的标签类型
    const getPositionTag = (position) => {
      const tagMap = {
        'principal': 'danger',
        'head_teacher': 'primary',
        'assistant_teacher': 'success',
        'life_teacher': 'warning'
      }
      return tagMap[position] || 'info'
    }
    
    // 获取职位文本
    const getPositionText = (position) => {
      const textMap = {
        'principal': '园长',
        'head_teacher': '班主任',
        'assistant_teacher': '配班老师',
        'life_teacher': '生活老师'
      }
      return textMap[position] || position
    }
    
    // 获取教师列表
    const loadTeacherList = async () => {
      loading.value = true
      try {
        const params = {
          page: pagination.currentPage,
          page_size: pagination.pageSize,
          name: searchForm.name,
          employee_id: searchForm.employee_id,
          phone: searchForm.phone,
          position: searchForm.position
        }
        const res = await getTeacherList(params)
        
        // 根据后端实际返回格式处理数据
        if (res && res.results) {
          // DRF默认分页格式
          teacherList.value = res.results.items || res.results
          pagination.total = res.count || res.results.total
        } else if (res && Array.isArray(res)) {
          // 如果是数组格式，直接使用
          teacherList.value = res
          pagination.total = res.length
        } else if (res && res.data && Array.isArray(res.data)) {
          // 兼容之前的处理方式
          teacherList.value = res.data
          pagination.total = res.data.length
        } else if (res && res.data && res.data.results && Array.isArray(res.data.results)) {
          // 兼容之前的分页格式
          teacherList.value = res.data.results
          pagination.total = res.data.count || res.data.results.length
        } else if (res && res.data && Array.isArray(res.data.items)) {
          // 如果是带有items字段的对象格式
          teacherList.value = res.data.items
          pagination.total = res.data.total || res.data.items.length
        } else {
          // 如果没有返回数据，设置为空数组
          teacherList.value = []
          pagination.total = 0
        }
      } catch (error) {
        ElMessage.error('获取教师列表失败')
        console.error(error)
      } finally {
        loading.value = false
      }
    }
    
    // 获取班级列表
    const loadClassList = async () => {
      try {
        const res = await getClassList()
        
        // 根据后端实际返回格式处理数据
        if (res && res.results) {
          // DRF默认分页格式
          classList.value = res.results.items || res.results
        } else if (res && Array.isArray(res)) {
          // 如果是数组格式，直接使用
          classList.value = res
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
      loadTeacherList()
    }
    
    // 重置搜索
    const resetSearch = () => {
      Object.keys(searchForm).forEach(key => {
        searchForm[key] = ''
      })
      pagination.currentPage = 1
      loadTeacherList()
    }
    
    // 处理分页大小变化
    const handleSizeChange = (size) => {
      pagination.pageSize = size
      loadTeacherList()
    }
    
    // 处理页码变化
    const handleCurrentChange = (current) => {
      pagination.currentPage = current
      loadTeacherList()
    }
    
    // 处理创建
    const handleAdd = () => {
      dialogTitle.value = '新增教师'
      // 清空表单数据，确保不回填之前的编辑数据
      formData.id = ''
      formData.name = ''
      formData.employee_id = ''
      formData.gender = 'female'
      formData.position = ''
      formData.phone = ''
      formData.email = ''
      formData.class_id = ''
      formData.hire_date = ''
      formData.notes = ''
      dialogVisible.value = true
    }
    
    // 处理编辑
    const handleEdit = (row) => {
      dialogTitle.value = '编辑教师'
      // 填充表单数据
      Object.keys(formData).forEach(key => {
        if (key === 'class_id') {
          // 特殊处理班级ID字段，从classes数组中获取第一个班级ID
          if (row.classes && row.classes.length > 0) {
            formData[key] = row.classes[0].id || '';
          } else {
            formData[key] = '';
          }
        } else {
          formData[key] = row[key] || (key === 'class_id' ? '' : formData[key]);
        }
      });
      dialogVisible.value = true
    }
    
    // 处理删除
    const handleDelete = async (id) => {
      try {
        await ElMessageBox.confirm('确定要删除这个教师吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        
        await deleteTeacher(id)
        ElMessage.success('删除成功')
        loadTeacherList()
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error('删除失败: ' + (error.message || error))
        }
      }
    }
    
    // 提交表单
    const handleSubmit = async () => {
      if (!formRef.value) return
      try {
        await formRef.value.validate()
        
        // 准备提交数据
        const submitData = { ...formData }
        
        // 处理入职日期格式
        if (submitData.hire_date) {
          // 如果是日期对象，转换为 YYYY-MM-DD 格式
          if (submitData.hire_date instanceof Date) {
            const year = submitData.hire_date.getFullYear()
            const month = String(submitData.hire_date.getMonth() + 1).padStart(2, '0')
            const day = String(submitData.hire_date.getDate()).padStart(2, '0')
            submitData.hire_date = `${year}-${month}-${day}`
          }
        } else {
          // 如果入职日期为空，删除该字段避免传递空字符串给后端
          delete submitData.hire_date
        }
        
        // 如果是园长职位，清除班级ID
        if (submitData.position === 'principal') {
          submitData.class_id = null
        }
        
        if (formData.id) {
          // 编辑
          await updateTeacher(formData.id, submitData)
          ElMessage.success('更新成功')
        } else {
          // 新增
          await createTeacher(submitData)
          ElMessage.success('创建成功')
        }
        
        dialogVisible.value = false
        loadTeacherList()
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
    
    // 查看班级
    const viewClasses = (row) => {
      ElMessage.info('查看班级功能待实现')
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
        const response = await importTeachers(formData)
        
        // 检查是否有错误信息
        if (response && response.errors && response.errors.length > 0) {
          // 显示详细的错误信息
          let errorMsg = `导入失败:\n`
          response.errors.forEach(error => {
            errorMsg += `${error}\n`
          })
          ElMessage.error(errorMsg)
        } else if (response) {
          ElMessage.success(`导入成功！共导入${response.created_count}条记录`)
          importDialogVisible.value = false
          loadTeacherList() // 重新加载列表
        } else {
          ElMessage.error('导入失败')
        }
      } catch (error) {
        console.log('error', error)
        // 特别处理包含错误信息的响应
        if (error.response && error.response.data && error.response.data.errors) {
          let errorMsg = '导入失败:\n'
          error.response.data.errors.forEach(err => {
            errorMsg += `${err}\n`
          })
          ElMessage.error(errorMsg)
        } else if (error.response && error.response.data) {
          // 处理其他错误响应
          const data = error.response.data
          if (data.errors && Array.isArray(data.errors) && data.errors.length > 0) {
            let errorMsg = '导入失败:\n'
            data.errors.forEach(err => {
              errorMsg += `${err}\n`
            })
            ElMessage.error(errorMsg)
          } else if (data.error) {
            ElMessage.error('导入失败: ' + data.error)
          } else {
            ElMessage.error('导入失败: ' + (error.message || '网络错误'))
          }
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
        const response = await exportTeacherTemplate()
        const blob = new Blob([response], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
        saveAs(blob, `教师导入模板.xlsx`)
        ElMessage.success('模板下载成功')
      } catch (error) {
        ElMessage.error('模板下载失败: ' + (error.message || '网络错误'))
      }
    }
    
    // 初始加载
    onMounted(async () => {
      await Promise.all([
        loadTeacherList(),
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
      teacherList,
      classList,
      userStore,
      searchForm,
      pagination,
      formData,
      importFormData,
      formRules,
      importFormRules,
      getPositionTag,
      getPositionText,
      handleSearch,
      resetSearch,
      handleSizeChange,
      handleCurrentChange,
      handleAdd,
      handleEdit,
      handleDelete,
      handleSubmit,
      handleClose,
      viewClasses,
      handleImport,
      handleFileChange,
      handleImportSubmit,
      handleExportTemplate
    }
  }
}
</script>

<style scoped>
.teachers-container {
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

.search-bar :deep(.el-form-item .el-input) {
  width: 150px;
}

.search-bar :deep(.el-select) {
  width: 150px;
}

.teachers-position-select {
  width: 150px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>