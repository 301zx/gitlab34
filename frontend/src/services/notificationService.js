import api from './api'

export const notificationService = {
  // 获取通知列表
  async getNotifications(params = {}) {
    const response = await api.get('/notifications', { params })
    return response
  },

  // 标记通知为已读
  async markAsRead(notificationId) {
    const response = await api.put(`/notifications/${notificationId}/read`)
    return response
  },

  // 标记所有通知为已读
  async markAllAsRead() {
    const response = await api.put('/notifications/read-all')
    return response
  },

  // 删除通知
  async deleteNotification(notificationId) {
    const response = await api.delete(`/notifications/${notificationId}`)
    return response
  }
}