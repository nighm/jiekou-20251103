# Klsec服务端手动安装命令（使用Podman）

## 完整安装命令序列

### 步骤1：启用Podman socket服务

```bash
# 启用并启动Podman socket服务（提供Docker兼容的API）
sudo systemctl enable --now podman.socket

# 验证服务状态
sudo systemctl status podman.socket
```

### 步骤2：设置DOCKER_HOST环境变量

```bash
# 设置DOCKER_HOST指向Podman socket
export DOCKER_HOST=unix:///run/podman/podman.sock

# 验证设置（可选）
echo $DOCKER_HOST
```

### 步骤3：运行Klsec安装脚本

```bash
# 运行安装脚本（会自动使用Podman socket）
sudo bash /tmp/Klsec-yg-146-251024-01
```

**安装过程中的交互提示**：
- 如果提示选择序列号，输入：`1`
- 如果提示是否修改镜像存储目录，输入：`1`
- 如果提示y/n确认，输入：`y`

### 步骤4：验证安装结果

```bash
# 检查容器状态
podman ps -a

# 检查镜像
podman images

# 检查运行中的容器
podman ps

# 检查Klsec相关服务
systemctl list-units | grep -i klsec
```

---

## 一键执行版本（复制粘贴）

```bash
# 启用Podman socket
sudo systemctl enable --now podman.socket && \
# 设置环境变量并运行安装脚本
export DOCKER_HOST=unix:///run/podman/podman.sock && \
sudo -E bash /tmp/Klsec-yg-146-251024-01
```

**注意**：`sudo -E` 会保留环境变量，确保DOCKER_HOST生效。

---

## 如果遇到问题

### 问题1：Podman socket未启动

```bash
# 检查socket文件是否存在
ls -la /run/podman/podman.sock

# 如果不存在，手动启动
sudo systemctl start podman.socket
```

### 问题2：安装脚本仍然连接Docker daemon

```bash
# 确保Docker daemon已停止
sudo systemctl stop docker
sudo systemctl disable docker

# 验证docker命令指向podman
docker --version  # 应该显示podman版本
```

### 问题3：查看安装日志

```bash
# 如果安装失败，查看详细输出
# 安装脚本会输出详细的执行过程

# 检查Podman日志
journalctl -u podman -n 50
```

---

## 安装后检查清单

- [ ] Podman socket服务运行正常
- [ ] 所有容器已创建并运行
- [ ] MySQL容器运行正常（端口3307）
- [ ] Redis容器运行正常（端口6389）
- [ ] Mosquitto容器运行正常（端口1883）
- [ ] Nginx容器运行正常（端口80）
- [ ] Klsec服务已启动（如果有）

---

## 常用Podman命令

```bash
# 查看所有容器
podman ps -a

# 查看运行中的容器
podman ps

# 查看容器日志
podman logs <容器名或ID>

# 启动容器
podman start <容器名或ID>

# 停止容器
podman stop <容器名或ID>

# 重启容器
podman restart <容器名或ID>

# 删除容器
podman rm <容器名或ID>

# 查看镜像
podman images

# 删除镜像
podman rmi <镜像名或ID>
```

