<template>
  <div class="kindergarten-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>幼儿园管理</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            新增幼儿园
          </el-button>
        </div>
      </template>
      
      <!-- 搜索栏 -->
      <div class="search-bar">
        <el-form :inline="true" :model="searchForm" size="small">
          <el-form-item label="幼儿园名称">
            <el-input v-model="searchForm.name" placeholder="请输入幼儿园名称" clearable />
          </el-form-item>
          <el-form-item label="地区">
            <el-input v-model="searchForm.region" placeholder="请输入地区" clearable />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">查询</el-button>
            <el-button @click="resetSearch">重置</el-button>
          </el-form-item>
        </el-form>
      </div>
      
      <!-- 数据表格 -->
      <el-table v-loading="loading" :data="kindergartenList" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="幼儿园名称" />
        <el-table-column prop="region" label="地区" />
        <el-table-column prop="address" label="地址" />
        <el-table-column prop="contact_person" label="联系人" />
        <el-table-column prop="contact_phone" label="联系电话" />
        <el-table-column prop="student_count" label="幼儿人数" width="100" />
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="scope">
            <el-button size="small" @click="handleEdit(scope.row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="pagination.currentPage"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="pagination.total"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
    
    <!-- 新增/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px">
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="120px">
        <el-form-item label="幼儿园名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入幼儿园名称" />
        </el-form-item>
        <el-form-item label="地区" prop="region">
          <el-input v-model="formData.region" placeholder="请输入地区" />
        </el-form-item>
        <el-form-item label="地址" prop="address">
          <el-input v-model="formData.address" placeholder="请输入详细地址" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="联系人" prop="contact_person">
          <el-input v-model="formData.contact_person" placeholder="请输入联系人姓名" />
        </el-form-item>
        <el-form-item label="联系电话" prop="contact_phone">
          <el-input v-model="formData.contact_phone" placeholder="请输入联系电话" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { getKindergartenList, createKindergarten, updateKindergarten, deleteKindergarten } from '@/api/kindergarten'

export default {
  name: 'KindergartenManagement',
  components: {
    Plus
  },
  setup() {
    // 状态定义
    const loading = ref(false)
    const dialogVisible = ref(false)
    const dialogTitle = ref('')
    const formRef = ref()
    const kindergartenList = ref([])
    
    // 搜索表单
    const searchForm = reactive({
      name: '',
      region: ''
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
      region: '',
      address: '',
      contact_person: '',
      contact_phone: ''
    })
    
    // 表单验证规则
    const formRules = {
      name: [
        { required: true, message: '请输入幼儿园名称', trigger: 'blur' },
        { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
      ]
    }
    
    // 获取幼儿园列表
    const loadKindergartenList = async () => {
      loading.value = true
      try {
        const params = {
          page: pagination.currentPage,
          page_size: pagination.pageSize
        }
        
        // 添加搜索参数 - 支持name和region搜索
        if (searchForm.name) {
          params.name = searchForm.name
        } else if (searchForm.region) {
          params.region = searchForm.region
        }
        
        const res = await getKindergartenList(params)
        // 检查响应数据结构
        if (res && res.results) {
          // DRF默认分页格式
          kindergartenList.value = res.results.items || res.results
          pagination.total = res.count || res.results.total
        } else if (res && res.data) {
          kindergartenList.value = res.data.items || res.data
          pagination.total = res.data.total || res.data.length || 0
        } else {
          kindergartenList.value = res.items || res
          pagination.total = res.total || res.length || 0
        }
      } catch (error) {
        ElMessage.error('获取幼儿园列表失败: ' + (error.message || '未知错误'))
        console.error(error)
      } finally {
        loading.value = false
      }
    }
    
    // 搜索
    const handleSearch = () => {
      pagination.currentPage = 1
      loadKindergartenList()
    }
    
    // 重置搜索
    const resetSearch = () => {
      searchForm.name = ''
      searchForm.region = ''
      pagination.currentPage = 1
      loadKindergartenList()
    }
    
    // 分页大小改变
    const handleSizeChange = (size) => {
      pagination.pageSize = size
      loadKindergartenList()
    }
    
    // 页码改变
    const handleCurrentChange = (current) => {
      pagination.currentPage = current
      loadKindergartenList()
    }
    
    // 新增幼儿园
    const handleAdd = () => {
      dialogTitle.value = '新增幼儿园'
      formData.id = ''
      formData.name = ''
      formData.region = ''
      formData.address = ''
      formData.contact_person = ''
      formData.contact_phone = ''
      formData.status = 'active'
      dialogVisible.value = true
    }
    
    // 编辑幼儿园
    const handleEdit = (row) => {
      dialogTitle.value = '编辑幼儿园'
      Object.assign(formData, row)
      dialogVisible.value = true
    }
    
    // 删除幼儿园
    const handleDelete = (row) => {
      ElMessageBox.confirm(`确定要删除幼儿园「${row.name}」吗？`, '警告', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(async () => {
        try {
          await deleteKindergarten(row.id)
          ElMessage.success('删除成功')
          loadKindergartenList()
        } catch (error) {
          ElMessage.error('删除失败')
        }
      }).catch(() => {
        // 取消删除
      })
    }
    
    // 切换状态
    const handleToggleStatus = async (row) => {
      try {
        await toggleKindergartenStatus(row.id)
        ElMessage.success('操作成功')
        loadKindergartenList()
      } catch (error) {
        ElMessage.error('操作失败')
      }
    }
    
    // 提交表单
    const handleSubmit = async () => {
      if (!formRef.value) return
      try {
        await formRef.value.validate()
        
        if (formData.id) {
          // 编辑
          await updateKindergarten(formData.id, formData)
          ElMessage.success('更新成功')
        } else {
          // 新增
          await createKindergarten(formData)
          ElMessage.success('创建成功')
        }
        
        dialogVisible.value = false
        loadKindergartenList()
      } catch (error) {
        // 验证失败或请求失败
        if (error !== false) { // 排除验证失败的情况
          ElMessage.error('操作失败')
        }
      }
    }
    
    // 初始加载
    onMounted(() => {
      loadKindergartenList()
    })
    
    return {
      loading,
      dialogVisible,
      dialogTitle,
      formRef,
      kindergartenList,
      searchForm,
      pagination,
      formData,
      formRules,
      handleSearch,
      resetSearch,
      handleSizeChange,
      handleCurrentChange,
      handleAdd,
      handleEdit,
      handleDelete,
      handleSubmit
    }
  }
}
</script>

<style scoped>
.kindergarten-container {
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

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>