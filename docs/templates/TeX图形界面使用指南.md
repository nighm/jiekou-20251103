# TeX Live图形界面使用指南

## 📝 重要说明

**TeX Live本身没有像WPS那样的图形界面**。TeX Live是一个命令行工具集，主要用于编译LaTeX文件。

但是，您可以使用以下图形界面工具来编辑和编译LaTeX文件：

---

## 🎨 推荐的图形界面工具

### 方案1：TeXworks（TeX Live自带，推荐）

**TeXworks是TeX Live自带的图形界面编辑器**

#### 查找TeXworks位置

TeXworks可能安装在以下位置：
- `C:\texlive\2025\bin\win32\texworks.exe`
- `C:\texlive\2025\tlpkg\tlperl\bin\texworks.exe`
- 或者需要单独安装

#### 安装TeXworks（如果未找到）

1. 访问：https://github.com/TeXworks/texworks/releases
2. 下载Windows版本
3. 安装后即可使用

#### 使用TeXworks

1. **打开TeXworks**
2. **打开TeX文件**：文件 → 打开 → 选择 `docs\templates\DP_文档计划模板.tex`
3. **选择编译引擎**：顶部下拉菜单选择 `XeLaTeX`
4. **编译**：点击绿色播放按钮（或按F5）
5. **查看PDF**：右侧自动显示PDF预览

---

### 方案2：TeXstudio（功能更强大，推荐）

**TeXstudio是功能最强大的LaTeX编辑器**

#### 下载安装

1. 访问：https://www.texstudio.org/
2. 下载Windows版本
3. 安装（会自动检测TeX Live）

#### 使用TeXstudio

1. **打开TeXstudio**
2. **打开文件**：文件 → 打开 → 选择 `docs\templates\DP_文档计划模板.tex`
3. **编译**：点击 `构建并查看` 按钮（或按F5）
4. **自动检测**：TeXstudio会自动检测XeLaTeX引擎

**优点**：
- ✅ 语法高亮
- ✅ 自动补全
- ✅ 实时预览
- ✅ 错误提示
- ✅ 内置PDF查看器

---

### 方案3：VS Code + LaTeX插件（如果您用VS Code）

#### 安装插件

1. 打开VS Code
2. 安装插件：`LaTeX Workshop`
3. 配置：自动检测TeX Live

#### 使用

1. **打开TeX文件**：在VS Code中打开 `docs\templates\DP_文档计划模板.tex`
2. **编译**：按 `Ctrl+Alt+B` 或点击右上角 `Build LaTeX project`
3. **查看PDF**：按 `Ctrl+Alt+V` 或点击右上角 `View LaTeX PDF`

---

### 方案4：在线编辑器（无需安装）

**Overleaf** - 在线LaTeX编辑器
- 网址：https://www.overleaf.com/
- 优点：无需安装，浏览器即可使用
- 使用：上传TeX文件，在线编译

---

## 🔧 快速开始（推荐TeXstudio）

### 步骤1：安装TeXstudio

1. 访问：https://www.texstudio.org/
2. 下载：`texstudio-4.7.3-win-qt6.exe`（或最新版本）
3. 安装：运行安装程序，选择默认设置

### 步骤2：打开TeX文件

1. 启动TeXstudio
2. 文件 → 打开
3. 选择：`D:\data\work\jiekou-20251103\docs\templates\DP_文档计划模板.tex`

### 步骤3：编译

1. 点击顶部工具栏的 `构建并查看` 按钮（或按F5）
2. 等待编译完成
3. PDF会自动在右侧显示

### 步骤4：查看PDF

- PDF自动显示在右侧窗口
- 可以点击PDF中的位置跳转到对应TeX代码

---

## 📋 对比表

| 工具 | 优点 | 缺点 | 推荐度 |
|------|------|------|--------|
| **TeXworks** | 轻量、简单、TeX Live自带 | 功能较少 | ⭐⭐⭐ |
| **TeXstudio** | 功能强大、自动补全、错误提示 | 需要单独安装 | ⭐⭐⭐⭐⭐ |
| **VS Code** | 如果您已用VS Code | 需要配置插件 | ⭐⭐⭐⭐ |
| **Overleaf** | 无需安装、在线使用 | 需要网络 | ⭐⭐⭐ |

---

## 💡 我的建议

**最佳选择：TeXstudio**
- ✅ 功能最强大
- ✅ 最适合LaTeX编辑
- ✅ 自动检测TeX Live
- ✅ 像WPS一样易用

**快速开始**：
1. 下载安装TeXstudio（5分钟）
2. 打开TeX文件
3. 点击编译按钮
4. 完成！

---

## 🔍 查找TeXworks（如果已安装）

如果TeX Live已安装TeXworks，可以在以下位置查找：

```bash
# PowerShell命令查找
Get-ChildItem C:\texlive -Recurse -Filter "texworks.exe" -ErrorAction SilentlyContinue
```

或者检查开始菜单：
- 开始菜单 → 搜索 "TeXworks"

---

**总结**：TeX Live本身是命令行工具，但配合TeXstudio等图形界面编辑器，就能像WPS一样方便使用了！

