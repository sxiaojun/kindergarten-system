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
              :popper-append-to-body="!isFullscreen"
              :teleported="!isFullscreen"
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
            <div class="children-grid" ref="childrenGridRef">
              <div
                v-for="child in allChildren"
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
                  <el-avatar
                    :size="avatarSize"
                    :src="child.avatar"
                    class="child-avatar"
                  >
                    {{ child.name.charAt(0) }}
                  </el-avatar>

                  <!-- 选区历史标记 -->
                  <div v-if="getChildHasHistory(child.id)" class="selection-history-marker">选</div>

                  <!-- 幼儿姓名 -->
                  <div class="child-name">{{ child.name }}</div>
                </div>
              </div>
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
                <el-image
                  :src="area.image"
                  class="area-image"
                  fit="cover"
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

    <!-- 全屏模式下的拖拽轨迹容器 -->
    <div v-if="isFullscreen" class="drag-trail-container" id="dragTrailContainer"></div>
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
const childrenGridRef = ref(null)
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

// 判断幼儿是否曾经有过选区记录
const getChildHasHistory = (childId) => {
  return assignedChildren.value.some(record => record.child === childId);
}

// 计算未分配幼儿
const unassignedChildren = computed(() => {
  const assignedIds = assignedChildren.value
    .filter(item => item && item.child)
    .map(item => item.child)
  return allChildren.value.filter(child => !assignedIds.includes(child.id))
})

const totalChildren = computed(() => allChildren.value.length)
const assignedTodayCount = computed(() => assignedChildren.value.length)
const unassignedCount = computed(() => totalChildren.value - assignedTodayCount.value)

// 动态计算幼儿头像大小
const avatarSize = computed(() => {
  if (!childrenGridRef.value || allChildren.value.length === 0) return 60

  const container = childrenGridRef.value
  const containerWidth = container.clientWidth
  const containerHeight = container.clientHeight

  if (containerWidth <= 0 || containerHeight <= 0) return 60

  // 计算每行最多可显示的项目数
  const maxItemsPerRow = Math.max(1, Math.floor(containerWidth / 100))
  const maxRows = Math.max(1, Math.ceil(allChildren.value.length / maxItemsPerRow))

  // 计算每行实际需要的项目数
  const itemsPerRow = Math.ceil(Math.sqrt(allChildren.value.length))

  // 计算头像大小，确保所有项目都能在容器内显示
  const horizontalSize = Math.floor(containerWidth / itemsPerRow * 0.85)
  const verticalSize = Math.floor(containerHeight / maxRows * 0.7) // 预留空间给姓名

  // 取较小值作为头像大小，并设置最小和最大限制
  const size = Math.min(horizontalSize, verticalSize)
  return Math.max(Math.min(size, 120), 30)
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

    // 更新选区宽度
    updateSelectionAreaWidth()

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
  trail.style.boxSizing = 'border-box'
  trail.style.border = '1px solid rgba(100, 200, 255, 0.8)'
  trail.style.boxShadow = '0 0 10px rgba(100, 200, 255, 0.8)'

  if (isFullscreen.value) {
    const container = document.getElementById('dragTrailContainer')
    if (container) {
      container.appendChild(trail)
    } else {
      document.body.appendChild(trail)
    }
  } else {
    document.body.appendChild(trail)
  }

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
  preview.style.transform = 'translate(-50%, -50%)'
  preview.style.left = '0'
  preview.style.top = '0'
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
    touchDragPreview.value.style.left = `${x}px`
    touchDragPreview.value.style.top = `${y}px`
  }

  // 创建拖拽轨迹效果
  createDragTrail(x, y)
}

// 检测当前触摸位置的选区
const detectTouchArea = (x, y) => {
  // 1. 首先检查是否在未分配区域
  const unassignedArea = document.querySelector('.unassigned-area')
  if (unassignedArea) {
    const unassignedRect = unassignedArea.getBoundingClientRect()
    if (x >= unassignedRect.left && x <= unassignedRect.right &&
        y >= unassignedRect.top && y <= unassignedRect.bottom) {
      return { type: 'source', id: null }
    }
  }

  // 2. 检查所有选区区域
  const areas = document.querySelectorAll('.selection-area')
  for (const area of areas) {
    const rect = area.getBoundingClientRect()
    if (x >= rect.left && x <= rect.right && y >= rect.top && y <= rect.bottom) {
      const areaId = area.dataset.areaId
      const exists = selectionAreas.value.some(a => parseInt(a.id) === parseInt(areaId))
      if (exists) {
        return { type: 'target', id: areaId }
      } else {
        return { type: 'target', id: areaId }
      }
    }
  }

  // 3. 如果没有找到匹配区域，返回null
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

    if (areaInfo.type === 'source') {
      await handleDropToSource()
    } else if (areaInfo.type === 'target' && areaInfo.id) {
      const targetAreaId = parseInt(areaInfo.id)
      const targetArea = selectionAreas.value.find(a => parseInt(a.id) === targetAreaId)

      if (targetArea) {
        await handleDropToArea(targetAreaId)
      } else {
        showFullscreenMessage('error', '选区不存在')
      }
    } else {
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
        showFullscreenMessage('error', '选区不存在')
      } else {
        showFullscreenMessage('warning', '请将幼儿拖拽到有效选区')
      }
    }
  } finally {
    cleanupTouchDrag()
  }
}

const handleTouchCancel = () => {
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

  // 创建拖拽轨迹效果
  createDragTrail(event.clientX, event.clientY)

  // 保存原始位置
  const originalElement = event.target
  originalElement.dataset.originalPosition = JSON.stringify({
    left: originalElement.offsetLeft,
    top: originalElement.offsetTop
  })
}

const handleDragEnd = () => {
  dragOverSource.value = false
  dragOverTarget.value = null

  // 重置所有正在拖拽的元素
  const draggingElements = document.querySelectorAll('.dragging')
  draggingElements.forEach(el => {
    el.classList.remove('dragging')
  })
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
  const record = assignedChildren.value.find(r => r.child === child.id)
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

  const targetAreaId = parseInt(areaId)
  const currentArea = selectionAreas.value.find(a => parseInt(a.id) === targetAreaId)

  if (!currentArea) {
    showFullscreenMessage('error', '选区不存在')
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
  selectKey.value += 1
}, 100)

// 在全屏模式下显示消息
const showFullscreenMessage = (type, message) => {
  if (isFullscreen.value) {
    const container = containerRef.value
    if (container) {
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

      const iconEl = document.createElement('i')
      iconEl.className = `el-message__icon el-icon-${type === 'success' ? 'success' : type === 'error' ? 'error' : 'warning'}`
      iconEl.style.marginRight = '10px'
      messageEl.appendChild(iconEl)

      const textEl = document.createElement('p')
      textEl.textContent = message
      textEl.style.margin = '0'
      messageEl.appendChild(textEl)

      container.appendChild(messageEl)

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
    .drag-trail {
      position: fixed !important;
      z-index: 1000000 !important;
    }
    .child-avatar {
      display: block !important;
      width: auto !important;
      height: auto !important;
    }
    .child-avatar .el-avatar {
      display: block !important;
    }
    .selection-operation-container:fullscreen .child-item {
      -webkit-user-select: none;
      -moz-user-select: none;
      -ms-user-select: none;
      user-select: none;
    }
    .selection-operation-container:fullscreen .child-item * {
      -webkit-user-select: none;
      -moz-user-select: none;
      -ms-user-select: none;
      user-select: none;
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
  overflow: hidden;
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
  flex: 0 0 40%;
}

.selection-areas-section {
  flex: 0 0 60%;
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
  overflow: hidden;
  display: flex;
  flex-direction: column;
  position: relative;
}

.children-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  grid-auto-rows: minmax(100px, auto);
  gap: 10px;
  flex: 1;
  align-content: flex-start;
  position: relative;
  z-index: 1;
  min-height: 0;
  padding: 5px;
  overflow: hidden;
  width: 100%;
  height: 100%;
  align-items: stretch;
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
  position: relative;
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
  user-select: none;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  min-width: 0;
  min-height: 0;
  box-sizing: border-box;
  width: 100%;
  height: 100%;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
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
  position: fixed !important;
  top: 0;
  left: 0;
  animation: bounceBack 0.5s ease-out forwards;
}

@keyframes bounceBack {
  0% {
    transform: translate(var(--drag-offset-x, 0), var(--drag-offset-y, 0)) scale(1.1);
  }
  70% {
    transform: translate(var(--return-offset-x, 0), var(--return-offset-y, 0)) scale(1.05);
  }
  100% {
    transform: scale(1);
    position: static;
  }
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
  position: fixed;
  pointer-events: none;
  z-index: 1000000;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(100, 200, 255, 0.8), transparent 70%);
  animation: trailFade 0.5s forwards;
  box-sizing: border-box;
  border: 1px solid rgba(100, 200, 255, 0.8);
  box-shadow: 0 0 10px rgba(100, 200, 255, 0.8);
}

@keyframes trailFade {
  to {
    transform: scale(0);
    opacity: 0;
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
  padding-bottom: 8px;
}

.selection-area {
  flex: 0 0 auto;
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
  /* 去掉炫酷效果 */
}

.area-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
  max-width: 100%;
  max-height: 100%;
  image-rendering: -webkit-optimize-contrast;
  image-rendering: crisp-edges;
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
  border-top: 1px solid rgba(255, 255, 255, 0.2);
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
  animation: infallingText 3s linear infinite;
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
  overflow: hidden;
}

.selection-operation-container:-webkit-full-screen {
  padding: 10px;
  background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
  min-height: 100vh;
  position: relative;
  z-index: 9998;
  overflow: hidden;
}

.selection-operation-container:-moz-full-screen {
  padding: 10px;
  background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
  min-height: 100vh;
  position: relative;
  z-index: 9998;
  overflow: hidden;
}

.selection-operation-container:-ms-fullscreen {
  padding: 10px;
  background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
  min-height: 100vh;
  position: relative;
  z-index: 9998;
  overflow: hidden;
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

/* 提升班级选择器下拉框的z-index */
.class-selector-wrapper .el-popper,
.class-selector-card .el-popper {
  z-index: 10008 !important;
}

/* 响应式设计 */
@media (max-width: 1400px) {
  .selection-areas {
    gap: 18px;
  }

  .selection-area {
    min-height: 150px;
  }
}

@media (max-width: 1200px) {
  .selection-areas {
    gap: 16px;
  }

  .selection-area {
    min-height: 140px;
  }
}

@media (max-width: 992px) {
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

  .unassigned-section {
    flex: 0 0 35%;
  }

  .selection-areas-section {
    flex: 0 0 65%;
  }
}

@media (max-width: 576px) {
  .selection-areas {
    gap: 10px;
  }

  .selection-area {
    min-height: 110px;
  }

  .unassigned-section {
    flex: 0 0 30%;
  }

  .selection-areas-section {
    flex: 0 0 70%;
  }
}

@media (max-width: 400px) {
  .selection-areas {
    gap: 8px;
  }

  .selection-area {
    min-height: 100px;
  }
}

/* 全屏模式下的自适应调整 */
.selection-operation-container:fullscreen .unassigned-section {
  flex: 0 0 40%;
}

.selection-operation-container:fullscreen .selection-areas-section {
  flex: 0 0 60%;
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
  touch-action: none;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
}

/* 平板设备上的特殊样式 */
@media (max-width: 1024px) and (pointer: coarse) {
  .selection-area {
    min-height: 180px;
    min-width: 180px;
  }

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
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
}

/* 选区历史标记 - 放在右上角 */
.selection-history-marker {
  position: absolute;
  top: 2px;
  right: 2px;
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
  line-height: 1;
  padding: 0;
  min-width: 18px;
}

/* 幼儿姓名 - 放在左下角 */
.child-name {
  position: absolute;
  bottom: 2px;
  left: 2px;
  background-color: rgba(0, 0, 0, 0.7);
  color: white;
  font-size: 12px;
  padding: 2px 6px;
  border-radius: 4px;
  z-index: 2;
  white-space: nowrap;
  max-width: calc(100% - 25px);
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1.2;
}

/* 幼儿头像自适应 */
.child-avatar {
  display: block !important;
  width: 100% !important;
  height: 100% !important;
  object-fit: cover !important;
}

/* 确保网格项目填满空间 */
.children-grid {
  display: grid !important;
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr)) !important;
  grid-auto-rows: minmax(100px, auto) !important;
  gap: 10px !important;
  flex: 1 !important;
  align-content: flex-start !important;
  position: relative !important;
  z-index: 1 !important;
  min-height: 0 !important;
  padding: 5px !important;
  overflow: hidden !important;
  width: 100% !important;
  height: 100% !important;
  align-items: stretch !important;
}

/* 修正幼儿项样式 */
.child-item {
  display: flex !important;
  flex-direction: column !important;
  align-items: center !important;
  justify-content: center !important;
  text-align: center !important;
  box-sizing: border-box !important;
  width: 100% !important;
  height: 100% !important;
  overflow: hidden !important;
  padding: 0 !important;
  margin: 0 !important;
  position: relative !important;
}

/* 确保头像容器完全填充 */
.child-avatar-wrapper {
  width: 100% !important;
  height: 100% !important;
  position: relative !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  overflow: hidden !important;
  border-radius: 8px !important;
}

/* 确保头像完全填充容器 */
.child-avatar {
  width: 100% !important;
  height: 100% !important;
  border-radius: 8px !important;
  object-fit: cover !important;
}

/* 修正头像大小 */
.child-avatar .el-avatar {
  width: 100% !important;
  height: 100% !important;
  border-radius: 8px !important;
  object-fit: cover !important;
}
</style>