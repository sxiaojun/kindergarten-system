import request from '@/utils/request'

/**
 * 用户管理相关API
 */
export default {
  /**
   * 获取用户列表
   * @param {Object} params - 查询参数
   * @returns {Promise}
   */
  getUserList(params) {
    return request({
      url: 'auth/users/',
      method: 'get',
      params
    })
  },

  /**
   * 获取用户详情
   * @param {number} id - 用户ID
   * @returns {Promise}
   */
  getUserDetail(id) {
    return request({
      url: `auth/users/${id}/`,
      method: 'get'
    })
  },

  /**
   * 创建用户
   * @param {Object} data - 用户数据
   * @returns {Promise}
   */
  createUser(data) {
    return request({
      url: 'auth/users/',
      method: 'post',
      data
    })
  },

  /**
   * 更新用户
   * @param {number} id - 用户ID
   * @param {Object} data - 用户数据
   * @returns {Promise}
   */
  updateUser(id, data) {
    return request({
      url: `auth/users/${id}/`,
      method: 'put',
      data
    })
  },

  /**
   * 删除用户
   * @param {number} id - 用户ID
   * @returns {Promise}
   */
  deleteUser(id) {
    return request({
      url: `auth/users/${id}/`,
      method: 'delete'
    })
  },

  /**
   * 激活用户
   * @param {number} id - 用户ID
   * @returns {Promise}
   */
  activateUser(id) {
    return request({
      url: `auth/users/${id}/activate/`,
      method: 'post'
    })
  },

  /**
   * 停用用户
   * @param {number} id - 用户ID
   * @returns {Promise}
   */
  deactivateUser(id) {
    return request({
      url: `auth/users/${id}/deactivate/`,
      method: 'post'
    })
  }
}