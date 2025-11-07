# 三种任务执行流程详解

## 1. 平台同步任务 (Platform Sync)

**API入口：** `POST /api/virtualization/<platform_id>/sync`

**执行流程：**
```
API调用
  ↓
创建 CollectionTask (host_ids = [-platform_id])
  ↓
启动 Celery 任务: sync_platform_resources_task
  ↓
tasks/collector.py::sync_platform_resources_task()
  ├─ 创建 VMwareCollector
  ├─ collector.connect()                    # 连接平台
  ├─ 快速获取VM和ESXi总数 (10%进度)
  ├─ collector.collect()                    # ⚠️ 获取所有VM详细信息（耗时，30%进度）
  │   └─ vmware.py::collect()
  │       ├─ _get_esxi_info()              # 获取ESXi信息
  │       └─ _get_vms_info()               # ⚠️ 遍历所有VM获取详细信息（耗时）
  │
  ├─ 创建 VMwareSyncService
  ├─ 包装 _sync_esxi_host 和 _sync_vm 方法（添加进度跟踪）
  └─ sync_service.sync_from_collector()
      ├─ 遍历所有 ESXi 主机
      │   └─ _sync_esxi_host()             # ✅ 每同步一个更新进度 (30%-100%)
      └─ 遍历所有 VM
          └─ _sync_vm()                     # ✅ 每同步一个更新进度 (30%-100%)
```

**数据流：**
- 输入：平台凭证
- 输出：创建/更新所有ESXi主机和VM到数据库
- 目的：发现和同步平台资源清单

**进度更新：**
- 0% → 10%：连接平台，获取总数
- 10% → 30%：收集所有VM详细信息（`collector.collect()`）
- 30% → 100%：同步ESXi和VM到数据库（每同步一个更新）

---

## 2. 平台采集任务 (Platform Collection)

**API入口：** `POST /api/hosts/batch/collect` (hosts with source='platform')

**执行流程：**
```
API调用 (选择平台主机)
  ↓
创建 CollectionTask (host_ids = [选中的主机ID列表])
  ↓
启动 Celery 任务: collect_platform_hosts_task
  ↓
tasks/collector.py::collect_platform_hosts_task()
  └─ PlatformCollectorService.collect_platform_hosts()
      └─ _collect_vmware_hosts(hosts)
          ├─ 创建 VMwareCollector
          ├─ collector.connect()
          ├─ 获取VM对象列表（不收集详细信息）
          ├─ 第一遍：快速匹配选中的VM
          ├─ 第二遍：只对匹配的VM调用 _get_vm_info()  ✅ 只收集选中的VM
          └─ 遍历选中的主机
              └─ 更新主机数据 + 更新进度 ✅
```

**数据流：**
- 输入：已存在的平台主机ID列表
- 输出：更新这些主机的详细信息
- 目的：更新已存在主机的配置数据

**进度更新：**
- 每采集完一个主机，立即更新进度

---

## 3. 普通采集任务 (Normal Collection)

**API入口：** `POST /api/hosts/batch/collect` (hosts with source='scan' or 'manual')

**执行流程：**
```
API调用 (选择扫描/手动添加的主机)
  ↓
创建 CollectionTask (host_ids = [选中的主机ID列表])
  ↓
启动 Celery 任务: collect_hosts_task
  ↓
tasks/collector.py::collect_hosts_task()
  └─ CollectorService.collect_hosts()
      ├─ 使用 ThreadPoolExecutor 并发采集
      └─ 对每个主机
          └─ _collect_single_host()
              ├─ 获取主机凭证
              ├─ 创建对应的 Collector (Linux/Windows/VMware)
              ├─ collector.collect()        # SSH连接主机收集数据
              └─ 更新主机数据 + 更新进度 ✅
```

**数据流：**
- 输入：已存在的主机ID列表 + 主机凭证
- 输出：更新这些主机的详细信息
- 目的：通过SSH/远程连接采集主机数据

**进度更新：**
- 每采集完一个主机，立即更新进度

---

## 关键区别总结

| 任务类型 | API入口 | Celery任务 | 服务类 | 数据来源 | 是否需要主机凭证 | 是否创建新主机 |
|---------|--------|-----------|--------|---------|----------------|--------------|
| **平台同步** | `/api/virtualization/<id>/sync` | `sync_platform_resources_task` | `VMwareSyncService` | 平台API | ❌ 不需要 | ✅ 会创建 |
| **平台采集** | `/api/hosts/batch/collect` | `collect_platform_hosts_task` | `PlatformCollectorService` | 平台API | ❌ 不需要 | ❌ 不创建 |
| **普通采集** | `/api/hosts/batch/collect` | `collect_hosts_task` | `CollectorService` | SSH/远程连接 | ✅ 需要 | ❌ 不创建 |

## 进度更新对比

| 任务类型 | 进度更新时机 | 进度更新频率 | 实时性 |
|---------|------------|------------|--------|
| **平台同步** | 连接(10%) → 收集(30%) → 同步(30%-100%) | 每同步一个ESXi/VM | ⚠️ 收集阶段无进度 |
| **平台采集** | 采集阶段 | 每采集一个主机 | ✅ 实时 |
| **普通采集** | 采集阶段 | 每采集一个主机 | ✅ 实时 |

## 当前问题

**平台同步进度问题：**
- `collector.collect()` 阶段会遍历所有VM获取详细信息，这个过程很耗时但没有细粒度进度更新
- 只有在开始同步到数据库时才有进度更新
- 如果平台有很多VM，`collect()` 阶段可能需要几分钟，期间进度从10%到30%没有中间更新

**优化建议：**
- 可以考虑在 `collector.collect()` 阶段也添加进度回调
- 或者优化为流式处理，边收集边同步

