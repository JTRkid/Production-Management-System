<template>
  <div class="page-card">
    <!-- 搜索栏 + 操作按钮 -->
    <div class="toolbar">
      <el-input
        v-model="query.search"
        placeholder="搜索车间名称 / 编码"
        clearable
        style="width: 280px"
        @keyup.enter="handleSearch"
        @clear="handleSearch"
      />
      <el-button type="primary" @click="openDialog()">
        <el-icon><Plus /></el-icon>
        添加车间
      </el-button>
    </div>

    <!-- 表格 -->
    <el-table :data="list" v-loading="loading" stripe border style="width: 100%; margin-top: 16px">
      <el-table-column prop="name" label="车间名称" min-width="140" />
      <el-table-column prop="code" label="车间编码" width="120" />
      <el-table-column label="负责人" min-width="120">
        <template #default="{ row }">
          {{ row.manager_name || '-' }}
        </template>
      </el-table-column>
      <el-table-column prop="is_active" label="状态" width="80" align="center">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
            {{ row.is_active ? '启用' : '停用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="170" />
      <el-table-column label="操作" width="160" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="openDialog(row)">编辑</el-button>
          <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="page-pagination">
      <el-pagination
        v-model:current-page="query.page"
        v-model:page-size="query.page_size"
        :total="total"
        :page-sizes="[10, 20, 50]"
        background
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSearch"
        @current-change="handleSearch"
      />
    </div>

    <!-- 弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑车间' : '添加车间'"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="车间名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入车间名称" />
        </el-form-item>
        <el-form-item label="车间编码" prop="code">
          <el-input v-model="form.code" placeholder="请输入车间编码" />
        </el-form-item>
        <el-form-item label="负责人">
          <el-select
            v-model="form.manager"
            placeholder="请选择负责人"
            filterable
            clearable
            style="width: 100%"
          >
            <el-option
              v-for="u in managers"
              :key="u.id"
              :label="u.name + ' (' + u.username + ')'"
              :value="u.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="状态" prop="is_active">
          <el-switch v-model="form.is_active" active-text="启用" inactive-text="停用" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
/**
 * 车间管理页面组件
 * 提供车间信息的增删改查功能，支持指定车间负责人
 * 负责人从车间主任角色的用户中选取
 */
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { workshopAPI, userAPI } from '@/api'

// ── 负责人下拉数据 ──
// 从用户列表中筛选车间主任角色作为负责人选项
const managers = ref([])

async function fetchManagers() {
  try {
    const res = await userAPI.list({ role: 'workshop_director', page_size: 999 })
    managers.value = res.data?.results || res.results || []
  } catch {
    // handled by interceptor
  }
}

// ── 列表数据与分页 ──
const loading = ref(false)
const list = ref([])
const total = ref(0)
const query = reactive({ page: 1, page_size: 10, search: '' })

// 搜索时重置到第一页并重新获取数据
function handleSearch() {
  query.page = query.page || 1
  fetchData()
}

// 从后端获取车间列表（支持分页和关键词搜索）
async function fetchData() {
  loading.value = true
  try {
    const params = { page: query.page, page_size: query.page_size }
    if (query.search) params.search = query.search
    const res = await workshopAPI.list(params)
    list.value = res.data?.results || res.results || []
    total.value = res.data?.count || res.count || 0
  } catch {
    // handled by interceptor
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchData()
  fetchManagers()
})

// ── 删除 ──
// 二次确认后删除车间，成功后刷新列表
function handleDelete(row) {
  ElMessageBox.confirm(`确定要删除车间「${row.name}」吗？此操作不可恢复。`, '警告', {
    type: 'warning',
    confirmButtonText: '确定删除',
  }).then(async () => {
    try {
      await workshopAPI.delete(row.id)
      ElMessage.success('已删除')
      fetchData()
    } catch {
      // handled by interceptor
    }
  }).catch(() => {})
}

// ── 新增/编辑弹窗与表单 ──
const dialogVisible = ref(false)
const isEdit = ref(false)
const submitLoading = ref(false)
const formRef = ref(null)

// 返回空白表单默认值
const defaultForm = () => ({
  id: null,
  name: '',
  code: '',
  manager: null,
  is_active: true,
})

const form = reactive(defaultForm())

const rules = {
  name: [{ required: true, message: '请输入车间名称', trigger: 'blur' }],
  code: [{ required: true, message: '请输入车间编码', trigger: 'blur' }],
}

// 打开弹窗：传入 row 时为编辑模式，否则为新增模式
// 编辑时刷新负责人列表以获取最新数据
function openDialog(row) {
  fetchManagers()
  if (row) {
    isEdit.value = true
    Object.assign(form, {
      id: row.id,
      name: row.name,
      code: row.code,
      manager: row.manager ?? null,
      is_active: row.is_active,
    })
  } else {
    isEdit.value = false
    Object.assign(form, defaultForm())
  }
  formRef.value?.resetFields()
  dialogVisible.value = true
}

// 提交表单：根据 isEdit 判断新增或更新
async function handleSubmit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  submitLoading.value = true
  try {
    const payload = {
      name: form.name,
      code: form.code,
      manager: form.manager,
      is_active: form.is_active,
    }
    if (isEdit.value) {
      await workshopAPI.update(form.id, payload)
      ElMessage.success('更新成功')
    } else {
      await workshopAPI.create(payload)
      ElMessage.success('添加成功')
    }
    dialogVisible.value = false
    fetchData()
  } catch {
    // handled by interceptor
  } finally {
    submitLoading.value = false
  }
}
</script>
