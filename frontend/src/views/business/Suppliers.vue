<template>
  <div class="page-card">
    <!-- 顶部操作栏 -->
    <div class="page-toolbar">
      <el-input
        v-model="query.keyword"
        placeholder="请输入供应商编码或名称搜索"
        clearable
        style="width: 260px"
        @clear="handleSearch"
        @keyup.enter="handleSearch"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
      <div class="toolbar-actions">
        <el-button type="primary" @click="handleSearch">
          <el-icon><Search /></el-icon>
          搜索
        </el-button>
        <el-button type="success" @click="openDialog()">
          <el-icon><Plus /></el-icon>
          新增供应商
        </el-button>
      </div>
    </div>

    <!-- 表格 -->
    <el-table
      v-loading="loading"
      :data="list"
      border
      stripe
      style="width: 100%; margin-top: 16px"
    >
      <el-table-column prop="supplier_code" label="供应商编码" min-width="130" />
      <el-table-column prop="supplier_name" label="供应商名称" min-width="170" />
      <el-table-column prop="contact_person" label="联系人" min-width="100" />
      <el-table-column prop="contact_phone" label="联系电话" min-width="130" />
      <el-table-column prop="supply_category" label="供应类别" min-width="120" />
      <el-table-column prop="is_active" label="状态" width="80" align="center">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">
            {{ row.is_active ? '启用' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="160" align="center" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" size="small" @click="openDialog(row)">编辑</el-button>
          <el-divider direction="vertical" />
          <el-popconfirm
            title="确定要删除该供应商吗？"
            confirm-button-text="删除"
            cancel-button-text="取消"
            @confirm="handleDelete(row.id)"
          >
            <template #reference>
              <el-button link type="danger" size="small">删除</el-button>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="page-pagination">
      <el-pagination
        v-model:current-page="query.page"
        v-model:page-size="query.page_size"
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        background
        @size-change="handleSearch"
        @current-change="handleSearch"
      />
    </div>

    <!-- 新增/编辑弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑供应商' : '新增供应商'"
      width="600px"
      :close-on-click-modal="false"
      @closed="resetForm"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="供应商编码" prop="supplier_code">
              <el-input v-model="form.supplier_code" placeholder="请输入供应商编码" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="供应商名称" prop="supplier_name">
              <el-input v-model="form.supplier_name" placeholder="请输入供应商名称" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="联系人" prop="contact_person">
              <el-input v-model="form.contact_person" placeholder="请输入联系人" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="联系电话" prop="contact_phone">
              <el-input v-model="form.contact_phone" placeholder="请输入联系电话" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="供应类别" prop="supply_category">
              <el-input v-model="form.supply_category" placeholder="请输入供应类别" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="状态" prop="is_active">
              <el-switch
                v-model="form.is_active"
                active-text="启用"
                inactive-text="禁用"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="地址" prop="address">
          <el-input v-model="form.address" placeholder="请输入地址" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
/**
 * 供应商管理页面组件
 * 提供供应商信息的增删改查功能
 * 支持按供应商编码/名称搜索，可设置供应类别和启用/禁用状态
 */
import { ref, reactive, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Plus } from '@element-plus/icons-vue'
import { supplierAPI } from '@/api'

// ── 列表数据与分页 ──
const loading = ref(false)
const list = ref([])
const total = ref(0)
const query = reactive({ keyword: '', page: 1, page_size: 10 })

// 从后端获取供应商列表（支持分页和关键词搜索）
async function fetchData() {
  loading.value = true
  try {
    const params = { page: query.page, page_size: query.page_size }
    if (query.keyword) params.keyword = query.keyword
    const res = await supplierAPI.list(params)
    list.value = res.data?.results || res.data || res.results || []
    total.value = res.data?.count || res.count || 0
  } finally {
    loading.value = false
  }
}

// 搜索时重置到第一页
function handleSearch() {
  query.page = 1
  fetchData()
}

// ── 新增/编辑弹窗与表单 ──
const dialogVisible = ref(false)
const isEdit = ref(false)
const submitLoading = ref(false)
const formRef = ref(null)
const editingId = ref(null)

const initialForm = {
  supplier_code: '',
  supplier_name: '',
  contact_person: '',
  contact_phone: '',
  address: '',
  supply_category: '',
  is_active: true,
}
const form = reactive({ ...initialForm })

const rules = {
  supplier_code: [{ required: true, message: '请输入供应商编码', trigger: 'blur' }],
  supplier_name: [{ required: true, message: '请输入供应商名称', trigger: 'blur' }],
  contact_person: [{ required: true, message: '请输入联系人', trigger: 'blur' }],
}

// 打开弹窗：传入 row 时为编辑模式，否则为新增模式
function openDialog(row) {
  if (row) {
    isEdit.value = true
    editingId.value = row.id
    Object.assign(form, {
      supplier_code: row.supplier_code || '',
      supplier_name: row.supplier_name || '',
      contact_person: row.contact_person || '',
      contact_phone: row.contact_phone || '',
      address: row.address || '',
      supply_category: row.supply_category || '',
      is_active: row.is_active !== undefined ? row.is_active : true,
    })
  } else {
    isEdit.value = false
    editingId.value = null
    Object.assign(form, { ...initialForm })
  }
  dialogVisible.value = true
  nextTick(() => formRef.value?.clearValidate())
}

// 弹窗关闭时重置表单数据和校验状态
function resetForm() {
  Object.assign(form, { ...initialForm })
  editingId.value = null
  formRef.value?.clearValidate()
}

// ── CRUD 操作 ──
// 提交表单：根据 isEdit 判断新增或更新
async function handleSubmit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  submitLoading.value = true
  try {
    const data = { ...form }
    if (isEdit.value) {
      await supplierAPI.update(editingId.value, data)
      ElMessage.success('更新成功')
    } else {
      await supplierAPI.create(data)
      ElMessage.success('新增成功')
    }
    dialogVisible.value = false
    fetchData()
  } finally {
    submitLoading.value = false
  }
}

// 删除供应商，若当前页只剩一条且非第一页则回退一页
async function handleDelete(id) {
  await supplierAPI.delete(id)
  ElMessage.success('删除成功')
  if (list.value.length === 1 && query.page > 1) {
    query.page--
  }
  fetchData()
}

onMounted(() => fetchData())
</script>

<style scoped>
.page-card {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
}

.page-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

.toolbar-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.page-pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
</style>
