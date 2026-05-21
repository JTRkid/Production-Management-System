<template>
  <div class="page-card">
    <!-- 搜索区域 -->
    <el-form :model="query" inline>
      <el-form-item label="父物料">
        <el-input v-model="query.parent_material" placeholder="父物料名称" clearable />
      </el-form-item>
      <el-form-item label="子物料">
        <el-input v-model="query.child_material" placeholder="子物料名称" clearable />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="handleSearch">搜索</el-button>
        <el-button @click="handleReset">重置</el-button>
      </el-form-item>
    </el-form>

    <!-- 操作按钮 -->
    <div style="margin-bottom: 16px">
      <el-button type="primary" @click="handleAdd">新增BOM</el-button>
    </div>

    <!-- 数据表格 -->
    <el-table v-loading="loading" :data="list" border stripe>
      <el-table-column label="父物料" min-width="160">
        <template #default="{ row }">
          {{ row.parent_material_code }} - {{ row.parent_material_name }}
        </template>
      </el-table-column>
      <el-table-column label="子物料" min-width="160">
        <template #default="{ row }">
          {{ row.child_material_code }} - {{ row.child_material_name }}
        </template>
      </el-table-column>
      <el-table-column prop="quantity" label="用量" width="90" align="right" />
      <el-table-column prop="unit" label="单位" width="80" />
      <el-table-column prop="process_step" label="工序" min-width="120" />
      <el-table-column label="操作" width="220" fixed="right">
        <template #default="{ row }">
          <el-button link type="success" @click="handleViewTree(row)">展开BOM</el-button>
          <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
          <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div style="margin-top: 16px; text-align: right">
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.page_size"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="fetchData"
        @current-change="fetchData"
      />
    </div>

    <!-- 新增/编辑弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑BOM' : '新增BOM'"
      width="560px"
      :close-on-click-modal="false"
      @closed="handleDialogClosed"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-form-item label="父物料" prop="parent_material">
          <el-select v-model="form.parent_material" placeholder="请选择父物料" filterable style="width: 100%">
            <el-option
              v-for="m in activeMaterials"
              :key="m.id"
              :label="`${m.material_code} - ${m.material_name}`"
              :value="m.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="子物料" prop="child_material">
          <el-select v-model="form.child_material" placeholder="请选择子物料" filterable style="width: 100%">
            <el-option
              v-for="m in activeMaterials"
              :key="m.id"
              :label="`${m.material_code} - ${m.material_name}`"
              :value="m.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="用量" prop="quantity">
          <el-input-number v-model="form.quantity" :min="0" :precision="4" style="width: 100%" />
        </el-form-item>
        <el-form-item label="单位" prop="unit">
          <el-input v-model="form.unit" placeholder="如：个、件、kg" />
        </el-form-item>
        <el-form-item label="工序" prop="process_step">
          <el-input v-model="form.process_step" placeholder="请输入工序步骤" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- BOM树形结构弹窗 -->
    <el-dialog
      v-model="treeDialogVisible"
      :title="'BOM结构树 - ' + treeParentName"
      width="640px"
      :close-on-click-modal="false"
    >
      <div v-loading="treeLoading" style="min-height: 200px">
        <el-tree
          v-if="treeData.length > 0"
          :data="treeData"
          node-key="id"
          default-expand-all
          :props="{ label: 'label', children: 'children' }"
        />
        <el-empty v-else-if="!treeLoading" description="暂无BOM数据" />
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
/**
 * BOM（物料清单）管理页面
 * 提供 BOM 关系的增删改查功能，支持按父物料/子物料筛选，
 * 可通过树形结构查看某物料的完整 BOM 层级关系。
 */

// ── 依赖导入 ──
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { bomAPI, materialAPI } from '@/api'

// ── 响应式状态（主列表） ──
const loading = ref(false)          // 列表加载状态
const list = ref([])                // BOM 列表数据
const dialogVisible = ref(false)    // 新增/编辑弹窗可见性
const isEdit = ref(false)           // 当前是否为编辑模式
const submitLoading = ref(false)    // 提交按钮加载状态
const formRef = ref(null)           // 表单引用
const pagination = reactive({ page: 1, page_size: 10, total: 0 })
const activeMaterials = ref([])     // 已启用的物料列表，用于下拉选择

// ── 树形弹窗状态 ──
const treeDialogVisible = ref(false)  // BOM 树形弹窗可见性
const treeLoading = ref(false)        // 树形数据加载状态
const treeData = ref([])              // 树形结构数据
const treeParentName = ref('')        // 当前查看的父物料名称

// ── 搜索条件 ──
const query = reactive({
  parent_material: '',
  child_material: '',
})

// ── 表单数据与校验规则 ──
const form = reactive({
  id: null,
  parent_material: null,
  child_material: null,
  quantity: 1,
  unit: '',
  process_step: '',
})

const rules = {
  parent_material: [{ required: true, message: '请选择父物料', trigger: 'change' }],
  child_material: [{ required: true, message: '请选择子物料', trigger: 'change' }],
  quantity: [{ required: true, message: '请输入用量', trigger: 'blur' }],
  unit: [{ required: true, message: '请输入单位', trigger: 'blur' }],
}

// ── 数据获取 ──

/** 获取所有已启用的物料，用于父/子物料下拉选择 */
async function fetchActiveMaterials() {
  try {
    const res = await materialAPI.active()
    activeMaterials.value = res.data || res.results || res || []
  } catch {
    activeMaterials.value = []
  }
}

/** 获取 BOM 分页列表，支持按父/子物料名称筛选 */
async function fetchData() {
  loading.value = true
  try {
    const params = { page: pagination.page, page_size: pagination.page_size }
    if (query.parent_material) params.parent_material = query.parent_material
    if (query.child_material) params.child_material = query.child_material
    const res = await bomAPI.list(params)
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

/** 清空搜索条件并重新查询 */
function handleReset() {
  query.parent_material = ''
  query.child_material = ''
  pagination.page = 1
  fetchData()
}

// ── 增删改操作 ──

/** 打开新增 BOM 弹窗，并加载物料选项 */
function handleAdd() {
  isEdit.value = false
  resetForm()
  fetchActiveMaterials()
  dialogVisible.value = true
}

/** 打开编辑弹窗，将行数据回填到表单 */
function handleEdit(row) {
  isEdit.value = true
  Object.assign(form, {
    id: row.id,
    parent_material: row.parent_material,
    child_material: row.child_material,
    quantity: row.quantity,
    unit: row.unit || '',
    process_step: row.process_step || '',
  })
  fetchActiveMaterials()
  dialogVisible.value = true
}

/** 删除 BOM 记录，需二次确认 */
async function handleDelete(row) {
  try {
    await ElMessageBox.confirm('确定要删除该BOM记录吗？', '删除确认', {
      type: 'warning',
      confirmButtonText: '确定',
      cancelButtonText: '取消',
    })
    await bomAPI.delete(row.id)
    ElMessage.success('删除成功')
    fetchData()
  } catch { /* 取消或不操作 */ }
}

// ── 弹窗表单处理 ──

/** 重置表单数据并清除校验状态 */
function resetForm() {
  form.id = null
  form.parent_material = null
  form.child_material = null
  form.quantity = 1
  form.unit = ''
  form.process_step = ''
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
      parent_material: form.parent_material,
      child_material: form.child_material,
      quantity: form.quantity,
      unit: form.unit,
      process_step: form.process_step,
    }
    if (isEdit.value) {
      await bomAPI.update(form.id, data)
      ElMessage.success('更新成功')
    } else {
      await bomAPI.create(data)
      ElMessage.success('新增成功')
    }
    dialogVisible.value = false
    fetchData()
  } finally {
    submitLoading.value = false
  }
}

// ── BOM 树形结构查看 ──

/** 展开指定父物料的 BOM 树形结构，递归构建节点 */
async function handleViewTree(row) {
  treeDialogVisible.value = true
  treeParentName.value = `${row.parent_material_code} - ${row.parent_material_name}`
  treeLoading.value = true
  treeData.value = []
  try {
    const res = await bomAPI.tree(row.parent_material)
    const raw = res.data || res || []
    treeData.value = raw.map(item => buildTreeNode(item))
  } catch {
    treeData.value = []
  } finally {
    treeLoading.value = false
  }
}

/** 递归构建树节点，将后端数据转为 el-tree 所需格式 */
function buildTreeNode(node) {
  const result = {
    id: node.id,
    label: `${node.material?.material_code || ''} ${node.material?.material_name || ''}${node.quantity != null ? ` (x${node.quantity})` : ''}`,
  }
  if (node.children && node.children.length > 0) {
    result.children = node.children.map(child => buildTreeNode(child))
  }
  return result
}

// ── 生命周期 ──
onMounted(async () => {
  await fetchActiveMaterials()
  fetchData()
})
</script>

<style>
.page-card { background: #fff; border-radius: 8px; padding: 20px; }
</style>
