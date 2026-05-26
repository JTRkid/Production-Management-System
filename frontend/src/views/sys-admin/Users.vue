<template>
  <div class="page-card">
    <!-- 搜索栏 + 操作按钮 -->
    <div class="toolbar">
      <el-input
        v-model="query.search"
        placeholder="搜索用户名 / 姓名 / 手机号"
        clearable
        style="width: 280px"
        @keyup.enter="handleSearch"
        @clear="handleSearch"
      />
      <el-button type="primary" @click="openDialog()">
        <el-icon><Plus /></el-icon>
        添加用户
      </el-button>
    </div>

    <!-- 表格 -->
    <el-table :data="list" v-loading="loading" stripe border style="width: 100%; margin-top: 16px">
      <el-table-column prop="username" label="用户名" min-width="120" />
      <el-table-column prop="name" label="姓名" min-width="100" />
      <el-table-column prop="role" label="角色" width="140">
        <template #default="{ row }">
          <el-tag :type="roleTagType(row.role)" size="small">{{ roleLabel(row.role) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="phone" label="手机号" width="140" />
      <el-table-column prop="is_active" label="状态" width="80" align="center">
        <template #default="{ row }">
          <el-switch
            :model-value="row.is_active"
            @change="(val) => handleToggleActive(row, val)"
            active-color="#13ce66"
          />
        </template>
      </el-table-column>
      <el-table-column prop="date_joined" label="创建时间" width="170" />
      <el-table-column label="操作" width="220" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="openDialog(row)">编辑</el-button>
          <el-button link type="warning" @click="handleResetPassword(row)">重置密码</el-button>
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
      :title="isEdit ? '编辑用户' : '添加用户'"
      width="520px"
      :close-on-click-modal="false"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" :disabled="isEdit" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="姓名" prop="name">
          <el-input v-model="form.name" placeholder="请输入姓名" />
        </el-form-item>
        <el-form-item v-if="!isEdit" label="密码" prop="password">
          <el-input v-model="form.password" type="password" placeholder="请输入密码" show-password />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="form.role" placeholder="请选择角色" style="width: 100%">
            <el-option
              v-for="item in roleOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="form.phone" placeholder="请输入手机号" />
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
 * 用户管理页面组件
 * 提供用户的增删改查功能，支持重置密码和启用/禁用账号
 * 角色包括：管理员、计划员、车间主任、班组长、工人、质检员、库管员、业务员、采购员
 */
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { userAPI } from '@/api'

// ── 角色配置 ──
// 系统支持的角色列表及其标签颜色映射
const roleOptions = [
  { label: '系统管理员', value: 'admin' },
  { label: '生产计划员', value: 'planner' },
  { label: '车间主任', value: 'workshop_director' },
  { label: '班组长', value: 'foreman' },
  { label: '工人', value: 'worker' },
  { label: '质检员', value: 'inspector' },
  { label: '库管员', value: 'storekeeper' },
  { label: '业务员', value: 'salesman' },
  { label: '采购员', value: 'purchaser' },
]

// 根据角色值返回中文标签
const roleLabel = (role) => {
  const found = roleOptions.find((r) => r.value === role)
  return found ? found.label : role
}

// 根据角色返回 Element Plus Tag 类型（决定标签颜色）
const roleTagType = (role) => {
  const map = {
    admin: 'danger',
    planner: 'primary',
    workshop_director: 'warning',
    foreman: 'warning',
    worker: '',
    inspector: 'success',
    storekeeper: 'info',
    salesman: '',
    purchaser: 'primary',
  }
  return map[role] || 'info'
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

async function fetchData() {
  loading.value = true
  try {
    const params = { page: query.page, page_size: query.page_size }
    if (query.search) params.search = query.search
    const res = await userAPI.list(params)
    list.value = res.data?.results || res.results || []
    total.value = res.data?.count || res.count || 0
  } catch {
    // handled by interceptor
  } finally {
    loading.value = false
  }
}

onMounted(() => fetchData())

// ── 启用/禁用 ──
// 切换用户启用/禁用状态
async function handleToggleActive(row, val) {
  try {
    await userAPI.toggleActive(row.id)
    row.is_active = val
    ElMessage.success(val ? '已启用' : '已停用')
  } catch {
    // handled by interceptor
  }
}

// ── 重置密码 ──
// 二次确认后重置用户密码为系统默认值
function handleResetPassword(row) {
  ElMessageBox.confirm(`确定要重置用户「${row.username}」的密码吗？`, '提示', {
    type: 'warning',
  }).then(async () => {
    try {
      await userAPI.resetPassword(row.id)
      ElMessage.success('密码已重置')
    } catch {
      // handled by interceptor
    }
  }).catch(() => {})
}

// ── 删除用户 ──
// 二次确认后删除用户，成功后刷新列表
function handleDelete(row) {
  ElMessageBox.confirm(`确定要删除用户「${row.username}」吗？此操作不可恢复。`, '警告', {
    type: 'warning',
    confirmButtonText: '确定删除',
  }).then(async () => {
    try {
      await userAPI.delete(row.id)
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

// 返回空白表单默认值（每次打开新增弹窗时重置）
const defaultForm = () => ({
  id: null,
  username: '',
  name: '',
  password: '',
  role: '',
  phone: '',
})

const form = reactive(defaultForm())

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码不能少于6位', trigger: 'blur' },
  ],
  role: [{ required: true, message: '请选择角色', trigger: 'change' }],
}

// 打开弹窗：传入 row 时为编辑模式，否则为新增模式
function openDialog(row) {
  if (row) {
    isEdit.value = true
    Object.assign(form, {
      id: row.id,
      username: row.username,
      name: row.name,
      password: '',
      role: row.role,
      phone: row.phone || '',
    })
  } else {
    isEdit.value = false
    Object.assign(form, defaultForm())
  }
  formRef.value?.resetFields()
  dialogVisible.value = true
}

// 提交表单：新增时包含密码字段，编辑时不含密码
async function handleSubmit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  submitLoading.value = true
  try {
    const payload = {
      username: form.username,
      name: form.name,
      role: form.role,
      phone: form.phone,
    }
    if (!isEdit.value) {
      payload.password = form.password
      await userAPI.create(payload)
      ElMessage.success('添加成功')
    } else {
      await userAPI.update(form.id, payload)
      ElMessage.success('更新成功')
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
