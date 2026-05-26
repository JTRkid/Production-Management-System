<template>
  <div class="page-card">
    <!-- 搜索区域 -->
    <el-form :model="query" inline>
      <el-form-item label="路线名称">
        <el-input v-model="query.route_name" placeholder="路线名称" clearable />
      </el-form-item>
      <el-form-item label="产品名称">
        <el-input v-model="query.product_name" placeholder="产品名称" clearable />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="handleSearch">搜索</el-button>
        <el-button @click="handleReset">重置</el-button>
      </el-form-item>
    </el-form>

    <!-- 操作按钮 -->
    <div style="margin-bottom: 16px">
      <el-button type="primary" @click="handleAdd">新增工艺路线</el-button>
    </div>

    <!-- 数据表格 -->
    <el-table v-loading="loading" :data="list" border stripe>
      <el-table-column prop="id" label="ID" width="70" />
      <el-table-column prop="route_name" label="路线名称" min-width="140" />
      <el-table-column prop="product_name" label="产品名称" min-width="140" />
      <el-table-column label="启用状态" width="90">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
            {{ row.is_active ? '启用' : '停用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="220" fixed="right">
        <template #default="{ row }">
          <el-button link type="success" @click="handleSteps(row)">工序</el-button>
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

    <!-- 新增/编辑路线弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑工艺路线' : '新增工艺路线'"
      width="560px"
      :close-on-click-modal="false"
      @closed="handleDialogClosed"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="产品" prop="product">
          <el-select v-model="form.product" placeholder="请选择成品物料" filterable style="width: 100%">
            <el-option
              v-for="p in finishedMaterials"
              :key="p.id"
              :label="`${p.material_code} - ${p.material_name}`"
              :value="p.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="路线名称" prop="route_name">
          <el-input v-model="form.route_name" placeholder="请输入路线名称" />
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

    <!-- 工序管理子弹窗 -->
    <el-dialog
      v-model="stepsDialogVisible"
      :title="'工序管理 - ' + currentRouteName"
      width="800px"
      :close-on-click-modal="false"
      @closed="handleStepsDialogClosed"
    >
      <div style="margin-bottom: 12px">
        <el-button type="primary" size="small" @click="handleAddStep">新增工序</el-button>
      </div>
      <el-table v-loading="stepsLoading" :data="stepsList" border stripe>
        <el-table-column prop="step_no" label="工序号" width="80" />
        <el-table-column prop="step_name" label="工序名称" min-width="120" />
        <el-table-column prop="work_center_name" label="工作中心" min-width="120" />
        <el-table-column prop="standard_hours" label="标准工时(h)" width="110" align="right" />
        <el-table-column prop="description" label="描述" min-width="140" show-overflow-tooltip />
        <el-table-column label="操作" width="140">
          <template #default="{ row: stepRow }">
            <el-button link type="primary" @click="handleEditStep(stepRow)">编辑</el-button>
            <el-button link type="danger" @click="handleDeleteStep(stepRow)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <template #footer>
        <el-button @click="stepsDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 工序 新增/编辑弹窗 -->
    <el-dialog
      v-model="stepDialogVisible"
      :title="isEditStep ? '编辑工序' : '新增工序'"
      width="520px"
      :close-on-click-modal="false"
      @closed="handleStepFormClosed"
    >
      <el-form ref="stepFormRef" :model="stepForm" :rules="stepRules" label-width="100px">
        <el-form-item label="工序号" prop="step_no">
          <el-input-number v-model="stepForm.step_no" :min="1" style="width: 100%" />
        </el-form-item>
        <el-form-item label="工序名称" prop="step_name">
          <el-input v-model="stepForm.step_name" placeholder="请输入工序名称" />
        </el-form-item>
        <el-form-item label="工作中心" prop="work_center">
          <el-select v-model="stepForm.work_center" placeholder="请选择工作中心" style="width: 100%">
            <el-option
              v-for="wc in workCenters"
              :key="wc.id"
              :label="wc.name || wc.code"
              :value="wc.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="标准工时(h)" prop="standard_hours">
          <el-input-number v-model="stepForm.standard_hours" :min="0" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="stepForm.description" type="textarea" :rows="3" placeholder="请输入描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="stepDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="stepSubmitLoading" @click="handleStepSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
/**
 * 工艺路线管理页面
 * 管理产品的工艺路线（主表）及其包含的工序（子表）。
 * 工艺路线关联成品物料，每个路线可包含多道工序，
 * 每道工序关联工作中心并记录标准工时。
 */

// ── 依赖导入 ──
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { routeAPI, routeStepAPI, materialAPI, workCenterAPI } from '@/api'

// ── 响应式状态（主列表） ──
const loading = ref(false)          // 主列表加载状态
const list = ref([])                // 工艺路线列表数据
const dialogVisible = ref(false)    // 路线新增/编辑弹窗可见性
const isEdit = ref(false)           // 路线表单是否为编辑模式
const submitLoading = ref(false)    // 路线表单提交加载状态
const formRef = ref(null)           // 路线表单引用
const pagination = reactive({ page: 1, page_size: 10, total: 0 })
const finishedMaterials = ref([])   // 成品物料列表，用于产品下拉
const workCenters = ref([])         // 工作中心列表，用于工序表单

// ── 搜索条件 ──
const query = reactive({
  route_name: '',
  product_name: '',
})

// ── 路线表单数据与校验规则 ──
const form = reactive({
  id: null,
  product: null,
  route_name: '',
  is_active: true,
})

const rules = {
  product: [{ required: true, message: '请选择产品', trigger: 'change' }],
  route_name: [{ required: true, message: '请输入路线名称', trigger: 'blur' }],
}

// ── 工序子弹窗状态 ──
const stepsDialogVisible = ref(false)  // 工序列表弹窗可见性
const stepsLoading = ref(false)        // 工序列表加载状态
const stepsList = ref([])              // 当前路线的工序列表
const currentRouteId = ref(null)       // 当前操作的路线 ID
const currentRouteName = ref('')       // 当前操作的路线名称

// ── 工序表单状态 ──
const stepDialogVisible = ref(false)   // 工序新增/编辑弹窗可见性
const isEditStep = ref(false)          // 工序表单是否为编辑模式
const stepSubmitLoading = ref(false)   // 工序表单提交加载状态
const stepFormRef = ref(null)          // 工序表单引用

const stepForm = reactive({
  id: null,
  step_no: 1,
  step_name: '',
  work_center: null,
  standard_hours: 0,
  description: '',
})

const stepRules = {
  step_no: [{ required: true, message: '请输入工序号', trigger: 'blur' }],
  step_name: [{ required: true, message: '请输入工序名称', trigger: 'blur' }],
  work_center: [{ required: true, message: '请选择工作中心', trigger: 'change' }],
}

// ── 数据获取（主列表） ──

/** 获取已启用的成品物料，用于新增路线时选择产品 */
async function fetchFinishedMaterials() {
  try {
    const res = await materialAPI.active()
    const list = res.data || res.results || res || []
    finishedMaterials.value = (Array.isArray(list) ? list : []).filter(m => m.material_type === 'finished')
  } catch {
    finishedMaterials.value = []
  }
}

/** 获取全部工作中心，用于工序表单中选择工作中心 */
async function fetchWorkCenters() {
  try {
    const res = await workCenterAPI.list({ page_size: 9999 })
    workCenters.value = res.data?.results || res.data || res.results || []
  } catch {
    workCenters.value = []
  }
}

/** 获取工艺路线分页列表 */
async function fetchData() {
  loading.value = true
  try {
    const params = { page: pagination.page, page_size: pagination.page_size }
    if (query.route_name) params.route_name = query.route_name
    if (query.product_name) params.product_name = query.product_name
    const res = await routeAPI.list(params)
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
  query.route_name = ''
  query.product_name = ''
  pagination.page = 1
  fetchData()
}

// ── 路线增删改操作 ──

/** 打开新增路线弹窗，加载成品物料选项 */
function handleAdd() {
  isEdit.value = false
  resetForm()
  fetchFinishedMaterials()
  dialogVisible.value = true
}

/** 打开编辑路线弹窗，回填行数据 */
function handleEdit(row) {
  isEdit.value = true
  Object.assign(form, {
    id: row.id,
    product: row.product || row.product,
    route_name: row.route_name,
    is_active: row.is_active,
  })
  fetchFinishedMaterials()
  dialogVisible.value = true
}

/** 删除工艺路线，需二次确认 */
async function handleDelete(row) {
  try {
    await ElMessageBox.confirm(`确定要删除工艺路线「${row.route_name}」吗？`, '删除确认', {
      type: 'warning',
      confirmButtonText: '确定',
      cancelButtonText: '取消',
    })
    await routeAPI.delete(row.id)
    ElMessage.success('删除成功')
    fetchData()
  } catch { /* 取消或不操作 */ }
}

// ── 路线弹窗表单处理 ──

function resetForm() {
  form.id = null
  form.product = null
  form.route_name = ''
  form.is_active = true
  formRef.value?.resetFields()
}

function handleDialogClosed() {
  resetForm()
}

/** 提交路线表单：校验后调用新增或更新接口 */
async function handleSubmit() {
  try {
    await formRef.value.validate()
  } catch {
    return
  }
  submitLoading.value = true
  try {
    const data = {
      product: form.product,
      route_name: form.route_name,
      is_active: form.is_active,
    }
    if (isEdit.value) {
      await routeAPI.update(form.id, data)
      ElMessage.success('更新成功')
    } else {
      await routeAPI.create(data)
      ElMessage.success('新增成功')
    }
    dialogVisible.value = false
    fetchData()
  } finally {
    submitLoading.value = false
  }
}

// ── 工序管理 ──

/** 打开工序列表弹窗，加载指定路线下的所有工序 */
async function handleSteps(row) {
  currentRouteId.value = row.id
  currentRouteName.value = row.route_name
  stepsDialogVisible.value = true
  stepsLoading.value = true
  try {
    const res = await routeAPI.steps(row.id)
    stepsList.value = res.data || res.results || res || []
  } catch {
    stepsList.value = []
  } finally {
    stepsLoading.value = false
  }
}

/** 工序列表弹窗关闭后清空状态 */
function handleStepsDialogClosed() {
  stepsList.value = []
  currentRouteId.value = null
  currentRouteName.value = ''
}

// ── 工序表单操作 ──

/** 打开新增工序弹窗 */
function handleAddStep() {
  isEditStep.value = false
  resetStepForm()
  fetchWorkCenters()
  stepDialogVisible.value = true
}

/** 打开编辑工序弹窗，回填工序数据 */
function handleEditStep(stepRow) {
  isEditStep.value = true
  Object.assign(stepForm, {
    id: stepRow.id,
    step_no: stepRow.step_no,
    step_name: stepRow.step_name,
    work_center: stepRow.work_center || stepRow.work_center,
    standard_hours: stepRow.standard_hours ?? 0,
    description: stepRow.description || '',
  })
  fetchWorkCenters()
  stepDialogVisible.value = true
}

/** 删除工序，成功后刷新工序列表 */
async function handleDeleteStep(stepRow) {
  try {
    await ElMessageBox.confirm(`确定要删除工序「${stepRow.step_name}」吗？`, '删除确认', {
      type: 'warning',
      confirmButtonText: '确定',
      cancelButtonText: '取消',
    })
    await routeStepAPI.delete(stepRow.id)
    ElMessage.success('删除成功')
    await refreshSteps()
  } catch { /* 取消或不操作 */ }
}

/** 重置工序表单数据 */
function resetStepForm() {
  stepForm.id = null
  stepForm.step_no = 1
  stepForm.step_name = ''
  stepForm.work_center = null
  stepForm.standard_hours = 0
  stepForm.description = ''
  stepFormRef.value?.resetFields()
}

function handleStepFormClosed() {
  resetStepForm()
}

/** 提交工序表单：校验后调用新增或更新接口，成功后刷新工序列表 */
async function handleStepSubmit() {
  try {
    await stepFormRef.value.validate()
  } catch {
    return
  }
  stepSubmitLoading.value = true
  try {
    const data = {
      route: currentRouteId.value,
      step_no: stepForm.step_no,
      step_name: stepForm.step_name,
      work_center: stepForm.work_center,
      standard_hours: stepForm.standard_hours,
      description: stepForm.description,
    }
    if (isEditStep.value) {
      await routeStepAPI.update(stepForm.id, data)
      ElMessage.success('更新成功')
    } else {
      await routeStepAPI.create(data)
      ElMessage.success('新增成功')
    }
    stepDialogVisible.value = false
    await refreshSteps()
  } finally {
    stepSubmitLoading.value = false
  }
}

/** 重新加载当前路线的工序列表 */
async function refreshSteps() {
  stepsLoading.value = true
  try {
    const res = await routeAPI.steps(currentRouteId.value)
    stepsList.value = res.data || res.results || res || []
  } catch {
    stepsList.value = []
  } finally {
    stepsLoading.value = false
  }
}

// ── 生命周期 ──
onMounted(() => fetchData())
</script>
