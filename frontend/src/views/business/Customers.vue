<template>
  <div class="page-card">
    <!-- 顶部操作栏 -->
    <div class="page-toolbar">
      <el-input
        v-model="query.keyword"
        placeholder="请输入客户编码或名称搜索"
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
          新增客户
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
      <el-table-column prop="customer_code" label="客户编码" min-width="120" />
      <el-table-column prop="customer_name" label="客户名称" min-width="160" />
      <el-table-column prop="contact_person" label="联系人" min-width="100" />
      <el-table-column prop="contact_phone" label="联系电话" min-width="130" />
      <el-table-column prop="address" label="地址" min-width="200" show-overflow-tooltip />
      <el-table-column prop="customer_level" label="客户等级" width="100" align="center">
        <template #default="{ row }">
          <el-tag
            :type="levelTagType(row.customer_level)"
            size="small"
          >
            {{ row.customer_level }}
          </el-tag>
        </template>
      </el-table-column>
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
            title="确定要删除该客户吗？"
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
      :title="isEdit ? '编辑客户' : '新增客户'"
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
            <el-form-item label="客户编码" prop="customer_code">
              <el-input v-model="form.customer_code" placeholder="请输入客户编码" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="客户名称" prop="customer_name">
              <el-input v-model="form.customer_name" placeholder="请输入客户名称" />
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
        <el-form-item label="地址" prop="address">
          <el-input v-model="form.address" placeholder="请输入地址" />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="客户等级" prop="customer_level">
              <el-select v-model="form.customer_level" placeholder="请选择客户等级" style="width: 100%">
                <el-option label="A级" value="A" />
                <el-option label="B级" value="B" />
                <el-option label="C级" value="C" />
              </el-select>
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
 * 客户管理页面组件
 * 提供客户信息的增删改查功能
 * 支持按客户编码/名称搜索，客户分ABC等级，可启用/禁用
 */
import { ref, reactive, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Plus } from '@element-plus/icons-vue'
import { customerAPI } from '@/api'

// ── 列表数据与分页 ──
const loading = ref(false)
const list = ref([])
const total = ref(0)
const query = reactive({ keyword: '', page: 1, page_size: 10 })

// 从后端获取客户列表（支持分页和关键词搜索）
async function fetchData() {
  loading.value = true
  try {
    const params = {
      page: query.page,
      page_size: query.page_size,
    }
    if (query.keyword) params.keyword = query.keyword
    const res = await customerAPI.list(params)
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

// 根据客户等级返回 Tag 颜色类型（A=红 B=橙 C=灰）
function levelTagType(level) {
  const map = { A: 'danger', B: 'warning', C: 'info' }
  return map[level] || 'info'
}

// ── 新增/编辑弹窗与表单 ──
const dialogVisible = ref(false)
const isEdit = ref(false)
const submitLoading = ref(false)
const formRef = ref(null)
const editingId = ref(null)

const initialForm = {
  customer_code: '',
  customer_name: '',
  contact_person: '',
  contact_phone: '',
  address: '',
  customer_level: 'B',
  is_active: true,
}
const form = reactive({ ...initialForm })

const rules = {
  customer_code: [{ required: true, message: '请输入客户编码', trigger: 'blur' }],
  customer_name: [{ required: true, message: '请输入客户名称', trigger: 'blur' }],
  contact_person: [{ required: true, message: '请输入联系人', trigger: 'blur' }],
}

// 打开弹窗：传入 row 时为编辑模式，否则为新增模式
function openDialog(row) {
  if (row) {
    isEdit.value = true
    editingId.value = row.id
    Object.assign(form, {
      customer_code: row.customer_code || '',
      customer_name: row.customer_name || '',
      contact_person: row.contact_person || '',
      contact_phone: row.contact_phone || '',
      address: row.address || '',
      customer_level: row.customer_level || 'B',
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
      await customerAPI.update(editingId.value, data)
      ElMessage.success('更新成功')
    } else {
      await customerAPI.create(data)
      ElMessage.success('新增成功')
    }
    dialogVisible.value = false
    fetchData()
  } finally {
    submitLoading.value = false
  }
}

// 删除客户，若当前页只剩一条且非第一页则回退一页
async function handleDelete(id) {
  await customerAPI.delete(id)
  ElMessage.success('删除成功')
  // 如果当前页删除后没有数据且不是第一页，回到上一页
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
