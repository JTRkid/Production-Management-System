<template>
  <div class="page-card">
    <!-- 搜索栏 -->
    <el-form :model="query" inline>
      <el-form-item label="单号">
        <el-input v-model="query.transaction_no" placeholder="输入单号" clearable style="width:180px" />
      </el-form-item>
      <el-form-item label="类型">
        <el-select v-model="query.transaction_type" placeholder="全部" clearable style="width:140px">
          <el-option label="采购入库" value="purchase_in" />
          <el-option label="生产入库" value="produce_in" />
          <el-option label="原料出库" value="material_out" />
          <el-option label="销售出库" value="sale_out" />
          <el-option label="退货入库" value="return_in" />
          <el-option label="其他" value="other" />
        </el-select>
      </el-form-item>
      <el-form-item label="物料">
        <el-input v-model="query.material_name" placeholder="输入物料名称" clearable style="width:180px" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="fetchData">查询</el-button>
        <el-button @click="resetQuery">重置</el-button>
      </el-form-item>
    </el-form>

    <!-- 操作按钮 -->
    <div style="margin-bottom:12px">
      <el-button type="primary" @click="openInbound">入库</el-button>
      <el-button type="danger" @click="openOutbound">出库</el-button>
    </div>

    <!-- 表格 -->
    <el-table :data="list" v-loading="loading" border stripe>
      <el-table-column prop="transaction_no" label="单号" min-width="140" />
      <el-table-column prop="transaction_type" label="类型" width="100">
        <template #default="{ row }">
          <el-tag :type="txTypeTag(row.transaction_type)">{{ txTypeLabel(row.transaction_type) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="material_name" label="物料" min-width="140" />
      <el-table-column prop="quantity" label="数量" width="80" align="right" />
      <el-table-column prop="warehouse_name" label="仓库" min-width="140" />
      <el-table-column prop="source_doc_type" label="来源单据" width="100">
        <template #default="{ row }">
          {{ sourceDocLabel(row.source_doc_type) }}
        </template>
      </el-table-column>
      <el-table-column prop="operator_name" label="操作人" width="100" />
      <el-table-column prop="created_at" label="操作时间" width="160" />
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

    <!-- 入库弹窗 -->
    <el-dialog v-model="inboundVisible" title="入库" width="500px">
      <el-form ref="inboundFormRef" :model="inboundForm" :rules="txRules" label-width="100px">
        <el-form-item label="入库类型" prop="transaction_type">
          <el-select v-model="inboundForm.transaction_type" placeholder="请选择" style="width:100%">
            <el-option label="采购入库" value="purchase_in" />
            <el-option label="生产入库" value="production_in" />
            <el-option label="退货入库" value="return_in" />
            <el-option label="其他入库" value="other_in" />
          </el-select>
        </el-form-item>
        <el-form-item label="物料" prop="material">
          <el-select v-model="inboundForm.material" placeholder="请选择物料" filterable style="width:100%">
            <el-option v-for="m in matOptions" :key="m.id" :label="m.name" :value="m.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="数量" prop="quantity">
          <el-input-number v-model="inboundForm.quantity" :min="1" style="width:100%" />
        </el-form-item>
        <el-form-item label="仓库" prop="warehouse">
          <el-select v-model="inboundForm.warehouse" placeholder="请选择仓库" filterable style="width:100%">
            <el-option v-for="w in whOptions" :key="w.id" :label="w.name" :value="w.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注" prop="remark">
          <el-input v-model="inboundForm.remark" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="inboundVisible = false">取消</el-button>
        <el-button type="primary" :loading="txSubmitting" @click="submitInbound">确认入库</el-button>
      </template>
    </el-dialog>

    <!-- 出库弹窗 -->
    <el-dialog v-model="outboundVisible" title="出库" width="500px">
      <el-form ref="outboundFormRef" :model="outboundForm" :rules="txRules" label-width="100px">
        <el-form-item label="出库类型" prop="transaction_type">
          <el-select v-model="outboundForm.transaction_type" placeholder="请选择" style="width:100%">
            <el-option label="生产领料" value="production_out" />
            <el-option label="销售出库" value="sales_out" />
            <el-option label="退货出库" value="return_out" />
            <el-option label="其他出库" value="other_out" />
          </el-select>
        </el-form-item>
        <el-form-item label="物料" prop="material">
          <el-select v-model="outboundForm.material" placeholder="请选择物料" filterable style="width:100%">
            <el-option v-for="m in matOptions" :key="m.id" :label="m.name" :value="m.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="数量" prop="quantity">
          <el-input-number v-model="outboundForm.quantity" :min="1" style="width:100%" />
        </el-form-item>
        <el-form-item label="仓库" prop="warehouse">
          <el-select v-model="outboundForm.warehouse" placeholder="请选择仓库" filterable style="width:100%">
            <el-option v-for="w in whOptions" :key="w.id" :label="w.name" :value="w.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注" prop="remark">
          <el-input v-model="outboundForm.remark" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="outboundVisible = false">取消</el-button>
        <el-button type="primary" :loading="txSubmitting" @click="submitOutbound">确认出库</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
/**
 * 出入库记录管理页面
 * 展示所有出入库流水记录，支持按单号/类型/物料筛选。
 * 提供入库和出库两个独立操作弹窗，入库支持采购入库/生产入库/退货入库，
 * 出库支持生产领料/销售出库等类型。每条记录自动关联来源单据。
 */

// ── 依赖导入 ──
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { transactionAPI, materialAPI, warehouseAPI } from '@/api'

// ── 响应式状态 ──
const loading = ref(false)              // 列表加载状态
const txSubmitting = ref(false)         // 入库/出库表单提交加载状态
const list = ref([])                    // 出入库记录列表
const total = ref(0)                    // 总记录数
const inboundVisible = ref(false)       // 入库弹窗可见性
const outboundVisible = ref(false)      // 出库弹窗可见性
const inboundFormRef = ref(null)        // 入库表单引用
const outboundFormRef = ref(null)       // 出库表单引用
const matOptions = ref([])              // 物料列表，用于表单下拉
const whOptions = ref([])               // 仓库列表，用于表单下拉

// ── 搜索条件 ──
const query = reactive({ page: 1, page_size: 10, transaction_no: '', transaction_type: '', material_name: '' })

// ── 入库表单数据 ──
const inboundForm = reactive({
  transaction_type: '',
  material: null,
  quantity: 1,
  warehouse: null,
  remark: '',
})

// ── 出库表单数据 ──
const outboundForm = reactive({
  transaction_type: '',
  material: null,
  quantity: 1,
  warehouse: null,
  remark: '',
})

// ── 入库/出库共用校验规则 ──
const txRules = {
  transaction_type: [{ required: true, message: '请选择类型', trigger: 'change' }],
  material: [{ required: true, message: '请选择物料', trigger: 'change' }],
  quantity: [{ required: true, message: '请输入数量', trigger: 'blur' }],
  warehouse: [{ required: true, message: '请选择仓库', trigger: 'change' }],
}

// ── 辅助函数 ──

/** 根据出入库类型返回对应的 Tag 样式类型（入库绿色、出库红色） */
function txTypeTag(t) {
  const map = { purchase_in: 'success', produce_in: 'success', material_out: 'danger', sale_out: 'danger', return_in: 'warning', other: 'info' }
  return map[t] || 'info'
}

/** 将出入库类型代码转换为中文标签 */
function txTypeLabel(t) {
  const map = { purchase_in: '采购入库', produce_in: '生产入库', material_out: '原料出库', sale_out: '销售出库', return_in: '退货入库', other: '其他' }
  return map[t] || t
}

/** 将来源单据类型代码转换为中文标签 */
function sourceDocLabel(t) {
  const map = { purchase_order: '采购订单', sales_order: '销售订单', production_plan: '生产计划', work_order: '生产工单', manual: '手动录入' }
  return map[t] || t || '-'
}

// ── 数据获取 ──

/** 并行加载物料和仓库列表，用于入库/出库表单下拉选择 */
async function loadOptions() {
  try {
    const [mRes, wRes] = await Promise.all([
      materialAPI.active(),
      warehouseAPI.list({ page_size: 999 }),
    ])
    matOptions.value = mRes.data || mRes || []
    whOptions.value = wRes.data?.results || wRes.data || wRes.results || []
  } catch { /* ignore */ }
}

/** 获取出入库记录分页列表，过滤空查询参数后请求 */
async function fetchData() {
  loading.value = true
  try {
    const params = { ...query }
    Object.keys(params).forEach(k => { if (params[k] === '' || params[k] === null || params[k] === undefined) delete params[k] })
    const res = await transactionAPI.list(params)
    list.value = res.data?.results || res.data || res.results || []
    total.value = res.data?.count || res.count || 0
  } catch { /* handled by interceptor */ }
  finally { loading.value = false }
}

// ── 搜索与重置 ──

/** 清空搜索条件并重新查询 */
function resetQuery() {
  query.transaction_no = ''
  query.transaction_type = ''
  query.material_name = ''
  query.page = 1
  fetchData()
}

// ── 入库操作 ──

/** 打开入库弹窗，重置表单并加载下拉选项 */
function openInbound() {
  loadOptions()
  Object.assign(inboundForm, { transaction_type: '', material: null, quantity: 1, warehouse: null, remark: '' })
  inboundVisible.value = true
}

/** 提交入库表单：校验后调用入库接口 */
async function submitInbound() {
  const valid = await inboundFormRef.value.validate().catch(() => false)
  if (!valid) return
  txSubmitting.value = true
  try {
    await transactionAPI.inbound({ ...inboundForm })
    ElMessage.success('入库成功')
    inboundVisible.value = false
    fetchData()
  } catch { /* handled by interceptor */ }
  finally { txSubmitting.value = false }
}

// ── 出库操作 ──

/** 打开出库弹窗，重置表单并加载下拉选项 */
function openOutbound() {
  loadOptions()
  Object.assign(outboundForm, { transaction_type: '', material: null, quantity: 1, warehouse: null, remark: '' })
  outboundVisible.value = true
}

/** 提交出库表单：校验后调用出库接口 */
async function submitOutbound() {
  const valid = await outboundFormRef.value.validate().catch(() => false)
  if (!valid) return
  txSubmitting.value = true
  try {
    await transactionAPI.outbound({ ...outboundForm })
    ElMessage.success('出库成功')
    outboundVisible.value = false
    fetchData()
  } catch { /* handled by interceptor */ }
  finally { txSubmitting.value = false }
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
