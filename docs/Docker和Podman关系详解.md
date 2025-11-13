# Docker和Podman关系详解

## 一、Docker和Podman是什么关系？

### 基本关系

**Docker** 和 **Podman** 都是**容器运行时工具**，用于创建、运行和管理容器。

### 相似之处

| 特性 | Docker | Podman |
|------|--------|--------|
| **核心功能** | 运行容器 | 运行容器 |
| **命令兼容性** | 标准命令 | 与Docker命令基本兼容 |
| **镜像格式** | OCI标准 | OCI标准（相同） |
| **容器格式** | OCI标准 | OCI标准（相同） |

**命令对比**：
```bash
# Docker命令
docker run -d --name nginx nginx:latest
docker ps
docker images

# Podman命令（几乎相同）
podman run -d --name nginx nginx:latest
podman ps
podman images
```

### 关键区别

| 特性 | Docker | Podman |
|------|--------|--------|
| **架构** | 客户端-服务器（需要daemon） | 无daemon，直接运行 |
| **权限** | 通常需要root权限 | 支持rootless（无需root） |
| **服务** | 需要docker.service | 不需要systemd服务 |
| **安全性** | daemon有安全风险 | 更安全（无daemon） |
| **cgroup v2支持** | 20.10+才支持 | 原生支持 |

### 架构对比

**Docker架构**：
```
docker命令
    ↓
Docker客户端
    ↓
Docker daemon（后台服务）
    ↓
containerd
    ↓
容器
```

**Podman架构**：
```
podman命令
    ↓
直接调用
    ↓
容器（无需daemon）
```

### 当前系统状态

根据检查结果：

1. **Docker命令**：`/usr/local/bin/docker` 是一个**包装脚本**，实际调用Podman
   ```bash
   # 当前docker命令内容
   #!/bin/bash
   podman "$@"
   ```

2. **Docker服务**：系统中存在 `docker.service`，但这是**真正的Docker daemon**（之前安装的）

3. **Podman**：`/usr/bin/podman` 是真正的Podman程序

4. **实际使用**：
   - 执行 `docker` 命令 → 调用Podman
   - Docker daemon服务在运行，但可能未被使用

## 二、升级Docker版本对系统的影响

### 当前状态

- **Docker命令**：指向Podman的别名脚本
- **Docker服务**：Docker daemon正在运行（版本可能是19.03.9）
- **Docker数据**：`/data/docker/` 目录存在，包含：
  - 容器数据
  - 镜像数据
  - 网络配置
  - 存储驱动数据

### 升级Docker的影响

#### 1. **会替换当前的docker别名**

**当前**：
```bash
/usr/local/bin/docker → Podman包装脚本
```

**升级后**：
```bash
/usr/local/bin/docker → 真正的Docker客户端
```

**影响**：
- ✅ 安装包可以正常使用真正的Docker
- ⚠️ 如果之前依赖Podman，需要调整

#### 2. **需要停止现有Docker服务**

```bash
sudo systemctl stop docker
sudo systemctl disable docker  # 如果不再需要
```

**影响**：
- 如果有容器在运行，会被停止
- 需要迁移或备份数据

#### 3. **数据迁移**

**Docker数据位置**：`/data/docker/`

**需要备份的内容**：
- 容器配置和数据
- 镜像文件
- 网络配置
- 卷数据

**迁移步骤**：
```bash
# 1. 停止Docker服务
sudo systemctl stop docker

# 2. 备份数据目录
sudo cp -r /data/docker /data/docker.backup

# 3. 升级Docker

# 4. 如果新版本数据格式兼容，可以直接使用
# 如果不兼容，需要重新拉取镜像和创建容器
```

#### 4. **配置文件调整**

**当前配置**：`/etc/docker/daemon.json`
```json
{
  "registry-mirrors": [...],
  "data-root": "/data/docker",
  "log-driver": "json-file",
  ...
}
```

**影响**：
- 配置文件通常兼容新版本
- 可能需要添加新版本的特定配置
- cgroup v2相关配置可能需要调整

#### 5. **对其他服务的影响**

**检查结果**：没有其他服务直接依赖Docker

**影响**：
- ✅ 升级不会影响其他系统服务
- ⚠️ 如果有自定义脚本使用Docker，需要测试

### 升级步骤（如果决定升级）

```bash
# 1. 备份当前状态
sudo systemctl stop docker
sudo cp -r /data/docker /data/docker.backup
sudo cp /etc/docker/daemon.json /etc/docker/daemon.json.backup

# 2. 卸载旧版本
sudo yum remove docker docker-client docker-client-latest \
    docker-common docker-latest docker-latest-logrotate \
    docker-logrotate docker-engine

# 3. 安装新版本（20.10+）
# 添加Docker仓库
sudo yum-config-manager --add-repo \
    https://download.docker.com/linux/centos/docker-ce.repo

# 安装新版本
sudo yum install docker-ce docker-ce-cli containerd.io

# 4. 恢复配置
sudo cp /etc/docker/daemon.json.backup /etc/docker/daemon.json

# 5. 启动服务
sudo systemctl start docker
sudo systemctl enable docker

# 6. 验证
docker --version  # 应该显示20.10+
docker info | grep cgroup  # 应该显示v2
```

## 三、安装包对Docker版本的要求

### 检查结果

**安装包**：`Klsec-yg-146-251024-01`（Makeself 2.4.0自解压脚本）

**检查发现**：
- ❌ **没有明确的版本要求**
- ❌ **没有版本检查命令**
- ✅ **只要求docker命令可用**

### 安装包的工作方式

1. **自解压**：Makeself脚本解压内部文件
2. **执行安装脚本**：内部包含 `install.sh` 脚本
3. **调用docker命令**：安装脚本会执行类似 `docker run` 的命令
4. **不检查版本**：只要 `docker` 命令存在且可用即可

### 兼容性分析

| Docker版本 | cgroup支持 | 是否可用 |
|-----------|-----------|---------|
| Docker 19.03.9 | ❌ 不支持v2 | ❌ 在CentOS 10上不可用 |
| Docker 20.10+ | ✅ 支持v2 | ✅ 可用 |
| Podman（通过别名） | ✅ 支持v2 | ✅ 可用 |

### 结论

**安装包要求**：
- ✅ `docker` 命令必须存在
- ✅ `docker` 命令必须能正常工作
- ❌ **不检查具体版本号**
- ❌ **不检查cgroup版本**

**当前方案（Podman别名）**：
- ✅ 满足安装包要求（docker命令存在）
- ✅ 可以正常工作（支持cgroup v2）
- ✅ **无需修改安装包**

## 四、推荐方案对比

### 方案1：保持现状（使用Podman别名）⭐⭐⭐⭐⭐

**优点**：
- ✅ 无需升级，立即可用
- ✅ 无需修改安装包
- ✅ 无需数据迁移
- ✅ Podman更安全（无daemon）
- ✅ 原生支持cgroup v2

**缺点**：
- ⚠️ 如果安装包有特殊Docker功能，可能不兼容（但通常不会）

**操作**：
```bash
# 直接运行安装脚本即可
sudo bash /tmp/Klsec-yg-146-251024-01
```

### 方案2：升级Docker到20.10+ ⭐⭐⭐

**优点**：
- ✅ 使用真正的Docker
- ✅ 支持cgroup v2
- ✅ 更好的兼容性

**缺点**：
- ❌ 需要停止服务
- ❌ 需要备份数据
- ❌ 需要重新配置
- ❌ 有数据丢失风险
- ❌ 需要网络访问Docker仓库

**操作**：
- 需要执行完整的升级步骤（见上文）

## 五、最终建议

### 推荐：使用Podman别名方案

**理由**：
1. ✅ **最简单**：无需任何修改，直接可用
2. ✅ **最安全**：无需停止服务，无数据风险
3. ✅ **最快速**：立即可用，无需等待升级
4. ✅ **满足需求**：安装包只要求docker命令可用，不检查版本

**如果必须升级Docker**：
- 先备份所有数据
- 在测试环境验证
- 确保网络可以访问Docker仓库
- 准备回滚方案

---

**总结**：
- Docker和Podman是**竞争关系**，但**命令兼容**
- 升级Docker**有影响**，需要备份和迁移
- 安装包**不检查版本**，只要docker命令可用即可
- **推荐使用Podman别名**，最简单且安全

