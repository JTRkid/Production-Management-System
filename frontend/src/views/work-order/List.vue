<template>
  <div class="page-card">
    <!-- 搜索栏 -->
    <el-form :model="query" inline>
      <el-form-item label="工单号">
        <el-input v-model="query.wo_no" placeholder="输入工单号" clearable style="width:180px" />
      </el-form-item>
      <el-form-item label="计划单号">
        <el-input v-model="query.plan_no" placeholder="输入计划单号" clearable style="width:180px" />
      </el-form-item>
      <el-form-item label="优先级">
        <el-select v-model="query.priority" placeholder="全部" clearable style="width:120px">
          <el-option label="紧急" value="urgent" />
          <el-option label="普通" value="normal" />
          <el-option label="低" value="low" />
        </el-select>
      </el-form-item>
      <el-form-item label="状态">
        <el-select v-model="query.status" placeholder="全部" clearable style="width:140px">
          <el-option label="待派工" value="pending" />
          <el-option label="已派工" value="dispatched" />
          <el-option label="生产中" value="in_progress" />
          <el-option label="已完成" value="completed" />
          <el-option label="已关闭" value="closed" />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="fetchData">查询</el-button>
        <el-button @click="resetQuery">重置</el-button>
      </el-form-item>
    </el-form>

    <!-- 操作按钮 -->
    <div style="margin-bottom:12px">
      <el-button type="primary" @click="openDialog()">新增工单</el-button>
    </div>

    <!-- 表格 -->
    <el-table :data="list" v-loading="loading" border stripe>
      <el-table-column prop="wo_no" label="工单号" min-width="140" />
      <el-table-column prop="plan_no" label="计划单号" min-width="130" />
      <el-table-column prop="product_name" label="产品" min-width="140" />
      <el-table-column prop="order_quantity" label="订单数量" width="90" align="right" />
      <el-table-column prop="completed_quantity" label="已完成" width="80" align="right" />
      <el-table-column prop="defect_quantity" label="缺陷数" width="80" align="right" />
      <el-table-column prop="workshop_name" label="车间" width="100" />
      <el-table-column prop="priority" label="优先级" width="80">
        <template #default="{ row }">
          <el-tag :type="priorityType(row.priority)">{{ priorityLabel(row.priority) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="90">
        <template #default="{ row }">
          <el-tag :type="statusType(row.status)">{{ statusLabel(row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_by_name" label="创建人" width="100" />
      <el-table-column prop="created_at" label="创建时间" width="160" />
      <el-table-column label="操作" width="280" fixed="right">
        <template #default="{ row }">
          <el-button v-if="row.status === 'pending'" type="warning" size="small" @click="handleDispatch(row)">派工</el-button>
          <el-button v-if="row.status === 'dispatched'" type="success" size="small" @click="handleStart(row)">开工</el-button>
          <el-button v-if="row.status === 'in_progress'" type="primary" size="small" @click="handleComplete(row)">完工</el-button>
          <el-button v-if="row.status === 'in_progress'" type="warning" size="small" @click="openReport(row)">报工</el-button>
          <el-button v-if="row.status === 'completed'" type="info" size="small" @click="handleClose(row)">关闭</el-button>
          <el-button v-if="row.status === 'pending'" type="primary" size="small" @click="openDialog(row)">编辑</el-button>
          <el-button v-if="row.status === 'pending'" type="danger" size="small" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <el-pagination
      v-model:current-page="query.page"
      v-model:page-size="query.page_size"
      :total="total"
      layout="total, sizes, prev, pager, next, jumper"
      style="margin-top:16px; justify-content:flex-end"
      @current-change="fetchData"
      @size-change="fetchData"
    />

    <!-- 新增/编辑弹窗 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑工单' : '新增工单'" width="560px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="产品" prop="product">
          <el-select v-model="form.product" placeholder="请选择产品" filterable style="width:100%">
            <el-option v-for="m in materials" :key="m.id" :label="m.name" :value="m.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="订单数量" prop="order_quantity">
          <el-input-number v-model="form.order_quantity" :min="1" style="width:100%" />
        </el-form-item>
        <el-form-item label="车间" prop="workshop">
          <el-select v-model="form.workshop" placeholder="请选择车间" filterable style="width:100%">
            <el-option v-for="w in workshops" :key="w.id" :label="w.name" :value="w.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="工艺路线" prop="route">
          <el-select v-model="form.route" placeholder="请选择工艺路线" filterable style="width:100%">
            <el-option v-for="r in routes" :key="r.id" :label="r.name" :value="r.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="优先级" prop="priority">
          <el-select v-model="form.priority" placeholder="请选择" style="width:100%">
            <el-option label="紧急" value="urgent" />
            <el-option label="普通" value="normal" />
            <el-option label="低" value="low" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">确认</el-button>
      </template>
    </el-dialog>

    <!-- 报工弹窗 -->
    <el-dialog v-model="reportVisible" title="报工" width="480px">
      <el-form ref="reportFormRef" :model="reportForm" :rules="reportRules" label-width="100px">
        <el-form-item label="工序" prop="route_step">
          <el-select v-model="reportForm.route_step" placeholder="请选择工序" style="width:100%">
            <el-option v-for="s in routeSteps" :key="s.id" :label="s.name" :value="s.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="合格数量" prop="report_quantity">
          <el-input-number v-model="reportForm.report_quantity" :min="0" style="width:100%" />
        </el-form-item>
        <el-form-item label="缺陷数量" prop="defect_quantity">
          <el-input-number v-model="reportForm.defect_quantity" :min="0" style="width:100%" />
        </el-form-item>
        <el-form-item label="工时" prop="work_hours">
          <el-input-number v-model="reportForm.work_hours" :min="0" :precision="1" style="width:100%" />
        </el-form-item>
        <el-form-item label="备注" prop="remark">
          <el-input v-model="reportForm.remark" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="reportVisible = false">取消</el-button>
        <el-button type="primary" :loading="reporting" @click="submitReport">确认报工</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
/**
 * 工单管理页面
 * 提供工单的增删改查功能，支持按工单号/计划单号/优先级/状态筛选。
 * 工单包含完整生产生命周期：待派工 -> 已派工 -> 生产中 -> 已完成 -> 已关闭，
 * 支持派工、开工、完工、关闭等流程操作，以及生产过程中的报工功能。
 */

// ── 依赖导入 ──
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { workOrderAPI, materialAPI, workshopAPI, routeAPI, routeStepAPI } from '@/api'

// ── 响应式状态 ──
const loading = ref(false)              // 列表加载状态
const submitting = ref(false)           // 工单表单提交加载状态
const reporting = ref(false)            // 报工表单提交加载状态
const list = ref([])                    // 工单列表数据
const total = ref(0)                    // 总记录数
const dialogVisible = ref(false)        // 工单新增/编辑弹窗可见性
const reportVisible = ref(false)        // 报工弹窗可见性
const isEdit = ref(false)               // 工单表单是否为编辑模式
const editId = ref(null)                // 当前编辑的工单 ID
const reportWorkOrderId = ref(null)     // 当前报工的工单 ID
const formRef = ref(null)               // 工单表单引用
const reportFormRef = ref(null)         // 报工表单引用
const materials = ref([])               // 物料列表（产品下拉）
const workshops = ref([])               // 车间列表（车间下拉）
const routes = ref([])                  // 工艺路线列表（路线选择）
const routeSteps = ref([])              // 工序列表（报工时选择工序）

// ── 搜索条件 ──
const query = reactive({ page: 1, page_size: 10, wo_no: '', plan_no: '', priority: '', status: '' })

// ── 工单表单数据与校验规则 ──
const form = reactive({
  product: null,
  order_quantity: 1,
  workshop: null,
  route: null,
  priority: 'normal',
})

const rules = {
  product: [{ required: true, message: '请选择产品', trigger: 'change' }],
  order_quantity: [{ required: true, message: '请输入订单数量', trigger: 'blur' }],
  workshop: [{ required: true, message: '请选择车间', trigger: 'change' }],
  route: [{ required: true, message: '请选择工艺路线', trigger: 'change' }],
}

// ── 报工表单数据与校验规则 ──
const reportForm = reactive({
  route_step: null,
  report_quantity: 0,
  defect_quantity: 0,
  work_hours: 0,
  remark: '',
})

const reportRules = {
  route_step: [{ required: true, message: '请选择工序', trigger: 'change' }],
  report_quantity: [{ required: true, message: '请输入合格数量', trigger: 'blur' }],
}

// ── 辅助函数 ──

/** 根据优先级返回对应的 Tag 样式类型 */
function priorityType(p) {
  const map = { urgent: 'danger', normal: 'primary', low: 'info' }
  return map[p] || 'info'
}

/** 将优先级代码转换为中文标签 */
function priorityLabel(p) {
  const map = { urgent: '紧急', normal: '普通', low: '低' }
  return map[p] || p
}

/** 根据工单状态返回对应的 Tag 样式类型 */
function statusType(s) {
  const map = { pending: 'info', dispatched: 'warning', in_progress: 'primary', completed: 'success', closed: 'info' }
  return map[s] || 'info'
}

/** 将工单状态代码转换为中文标签 */
function statusLabel(s) {
  const map = { pending: '待派工', dispatched: '已派工', in_progress: '生产中', completed: '已完成', closed: '已关闭' }
  return map[s] || s
}

// ── 数据获取 ──

/** 并行加载表单所需的下拉选项数据（物料、车间、工艺路线） */
async function loadOptions() {
  try {
    const [mRes, wRes, rRes] = await Promise.all([
      materialAPI.active(),
      workshopAPI.list(),
      routeAPI.list(),
    ])
    materials.value = mRes.data || mRes || []
    workshops.value = wRes.data?.results || wRes.data || wRes.results || []
    routes.value = rRes.data?.results || rRes.data || rRes.results || []
  } catch { /* ignore */ }
}

/** 加载全部工序列表，用于报工时选择工序 */
async function loadRouteSteps() {
  try {
    const res = await routeStepAPI.list()
    routeSteps.value = res.data?.results || res.data || res.results || []
  } catch { /* ignore */ }
}

/** 获取工单分页列表，过滤空查询参数后请求 */
async function fetchData() {
  loading.value = true
  try {
    const params = { ...query }
    Object.keys(params).forEach(k => { if (params[k] === '' || params[k] === null || params[k] === undefined) delete params[k] })
    const res = await workOrderAPI.list(params)
    list.value = res.data?.results || res.data || res.results || []
    total.value = res.data?.count || res.count || 0
  } catch { /* handled by interceptor */ }
  finally { loading.value = false }
}

// ── 搜索与重置 ──

/** 清空所有搜索条件并重新查询 */
function resetQuery() {
  query.wo_no = ''
  query.plan_no = ''
  query.priority = ''
  query.status = ''
  query.page = 1
  fetchData()
}

// ── 工单增删改弹窗 ──

/**
 * 打开新增/编辑工单弹窗
 * 传入 row 参数时为编辑模式，回填数据；不传则为新增模式
 */
function openDialog(row) {
  if (row) {
    isEdit.value = true
    editId.value = row.id
    Object.assign(form, {
      product: row.product || null,
      order_quantity: row.order_quantity || 1,
      workshop: row.workshop || null,
      route: row.route || null,
      priority: row.priority || 'normal',
    })
  } else {
    isEdit.value = false
    editId.value = null
    Object.assign(form, { product: null, order_quantity: 1, workshop: null, route: null, priority: 'normal' })
  }
  dialogVisible.value = true
}

/** 提交工单表单：校验后调用新增或更新接口 */
async function handleSubmit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  submitting.value = true
  try {
    const payload = { ...form }
    if (isEdit.value) {
      await workOrderAPI.update(editId.value, payload)
      ElMessage.success('更新成功')
    } else {
      await workOrderAPI.create(payload)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    fetchData()
  } catch { /* handled by interceptor */ }
  finally { submitting.value = false }
}

/** 删除工单，仅待派工状态可删除 */
function handleDelete(row) {
  ElMessageBox.confirm(`确认删除工单 "${row.wo_no}" 吗？`, '提示', { type: 'warning' })
    .then(async () => {
      await workOrderAPI.delete(row.id)
      ElMessage.success('删除成功')
      fetchData()
    })
    .catch(() => {})
}

// ── 工单状态流转操作 ──

/**
 * 通用状态操作确认函数
 * 弹出确认对话框后调用对应的 API 方法
 * @param {Object} row - 工单行数据
 * @param {Function} action - API 方法（未使用，保留兼容）
 * @param {string} label - 操作名称（用于确认提示和成功消息）
 * @param {Function} apiMethod - 实际调用的 API 方法
 */
function actionConfirm(row, action, label, apiMethod) {
  ElMessageBox.confirm(`确认${label}工单 "${row.wo_no}" 吗？`, `${label}确认`, { type: 'info' })
    .then(async () => {
      await apiMethod(row.id)
      ElMessage.success(`${label}成功`)
      fetchData()
    })
    .catch(() => {})
}

/** 派工操作（待派工 -> 已派工） */
function handleDispatch(row) { actionConfirm(row, workOrderAPI.dispatch, '派工', workOrderAPI.dispatch) }
/** 开工操作（已派工 -> 生产中） */
function handleStart(row) { actionConfirm(row, workOrderAPI.start, '开工', workOrderAPI.start) }
/** 完工操作（生产中 -> 已完成） */
function handleComplete(row) { actionConfirm(row, workOrderAPI.complete, '完工', workOrderAPI.complete) }
/** 关闭操作（已完成 -> 已关闭） */
function handleClose(row) { actionConfirm(row, workOrderAPI.close, '关闭', workOrderAPI.close) }

// ── 报工操作 ──

/** 打开报工弹窗，重置表单并加载工序选项 */
function openReport(row) {
  reportWorkOrderId.value = row.id
  loadRouteSteps()
  Object.assign(reportForm, { route_step: null, report_quantity: 0, defect_quantity: 0, work_hours: 0, remark: '' })
  reportVisible.value = true
}

/** 提交报工：校验后调用报工接口 */
async function submitReport() {
  const valid = await reportFormRef.value.validate().catch(() => false)
  if (!valid) return
  reporting.value = true
  try {
    await workOrderAPI.report(reportWorkOrderId.value, { ...reportForm })
    ElMessage.success('报工成功')
    reportVisible.value = false
    fetchData()
  } catch { /* handled by interceptor */ }
  finally { reporting.value = false }
}

// ── 生命周期 ──
onMounted(() => {
  loadOptions()
  fetchData()
})
</script>

<style scoped>
.page-card { background: #fff; border-radius: 8px; padding: 20px; }
</style>
