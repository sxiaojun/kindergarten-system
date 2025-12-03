import request from '@/utils/request'

/**
 * 获取教师列表
 * @param {Object} params - 查询参数
 * @param {number} params.page - 页码
 * @param {number} params.page_size - 每页数量
 * @param {string} params.name - 教师姓名
 * @param {string} params.employee_id - 工号
 * @param {string} params.phone - 手机号码
 * @param {string} params.position - 职位
 * @returns {Promise} - 返回Promise对象
 */
export function getTeacherList(params) {
  return request({
    url: 'teachers/',
    method: 'get',
    params
  })
}

/**
 * 获取教师详情
 * @param {number} id - 教师ID
 * @returns {Promise} - 返回Promise对象
 */
export function getTeacherDetail(id) {
  return request({
    url: `teachers/${id}/`,
    method: 'get'
  })
}

/**
 * 创建教师
 * @param {Object} data - 教师数据
 * @returns {Promise} - 返回Promise对象
 */
export function createTeacher(data) {
  return request({
    url: 'teachers/',
    method: 'post',
    data
  })
}

/**
 * 更新教师
 * @param {number} id - 教师ID
 * @param {Object} data - 教师数据
 * @returns {Promise} - 返回Promise对象
 */
export function updateTeacher(id, data) {
  return request({
    url: `teachers/${id}/`,
    method: 'put',
    data
  })
}

/**
 * 删除教师
 * @param {number} id - 教师ID
 * @returns {Promise} - 返回Promise对象
 */
export function deleteTeacher(id) {
  return request({
    url: `teachers/${id}/`,
    method: 'delete'
  })
}

/**
 * 获取班级列表（用于教师管理页面选择班级）
 * @returns {Promise} - 返回Promise对象
 */
export function getClassList() {
  return request({
    url: 'classes/',
    method: 'get',
    params: { page_size: 1000 }
  })
}

/**
 * 获取教师的班级信息
 * @param {number} id - 教师ID
 * @returns {Promise} - 返回Promise对象
 */
export function getTeacherClasses(id) {
  return request({
    url: `teachers/${id}/classes/`,
    method: 'get'
  })
}

/**
 * 更新教师状态
 * @param {number} id - 教师ID
 * @param {string} status - 状态
 * @returns {Promise} - 返回Promise对象
 */
export function updateTeacherStatus(id, status) {
  return request({
    url: `teachers/${id}/update-status/`,
    method: 'patch',
    data: { status }
  })
}

/**
 * 批量导入教师数据
 * @param {FormData} formData - 包含Excel文件的表单数据
 * @returns {Promise} - 返回导入结果
 */
export function importTeachers(formData) {
  return request({
    url: 'teachers/import_data/',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

/**
 * 导出教师数据模板
 * @returns {Promise} - 返回模板文件
 */
export function exportTeacherTemplate() {
  return request({
    url: 'teachers/export_template/',
    method: 'get',
    responseType: 'blob'
  })
}