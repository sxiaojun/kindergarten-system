import request from '@/utils/request'

/**
 * 选区管理相关API
 */

// 选区相关API
export function getSelectionAreas(params) {
  return request({
    url: 'selections/selection-areas/',
    method: 'get',
    params
  })
}

export function getSelectionArea(id) {
  return request({
    url: `selections/selection-areas/${id}/`,
    method: 'get'
  })
}

export function createSelectionArea(data) {
  return request({
    url: 'selections/selection-areas/',
    method: 'post',
    data
  })
}

export function updateSelectionArea(id, data) {
  return request({
    url: `selections/selection-areas/${id}/`,
    method: 'put',
    data
  })
}

export function deleteSelectionArea(id) {
  return request({
    url: `selections/selection-areas/${id}/`,
    method: 'delete'
  })
}

// 选区记录相关API
export function getSelectionRecords(params) {
  return request({
    url: 'selections/selection-records/',
    method: 'get',
    params
  })
}

export function getSelectionRecord(id) {
  return request({
    url: `selections/selection-records/${id}/`,
    method: 'get'
  })
}

export function createSelectionRecord(data) {
  return request({
    url: 'selections/selection-records/',
    method: 'post',
    data
  })
}

export function updateSelectionRecord(id, data) {
  return request({
    url: `selections/selection-records/${id}/`,
    method: 'put',
    data
  })
}

export function deleteSelectionRecord(id) {
  return request({
    url: `selections/selection-records/${id}/`,
    method: 'delete'
  })
}

export function batchDeleteSelectionRecords(ids) {
  return request({
    url: 'selections/selection-records/batch-delete/',
    method: 'post',
    data: { ids }
  })
}

export function getSelectionHistory(childId) {
  return request({
    url: `selections/selection-records/history/${childId}/`,
    method: 'get'
  })
}

export function getActiveSelections() {
  return request({
    url: 'selections/selection-records/active/',
    method: 'get'
  })
}

export function endSelection(id) {
  return request({
    url: `selections/selection-records/${id}/end/`,
    method: 'post'
  })
}

export function getRecentActivities(params) {
  return request({
    url: 'selections/recent-activities/',
    method: 'get',
    params
  })
}

// 选区操作相关API
export function startSelection(data) {
  return request({
    url: 'selections/selection-records/start/',
    method: 'post',
    data
  })
}

// 仪表盘统计数据API
export function getDashboardStats(params) {
  return request({
    url: 'selections/dashboard-stats/',
    method: 'get',
    params
  })
}

// 导出选区记录API
export function exportSelectionRecords(params) {
  return request({
    url: 'selections/selection-records/export/',
    method: 'get',
    params,
    responseType: 'blob'
  })
}