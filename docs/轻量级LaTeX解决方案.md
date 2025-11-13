# 轻量级LaTeX解决方案

## 🎯 推荐方案：MiKTeX Basic（约138MB）

### 优点
- ✅ **体积小**：安装包只有138MB（vs TeX Live 4GB）
- ✅ **按需安装**：只安装需要的包，自动下载
- ✅ **中文支持好**：内置中文支持
- ✅ **安装简单**：Windows安装程序，一键安装

### 下载地址
- 官网：https://miktex.org/download
- 直接下载：https://miktex.org/download/ctan/systems/win32/miktex/setup/windows-x64/basic-miktex-2.9.7440-x64.exe

### 安装步骤
1. 下载 `basic-miktex-2.9.7440-x64.exe`（约138MB）
2. 运行安装程序
3. 安装完成后，重启命令行/PowerShell
4. 验证：`xelatex --version`

### 第一次使用
- 第一次编译时会自动下载需要的包（如xeCJK等）
- 可能需要几分钟下载
- 之后就不需要下载了

---

## 🚀 替代方案

### 方案1：在线编译（Overleaf）
- 网址：https://www.overleaf.com/
- 优点：无需安装，浏览器即可
- 缺点：需要网络，文件需要上传

### 方案2：使用已有的TeX文件
- 我们已经生成了 `temp\DP_文档计划模板.tex`
- 可以直接上传到Overleaf编译
- 或者等MiKTeX安装完成后再编译

---

## 📝 快速安装MiKTeX步骤

```bash
# 1. 下载（约138MB）
# 访问：https://miktex.org/download

# 2. 安装后验证
xelatex --version

# 3. 使用我们的脚本编译
python tools\md_to_pdf.py "docs\templates\DP_文档计划模板.md"
```

---

## 💡 建议

**最佳方案**：安装MiKTeX Basic（138MB）
- 体积小，够用
- 支持中文
- 自动管理包

**临时方案**：使用Overleaf在线编译
- 上传 `temp\DP_文档计划模板.tex`
- 即可编译生成PDF

