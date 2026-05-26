<template>
  <div class="page-card">
    <!-- 搜索区域 -->
    <el-form :model="query" inline>
      <el-form-item label="设备编码">
        <el-input v-model="query.code" placeholder="设备编码" clearable />
      </el-form-item>
      <el-form-item label="设备名称">
        <el-input v-model="query.name" placeholder="设备名称" clearable />
      </el-form-item>
      <el-form-item label="状态">
        <el-select v-model="query.status" placeholder="全部" clearable style="width: 140px">
          <el-option label="正常" value="normal" />
          <el-option label="维修中" value="maintenance" />
          <el-option label="已报废" value="scrapped" />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="handleSearch">搜索</el-button>
        <el-button @click="handleReset">重置</el-button>
      </el-form-item>
    </el-form>

    <!-- 操作按钮 -->
    <div style="margin-bottom: 16px">
      <el-button type="primary" @click="handleAdd">新增设备</el-button>
    </div>

    <!-- 数据表格 -->
    <el-table v-loading="loading" :data="list" border stripe>
      <el-table-column prop="code" label="设备编码" min-width="120" />
      <el-table-column prop="name" label="设备名称" min-width="140" />
      <el-table-column prop="model" label="规格型号" min-width="140" />
      <el-table-column prop="work_center_name" label="所属工作中心" min-width="140" />
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="statusTag(row.status)" size="small">
            {{ statusLabel(row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="采购日期" width="120">
        <template #default="{ row }">
          {{ row.purchase_date || '-' }}
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
      :title="isEdit ? '编辑设备' : '新增设备'"
      width="560px"
      :close-on-click-modal="false"
      @closed="handleDialogClosed"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="设备编码" prop="code">
          <el-input v-model="form.code" placeholder="请输入设备编码" />
        </el-form-item>
        <el-form-item label="设备名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入设备名称" />
        </el-form-item>
        <el-form-item label="规格型号" prop="model">
          <el-input v-model="form.model" placeholder="请输入规格型号" />
        </el-form-item>
        <el-form-item label="所属工作中心" prop="work_center">
          <el-select v-model="form.work_center" placeholder="请选择工作中心" filterable style="width: 100%">
            <el-option
              v-for="wc in workCenters"
              :key="wc.id"
              :label="wc.name || wc.code"
              :value="wc.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="设备状态" prop="status">
          <el-select v-model="form.status" placeholder="请选择状态" style="width: 100%">
            <el-option label="正常" value="normal" />
            <el-option label="维修中" value="maintenance" />
            <el-option label="已报废" value="scrapped" />
          </el-select>
        </el-form-item>
        <el-form-item label="采购日期" prop="purchase_date">
          <el-date-picker
            v-model="form.purchase_date"
            type="date"
            placeholder="选择采购日期"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
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
 * 设备台账管理页面
 * 提供设备信息的增删改查功能，支持按编码/名称/状态筛选。
 * 设备关联工作中心，可记录设备状态（正常/维修中/已报废）及采购日期。
 */

// ── 依赖导入 ──
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { equipmentAPI, workCenterAPI } from '@/api'

// ── 响应式状态 ──
const loading = ref(false)          // 列表加载状态
const list = ref([])                // 设备列表数据
const dialogVisible = ref(false)    // 新增/编辑弹窗可见性
const isEdit = ref(false)           // 当前是否为编辑模式
const submitLoading = ref(false)    // 提交按钮加载状态
const formRef = ref(null)           // 表单引用
const pagination = reactive({ page: 1, page_size: 10, total: 0 })
const workCenters = ref([])         // 工作中心列表，用于下拉选择

// ── 搜索条件 ──
const query = reactive({
  code: '',
  name: '',
  status: '',
})

// ── 表单数据与校验规则 ──
const form = reactive({
  id: null,
  code: '',
  name: '',
  model: '',
  work_center: null,
  status: 'normal',
  purchase_date: '',
})

const rules = {
  code: [{ required: true, message: '请输入设备编码', trigger: 'blur' }],
  name: [{ required: true, message: '请输入设备名称', trigger: 'blur' }],
  work_center: [{ required: true, message: '请选择所属工作中心', trigger: 'change' }],
  status: [{ required: true, message: '请选择设备状态', trigger: 'change' }],
}

// ── 辅助函数 ──

/** 根据设备状态返回对应的 Tag 样式类型 */
function statusTag(status) {
  const map = { normal: 'success', maintenance: 'warning', scrapped: 'danger' }
  return map[status] || 'info'
}

/** 将设备状态代码转换为中文标签 */
function statusLabel(status) {
  const map = { normal: '正常', maintenance: '维修中', scrapped: '已报废' }
  return map[status] || status
}

// ── 数据获取 ──

/** 获取全部工作中心，用于表单中的所属工作中心下拉选择 */
async function fetchWorkCenters() {
  try {
    const res = await workCenterAPI.list({ page_size: 9999 })
    workCenters.value = res.data?.results || res.data || res.results || []
  } catch {
    workCenters.value = []
  }
}

/** 获取设备分页列表，支持按编码/名称/状态筛选 */
async function fetchData() {
  loading.value = true
  try {
    const params = { page: pagination.page, page_size: pagination.page_size }
    if (query.code) params.code = query.code
    if (query.name) params.name = query.name
    if (query.status) params.status = query.status
    const res = await equipmentAPI.list(params)
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
  query.status = ''
  pagination.page = 1
  fetchData()
}

// ── 增删改操作 ──

/** 打开新增设备弹窗 */
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
    model: row.model || '',
    work_center: row.work_center || row.work_center,
    status: row.status,
    purchase_date: row.purchase_date || '',
  })
  dialogVisible.value = true
}

/** 删除设备，需二次确认 */
async function handleDelete(row) {
  try {
    await ElMessageBox.confirm(`确定要删除设备「${row.name}」吗？`, '删除确认', {
      type: 'warning',
      confirmButtonText: '确定',
      cancelButtonText: '取消',
    })
    await equipmentAPI.delete(row.id)
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
  form.model = ''
  form.work_center = null
  form.status = 'normal'
  form.purchase_date = ''
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
      model: form.model,
      work_center: form.work_center,
      status: form.status,
      purchase_date: form.purchase_date || null,
    }
    if (isEdit.value) {
      await equipmentAPI.update(form.id, data)
      ElMessage.success('更新成功')
    } else {
      await equipmentAPI.create(data)
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
  await fetchWorkCenters()
  fetchData()
})
</script>
