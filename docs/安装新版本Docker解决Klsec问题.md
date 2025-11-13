# 安装新版本Docker解决Klsec问题

## 问题分析

### 当前情况

1. **Klsec安装脚本的行为**：
   - 检查`docker -v`命令是否存在
   - 如果不存在，安装自带的Docker 19.03.9
   - 如果存在，跳过安装步骤，使用现有的Docker

2. **失败原因**：
   - Docker 19.03.9不支持cgroup v2
   - CentOS 10使用cgroup v2
   - 容器无法启动

### 解决方案

**如果在运行Klsec安装脚本之前，先安装新版本Docker（20.10+）：**

1. ✅ Klsec脚本检测到docker已存在
2. ✅ 跳过安装自带的Docker 19.03.9
3. ✅ 使用已安装的新版本Docker（支持cgroup v2）
4. ✅ 容器可以正常启动

## 安装步骤（SSH命令）

### 步骤1：清理旧版本Docker

```bash
# 停止Docker服务
systemctl stop docker
systemctl disable docker

# 删除Docker 19.03.9的二进制文件
rm -f /usr/bin/docker /usr/bin/dockerd /usr/bin/containerd \
     /usr/bin/containerd-shim /usr/bin/docker-init \
     /usr/bin/docker-proxy /usr/bin/runc /usr/bin/ctr

# 验证已删除
ls -la /usr/bin/docker* /usr/bin/containerd* 2>/dev/null || echo "已清理"
```

### 步骤2：安装yum-utils

```bash
yum install -y yum-utils
```

### 步骤3：添加Docker仓库（清华镜像）

```bash
cat > /tmp/docker-ce.repo << 'EOF'
[docker-ce]
name=Docker CE
baseurl=https://mirrors.tuna.tsinghua.edu.cn/docker-ce/linux/centos/$releasever/$basearch/stable
enabled=1
gpgcheck=1
gpgkey=https://mirrors.tuna.tsinghua.edu.cn/docker-ce/linux/centos/gpg
EOF

cp /tmp/docker-ce.repo /etc/yum.repos.d/
```

### 步骤4：安装Docker

```bash
# 清理缓存
yum clean all

# 安装Docker CE（支持cgroup v2）
yum install -y docker-ce docker-ce-cli containerd.io
```

### 步骤5：配置Docker

```bash
# 创建配置目录
mkdir -p /etc/docker

# 配置Docker镜像源和存储路径
cat > /etc/docker/daemon.json << 'EOF'
{
  "registry-mirrors": [
    "https://mirror.ccs.tencentyun.com",
    "https://docker.mirrors.ustc.edu.cn",
    "https://registry.docker-cn.com"
  ],
  "data-root": "/data/docker",
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "500m",
    "max-file": "3"
  }
}
EOF
```

### 步骤6：启动Docker服务

```bash
# 启动Docker服务
systemctl start docker

# 设置开机自启
systemctl enable docker

# 验证Docker版本
docker --version

# 验证cgroup支持
docker info | grep -i cgroup
```

### 步骤7：验证安装

```bash
# 测试Docker是否正常工作
docker run --rm hello-world

# 检查cgroup版本支持
docker info | grep "Cgroup Version"
```

### 步骤8：重新运行Klsec安装脚本

```bash
cd /home/test/桌面
sudo ./Klsec-yg-146-251024-01
```

## 预期结果

1. ✅ Klsec脚本检测到docker已存在
2. ✅ 跳过"Start install docker"步骤
3. ✅ 直接使用已安装的新版本Docker
4. ✅ MySQL容器可以正常启动（不再出现cgroup错误）

## 一键执行版本

```bash
# 清理旧Docker
systemctl stop docker; systemctl disable docker
rm -f /usr/bin/docker /usr/bin/dockerd /usr/bin/containerd /usr/bin/containerd-shim /usr/bin/docker-init /usr/bin/docker-proxy /usr/bin/runc /usr/bin/ctr

# 安装yum-utils
yum install -y yum-utils

# 添加Docker仓库
cat > /tmp/docker-ce.repo << 'EOF'
[docker-ce]
name=Docker CE
baseurl=https://mirrors.tuna.tsinghua.edu.cn/docker-ce/linux/centos/$releasever/$basearch/stable
enabled=1
gpgcheck=1
gpgkey=https://mirrors.tuna.tsinghua.edu.cn/docker-ce/linux/centos/gpg
EOF
cp /tmp/docker-ce.repo /etc/yum.repos.d/

# 安装Docker
yum clean all
yum install -y docker-ce docker-ce-cli containerd.io

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

## 总结

**您的想法完全正确！**

如果在运行Klsec安装脚本之前先安装新版本Docker：
- ✅ 可以避免安装旧版本Docker 19.03.9
- ✅ 使用支持cgroup v2的新版本Docker
- ✅ Klsec安装应该可以正常完成

这是最简单、最直接的解决方案！

