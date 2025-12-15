import api from './api'

export const logService = {
  // 获取日志列表
  async getLogs(params = {}) {
    const response = await api.get('/logs', { params })
    return response.data
  },

  // 清空日志
  async clearLogs() {
    const response = await api.delete('/logs')
    return response.data
  }
}
