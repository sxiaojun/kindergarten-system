import request from '@/utils/request'

/**
 * 获取幼儿园列表
 * @param {Object} params - 查询参数
 * @param {number} params.page - 页码
 * @param {number} params.page_size - 每页数量
 * @param {string} params.name - 幼儿园名称
 * @param {string} params.region - 地区
 * @returns {Promise} - 返回Promise对象
 */
export function getKindergartenList(params) {
  return request({
    url: 'kindergartens/',
    method: 'get',
    params
  })
}

/**
 * 获取幼儿园详情
 * @param {number} id - 幼儿园ID
 * @returns {Promise} - 返回Promise对象
 */
export function getKindergartenDetail(id) {
  return request({
    url: `kindergartens/${id}/`,
    method: 'get'
  })
}

/**
 * 创建幼儿园
 * @param {Object} data - 幼儿园数据
 * @param {string} data.name - 幼儿园名称
 * @param {string} data.region - 地区
 * @param {string} data.address - 地址
 * @param {string} data.contact_person - 联系人
 * @param {string} data.contact_phone - 联系电话
 * @param {string} data.status - 状态
 * @returns {Promise} - 返回Promise对象
 */
export function createKindergarten(data) {
  return request({
    url: 'kindergartens/',
    method: 'post',
    data,
    headers: {
      'Content-Type': 'application/json'
    }
  })
}

/**
 * 更新幼儿园
 * @param {number} id - 幼儿园ID
 * @param {Object} data - 幼儿园数据
 * @returns {Promise} - 返回Promise对象
 */
export function updateKindergarten(id, data) {
  return request({
    url: `kindergartens/${id}/`,
    method: 'put',
    data,
    headers: {
      'Content-Type': 'application/json'
    }
  })
}

/**
 * 删除幼儿园
 * @param {number} id - 幼儿园ID
 * @returns {Promise} - 返回Promise对象
 */
export function deleteKindergarten(id) {
  return request({
    url: `kindergartens/${id}/`,
    method: 'delete'
  })
}

/**
 * 切换幼儿园状态
 * @param {number} id - 幼儿园ID
 * @returns {Promise} - 返回Promise对象
 */
export function toggleKindergartenStatus(id) {
  return request({
    url: `kindergartens/${id}/toggle-status/`,
    method: 'patch'
  })
}

/**
 * 获取幼儿园统计信息
 * @param {number} id - 幼儿园ID
 * @returns {Promise} - 返回Promise对象
 */
export function getKindergartenStats(id) {
  return request({
    url: `kindergartens/${id}/stats/`,
    method: 'get'
  })
}