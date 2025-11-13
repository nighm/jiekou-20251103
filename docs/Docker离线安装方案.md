# Docker离线安装方案（RPM包方式）

## 方案说明

Docker可以通过RPM包离线安装，适合网络受限或需要预先准备的环境。

## Docker是什么？

Docker不是单个RPM文件，而是**多个RPM包的组合**：

1. **docker-ce** - Docker引擎主程序
2. **docker-ce-cli** - Docker命令行工具
3. **containerd.io** - 容器运行时

## 下载RPM包的方法

### 方法1：在服务器上使用yum downloadonly（推荐）

```bash
# 1. 安装yum-utils
yum install -y yum-utils

# 2. 添加Docker仓库
yum-config-manager --add-repo https://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo

# 3. 重建缓存
yum makecache

# 4. 下载RPM包（不安装）
mkdir -p ~/docker_rpms
yum download --downloaddir=~/docker_rpms docker-ce docker-ce-cli containerd.io

# 5. 查看下载的文件
ls -lh ~/docker_rpms/
```

### 方法2：手动从镜像站下载

访问：https://mirrors.aliyun.com/docker-ce/linux/centos/8/x86_64/stable/Packages/

查找最新版本的RPM包：
- `docker-ce-24.0.7-1.el8.x86_64.rpm`
- `docker-ce-cli-24.0.7-1.el8.x86_64.rpm`
- `containerd.io-1.6.28-3.1.el8.x86_64.rpm`

### 方法3：使用wget直接下载

```bash
# 创建下载目录
mkdir -p docker_rpms
cd docker_rpms

# 下载RPM包（需要知道具体版本号）
wget https://mirrors.aliyun.com/docker-ce/linux/centos/8/x86_64/stable/Packages/docker-ce-24.0.7-1.el8.x86_64.rpm
wget https://mirrors.aliyun.com/docker-ce/linux/centos/8/x86_64/stable/Packages/docker-ce-cli-24.0.7-1.el8.x86_64.rpm
wget https://mirrors.aliyun.com/docker-ce/linux/centos/8/x86_64/stable/Packages/containerd.io-1.6.28-3.1.el8.x86_64.rpm
```

## 上传RPM包到服务器

### 从Windows上传到服务器

```bash
# 使用scp命令（在Windows PowerShell中执行）
scp docker_rpms/*.rpm root@192.168.24.45:/tmp/

# 或者使用sftp
sftp root@192.168.24.45
put docker_rpms/*.rpm /tmp/
```

## 离线安装Docker

### 在服务器上执行

```bash
# 1. 进入RPM包目录
cd /tmp

# 2. 查看RPM包
ls -lh *.rpm

# 3. 安装RPM包（会自动解决依赖）
yum localinstall -y *.rpm

# 或者逐个安装
rpm -ivh docker-ce-*.rpm docker-ce-cli-*.rpm containerd.io-*.rpm
```

## 完整流程

### 步骤1：在服务器上下载RPM包

```bash
# 在服务器上执行
mkdir -p ~/docker_rpms
cd ~/docker_rpms

# 添加Docker仓库
yum install -y yum-utils
yum-config-manager --add-repo https://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo
yum makecache

# 下载RPM包
yum download --downloaddir=. docker-ce docker-ce-cli containerd.io

# 打包（可选）
tar czf docker_rpms.tar.gz *.rpm
```

### 步骤2：传输到Windows项目目录（可选）

```bash
# 从服务器下载到Windows
scp root@192.168.24.45:~/docker_rpms/*.rpm ./docker_rpms/
```

### 步骤3：在服务器上安装

```bash
# 如果RPM包在服务器上，直接安装
cd ~/docker_rpms
yum localinstall -y *.rpm

# 配置Docker
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

# 启动Docker
systemctl start docker
systemctl enable docker

# 验证
docker --version
docker info | grep -i cgroup
```

## 项目目录结构

```
jiekou-20251103/
├── docker_rpms/          # Docker RPM包目录
│   ├── docker-ce-*.rpm
│   ├── docker-ce-cli-*.rpm
│   └── containerd.io-*.rpm
├── tools/
│   └── download_docker_rpms.sh  # 下载脚本
└── docs/
    └── Docker离线安装方案.md
```

## 优势

1. ✅ **离线安装**：不需要实时网络连接
2. ✅ **版本可控**：可以指定具体版本
3. ✅ **可重复**：RPM包可以重复使用
4. ✅ **快速部署**：避免每次下载

## 注意事项

1. **依赖关系**：RPM包可能有依赖，需要一起下载
2. **版本匹配**：确保RPM包版本与CentOS版本匹配
3. **架构匹配**：确保是x86_64架构的RPM包

