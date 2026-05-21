<template>
  <div class="page-card">
    <!-- 搜索栏 -->
    <el-form :model="query" inline>
      <el-form-item label="物料名称">
        <el-input v-model="query.material_name" placeholder="输入物料名称" clearable style="width:240px" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="fetchData">查询</el-button>
        <el-button @click="resetQuery">重置</el-button>
      </el-form-item>
    </el-form>

    <!-- 表格（只读，无CRUD） -->
    <el-table :data="list" v-loading="loading" border stripe>
      <el-table-column prop="material_code" label="物料编码" min-width="140" />
      <el-table-column prop="material_name" label="物料名称" min-width="160" />
      <el-table-column prop="warehouse_name" label="仓库" min-width="140" />
      <el-table-column prop="location" label="库位" width="120" />
      <el-table-column prop="quantity" label="库存数量" width="100" align="right" />
      <el-table-column prop="locked_quantity" label="锁定数量" width="100" align="right" />
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
  </div>
</template>

<script setup>
/**
 * 库存查询页面（只读）
 * 展示当前各仓库的库存数据，支持按物料名称筛选。
 * 表格显示物料编码、名称、所属仓库、库位、库存数量和锁定数量，
 * 仅用于查询，不提供新增/编辑/删除操作。
 */

// ── 依赖导入 ──
import { ref, reactive, onMounted } from 'vue'
import { inventoryAPI } from '@/api'

// ── 响应式状态 ──
const loading = ref(false)    // 列表加载状态
const list = ref([])          // 库存列表数据
const total = ref(0)          // 总记录数

// ── 搜索条件 ──
const query = reactive({ page: 1, page_size: 10, material_name: '' })

// ── 数据获取 ──

/** 获取库存分页列表，过滤空查询参数后请求 */
async function fetchData() {
  loading.value = true
  try {
    const params = { ...query }
    Object.keys(params).forEach(k => { if (params[k] === '' || params[k] === null || params[k] === undefined) delete params[k] })
    const res = await inventoryAPI.list(params)
    list.value = res.data?.results || res.data || res.results || []
    total.value = res.data?.count || res.count || 0
  } catch { /* handled by interceptor */ }
  finally { loading.value = false }
}

// ── 搜索与重置 ──

/** 清空搜索条件并重新查询 */
function resetQuery() {
  query.material_name = ''
  query.page = 1
  fetchData()
}

// ── 生命周期 ──
onMounted(() => fetchData())
</script>

<style scoped>
.page-card { background: #fff; border-radius: 8px; padding: 20px; }
</style>
