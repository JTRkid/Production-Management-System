<template>
  <div class="page-card">
    <!-- 搜索栏 -->
    <el-form :model="query" inline>
      <el-form-item label="产品">
        <el-input v-model="query.product_name" placeholder="输入产品名称" clearable style="width:200px" />
      </el-form-item>
      <el-form-item label="检验项目">
        <el-input v-model="query.item_name" placeholder="输入项目名称" clearable style="width:200px" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="fetchData">查询</el-button>
        <el-button @click="resetQuery">重置</el-button>
      </el-form-item>
    </el-form>

    <!-- 操作按钮 -->
    <div style="margin-bottom:12px">
      <el-button type="primary" @click="openDialog()">新增标准</el-button>
    </div>

    <!-- 表格 -->
    <el-table :data="list" v-loading="loading" border stripe>
      <el-table-column prop="product_name" label="产品" min-width="140" />
      <el-table-column prop="item_name" label="检验项目" min-width="140" />
      <el-table-column prop="standard_desc" label="标准描述" min-width="200" show-overflow-tooltip />
      <el-table-column prop="tolerance" label="公差" width="120" />
      <el-table-column prop="is_active" label="启用" width="80">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'info'">{{ row.is_active ? '是' : '否' }}</el-tag>
        </template>
      </el-table-column>
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
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑标准' : '新增标准'" width="560px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="产品" prop="product">
          <el-select v-model="form.product" placeholder="请选择产品" filterable style="width:100%">
            <el-option v-for="m in materials" :key="m.id" :label="m.name" :value="m.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="检验项目" prop="item_name">
          <el-input v-model="form.item_name" placeholder="如：尺寸、外观、硬度" />
        </el-form-item>
        <el-form-item label="标准描述" prop="standard_desc">
          <el-input v-model="form.standard_desc" type="textarea" :rows="3" placeholder="检验标准详细描述" />
        </el-form-item>
        <el-form-item label="公差" prop="tolerance">
          <el-input v-model="form.tolerance" placeholder="如：±0.05mm" />
        </el-form-item>
        <el-form-item label="是否启用" prop="is_active">
          <el-switch v-model="form.is_active" />
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
 * 检验标准管理页面
 * 提供检验标准的增删改查功能，支持按产品名称/检验项目筛选。
 * 每条标准记录包含产品、检验项目名称、标准描述、公差范围等信息，
 * 用于质量检验时对照判定产品是否合格。
 */

// ── 依赖导入 ──
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { inspectionStandardAPI, materialAPI } from '@/api'

// ── 响应式状态 ──
const loading = ref(false)          // 列表加载状态
const submitting = ref(false)       // 表单提交加载状态
const list = ref([])                // 检验标准列表数据
const total = ref(0)                // 总记录数
const dialogVisible = ref(false)    // 新增/编辑弹窗可见性
const isEdit = ref(false)           // 当前是否为编辑模式
const editId = ref(null)            // 当前编辑的记录 ID
const formRef = ref(null)           // 表单引用
const materials = ref([])           // 物料列表，用于产品下拉选择

// ── 搜索条件 ──
const query = reactive({ page: 1, page_size: 10, product_name: '', item_name: '' })

// ── 表单数据与校验规则 ──
const form = reactive({
  product: null,
  item_name: '',
  standard_desc: '',
  tolerance: '',
  is_active: true,
})

const rules = {
  product: [{ required: true, message: '请选择产品', trigger: 'change' }],
  item_name: [{ required: true, message: '请输入检验项目', trigger: 'blur' }],
  standard_desc: [{ required: true, message: '请输入标准描述', trigger: 'blur' }],
}

// ── 数据获取 ──

/** 加载已启用的物料列表，用于新增标准时选择产品 */
async function loadMaterials() {
  try {
    const res = await materialAPI.active()
    materials.value = res.data || res || []
  } catch { /* ignore */ }
}

/** 获取检验标准分页列表，过滤空查询参数后请求 */
async function fetchData() {
  loading.value = true
  try {
    const params = { ...query }
    Object.keys(params).forEach(k => { if (params[k] === '' || params[k] === null || params[k] === undefined) delete params[k] })
    const res = await inspectionStandardAPI.list(params)
    list.value = res.data?.results || res.data || res.results || []
    total.value = res.data?.count || res.count || 0
  } catch { /* handled by interceptor */ }
  finally { loading.value = false }
}

// ── 搜索与重置 ──

/** 清空搜索条件并重新查询 */
function resetQuery() {
  query.product_name = ''
  query.item_name = ''
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
      product: row.product || null,
      item_name: row.item_name || '',
      standard_desc: row.standard_desc || '',
      tolerance: row.tolerance || '',
      is_active: row.is_active !== undefined ? row.is_active : true,
    })
  } else {
    isEdit.value = false
    editId.value = null
    Object.assign(form, { product: null, item_name: '', standard_desc: '', tolerance: '', is_active: true })
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
      await inspectionStandardAPI.update(editId.value, payload)
      ElMessage.success('更新成功')
    } else {
      await inspectionStandardAPI.create(payload)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    fetchData()
  } catch { /* handled by interceptor */ }
  finally { submitting.value = false }
}

/** 删除检验标准记录，需二次确认 */
function handleDelete(row) {
  ElMessageBox.confirm(`确认删除 "${row.item_name}" 吗？`, '提示', { type: 'warning' })
    .then(async () => {
      await inspectionStandardAPI.delete(row.id)
      ElMessage.success('删除成功')
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

<style scoped>
.page-card { background: #fff; border-radius: 8px; padding: 20px; }
</style>
