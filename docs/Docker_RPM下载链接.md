# Docker RPM包直接下载链接

## 阿里云镜像站下载链接

### CentOS 8/Stream 10 x86_64架构

**仓库地址**：https://mirrors.aliyun.com/docker-ce/linux/centos/8/x86_64/stable/Packages/

### 最新版本RPM包（需要访问仓库页面查看最新版本号）

#### 方法1：访问仓库页面手动选择

访问：**https://mirrors.aliyun.com/docker-ce/linux/centos/8/x86_64/stable/Packages/**

查找以下文件（选择最新版本）：
- `docker-ce-*.x86_64.rpm` （Docker引擎）
- `docker-ce-cli-*.x86_64.rpm` （Docker命令行工具）
- `containerd.io-*.x86_64.rpm` （容器运行时）

#### 方法2：使用通用链接格式（需要替换版本号）

**Docker CE**：
```
https://mirrors.aliyun.com/docker-ce/linux/centos/8/x86_64/stable/Packages/docker-ce-24.0.7-1.el8.x86_64.rpm
```

**Docker CE CLI**：
```
https://mirrors.aliyun.com/docker-ce/linux/centos/8/x86_64/stable/Packages/docker-ce-cli-24.0.7-1.el8.x86_64.rpm
```

**Containerd.io**：
```
https://mirrors.aliyun.com/docker-ce/linux/centos/8/x86_64/stable/Packages/containerd.io-1.6.28-3.1.el8.x86_64.rpm
```

**注意**：版本号可能会更新，请访问仓库页面确认最新版本。

## 下载步骤

### 1. 访问仓库页面

打开浏览器访问：
```
https://mirrors.aliyun.com/docker-ce/linux/centos/8/x86_64/stable/Packages/
```

### 2. 查找最新版本

按时间排序，找到最新的：
- `docker-ce-` 开头的文件（选择最大的版本号）
- `docker-ce-cli-` 开头的文件（版本号与docker-ce匹配）
- `containerd.io-` 开头的文件

### 3. 下载RPM包

右键点击文件 → 另存为 → 保存到项目的 `docker_rpms/` 目录

### 4. 项目目录结构

```
jiekou-20251103/
├── docker_rpms/          # 创建这个目录
│   ├── docker-ce-24.0.7-1.el8.x86_64.rpm
│   ├── docker-ce-cli-24.0.7-1.el8.x86_64.rpm
│   └── containerd.io-1.6.28-3.1.el8.x86_64.rpm
```

## 上传到服务器

### 使用scp（Windows PowerShell）

```bash
# 创建docker_rpms目录（如果不存在）
mkdir docker_rpms

# 上传RPM包到服务器
scp docker_rpms/*.rpm root@192.168.24.45:/tmp/
```

### 使用sftp

```bash
sftp root@192.168.24.45
put docker_rpms/*.rpm /tmp/
exit
```

## 在服务器上安装

```bash
# 1. 进入RPM包目录
cd /tmp

# 2. 查看RPM包
ls -lh *.rpm

# 3. 安装（会自动解决依赖）
yum localinstall -y *.rpm

# 4. 配置Docker
mkdir -p /etc/docker
cat > /etc/docker/daemon.json << 'EOF'
{
  "registry-mirrors": [
    "https://mirror.ccs.tencentyun.com",
    "https://docker.mirrors.ustc.edu.cn"
  ],
  "data-root": "/data/docker"
}
EOF

# 5. 启动Docker
systemctl start docker
systemctl enable docker

# 6. 验证版本（应该是20.10+）
docker --version

# 7. 验证cgroup支持（应该显示v2）
docker info | grep -i cgroup
```

## 依赖包说明

安装时可能需要以下依赖包（yum会自动下载）：
- `container-selinux`
- `libcgroup`
- `libseccomp`
- `pigz`
- 等

如果离线安装，可能需要一起下载这些依赖包。

