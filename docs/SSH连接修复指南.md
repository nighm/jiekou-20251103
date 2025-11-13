# SSH连接修复指南

## 当前问题

命令行 `ssh` 无法连接，错误信息：
- `kex_exchange_identification: read: Connection reset`
- `Connection closed by 192.168.24.45 port 22`

现在连Python脚本也无法连接，说明服务器SSH服务可能出现了问题。

## 诊断步骤

### 1. 检查服务器是否在线

```bash
# 在Windows PowerShell中
ping 192.168.24.45

# 或使用Python脚本诊断
python temp_diagnose_ssh_server.py
```

### 2. 检查SSH端口是否开放

```bash
# 在Windows PowerShell中
Test-NetConnection -ComputerName 192.168.24.45 -Port 22
```

### 3. 如果服务器在线但SSH不通

**需要在服务器上执行以下命令**（如果有物理访问或控制台访问）：

```bash
# 1. 检查SSH服务状态
sudo systemctl status sshd

# 2. 如果服务未运行，启动服务
sudo systemctl start sshd
sudo systemctl enable sshd

# 3. 检查SSH配置
sudo sshd -t

# 4. 查看SSH日志
sudo tail -f /var/log/secure
# 或
sudo journalctl -u sshd -f

# 5. 检查防火墙
sudo firewall-cmd --list-all
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --reload
```

## 修复SSH配置（在服务器上执行）

如果SSH服务运行但连接被拒绝，可能需要修复配置：

```bash
# 1. 备份配置
sudo cp /etc/ssh/sshd_config /etc/ssh/sshd_config.backup

# 2. 编辑配置
sudo vi /etc/ssh/sshd_config

# 3. 确保以下配置项正确：
# PermitRootLogin yes
# PasswordAuthentication yes
# PubkeyAuthentication yes
# MaxStartups 10:30:100
# MaxSessions 10

# 4. 测试配置
sudo sshd -t

# 5. 重启SSH服务
sudo systemctl restart sshd
```

## 快速修复脚本（在服务器上执行）

```bash
# 一键修复SSH配置
sudo bash << 'EOF'
# 备份配置
cp /etc/ssh/sshd_config /etc/ssh/sshd_config.backup.$(date +%Y%m%d_%H%M%S)

# 修改配置
sed -i 's/^#*PermitRootLogin.*/PermitRootLogin yes/' /etc/ssh/sshd_config
sed -i 's/^#*PasswordAuthentication.*/PasswordAuthentication yes/' /etc/ssh/sshd_config
sed -i 's/^#*PubkeyAuthentication.*/PubkeyAuthentication yes/' /etc/ssh/sshd_config

# 添加或修改连接限制
grep -q '^MaxStartups' /etc/ssh/sshd_config || echo 'MaxStartups 10:30:100' >> /etc/ssh/sshd_config
grep -q '^MaxSessions' /etc/ssh/sshd_config || echo 'MaxSessions 10' >> /etc/ssh/sshd_config

# 测试配置
sshd -t && systemctl restart sshd && echo "SSH配置已修复并重启" || echo "配置错误，请检查"
EOF
```

## 如果无法访问服务器

如果无法通过SSH或物理方式访问服务器，可能需要：

1. **检查网络设备**
   - 路由器/交换机配置
   - 网络连接状态

2. **检查服务器硬件**
   - 服务器是否开机
   - 是否有硬件故障

3. **使用其他访问方式**
   - 如果有IPMI/iDRAC等带外管理
   - 如果有VNC/远程桌面
   - 如果有控制台访问

## 测试连接

修复后，在Windows PowerShell中测试：

```bash
# 基本连接
ssh root@192.168.24.45

# 或使用详细模式查看问题
ssh -vvv root@192.168.24.45
```

## 预防措施

为了避免将来出现类似问题：

1. **定期检查SSH服务**
   ```bash
   sudo systemctl status sshd
   ```

2. **监控SSH日志**
   ```bash
   sudo tail -f /var/log/secure
   ```

3. **设置SSH服务自动重启**
   ```bash
   sudo systemctl enable sshd
   ```

4. **配置SSH连接限制**
   - 合理设置MaxStartups和MaxSessions
   - 使用fail2ban防止暴力破解

