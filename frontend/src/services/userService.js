import api from './api'

export const userService = {
  // 获取用户列表
  async getUsers(params = {}) {
    const response = await api.get('/users', { params })
    return response
  },

  // 获取单个用户详情
  async getUser(id) {
    const response = await api.get(`/users/${id}`)
    return response
  },

  // 更新用户信息
  async updateUser(id, userData) {
    const response = await api.put(`/users/${id}`, userData)
    return response
  },

  // 删除用户
  async deleteUser(id) {
    const response = await api.delete(`/users/${id}`)
    return response
  },

  // 更新个人资料
  async updateProfile(userData) {
    const response = await api.put('/auth/profile', userData)
    return response
  },

  // 创建用户（管理员）
  async createUser(userData) {
    const response = await api.post('/users', userData)
    return response
  }
}