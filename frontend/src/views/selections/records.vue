<template>
  <div class="selection-records-container">
    <div class="page-header">
      <h2>选区记录</h2>
      <p>管理幼儿选区记录</p>
    </div>
    
    <el-card class="search-card">
      <el-form :model="searchForm" label-width="80px" inline>
        <el-form-item label="幼儿姓名">
          <el-input v-model="searchForm.child_name" placeholder="请输入幼儿姓名" clearable />
        </el-form-item>
        <el-form-item label="选区">
          <el-select v-model="searchForm.selection_area_id" placeholder="请选择选区" clearable class="records-selection-area-select">
            <el-option
              v-for="item in selectionAreaList"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="所属班级">
          <el-select v-model="searchForm.class_id" placeholder="请选择班级" clearable class="records-class-select">
            <el-option
              v-for="item in classList"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="时间范围">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="resetSearch">重置</el-button>
          <el-button @click="handleExport">导出</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <el-card class="content-card">
      <template #header>
        <div class="card-header">
          <span>选区记录列表</span>
          <div class="card-actions">
            <el-button type="primary" @click="handleCreate">新增记录</el-button>
          </div>
        </div>
      </template>
      
      <el-table
        v-loading="loading"
        :data="selectionRecordsData"
        stripe
      >
        <el-table-column prop="child_name" label="幼儿姓名" min-width="100" />
        <el-table-column prop="selection_area_name" label="选区名称" min-width="120" />
        <el-table-column prop="class_name" label="所属班级" min-width="120" />
        <el-table-column prop="select_time" label="选择时间" width="180" />
        <el-table-column prop="notes" label="备注" min-width="150" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-popconfirm
              title="确定要删除这条记录吗？"
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
        <el-form-item label="幼儿" prop="child_id">
          <el-select v-model="formData.child_id" placeholder="请选择幼儿" style="width: 100%">
            <el-option
              v-for="item in childList"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="选区" prop="selection_area_id">
          <el-select v-model="formData.selection_area_id" placeholder="请选择选区" style="width: 100%">
            <el-option
              v-for="item in selectionAreaList"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="选择时间" prop="select_time">
          <el-date-picker
            v-model="formData.select_time"
            type="datetime"
            placeholder="请选择选择时间"
            value-format="YYYY-MM-DD HH:mm:ss"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="备注" prop="notes">
          <el-input
            v-model="formData.notes"
            type="textarea"
            :rows="3"
            placeholder="请输入备注信息"
          />
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
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { saveAs } from 'file-saver'
import { 
  getSelectionRecords,
  createSelectionRecord,
  updateSelectionRecord,
  deleteSelectionRecord,
  getSelectionAreas,
  exportSelectionRecords
} from '@/api/selections'
import childApi from '@/api/children'
import classApi from '@/api/classes'

// 状态管理
const loading = ref(false)
const dialogVisible = ref(false)
const dialogTitle = ref('')
const formRef = ref(null)
const selectionRecordsData = ref([])
const selectedRows = ref([])
const selectionAreaList = ref([])
const childList = ref([])
const classList = ref([])
const dateRange = ref([])

// 查询条件
const searchForm = reactive({
  child_name: '',
  selection_area_id: '',
  class_id: '' // 新增所属班级查询条件
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
  child_id: '',
  selection_area_id: '',
  select_time: '',
  notes: ''
})

// 表单验证规则
const formRules = reactive({
  child_id: [
    { required: true, message: '请选择幼儿', trigger: 'change' }
  ],
  selection_area_id: [
    { required: true, message: '请选择选区', trigger: 'change' }
  ],
  select_time: [
    { required: true, message: '请选择选择时间', trigger: 'blur' }
  ]
})

// 获取选区记录列表
const getSelectionRecordsList = async () => {
  loading.value = true
  try {
    const params = {
      ...searchForm,
      page: pagination.currentPage,
      page_size: pagination.pageSize
    }
    
    // 添加日期范围查询
    if (dateRange.value && dateRange.value.length === 2) {
      params.date_from = dateRange.value[0]
      params.date_to = dateRange.value[1]
    }
    
    const res = await getSelectionRecords(params)
    // 处理分页数据结构的变化
    if (res && res.results) {
      // DRF默认分页格式
      selectionRecordsData.value = res.results.items || res.results
      pagination.total = res.count || res.results.total
    } else {
      // 兼容旧格式
      selectionRecordsData.value = res.items
      pagination.total = res.total
    }
  } catch (error) {
    ElMessage.error('获取选区记录列表失败')
  } finally {
    loading.value = false
  }
}

// 获取选区列表
const getSelectionAreaList = async () => {
  try {
    const res = await getSelectionAreas({ page_size: 100 })
    // 处理分页数据结构的变化
    if (res && res.results) {
      // DRF默认分页格式
      selectionAreaList.value = res.results.items || res.results
    } else {
      // 兼容旧格式
      selectionAreaList.value = res.items || res.data || res
    }
  } catch (error) {
    ElMessage.error('获取选区列表失败')
  }
}

// 获取班级列表
const getClassList = async () => {
  try {
    const res = await classApi.getClasses({ page_size: 100 })
    // 处理分页数据结构的变化
    if (res && res.results) {
      // DRF默认分页格式
      classList.value = res.results.items || res.results
    } else {
      // 兼容旧格式
      classList.value = res.items || res.data || res
    }
  } catch (error) {
    ElMessage.error('获取班级列表失败')
  }
}

// 获取幼儿列表
const getChildList = async () => {
  try {
    const res = await childApi.getChildrenList({ page_size: 200 })
    // 处理分页数据结构的变化
    if (res && res.results) {
      // DRF默认分页格式
      childList.value = res.results.items || res.results
    } else {
      // 兼容旧格式
      childList.value = res.items || res.data || res
    }
  } catch (error) {
    ElMessage.error('获取幼儿列表失败')
  }
}

// 处理搜索
const handleSearch = () => {
  pagination.currentPage = 1
  getSelectionRecordsList()
}

// 重置搜索
const resetSearch = () => {
  Object.keys(searchForm).forEach(key => {
    searchForm[key] = ''
  })
  dateRange.value = []
  pagination.currentPage = 1
  getSelectionRecordsList()
}

// 处理导出
const handleExport = async () => {
  try {
    const params = {
      ...searchForm
    }
    
    // 添加日期范围查询
    if (dateRange.value && dateRange.value.length === 2) {
      params.date_from = dateRange.value[0]
      params.date_to = dateRange.value[1]
    }
    
    const res = await exportSelectionRecords(params)
    const blob = new Blob([res], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
    saveAs(blob, `选区记录_${new Date().toISOString().slice(0, 10)}.xlsx`)
    ElMessage.success('导出成功')
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('导出失败：' + (error.message || '未知错误'))
  }
}

// 处理分页大小变化
const handleSizeChange = (size) => {
  pagination.pageSize = size
  getSelectionRecordsList()
}

// 处理页码变化
const handleCurrentChange = (current) => {
  pagination.currentPage = current
  getSelectionRecordsList()
}

// 处理选择变化
const handleSelectionChange = (rows) => {
  selectedRows.value = rows
}

// 处理创建
const handleCreate = async () => {
  dialogTitle.value = '新增选区记录'
  // 先重置表单确保清空所有数据
  resetForm()
  // 确保数据已加载
  if (!childList.value || childList.value.length === 0) {
    await getChildList()
  }
  if (!selectionAreaList.value || selectionAreaList.value.length === 0) {
    await getSelectionAreaList()
  }
  dialogVisible.value = true
}

// 处理编辑
const handleEdit = async (row) => {
  dialogTitle.value = '编辑选区记录'
  // 确保数据已加载
  if (!childList.value || childList.value.length === 0) {
    await getChildList()
  }
  if (!selectionAreaList.value || selectionAreaList.value.length === 0) {
    await getSelectionAreaList()
  }
  
  // 填充表单数据
  formData.id = row.id
  formData.child_id = row.child
  formData.selection_area_id = row.selection_area
  formData.select_time = row.select_time
  formData.notes = row.notes
  dialogVisible.value = true
}

// 处理删除
const handleDelete = async (id) => {
  try {
    await deleteSelectionRecord(id)
    ElMessage.success('删除成功')
    getSelectionRecordsList()
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

// 批量删除
const handleBatchDelete = async () => {
  // 已删除批量删除功能
  ElMessage.info('批量删除功能已移除')
}

// 重置表单
const resetForm = () => {
  formData.id = ''
  formData.child_id = ''
  formData.selection_area_id = ''
  formData.select_time = ''
  formData.notes = ''
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
    
    const data = {
      child_id: formData.child_id,
      selection_area_id: formData.selection_area_id,
      select_time: formData.select_time,
      notes: formData.notes
    }

    if (formData.id) {
      // 更新
      await updateSelectionRecord(formData.id, data)
      ElMessage.success('更新成功')
    } else {
      // 创建
      await createSelectionRecord(data)
      ElMessage.success('创建成功')
    }
    
    dialogVisible.value = false
    getSelectionRecordsList()
  } catch (error) {
    console.error('提交失败:', error)
    ElMessage.error('操作失败：' + (error.message || '未知错误'))
  }
}

// 组件挂载时获取数据
onMounted(() => {
  getSelectionAreaList()
  getChildList()
  getClassList() // 获取班级列表
  getSelectionRecordsList()
})
</script>

<style scoped>
.selection-records-container {
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

.records-selection-area-select,
.records-class-select {
  width: 100%;
}
</style>