import api from './api'

export const categoriesService = {
  // 获取分类列表
  async getCategories(params = {}) {
    const response = await api.get('/categories', { params })
    return response
  },

  // 获取分类详情
  async getCategory(categoryId) {
    const response = await api.get(`/categories/${categoryId}`)
    return response
  },

  // 创建分类
  async createCategory(categoryData) {
    const response = await api.post('/categories', categoryData)
    return response
  },

  // 更新分类
  async updateCategory(categoryId, categoryData) {
    const response = await api.put(`/categories/${categoryId}`, categoryData)
    return response
  },

  // 删除分类
  async deleteCategory(categoryId) {
    const response = await api.delete(`/categories/${categoryId}`)
    return response
  }
}
