<template>
  <div class="page-card">
    <!-- 顶部操作栏 -->
    <div class="page-toolbar">
      <div class="toolbar-left">
        <el-input
          v-model="query.keyword"
          placeholder="请输入销售单号或客户名称搜索"
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
          <el-option label="生产中" value="in_production" />
          <el-option label="已发货" value="shipped" />
          <el-option label="已完成" value="completed" />
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
          新增销售单
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
      <el-table-column prop="so_no" label="销售单号" min-width="140" />
      <el-table-column prop="customer_name" label="客户名称" min-width="150" />
      <el-table-column prop="product_name" label="产品名称" min-width="140" />
      <el-table-column prop="order_quantity" label="订单数量" width="100" align="right" />
      <el-table-column prop="delivered_quantity" label="已发货数量" width="110" align="right" />
      <el-table-column prop="unit_price" label="单价" width="100" align="right" />
      <el-table-column prop="total_amount" label="总金额" width="120" align="right" />
      <el-table-column prop="scheduled_date" label="计划交付日期" width="130" />
      <el-table-column prop="status" label="状态" width="110" align="center">
        <template #default="{ row }">
          <el-tag :type="statusTagType(row.status)" size="small">
            {{ statusLabel(row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="sales_person_name" label="销售员" width="100" />
      <el-table-column prop="created_at" label="创建时间" width="170" />
      <el-table-column label="操作" min-width="220" align="center" fixed="right">
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
            v-if="['draft', 'approved'].includes(row.status)"
            link
            type="danger"
            @click="handleCancel(row.id)"
          >
            取消
          </el-button>
          <el-button link type="primary" @click="openDialog(row)">编辑</el-button>
          <el-popconfirm
            title="确定要删除该销售单吗？"
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
      :title="isEdit ? '编辑销售单' : '新增销售单'"
      width="680px"
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
            <el-form-item label="客户" prop="customer">
              <el-select
                v-model="form.customer"
                placeholder="请选择客户"
                filterable
                style="width: 100%"
              >
                <el-option
                  v-for="c in customerOptions"
                  :key="c.id"
                  :label="c.customer_name"
                  :value="c.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="产品" prop="product">
              <el-select
                v-model="form.product"
                placeholder="请选择产品"
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
            <el-form-item label="计划交付日期" prop="scheduled_date">
              <el-date-picker
                v-model="form.scheduled_date"
                type="date"
                placeholder="请选择日期"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="销售员" prop="sales_person">
              <el-select
                v-model="form.sales_person"
                placeholder="请选择销售员"
                filterable
                style="width: 100%"
              >
                <el-option
                  v-for="u in salesPersonOptions"
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
  </div>
</template>

<script setup>
/**
 * 销售订单管理页面组件
 * 提供销售订单的增删改查功能，支持审批和取消操作
 * 订单状态流转：草稿 -> 已审批 -> 生产中 -> 已发货 -> 已完成
 * 表单中客户、产品、销售员通过下拉选择
 */
import { ref, reactive, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Plus } from '@element-plus/icons-vue'
import { salesOrderAPI, customerAPI, materialAPI, userAPI } from '@/api'

// ── 列表数据与分页 ──
const loading = ref(false)
const list = ref([])
const total = ref(0)
const query = reactive({ keyword: '', status: '', page: 1, page_size: 10 })

// 从后端获取销售订单列表（支持分页、关键词和状态筛选）
async function fetchData() {
  loading.value = true
  try {
    const params = { page: query.page, page_size: query.page_size }
    if (query.keyword) params.keyword = query.keyword
    if (query.status) params.status = query.status
    const res = await salesOrderAPI.list(params)
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
    in_production: '',
    shipped: 'success',
    completed: 'success',
    cancelled: 'danger',
  }
  return map[status] || 'info'
}

// 根据订单状态返回中文标签
function statusLabel(status) {
  const map = {
    draft: '草稿',
    approved: '已审批',
    in_production: '生产中',
    shipped: '已发货',
    completed: '已完成',
    cancelled: '已取消',
  }
  return map[status] || status
}

// ── 审批 / 取消 ──
// 审批销售单（仅草稿状态可审批）
async function handleApprove(id) {
  await ElMessageBox.confirm('确定要审批该销售单吗？', '审批确认', {
    confirmButtonText: '审批',
    cancelButtonText: '取消',
    type: 'info',
  })
  await salesOrderAPI.approve(id)
  ElMessage.success('审批成功')
  fetchData()
}

// 取消销售单（草稿和已审批状态可取消）
async function handleCancel(id) {
  await ElMessageBox.confirm('确定要取消该销售单吗？', '取消确认', {
    confirmButtonText: '取消订单',
    cancelButtonText: '返回',
    type: 'warning',
  })
  await salesOrderAPI.cancel(id)
  ElMessage.success('已取消')
  fetchData()
}

// ── 新增/编辑弹窗与表单 ──
const dialogVisible = ref(false)
const isEdit = ref(false)
const submitLoading = ref(false)
const formRef = ref(null)
const editingId = ref(null)

// ── 下拉选项数据 ──
const customerOptions = ref([])     // 客户下拉列表
const materialOptions = ref([])     // 产品/物料下拉列表
const salesPersonOptions = ref([])  // 销售员下拉列表

const initialForm = {
  customer: null,
  product: null,
  order_quantity: 1,
  unit_price: 0,
  scheduled_date: '',
  sales_person: null,
  remark: '',
}
const form = reactive({ ...initialForm })

const rules = {
  customer: [{ required: true, message: '请选择客户', trigger: 'change' }],
  product: [{ required: true, message: '请选择产品', trigger: 'change' }],
  order_quantity: [{ required: true, message: '请输入订单数量', trigger: 'blur' }],
  unit_price: [{ required: true, message: '请输入单价', trigger: 'blur' }],
  scheduled_date: [{ required: true, message: '请选择计划交付日期', trigger: 'change' }],
  sales_person: [{ required: true, message: '请选择销售员', trigger: 'change' }],
}

// 并行加载客户、产品、销售员三个下拉选项
async function loadDropdownOptions() {
  try {
    const [custRes, matRes, userRes] = await Promise.all([
      customerAPI.list({ is_active: true, page_size: 9999 }),
      materialAPI.active(),
      userAPI.list({ role: 'salesman', page_size: 9999 }),
    ])
    customerOptions.value = custRes.data?.results || custRes.data || custRes.results || []
    materialOptions.value = matRes.data?.results || matRes.data || matRes.results || []
    salesPersonOptions.value = userRes.data?.results || userRes.data || userRes.results || []
  } catch {
    // 静默处理，下拉为空由用户感知
  }
}

// 打开弹窗：传入 row 时为编辑模式，否则为新增模式
function openDialog(row) {
  if (row) {
    isEdit.value = true
    editingId.value = row.id
    Object.assign(form, {
      customer: row.customer || row.customer || null,
      product: row.product || null,
      order_quantity: row.order_quantity || 1,
      unit_price: row.unit_price || 0,
      scheduled_date: row.scheduled_date || '',
      sales_person: row.sales_person || row.sales_person || null,
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
      await salesOrderAPI.update(editingId.value, data)
      ElMessage.success('更新成功')
    } else {
      await salesOrderAPI.create(data)
      ElMessage.success('新增成功')
    }
    dialogVisible.value = false
    fetchData()
  } finally {
    submitLoading.value = false
  }
}

// 删除销售单，若当前页只剩一条且非第一页则回退一页
async function handleDelete(id) {
  await salesOrderAPI.delete(id)
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
