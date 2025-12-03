import request from '@/utils/request'

/**
 * 获取班级列表
 * @param {Object} params - 查询参数
 * @param {number} params.page - 页码
 * @param {number} params.page_size - 每页数量
 * @param {string} params.name - 班级名称
 * @param {string} params.class_type - 班级类型
 * @param {string} params.head_teacher - 班主任姓名
 * @returns {Promise} - 返回Promise对象
 */
export function getClassList(params) {
  return request({
    url: 'classes/',
    method: 'get',
    params
  })
}

/**
 * 获取班级详情
 * @param {number} id - 班级ID
 * @returns {Promise} - 返回Promise对象
 */
export function getClassDetail(id) {
  return request({
    url: `classes/${id}/`,
    method: 'get'
  })
}

/**
 * 创建班级
 * @param {Object} data - 班级数据
 * @param {string} data.name - 班级名称
 * @param {string} data.class_type - 班级类型
 * @param {number} data.head_teacher_id - 班主任ID
 * @param {number} data.max_capacity - 最大容量
 * @param {string} data.classroom_location - 教室位置
 * @param {string} data.status - 状态
 * @returns {Promise} - 返回Promise对象
 */
export function createClass(data) {
  return request({
    url: 'classes/',
    method: 'post',
    data
  })
}

/**
 * 更新班级
 * @param {number} id - 班级ID
 * @param {Object} data - 班级数据
 * @returns {Promise} - 返回Promise对象
 */
export function updateClass(id, data) {
  return request({
    url: `classes/${id}/`,
    method: 'put',
    data
  })
}

/**
 * 删除班级
 * @param {number} id - 班级ID
 * @returns {Promise} - 返回Promise对象
 */
export function deleteClass(id) {
  return request({
    url: `classes/${id}/`,
    method: 'delete'
  })
}

/**
 * 切换班级状态
 * @param {number} id - 班级ID
 * @returns {Promise} - 返回Promise对象
 */
export function toggleClassStatus(id) {
  return request({
    url: `classes/${id}/toggle-status/`,
    method: 'patch'
  })
}

/**
 * 获取教师列表
 * @returns {Promise} - 返回Promise对象
 */
export function getTeacherList() {
  return request({
    url: 'teachers/',
    method: 'get',
    params: { page_size: 1000 }
  })
}

/**
 * 获取班级选项列表（用于下拉选择）
 * @returns {Promise} - 返回Promise对象
 */
export function getClasses(params) {
  return request({
    url: 'classes/options/',
    method: 'get',
    params
  })
}

/**
 * 批量导入班级数据
 * @param {FormData} formData - 包含Excel文件的表单数据
 * @returns {Promise} - 返回导入结果
 */
export function importClasses(formData) {
  return request({
    url: 'classes/import_data/',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

/**
 * 导出班级数据模板
 * @returns {Promise} - 返回模板文件
 */
export function exportClassTemplate() {
  return request({
    url: 'classes/export_template/',
    method: 'get',
    responseType: 'blob'
  })
}

// 添加default导出
export default {
  getClassList,
  getClassDetail,
  createClass,
  updateClass,
  deleteClass,
  toggleClassStatus,
  getTeacherList,
  getClasses,
  getClassStudents,
  addStudentsToClass,
  removeStudentFromClass,
  importClasses,
  exportClassTemplate
}

/**
 * 获取班级幼儿列表
 * @param {number} classId - 班级ID
 * @param {Object} params - 查询参数
 * @returns {Promise} - 返回Promise对象
 */
export function getClassStudents(classId, params = {}) {
  return request({
    url: `classes/${classId}/students/`,
    method: 'get',
    params
  })
}

/**
 * 添加幼儿到班级
 * @param {number} classId - 班级ID
 * @param {Object} data - 幼儿数据
 * @param {Array} data.student_ids - 幼儿ID列表
 * @returns {Promise} - 返回Promise对象
 */
export function addStudentsToClass(classId, data) {
  return request({
    url: `classes/${classId}/add-students/`,
    method: 'post',
    data
  })
}

/**
 * 从班级移除幼儿
 * @param {number} classId - 班级ID
 * @param {number} studentId - 幼儿ID
 * @returns {Promise} - 返回Promise对象
 */
export function removeStudentFromClass(classId, studentId) {
  return request({
    url: `classes/${classId}/remove-student/${studentId}/`,
    method: 'delete'
  })
}