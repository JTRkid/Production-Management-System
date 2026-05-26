<template>
  <div class="page-card">
    <!-- 搜索区域 -->
    <el-form :model="query" inline>
      <el-form-item label="物料编码">
        <el-input v-model="query.material_code" placeholder="物料编码" clearable />
      </el-form-item>
      <el-form-item label="物料名称">
        <el-input v-model="query.material_name" placeholder="物料名称" clearable />
      </el-form-item>
      <el-form-item label="物料类型">
        <el-select v-model="query.material_type" placeholder="全部" clearable style="width: 140px">
          <el-option label="原材料" value="raw" />
          <el-option label="半成品" value="semi" />
          <el-option label="成品" value="finished" />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="handleSearch">搜索</el-button>
        <el-button @click="handleReset">重置</el-button>
      </el-form-item>
    </el-form>

    <!-- 操作按钮 -->
    <div style="margin-bottom: 16px">
      <el-button type="primary" @click="handleAdd">新增物料</el-button>
    </div>

    <!-- 数据表格 -->
    <el-table v-loading="loading" :data="list" border stripe>
      <el-table-column prop="material_code" label="物料编码" min-width="120" />
      <el-table-column prop="material_name" label="物料名称" min-width="140" />
      <el-table-column prop="specification" label="规格型号" min-width="140" />
      <el-table-column prop="unit" label="单位" width="80" />
      <el-table-column label="物料类型" width="100">
        <template #default="{ row }">
          <el-tag :type="materialTypeTag(row.material_type)" size="small">
            {{ materialTypeLabel(row.material_type) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="unit_cost" label="单位成本" width="110" align="right" />
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
      :title="isEdit ? '编辑物料' : '新增物料'"
      width="560px"
      :close-on-click-modal="false"
      @closed="handleDialogClosed"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="物料编码" prop="material_code">
          <el-input v-model="form.material_code" placeholder="请输入物料编码" />
        </el-form-item>
        <el-form-item label="物料名称" prop="material_name">
          <el-input v-model="form.material_name" placeholder="请输入物料名称" />
        </el-form-item>
        <el-form-item label="规格型号" prop="specification">
          <el-input v-model="form.specification" placeholder="请输入规格型号" />
        </el-form-item>
        <el-form-item label="单位" prop="unit">
          <el-input v-model="form.unit" placeholder="如：个、件、kg" />
        </el-form-item>
        <el-form-item label="物料类型" prop="material_type">
          <el-select v-model="form.material_type" placeholder="请选择物料类型" style="width: 100%">
            <el-option label="原材料" value="raw" />
            <el-option label="半成品" value="semi" />
            <el-option label="成品" value="finished" />
          </el-select>
        </el-form-item>
        <el-form-item label="单位成本" prop="unit_cost">
          <el-input-number v-model="form.unit_cost" :min="0" :precision="2" style="width: 100%" />
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
 * 物料主数据管理页面
 * 提供物料信息的增删改查功能，支持按编码/名称/类型筛选，
 * 可管理物料的启用/停用状态，包含单位成本等财务信息。
 */

// ── 依赖导入 ──
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { materialAPI } from '@/api'

// ── 响应式状态 ──
const loading = ref(false)          // 列表加载状态
const list = ref([])                // 物料列表数据
const dialogVisible = ref(false)    // 新增/编辑弹窗可见性
const isEdit = ref(false)           // 当前是否为编辑模式
const submitLoading = ref(false)    // 提交按钮加载状态
const formRef = ref(null)           // 表单引用，用于校验
const pagination = reactive({ page: 1, page_size: 10, total: 0 })

// ── 搜索条件 ──
const query = reactive({
  material_code: '',
  material_name: '',
  material_type: '',
})

// ── 表单数据与校验规则 ──
const form = reactive({
  id: null,
  material_code: '',
  material_name: '',
  specification: '',
  unit: '',
  material_type: 'raw',
  unit_cost: 0,
  is_active: true,
})

const rules = {
  material_code: [{ required: true, message: '请输入物料编码', trigger: 'blur' }],
  material_name: [{ required: true, message: '请输入物料名称', trigger: 'blur' }],
  unit: [{ required: true, message: '请输入单位', trigger: 'blur' }],
  material_type: [{ required: true, message: '请选择物料类型', trigger: 'change' }],
}

// ── 辅助函数 ──

/** 根据物料类型返回对应的 Tag 样式类型 */
function materialTypeTag(type) {
  const map = { raw: 'info', semi: 'warning', finished: 'success' }
  return map[type] || 'info'
}

/** 将物料类型代码转换为中文标签 */
function materialTypeLabel(type) {
  const map = { raw: '原材料', semi: '半成品', finished: '成品' }
  return map[type] || type
}

// ── 数据获取 ──

/** 获取物料分页列表，支持按编码/名称/类型条件筛选 */
async function fetchData() {
  loading.value = true
  try {
    const params = { page: pagination.page, page_size: pagination.page_size }
    if (query.material_code) params.material_code = query.material_code
    if (query.material_name) params.material_name = query.material_name
    if (query.material_type) params.material_type = query.material_type
    const res = await materialAPI.list(params)
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

/** 点击搜索按钮，重置页码后重新查询 */
function handleSearch() {
  pagination.page = 1
  fetchData()
}

/** 清空所有搜索条件并重新查询 */
function handleReset() {
  query.material_code = ''
  query.material_name = ''
  query.material_type = ''
  pagination.page = 1
  fetchData()
}

// ── 增删改操作 ──

/** 打开新增物料弹窗 */
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
    material_code: row.material_code,
    material_name: row.material_name,
    specification: row.specification || '',
    unit: row.unit || '',
    material_type: row.material_type,
    unit_cost: row.unit_cost ?? 0,
    is_active: row.is_active,
  })
  dialogVisible.value = true
}

/** 删除物料，需二次确认 */
async function handleDelete(row) {
  try {
    await ElMessageBox.confirm(`确定要删除物料「${row.material_name}」吗？`, '删除确认', {
      type: 'warning',
      confirmButtonText: '确定',
      cancelButtonText: '取消',
    })
    await materialAPI.delete(row.id)
    ElMessage.success('删除成功')
    fetchData()
  } catch { /* 取消或不操作 */ }
}

// ── 弹窗表单处理 ──

/** 重置表单数据并清除校验状态 */
function resetForm() {
  form.id = null
  form.material_code = ''
  form.material_name = ''
  form.specification = ''
  form.unit = ''
  form.material_type = 'raw'
  form.unit_cost = 0
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
      material_code: form.material_code,
      material_name: form.material_name,
      specification: form.specification,
      unit: form.unit,
      material_type: form.material_type,
      unit_cost: form.unit_cost,
      is_active: form.is_active,
    }
    if (isEdit.value) {
      await materialAPI.update(form.id, data)
      ElMessage.success('更新成功')
    } else {
      await materialAPI.create(data)
      ElMessage.success('新增成功')
    }
    dialogVisible.value = false
    fetchData()
  } finally {
    submitLoading.value = false
  }
}

// ── 生命周期 ──
onMounted(() => fetchData())
</script>
