import api from './api'

export const borrowService = {
  // 借阅图书
  async borrowBook(bookId) {
    const response = await api.post('/borrow', { book_id: bookId })
    return response
  },

  // 归还图书
  async returnBook(recordId) {
    const response = await api.post(`/return/${recordId}`)
    return response
  },

  // 获取我的借阅记录
  async getMyBorrows(params = {}) {
    const response = await api.get('/borrows/my', { params })
    return response
  },

  // 获取所有借阅记录（管理员）
  async getAllBorrows(params = {}) {
    const response = await api.get('/borrows', { params })
    return response
  },

  // 续借图书
  async renewBook(recordId) {
    const response = await api.post(`/borrows/${recordId}/renew`)
    return response
  }
}