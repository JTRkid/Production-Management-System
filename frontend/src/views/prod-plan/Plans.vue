<template>
  <div class="page-card">
    <!-- 搜索栏 -->
    <el-form :model="query" inline>
      <el-form-item label="计划单号">
        <el-input v-model="query.plan_no" placeholder="输入单号" clearable style="width:180px" />
      </el-form-item>
      <el-form-item label="计划类型">
        <el-select v-model="query.plan_type" placeholder="全部" clearable style="width:140px">
          <el-option label="MPS" value="MPS" />
          <el-option label="MRP" value="MRP" />
          <el-option label="手工" value="手工" />
        </el-select>
      </el-form-item>
      <el-form-item label="状态">
        <el-select v-model="query.status" placeholder="全部" clearable style="width:140px">
          <el-option label="草稿" value="draft" />
          <el-option label="已审批" value="approved" />
          <el-option label="已下达" value="released" />
          <el-option label="已完成" value="completed" />
          <el-option label="已取消" value="cancelled" />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="fetchData">查询</el-button>
        <el-button @click="resetQuery">重置</el-button>
      </el-form-item>
    </el-form>

    <!-- 操作按钮 -->
    <div style="margin-bottom:12px">
      <el-button type="primary" @click="openDialog()">新增计划</el-button>
    </div>

    <!-- 表格 -->
    <el-table :data="list" v-loading="loading" border stripe>
      <el-table-column prop="plan_no" label="计划单号" min-width="140" />
      <el-table-column prop="plan_type" label="计划类型" width="90">
        <template #default="{ row }">
          <el-tag>{{ row.plan_type }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="product_name" label="产品" min-width="140" />
      <el-table-column prop="plan_quantity" label="计划数量" width="100" align="right" />
      <el-table-column prop="scheduled_start" label="计划开始" width="110" />
      <el-table-column prop="scheduled_end" label="计划结束" width="110" />
      <el-table-column prop="status" label="状态" width="90">
        <template #default="{ row }">
          <el-tag :type="statusType(row.status)">{{ statusLabel(row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_by_name" label="创建人" width="100" />
      <el-table-column label="操作" width="260" fixed="right">
        <template #default="{ row }">
          <el-button v-if="row.status === 'draft'" link type="warning" @click="handleApprove(row)">审批</el-button>
          <el-button v-if="row.status === 'approved'" link type="success" @click="handleRelease(row)">下达</el-button>
          <el-button v-if="row.status === 'approved'" link type="danger" @click="handleCancel(row)">取消</el-button>
          <el-button v-if="row.status === 'draft'" link type="primary" @click="openDialog(row)">编辑</el-button>
          <el-button v-if="row.status === 'draft'" link type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="page-pagination">
      <el-pagination
        v-model:current-page="query.page"
        v-model:page-size="query.page_size"
        :total="total"
        background
        layout="total, sizes, prev, pager, next, jumper"
        @current-change="fetchData"
        @size-change="fetchData"
      />
    </div>

    <!-- 新增/编辑弹窗 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑计划' : '新增计划'" width="560px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="计划单号" prop="plan_no">
          <el-input v-model="form.plan_no" placeholder="自动生成可留空" />
        </el-form-item>
        <el-form-item label="计划类型" prop="plan_type">
          <el-select v-model="form.plan_type" placeholder="请选择" style="width:100%">
            <el-option label="MPS" value="MPS" />
            <el-option label="MRP" value="MRP" />
            <el-option label="手工" value="手工" />
          </el-select>
        </el-form-item>
        <el-form-item label="产品" prop="product">
          <el-select v-model="form.product" placeholder="请选择成品物料" filterable style="width:100%">
            <el-option v-for="m in materials" :key="m.id" :label="m.name" :value="m.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="计划数量" prop="plan_quantity">
          <el-input-number v-model="form.plan_quantity" :min="1" style="width:100%" />
        </el-form-item>
        <el-form-item label="计划开始" prop="scheduled_start">
          <el-date-picker v-model="form.scheduled_start" type="date" placeholder="选择日期" style="width:100%" value-format="YYYY-MM-DD" />
        </el-form-item>
        <el-form-item label="计划结束" prop="scheduled_end">
          <el-date-picker v-model="form.scheduled_end" type="date" placeholder="选择日期" style="width:100%" value-format="YYYY-MM-DD" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">确认</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
/**
 * 生产计划管理页面
 * 提供生产计划的增删改查功能，支持计划单号/类型/状态筛选。
 * 计划包含完整生命周期：草稿 -> 已审批 -> 已下达 -> 已完成/已取消，
 * 支持审批、下达、取消等流程操作。
 */

// ── 依赖导入 ──
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { prodPlanAPI, materialAPI } from '@/api'

// ── 响应式状态 ──
const loading = ref(false)          // 列表加载状态
const submitting = ref(false)       // 表单提交加载状态
const list = ref([])                // 计划列表数据
const total = ref(0)                // 总记录数
const dialogVisible = ref(false)    // 新增/编辑弹窗可见性
const isEdit = ref(false)           // 当前是否为编辑模式
const editId = ref(null)            // 当前编辑的计划 ID
const formRef = ref(null)           // 表单引用
const materials = ref([])           // 成品物料列表，用于产品下拉

// ── 搜索条件 ──
const query = reactive({ page: 1, page_size: 10, plan_no: '', plan_type: '', status: '' })

// ── 表单数据与校验规则 ──
const form = reactive({
  plan_no: '',
  plan_type: '',
  product: null,
  plan_quantity: 1,
  scheduled_start: '',
  scheduled_end: '',
})

const rules = {
  plan_type: [{ required: true, message: '请选择计划类型', trigger: 'change' }],
  product: [{ required: true, message: '请选择产品', trigger: 'change' }],
  plan_quantity: [{ required: true, message: '请输入计划数量', trigger: 'blur' }],
}

// ── 辅助函数 ──

/** 根据计划状态返回对应的 Tag 样式类型 */
function statusType(status) {
  const map = { draft: 'info', approved: 'warning', released: 'primary', completed: 'success', cancelled: 'danger' }
  return map[status] || 'info'
}

/** 将计划状态代码转换为中文标签 */
function statusLabel(status) {
  const map = { draft: '草稿', approved: '已审批', released: '已下达', completed: '已完成', cancelled: '已取消' }
  return map[status] || status
}

// ── 数据获取 ──

/** 加载已启用的成品物料，用于新增计划时选择产品 */
async function loadMaterials() {
  try {
    const res = await materialAPI.active()
    const data = res.data || res || []
    materials.value = (Array.isArray(data) ? data : []).filter(m => m.material_type === 'finished' || m.material_type === '成品')
  } catch { /* ignore */ }
}

/** 获取生产计划分页列表，过滤空查询参数后请求 */
async function fetchData() {
  loading.value = true
  try {
    const params = { ...query }
    Object.keys(params).forEach(k => { if (params[k] === '' || params[k] === null || params[k] === undefined) delete params[k] })
    const res = await prodPlanAPI.list(params)
    list.value = res.data?.results || res.data || res.results || []
    total.value = res.data?.count || res.count || 0
  } catch { /* handled by interceptor */ }
  finally { loading.value = false }
}

// ── 搜索与重置 ──

/** 清空所有搜索条件并重新查询 */
function resetQuery() {
  query.plan_no = ''
  query.plan_type = ''
  query.status = ''
  query.page = 1
  fetchData()
}

// ── 增删改弹窗操作 ──

/**
 * 打开新增/编辑弹窗
 * 传入 row 参数时为编辑模式，回填数据；不传则为新增模式
 */
function openDialog(row) {
  if (row) {
    isEdit.value = true
    editId.value = row.id
    Object.assign(form, {
      plan_no: row.plan_no || '',
      plan_type: row.plan_type || '',
      product: row.product || null,
      plan_quantity: row.plan_quantity || 1,
      scheduled_start: row.scheduled_start || '',
      scheduled_end: row.scheduled_end || '',
    })
  } else {
    isEdit.value = false
    editId.value = null
    Object.assign(form, { plan_no: '', plan_type: '', product: null, plan_quantity: 1, scheduled_start: '', scheduled_end: '' })
  }
  dialogVisible.value = true
}

/** 提交表单：校验后调用新增或更新接口 */
async function handleSubmit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  submitting.value = true
  try {
    const payload = { ...form }
    if (isEdit.value) {
      await prodPlanAPI.update(editId.value, payload)
      ElMessage.success('更新成功')
    } else {
      await prodPlanAPI.create(payload)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    fetchData()
  } catch { /* handled by interceptor */ }
  finally { submitting.value = false }
}

/** 删除计划单，仅草稿状态可删除 */
function handleDelete(row) {
  ElMessageBox.confirm(`确认删除计划单 "${row.plan_no}" 吗？`, '提示', { type: 'warning' })
    .then(async () => {
      await prodPlanAPI.delete(row.id)
      ElMessage.success('删除成功')
      fetchData()
    })
    .catch(() => {})
}

// ── 审批流程操作 ──

/** 审批计划单（草稿 -> 已审批） */
function handleApprove(row) {
  ElMessageBox.confirm(`确认审批 "${row.plan_no}" 吗？`, '审批确认', { type: 'info' })
    .then(async () => {
      await prodPlanAPI.approve(row.id)
      ElMessage.success('审批成功')
      fetchData()
    })
    .catch(() => {})
}

/** 下达计划单（已审批 -> 已下达），下达后可生成工单 */
function handleRelease(row) {
  ElMessageBox.confirm(`确认下达 "${row.plan_no}" 吗？`, '下达确认', { type: 'info' })
    .then(async () => {
      await prodPlanAPI.release(row.id)
      ElMessage.success('下达成功')
      fetchData()
    })
    .catch(() => {})
}

/** 取消计划单（已审批 -> 已取消） */
function handleCancel(row) {
  ElMessageBox.confirm(`确认取消 "${row.plan_no}" 吗？`, '取消确认', { type: 'warning' })
    .then(async () => {
      await prodPlanAPI.cancel(row.id)
      ElMessage.success('已取消')
      fetchData()
    })
    .catch(() => {})
}

// ── 生命周期 ──
onMounted(() => {
  loadMaterials()
  fetchData()
})
</script>
