# SSH连接修复说明

## 问题诊断结果

- ✅ 服务器在线（ping通）
- ✅ SSH端口22开放
- ❌ 但连接在握手阶段被强制关闭

这说明SSH服务在运行，但配置可能有问题，或者连接被某种策略阻止。

## 解决方案

### 方法1：在服务器上执行修复脚本（推荐）

如果您有物理访问或控制台访问服务器，可以：

1. **上传修复脚本到服务器**（如果有其他方式访问）
2. **在服务器上执行**：
   ```bash
   sudo bash fix_ssh_on_server.sh
   ```

### 方法2：手动修复（在服务器上执行）

```bash
# 1. 备份配置
sudo cp /etc/ssh/sshd_config /etc/ssh/sshd_config.backup

# 2. 编辑配置
sudo vi /etc/ssh/sshd_config

# 确保以下配置：
PermitRootLogin yes
PasswordAuthentication yes
PubkeyAuthentication yes
MaxStartups 10:30:100
MaxSessions 10
ClientAliveInterval 60
ClientAliveCountMax 3

# 3. 测试配置
sudo sshd -t

# 4. 重启SSH服务
sudo systemctl restart sshd

# 5. 检查状态
sudo systemctl status sshd
```

### 方法3：一键修复命令（在服务器上执行）

```bash
sudo bash << 'EOF'
cp /etc/ssh/sshd_config /etc/ssh/sshd_config.backup.$(date +%Y%m%d_%H%M%S)
sed -i 's/^#*PermitRootLogin.*/PermitRootLogin yes/' /etc/ssh/sshd_config
sed -i 's/^#*PasswordAuthentication.*/PasswordAuthentication yes/' /etc/ssh/sshd_config
sed -i 's/^#*PubkeyAuthentication.*/PubkeyAuthentication yes/' /etc/ssh/sshd_config
grep -q '^MaxStartups' /etc/ssh/sshd_config || echo 'MaxStartups 10:30:100' >> /etc/ssh/sshd_config
grep -q '^MaxSessions' /etc/ssh/sshd_config || echo 'MaxSessions 10' >> /etc/ssh/sshd_config
sshd -t && systemctl restart sshd && echo "SSH已修复并重启" || echo "配置错误"
EOF
```

## 如果无法访问服务器

如果无法通过SSH或物理方式访问服务器：

1. **检查是否有其他访问方式**
   - IPMI/iDRAC带外管理
   - VNC/远程桌面
   - 控制台访问

2. **检查服务器日志**
   - 如果有其他方式访问，查看 `/var/log/secure` 或 `journalctl -u sshd`

3. **联系服务器管理员**
   - 如果有其他管理员账户可以访问

## 修复后测试

修复后，在Windows PowerShell中测试：

```bash
ssh root@192.168.24.45
```

或使用详细模式：

```bash
ssh -vvv root@192.168.24.45
```

## 预防措施

修复后，建议：

1. **监控SSH服务**
   ```bash
   sudo systemctl enable sshd
   sudo systemctl status sshd
   ```

2. **查看SSH日志**
   ```bash
   sudo tail -f /var/log/secure
   ```

3. **设置合理的连接限制**
   - MaxStartups: 10:30:100（最多10个并发，30秒内最多30个，最多100个）
   - MaxSessions: 10（每个连接最多10个会话）

