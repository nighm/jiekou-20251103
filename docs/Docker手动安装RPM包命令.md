# Docker手动安装RPM包命令

## 说明

**`yum clean all` 不会影响手动安装RPM包**，因为：
- `yum clean all` 只清理 `/var/cache/yum/` 目录下的缓存文件
- 手动安装RPM包使用的是**本地文件**（如 `/tmp/*.rpm`），不依赖yum缓存
- 即使清理了缓存，您下载的RPM包文件仍然可以正常安装

## 前提条件

1. **RPM包已上传到服务器**（如果还没上传，见下方"上传RPM包"步骤）
2. 知道RPM包存放的位置（通常是 `/tmp/` 或 `/root/`）

## 手动安装步骤

### 步骤1：上传RPM包到服务器（如果还没上传）

**在Windows PowerShell中执行**：

```powershell
# 假设RPM包在本地 docker_rpms 目录
scp docker_rpms/*.rpm root@192.168.24.45:/tmp/
```

### 步骤2：SSH登录服务器

```bash
ssh root@192.168.24.45
# 密码: 1
```

### 步骤3：进入RPM包目录

```bash
cd /tmp
```

### 步骤4：查看RPM包

```bash
ls -lh *.rpm
```

应该看到类似这样的文件：
- `docker-ce-28.5.2-1.el10.x86_64.rpm`
- `docker-ce-cli-28.5.2-1.el10.x86_64.rpm`
- `containerd.io-1.7.28-2.el10.x86_64.rpm`

### 步骤5：手动安装RPM包

**方法1：使用 `rpm -ivh`（推荐，显示安装进度）**

```bash
rpm -ivh docker-ce-*.rpm docker-ce-cli-*.rpm containerd.io-*.rpm
```

**方法2：使用 `yum localinstall`（自动解决依赖）**

```bash
yum localinstall -y docker-ce-*.rpm docker-ce-cli-*.rpm containerd.io-*.rpm
```

**注意**：如果提示缺少依赖，`yum localinstall` 会自动从仓库下载依赖包。

### 步骤6：配置Docker

```bash
# 创建配置目录
mkdir -p /etc/docker

# 创建配置文件
cat > /etc/docker/daemon.json << 'EOF'
{
  "registry-mirrors": [
    "https://mirror.ccs.tencentyun.com",
    "https://docker.mirrors.ustc.edu.cn"
  ],
  "data-root": "/data/docker"
}
EOF
```

### 步骤7：启动Docker服务

```bash
# 重新加载systemd配置
systemctl daemon-reload

# 启动Docker服务
systemctl start docker

# 设置开机自启
systemctl enable docker

# 验证Docker版本
docker --version

# 验证Docker运行状态
systemctl status docker
```

### 步骤8：验证安装

```bash
# 检查Docker版本
docker --version

# 检查cgroup支持（应该显示 cgroup v2）
docker info | grep -i cgroup

# 测试运行容器
docker run --rm hello-world
```

## 一键安装命令（如果RPM包在 /tmp/ 目录）

```bash
cd /tmp && \
rpm -ivh docker-ce-*.rpm docker-ce-cli-*.rpm containerd.io-*.rpm && \
mkdir -p /etc/docker && \
cat > /etc/docker/daemon.json << 'EOF'
{
  "registry-mirrors": [
    "https://mirror.ccs.tencentyun.com",
    "https://docker.mirrors.ustc.edu.cn"
  ],
  "data-root": "/data/docker"
}
EOF
systemctl daemon-reload && \
systemctl start docker && \
systemctl enable docker && \
docker --version
```

## 常见问题

### Q1: 提示缺少依赖怎么办？

**A**: 使用 `yum localinstall` 而不是 `rpm -ivh`，它会自动从仓库下载依赖：

```bash
yum localinstall -y docker-ce-*.rpm docker-ce-cli-*.rpm containerd.io-*.rpm
```

### Q2: 安装后找不到 `dockerd` 命令？

**A**: 检查安装是否成功：

```bash
rpm -qa | grep docker
rpm -ql docker-ce | grep dockerd
```

如果包已安装但找不到命令，可能需要重新安装：

```bash
rpm -ivh --force docker-ce-*.rpm docker-ce-cli-*.rpm containerd.io-*.rpm
```

### Q3: 启动Docker失败？

**A**: 查看详细错误信息：

```bash
systemctl status docker -l
journalctl -xeu docker.service --no-pager -n 50
```

## 总结

- ✅ **`yum clean all` 不影响手动安装RPM包**
- ✅ **手动安装使用本地RPM文件，不依赖yum缓存**
- ✅ **如果RPM包已下载，直接使用 `rpm -ivh` 或 `yum localinstall` 安装即可**

