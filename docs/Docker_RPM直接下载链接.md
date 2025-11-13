# Docker RPM包直接下载链接 - CentOS Stream 10

## 仓库页面
**访问这个页面，按日期排序，下载最新的3个文件**：
https://mirrors.aliyun.com/docker-ce/linux/centos/8/x86_64/stable/Packages/

## 需要下载的3个RPM包

### 方法：访问仓库页面手动选择

1. **打开链接**：https://mirrors.aliyun.com/docker-ce/linux/centos/8/x86_64/stable/Packages/
2. **按日期排序**（点击Date列）
3. **下载以下3个文件**（选择最新版本）：

   - **docker-ce**：找 `docker-ce-` 开头的文件，选择版本号最大的（如27.x.x）
   - **docker-ce-cli**：找 `docker-ce-cli-` 开头的文件，版本号必须与docker-ce相同
   - **containerd.io**：找 `containerd.io-` 开头的文件，选择最新的（如1.6.32）

### 快速识别方法

在仓库页面中：
- 找到文件名包含 `docker-ce-27` 或 `docker-ce-26` 的文件（最新版本）
- 找到对应的 `docker-ce-cli-` 文件（版本号相同）
- 找到 `containerd.io-1.6.32` 或更新的版本

## 下载后

1. **保存到项目目录**：`docker_rpms/`
2. **上传到服务器**：
   ```bash
   scp docker_rpms/*.rpm root@192.168.24.45:/tmp/
   ```
3. **在服务器上安装**：
   ```bash
   cd /tmp
   yum localinstall -y *.rpm
   ```

