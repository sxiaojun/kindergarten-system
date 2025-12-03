import request from '@/utils/request'

/**
 * 用户登录
 * @param {Object} data - 登录信息
 * @param {string} data.username - 用户名
 * @param {string} data.password - 密码
 * @param {string} data.captcha - 验证码
 * @param {string} data.captchaKey - 验证码key
 * @returns {Promise} 登录结果
 */
export function login(data) {
  return request({
    url: 'auth/login/',
    method: 'post',
    data
  })
}

/**
 * 用户登出
 * @returns {Promise} 登出结果
 */
export function logout() {
  return request({
    url: 'auth/logout/',
    method: 'post'
  })
}

/**
 * 获取验证码
 * @returns {Promise} 验证码图片和key
 */
export function getCaptcha() {
  return request({
    url: 'auth/inter_captcha/',
    method: 'get'
  })
}

/**
 * 获取用户信息
 * @returns {Promise} 用户信息
 */
export function getUserInfo() {
  return request({
    url: 'auth/users/me/',
    method: 'get'
  })
}

/**
 * 修改当前用户密码（无需旧密码）
 * @param {Object} data - 密码信息
 * @param {string} data.new_password - 新密码
 * @returns {Promise} 修改结果
 */
export function changeCurrentUserPassword(data) {
  return request({
    url: 'auth/users/change_password/',
    method: 'post',
    data
  })
}

/**
 * 修改指定用户密码（管理员功能，无需旧密码）
 * @param {Object} data - 密码信息
 * @param {string} data.username - 用户名
 * @param {string} data.new_password - 新密码
 * @param {string} data.captcha - 验证码
 * @param {string} data.captcha_key - 验证码key
 * @returns {Promise} 修改结果
 */
export function changePassword(data) {
  return request({
    url: 'auth/change_password/',
    method: 'post',
    data
  })
}
