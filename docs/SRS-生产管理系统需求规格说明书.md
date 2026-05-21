# 生产管理系统 — 软件需求规格说明书 (SRS)

**版本**: V1.0  
**日期**: 2026-05-19  
**项目**: 中小型制造企业生产管理系统

---

## 目录

1. [引言](#1-引言)
2. [总体描述](#2-总体描述)
3. [功能需求](#3-功能需求)
4. [非功能需求](#4-非功能需求)
5. [数据字典](#5-数据字典)

---

## 1. 引言

### 1.1 目的

本文档定义生产管理系统的全部功能与非功能需求，作为后续设计、开发、测试的依据。

### 1.2 范围

系统面向中小型制造企业，覆盖从客户订单、采购供应、生产计划、物料管理、工单派发、过程跟踪、质量检验到成品入库的全业务流程。

### 1.3 技术栈

| 层级 | 技术 | 版本 |
|------|------|------|
| 后端框架 | Django + Django REST Framework | 5.0 |
| 数据库 | SQLite（开发）/ MySQL 8.0（生产） | — |
| 认证 | JWT（djangorestframework-simplejwt） | — |
| 过滤 | django-filters | 24.2 |
| 前端框架 | Vue 3 + Vite | 3.5 |
| UI 组件库 | Element Plus | 2.14 |
| 状态管理 | Pinia | 3.0 |
| 路由 | Vue Router | 4.6 |
| 图表 | ECharts | 5.x |

### 1.4 角色定义

| 角色 | 编码 | 描述 |
|------|------|------|
| 系统管理员 | admin | 拥有全部权限，管理系统配置和用户 |
| 业务员 | salesman | 管理客户档案、创建销售订单、跟进订单交付 |
| 采购员 | purchaser | 管理供应商、下达采购订单、跟催到货 |
| 生产计划员 | planner | 制定生产计划、排产、下发工单 |
| 车间主任 | workshop_director | 审核工单、调度人员、查看生产进度 |
| 班组长 | foreman | 接收工单、分配任务、报工 |
| 工人 | worker | 执行工序报工 |
| 质检员 | inspector | 执行质量检验、出具检验报告 |
| 库管员 | storekeeper | 管理物料与成品出入库 |

---

## 2. 总体描述

### 2.1 业务流程

```
业务员创建客户 → 创建销售订单 → 计划员审批订单
    ↓
计划员创建生产计划 → 审批 → 下发 → 生成工单
    ↓
车间主任派发工单 → 班组长开始生产 → 工人逐工序报工
    ↓
质检员过程/完工检验 → 完工入库 → 销售发货
```

物料采购流程：

```
计划员审批计划 → 采购员创建采购订单 → 审批
    ↓
供应商交货 → 库管员收货入库 → 库存更新
```

### 2.2 系统架构

```
┌─────────────────────────────────────────┐
│               Vue 3 前端 (SPA)            │
│          Element Plus + ECharts          │
├─────────────────────────────────────────┤
│     Django REST Framework (JWT API)      │
│           django-filters                 │
├──────────┬──────────┬───────────────────┤
│ 基础数据  │  生产管理  │      报表分析       │
├──────────┴──────────┴───────────────────┤
│       SQLite（开发）/ MySQL 8.0          │
└─────────────────────────────────────────┘
```

---

## 3. 功能需求

### 3.1 模块一：系统管理 (accounts + sys_admin)

| ID | 功能 | 描述 | 优先级 | 状态 |
|----|------|------|--------|------|
| SA-01 | 用户管理 | 创建、编辑、禁用用户，分配角色 | P0 | 已实现 |
| SA-02 | 角色管理 | 定义角色及其权限集合 | P0 | 已实现 |
| SA-03 | 部门/车间管理 | 管理组织架构（工厂→车间→班组） | P0 | 已实现 |
| SA-04 | 个人信息 | 修改密码、查看个人信息 | P1 | 已实现 |
| SA-05 | 操作日志 | 记录关键操作（谁在何时做了什么） | P1 | 已实现 |

### 3.2 模块二：业务管理 (business)

| ID | 功能 | 描述 | 优先级 | 状态 |
|----|------|------|--------|------|
| BIZ-01 | 客户管理 | 维护客户档案（名称、联系人、地址），客户分级，合作状态 | P0 | 已实现 |
| BIZ-02 | 销售订单管理 | 创建销售订单，指定产品、数量、交期；订单状态追踪（待审核→生产中→已发货→已完成）；订单变更记录 | P0 | 已实现 |
| BIZ-03 | 采购管理 | 供应商档案维护；采购订单创建/审批/跟催；收货确认 | P0 | 已实现 |

### 3.3 模块三：基础数据 (base_data)

| ID | 功能 | 描述 | 优先级 | 状态 |
|----|------|------|--------|------|
| BD-01 | 物料主数据 | 原材料、半成品、成品编码/名称/规格/单位 | P0 | 已实现 |
| BD-02 | BOM 管理 | 树形产品结构：成品→半成品→原料，含用量与工序 | P0 | 已实现 |
| BD-03 | 工艺路线 | 定义产品加工的工序顺序与标准工时 | P0 | 已实现 |
| BD-04 | 设备台账 | 设备编号、名称、型号、状态（正常/维修/报废） | P1 | 已实现 |
| BD-05 | 工作中心 | 定义产能单位（产线/工作站），绑定设备与班组 | P1 | 已实现 |

### 3.4 模块四：生产计划 (prod_plan)

| ID | 功能 | 描述 | 优先级 | 状态 |
|----|------|------|--------|------|
| PP-01 | 主生产计划 | 创建月度/周度生产计划，指定产品、数量、交期 | P0 | 已实现 |
| PP-02 | MRP 运算 | 根据计划自动计算所需物料，生成采购/领料建议 | P1 | 规划中 |
| PP-03 | 计划审批 | 计划提交→审批→驳回流程 | P1 | 已实现 |
| PP-04 | 计划变更 | 计划变更记录，版本追溯 | P2 | 已实现 |
| PP-05 | 产能检查 | 排产时检查工作中心负荷是否超限 | P2 | 规划中 |

### 3.5 模块五：工单管理 (work_order)

| ID | 功能 | 描述 | 优先级 | 状态 |
|----|------|------|--------|------|
| WO-01 | 工单生成 | 由生产计划拆分生成工单，或手动创建 | P0 | 已实现 |
| WO-02 | 工单下发 | 工单下发给指定车间/产线 | P0 | 已实现 |
| WO-03 | 工单领料 | 关联物料领用记录，扣减库存 | P1 | 规划中 |
| WO-04 | 工单报工 | 班组长/工人汇报完工数量、工时、不良数 | P0 | 已实现 |
| WO-05 | 工单状态 | 状态流转：待派发→生产中→已完成→已关闭 | P0 | 已实现 |
| WO-06 | 工单甘特图 | 以甘特图形式展示工单排程 | P2 | 规划中 |

### 3.6 模块六：生产过程跟踪 (prod_track)

| ID | 功能 | 描述 | 优先级 | 状态 |
|----|------|------|--------|------|
| PT-01 | 工序报工 | 按工序汇报生产进度（扫码/输入） | P0 | 已实现 |
| PT-02 | 生产看板 | 实时展示当日/当班产量、达成率、不良率 | P1 | 已实现 |
| PT-03 | 异常上报 | 设备故障、物料短缺等异常实时上报 | P2 | 规划中 |
| PT-04 | 工时统计 | 统计工人/班组实际工时 vs 标准工时 | P1 | 已实现 |

### 3.7 模块七：质量管理 (quality)

| ID | 功能 | 描述 | 优先级 | 状态 |
|----|------|------|--------|------|
| QC-01 | 检验标准 | 定义成品/半成品检验项目与允收标准 | P0 | 已实现 |
| QC-02 | 过程检验 | 工序中按检验标准记录检验结果 | P0 | 已实现 |
| QC-03 | 完工检验 | 工单完成后进行最终检验 | P0 | 已实现 |
| QC-04 | 不良品处理 | 记录不良品、处理方式（返工/报废/让步接收） | P1 | 已实现 |
| QC-05 | 质量报表 | 不良率趋势图、Pareto分析 | P2 | 部分实现（已有趋势图） |

### 3.8 模块八：库存管理 (inventory)

| ID | 功能 | 描述 | 优先级 | 状态 |
|----|------|------|--------|------|
| INV-01 | 仓库管理 | 仓库/库位定义 | P1 | 已实现 |
| INV-02 | 入库管理 | 采购入库、生产入库、其他入库 | P0 | 已实现 |
| INV-03 | 出库管理 | 生产领料出库、销售出库 | P0 | 已实现 |
| INV-04 | 库存查询 | 按物料/库位查询实时库存量 | P0 | 已实现 |
| INV-05 | 库存盘点 | 盘点单生成、差异处理 | P2 | 规划中 |

### 3.9 模块九：报表分析（看板，dashboard）

| ID | 功能 | 描述 | 优先级 | 状态 |
|----|------|------|--------|------|
| KB-01 | 生产日报 | 当日产出、不良、效率汇总 | P1 | 已实现 |
| KB-02 | 工单完成率 | 按时完成率、延期工单统计 | P1 | 已实现 |
| KB-03 | 质量趋势 | 近30天不良率、返工率趋势 | P2 | 已实现 |
| KB-04 | 产能利用率 | 各工作中心负荷率统计 | P2 | 已实现 |

---

## 4. 非功能需求

| 编号 | 分类 | 需求描述 |
|------|------|----------|
| NF-01 | 性能 | 常规查询响应 < 500ms；报表查询 < 3s |
| NF-02 | 可用性 | 系统可用性 ≥ 99%（计划内停机除外） |
| NF-03 | 安全性 | JWT 认证；密码加密存储；权限精细到按钮级别 |
| NF-04 | 易用性 | 中文界面；PC Web 端；表单支持回车提交与基本校验 |
| NF-05 | 可维护性 | 后端模块化 app 拆分；前端按模块组织 views |
| NF-06 | 数据一致性 | 库存扣减、工单状态变更等关键操作使用数据库事务 |

---

## 5. 数据字典（核心实体摘要）

### 5.1 物料 (Material)
```
id               BIGINT PK
material_code    VARCHAR(64)  UNIQUE  — 物料编码
material_name    VARCHAR(128) — 物料名称
specification    VARCHAR(256) — 规格型号
unit             VARCHAR(16)  — 计量单位
material_type    ENUM('raw','semi','finished') — 物料类型
unit_cost        DECIMAL(10,2) DEFAULT 0 — 参考单价
is_active        BOOLEAN DEFAULT True   — 是否启用
created_at / updated_at
```

### 5.2 BOM 明细 (BOMItem)
```
id               BIGINT PK
parent_material  FK→Material — 父物料
child_material   FK→Material — 子物料
quantity         DECIMAL(10,4) — 用量
unit             VARCHAR(16)  — 单位
process_step     INT          — 所属工序序号(可选)
```

### 5.3 工艺路线 (Route / RouteStep)
```
Route: id, product(FK→Material), route_name, is_active
RouteStep: id, route(FK), step_no, step_name, work_center(FK),
           standard_hours, description
```

### 5.4 生产计划 (ProductionPlan)
```
id               BIGINT PK
plan_no          VARCHAR(32) UNIQUE  — 计划单号
plan_type        ENUM('month','week','urgent')
product          FK→Material
plan_quantity    INT                — 计划数量
scheduled_start  DATE               — 计划开始
scheduled_end    DATE               — 计划截止
status           ENUM('draft','approved','released','completed','cancelled')
approved_by / approved_at
created_by / created_at
```

### 5.5 生产工单 (WorkOrder)
```
id               BIGINT PK
wo_no            VARCHAR(32) UNIQUE  — 工单号
production_plan  FK→ProductionPlan(NULLABLE)
product          FK→Material
order_quantity   INT                — 生产数量
completed_quantity INT DEFAULT 0    — 已完成数量
defect_quantity  INT DEFAULT 0      — 不良品数量
workshop         FK→Workshop
route            FK→Route
priority         ENUM('normal','urgent','low')
status           ENUM('pending','dispatched','in_progress','completed','closed')
started_at / completed_at
created_by / created_at
```

### 5.6 报工记录 (WorkReport)
```
id               BIGINT PK
work_order       FK→WorkOrder
route_step       FK→RouteStep        — 当前工序
worker           FK→User
report_quantity  INT                 — 本次报工合格数量
defect_quantity  INT DEFAULT 0       — 本次报工不良数量
work_hours       DECIMAL(5,2)        — 实际上报工时
report_time      DATETIME
remark           VARCHAR(512)
```

### 5.7 检验记录 (InspectionRecord)
```
id               BIGINT PK
work_order       FK→WorkOrder(NULLABLE)
inspection_type  ENUM('in_process','final')
product          FK→Material
inspector        FK→User
sample_quantity  INT
pass_quantity    INT
defect_quantity  INT
defect_details   JSON                 — [{defect_type, count}]
result           ENUM('pass','fail','concession')
report_no        VARCHAR(32)
inspected_at     DATETIME
```

### 5.8 库存记录 (Inventory)
```
id               BIGINT PK
material         FK→Material
warehouse        FK→Warehouse
location         VARCHAR(64)  — 库位（文本）
quantity         DECIMAL(12,4) DEFAULT 0
locked_quantity  DECIMAL(12,4) DEFAULT 0  — 已锁定/已分配数量
updated_at
— UNIQUE(material, warehouse, location)
```

### 5.9 出入库单 (InventoryTransaction)
```
id               BIGINT PK
transaction_no   VARCHAR(32) UNIQUE
transaction_type ENUM('purchase_in','produce_in','material_out','sale_out','return_in','other')
material         FK→Material
quantity         DECIMAL(12,4)  — 正数入库，负数出库
warehouse        FK→Warehouse
source_doc_type  VARCHAR(32)    — 来源单据类型(work_order等)
source_doc_id    BIGINT         — 来源单据ID
operator         FK→User
remark           VARCHAR(256)
created_at
```

### 5.10 客户 (Customer)
```
id               BIGINT PK
customer_code    VARCHAR(32)  UNIQUE  — 客户编码
customer_name    VARCHAR(128) — 客户名称
contact_person   VARCHAR(64)  — 联系人
contact_phone    VARCHAR(32)  — 联系电话
address          VARCHAR(256) — 地址
customer_level   ENUM('A','B','C')  — 客户等级
is_active        BOOLEAN      — 是否启用
created_at / updated_at
```

### 5.11 销售订单 (SalesOrder)
```
id               BIGINT PK
so_no            VARCHAR(32)  UNIQUE  — 订单号
customer         FK→Customer
product          FK→Material (成品)
order_quantity   INT                 — 订单数量
delivered_quantity INT DEFAULT 0     — 已发货数量
unit_price       DECIMAL(10,2)       — 单价
total_amount     DECIMAL(12,2)       — 总金额
scheduled_date   DATE                — 要求交期
status           ENUM('draft','approved','in_production','shipped','completed','cancelled')
sales_person     FK→User             — 业务员
approved_by / approved_at
created_by / created_at
```

### 5.12 供应商 (Supplier)
```
id               BIGINT PK
supplier_code    VARCHAR(32)  UNIQUE  — 供应商编码
supplier_name    VARCHAR(128) — 供应商名称
contact_person   VARCHAR(64)
contact_phone    VARCHAR(32)
supply_category  VARCHAR(128) — 供应品类
is_active        BOOLEAN
created_at / updated_at
```

### 5.13 采购订单 (PurchaseOrder)
```
id               BIGINT PK
po_no            VARCHAR(64)  UNIQUE  — 采购单号
supplier         FK→Supplier
material         FK→Material (原材料/半成品)
order_quantity   INT                 — 采购数量
received_quantity INT DEFAULT 0      — 已收货数量
unit_price       DECIMAL(10,2)       — 单价
total_amount     DECIMAL(12,2)       — 总金额
ordered_date     DATE                — 下单日期
expected_date    DATE                — 预计到货日期
status           ENUM('draft','approved','ordered','partial_received','received','cancelled')
source_doc_type  VARCHAR(32) NULL    — 来源单据类型(production_plan等)
source_doc_id    BIGINT NULL         — 来源单据ID
buyer            FK→User             — 采购员
approved_by / approved_at
created_by / created_at / updated_at
```

### 5.14 其他支撑实体
- **Workshop** (车间): id, name, code, manager(FK→User), is_active
- **WorkCenter** (工作中心): id, name, code, workshop(FK), capacity_per_day, is_active
- **Warehouse** (仓库): id, name, code, warehouse_type ENUM('raw','finished','spare'), keeper(FK→User), is_active
- **Equipment** (设备): id, name, code, model, work_center(FK), status, purchase_date
- **OperationLog** (操作日志): id, user(FK→User), action, target_model, target_id, detail, created_at

---

## 附录：模块与后端 App 映射

| 模块 | Django App | 前端 views 目录 |
|------|------------|----------------|
| 系统管理 | `apps/accounts` + `apps/sys_admin` | `src/views/sys-admin/` |
| 业务管理 | `apps/business` | `src/views/business/` |
| 基础数据 | `apps/base_data` | `src/views/base-data/` |
| 生产计划 | `apps/prod_plan` | `src/views/prod-plan/` |
| 工单管理 | `apps/work_order` | `src/views/work-order/` |
| 过程跟踪 | `apps/prod_track` | `src/views/prod-track/` |
| 质量管理 | `apps/quality` | `src/views/quality/` |
| 库存管理 | `apps/inventory` | `src/views/inventory/` |
| 报表看板 | `apps/dashboard` | `src/views/dashboard/` |

---
