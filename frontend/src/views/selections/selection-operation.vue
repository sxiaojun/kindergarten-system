<template>
  <div class="selection-operation-container" ref="containerRef">
    <div class="page-header">
      <h2>幼儿选区操作</h2>
      <p>通过拖拽方式为幼儿分配选区</p>
      
      <!-- 班级选择器 -->
      <div class="class-selector-wrapper">
        <el-form :model="formModel" label-width="80px" inline>
          <el-form-item label="选择班级">
            <el-select 
              v-model="selectedClassId" 
              placeholder="请选择班级" 
              @change="handleClassChange" 
              clearable
              :key="selectKey"
              :popper-append-to-body="false"
              :teleported="false"
              placement="bottom-start"
              style="width: 200px;"
              :popper-class="isFullscreen ? 'fullscreen-select-popper' : 'normal-select-popper'"
            >
              <el-option
                v-for="item in classList"
                :key="item.id"
                :label="item.name"
                :value="item.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button 
              :icon="isFullscreen ? 'full-screen-exit' : 'full-screen'" 
              @click="toggleFullscreen">
              {{ isFullscreen ? '退出全屏' : '全屏显示' }}
            </el-button>
          </el-form-item>
        </el-form>
      </div>
    </div>
    
    <!-- 主要内容区域 -->
    
    <!-- 全屏模式下用于放置下拉框的容器 -->
    <div v-if="isFullscreen" class="fullscreen-dropdown-container" id="fullscreenDropdownContainer"></div>
    
    <!-- 解决全屏模式下班级选择器被遮挡问题的特殊处理 -->
    <div v-if="isFullscreen" ref="dropdownPlaceholder" style="position: fixed; z-index: 10003; top: 60px; left: 20px;"></div>
    
    <el-card v-loading="loading" class="content-card">
      <template #header>
        <div class="card-header">
          <span>选区分配</span>
          <div class="stats-info">
            总人数: {{ totalChildren }} | 已分配: {{ assignedChildrenCount }} | 未分配: {{ unassignedChildren.length }}
          </div>
        </div>
      </template>
      
      <div class="selection-operation-content">
        <!-- 未分配幼儿区域 -->
        <div class="unassigned-section">
          <h3>未分配幼儿</h3>
          <div 
            class="unassigned-area"
            :class="{ 'drag-over': dragOverSource }"
            @dragenter.prevent="handleDragEnter('source')"
            @dragleave.prevent="handleDragLeave('source')"
            @dragover.prevent
            @drop.prevent="handleDropToSource"
            @touchstart="handleTouchStart($event, 'source')"
            @touchmove="handleTouchMove"
            @touchend="handleTouchEnd($event, 'source')"
            @touchcancel="handleTouchCancel"
          >
            <div class="children-list">
              <div
                v-for="child in unassignedChildren"
                :key="child.id"
                class="child-item"
                draggable="true"
                @dragstart="handleDragStart($event, 'child', child)"
                @dragend="handleDragEnd"
                @touchstart="handleTouchStart($event, 'child', child)"
                @touchmove="handleTouchMove"
                @touchend="handleTouchEnd($event, 'source')"
                @touchcancel="handleTouchCancel"
              >
                <div class="child-avatar">
                  <el-avatar :size="48" :src="child.avatar">{{ child.name.charAt(0) }}</el-avatar>
                </div>
                <div class="child-name">{{ child.name }}</div>
              </div>
            </div>
            
            <!-- 添加炫酷的背景效果 -->
            <div class="unassigned-background-effects">
              <div class="nebula" v-for="i in 2" :key="'nebula'+i"></div>
              <div class="floating-particle" v-for="i in 50" :key="i"></div>
              <div class="glowing-orb" v-for="i in 5" :key="'orb'+i"></div>
              <div class="pulse-ring" v-for="i in 4" :key="'ring'+i"></div>
            </div>
          </div>
        </div>
        
        <!-- 选区列表区域 -->
        <div class="selection-areas-section">
          <h3>选区列表</h3>
          <div class="selection-areas" ref="selectionAreasContainer">
            <div
              v-for="area in selectionAreas"
              :key="area.id"
              class="selection-area"
              :class="{ 'drag-over': dragOverTarget === area.id }"
              :data-area-id="area.id"
              @dragenter.prevent="handleDragEnter('target', area.id)"
              @dragleave.prevent="handleDragLeave('target')"
              @dragover.prevent
              @drop.prevent="handleDropToArea(area.id)"
              @touchstart="handleTouchStart($event, 'area', area)"
              @touchmove="handleTouchMove"
              @touchend="handleTouchEnd($event, 'target', area.id)"
              @touchcancel="handleTouchCancel"
            >
              <!-- 黑洞动画效果 -->
              <div class="black-hole-container">
                <div class="black-hole">
                  <div class="black-hole-core"></div>
                  <div class="black-hole-ring ring-1"></div>
                  <div class="black-hole-ring ring-2"></div>
                  <div class="black-hole-ring ring-3"></div>
                  <div class="black-hole-accretion-disk"></div>
                  <div class="black-hole-swirl swirl-1"></div>
                  <div class="black-hole-swirl swirl-2"></div>
                  <div class="black-hole-swirl swirl-3"></div>
                  <div class="black-hole-particle" v-for="i in 12" :key="i"></div>
                  
                  <!-- 吸入的选区名称 -->
                  <div class="area-name-infalling" :style="{ 
                    '--start-x': getRandomStartPosition('x'),
                    '--start-y': getRandomStartPosition('y'),
                    animationDelay: i * 0.05 + 's'
                  }" v-for="i in 25" :key="i">
                    {{ area.name }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  getSelectionAreas,
  getSelectionRecords,
  createSelectionRecord,
  updateSelectionRecord,
  deleteSelectionRecord
} from '@/api/selections'
import childApi from '@/api/children'
import classApi from '@/api/classes'

// 状态管理
const loading = ref(false)
const selectedClassId = ref('')
const selectKey = ref(0) // 用于强制刷新select组件
const containerRef = ref(null) // 容器引用
const formModel = reactive({
  selectedClassId: ''
})
const classList = ref([])
const selectionAreas = ref([])
const allChildren = ref([])
const assignedChildren = ref([])
const dragOverSource = ref(false)
const dragOverTarget = ref(null)
const dragData = ref(null)
const isFullscreen = ref(false)
const fullscreenElement = ref(null)
const dropdownPlaceholder = ref(null)

// 获取随机位置函数
const getRandomPosition = (type) => {
  if (type === 'top') {
    // 随机生成顶部或底部位置
    return Math.random() > 0.5 ? '-20px' : '100%'
  } else {
    // 随机生成左侧或右侧位置
    return Math.random() * 100 + '%'
  }
}

// 获取随机起始位置
const getRandomStartPosition = (axis) => {
  if (axis === 'x') {
    // 生成-200px到容器宽度+200px之间的随机值
    return (Math.random() * 400 - 200) + 'px'
  } else {
    // 生成-200px到容器高度+200px之间的随机值
    return (Math.random() * 400 - 200) + 'px'
  }
}

// 获取随机字体大小
const getRandomFontSize = () => {
  const sizes = ['16px', '18px', '20px', '22px', '24px']
  return sizes[Math.floor(Math.random() * sizes.length)]
}

// 计算未分配幼儿
const unassignedChildren = computed(() => {
  const assignedIds = assignedChildren.value
    .filter(item => item && item.child_id)  // 添加 item 存在性检查
    .map(item => item.child_id)
  return allChildren.value.filter(child => !assignedIds.includes(child.id))
})

// 计算统计信息
const totalChildren = computed(() => allChildren.value.length)
const assignedChildrenCount = computed(() => assignedChildren.value.length)

// 获取班级列表
const getClassList = async () => {
  try {
    const res = await classApi.getClassList({ page_size: 100 })
    // 处理分页数据结构的变化
    if (res && res.results) {
      // 新的DRF分页格式 - 数据在results.items中
      classList.value = Array.isArray(res.results.items) ? res.results.items : res.results
    } else {
      // 兼容旧格式
      classList.value = res.data?.results || res.items || res || []
    }
    if (classList.value.length > 0 && !selectedClassId.value) {
      selectedClassId.value = classList.value[0].id
      handleClassChange()
    }
  } catch (error) {
    console.error('获取班级列表失败:', error)
    ElMessage.error('获取班级列表失败')
  }
}

// 处理班级切换
const handleClassChange = async () => {
  console.log('班级切换事件触发，当前选中班级ID:', selectedClassId.value) // 调试日志
  
  if (!selectedClassId.value) {
    // 重置数据
    selectionAreas.value = []
    allChildren.value = []
    assignedChildren.value = []
    return
  }
  
  loading.value = true
  try {
    // 获取该班级的选区
    const areasRes = await getSelectionAreas({ 
      class_id: selectedClassId.value,
      page_size: 100 
    })
    console.log('获取选区结果:', areasRes) // 调试日志
    // 处理分页数据结构的变化
    if (areasRes && areasRes.results) {
      // 新的DRF分页格式 - 数据在results.items中
      selectionAreas.value = Array.isArray(areasRes.results.items) ? areasRes.results.items : areasRes.results
    } else {
      // 兼容旧格式
      selectionAreas.value = areasRes.data?.results || areasRes.items || areasRes || []
    }
    
    // 获取该班级的幼儿
    const childrenRes = await childApi.getChildrenList({ 
      class_id: selectedClassId.value,
      page_size: 200 
    })
    console.log('获取幼儿结果:', childrenRes) // 调试日志
    // 处理分页数据结构的变化
    if (childrenRes && childrenRes.results) {
      // 新的DRF分页格式 - 数据在results.items中
      allChildren.value = Array.isArray(childrenRes.results.items) ? childrenRes.results.items : childrenRes.results
    } else {
      // 兼容旧格式
      allChildren.value = childrenRes.data?.results || childrenRes.items || childrenRes || []
    }
    
    // 获取该班级的选区记录
    const recordsRes = await getSelectionRecords({ 
      class_id: selectedClassId.value,
      page_size: 200 
    })
    console.log('获取选区记录结果:', recordsRes) // 调试日志
    // 处理分页数据结构的变化
    if (recordsRes && recordsRes.results) {
      // 新的DRF分页格式 - 数据在results.items中
      assignedChildren.value = Array.isArray(recordsRes.results.items) ? recordsRes.results.items : recordsRes.results
    } else {
      // 兼容旧格式
      assignedChildren.value = recordsRes.data?.results || recordsRes.items || recordsRes || []
    }
    
    console.log('数据加载完成') // 调试日志
  } catch (error) {
    console.error('获取数据失败:', error)
    ElMessage.error('获取数据失败')
  } finally {
    loading.value = false
  }
}

// 根据选区ID获取幼儿列表
const getChildrenByArea = (areaId) => {
  const assignedChildIds = assignedChildren.value
    .filter(record => record && record.selection_area_id === areaId)  // 添加 record 存在性检查
    .map(record => record.child_id)

  return allChildren.value.filter(child => assignedChildIds.includes(child.id))
}

// 计算年龄
const calculateAge = (birthDate) => {
  const today = new Date()
  const birth = new Date(birthDate)
  let age = today.getFullYear() - birth.getFullYear()
  const monthDiff = today.getMonth() - birth.getMonth()
  
  if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
    age--
  }
  
  return age
}

// 拖拽相关处理
const handleDragStart = (event, type, data) => {
  dragData.value = { type, data }
  event.dataTransfer.effectAllowed = 'move'
  event.target.classList.add('dragging')
  
  // 添加拖拽预览效果
  const dragImage = event.target.cloneNode(true)
  dragImage.style.opacity = '0.8'
  dragImage.style.transform = 'scale(1.1)'
  dragImage.classList.add('drag-preview')
  document.body.appendChild(dragImage)
  event.dataTransfer.setDragImage(dragImage, 0, 0)
  setTimeout(() => document.body.removeChild(dragImage), 0)
  
  // 创建拖拽轨迹点
  if (event.clientX && event.clientY) {
    createDragTrail(event.clientX, event.clientY)
  }
}

const handleDragEnd = (event) => {
  event.target.classList.remove('dragging')
  dragOverSource.value = false
  dragOverTarget.value = null
}

const handleDragEnter = (areaType, areaId = null) => {
  if (areaType === 'source') {
    dragOverSource.value = true
  } else if (areaType === 'target') {
    dragOverTarget.value = areaId
  }
}

const handleDragLeave = (areaType) => {
  if (areaType === 'source') {
    dragOverSource.value = false
  } else if (areaType === 'target') {
    dragOverTarget.value = null
  }
}

// 创建拖拽轨迹点
const createDragTrail = (x, y) => {
  const trail = document.createElement('div')
  trail.className = 'drag-trail'
  trail.style.left = `${x}px`
  trail.style.top = `${y}px`
  document.body.appendChild(trail)
  
  // 移除轨迹点
  setTimeout(() => {
    if (trail.parentNode) {
      trail.parentNode.removeChild(trail)
    }
  }, 500)
}

// 监听鼠标移动以创建轨迹
document.addEventListener('dragover', (e) => {
  if (dragData.value) {
    createDragTrail(e.clientX, e.clientY)
  }
})

// 拖拽到未分配区域
const handleDropToSource = async () => {
  if (!dragData.value || dragData.value.type !== 'child') return
  
  const child = dragData.value.data
  const record = assignedChildren.value.find(r => r.child_id === child.id)
  
  if (record) {
    try {
      await deleteSelectionRecord(record.id)
      assignedChildren.value = assignedChildren.value.filter(r => r.id !== record.id)
      ElMessage.success(`${child.name}已取消分配`)
    } catch (error) {
      ElMessage.error('取消分配失败')
    }
  }
  
  dragOverSource.value = false
  dragData.value = null
}

// 拖拽到选区
const handleDropToArea = async (areaId) => {
  if (!dragData.value || dragData.value.type !== 'child') return
  
  const child = dragData.value.data
  const area = selectionAreas.value.find(a => a.id === areaId)

  // 检查area是否存在
  if (!area) {
    ElMessage.error('选区不存在')
    dragOverTarget.value = null
    dragData.value = null
    return
  }

  // 检查选区是否已满
  const currentCount = getChildrenByArea(areaId).length
  if (currentCount >= area.capacity) {
    ElMessage.warning('该选区人数已满')
    dragOverTarget.value = null
    dragData.value = null
    return
  }

  // 添加视觉反馈
  const targetArea = document.querySelector(`[data-area-id="${areaId}"]`)
  if (targetArea) {
    targetArea.classList.add('drop-success')
    setTimeout(() => {
      targetArea.classList.remove('drop-success')
    }, 1000)
  }

  // 检查幼儿是否已分配到其他选区
  const existingRecord = assignedChildren.value.find(r => r && r.child_id === child.id)
  if (existingRecord) {
    // 更新选区
    try {
      await updateSelectionRecord(existingRecord.id, {
        selection_area_id: areaId
      })
      // 更新本地状态
      const index = assignedChildren.value.findIndex(r => r && r.id === existingRecord.id)
      if (index !== -1) {
        assignedChildren.value[index].selection_area_id = areaId
      }
      ElMessage.success(`${child.name}已重新分配到${area.name}`)
    } catch (error) {
      ElMessage.error('重新分配失败')
    }
  } else {
    // 创建新记录
    try {
      const res = await createSelectionRecord({
        child_id: child.id,
        selection_area_id: areaId
      })
      assignedChildren.value.push(res.data)
      ElMessage.success(`${child.name}已分配到${area.name}`)
    } catch (error) {
      ElMessage.error('分配失败')
    }
  }
  
  dragOverTarget.value = null
  dragData.value = null
}

// 全屏切换功能
const toggleFullscreen = () => {
  console.log('切换全屏状态') // 调试日志
  
  // 确保始终获取到正确的容器元素
  const container = containerRef.value
  if (container) {
    fullscreenElement.value = container
  } else {
    ElMessage.error('无法找到容器元素')
    return
  }
  
  if (!document.fullscreenElement) {
    // 进入全屏
    console.log('进入全屏模式') // 调试日志
    if (fullscreenElement.value.requestFullscreen) {
      fullscreenElement.value.requestFullscreen()
    } else if (fullscreenElement.value.mozRequestFullScreen) { // Firefox
      fullscreenElement.value.mozRequestFullScreen()
    } else if (fullscreenElement.value.webkitRequestFullscreen) { // Chrome, Safari and Opera
      fullscreenElement.value.webkitRequestFullscreen()
    } else if (fullscreenElement.value.msRequestFullscreen) { // IE/Edge
      fullscreenElement.value.msRequestFullscreen()
    } else {
      ElMessage.error('浏览器不支持全屏功能')
      return
    }
    isFullscreen.value = true
  } else {
    // 退出全屏
    console.log('退出全屏模式') // 调试日志
    if (document.exitFullscreen) {
      document.exitFullscreen()
    } else if (document.mozCancelFullScreen) { // Firefox
      document.mozCancelFullScreen()
    } else if (document.webkitExitFullscreen) { // Chrome, Safari and Opera
      document.webkitExitFullscreen()
    } else if (document.msExitFullscreen) { // IE/Edge
      document.msExitFullscreen()
    } else {
      ElMessage.error('无法退出全屏模式')
      return
    }
    isFullscreen.value = false
  }
  
  // 强制刷新选择器
  selectKey.value += 1
}

// 监听全屏变化事件
const handleFullscreenChange = () => {
  isFullscreen.value = !!document.fullscreenElement ||
    !!document.mozFullScreenElement ||
    !!document.webkitFullscreenElement ||
    !!document.msFullscreenElement
    
  // 全屏状态改变时强制刷新选择器
  selectKey.value += 1
  
  // 在全屏状态改变后重新绑定事件监听器
  setTimeout(() => {
    if (containerRef.value) {
      fullscreenElement.value = containerRef.value
    }
    
    // 强制重新计算下拉框位置
    const dropdowns = document.querySelectorAll('.el-select-dropdown')
    dropdowns.forEach(dropdown => {
      // 如果在全屏模式下，将下拉框附加到特定容器
      if (isFullscreen.value) {
        dropdown.style.zIndex = '10002';
      } else {
        dropdown.style.position = '';
        dropdown.style.zIndex = '';
      }
    })
    
    // 为所有下拉框添加全屏兼容样式
    const poppers = document.querySelectorAll('.el-popper')
    poppers.forEach(popper => {
      popper.style.zIndex = '10003'
    })
    
    // 重新触发班级选择事件
    if (selectedClassId.value) {
      handleClassChange()
    }
  }, 100)
}

// 组件挂载时获取数据
onMounted(() => {
  console.log('组件挂载') // 调试日志
  fullscreenElement.value = containerRef.value
  if (!containerRef.value) {
    console.error('容器引用未正确设置') // 调试日志
  }
  
  document.addEventListener('fullscreenchange', handleFullscreenChange)
  document.addEventListener('mozfullscreenchange', handleFullscreenChange)
  document.addEventListener('webkitfullscreenchange', handleFullscreenChange)
  document.addEventListener('msfullscreenchange', handleFullscreenChange)
  getClassList()
  
  // 添加全局样式以确保下拉框在全屏模式下可见
  const style = document.createElement('style')
  style.innerHTML = `
    .el-select-dropdown.fullscreen-compatible-popper {
      position: fixed !important;
      z-index: 9999 !important;
    }
  `
  document.head.appendChild(style)
})

// 组件卸载时移除事件监听
onUnmounted(() => {
  console.log('组件卸载，移除事件监听') // 调试日志
  document.removeEventListener('fullscreenchange', handleFullscreenChange)
  document.removeEventListener('mozfullscreenchange', handleFullscreenChange)
  document.removeEventListener('webkitfullscreenchange', handleFullscreenChange)
  document.removeEventListener('msfullscreenchange', handleFullscreenChange)
})

// 添加触摸开始事件处理
const handleTouchStart = (event, type, data) => {
  // 阻止默认滚动行为
  event.preventDefault()
  
  // 设置拖拽数据
  dragData.value = { type, data }
  
  // 添加触摸状态类
  event.target.classList.add('dragging')
  
  // 添加触摸反馈效果
  const touchEffect = document.createElement('div')
  touchEffect.className = 'touch-feedback'
  touchEffect.style.left = `${event.touches[0].clientX}px`
  touchEffect.style.top = `${event.touches[0].clientY}px`
  document.body.appendChild(touchEffect)
  
  // 移除触摸反馈效果
  setTimeout(() => {
    if (touchEffect.parentNode) {
      touchEffect.parentNode.removeChild(touchEffect)
    }
  }, 300)
}

// 添加触摸移动事件处理
const handleTouchMove = (event) => {
  // 阻止默认滚动行为
  event.preventDefault()
  
  // 创建触摸轨迹点
  if (event.touches[0]) {
    createDragTrail(event.touches[0].clientX, event.touches[0].clientY)
  }
}

// 添加触摸结束事件处理
const handleTouchEnd = (event, areaType, areaId = null) => {
  event.preventDefault()
  
  // 移除拖拽状态类
  const target = event.target
  if (target) {
    target.classList.remove('dragging')
  }
  
  // 根据区域类型处理触摸结束事件
  if (areaType === 'source') {
    dragOverSource.value = false
  } else if (areaType === 'target') {
    dragOverTarget.value = areaId
    if (areaId && dragData.value) {
      // 触摸结束时执行放置操作
      handleDropToArea(areaId)
    }
  }
}

// 添加触摸取消事件处理
const handleTouchCancel = (event) => {
  event.preventDefault()
  
  // 清理状态
  dragOverSource.value = false
  dragOverTarget.value = null
  dragData.value = null
  
  // 移除拖拽状态类
  const target = event.target
  if (target) {
    target.classList.remove('dragging')
  }
}

</script>

<style scoped>
.selection-operation-container {
  padding: 10px;
  background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
  min-height: calc(100vh - 20px);
  color: #fff;
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.page-header {
  margin-bottom: 10px;
  text-align: center;
  flex-shrink: 0;
}

.page-header h2 {
  margin: 0 0 5px 0;
  font-size: 24px;
  color: #fff;
  font-weight: 600;
  text-shadow: 0 0 10px rgba(255, 255, 255, 0.5);
}

.page-header p {
  margin: 0;
  color: #ccc;
  font-size: 14px;
}

.class-selector-card {
  margin-bottom: 10px;
  border-radius: 8px;
  box-shadow: 0 2px 8px 0 rgba(0, 0, 0, 0.3);
  background: rgba(30, 30, 46, 0.7);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  flex-shrink: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stats-info {
  font-size: 12px;
  color: #aaa;
  font-weight: 500;
}

.content-card {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  height: 100%;
}

.content-card :deep(.el-card__body) {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding: 15px !important;
  height: 100%;
}

.selection-operation-content {
  display: flex;
  flex-direction: column;
  gap: 15px;
  flex: 1;
  overflow: hidden;
  height: 100%;
}

.unassigned-section, .selection-areas-section {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.unassigned-section {
  flex: 0 0 40%; /* 固定占用40%高度 */
}

.selection-areas-section {
  flex: 0 0 60%; /* 固定占用60%高度 */
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.unassigned-area {
  border: 2px dashed rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  padding: 10px;
  flex: 1;
  min-height: 0;
  transition: all 0.3s ease;
  background: rgba(30, 30, 46, 0.5);
  backdrop-filter: blur(5px);
  overflow-y: hidden;
  display: flex;
  flex-direction: column;
  position: relative; /* 添加相对定位 */
}

/* 未分配区域的炫酷背景效果 */
.unassigned-background-effects {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
}

.floating-particle {
  position: absolute;
  width: 6px;
  height: 6px;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  animation: floatParticle 8s infinite linear;
  box-shadow: 0 0 10px rgba(100, 200, 255, 0.8);
}

.floating-particle:nth-child(2n) {
  background: rgba(100, 200, 255, 0.4);
  width: 4px;
  height: 4px;
  box-shadow: 0 0 8px rgba(100, 200, 255, 0.6);
}

.floating-particle:nth-child(3n) {
  background: rgba(255, 100, 200, 0.4);
  width: 5px;
  height: 5px;
  box-shadow: 0 0 12px rgba(255, 100, 200, 0.6);
}

.floating-particle:nth-child(4n) {
  background: rgba(100, 255, 200, 0.4);
  width: 3px;
  height: 3px;
  box-shadow: 0 0 6px rgba(100, 255, 200, 0.6);
}

/* 增加更多浮动粒子 */
.floating-particle.extra {
  width: 2px;
  height: 2px;
  animation-duration: 12s;
}

.floating-particle.extra:nth-child(2n) {
  background: rgba(255, 200, 100, 0.4);
  width: 3px;
  height: 3px;
  box-shadow: 0 0 8px rgba(255, 200, 100, 0.6);
}

.floating-particle.extra:nth-child(3n) {
  background: rgba(200, 100, 255, 0.4);
  width: 4px;
  height: 4px;
  box-shadow: 0 0 10px rgba(200, 100, 255, 0.6);
}

/* 为每个粒子设置不同的初始位置和动画延迟 */
.floating-particle:nth-child(1) { top: 10%; left: 10%; animation-delay: 0s; }
.floating-particle:nth-child(2) { top: 20%; left: 80%; animation-delay: 1s; }
.floating-particle:nth-child(3) { top: 30%; left: 30%; animation-delay: 2s; }
.floating-particle:nth-child(4) { top: 40%; left: 70%; animation-delay: 3s; }
.floating-particle:nth-child(5) { top: 50%; left: 20%; animation-delay: 4s; }
.floating-particle:nth-child(6) { top: 60%; left: 60%; animation-delay: 5s; }
.floating-particle:nth-child(7) { top: 70%; left: 40%; animation-delay: 6s; }
.floating-particle:nth-child(8) { top: 80%; left: 80%; animation-delay: 7s; }
.floating-particle:nth-child(9) { top: 15%; left: 50%; animation-delay: 0.5s; }
.floating-particle:nth-child(10) { top: 25%; left: 25%; animation-delay: 1.5s; }
.floating-particle:nth-child(11) { top: 35%; left: 65%; animation-delay: 2.5s; }
.floating-particle:nth-child(12) { top: 45%; left: 15%; animation-delay: 3.5s; }
.floating-particle:nth-child(13) { top: 55%; left: 55%; animation-delay: 4.5s; }
.floating-particle:nth-child(14) { top: 65%; left: 35%; animation-delay: 5.5s; }
.floating-particle:nth-child(15) { top: 75%; left: 75%; animation-delay: 6.5s; }
.floating-particle:nth-child(16) { top: 85%; left: 45%; animation-delay: 7.5s; }
.floating-particle:nth-child(17) { top: 12%; left: 90%; animation-delay: 0.8s; }
.floating-particle:nth-child(18) { top: 22%; left: 10%; animation-delay: 1.8s; }
.floating-particle:nth-child(19) { top: 32%; left: 80%; animation-delay: 2.8s; }
.floating-particle:nth-child(20) { top: 42%; left: 20%; animation-delay: 3.8s; }
.floating-particle:nth-child(21) { top: 52%; left: 60%; animation-delay: 4.8s; }
.floating-particle:nth-child(22) { top: 62%; left: 30%; animation-delay: 5.8s; }
.floating-particle:nth-child(23) { top: 72%; left: 70%; animation-delay: 6.8s; }
.floating-particle:nth-child(24) { top: 82%; left: 40%; animation-delay: 7.8s; }
.floating-particle:nth-child(25) { top: 18%; left: 15%; animation-delay: 0.3s; }
.floating-particle:nth-child(26) { top: 28%; left: 85%; animation-delay: 1.3s; }
.floating-particle:nth-child(27) { top: 38%; left: 35%; animation-delay: 2.3s; }
.floating-particle:nth-child(28) { top: 48%; left: 65%; animation-delay: 3.3s; }
.floating-particle:nth-child(29) { top: 58%; left: 25%; animation-delay: 4.3s; }
.floating-particle:nth-child(30) { top: 68%; left: 75%; animation-delay: 5.3s; }
.floating-particle:nth-child(31) { top: 5%; left: 40%; animation-delay: 0.2s; }
.floating-particle:nth-child(32) { top: 15%; left: 70%; animation-delay: 1.2s; }
.floating-particle:nth-child(33) { top: 25%; left: 10%; animation-delay: 2.2s; }
.floating-particle:nth-child(34) { top: 35%; left: 80%; animation-delay: 3.2s; }
.floating-particle:nth-child(35) { top: 45%; left: 30%; animation-delay: 4.2s; }
.floating-particle:nth-child(36) { top: 55%; left: 60%; animation-delay: 5.2s; }
.floating-particle:nth-child(37) { top: 65%; left: 20%; animation-delay: 6.2s; }
.floating-particle:nth-child(38) { top: 75%; left: 90%; animation-delay: 7.2s; }
.floating-particle:nth-child(39) { top: 85%; left: 50%; animation-delay: 0.7s; }
.floating-particle:nth-child(40) { top: 95%; left: 25%; animation-delay: 1.7s; }
.floating-particle:nth-child(41) { top: 8%; left: 65%; animation-delay: 2.7s; }
.floating-particle:nth-child(42) { top: 18%; left: 15%; animation-delay: 3.7s; }
.floating-particle:nth-child(43) { top: 28%; left: 75%; animation-delay: 4.7s; }
.floating-particle:nth-child(44) { top: 38%; left: 35%; animation-delay: 5.7s; }
.floating-particle:nth-child(45) { top: 48%; left: 85%; animation-delay: 6.7s; }
.floating-particle:nth-child(46) { top: 58%; left: 45%; animation-delay: 7.7s; }
.floating-particle:nth-child(47) { top: 68%; left: 5%; animation-delay: 0.9s; }
.floating-particle:nth-child(48) { top: 78%; left: 55%; animation-delay: 1.9s; }
.floating-particle:nth-child(49) { top: 88%; left: 95%; animation-delay: 2.9s; }
.floating-particle:nth-child(50) { top: 3%; left: 30%; animation-delay: 3.9s; }

/* 发光球体 */
.glowing-orb {
  position: absolute;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(100, 200, 255, 0.8), transparent 70%);
  box-shadow: 0 0 30px rgba(100, 200, 255, 0.5);
  animation: floatOrb 15s infinite ease-in-out;
  opacity: 0.7;
}

.glowing-orb:nth-child(1) { 
  width: 40px; 
  height: 40px; 
  top: 20%; 
  left: 15%; 
  animation-delay: 0s; 
}

.glowing-orb:nth-child(2) { 
  width: 30px; 
  height: 30px; 
  top: 70%; 
  left: 80%; 
  animation-delay: 2s; 
  background: radial-gradient(circle, rgba(255, 100, 200, 0.8), transparent 70%);
  box-shadow: 0 0 30px rgba(255, 100, 200, 0.5);
}

.glowing-orb:nth-child(3) { 
  width: 50px; 
  height: 50px; 
  top: 40%; 
  left: 50%; 
  animation-delay: 4s; 
  background: radial-gradient(circle, rgba(100, 255, 200, 0.8), transparent 70%);
  box-shadow: 0 0 30px rgba(100, 255, 200, 0.5);
}

.glowing-orb:nth-child(4) { 
  width: 35px; 
  height: 35px; 
  top: 60%; 
  left: 20%; 
  animation-delay: 6s; 
  background: radial-gradient(circle, rgba(200, 100, 255, 0.8), transparent 70%);
  box-shadow: 0 0 30px rgba(200, 100, 255, 0.5);
}

.glowing-orb:nth-child(5) { 
  width: 45px; 
  height: 45px; 
  top: 30%; 
  left: 70%; 
  animation-delay: 8s; 
  background: radial-gradient(circle, rgba(255, 200, 100, 0.8), transparent 70%);
  box-shadow: 0 0 30px rgba(255, 200, 100, 0.5);
}

/* 添加脉冲环效果 */
.pulse-ring {
  position: absolute;
  border-radius: 50%;
  border: 2px solid rgba(255, 255, 255, 0.5);
  animation: pulseRing 4s infinite ease-out;
}

.pulse-ring:nth-child(1) {
  top: 30%;
  left: 25%;
  width: 20px;
  height: 20px;
  animation-delay: 0s;
}

.pulse-ring:nth-child(2) {
  top: 60%;
  left: 70%;
  width: 30px;
  height: 30px;
  animation-delay: 1s;
}

.pulse-ring:nth-child(3) {
  top: 40%;
  left: 60%;
  width: 25px;
  height: 25px;
  animation-delay: 2s;
}

.pulse-ring:nth-child(4) {
  top: 70%;
  left: 30%;
  width: 15px;
  height: 15px;
  animation-delay: 3s;
}

/* 星云效果 */
.nebula {
  position: absolute;
  border-radius: 50%;
  background: radial-gradient(
    ellipse at center,
    rgba(120, 100, 255, 0.3) 0%,
    rgba(80, 60, 200, 0.2) 40%,
    rgba(40, 30, 100, 0.1) 70%,
    transparent 100%
  );
  filter: blur(20px);
  animation: nebulaFloat 25s infinite linear;
}

.nebula:nth-child(1) {
  top: 20%;
  left: 30%;
  width: 150px;
  height: 150px;
  animation-delay: 0s;
}

.nebula:nth-child(2) {
  top: 50%;
  left: 70%;
  width: 200px;
  height: 200px;
  animation-delay: 5s;
  background: radial-gradient(
    ellipse at center,
    rgba(255, 100, 150, 0.3) 0%,
    rgba(200, 60, 100, 0.2) 40%,
    rgba(100, 30, 50, 0.1) 70%,
    transparent 100%
  );
}

.children-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  flex: 1;
  align-content: flex-start;
  position: relative;
  z-index: 1; /* 确保幼儿列表在背景效果之上 */
}

/* 悬停时的视觉效果 */
.unassigned-area.drag-over {
  border: 2px dashed rgba(100, 200, 255, 0.8);
  background: rgba(30, 30, 46, 0.8);
  box-shadow: 0 0 20px rgba(100, 200, 255, 0.5);
}

/* 幼儿项悬停时的放大效果 */
.child-item {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  cursor: grab;
}

.child-item:hover {
  transform: scale(1.05);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
}

.child-item.dragging {
  cursor: grabbing;
  transform: scale(1.1);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.5);
  z-index: 100;
  opacity: 0.9;
}

/* 添加拖拽预览效果 */
.drag-preview {
  position: fixed;
  pointer-events: none;
  z-index: 9999;
  transform: translate(-50%, -50%) scale(1.2);
  opacity: 0.8;
  box-shadow: 0 0 20px rgba(100, 200, 255, 0.8);
  border-radius: 50%;
  transition: all 0.2s ease;
}

/* 拖拽悬停效果 */
.selection-area.drag-over {
  transform: scale(1.05);
  box-shadow: 0 0 30px rgba(100, 200, 255, 0.8);
  border-color: rgba(100, 200, 255, 0.8);
  animation: areaGlow 1s infinite alternate;
}

@keyframes areaGlow {
  from {
    box-shadow: 0 0 20px rgba(100, 200, 255, 0.8);
  }
  to {
    box-shadow: 0 0 40px rgba(100, 200, 255, 1), 0 0 60px rgba(100, 200, 255, 0.6);
  }
}

/* 成功投放动画 */
.selection-area.drop-success {
  animation: dropSuccess 0.8s ease;
}

@keyframes dropSuccess {
  0% {
    transform: scale(1);
    box-shadow: 0 0 20px rgba(100, 200, 255, 0.8);
  }
  50% {
    transform: scale(1.15);
    box-shadow: 0 0 40px rgba(100, 255, 100, 1), 0 0 60px rgba(100, 255, 100, 0.6);
  }
  100% {
    transform: scale(1);
    box-shadow: 0 0 20px rgba(100, 200, 255, 0.8);
  }
}

/* 拖拽轨迹效果 */
.drag-trail {
  position: absolute;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(100, 200, 255, 0.8), transparent 70%);
  pointer-events: none;
  z-index: 9998;
  animation: trailFade 0.5s forwards;
}

@keyframes trailFade {
  to {
    transform: scale(0);
    opacity: 0;
  }
}

/* 浮动粒子动画 */
@keyframes floatParticle {
  0% {
    transform: translate(0, 0) rotate(0deg);
    opacity: 0;
  }
  10% {
    opacity: 1;
  }
  90% {
    opacity: 1;
  }
  100% {
    transform: translate(20px, -20px) rotate(360deg);
    opacity: 0;
  }
}

/* 浮动球体动画 */
@keyframes floatOrb {
  0%, 100% {
    transform: translate(0, 0);
  }
  25% {
    transform: translate(20px, -15px);
  }
  50% {
    transform: translate(10px, 20px);
  }
  75% {
    transform: translate(-15px, 10px);
  }
}

/* 脉冲环动画 */
@keyframes pulseRing {
  0% {
    transform: scale(0.5);
    opacity: 1;
  }
  100% {
    transform: scale(3);
    opacity: 0;
  }
}

/* 星云浮动动画 */
@keyframes nebulaFloat {
  0% {
    transform: translate(0, 0) rotate(0deg);
  }
  25% {
    transform: translate(20px, 10px) rotate(90deg);
  }
  50% {
    transform: translate(10px, -20px) rotate(180deg);
  }
  75% {
    transform: translate(-15px, 15px) rotate(270deg);
  }
  100% {
    transform: translate(0, 0) rotate(360deg);
  }
}

.selection-areas {
  display: flex;
  flex-wrap: nowrap;
  gap: 20px;
  flex: 1;
  overflow-x: auto;
  overflow-y: hidden;
  align-content: stretch;
  min-height: 0;
}

.selection-area {
  flex: 1 0 auto;
  background: #000;
  border-radius: 12px;
  transition: all 0.3s ease;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.1);
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 160px;
  min-height: 160px;
}

.selection-area.drag-over {
  transform: scale(1.05);
  box-shadow: 0 0 30px rgba(100, 200, 255, 0.8);
  border-color: rgba(100, 200, 255, 0.8);
}

.selection-area.drop-success {
  animation: dropSuccess 0.5s ease;
}

@keyframes dropSuccess {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.15);
  }
  100% {
    transform: scale(1);
  }
}

.black-hole-container {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  justify-content: center;
  align-items: center;
  overflow: hidden;
  width: 100%;
  height: 100%;
}

.black-hole {
  position: relative;
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  background: #000;
}

.black-hole-core {
  position: absolute;
  width: 60px;
  height: 60px;
  background: #000;
  border-radius: 50%;
  box-shadow: 
    0 0 40px #000,
    0 0 80px #000,
    0 0 120px #000;
  z-index: 10;
  animation: blackHolePulse 3s infinite alternate;
}

.black-hole-ring {
  position: absolute;
  border-radius: 50%;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.ring-1 {
  width: 100px;
  height: 100px;
  border-color: rgba(255, 255, 255, 0.4);
  box-shadow: 0 0 20px rgba(255, 255, 255, 0.3);
  animation: rotateRing 8s linear infinite;
}

.ring-2 {
  width: 140px;
  height: 140px;
  border-color: rgba(255, 255, 255, 0.3);
  box-shadow: 0 0 25px rgba(255, 255, 255, 0.2);
  animation: rotateRing 12s linear infinite reverse;
}

.ring-3 {
  width: 180px;
  height: 180px;
  border-color: rgba(255, 255, 255, 0.2);
  box-shadow: 0 0 30px rgba(255, 255, 255, 0.1);
  animation: rotateRing 16s linear infinite;
}

.black-hole-accretion-disk {
  position: absolute;
  width: 200px;
  height: 200px;
  border-radius: 50%;
  background: conic-gradient(
    from 0deg,
    rgba(255, 255, 255, 0.1),
    rgba(255, 255, 255, 0.2),
    rgba(255, 255, 255, 0.3),
    rgba(255, 255, 255, 0.2),
    rgba(255, 255, 255, 0.1)
  );
  animation: rotateDisk 20s linear infinite;
  opacity: 0.5;
}

.black-hole-swirl {
  position: absolute;
  border-radius: 50%;
  border: 2px solid transparent;
  border-top-color: rgba(255, 255, 255, 0.5);
  opacity: 0.6;
}

.swirl-1 {
  width: 120px;
  height: 120px;
  animation: swirl 4s linear infinite;
}

.swirl-2 {
  width: 160px;
  height: 160px;
  border-top-color: rgba(255, 255, 255, 0.4);
  animation: swirl 6s linear infinite reverse;
}

.swirl-3 {
  width: 200px;
  height: 200px;
  border-top-color: rgba(255, 255, 255, 0.3);
  animation: swirl 8s linear infinite;
}

.black-hole-particle {
  position: absolute;
  width: 2px;
  height: 2px;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 50%;
  animation: particleOrbit 5s linear infinite;
}

/* 为每个粒子设置不同的轨道 */
.black-hole-particle:nth-child(1) { animation-delay: 0s; }
.black-hole-particle:nth-child(2) { animation-delay: 0.4s; }
.black-hole-particle:nth-child(3) { animation-delay: 0.8s; }
.black-hole-particle:nth-child(4) { animation-delay: 1.2s; }
.black-hole-particle:nth-child(5) { animation-delay: 1.6s; }
.black-hole-particle:nth-child(6) { animation-delay: 2s; }
.black-hole-particle:nth-child(7) { animation-delay: 2.4s; }
.black-hole-particle:nth-child(8) { animation-delay: 2.8s; }
.black-hole-particle:nth-child(9) { animation-delay: 3.2s; }
.black-hole-particle:nth-child(10) { animation-delay: 3.6s; }
.black-hole-particle:nth-child(11) { animation-delay: 4s; }
.black-hole-particle:nth-child(12) { animation-delay: 4.4s; }

/* 吸入的选区名称 */
.area-name-infalling {
  position: absolute;
  color: #fff;
  font-weight: bold;
  white-space: nowrap;
  animation: infallingText 3s linear infinite; /* 从1.5s改为3s，降低速度 */
  text-shadow: 0 0 10px rgba(255, 255, 255, 1);
  z-index: 5;
  pointer-events: none;
  font-size: 16px;
}

/* 动画定义 */
@keyframes rotateRing {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

@keyframes rotateDisk {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

@keyframes swirl {
  0% {
    transform: rotate(0deg);
    opacity: 0.7;
  }
  50% {
    opacity: 0.3;
  }
  100% {
    transform: rotate(360deg);
    opacity: 0.7;
  }
}

@keyframes particleOrbit {
  0% {
    transform: rotate(0deg) translateX(80px) rotate(0deg);
  }
  100% {
    transform: rotate(360deg) translateX(80px) rotate(-360deg);
  }
}

@keyframes blackHolePulse {
  0% {
    box-shadow: 0 0 40px #000, 0 0 80px #000, 0 0 120px #000;
  }
  100% {
    box-shadow: 0 0 50px #000, 0 0 90px #000, 0 0 130px #000;
  }
}

@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-5px);
  }
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
}

@keyframes glow {
  0% {
    text-shadow: 0 0 5px rgba(255, 255, 255, 0.5);
  }
  100% {
    text-shadow: 0 0 15px rgba(255, 255, 255, 0.8), 0 0 25px rgba(255, 255, 255, 0.5);
  }
}

@keyframes suckedIn {
  0% {
    transform: scale(1) translate(0, 0);
    opacity: 1;
  }
  100% {
    transform: scale(0.5) translate(var(--suck-x, 0), var(--suck-y, 0));
    opacity: 0.5;
  }
}

@keyframes infallingText {
  0% {
    transform: translate(var(--start-x, -100px), var(--start-y, -100px)) scale(1);
    opacity: 1;
  }
  100% {
    transform: translate(0, 0) scale(0.1);
    opacity: 0;
  }
}

/* 全屏样式 */
.selection-operation-container:fullscreen {
  padding: 10px;
  background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
  min-height: 100vh;
  position: relative;
  z-index: 9998;
}

.selection-operation-container:fullscreen .el-select-dropdown {
  position: absolute !important;
  z-index: 10002 !important;
}

.selection-operation-container:-webkit-full-screen {
  padding: 10px;
  background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
  min-height: 100vh;
  position: relative;
  z-index: 9998;
}

.selection-operation-container:-webkit-full-screen .el-select-dropdown {
  position: absolute !important;
  z-index: 10002 !important;
}

.selection-operation-container:-moz-full-screen {
  padding: 10px;
  background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
  min-height: 100vh;
  position: relative;
  z-index: 9998;
}

.selection-operation-container:-moz-full-screen .el-select-dropdown {
  position: absolute !important;
  z-index: 10002 !important;
}

.selection-operation-container:-ms-fullscreen {
  padding: 10px;
  background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
  min-height: 100vh;
  position: relative;
  z-index: 9998;
}

.selection-operation-container:-ms-fullscreen .el-select-dropdown {
  position: absolute !important;
  z-index: 10002 !important;
}

/* 确保班级选择器在全屏模式下可见并位于顶层 */
.class-selector-wrapper {
  position: relative;
  z-index: 10000;
}

.class-selector-card {
  position: relative;
  z-index: 10000;
}

.class-selector-card .el-select {
  position: relative;
  z-index: 10004;
}

/* 确保全屏模式下下拉框容器定位正确 */
.fullscreen-dropdown-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 9999;
  overflow: visible;
}

/* 非全屏模式下的样式 */
:not(.selection-operation-container:fullscreen) .el-select-dropdown {
  max-height: 200px !important;
  overflow-y: auto !important;
}

/* 确保下拉菜单在全屏模式下可见 */
.el-select-dropdown__item {
  color: #333 !important;
  background-color: #fff !important;
}

.el-select-dropdown__item:hover {
  background-color: #f5f5f5 !important;
}

.el-select-dropdown__item.selected {
  background-color: #e6f7ff !important;
  font-weight: bold;
}
.el-select-dropdown {
  z-index: 9999 !important;
  max-height: 300px !important;
  overflow-y: auto !important;
  overflow-x: hidden !important;
}

/* 确保下拉框出现在正确位置 */
.el-popper[x-placement^="bottom-start"] {
  margin-top: 5px !important;
  will-change: transform;
}

.fullscreen-dropdown-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 2000;
}

/* 确保下拉框出现在正确位置 */
.fullscreen-compatible-popper,
.fullscreen-select-popper {
  z-index: 10009 !important;
  position: absolute !important;
  transform-origin: center top !important;
  max-height: 300px !important;
  overflow-y: auto !important;
}

.normal-select-popper {
  z-index: 10009 !important;
  max-height: 300px !important;
  overflow-y: auto !important;
}

.fullscreen-dropdown-container .el-select-dropdown__item {
  color: #fff !important;
  background-color: #333 !important;
}

.fullscreen-dropdown-container .el-select-dropdown__item:hover {
  background-color: #555 !important;
}

.fullscreen-dropdown-container .el-select-dropdown__item.selected {
  background-color: #666 !important;
  font-weight: bold;
}

.fullscreen-dropdown-container .el-select-dropdown {
  background-color: #333 !important;
  border: 1px solid #555 !important;
  max-height: 300px !important;
  overflow-y: auto !important;
}

.fullscreen-dropdown-container .el-select-dropdown__list {
  background-color: #333 !important;
}

/* 全屏模式下班级选择器专用容器 */
.class-selector-portal {
  position: fixed;
  top: 20px;
  left: 150px;
  z-index: 10006;
  background: rgba(30, 30, 46, 0.7);
  padding: 10px 15px;
  border-radius: 8px;
  box-shadow: 0 2px 8px 0 rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

/* 提升班级选择器下拉框的z-index */
.class-selector-wrapper .el-popper,
.class-selector-card .el-popper {
  z-index: 10008 !important;
}

/* 响应式设计 */
@media (max-width: 1400px) {
  .child-item {
    flex: 1 1 calc(12.5% - 10px); /* 每行最多8个 */
    max-width: calc(12.5% - 10px);
  }
  
  .selection-areas {
    grid-template-columns: repeat(auto-fit, minmax(calc((100% - 90px) / 7), 1fr));
    grid-auto-rows: 1fr;
    gap: 18px;
  }
  
  .selection-area {
    min-height: 150px;
  }
}

@media (max-width: 1200px) {
  .child-item {
    flex: 1 1 calc(14.28% - 10px); /* 每行最多7个 */
    max-width: calc(14.28% - 10px);
  }
  
  .selection-areas {
    grid-template-columns: repeat(auto-fit, minmax(calc((100% - 80px) / 7), 1fr));
    grid-auto-rows: 1fr;
    gap: 16px;
  }
  
  .selection-area {
    min-height: 140px;
  }
}

@media (max-width: 992px) {
  .child-item {
    flex: 1 1 calc(16.66% - 10px); /* 每行最多6个 */
    max-width: calc(16.66% - 10px);
  }
  
  .selection-areas {
    grid-template-columns: repeat(auto-fit, minmax(calc((100% - 70px) / 7), 1fr));
    grid-auto-rows: 1fr;
    gap: 14px;
  }
  
  .selection-area {
    min-height: 130px;
  }
}

@media (max-width: 768px) {
  .selection-operation-container {
    padding: 5px;
  }
  
  .selection-areas {
    grid-template-columns: repeat(auto-fit, minmax(calc((100% - 60px) / 7), 1fr));
    grid-auto-rows: 1fr;
    gap: 12px;
  }
  
  .selection-area {
    min-height: 120px;
  }
}

@media (max-width: 576px) {
  .child-item {
    flex: 1 1 calc(25% - 10px); /* 每行最多4个 */
    max-width: calc(25% - 10px);
  }
  
  .selection-areas {
    grid-template-columns: repeat(auto-fit, minmax(calc((100% - 50px) / 7), 1fr));
    grid-auto-rows: 1fr;
    gap: 10px;
  }
  
  .selection-area {
    min-height: 110px;
  }
}

@media (max-width: 400px) {
  .child-item {
    flex: 1 1 calc(33.33% - 10px); /* 每行最多3个 */
    max-width: calc(33.33% - 10px);
  }
  
  .selection-areas {
    grid-template-columns: repeat(auto-fit, minmax(calc((100% - 40px) / 7), 1fr));
    grid-auto-rows: 1fr;
    gap: 8px;
  }
  
  .selection-area {
    min-height: 100px;
  }
}

/* 添加触摸反馈效果样式 */
.touch-feedback {
  position: fixed;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(100, 200, 255, 0.3);
  pointer-events: none;
  z-index: 9999;
  animation: touchFeedback 0.3s forwards;
  transform: translate(-50%, -50%);
}

@keyframes touchFeedback {
  0% {
    transform: translate(-50%, -50%) scale(0.5);
    opacity: 1;
  }
  100% {
    transform: translate(-50%, -50%) scale(1.5);
    opacity: 0;
  }
}

/* 增加幼儿项在触摸设备上的可点击区域 */
.child-item {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  cursor: grab;
  touch-action: none; /* 防止触摸时的默认滚动行为 */
  min-height: 80px; /* 增加最小高度以适应手指操作 */
  min-width: 80px; /* 增加最小宽度以适应手指操作 */
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

/* 平板设备上的特殊样式 */
@media (max-width: 1024px) and (pointer: coarse) {
  .child-item {
    min-height: 90px;
    min-width: 90px;
    padding: 10px;
  }
  
  .child-avatar {
    transform: scale(1.2);
  }
  
  .child-name {
    font-size: 16px;
    margin-top: 8px;
  }
  
  /* 增加选区区域的触摸友好性 */
  .selection-area {
    min-height: 180px;
    min-width: 180px;
  }
  
  /* 增加拖拽区域的触摸友好性 */
  .unassigned-area {
    min-height: 200px;
  }
}

/* 触摸设备上的悬停效果 */
@media (pointer: coarse) {
  .child-item:hover {
    transform: scale(1.05);
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
  }
  
  .child-item:active {
    transform: scale(1.1);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.5);
  }
}

</style>