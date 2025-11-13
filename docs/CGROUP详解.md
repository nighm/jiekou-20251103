# cgroup 详解

## 什么是 cgroup？

**cgroup**（Control Groups，控制组）是 Linux 内核的一个功能，用于**限制、记录和隔离进程组使用的物理资源**（CPU、内存、磁盘I/O、网络等）。

### 简单理解

想象一下：
- **没有 cgroup**：所有程序可以无限制地使用系统资源，一个程序可能占满所有CPU和内存
- **有 cgroup**：系统管理员可以给每个程序或程序组分配资源配额，比如"这个程序最多用2GB内存"

## cgroup 的核心作用

### 1. **资源限制**（Resource Limiting）
限制进程组可以使用的资源上限：
- CPU：限制使用率（如最多使用50% CPU）
- 内存：限制最大内存使用量（如最多2GB）
- 磁盘I/O：限制读写速度
- 网络带宽：限制网络流量

### 2. **优先级控制**（Prioritization）
控制进程组获取资源的优先级：
- 高优先级进程优先获得CPU时间
- 低优先级进程在资源紧张时被限制

### 3. **资源统计**（Accounting）
记录进程组实际使用的资源：
- 统计CPU使用时间
- 统计内存使用量
- 用于计费、监控、分析

### 4. **进程控制**（Control）
对进程组进行统一操作：
- 暂停/恢复进程组
- 迁移进程组到其他CPU核心

## cgroup v1 vs cgroup v2

### cgroup v1（旧版本）

**特点**：
- 多个独立的控制器（controller），每个控制器单独管理
- 控制器挂载在不同的目录下：
  - `/sys/fs/cgroup/cpu/` - CPU控制
  - `/sys/fs/cgroup/memory/` - 内存控制
  - `/sys/fs/cgroup/blkio/` - 磁盘I/O控制
- 每个控制器有独立的层次结构

**问题**：
- 结构复杂，难以统一管理
- 不同控制器之间可能冲突
- 某些功能实现困难

### cgroup v2（新版本，CentOS 10默认）

**特点**：
- **统一层次结构**：所有控制器在同一个目录树中
- **单一挂载点**：`/sys/fs/cgroup/`
- **统一接口**：所有资源管理通过统一API
- **更好的资源管理**：避免控制器之间的冲突

**优势**：
- 更简单、更统一
- 更好的资源隔离
- 支持更多高级功能

## Docker 和 cgroup 的关系

### Docker 如何使用 cgroup？

Docker 使用 cgroup 来**限制和管理容器的资源使用**：

1. **创建容器时**：
   ```bash
   docker run --memory=2g --cpus=2 myapp
   ```
   Docker 会为容器创建 cgroup，限制：
   - 内存最多2GB
   - CPU最多使用2个核心

2. **运行时**：
   - Docker 通过 cgroup 监控容器资源使用
   - 如果容器超过限制，会被限制或终止

3. **隔离**：
   - 每个容器有独立的 cgroup
   - 容器之间资源互不影响

### 为什么会出现 "cgroup mountpoint does not exist" 错误？

**原因**：
- **CentOS 10** 使用 **cgroup v2**
- **Docker 19.03.9** 只支持 **cgroup v1**
- Docker 尝试访问 cgroup v1 的挂载点（如 `/sys/fs/cgroup/memory/`），但在 cgroup v2 中这些路径不存在

**错误流程**：
```
Docker 19.03.9 启动容器
    ↓
尝试访问 /sys/fs/cgroup/memory/（cgroup v1路径）
    ↓
CentOS 10 只有 /sys/fs/cgroup/（cgroup v2统一路径）
    ↓
路径不存在 → 错误：cgroup mountpoint does not exist
```

## 实际例子

### 例子1：限制容器内存

```bash
# 使用 cgroup v1（Docker 19.03.9）
docker run --memory=1g nginx
# Docker 会在 /sys/fs/cgroup/memory/docker/<容器ID>/ 创建限制

# 使用 cgroup v2（Docker 20.10+ 或 Podman）
podman run --memory=1g nginx
# Podman 会在 /sys/fs/cgroup/docker/<容器ID>/ 创建限制
```

### 例子2：查看容器的 cgroup 信息

```bash
# cgroup v1
cat /sys/fs/cgroup/memory/docker/<容器ID>/memory.limit_in_bytes

# cgroup v2
cat /sys/fs/cgroup/docker/<容器ID>/memory.max
```

## 总结

| 项目 | 说明 |
|------|------|
| **cgroup 是什么** | Linux内核的资源管理机制 |
| **主要作用** | 限制、统计、隔离进程的资源使用 |
| **v1 vs v2** | v2更统一、更简单，是未来趋势 |
| **Docker依赖** | Docker必须通过cgroup来管理容器资源 |
| **兼容性问题** | 旧版Docker不支持cgroup v2，导致容器无法启动 |

## 解决方案

1. **升级Docker**：使用Docker 20.10+（支持cgroup v2）
2. **使用Podman**：Podman原生支持cgroup v2
3. **降级cgroup**：修改系统使用cgroup v1（不推荐）

---

**关键点**：cgroup是Linux系统管理资源的基础机制，Docker/Podman等容器工具必须依赖它才能正常工作。版本不匹配就会导致容器无法启动。

