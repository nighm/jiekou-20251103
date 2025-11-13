# Klsec安装流程详细分析

## 执行流程分析

### 阶段1：脚本解压和初始化

```
Verifying archive integrity...  100%   All good.
Uncompressing Klsec-yg-146-251024-01  100%
```

**说明**：
- 这是Makeself自解压脚本
- 验证完整性后解压内部文件到临时目录

### 阶段2：环境初始化

```
SELINUX=enforcing
Init kse environment.....
move deb/etc success!
move deb/opt success!
move deb/usr success!
```

**说明**：
- 检测SELinux状态（enforcing模式）
- 初始化Klsec环境
- 将解压出的`deb/etc`、`deb/opt`、`deb/usr`目录内容移动到系统对应目录
- 这些是Klsec的系统文件

### 阶段3：初始化私有数据模板

```
start init private data template
ps/480G.img-guest.udf
ps/120G.img-guest.udf
ps/40G.img-guest.udf
...
init private data template success!
```

**说明**：
- 创建私有数据模板
- 生成多个不同大小的镜像文件（.udf和.mdf格式）
- 这些可能是虚拟机磁盘镜像或数据存储文件

### 阶段4：创建系统用户

```
useradd：用户"dnsmasq"已存在
```

**说明**：
- 尝试创建dnsmasq用户
- 用户已存在，跳过（不影响安装）

### 阶段5：检查Docker

```
Check that Docker is installed.....
./install.sh: 行 78: docker: 未找到命令
```

**关键点**：
- 脚本检查`docker`命令是否存在
- **未找到命令**（因为docker别名指向podman，但脚本可能直接调用docker二进制文件）
- 或者docker命令不在PATH中

### 阶段6：安装Docker（从脚本自带）

```
Start install docker ......
docker/docker-init
docker/runc
docker/docker
docker/docker-proxy
docker/containerd
docker/ctr
docker/dockerd
docker/containerd-shim
```

**说明**：
- 脚本自带Docker 19.03.9的二进制文件
- 解压并复制到系统目录（通常是`/usr/bin/`）
- 包含Docker的所有组件：
  - `docker` - Docker客户端
  - `dockerd` - Docker守护进程
  - `containerd` - 容器运行时
  - `runc` - OCI运行时
  - `docker-init` - 初始化进程
  - `docker-proxy` - 网络代理
  - `containerd-shim` - containerd的shim层

```
Created symlink '/etc/systemd/system/multi-user.target.wants/docker.service' → '/usr/lib/systemd/system/docker.service'.
Docker version 19.03.9, build 9d988398e7
Install docker success
```

**说明**：
- 创建systemd服务链接（开机自启）
- 验证Docker版本：**19.03.9**
- 安装成功

### 阶段7：检查MySQL容器

```
Check that Mysql is installed.....
Error: No such object: mysql
```

**说明**：
- 检查是否存在名为`mysql`的容器
- 不存在，继续安装

### 阶段8：加载MySQL镜像

```
Start install Mysql ......
c233345f327a: Loading layer    145MB/145MB
9117b1e53ba3: Loading layer  11.26kB/11.26kB
...
Loaded image: mysql:5.7
```

**说明**：
- 从Docker镜像文件加载MySQL 5.7镜像
- 镜像加载成功（612ce4c0de69...）

### 阶段9：启动MySQL容器（失败）

```
612ce4c0de6934b739021a2b6cc0ae0f4dfd9b8d1e03bc49d47b45709193c79a
docker: Error response from daemon: cgroups: cgroup mountpoint does not exist: unknown.
Run the Mysql image failed!
```

**关键错误**：
- 容器ID：`612ce4c0de69...`
- 错误：`cgroups: cgroup mountpoint does not exist: unknown`
- 启动失败

## 失败原因分析

### 根本原因

**Docker 19.03.9 不支持 cgroup v2**

1. **系统环境**：
   - CentOS Stream 10
   - 内核：6.12.0-150.el10.x86_64
   - **默认使用 cgroup v2**

2. **Docker版本**：
   - Docker 19.03.9（脚本自带）
   - **只支持 cgroup v1**
   - 不支持 cgroup v2

3. **冲突**：
   ```
   Docker 19.03.9 尝试访问 cgroup v1 路径
       ↓
   /sys/fs/cgroup/memory/  (v1路径)
       ↓
   CentOS 10 只有 /sys/fs/cgroup/  (v2统一路径)
       ↓
   路径不存在 → 错误！
   ```

### 错误流程

```
1. 脚本检测docker命令不存在
   ↓
2. 安装自带的Docker 19.03.9
   ↓
3. Docker服务启动成功
   ↓
4. 加载MySQL镜像成功
   ↓
5. 尝试启动MySQL容器
   ↓
6. Docker尝试创建cgroup
   ↓
7. 访问 /sys/fs/cgroup/memory/ (v1路径)
   ↓
8. 路径不存在（系统使用v2）
   ↓
9. 错误：cgroup mountpoint does not exist
   ↓
10. 容器启动失败
```

## 解决方案

### 方案1：使用Podman（推荐）

**步骤**：
1. 停止Docker服务
2. 删除Docker 19.03.9
3. 使用Podman启动容器

**命令**：
```bash
# 停止Docker
systemctl stop docker
systemctl disable docker

# 删除Docker二进制文件
rm -f /usr/bin/docker /usr/bin/dockerd /usr/bin/containerd

# 使用Podman启动MySQL
podman run -d --name mysql -p 3307:3306 -p 33060:33060 \
  -e MYSQL_ROOT_PASSWORD=root123 mysql:5.7
```

### 方案2：启用Podman socket

**步骤**：
1. 启用Podman socket服务
2. 设置DOCKER_HOST环境变量
3. 重新运行安装脚本

**命令**：
```bash
# 启用Podman socket
systemctl enable --now podman.socket

# 设置环境变量
export DOCKER_HOST=unix:///run/podman/podman.sock

# 重新运行安装脚本
sudo bash ./Klsec-yg-146-251024-01
```

### 方案3：修改安装脚本

**步骤**：
1. 解压安装脚本
2. 修改install.sh中的docker命令为podman
3. 重新打包或直接执行修改后的脚本

## 总结

### 安装流程总结

1. ✅ **脚本解压**：成功
2. ✅ **环境初始化**：成功
3. ✅ **文件部署**：成功
4. ✅ **Docker安装**：成功（但版本过旧）
5. ✅ **镜像加载**：成功
6. ❌ **容器启动**：失败（cgroup v2不兼容）

### 关键问题

- **Docker版本过旧**：19.03.9不支持cgroup v2
- **系统版本过新**：CentOS 10默认使用cgroup v2
- **版本不匹配**：导致容器无法启动

### 建议

**最佳方案**：使用Podman替代Docker
- Podman原生支持cgroup v2
- 命令兼容Docker
- 无需修改系统配置
- 更安全（无daemon）

