# Git 凭据配置说明

## 📚 什么是 Git 凭据管理器？

**Git 凭据管理器**是 Git 的一个内置功能，用于**自动保存和提供**你的 Git 用户名和密码/Token，避免每次推送都手动输入。

### 为什么需要它？

当我们移除了配置文件中的硬编码 Token 后，Git 需要一个安全的方式来获取认证信息。Git 凭据管理器就是为此而生的。

## 🎯 脚本的自动处理

**好消息：脚本已经自动处理了！** 在新设备上使用时：

1. ✅ **自动配置远程仓库**：脚本会从配置文件中读取 URL，自动配置 `origin` 和 `github` 远程
2. ✅ **自动启用凭据存储**：首次运行时自动启用 Git 凭据管理器
3. ✅ **智能提示**：如果认证失败，会显示详细的配置指南

## 🚀 在新设备上使用（零配置）

### 方法1：使用 HTTPS（最简单）

**只需要一次设置：**

```bash
# 1. 直接运行脚本
python3 tools/git_flow_helper.py

# 2. 首次推送时会提示输入：
#    Username: 你的用户名
#    Password: 你的个人访问令牌（不是登录密码！）
#    
#    输入后会自动保存，以后再也不需要输入了
```

**获取 Token：**
- **Gitee**: 设置 → 安全设置 → 私人令牌 → 生成新令牌
- **GitHub**: Settings → Developer settings → Personal access tokens → Generate new token

### 方法2：使用 SSH（推荐，一劳永逸）

**只需要一次设置（每台设备）：**

```bash
# 1. 生成SSH密钥（如果还没有）
ssh-keygen -t ed25519 -C "your_email@example.com"
# 按回车使用默认路径，可以设置密码或留空

# 2. 查看公钥
cat ~/.ssh/id_ed25519.pub

# 3. 将公钥添加到Gitee/GitHub
#    Gitee: 设置 → SSH公钥 → 添加公钥
#    GitHub: Settings → SSH and GPG keys → New SSH key

# 4. 修改远程URL为SSH（脚本会自动读取配置，你也可以手动修改）
git remote set-url origin git@gitee.com:nighm/jiekou-20251103.git
git remote set-url github git@github.com:nighm/jiekou-20251103.git
```

**完成后，以后使用脚本推送就再也不需要输入任何密码了！**

## ❓ 常见问题

### Q1: Git 凭据存储在哪里？

- **Linux/macOS**: `~/.git-credentials`
- **Windows**: `%USERPROFILE%\.git-credentials`

这是 Git 的标准功能，安全可靠。

### Q2: 我担心安全性？

**HTTPS 方式**：
- 凭据存储在本地加密文件
- 只有你可以访问
- Git 官方推荐的方式

**SSH 方式**：
- 更安全（使用密钥对认证）
- 无需存储密码
- 企业环境常用

### Q3: 多台设备怎么处理？

**每台设备只需要设置一次：**
- 如果使用 HTTPS：每台设备首次推送时输入一次 Token
- 如果使用 SSH：每台设备生成一次 SSH 密钥并添加到 Gitee/GitHub

**之后都是自动的！**

### Q4: Token 过期了怎么办？

**HTTPS 方式**：
1. 生成新的 Token
2. 删除旧的凭据：编辑 `~/.git-credentials`，删除旧的那行
3. 下次推送时输入新的 Token

**SSH 方式**：
- 不受影响，密钥不会过期

### Q5: 脚本会自动配置吗？

**是的！** 脚本会自动：
- ✅ 检测远程是否存在，不存在则自动添加
- ✅ 检测是否配置了凭据管理器，未配置则自动启用
- ✅ 认证失败时显示详细的配置指南

**你只需要：**
- 首次推送时输入用户名和 Token（HTTPS方式）
- 或者配置SSH密钥（推荐，一劳永逸）

## 📝 总结

**脚本的设计理念：**
- ✅ 移除硬编码 Token（安全）
- ✅ 自动配置远程仓库（方便）
- ✅ 自动启用凭据管理（智能）
- ✅ 认证失败时给出清晰提示（友好）

**在新设备上：**
1. 克隆仓库
2. 直接运行脚本
3. 首次推送时输入 Token（或配置SSH）
4. 以后就完全自动化了！

**完全不需要手动配置 Git 远程仓库！**

