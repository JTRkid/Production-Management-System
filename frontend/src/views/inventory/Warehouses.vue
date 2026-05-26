<template>
  <div class="page-card">
    <!-- 搜索栏 -->
    <el-form :model="query" inline>
      <el-form-item label="编码">
        <el-input v-model="query.code" placeholder="输入编码" clearable style="width:160px" />
      </el-form-item>
      <el-form-item label="名称">
        <el-input v-model="query.name" placeholder="输入名称" clearable style="width:180px" />
      </el-form-item>
      <el-form-item label="类型">
        <el-select v-model="query.warehouse_type" placeholder="全部" clearable style="width:140px">
          <el-option label="原材料仓" value="raw" />
          <el-option label="成品仓" value="finished" />
          <el-option label="备件仓" value="spare" />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="fetchData">查询</el-button>
        <el-button @click="resetQuery">重置</el-button>
      </el-form-item>
    </el-form>

    <!-- 操作按钮 -->
    <div style="margin-bottom:12px">
      <el-button type="primary" @click="openDialog()">新增仓库</el-button>
    </div>

    <!-- 表格 -->
    <el-table :data="list" v-loading="loading" border stripe>
      <el-table-column prop="code" label="编码" width="120" />
      <el-table-column prop="name" label="名称" min-width="160" />
      <el-table-column prop="warehouse_type" label="类型" width="110">
        <template #default="{ row }">
          <el-tag :type="typeTag(row.warehouse_type)">{{ typeLabel(row.warehouse_type) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="keeper_name" label="库管员" width="100" />
      <el-table-column prop="is_active" label="启用" width="80">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'info'">{{ row.is_active ? '是' : '否' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="160" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="openDialog(row)">编辑</el-button>
          <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
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
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑仓库' : '新增仓库'" width="500px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="名称" prop="name">
          <el-input v-model="form.name" placeholder="仓库名称" />
        </el-form-item>
        <el-form-item label="编码" prop="code">
          <el-input v-model="form.code" placeholder="仓库编码" />
        </el-form-item>
        <el-form-item label="类型" prop="warehouse_type">
          <el-select v-model="form.warehouse_type" placeholder="请选择" style="width:100%">
            <el-option label="原材料仓" value="raw" />
            <el-option label="成品仓" value="finished" />
            <el-option label="备件仓" value="spare" />
          </el-select>
        </el-form-item>
        <el-form-item label="库管员" prop="keeper">
          <el-input v-model="form.keeper" placeholder="库管员姓名" />
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
 * 仓库管理页面
 * 提供仓库信息的增删改查功能，支持按编码/名称/仓库类型筛选。
 * 仓库类型包括原材料仓、成品仓、备件仓，每条记录关联库管员。
 */

// ── 依赖导入 ──
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { warehouseAPI } from '@/api'

// ── 响应式状态 ──
const loading = ref(false)          // 列表加载状态
const submitting = ref(false)       // 表单提交加载状态
const list = ref([])                // 仓库列表数据
const total = ref(0)                // 总记录数
const dialogVisible = ref(false)    // 新增/编辑弹窗可见性
const isEdit = ref(false)           // 当前是否为编辑模式
const editId = ref(null)            // 当前编辑的仓库 ID
const formRef = ref(null)           // 表单引用

// ── 搜索条件 ──
const query = reactive({ page: 1, page_size: 10, code: '', name: '', warehouse_type: '' })

// ── 表单数据与校验规则 ──
const form = reactive({
  name: '',
  code: '',
  warehouse_type: '',
  keeper: '',
  is_active: true,
})

const rules = {
  name: [{ required: true, message: '请输入名称', trigger: 'blur' }],
  code: [{ required: true, message: '请输入编码', trigger: 'blur' }],
  warehouse_type: [{ required: true, message: '请选择类型', trigger: 'change' }],
}

// ── 辅助函数 ──

/** 根据仓库类型返回对应的 Tag 样式类型 */
function typeTag(t) {
  const map = { raw: 'info', finished: 'success', spare: 'warning' }
  return map[t] || 'info'
}

/** 将仓库类型代码转换为中文标签 */
function typeLabel(t) {
  const map = { raw: '原材料仓', finished: '成品仓', spare: '备件仓' }
  return map[t] || t
}

// ── 数据获取 ──

/** 获取仓库分页列表，过滤空查询参数后请求 */
async function fetchData() {
  loading.value = true
  try {
    const params = { ...query }
    Object.keys(params).forEach(k => { if (params[k] === '' || params[k] === null || params[k] === undefined) delete params[k] })
    const res = await warehouseAPI.list(params)
    list.value = res.data?.results || res.data || res.results || []
    total.value = res.data?.count || res.count || 0
  } catch { /* handled by interceptor */ }
  finally { loading.value = false }
}

// ── 搜索与重置 ──

/** 清空搜索条件并重新查询 */
function resetQuery() {
  query.code = ''
  query.name = ''
  query.warehouse_type = ''
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
      name: row.name || '',
      code: row.code || '',
      warehouse_type: row.warehouse_type || '',
      keeper: row.keeper_name || row.keeper || '',
      is_active: row.is_active !== undefined ? row.is_active : true,
    })
  } else {
    isEdit.value = false
    editId.value = null
    Object.assign(form, { name: '', code: '', warehouse_type: '', keeper: '', is_active: true })
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
      await warehouseAPI.update(editId.value, payload)
      ElMessage.success('更新成功')
    } else {
      await warehouseAPI.create(payload)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    fetchData()
  } catch { /* handled by interceptor */ }
  finally { submitting.value = false }
}

/** 删除仓库记录，需二次确认 */
function handleDelete(row) {
  ElMessageBox.confirm(`确认删除仓库 "${row.name}" 吗？`, '提示', { type: 'warning' })
    .then(async () => {
      await warehouseAPI.delete(row.id)
      ElMessage.success('删除成功')
      fetchData()
    })
    .catch(() => {})
}

// ── 生命周期 ──
onMounted(() => fetchData())
</script>
