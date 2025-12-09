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
    
    <!-- 全屏模式下用于放置下拉框的容器 -->
    <div v-if="isFullscreen" class="fullscreen-dropdown-container" id="fullscreenDropdownContainer"></div>

    <!-- 解决全屏模式下班级选择器被遮挡问题的特殊处理 -->
    <div v-if="isFullscreen" ref="dropdownPlaceholder" style="position: fixed; z-index: 10003; top: 60px; left: 20px;"></div>

    <el-card v-loading="loading" class="content-card">
      <template #header>
        <div class="card-header">
          <span>选区分配</span>
          <div class="stats-info">
            总人数: {{ totalChildren }} | 已分配: {{ assignedTodayCount }} | 未分配: {{ unassignedCount }}
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
            @touchend="handleTouchEnd"
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
                @touchend="handleTouchEnd"
                @touchcancel="handleTouchCancel"
              >
                <div class="child-avatar-wrapper">
                  <div class="child-avatar">
                    <el-avatar :size="childAvatarSize" :src="child.avatar">{{ child.name.charAt(0) }}</el-avatar>
                  </div>
                  <!-- 添加选区历史标记 -->
                  <div v-if="getChildHasHistory(child.id)" class="selection-history-marker">选</div>
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
              :id="'selection-area-' + area.id"
              @dragenter.prevent="handleDragEnter('target', area.id)"
              @dragleave.prevent="handleDragLeave('target')"
              @dragover.prevent
              @drop.prevent="handleDropToArea(area.id)"
              @touchstart="handleTouchStart($event, 'area', area)"
              @touchmove="handleTouchMove"
              @touchend="handleTouchEnd"
              @touchcancel="handleTouchCancel"
            >
              <!-- 黑洞动画效果 -->
              <div class="black-hole-container" v-if="!area.image">
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

                  <!-- 调试信息显示 -->
                  <div class="debug-info">
                    {{ area.name }}<br>Id: {{ area.id }}
                  </div>
                </div>
              </div>
              
              <!-- 选区图片展示 -->
              <div class="area-image-container" v-else>
                <div class="glow-effect"></div>
                <div class="scan-line"></div>
                <el-image 
                  :src="area.image" 
                  class="area-image"
                  fit="contain"
                  :preview-src-list="[area.image]"
                  preview-teleported
                  :lazy="true"
                  :hide-on-click-modal="true"
                >
                  <template #placeholder>
                    <div class="image-placeholder">加载中...</div>
                  </template>
                  <template #error>
                    <div class="image-error">加载失败</div>
                  </template>
                </el-image>
                <div class="area-name-overlay">{{ area.name }}</div>
              </div>
              </div>
            </div>
          </div>
        </div>
    </el-card>

    <!-- 调试信息面板 -->
<!--    <div class="debug-panel">-->
<!--      <h4>调试信息</h4>-->
<!--      <p>当前选区数量: {{ selectionAreas.length }}</p>-->
<!--      <p>当前选区ID列表: {{ selectionAreas.map(a => a.id).join(', ') }}</p>-->
<!--      <p>触摸拖拽状态: {{ touchDragging }}</p>-->
<!--      <p>拖拽数据: {{ dragData ? dragData.data.name : '无' }}</p>-->
<!--      <p>触摸位置: {{ touchCurrentPos.x.toFixed(2) }}, {{ touchCurrentPos.y.toFixed(2) }}</p>-->
<!--      <p>当前拖拽目标: {{ dragOverTarget || '无' }}</p>-->
<!--      <p>触摸区域: {{ lastTouchArea || '无' }}</p>-->
<!--    </div>-->
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
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
const selectKey = ref(0)
const containerRef = ref(null)
const formModel = reactive({ selectedClassId: '' })
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

// Touch 拖拽状态
const touchDragging = ref(false)
const touchDragPreview = ref(null)
const touchStartPos = ref({ x: 0, y: 0 })
const touchCurrentPos = ref({ x: 0, y: 0 })
const touchMoveTimer = ref(null)
const lastTouchArea = ref(null)

// 获取随机起始位置（用于黑洞文字动画）
const getRandomStartPosition = (axis) => {
  return (Math.random() * 400 - 200) + 'px'
}

// 计算未分配幼儿
const unassignedChildren = computed(() => {
  const assignedIds = assignedChildren.value
    .filter(item => item && item.child_id)
    .map(item => item.child_id)
  return allChildren.value.filter(child => !assignedIds.includes(child.id))
})
// 判断幼儿是否曾经有过选区记录
const getChildHasHistory = (childId) => {
  // 检查该幼儿是否在所有选区记录中出现过（不仅限于今日）
  return assignedChildren.value.some(record => record.child === childId);
}


const totalChildren = computed(() => allChildren.value.length)
const assignedTodayCount = computed(() => assignedChildren.value.length)
const unassignedCount = computed(() => totalChildren.value - assignedTodayCount.value)

// 动态计算幼儿头像大小
const childAvatarSize = computed(() => {
  // 根据屏幕宽度动态调整头像大小
  const screenWidth = window.innerWidth
  if (screenWidth < 480) return 32 // 小屏幕
  if (screenWidth < 768) return 40 // 中等屏幕
  if (screenWidth < 1024) return 44 // 大屏幕
  return 48 // 超大屏幕
})

// 获取班级列表
const getClassList = async () => {
  try {
    const res = await classApi.getClassList({ page_size: 100 })
    if (res && res.results) {
      classList.value = Array.isArray(res.results.items) ? res.results.items : res.results
    } else {
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
  if (!selectedClassId.value) {
    selectionAreas.value = []
    allChildren.value = []
    assignedChildren.value = []
    return
  }

  loading.value = true
  try {
    // 获取今天的日期，格式为 YYYY-MM-DD
    const today = new Date().toISOString().split('T')[0]

    const [areasRes, childrenRes, recordsRes] = await Promise.all([
      getSelectionAreas({ class_id: selectedClassId.value, page_size: 100 }),
      childApi.getChildrenList({ class_id: selectedClassId.value, page_size: 200 }),
      getSelectionRecords({
        class_id: selectedClassId.value,
        page_size: 200,
        date_from: today,
        date_to: today,
        is_active: true
      })
    ])

    selectionAreas.value = areasRes.results?.items || areasRes.results || areasRes.data?.results || areasRes.items || areasRes || []
    allChildren.value = childrenRes.results?.items || childrenRes.results || childrenRes.data?.results || childrenRes.items || childrenRes || []
    assignedChildren.value = recordsRes.results?.items || recordsRes.results || recordsRes.data?.results || recordsRes.items || recordsRes || []
    console.log("assignedChildren.value", assignedChildren.value)
    // 更新选区宽度
    updateSelectionAreaWidth()

    // 调试信息
    console.log('获取到的选区列表:', selectionAreas.value)
    console.log('选区ID列表:', selectionAreas.value.map(a => a.id))

  } catch (error) {
    console.error('获取数据失败:', error)
    ElMessage.error('获取数据失败')
  } finally {
    loading.value = false
  }
}

// 根据选区数量动态调整宽度
const updateSelectionAreaWidth = () => {
  nextTick(() => {
    const container = document.querySelector('.selection-areas')
    if (!container || selectionAreas.value.length === 0) return

    const containerWidth = container.clientWidth
    const gap = 20 // 与 CSS 中 gap 一致
    const totalGap = (selectionAreas.value.length - 1) * gap
    const availableWidth = containerWidth - totalGap
    const idealWidth = availableWidth / selectionAreas.value.length

    // 设置最小宽度（比如 100px），防止太小无法点击
    const finalWidth = Math.max(idealWidth, 100)

    // 应用到所有 .selection-area
    const areas = container.querySelectorAll('.selection-area')
    areas.forEach(area => {
      area.style.width = `${finalWidth}px`
      area.style.minWidth = `${finalWidth}px`
    })
  })
}

// 根据选区ID获取已分配幼儿
const getChildrenByArea = (areaId) => {
  const assignedChildIds = assignedChildren.value
    .filter(record => record && record.selection_area_id === areaId)
    .map(record => record.child_id)
  return allChildren.value.filter(child => assignedChildIds.includes(child.id))
}

// 创建拖拽轨迹效果
const createDragTrail = (x, y) => {
  const trail = document.createElement('div')
  trail.className = 'drag-trail'
  trail.style.left = `${x}px`
  trail.style.top = `${y}px`
  trail.style.position = 'fixed'
  trail.style.pointerEvents = 'none'
  trail.style.zIndex = '1000000'
  trail.style.width = '20px'
  trail.style.height = '20px'
  trail.style.borderRadius = '50%'
  trail.style.background = 'radial-gradient(circle, rgba(100, 200, 255, 0.8), transparent 70%)'
  trail.style.animation = 'trailFade 0.5s forwards'
  document.body.appendChild(trail)

  // 0.5秒后移除轨迹元素
  setTimeout(() => {
    if (trail.parentNode) {
      trail.parentNode.removeChild(trail)
    }
  }, 500)

  return trail
}

// ========== 触摸拖拽核心逻辑 ==========

const createTouchDragPreview = (child) => {
  const preview = document.createElement('div')
  preview.className = 'drag-preview touch-drag-preview'
  preview.innerHTML = `
    <div style="display:flex;align-items:center;gap:8px;">
      <el-avatar size="40" src="${child.avatar || ''}">${child.name.charAt(0)}</el-avatar>
      <span>${child.name}</span>
    </div>
  `
  preview.style.position = 'fixed'
  preview.style.pointerEvents = 'none'
  preview.style.zIndex = '9999'
  preview.style.opacity = '0.9'
  preview.style.background = 'rgba(30,30,46,0.9)'
  preview.style.borderRadius = '8px'
  preview.style.padding = '6px 12px'
  preview.style.boxShadow = '0 4px 20px rgba(0,0,0,0.5)'
  preview.style.fontSize = '14px'
  preview.style.color = '#fff'
  document.body.appendChild(preview)
  return preview
}

const handleTouchStart = (event, type, data) => {
  if (type !== 'child') return

  event.preventDefault()
  const child = data
  dragData.value = { type: 'child', data: child }
  touchDragging.value = true
  touchStartPos.value = { x: event.touches[0].clientX, y: event.touches[0].clientY }
  touchCurrentPos.value = { ...touchStartPos.value }

  // 创建预览
  touchDragPreview.value = createTouchDragPreview(child)

  // 初始位置
  moveDragPreview(touchStartPos.value.x, touchStartPos.value.y)
}

const moveDragPreview = (x, y) => {
  if (touchDragPreview.value) {
    touchDragPreview.value.style.left = `${x + 10}px`
    touchDragPreview.value.style.top = `${y + 10}px`
  }

  // 创建拖拽轨迹效果
  createDragTrail(x, y)
}

// 检测当前触摸位置的选区 - 修复问题2：扩展检测区域到整个选区
const detectTouchArea = (x, y) => {
  console.log(`检测触摸位置: x=${x}, y=${y}`)

  // 1. 首先检查是否在未分配区域
  const unassignedArea = document.querySelector('.unassigned-area')
  if (unassignedArea) {
    const unassignedRect = unassignedArea.getBoundingClientRect()
    console.log(`未分配区域边界: ${unassignedRect.left}, ${unassignedRect.top}, ${unassignedRect.right}, ${unassignedRect.bottom}`)
    if (x >= unassignedRect.left && x <= unassignedRect.right &&
        y >= unassignedRect.top && y <= unassignedRect.bottom) {
      console.log('检测到未分配区域')
      return { type: 'source', id: null }
    }
  }

  // 2. 检查所有选区区域 - 修复问题2：使用整个选区容器而非黑洞中心
  const areas = document.querySelectorAll('.selection-area')
  console.log(`找到 ${areas.length} 个选区元素`)

  for (const area of areas) {
    const rect = area.getBoundingClientRect()
    console.log(`选区 ${area.dataset.areaId} 边界: ${rect.left}, ${rect.top}, ${rect.right}, ${rect.bottom}`)

    // 修复问题2：检测整个选区区域而非黑洞中心
    if (x >= rect.left && x <= rect.right && y >= rect.top && y <= rect.bottom) {
      const areaId = area.dataset.areaId
      console.log(`检测到选区 ${areaId}`)

      // 验证选区是否存在于当前列表中 - 修复问题1：类型转换
      const exists = selectionAreas.value.some(a => parseInt(a.id) === parseInt(areaId))
      if (exists) {
        console.log(`选区 ${areaId} 存在于当前列表中`)
        return { type: 'target', id: areaId }
      } else {
        console.log(`选区 ${areaId} 不存在于当前列表中`)
        return { type: 'target', id: areaId }
      }
    }
  }

  // 3. 如果没有找到匹配区域，返回null
  console.log('未检测到任何区域')
  return { type: null, id: null }
}

const handleTouchMove = (event) => {
  if (!touchDragging.value || !event.touches[0]) return
  event.preventDefault()

  const x = event.touches[0].clientX
  const y = event.touches[0].clientY
  touchCurrentPos.value = { x, y }

  moveDragPreview(x, y)

  // 检测当前触摸位置的区域
  const areaInfo = detectTouchArea(x, y)

  // 防止重复设置相同区域
  if (areaInfo.type === 'source' && !dragOverSource.value) {
    dragOverSource.value = true
    dragOverTarget.value = null
  } else if (areaInfo.type === 'target' && dragOverTarget.value !== areaInfo.id) {
    dragOverSource.value = false
    dragOverTarget.value = areaInfo.id
    lastTouchArea.value = areaInfo.id
  } else if (areaInfo.type === null) {
    dragOverSource.value = false
    dragOverTarget.value = null
  }
}

const cleanupTouchDrag = () => {
  if (touchDragPreview.value) {
    document.body.removeChild(touchDragPreview.value)
    touchDragPreview.value = null
  }
  dragOverSource.value = false
  dragOverTarget.value = null
  dragData.value = null
  touchDragging.value = false
  lastTouchArea.value = null
}

const handleTouchEnd = async (event) => {
  if (!touchDragging.value) return
  event.preventDefault()

  try {
    // 确定最终的投放位置
    const x = event.changedTouches[0].clientX
    const y = event.changedTouches[0].clientY
    const areaInfo = detectTouchArea(x, y)

    console.log('触摸结束，检测到区域:', areaInfo)

    if (areaInfo.type === 'source') {
      await handleDropToSource()
    } else if (areaInfo.type === 'target' && areaInfo.id) {
      // 验证选区存在性 - 修复类型转换问题
      console.log('验证选区是否存在，当前选区列表:', selectionAreas.value.map(a => a.id))
      console.log('目标选区ID:', areaInfo.id)

      const targetAreaId = parseInt(areaInfo.id)
      const targetArea = selectionAreas.value.find(a => parseInt(a.id) === targetAreaId)

      if (targetArea) {
        console.log(`验证选区 ${targetAreaId} 存在，执行分配`)
        await handleDropToArea(targetAreaId)
      } else {
        console.log(`验证选区 ${targetAreaId} 不存在`)
        showFullscreenMessage('error', '选区不存在')
      }
    } else {
      // 检查是否有选区被检测到但不存在
      const allAreas = document.querySelectorAll('.selection-area')
      let foundArea = false
      for (const area of allAreas) {
        const rect = area.getBoundingClientRect()
        if (x >= rect.left && x <= rect.right && y >= rect.top && y <= rect.bottom) {
          foundArea = true
          break
        }
      }

      if (foundArea) {
        console.log('检测到选区但验证失败')
        showFullscreenMessage('error', '选区不存在')
      } else {
        console.log('未检测到任何有效区域')
        showFullscreenMessage('warning', '请将幼儿拖拽到有效选区')
      }
    }
  } finally {
    cleanupTouchDrag()
  }
}

const handleTouchCancel = () => {
  console.log('触摸取消')
  cleanupTouchDrag()
}

// ========== 原有鼠标拖拽逻辑（保留用于桌面端） ==========

const handleDragStart = (event, type, data) => {
  dragData.value = { type, data }
  event.dataTransfer.effectAllowed = 'move'
  event.target.classList.add('dragging')

  // 创建拖拽预览
  const dragImage = event.target.cloneNode(true)
  dragImage.style.opacity = '0.8'
  dragImage.style.transform = 'scale(1.1)'
  dragImage.classList.add('drag-preview')
  document.body.appendChild(dragImage)
  event.dataTransfer.setDragImage(dragImage, 0, 0)
  setTimeout(() => document.body.removeChild(dragImage), 0)

  // 创建拖拽轨迹效果 - 修复问题3：全屏下彩虹跟随效果
  createDragTrail(event.clientX, event.clientY)
}

const handleDragEnd = () => {
  dragOverSource.value = false
  dragOverTarget.value = null
}

const handleDragEnter = (areaType, areaId = null) => {
  if (areaType === 'source') dragOverSource.value = true
  else if (areaType === 'target') dragOverTarget.value = areaId
}

const handleDragLeave = (areaType) => {
  if (areaType === 'source') dragOverSource.value = false
  else if (areaType === 'target') dragOverTarget.value = null
}

// ========== 触摸拖拽核心逻辑 ==========

const handleDropToSource = async () => {
  if (!dragData.value || dragData.value.type !== 'child') return
  const child = dragData.value.data
  const record = assignedChildren.value.find(r => r.child_id === child.id)
  if (record) {
    try {
      await deleteSelectionRecord(record.id)
      assignedChildren.value = assignedChildren.value.filter(r => r.id !== record.id)
      showFullscreenMessage('success', `${child.name}已取消分配`)
    } catch (error) {
      console.error('取消分配失败:', error)
      showFullscreenMessage('error', '取消分配失败')
    }
  }
}

const handleDropToArea = async (areaId) => {
  if (!dragData.value || dragData.value.type !== 'child') return
  const child = dragData.value.data

  // 验证选区是否存在 - 修复类型转换问题
  console.log('分配前验证选区是否存在，当前选区列表:', selectionAreas.value.map(a => a.id))
  console.log('分配目标选区ID:', areaId)

  const targetAreaId = parseInt(areaId)
  const currentArea = selectionAreas.value.find(a => parseInt(a.id) === targetAreaId)

  if (!currentArea) {
    console.log(`选区 ${targetAreaId} 不存在于当前列表中`)
    showFullscreenMessage('error', '选区不存在')
    return
  }

  const currentCount = getChildrenByArea(targetAreaId).length
  if (currentCount >= currentArea.capacity) {
    showFullscreenMessage('warning', '该选区人数已满')
    return
  }

  const targetArea = document.querySelector(`[data-area-id="${targetAreaId}"]`)
  if (targetArea) {
    targetArea.classList.add('drop-success')
    setTimeout(() => targetArea.classList.remove('drop-success'), 1000)
  }

  // 获取当前时间作为选择时间
  const selectTime = new Date().toISOString()

  const existingRecord = assignedChildren.value.find(r => r && r.child === child.id)
  try {
    if (existingRecord) {
      await updateSelectionRecord(existingRecord.id, {selection_area_id: targetAreaId, select_time: selectTime})
      const index = assignedChildren.value.findIndex(r => r && r.id === existingRecord.id)
      if (index !== -1) {
        assignedChildren.value[index] = {
          ...assignedChildren.value[index],
          selection_area_id: targetAreaId,
          select_time: selectTime
        }
      }
      showFullscreenMessage('success', `${child.name}已重新分配到${currentArea.name}`)
    } else {
      const res = await createSelectionRecord({
        child_id: child.id,
        selection_area_id: targetAreaId,
        select_time: selectTime
      })
      console.log("assignedChildren.value-push", res)
      assignedChildren.value.push(res)
      showFullscreenMessage('success', `${child.name}已分配到${currentArea.name}`)
    }
  } catch (error) {
    console.error('分配失败:', error)
    showFullscreenMessage('error', '分配失败')
  }
}

// ========== 全屏逻辑 ==========

const toggleFullscreen = () => {
  const container = containerRef.value
  if (!container) return ElMessage.error('无法找到容器元素')

  if (!document.fullscreenElement) {
    if (container.requestFullscreen) container.requestFullscreen()
    else if (container.mozRequestFullScreen) container.mozRequestFullScreen()
    else if (container.webkitRequestFullscreen) container.webkitRequestFullscreen()
    else if (container.msRequestFullscreen) container.msRequestFullscreen()
    else return ElMessage.error('浏览器不支持全屏')
    isFullscreen.value = true
  } else {
    if (document.exitFullscreen) document.exitFullscreen()
    else if (document.mozCancelFullScreen) document.mozCancelFullScreen()
    else if (document.webkitExitFullscreen) document.webkitExitFullscreen()
    else if (document.msExitFullscreen) document.msExitFullscreen()
    else return ElMessage.error('无法退出全屏')
    isFullscreen.value = false
  }
  selectKey.value += 1
  updateSelectionAreaWidth()
}

const handleFullscreenChange = () => {
  isFullscreen.value = !!(
      document.fullscreenElement ||
      document.mozFullScreenElement ||
      document.webkitExitFullscreenElement ||
      document.msFullscreenElement
  )
  selectKey.value += 1

  nextTick(() => {
    if (selectedClassId.value) handleClassChange()
  })
}

// 防抖函数
const debounce = (fn, delay) => {
  let timer
  return (...args) => {
    clearTimeout(timer)
    timer = setTimeout(() => fn.apply(this, args), delay)
  }
}

// 窗口大小变化时更新选区宽度
const handleResize = debounce(() => {
  if (selectedClassId.value) {
    updateSelectionAreaWidth()
  }
}, 300)

// 监听屏幕大小变化，更新头像大小
const handleScreenResize = debounce(() => {
  // 触发响应式更新
  selectKey.value += 1
}, 100)

// 在全屏模式下显示消息
const showFullscreenMessage = (type, message) => {
  if (isFullscreen.value) {
    // 在全屏模式下，将消息显示在全屏容器内
    const container = containerRef.value
    if (container) {
      // 创建消息元素
      const messageEl = document.createElement('div')
      messageEl.className = `el-message el-message--${type}`
      messageEl.style.cssText = `
        position: fixed;
        top: 20px;
        left: 50%;
        transform: translateX(-50%);
        z-index: 1000000;
        padding: 15px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        background: ${type === 'success' ? '#f0f9ff' : type === 'error' ? '#fef0f0' : '#fdf6ec'};
        color: ${type === 'success' ? '#67c23a' : type === 'error' ? '#f56c6c' : '#e6a23c'};
        display: flex;
        align-items: center;
        font-size: 14px;
      `

      // 添加图标
      const iconEl = document.createElement('i')
      iconEl.className = `el-message__icon el-icon-${type === 'success' ? 'success' : type === 'error' ? 'error' : 'warning'}`
      iconEl.style.marginRight = '10px'
      messageEl.appendChild(iconEl)

      // 添加文本
      const textEl = document.createElement('p')
      textEl.textContent = message
      textEl.style.margin = '0'
      messageEl.appendChild(textEl)

      // 添加到全屏容器
      container.appendChild(messageEl)

      // 3秒后自动移除
      setTimeout(() => {
        if (messageEl.parentNode) {
          messageEl.parentNode.removeChild(messageEl)
        }
      }, 3000)

      return
    }
  }

  // 非全屏模式下使用默认的 ElMessage
  ElMessage[type](message)
}

// ========== 生命周期 ==========

onMounted(() => {
  fullscreenElement.value = containerRef.value
  document.addEventListener('fullscreenchange', handleFullscreenChange)
  document.addEventListener('mozfullscreenchange', handleFullscreenChange)
  document.addEventListener('webkitfullscreenchange', handleFullscreenChange)
  document.addEventListener('msfullscreenchange', handleFullscreenChange)
  window.addEventListener('resize', handleResize)
  window.addEventListener('resize', handleScreenResize)
  getClassList()

  // 全局样式确保下拉框层级和消息提示在全屏模式下可见
  const style = document.createElement('style')
  style.innerHTML = `
    .el-select-dropdown{z-index:9999!important;}
    .el-message{z-index:999999!important;}
    .el-message-box{z-index:999999!important;}
    /* 修复问题3：全屏下彩虹跟随效果 */
    .drag-trail {
      position: fixed !important;
      z-index: 1000000 !important;
    }
  `
  document.head.appendChild(style)
})

onUnmounted(() => {
  document.removeEventListener('fullscreenchange', handleFullscreenChange)
  document.removeEventListener('mozfullscreenchange', handleFullscreenChange)
  document.removeEventListener('webkitfullscreenchange', handleFullscreenChange)
  document.removeEventListener('msfullscreenchange', handleFullscreenChange)
  window.removeEventListener('resize', handleResize)
  window.removeEventListener('resize', handleScreenResize)
})
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
.floating-particle:nth-child(1) {
  top: 10%;
  left: 10%;
  animation-delay: 0s;
}

.floating-particle:nth-child(2) {
  top: 20%;
  left: 80%;
  animation-delay: 1s;
}

.floating-particle:nth-child(3) {
  top: 30%;
  left: 30%;
  animation-delay: 2s;
}

.floating-particle:nth-child(4) {
  top: 40%;
  left: 70%;
  animation-delay: 3s;
}

.floating-particle:nth-child(5) {
  top: 50%;
  left: 20%;
  animation-delay: 4s;
}

.floating-particle:nth-child(6) {
  top: 60%;
  left: 60%;
  animation-delay: 5s;
}

.floating-particle:nth-child(7) {
  top: 70%;
  left: 40%;
  animation-delay: 6s;
}

.floating-particle:nth-child(8) {
  top: 80%;
  left: 80%;
  animation-delay: 7s;
}

.floating-particle:nth-child(9) {
  top: 15%;
  left: 50%;
  animation-delay: 0.5s;
}

.floating-particle:nth-child(10) {
  top: 25%;
  left: 25%;
  animation-delay: 1.5s;
}

.floating-particle:nth-child(11) {
  top: 35%;
  left: 65%;
  animation-delay: 2.5s;
}

.floating-particle:nth-child(12) {
  top: 45%;
  left: 15%;
  animation-delay: 3.5s;
}

.floating-particle:nth-child(13) {
  top: 55%;
  left: 55%;
  animation-delay: 4.5s;
}

.floating-particle:nth-child(14) {
  top: 65%;
  left: 35%;
  animation-delay: 5.5s;
}

.floating-particle:nth-child(15) {
  top: 75%;
  left: 75%;
  animation-delay: 6.5s;
}

.floating-particle:nth-child(16) {
  top: 85%;
  left: 45%;
  animation-delay: 7.5s;
}

.floating-particle:nth-child(17) {
  top: 12%;
  left: 90%;
  animation-delay: 0.8s;
}

.floating-particle:nth-child(18) {
  top: 22%;
  left: 10%;
  animation-delay: 1.8s;
}

.floating-particle:nth-child(19) {
  top: 32%;
  left: 80%;
  animation-delay: 2.8s;
}

.floating-particle:nth-child(20) {
  top: 42%;
  left: 20%;
  animation-delay: 3.8s;
}

.floating-particle:nth-child(21) {
  top: 52%;
  left: 60%;
  animation-delay: 4.8s;
}

.floating-particle:nth-child(22) {
  top: 62%;
  left: 30%;
  animation-delay: 5.8s;
}

.floating-particle:nth-child(23) {
  top: 72%;
  left: 70%;
  animation-delay: 6.8s;
}

.floating-particle:nth-child(24) {
  top: 82%;
  left: 40%;
  animation-delay: 7.8s;
}

.floating-particle:nth-child(25) {
  top: 18%;
  left: 15%;
  animation-delay: 0.3s;
}

.floating-particle:nth-child(26) {
  top: 28%;
  left: 85%;
  animation-delay: 1.3s;
}

.floating-particle:nth-child(27) {
  top: 38%;
  left: 35%;
  animation-delay: 2.3s;
}

.floating-particle:nth-child(28) {
  top: 48%;
  left: 65%;
  animation-delay: 3.3s;
}

.floating-particle:nth-child(29) {
  top: 58%;
  left: 25%;
  animation-delay: 4.3s;
}

.floating-particle:nth-child(30) {
  top: 68%;
  left: 75%;
  animation-delay: 5.3s;
}

.floating-particle:nth-child(31) {
  top: 5%;
  left: 40%;
  animation-delay: 0.2s;
}

.floating-particle:nth-child(32) {
  top: 15%;
  left: 70%;
  animation-delay: 1.2s;
}

.floating-particle:nth-child(33) {
  top: 25%;
  left: 10%;
  animation-delay: 2.2s;
}

.floating-particle:nth-child(34) {
  top: 35%;
  left: 80%;
  animation-delay: 3.3s;
}

.floating-particle:nth-child(35) {
  top: 45%;
  left: 30%;
  animation-delay: 4.2s;
}

.floating-particle:nth-child(36) {
  top: 55%;
  left: 60%;
  animation-delay: 5.2s;
}

.floating-particle:nth-child(37) {
  top: 65%;
  left: 20%;
  animation-delay: 6.2s;
}

.floating-particle:nth-child(38) {
  top: 75%;
  left: 90%;
  animation-delay: 7.2s;
}

.floating-particle:nth-child(39) {
  top: 85%;
  left: 50%;
  animation-delay: 0.7s;
}

.floating-particle:nth-child(40) {
  top: 95%;
  left: 25%;
  animation-delay: 1.7s;
}

.floating-particle:nth-child(41) {
  top: 8%;
  left: 65%;
  animation-delay: 2.7s;
}

.floating-particle:nth-child(42) {
  top: 18%;
  left: 15%;
  animation-delay: 3.7s;
}

.floating-particle:nth-child(43) {
  top: 28%;
  left: 75%;
  animation-delay: 4.7s;
}

.floating-particle:nth-child(44) {
  top: 38%;
  left: 35%;
  animation-delay: 5.7s;
}

.floating-particle:nth-child(45) {
  top: 48%;
  left: 85%;
  animation-delay: 6.7s;
}

.floating-particle:nth-child(46) {
  top: 58%;
  left: 45%;
  animation-delay: 7.7s;
}

.floating-particle:nth-child(47) {
  top: 68%;
  left: 5%;
  animation-delay: 0.9s;
}

.floating-particle:nth-child(48) {
  top: 78%;
  left: 55%;
  animation-delay: 1.9s;
}

.floating-particle:nth-child(49) {
  top: 88%;
  left: 95%;
  animation-delay: 2.9s;
}

.floating-particle:nth-child(50) {
  top: 3%;
  left: 30%;
  animation-delay: 3.9s;
}

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

/* 拖拽轨迹效果 - 修复问题3：全屏下彩虹跟随效果 */
.drag-trail {
  position: fixed;
  pointer-events: none;
  z-index: 1000000;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(100, 200, 255, 0.8), transparent 70%);
  animation: trailFade 0.5s forwards;
  /* 修复问题3：确保在全屏模式下也可见
  z-index: 1000000 !important;*/
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
  padding-bottom: 8px; /* 防止滚动条遮挡内容 */
}

.selection-area {
  flex: 0 0 auto; /* 改为固定尺寸，由JS控制宽度 */
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
  min-height: 160px;
  /* 宽度由JS动态设置 */
  /* 修复问题2：增加选区检测区域 */
  cursor: pointer;
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
  box-shadow: 0 0 40px #000,
  0 0 80px #000,
  0 0 120px #000;
  z-index: 10;
  animation: blackHolePulse 3s infinite alternate;
}

.area-image-container {
  position: relative;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  border-radius: 12px;
  /* 添加基础炫酷效果 */
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.5);
  transition: all 0.3s ease;
  /* 添加3D透视效果 */
  perspective: 1000px;
}

.area-image-container:hover {
  transform: scale(1.02) rotateY(5deg);
  box-shadow: 0 0 30px rgba(100, 150, 255, 0.7);
}

.area-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
  transition: transform 0.3s ease;
  max-width: 100%;
  max-height: 100%;
  image-rendering: -webkit-optimize-contrast;
  image-rendering: crisp-edges;
  /* 添加滤镜效果增强视觉 */
  filter: saturate(1.2) contrast(1.1);
}

.area-image-container:hover .area-image {
  transform: scale(1.05);
}

.area-name-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  text-align: center;
  padding: 12px;
  font-size: 18px;
  font-weight: bold;
  text-shadow: 0 0 8px rgba(255, 255, 255, 0.5);
  backdrop-filter: blur(2px);
  /* 添加发光效果 */
  box-shadow: 0 -5px 15px rgba(0, 0, 0, 0.5);
  /* 添加霓虹灯效果 */
  border-top: 1px solid rgba(255, 255, 255, 0.2);
}

/* 添加炫酷的悬浮粒子效果 */
.area-image-container::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(
    circle at center,
    rgba(255, 255, 255, 0.1) 0%,
    transparent 70%
  );
  animation: shine 3s infinite;
  pointer-events: none;
  opacity: 0.5;
}

/* 添加动态边框效果 */
.area-image-container::after {
  content: '';
  position: absolute;
  inset: 0;
  border: 2px solid transparent;
  border-radius: 12px;
  background: linear-gradient(45deg, #00dbde, #fc00ff, #00dbde) border-box;
  background-size: 300% 300%;
  mask: linear-gradient(#fff 0 0) padding-box, linear-gradient(#fff 0 0);
  mask-composite: exclude;
  animation: borderAnimation 2s linear infinite;
  pointer-events: none;
  opacity: 0.7;
}

/* 添加额外的炫酷效果层 */
.area-image-container .glow-effect {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  border-radius: 12px;
  opacity: 0.3;
  background: radial-gradient(
    circle at var(--x, 50%) var(--y, 50%),
    rgba(100, 200, 255, 0.8) 0%,
    transparent 70%
  );
  transition: opacity 0.3s ease;
}

.area-image-container:hover .glow-effect {
  opacity: 0.6;
}

/* 添加扫描线效果 */
.area-image-container .scan-line {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 10px;
  background: linear-gradient(to bottom, 
    rgba(255, 255, 255, 0) 0%,
    rgba(255, 255, 255, 0.5) 50%,
    rgba(255, 255, 255, 0) 100%);
  animation: scan 4s linear infinite;
  pointer-events: none;
  opacity: 0.7;
}

.image-placeholder,
.image-error {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  background: #f5f5f5;
  color: #999;
  font-size: 14px;
  /* 添加占位图炫酷效果 */
  background: linear-gradient(45deg, #ddd, #eee, #ddd);
  background-size: 400% 400%;
  animation: gradientBG 3s ease infinite;
}

@keyframes shine {
  0% {
    transform: translate(0, 0);
  }
  50% {
    transform: translate(20%, 20%);
  }
  100% {
    transform: translate(0, 0);
  }
}

@keyframes borderAnimation {
  0% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
}

@keyframes scan {
  0% {
    top: 0;
  }
  100% {
    top: 100%;
  }
}

@keyframes gradientBG {
  0% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
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
.black-hole-particle:nth-child(1) {
  animation-delay: 0s;
}

.black-hole-particle:nth-child(2) {
  animation-delay: 0.4s;
}

.black-hole-particle:nth-child(3) {
  animation-delay: 0.8s;
}

.black-hole-particle:nth-child(4) {
  animation-delay: 1.2s;
}

.black-hole-particle:nth-child(5) {
  animation-delay: 1.6s;
}

.black-hole-particle:nth-child(6) {
  animation-delay: 2s;
}

.black-hole-particle:nth-child(7) {
  animation-delay: 2.4s;
}

.black-hole-particle:nth-child(8) {
  animation-delay: 2.8s;
}

.black-hole-particle:nth-child(9) {
  animation-delay: 3.2s;
}

.black-hole-particle:nth-child(10) {
  animation-delay: 3.6s;
}

.black-hole-particle:nth-child(11) {
  animation-delay: 4s;
}

.black-hole-particle:nth-child(12) {
  animation-delay: 4.4s;
}

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

/* 调试信息显示 */
.debug-info {
  position: absolute;
  top: 5px;
  left: 5px;
  color: rgba(255, 255, 255, 0.7);
  font-size: 12px;
  text-align: center;
  z-index: 15;
  background: rgba(0, 0, 0, 0.5);
  padding: 5px;
  border-radius: 5px;
  pointer-events: none;
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

.selection-operation-container:-webkit-full-screen {
  padding: 10px;
  background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
  min-height: 100vh;
  position: relative;
  z-index: 9998;
}

.selection-operation-container:-moz-full-screen {
  padding: 10px;
  background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
  min-height: 100vh;
  position: relative;
  z-index: 9998;
}

.selection-operation-container:-ms-fullscreen {
  padding: 10px;
  background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
  min-height: 100vh;
  position: relative;
  z-index: 9998;
}

/* 确保班级选择器在全屏模式下可见 */
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

/* 确保下拉框在正确位置 */
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

/* 动态调整幼儿头像大小的响应式样式 */
.child-avatar {
  transition: width 0.3s ease, height 0.3s ease;
}

@media (max-width: 480px) {
  .child-avatar {
    width: 32px !important;
    height: 32px !important;
  }

  .child-name {
    font-size: 12px;
  }
}

@media (min-width: 481px) and (max-width: 768px) {
  .child-avatar {
    width: 40px !important;
    height: 40px !important;
  }

  .child-name {
    font-size: 14px;
  }
}

@media (min-width: 769px) and (max-width: 1024px) {
  .child-avatar {
    width: 44px !important;
    height: 44px !important;
  }

  .child-name {
    font-size: 16px;
  }
}

@media (min-width: 1025px) {
  .child-avatar {
    width: 48px !important;
    height: 48px !important;
  }

  .child-name {
    font-size: 18px;
  }
}

/* 调试面板样式 */
.debug-panel {
  position: fixed;
  bottom: 10px;
  right: 10px;
  background: rgba(0, 0, 0, 0.8);
  color: #fff;
  padding: 10px;
  border-radius: 8px;
  z-index: 1000000;
  font-size: 12px;
  max-width: 300px;
  max-height: 200px;
  overflow-y: auto;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
}

.debug-panel h4 {
  margin: 0 0 8px 0;
  color: #00ffcc;
  border-bottom: 1px solid #444;
  padding-bottom: 4px;
}

.debug-panel p {
  margin: 4px 0;
  line-height: 1.4;
}

/* 在全屏模式下隐藏调试面板 */
.selection-operation-container:fullscreen .debug-panel {
  display: none;
}

/* 幼儿头像包装器 */
.child-avatar-wrapper {
  position: relative;
  display: inline-block;
}

/* 选区历史标记 */
.selection-history-marker {
  position: absolute;
  top: -5px;
  right: -5px;
  background-color: #409EFF;
  color: white;
  border-radius: 50%;
  width: 18px;
  height: 18px;
  font-size: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  box-shadow: 0 0 2px rgba(0, 0, 0, 0.5);
  z-index: 2;
}

</style>