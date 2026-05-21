<template>
  <div class="page-card">
    <!-- 搜索栏 -->
    <el-form :model="query" inline>
      <el-form-item label="报告号">
        <el-input v-model="query.report_no" placeholder="输入报告号" clearable style="width:180px" />
      </el-form-item>
      <el-form-item label="工单号">
        <el-input v-model="query.work_order" placeholder="输入工单号" clearable style="width:180px" />
      </el-form-item>
      <el-form-item label="检验结果">
        <el-select v-model="query.result" placeholder="全部" clearable style="width:140px">
          <el-option label="合格" value="pass" />
          <el-option label="不合格" value="fail" />
          <el-option label="让步接收" value="concession" />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="fetchData">查询</el-button>
        <el-button @click="resetQuery">重置</el-button>
      </el-form-item>
    </el-form>

    <!-- 操作按钮 -->
    <div style="margin-bottom:12px">
      <el-button type="primary" @click="openDialog()">新增记录</el-button>
    </div>

    <!-- 表格 -->
    <el-table :data="list" v-loading="loading" border stripe>
      <el-table-column prop="report_no" label="报告号" min-width="140" />
      <el-table-column prop="work_order_wo_no" label="工单号" min-width="140" />
      <el-table-column prop="inspection_type" label="检验类型" width="100">
        <template #default="{ row }">
          <el-tag :type="row.inspection_type === 'final' ? 'primary' : 'warning'">
            {{ row.inspection_type === 'in_process' ? '过程检' : row.inspection_type === 'final' ? '终检' : row.inspection_type }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="product_name" label="产品" min-width="140" />
      <el-table-column prop="inspector_name" label="检验员" width="100" />
      <el-table-column prop="sample_quantity" label="抽样数" width="80" align="right" />
      <el-table-column prop="pass_quantity" label="合格数" width="80" align="right" />
      <el-table-column prop="defect_quantity" label="缺陷数" width="80" align="right" />
      <el-table-column prop="result" label="结果" width="100">
        <template #default="{ row }">
          <el-tag :type="resultType(row.result)">{{ resultLabel(row.result) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="inspected_at" label="检验时间" width="160" />
      <el-table-column label="操作" width="160" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" size="small" @click="openDialog(row)">编辑</el-button>
          <el-button type="danger" size="small" @click="handleDelete(row)">删除</el-button>
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
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑记录' : '新增记录'" width="560px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="报告号" prop="report_no">
          <el-input v-model="form.report_no" placeholder="自动生成可留空" />
        </el-form-item>
        <el-form-item label="工单" prop="work_order">
          <el-select v-model="form.work_order" placeholder="请选择工单" filterable style="width:100%">
            <el-option v-for="w in workOrders" :key="w.id" :label="w.wo_no" :value="w.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="检验类型" prop="inspection_type">
          <el-select v-model="form.inspection_type" placeholder="请选择" style="width:100%">
            <el-option label="过程检" value="in_process" />
            <el-option label="终检" value="final" />
          </el-select>
        </el-form-item>
        <el-form-item label="产品" prop="product">
          <el-select v-model="form.product" placeholder="请选择产品" filterable style="width:100%">
            <el-option v-for="m in materials" :key="m.id" :label="m.name" :value="m.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="抽样数量" prop="sample_quantity">
          <el-input-number v-model="form.sample_quantity" :min="0" style="width:100%" />
        </el-form-item>
        <el-form-item label="合格数量" prop="pass_quantity">
          <el-input-number v-model="form.pass_quantity" :min="0" style="width:100%" />
        </el-form-item>
        <el-form-item label="缺陷数量" prop="defect_quantity">
          <el-input-number v-model="form.defect_quantity" :min="0" style="width:100%" />
        </el-form-item>
        <el-form-item label="结果" prop="result">
          <el-select v-model="form.result" placeholder="请选择" style="width:100%">
            <el-option label="合格" value="pass" />
            <el-option label="不合格" value="fail" />
            <el-option label="让步接收" value="concession" />
          </el-select>
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
 * 检验记录管理页面
 * 提供检验记录的增删改查功能，支持按报告号/工单号/检验结果筛选。
 * 每条记录包含关联工单、检验类型（过程检/终检）、产品、抽样数量、
 * 合格/缺陷数量及最终检验结果（合格/不合格/让步接收）。
 */

// ── 依赖导入 ──
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { inspectionRecordAPI, workOrderAPI, materialAPI } from '@/api'

// ── 响应式状态 ──
const loading = ref(false)          // 列表加载状态
const submitting = ref(false)       // 表单提交加载状态
const list = ref([])                // 检验记录列表数据
const total = ref(0)                // 总记录数
const dialogVisible = ref(false)    // 新增/编辑弹窗可见性
const isEdit = ref(false)           // 当前是否为编辑模式
const editId = ref(null)            // 当前编辑的记录 ID
const formRef = ref(null)           // 表单引用
const materials = ref([])           // 物料列表，用于产品下拉
const workOrders = ref([])          // 工单列表，用于工单下拉

// ── 搜索条件 ──
const query = reactive({ page: 1, page_size: 10, report_no: '', work_order: '', result: '' })

// ── 表单数据与校验规则 ──
const form = reactive({
  report_no: '',
  work_order: null,
  inspection_type: '',
  product: null,
  sample_quantity: 0,
  pass_quantity: 0,
  defect_quantity: 0,
  result: '',
})

const rules = {
  work_order: [{ required: true, message: '请选择工单', trigger: 'change' }],
  inspection_type: [{ required: true, message: '请选择检验类型', trigger: 'change' }],
  product: [{ required: true, message: '请选择产品', trigger: 'change' }],
  result: [{ required: true, message: '请选择结果', trigger: 'change' }],
}

// ── 辅助函数 ──

/** 根据检验结果返回对应的 Tag 样式类型 */
function resultType(r) {
  const map = { pass: 'success', fail: 'danger', concession: 'warning' }
  return map[r] || 'info'
}

/** 将检验结果代码转换为中文标签 */
function resultLabel(r) {
  const map = { pass: '合格', fail: '不合格', concession: '让步接收' }
  return map[r] || r
}

// ── 数据获取 ──

/** 并行加载物料和工单列表，用于表单下拉选择 */
async function loadOptions() {
  try {
    const [mRes, wRes] = await Promise.all([
      materialAPI.active(),
      workOrderAPI.list({ page_size: 999 }),
    ])
    materials.value = mRes.data || mRes || []
    workOrders.value = wRes.data?.results || wRes.data || wRes.results || []
  } catch { /* ignore */ }
}

/** 获取检验记录分页列表，过滤空查询参数后请求 */
async function fetchData() {
  loading.value = true
  try {
    const params = { ...query }
    Object.keys(params).forEach(k => { if (params[k] === '' || params[k] === null || params[k] === undefined) delete params[k] })
    const res = await inspectionRecordAPI.list(params)
    list.value = res.data?.results || res.data || res.results || []
    total.value = res.data?.count || res.count || 0
  } catch { /* handled by interceptor */ }
  finally { loading.value = false }
}

// ── 搜索与重置 ──

/** 清空搜索条件并重新查询 */
function resetQuery() {
  query.report_no = ''
  query.work_order = ''
  query.result = ''
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
      report_no: row.report_no || '',
      work_order: row.work_order || null,
      inspection_type: row.inspection_type || '',
      product: row.product || null,
      sample_quantity: row.sample_quantity || 0,
      pass_quantity: row.pass_quantity || 0,
      defect_quantity: row.defect_quantity || 0,
      result: row.result || '',
    })
  } else {
    isEdit.value = false
    editId.value = null
    Object.assign(form, {
      report_no: '', work_order: null, inspection_type: '', product: null,
      sample_quantity: 0, pass_quantity: 0, defect_quantity: 0, result: '',
    })
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
      await inspectionRecordAPI.update(editId.value, payload)
      ElMessage.success('更新成功')
    } else {
      await inspectionRecordAPI.create(payload)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    fetchData()
  } catch { /* handled by interceptor */ }
  finally { submitting.value = false }
}

/** 删除检验记录，需二次确认 */
function handleDelete(row) {
  ElMessageBox.confirm(`确认删除 "${row.report_no}" 吗？`, '提示', { type: 'warning' })
    .then(async () => {
      await inspectionRecordAPI.delete(row.id)
      ElMessage.success('删除成功')
      fetchData()
    })
    .catch(() => {})
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
