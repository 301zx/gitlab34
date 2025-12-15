import api from './api'

export const bookService = {
  // 获取图书列表
  async getBooks(params = {}) {
    const response = await api.get('/books', { params })
    return response
  },

  // 获取单个图书详情
  async getBook(id) {
    const response = await api.get(`/books/${id}`)
    return response
  },

  // 创建图书
  async createBook(bookData) {
    const response = await api.post('/books', bookData)
    return response
  },

  // 更新图书
  async updateBook(id, bookData) {
    const response = await api.put(`/books/${id}`, bookData)
    return response
  },

  // 删除图书
  async deleteBook(id) {
    const response = await api.delete(`/books/${id}`)
    return response
  },

  // 搜索图书
  async searchBooks(keyword, params = {}) {
    const response = await api.get('/books', {
      params: { search: keyword, ...params }
    })
    return response
  }
}