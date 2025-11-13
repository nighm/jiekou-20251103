# Docker RPM包下载链接 - CentOS Stream 10

## 重要说明

CentOS Stream 10可以使用CentOS 8的Docker仓库（兼容）。

## 直接下载链接（阿里云镜像）

### 仓库页面（推荐，可选择最新版本）

**访问这个页面选择最新版本**：
```
https://mirrors.aliyun.com/docker-ce/linux/centos/8/x86_64/stable/Packages/
```

### 最新版本RPM包链接（直接下载）

**访问仓库页面查看最新版本**：
https://mirrors.aliyun.com/docker-ce/linux/centos/8/x86_64/stable/Packages/

**下载这3个文件（选择最新版本，按日期排序找最新的）**：

#### 1. docker-ce（Docker引擎）- 选择版本号最大的
查找：`docker-ce-` 开头的文件，选择版本号最大的（如 27.x 或 26.x）

#### 2. docker-ce-cli（Docker命令行工具）- 版本号与docker-ce匹配
查找：`docker-ce-cli-` 开头的文件，版本号必须与docker-ce相同

#### 3. containerd.io（容器运行时）- 选择最新版本
查找：`containerd.io-` 开头的文件，选择最新的（如 1.6.32-3.1.el8.x86_64.rpm）

**示例（如果找不到最新版本，用这些）**：
```
https://mirrors.aliyun.com/docker-ce/linux/centos/8/x86_64/stable/Packages/docker-ce-27.3.1-1.el8.x86_64.rpm
https://mirrors.aliyun.com/docker-ce/linux/centos/8/x86_64/stable/Packages/docker-ce-cli-27.3.1-1.el8.x86_64.rpm
https://mirrors.aliyun.com/docker-ce/linux/centos/8/x86_64/stable/Packages/containerd.io-1.6.32-3.1.el8.x86_64.rpm
```

## 下载步骤

### 方法1：直接点击链接下载

1. 复制上面的3个链接
2. 在浏览器中打开
3. 右键 → 另存为
4. 保存到项目的 `docker_rpms/` 目录

### 方法2：访问仓库页面手动选择

1. 访问：https://mirrors.aliyun.com/docker-ce/linux/centos/8/x86_64/stable/Packages/
2. 按时间排序，找到最新的：
   - `docker-ce-24.0.7-1.el8.x86_64.rpm`（或更新的版本）
   - `docker-ce-cli-24.0.7-1.el8.x86_64.rpm`（版本号与docker-ce匹配）
   - `containerd.io-1.6.28-3.1.el8.x86_64.rpm`（或更新的版本）
3. 下载这3个文件

## 项目目录结构

```
jiekou-20251103/
├── docker_rpms/          # 创建这个目录存放RPM包
│   ├── docker-ce-24.0.7-1.el8.x86_64.rpm
│   ├── docker-ce-cli-24.0.7-1.el8.x86_64.rpm
│   └── containerd.io-1.6.28-3.1.el8.x86_64.rpm
```

## 上传到服务器

### 在Windows PowerShell中执行

```bash
# 创建docker_rpms目录（如果不存在）
mkdir docker_rpms

# 上传RPM包到服务器
scp docker_rpms/*.rpm root@192.168.24.45:/tmp/
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

# 6. 验证版本（应该是24.0+，支持cgroup v2）
docker --version

# 7. 验证cgroup支持
docker info | grep -i cgroup
```

## 注意事项

1. **版本号可能更新**：如果链接失效，访问仓库页面查找最新版本
2. **依赖包**：安装时yum会自动下载依赖包
3. **架构匹配**：确保下载的是x86_64架构的RPM包

## 备用镜像源

如果阿里云镜像不可用，可以使用：

**腾讯云镜像**：
```
https://mirrors.cloud.tencent.com/docker-ce/linux/centos/8/x86_64/stable/Packages/
```

**中科大镜像**：
```
https://mirrors.ustc.edu.cn/docker-ce/linux/centos/8/x86_64/stable/Packages/
```

