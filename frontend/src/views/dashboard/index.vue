<template>
  <div class="dashboard">
    <div class="page-header">
      <h1>欢迎回来！{{ username }}</h1>
      <p>{{ currentTime }}</p>
    </div>
    
    <div class="stats-card">
      <div class="stats-grid">
        <el-card class="stat-item">
          <div class="stat-icon blue">
            <el-icon><User /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ totalStudents }}</div>
            <div class="stat-label">幼儿总数</div>
          </div>
        </el-card>
        
        <el-card class="stat-item">
          <div class="stat-icon green">
            <el-icon><School /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ totalClasses }}</div>
            <div class="stat-label">班级数量</div>
          </div>
        </el-card>
        
        <el-card class="stat-item">
          <div class="stat-icon orange">
            <el-icon><Avatar /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ totalTeachers }}</div>
            <div class="stat-label">教师总数</div>
          </div>
        </el-card>
        
        <el-card class="stat-item">
          <div class="stat-icon purple">
            <el-icon><Present /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ attendanceRate }}%</div>
            <div class="stat-label">今日已选区率</div>
          </div>
        </el-card>
      </div>
    </div>
    
    <!-- 选区统计卡片 -->
    <div class="selection-stats">
      <div class="section-header">
        <h3>选区统计</h3>
        <el-button type="primary" size="small" @click="fetchDashboardData">刷新数据</el-button>
      </div>
      <div class="stats-grid">
        <el-card class="stat-item">
          <div class="stat-icon cyan">
            <el-icon><Grid /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ selectionStats.selection_areas }}</div>
            <div class="stat-label">选区总数</div>
          </div>
        </el-card>
        
        <el-card class="stat-item">
          <div class="stat-icon blue">
            <el-icon><Check /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ selectionStats.assigned_children }}</div>
            <div class="stat-label">已分配选区幼儿</div>
          </div>
        </el-card>
        
        <el-card class="stat-item">
          <div class="stat-icon orange">
            <el-icon><Warning /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ selectionStats.unassigned_children }}</div>
            <div class="stat-label">未分配选区幼儿</div>
          </div>
        </el-card>
      </div>
    </div>
    
    <div class="charts-section">
      <el-row :gutter="20">
        <el-col :span="12">
          <el-card class="chart-card">
            <template #header>
              <div class="card-header">
                <span>近7天已分配选区的幼儿数</span>
                <el-select v-model="chartRange" class="chart-range">
                  <el-option label="近7天" value="7d"></el-option>
                  <el-option label="近30天" value="30d"></el-option>
                  <el-option label="近90天" value="90d"></el-option>
                </el-select>
              </div>
            </template>
            <div class="chart-container">
              <canvas ref="studentsChart"></canvas>
            </div>
          </el-card>
        </el-col>
        
        <el-col :span="6">
          <el-card class="chart-card">
            <template #header>
              <div class="card-header">
                <span>班级人数分布</span>
              </div>
            </template>
            <div class="chart-container">
              <canvas ref="classesChart"></canvas>
            </div>
          </el-card>
        </el-col>
        
        <el-col :span="6">
          <el-card class="chart-card">
            <template #header>
              <div class="card-header">
                <span>选区幼儿分布</span>
              </div>
            </template>
            <div class="chart-container">
              <canvas ref="selectionChart"></canvas>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
    
    <!-- 选区活动记录 -->
    <div class="selection-activities">
      <el-card>
        <template #header>
          <div class="card-header">
            <span>最近选区活动</span>
            <el-button type="primary" size="small" @click="fetchDashboardData">刷新</el-button>
          </div>
        </template>
        <el-table v-loading="loading" :data="realSelectionActivities" stripe>
          <el-table-column prop="child_name" label="幼儿姓名" width="120"></el-table-column>
          <el-table-column prop="selection_area_name" label="选区名称" width="150"></el-table-column>
          <el-table-column prop="class_name" label="班级" width="120"></el-table-column>
          <el-table-column prop="select_time" label="选择时间" width="180">
            <template #default="{ row }">
              {{ formatDate(row.select_time) }}
            </template>
          </el-table-column>
          <el-table-column prop="is_active" label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="row.is_active ? 'success' : 'info'">
                {{ row.is_active ? '进行中' : '已结束' }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { useUserStore } from '@/store/modules/user'
import { ElMessage } from 'element-plus'
import { User, School, Avatar, Present, CaretTop, CaretBottom, Grid, Check, Warning } from '@element-plus/icons-vue'
import Chart from 'chart.js/auto'
import { getRecentActivities, getDashboardStats } from '@/api/selections'

// 状态管理
const userStore = useUserStore()

// 计算属性
const username = computed(() => userStore.userInfo.nickname || userStore.userInfo.username || '管理员')

// 实时时间数据
const currentTime = ref('')

// 实时更新时间
const updateCurrentTime = () => {
  const now = new Date()
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const day = String(now.getDate()).padStart(2, '0')
  const hour = String(now.getHours()).padStart(2, '0')
  const minute = String(now.getMinutes()).padStart(2, '0')
  const second = String(now.getSeconds()).padStart(2, '0')
  
  const weekdays = ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六']
  const weekday = weekdays[now.getDay()]
  
  currentTime.value = `${year}年${month}月${day}日 ${weekday} ${hour}:${minute}:${second}`
}

// 响应式数据
const chartRange = ref('7d')
const activities = ref([])
const studentsChart = ref(null)
const classesChart = ref(null)
const selectionChart = ref(null)
let studentsChartInstance = null
let classesChartInstance = null
let selectionChartInstance = null

// 统计数据
const totalStudents = ref(0)
const totalClasses = ref(0)
const totalTeachers = ref(0)
const attendanceRate = ref(0)
const studentsChange = ref(0)
const classesChange = ref(0)
const teachersChange = ref(0)
const attendanceChange = ref(0)

// 选区统计数据
const selectionStats = ref({
  total_children: 0,
  assigned_children: 0,
  unassigned_children: 0,
  selection_areas: 0
})

// 选区活动数据
const selectionActivities = ref([])
const realSelectionActivities = ref([]) // 真实的选区活动数据
const loading = ref(false)

// 班级人数分布数据
const classDistributionData = ref({
  labels: [],
  data: []
})

// 获取仪表盘数据
const fetchDashboardData = async () => {
  loading.value = true
  try {
    // 获取统计数据
    // 修改为使用 selections 接口获取仪表盘数据
    const statsRes = await getDashboardStats({ days: chartRange.value === '7d' ? 7 : chartRange.value === '30d' ? 30 : 90 })
    
    // 获取最近的选区活动记录
    const activitiesRes = await getRecentActivities({ limit: 10 })
    
    // 更新选区统计数据
    const dashboardData = statsRes
    
    // 更新其他统计数据
    totalStudents.value = dashboardData.total_children || 0
    totalClasses.value = dashboardData.total_classes || 0
    totalTeachers.value = dashboardData.total_teachers || 0
    
    // 计算今日已选区率（出勤率）
    if (dashboardData.total_children > 0) {
      attendanceRate.value = Math.round((dashboardData.assigned_children / dashboardData.total_children) * 100)
    } else {
      attendanceRate.value = 0
    }
    
    // 计算变化率，基于selection_trend数据
    if (dashboardData.selection_trend && dashboardData.selection_trend.length >= 2) {
      const latestCount = dashboardData.selection_trend[dashboardData.selection_trend.length - 1].count
      const previousCount = dashboardData.selection_trend[dashboardData.selection_trend.length - 2].count
      if (previousCount > 0) {
        studentsChange.value = Math.round(((latestCount - previousCount) / previousCount) * 100)
      } else if (latestCount > 0) {
        studentsChange.value = 100 // 从0到有数据，增长100%
      } else {
        studentsChange.value = 0 // 都为0，无变化
      }
    } else {
      studentsChange.value = 0 // 默认无变化
    }
    
    // 移除其他统计项的变化率计算（因为我们不再显示它们）
    classesChange.value = 0 // 默认无变化
    teachersChange.value = 0 // 默认无变化
    attendanceChange.value = 0 // 默认无变化
    
    // 更新选区统计数据
    selectionStats.value = {
      total_children: dashboardData.total_children || 0,
      assigned_children: dashboardData.assigned_children || 0,
      unassigned_children: dashboardData.unassigned_children || 0,
      selection_areas: dashboardData.total_selection_areas || 0
    }
    
    // 更新班级人数分布数据
    if (dashboardData.class_statistics) {
      classDistributionData.value.labels = dashboardData.class_statistics.map(item => item.class_name)
      classDistributionData.value.data = dashboardData.class_statistics.map(item => item.student_count)
    } else {
      // 如果没有班级统计数据，设置为空数组
      classDistributionData.value.labels = []
      classDistributionData.value.data = []
    }
    
    // 更新选区活动数据，使用真实的趋势数据
    if (dashboardData.selection_trend) {
      selectionActivities.value = dashboardData.selection_trend.map(item => ({
        child_name: '示例幼儿',
        selection_area_name: '示例选区',
        start_time: item.date,
        duration: item.count * 36, // 将数量转换为秒数用于显示
        count: item.count // 保存原始数量数据
      }))
    }
    
    // 更新真实的选区活动数据
    if (activitiesRes && activitiesRes.data) {
      realSelectionActivities.value = activitiesRes.data
    }
    
    // 更新图表数据
    nextTick(() => {
      initStudentsChart()
      initClassesChart()
      initSelectionChart()
    })
  } catch (error) {
    console.error('获取仪表盘数据失败:', error)
    ElMessage.error('获取仪表盘数据失败: ' + (error.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

// 格式化时长
const formatDuration = (seconds) => {
  if (!seconds) return '0秒'
  
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = seconds % 60
  
  let result = ''
  if (hours > 0) {
    result += `${hours}小时`
  }
  if (minutes > 0) {
    result += `${minutes}分钟`
  }
  if (secs > 0 || result === '') {
    result += `${secs}秒`
  }
  
  return result
}

// 格式化日期时间
const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hour = String(date.getHours()).padStart(2, '0')
  const minute = String(date.getMinutes()).padStart(2, '0')
  const second = String(date.getSeconds()).padStart(2, '0')
  return `${year}-${month}-${day} ${hour}:${minute}:${second}`
}

// 初始化学生图表
function initStudentsChart() {
  if (!studentsChart.value) return
  
  const ctx = studentsChart.value.getContext('2d')
  
  // 使用真实的趋势数据
  let labels = []
  let data = []
  
  if (selectionActivities.value && selectionActivities.value.length > 0) {
    // 使用真实的趋势数据
    labels = selectionActivities.value.map(activity => activity.start_time)
    // 修复：直接使用真实的count数据，而不是转换duration
    data = selectionActivities.value.map(activity => activity.count)
  } else {
    // 默认数据
    labels = chartRange.value === '7d' 
      ? Array.from({ length: 7 }, (_, i) => `${i + 1}日`) 
      : chartRange.value === '30d' 
        ? Array.from({ length: 30 }, (_, i) => `${i + 1}日`) 
        : Array.from({ length: 90 }, (_, i) => `${Math.floor(i / 30) + 1}月${(i % 30) + 1}日`)
        
    data = labels.map(() => Math.floor(Math.random() * 50) + 230)
  }
  
  // 销毁旧图表
  if (studentsChartInstance) {
    studentsChartInstance.destroy()
  }
  
  studentsChartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels,
      datasets: [{
        label: '幼儿人数',
        data,
        borderColor: '#1890ff',
        backgroundColor: 'rgba(24, 144, 255, 0.1)',
        fill: true,
        tension: 0.3,
        pointRadius: 4,
        pointBackgroundColor: '#1890ff',
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false
        },
        tooltip: {
          mode: 'index',
          intersect: false
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          grid: {
            color: 'rgba(0, 0, 0, 0.05)'
          }
        },
        x: {
          grid: {
            display: false
          }
        }
      }
    }
  })
}

// 初始化班级图表
function initClassesChart() {
  if (!classesChart.value) return
  
  const ctx = classesChart.value.getContext('2d')
  
  // 使用真实的班级统计数据
  const labels = classDistributionData.value.labels
  const data = classDistributionData.value.data
  
  // 销毁旧图表
  if (classesChartInstance) {
    classesChartInstance.destroy()
  }
  
  classesChartInstance = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels,
      datasets: [{
        data,
        backgroundColor: [
          '#1890ff', '#52c41a', '#faad14', '#f5222d',
          '#722ed1', '#13c2c2', '#eb2f96', '#fa8c16'
        ],
        borderWidth: 0
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'bottom',
          labels: {
            padding: 15,
            boxWidth: 10
          }
        }
      },
      cutout: '60%'
    }
  })
}

// 刷新活动列表
function refreshActivities() {
  fetchDashboardData()
}

// 初始化选区分布图表
function initSelectionChart() {
  if (!selectionChart.value) return
  
  const ctx = selectionChart.value.getContext('2d')
  
  // 使用真实数据构建选区分布图表
  const labels = ['已分配', '未分配']
  const data = [
    selectionStats.value.assigned_children || 0,
    selectionStats.value.unassigned_children || 0
  ]
  
  // 销毁旧图表
  if (selectionChartInstance) {
    selectionChartInstance.destroy()
  }
  
  selectionChartInstance = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels,
      datasets: [{
        data,
        backgroundColor: [
          '#1890ff', '#faad14'
        ],
        borderWidth: 0
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'bottom',
          labels: {
            padding: 15,
            boxWidth: 10
          }
        }
      },
      cutout: '60%' // 保持与班级图表相同的样式
    }
  })
}

// 监听图表范围变化
watch(chartRange, () => {
  fetchDashboardData()
})

// 生命周期
onMounted(() => {
  // 初始化时间显示
  updateCurrentTime()
  // 每秒更新时间
  setInterval(updateCurrentTime, 1000)
  
  // 获取仪表盘数据
  fetchDashboardData()
  
  // 初始化图表
  nextTick(() => {
    initStudentsChart()
    initClassesChart()
    initSelectionChart()
  })
})
</script>

<style scoped>
.dashboard {
  padding: 20px;
}

.page-header {
  margin-bottom: 30px;
}

.page-header h1 {
  font-size: 28px;
  margin-bottom: 10px;
  color: #303133;
}

.page-header p {
  font-size: 16px;
  color: #606266;
}

.stats-card {
  margin-bottom: 30px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.stat-item {
  display: flex;
  align-items: center;
  padding: 20px;
  transition: all 0.3s ease;
}

.stat-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: #fff;
  margin-right: 20px;
}

.stat-icon.blue {
  background-color: #1890ff;
}

.stat-icon.green {
  background-color: #52c41a;
}

.stat-icon.orange {
  background-color: #faad14;
}

.stat-icon.purple {
  background-color: #722ed1;
}

.stat-icon.cyan {
  background-color: #13c2c2;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  color: #606266;
}

.stat-change {
  font-size: 14px;
  font-weight: 500;
}

.stat-change.positive {
  color: #52c41a;
}

.stat-change.negative {
  color: #f5222d;
}

.charts-section {
  margin-bottom: 30px;
}

.chart-card {
  height: 400px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 16px;
  font-weight: 500;
  color: #303133;
}

.chart-range {
  width: 120px;
}

.chart-container {
  height: calc(100% - 60px);
  position: relative;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h3 {
  margin: 0;
  font-size: 18px;
  color: #303133;
}

.selection-stats {
  margin-bottom: 30px;
}

.recent-activities {
  margin-bottom: 30px;
}

.selection-activities {
  margin-bottom: 30px;
}

.text-green {
  color: #52c41a;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .chart-card {
    height: 300px;
  }
}
</style>