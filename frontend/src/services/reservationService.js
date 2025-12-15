import api from './api'

export const reservationService = {
  // 创建预约
  async createReservation(bookId) {
    const response = await api.post('/reservations', { book_id: bookId })
    return response
  },

  // 取消预约
  async cancelReservation(reservationId) {
    const response = await api.delete(`/reservations/${reservationId}`)
    return response
  },

  // 获取我的预约记录
  async getMyReservations(params = {}) {
    const response = await api.get('/reservations/my', { params })
    return response
  },

  // 获取所有预约记录（管理员）
  async getAllReservations(params = {}) {
    const response = await api.get('/reservations', { params })
    return response
  },

  // 完成预约（管理员）
  async fulfillReservation(reservationId) {
    const response = await api.post(`/reservations/${reservationId}/fulfill`)
    return response
  }
}