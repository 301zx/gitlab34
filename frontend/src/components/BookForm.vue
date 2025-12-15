<template>
  <el-form 
    :model="form" 
    :rules="rules" 
    ref="bookForm"
    label-width="100px"
  >
    <el-form-item label="ISBN" prop="isbn">
      <el-input
        v-model="form.isbn"
        placeholder="请输入ISBN号"
        :disabled="!!book"
      />
    </el-form-item>

    <el-form-item label="书名" prop="title">
      <el-input
        v-model="form.title"
        placeholder="请输入书名"
      />
    </el-form-item>

    <el-form-item label="作者" prop="author">
      <el-input
        v-model="form.author"
        placeholder="请输入作者"
      />
    </el-form-item>

    <el-form-item label="出版社" prop="publisher">
      <el-input
        v-model="form.publisher"
        placeholder="请输入出版社"
      />
    </el-form-item>

    <el-form-item label="出版日期" prop="publish_date">
      <el-date-picker
        v-model="form.publish_date"
        type="date"
        placeholder="选择出版日期"
        value-format="YYYY-MM-DD"
        style="width: 100%"
      />
    </el-form-item>

    <el-form-item label="分类" prop="category_id">
      <el-select
        v-model="form.category_id"
        placeholder="请选择分类"
        style="width: 100%"
      >
        <el-option
          v-for="category in categories"
          :key="category.id"
          :label="category.name"
          :value="category.id"
        />
      </el-select>
    </el-form-item>

    <el-form-item label="总册数" prop="total_copies">
      <el-input-number
        v-model="form.total_copies"
        :min="1"
        :max="1000"
        controls-position="right"
      />
    </el-form-item>

    <el-form-item>
      <el-button type="primary" @click="handleSubmit" :loading="loading">
        {{ book ? '更新' : '添加' }}
      </el-button>
      <el-button @click="handleCancel">取消</el-button>
    </el-form-item>
  </el-form>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { bookService } from '@/services/bookService'

const props = defineProps({
  book: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['success', 'cancel'])

const bookForm = ref()
const loading = ref(false)
const categories = ref([])

const form = reactive({
  isbn: '',
  title: '',
  author: '',
  publisher: '',
  publish_date: '',
  category_id: null,
  total_copies: 1
})

const rules = {
  isbn: [
    { required: true, message: '请输入ISBN号', trigger: 'blur' },
    { pattern: /^[0-9-]+$/, message: 'ISBN号只能包含数字和横线', trigger: 'blur' }
  ],
  title: [
    { required: true, message: '请输入书名', trigger: 'blur' },
    { min: 1, max: 255, message: '书名长度在1到255个字符', trigger: 'blur' }
  ],
  author: [
    { required: true, message: '请输入作者', trigger: 'blur' },
    { min: 1, max: 255, message: '作者长度在1到255个字符', trigger: 'blur' }
  ],
  category_id: [
    { required: true, message: '请选择分类', trigger: 'change' }
  ],
  total_copies: [
    { required: true, message: '请输入总册数', trigger: 'blur' },
    { type: 'number', min: 1, message: '总册数必须大于0', trigger: 'blur' }
  ]
}

// 加载分类数据
const loadCategories = async () => {
  try {
    // 这里需要实现分类服务
    // categories.value = await categoryService.getCategories()
    categories.value = [
      { id: 1, name: '文学' },
      { id: 2, name: '科技' },
      { id: 3, name: '历史' },
      { id: 4, name: '艺术' },
      { id: 5, name: '教育' }
    ]
  } catch (error) {
    console.error('加载分类失败:', error)
  }
}

const handleSubmit = async () => {
  if (!bookForm.value) return

  try {
    await bookForm.value.validate()
    loading.value = true

    if (props.book) {
      // 更新图书
      await bookService.updateBook(props.book.id, form)
      ElMessage.success('图书更新成功')
    } else {
      // 添加图书
      await bookService.createBook(form)
      ElMessage.success('图书添加成功')
    }

    emit('success')
  } catch (error) {
    console.error('操作失败:', error)
    ElMessage.error(error.response?.data?.error || '操作失败')
  } finally {
    loading.value = false
  }
}

const handleCancel = () => {
  emit('cancel')
}

// 监听props.book变化，填充表单数据
watch(() => props.book, (newBook) => {
  if (newBook) {
    Object.keys(form).forEach(key => {
      if (newBook[key] !== undefined) {
        form[key] = newBook[key]
      }
    })
  } else {
    // 重置表单
    Object.keys(form).forEach(key => {
      if (key === 'total_copies') {
        form[key] = 1
      } else {
        form[key] = ''
      }
    })
  }
}, { immediate: true })

onMounted(() => {
  loadCategories()
})
</script>