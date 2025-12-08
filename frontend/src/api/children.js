import request from '@/utils/request'

/**
 * 获取幼儿列表
 * @param {Object} params - 查询参数
 * @param {number} params.page - 页码
 * @param {number} params.page_size - 每页大小
 * @param {string} params.name - 幼儿姓名（可选）
 * @param {number} params.class_id - 班级ID（可选）
 * @param {string} params.parent_name - 家长姓名（可选）
 * @param {string} params.parent_phone - 家长电话（可选）
 * @param {string} params.status - 状态（可选，active/inactive）
 * @returns {Promise} - 返回幼儿列表数据
 */
export const getChildrenList = (params) => {
  return request({
    url: 'children/',
    method: 'get',
    params
  })
}

/**
 * 获取幼儿详情
 * @param {number} id - 幼儿ID
 * @returns {Promise} - 返回幼儿详情数据
 */
export const getChildDetail = (id) => {
  return request({
    url: `children/${id}/`,
    method: 'get'
  })
}

/**
 * 创建幼儿
 * @param {Object} data - 幼儿数据
 * @param {string} data.name - 幼儿姓名
 * @param {string} data.gender - 性别（male/female）
 * @param {string} data.birth_date - 出生日期（YYYY-MM-DD）
 * @param {number} data.class_id - 班级ID
 * @param {string} data.enroll_date - 入学日期（YYYY-MM-DD）
 * @param {string} data.id_card - 身份证号（可选）
 * @param {string} data.parent_name - 家长姓名
 * @param {string} data.parent_phone - 家长电话
 * @param {string} data.parent_relation - 家长关系
 * @param {string} data.parent_phone_backup - 备用电话（可选）
 * @param {string} data.home_address - 家庭住址
 * @param {string} data.emergency_contact - 紧急联系人
 * @param {string} data.emergency_phone - 紧急联系电话
 * @param {string} data.remark - 备注（可选）
 * @returns {Promise} - 返回创建结果
 */
export const createChild = (data) => {
  return request({
    url: 'children/',
    method: 'post',
    data
  })
}

/**
 * 更新幼儿信息
 * @param {number} id - 幼儿ID
 * @param {Object} data - 更新数据
 * @returns {Promise} - 返回更新结果
 */
export const updateChild = (id, data) => {
  // 如果数据包含头像文件，使用FormData格式
  if (data instanceof FormData || (typeof data === 'object' && data.avatar && data.avatar instanceof File)) {
    const formData = data instanceof FormData ? data : new FormData();
    
    // 如果是普通对象且包含文件，转换为FormData
    if (!(data instanceof FormData)) {
      Object.keys(data).forEach(key => {
        if (key !== 'avatar' && data[key] !== '') {
          formData.append(key, data[key]);
        }
      });
      if (data.avatar instanceof File) {
        formData.append('avatar', data.avatar);
      }
    }
    
    return request({
      url: `children/${id}/`,
      method: 'put',
      data: formData
    });
  } else {
    // 否则使用JSON格式
    return request({
      url: `children/${id}/`,
      method: 'put',
      data
    });
  }
}

/**
 * 删除幼儿
 * @param {number} id - 幼儿ID
 * @returns {Promise} - 返回删除结果
 */
export const deleteChild = (id) => {
  return request({
    url: `children/${id}/`,
    method: 'delete'
  })
}
/**
 * 批量删除幼儿
 * @param {Array<number>} ids - 幼儿ID数组
 * @returns {Promise} - 返回删除结果
 */
export const batchDeleteChildren = (ids) => {
  return request({
    url: 'children/batch_delete/',
    method: 'post',
    data: { ids }
  })
}


/**
 * 切换幼儿状态
 * @param {number} id - 幼儿ID
 * @param {string} status - 目标状态（active/inactive）
 * @returns {Promise} - 返回状态切换结果
 */
export const toggleChildStatus = (id, status) => {
  return request({
    url: `children/${id}/status/`,
    method: 'patch',
    data: { status }
  })
}

/**
 * 获取班级列表（用于选择）
 * @returns {Promise} - 返回班级列表
 */
export const getClassList = () => {
  return request({
    url: 'classes/options/',
    method: 'get'
  })
}

/**
 * 上传幼儿头像
 * @param {number} childId - 幼儿ID
 * @param {FormData} formData - 包含头像文件的表单数据
 * @returns {Promise} - 返回上传结果
 */
export const uploadChildAvatar = (childId, formData) => {
  return request({
    url: `children/${childId}/upload_avatar/`,
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

/**
 * 删除幼儿头像
 * @param {number} childId - 幼儿ID
 * @returns {Promise} - 返回删除结果
 */
export const deleteChildAvatar = (childId) => {
  return request({
    url: `children/${childId}/delete_avatar/`,
    method: 'delete'
  })
}

/**
 * 获取幼儿统计信息
 * @param {Object} params - 查询参数
 * @param {number} params.kindergarten_id - 幼儿园ID（可选）
 * @param {number} params.class_id - 班级ID（可选）
 * @returns {Promise} - 返回统计数据
 */
export const getChildrenStatistics = (params = {}) => {
  return request({
    url: 'children/statistics/',
    method: 'get',
    params
  })
}

/**
 * 获取幼儿出勤统计
 * @param {Object} params - 查询参数
 * @param {string} params.date_start - 开始日期
 * @param {string} params.date_end - 结束日期
 * @param {number} params.class_id - 班级ID（可选）
 * @returns {Promise} - 返回出勤统计数据
 */
export const getChildrenAttendanceStats = (params) => {
  return request({
    url: 'children/attendance/statistics/',
    method: 'get',
    params
  })
}

/**
 * 批量导入幼儿数据
 * @param {FormData} formData - 包含文件的表单数据
 * @returns {Promise} - 返回导入结果
 */
export const importChildren = (formData) => {
  return request({
    url: 'children/import_data/',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

/**
 * 导出幼儿数据模板
 * @returns {Promise} - 返回模板文件
 */
export const exportChildTemplate = () => {
  return request({
    url: 'children/export_template/',
    method: 'get',
    responseType: 'blob'
  })
}

/**
 * 导出幼儿数据
 * @param {Object} params - 查询参数（与获取列表参数一致）
 * @returns {Promise} - 返回导出的文件流
 */
export const exportChildren = (params) => {
  return request({
    url: 'children/export_data/',
    method: 'get',
    params,
    responseType: 'blob'
  })
}

/**
 * 获取幼儿成长记录
 * @param {number} childId - 幼儿ID
 * @param {Object} params - 查询参数
 * @param {number} params.page - 页码
 * @param {number} params.page_size - 每页大小
 * @returns {Promise} - 返回成长记录列表
 */
export const getChildGrowthRecords = (childId, params) => {
  return request({
    url: `children/${childId}/growth-records/`,
    method: 'get',
    params
  })
}

/**
 * 新增幼儿成长记录
 * @param {number} childId - 幼儿ID
 * @param {Object} data - 记录数据
 * @returns {Promise} - 返回创建结果
 */
export const createChildGrowthRecord = (childId, data) => {
  return request({
    url: `children/${childId}/growth-records/`,
    method: 'post',
    data
  })
}

// 添加default导出
export default {
  getChildrenList,
  getChildDetail,
  createChildGrowthRecord
}