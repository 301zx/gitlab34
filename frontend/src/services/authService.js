import api from './api'

export const authService = {
  // 用户登录
  async login(credentials) {
    const response = await api.post('/auth/login', credentials)
    return response
  },

  // 用户注册
  async register(userData) {
    const response = await api.post('/auth/register', userData)
    return response
  },

  // 获取当前用户信息
  async getCurrentUser() {
    const response = await api.get('/auth/me')
    return response
  },

  // 刷新token
  async refreshToken() {
    const response = await api.post('/auth/refresh')
    return response
  }
}