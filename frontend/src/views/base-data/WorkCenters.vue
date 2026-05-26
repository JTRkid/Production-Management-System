<template>
  <div class="page-card">
    <!-- 搜索区域 -->
    <el-form :model="query" inline>
      <el-form-item label="编码">
        <el-input v-model="query.code" placeholder="工作中心编码" clearable />
      </el-form-item>
      <el-form-item label="名称">
        <el-input v-model="query.name" placeholder="工作中心名称" clearable />
      </el-form-item>
      <el-form-item label="所属车间">
        <el-select v-model="query.workshop" placeholder="全部" clearable style="width: 160px">
          <el-option
            v-for="ws in workshops"
            :key="ws.id"
            :label="ws.name"
            :value="ws.id"
          />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="handleSearch">搜索</el-button>
        <el-button @click="handleReset">重置</el-button>
      </el-form-item>
    </el-form>

    <!-- 操作按钮 -->
    <div style="margin-bottom: 16px">
      <el-button type="primary" @click="handleAdd">新增工作中心</el-button>
    </div>

    <!-- 数据表格 -->
    <el-table v-loading="loading" :data="list" border stripe>
      <el-table-column prop="code" label="编码" min-width="120" />
      <el-table-column prop="name" label="名称" min-width="140" />
      <el-table-column prop="workshop_name" label="所属车间" min-width="120" />
      <el-table-column prop="capacity_per_day" label="日产能" width="100" align="right" />
      <el-table-column label="启用状态" width="90">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
            {{ row.is_active ? '启用' : '停用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="160" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
          <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="page-pagination">
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.page_size"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        background
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="fetchData"
        @current-change="fetchData"
      />
    </div>

    <!-- 新增/编辑弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑工作中心' : '新增工作中心'"
      width="560px"
      :close-on-click-modal="false"
      @closed="handleDialogClosed"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="编码" prop="code">
          <el-input v-model="form.code" placeholder="请输入编码" />
        </el-form-item>
        <el-form-item label="名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入名称" />
        </el-form-item>
        <el-form-item label="所属车间" prop="workshop">
          <el-select v-model="form.workshop" placeholder="请选择所属车间" style="width: 100%">
            <el-option
              v-for="ws in workshops"
              :key="ws.id"
              :label="ws.name"
              :value="ws.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="日产能" prop="capacity_per_day">
          <el-input-number v-model="form.capacity_per_day" :min="0" :precision="0" style="width: 100%" />
        </el-form-item>
        <el-form-item label="启用状态" prop="is_active">
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
 * 工作中心管理页面
 * 提供工作中心的增删改查功能，支持按编码/名称/所属车间筛选。
 * 工作中心是生产执行的基本单元，关联车间并记录日产能。
 */

// ── 依赖导入 ──
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { workCenterAPI, workshopAPI } from '@/api'

// ── 响应式状态 ──
const loading = ref(false)          // 列表加载状态
const list = ref([])                // 工作中心列表数据
const dialogVisible = ref(false)    // 新增/编辑弹窗可见性
const isEdit = ref(false)           // 当前是否为编辑模式
const submitLoading = ref(false)    // 提交按钮加载状态
const formRef = ref(null)           // 表单引用
const pagination = reactive({ page: 1, page_size: 10, total: 0 })
const workshops = ref([])           // 车间列表，用于下拉选择

// ── 搜索条件 ──
const query = reactive({
  code: '',
  name: '',
  workshop: '',
})

// ── 表单数据与校验规则 ──
const form = reactive({
  id: null,
  code: '',
  name: '',
  workshop: null,
  capacity_per_day: 0,
  is_active: true,
})

const rules = {
  code: [{ required: true, message: '请输入编码', trigger: 'blur' }],
  name: [{ required: true, message: '请输入名称', trigger: 'blur' }],
  workshop: [{ required: true, message: '请选择所属车间', trigger: 'change' }],
}

// ── 数据获取 ──

/** 获取全部车间列表，用于搜索条件和表单中的车间下拉选择 */
async function fetchWorkshops() {
  try {
    const res = await workshopAPI.list({ page_size: 9999 })
    workshops.value = res.data?.results || res.data || res.results || []
  } catch {
    workshops.value = []
  }
}

/** 获取工作中心分页列表，支持按编码/名称/车间筛选 */
async function fetchData() {
  loading.value = true
  try {
    const params = { page: pagination.page, page_size: pagination.page_size }
    if (query.code) params.code = query.code
    if (query.name) params.name = query.name
    if (query.workshop) params.workshop = query.workshop
    const res = await workCenterAPI.list(params)
    list.value = res.data?.results || res.data || res.results || []
    pagination.total = res.data?.count || res.count || list.value.length
  } catch {
    list.value = []
    pagination.total = 0
  } finally {
    loading.value = false
  }
}

// ── 搜索与重置 ──

function handleSearch() {
  pagination.page = 1
  fetchData()
}

function handleReset() {
  query.code = ''
  query.name = ''
  query.workshop = ''
  pagination.page = 1
  fetchData()
}

// ── 增删改操作 ──

/** 打开新增工作中心弹窗 */
function handleAdd() {
  isEdit.value = false
  resetForm()
  dialogVisible.value = true
}

/** 打开编辑弹窗，将行数据回填到表单 */
function handleEdit(row) {
  isEdit.value = true
  Object.assign(form, {
    id: row.id,
    code: row.code,
    name: row.name,
    workshop: row.workshop || row.workshop,
    capacity_per_day: row.capacity_per_day ?? 0,
    is_active: row.is_active,
  })
  dialogVisible.value = true
}

/** 删除工作中心，需二次确认 */
async function handleDelete(row) {
  try {
    await ElMessageBox.confirm(`确定要删除工作中心「${row.name}」吗？`, '删除确认', {
      type: 'warning',
      confirmButtonText: '确定',
      cancelButtonText: '取消',
    })
    await workCenterAPI.delete(row.id)
    ElMessage.success('删除成功')
    fetchData()
  } catch { /* 取消或不操作 */ }
}

// ── 弹窗表单处理 ──

/** 重置表单数据并清除校验状态 */
function resetForm() {
  form.id = null
  form.code = ''
  form.name = ''
  form.workshop = null
  form.capacity_per_day = 0
  form.is_active = true
  formRef.value?.resetFields()
}

/** 弹窗关闭后自动重置表单 */
function handleDialogClosed() {
  resetForm()
}

/** 提交表单：校验通过后调用新增或更新接口 */
async function handleSubmit() {
  try {
    await formRef.value.validate()
  } catch {
    return
  }
  submitLoading.value = true
  try {
    const data = {
      code: form.code,
      name: form.name,
      workshop: form.workshop,
      capacity_per_day: form.capacity_per_day,
      is_active: form.is_active,
    }
    if (isEdit.value) {
      await workCenterAPI.update(form.id, data)
      ElMessage.success('更新成功')
    } else {
      await workCenterAPI.create(data)
      ElMessage.success('新增成功')
    }
    dialogVisible.value = false
    fetchData()
  } finally {
    submitLoading.value = false
  }
}

// ── 生命周期 ──
onMounted(async () => {
  await fetchWorkshops()
  fetchData()
})
</script>
