<template>
  <div class="page-card">
    <!-- 顶部操作栏 -->
    <div class="page-toolbar">
      <div class="toolbar-left">
        <el-input
          v-model="query.keyword"
          placeholder="请输入采购单号或供应商名称搜索"
          clearable
          style="width: 260px"
          @clear="handleSearch"
          @keyup.enter="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-select
          v-model="query.status"
          placeholder="请选择状态"
          clearable
          style="width: 160px; margin-left: 12px"
          @change="handleSearch"
          @clear="handleSearch"
        >
          <el-option label="草稿" value="draft" />
          <el-option label="已审批" value="approved" />
          <el-option label="已下单" value="ordered" />
          <el-option label="部分到货" value="partial_received" />
          <el-option label="已到货" value="received" />
          <el-option label="已取消" value="cancelled" />
        </el-select>
      </div>
      <div class="toolbar-actions">
        <el-button type="primary" @click="handleSearch">
          <el-icon><Search /></el-icon>
          搜索
        </el-button>
        <el-button type="success" @click="openDialog()">
          <el-icon><Plus /></el-icon>
          新增采购单
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
      <el-table-column prop="po_no" label="采购单号" min-width="140" />
      <el-table-column prop="supplier_name" label="供应商名称" min-width="150" />
      <el-table-column prop="material_name" label="物料名称" min-width="140" />
      <el-table-column prop="order_quantity" label="订单数量" width="100" align="right" />
      <el-table-column prop="received_quantity" label="已收货数量" width="110" align="right" />
      <el-table-column prop="unit_price" label="单价" width="100" align="right" />
      <el-table-column prop="total_amount" label="总金额" width="120" align="right" />
      <el-table-column prop="ordered_date" label="下单日期" width="120" />
      <el-table-column prop="expected_date" label="预计到货日期" width="130" />
      <el-table-column prop="status" label="状态" width="110" align="center">
        <template #default="{ row }">
          <el-tag :type="statusTagType(row.status)" size="small">
            {{ statusLabel(row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="buyer_name" label="采购员" width="100" />
      <el-table-column prop="created_at" label="创建时间" width="170" />
      <el-table-column label="操作" min-width="260" align="center" fixed="right">
        <template #default="{ row }">
          <el-button
            v-if="row.status === 'draft'"
            link
            type="warning"
            @click="handleApprove(row.id)"
          >
            审批
          </el-button>
          <el-button
            v-if="['approved', 'ordered', 'partial_received'].includes(row.status)"
            link
            type="success"
            @click="openReceiveDialog(row)"
          >
            收货
          </el-button>
          <el-button link type="primary" @click="openDialog(row)">编辑</el-button>
          <el-popconfirm
            title="确定要删除该采购单吗？"
            confirm-button-text="删除"
            cancel-button-text="取消"
            @confirm="handleDelete(row.id)"
          >
            <template #reference>
              <el-button link type="danger">删除</el-button>
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
      :title="isEdit ? '编辑采购单' : '新增采购单'"
      width="680px"
      :close-on-click-modal="false"
      @closed="resetForm"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="110px"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="供应商" prop="supplier">
              <el-select
                v-model="form.supplier"
                placeholder="请选择供应商"
                filterable
                style="width: 100%"
              >
                <el-option
                  v-for="s in supplierOptions"
                  :key="s.id"
                  :label="s.supplier_name"
                  :value="s.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="物料" prop="material">
              <el-select
                v-model="form.material"
                placeholder="请选择物料"
                filterable
                style="width: 100%"
              >
                <el-option
                  v-for="m in materialOptions"
                  :key="m.id"
                  :label="m.material_name"
                  :value="m.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="订单数量" prop="order_quantity">
              <el-input-number
                v-model="form.order_quantity"
                :min="1"
                :precision="0"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="单价" prop="unit_price">
              <el-input-number
                v-model="form.unit_price"
                :min="0"
                :precision="2"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="预计到货日期" prop="expected_date">
              <el-date-picker
                v-model="form.expected_date"
                type="date"
                placeholder="请选择日期"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="采购员" prop="buyer">
              <el-select
                v-model="form.buyer"
                placeholder="请选择采购员"
                filterable
                style="width: 100%"
              >
                <el-option
                  v-for="u in buyerOptions"
                  :key="u.id"
                  :label="u.name || u.username"
                  :value="u.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="备注" prop="remark">
          <el-input
            v-model="form.remark"
            type="textarea"
            :rows="3"
            placeholder="请输入备注信息"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">
          确定
        </el-button>
      </template>
    </el-dialog>

    <!-- 收货弹窗 -->
    <el-dialog
      v-model="receiveDialogVisible"
      title="收货"
      width="450px"
      :close-on-click-modal="false"
      @closed="resetReceiveForm"
    >
      <el-form ref="receiveFormRef" :model="receiveForm" :rules="receiveRules" label-width="100px">
        <el-form-item label="采购单号">
          <el-input :model-value="currentOrder?.po_no" disabled />
        </el-form-item>
        <el-form-item label="已收货数量">
          <el-input :model-value="currentOrder?.received_quantity ?? 0" disabled />
        </el-form-item>
        <el-form-item label="本次收货数量" prop="quantity">
          <el-input-number
            v-model="receiveForm.quantity"
            :min="1"
            :max="maxReceive"
            :precision="0"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="receiveDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="receiveLoading" @click="handleReceive">
          确认收货
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
/**
 * 采购订单管理页面组件
 * 提供采购订单的增删改查功能，支持审批和收货操作
 * 订单状态流转：草稿 -> 已审批 -> 已下单 -> 部分收货/已到货
 * 收货时校验数量不超过剩余未收货量
 */
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Plus } from '@element-plus/icons-vue'
import { purchaseOrderAPI, supplierAPI, materialAPI, userAPI } from '@/api'

// ── 列表数据与分页 ──
const loading = ref(false)
const list = ref([])
const total = ref(0)
const query = reactive({ keyword: '', status: '', page: 1, page_size: 10 })

// 从后端获取采购订单列表（支持分页、关键词和状态筛选）
async function fetchData() {
  loading.value = true
  try {
    const params = { page: query.page, page_size: query.page_size }
    if (query.keyword) params.keyword = query.keyword
    if (query.status) params.status = query.status
    const res = await purchaseOrderAPI.list(params)
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

// ── 状态辅助函数 ──
// 根据订单状态返回 Tag 颜色类型
function statusTagType(status) {
  const map = {
    draft: 'info',
    approved: 'warning',
    ordered: '',
    partial_received: 'warning',
    received: 'success',
    cancelled: 'danger',
  }
  return map[status] || 'info'
}

// 根据订单状态返回中文标签
function statusLabel(status) {
  const map = {
    draft: '草稿',
    approved: '已审批',
    ordered: '已下单',
    partial_received: '部分收货',
    received: '已到货',
    cancelled: '已取消',
  }
  return map[status] || status
}

// ── 审批操作 ──
// 审批采购单（仅草稿状态可审批）
async function handleApprove(id) {
  await ElMessageBox.confirm('确定要审批该采购单吗？', '审批确认', {
    confirmButtonText: '审批',
    cancelButtonText: '取消',
    type: 'info',
  })
  await purchaseOrderAPI.approve(id)
  ElMessage.success('审批成功')
  fetchData()
}

// ── 收货弹窗 ──
const receiveDialogVisible = ref(false)  // 收货弹窗可见性
const receiveLoading = ref(false)        // 收货提交加载状态
const receiveFormRef = ref(null)         // 收货表单引用
const currentOrder = ref(null)           // 当前收货的采购单

const receiveForm = reactive({ quantity: 1 })

// 计算最大可收货数量 = 订单数量 - 已收货数量
const maxReceive = computed(() => {
  if (!currentOrder.value) return 0
  return (currentOrder.value.order_quantity || 0) - (currentOrder.value.received_quantity || 0)
})

// 收货数量校验规则：必填 + 不超过剩余可收货量
const receiveRules = {
  quantity: [
    { required: true, message: '请输入收货数量', trigger: 'blur' },
    {
      validator: (_rule, value, callback) => {
        if (value < 1) {
          callback(new Error('收货数量必须大于0'))
        } else if (value > maxReceive.value) {
          callback(new Error(`收货数量不能超过 ${maxReceive.value}`))
        } else {
          callback()
        }
      },
      trigger: 'blur',
    },
  ],
}

// 打开收货弹窗，记录当前操作的采购单
function openReceiveDialog(row) {
  currentOrder.value = row
  receiveForm.quantity = 1
  receiveDialogVisible.value = true
  nextTick(() => receiveFormRef.value?.clearValidate())
}

// 收货弹窗关闭时重置表单
function resetReceiveForm() {
  currentOrder.value = null
  receiveForm.quantity = 1
  receiveFormRef.value?.clearValidate()
}

// 提交收货：调用收货接口并刷新列表
async function handleReceive() {
  if (!currentOrder.value) return
  const valid = await receiveFormRef.value.validate().catch(() => false)
  if (!valid) return
  receiveLoading.value = true
  try {
    await purchaseOrderAPI.receive(currentOrder.value.id, { quantity: receiveForm.quantity })
    ElMessage.success('收货成功')
    receiveDialogVisible.value = false
    fetchData()
  } finally {
    receiveLoading.value = false
  }
}

// ── 新增/编辑弹窗与表单 ──
const dialogVisible = ref(false)
const isEdit = ref(false)
const submitLoading = ref(false)
const formRef = ref(null)
const editingId = ref(null)

// ── 下拉选项数据 ──
const supplierOptions = ref([])  // 供应商下拉列表
const materialOptions = ref([])  // 物料下拉列表
const buyerOptions = ref([])     // 采购员下拉列表

const initialForm = {
  supplier: null,
  material: null,
  order_quantity: 1,
  unit_price: 0,
  expected_date: '',
  buyer: null,
  remark: '',
}
const form = reactive({ ...initialForm })

const rules = {
  supplier: [{ required: true, message: '请选择供应商', trigger: 'change' }],
  material: [{ required: true, message: '请选择物料', trigger: 'change' }],
  order_quantity: [{ required: true, message: '请输入订单数量', trigger: 'blur' }],
  unit_price: [{ required: true, message: '请输入单价', trigger: 'blur' }],
  expected_date: [{ required: true, message: '请选择预计到货日期', trigger: 'change' }],
  buyer: [{ required: true, message: '请选择采购员', trigger: 'change' }],
}

// 并行加载供应商、物料、采购员三个下拉选项
async function loadDropdownOptions() {
  try {
    const [supplierRes, matRes, userRes] = await Promise.all([
      supplierAPI.list({ is_active: true, page_size: 9999 }),
      materialAPI.active(),
      userAPI.list({ role: 'purchaser', page_size: 9999 }),
    ])
    supplierOptions.value = supplierRes.data?.results || supplierRes.data || supplierRes.results || []
    materialOptions.value = matRes.data?.results || matRes.data || matRes.results || []
    buyerOptions.value = userRes.data?.results || userRes.data || userRes.results || []
  } catch {
    // 静默处理
  }
}

// 打开弹窗：传入 row 时为编辑模式，否则为新增模式
function openDialog(row) {
  if (row) {
    isEdit.value = true
    editingId.value = row.id
    Object.assign(form, {
      supplier: row.supplier || row.supplier || null,
      material: row.material || row.material || null,
      order_quantity: row.order_quantity || 1,
      unit_price: row.unit_price || 0,
      expected_date: row.expected_date || '',
      buyer: row.buyer || row.buyer || null,
      remark: row.remark || '',
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
      await purchaseOrderAPI.update(editingId.value, data)
      ElMessage.success('更新成功')
    } else {
      await purchaseOrderAPI.create(data)
      ElMessage.success('新增成功')
    }
    dialogVisible.value = false
    fetchData()
  } finally {
    submitLoading.value = false
  }
}

// 删除采购单，若当前页只剩一条且非第一页则回退一页
async function handleDelete(id) {
  await purchaseOrderAPI.delete(id)
  ElMessage.success('删除成功')
  if (list.value.length === 1 && query.page > 1) {
    query.page--
  }
  fetchData()
}

onMounted(() => {
  loadDropdownOptions()
  fetchData()
})
</script>
