# Pandoc安装和PATH配置指南

## ⚠️ 当前状态

检测到Pandoc未在系统PATH中，需要配置后才能使用。

## 🔧 解决方案

### 方案1：将Pandoc添加到PATH环境变量

#### Windows系统

1. **找到Pandoc安装位置**
   - 如果通过Chocolatey安装：通常在 `C:\ProgramData\chocolatey\bin\pandoc.exe`
   - 如果通过安装包安装：通常在 `C:\Users\<用户名>\AppData\Local\Pandoc\` 或 `C:\Program Files\Pandoc\`

2. **添加到PATH**
   - 右键"此电脑" → "属性" → "高级系统设置"
   - 点击"环境变量"
   - 在"系统变量"中找到"Path"，点击"编辑"
   - 点击"新建"，添加Pandoc的安装路径（例如：`C:\ProgramData\chocolatey\bin`）
   - 点击"确定"保存

3. **验证**
   - 打开新的命令行窗口（PowerShell或CMD）
   - 执行：`pandoc --version`
   - 如果显示版本信息，说明配置成功

### 方案2：使用完整路径

如果知道Pandoc的安装路径，可以直接使用完整路径：

```powershell
# 假设Pandoc安装在 C:\ProgramData\chocolatey\bin\pandoc.exe
& "C:\ProgramData\chocolatey\bin\pandoc.exe" "docs\templates\DP_文档计划模板.md" -o "docs\templates\DP_文档计划模板.docx" --reference-doc="templates\reference.docx" --toc --toc-depth=3 --number-sections
```

### 方案3：重新安装Pandoc（推荐）

如果找不到Pandoc的安装位置，建议重新安装：

#### 使用Chocolatey（推荐）

```powershell
# 以管理员身份运行PowerShell
choco install pandoc -y
```

#### 手动下载安装

1. 访问：https://pandoc.org/installing.html
2. 下载Windows安装包
3. 运行安装程序
4. 安装时选择"添加到PATH"

## 📋 转换文档计划模板

配置好Pandoc后，使用以下命令转换：

### 方法1：使用Python脚本（推荐）

```powershell
cd d:\data\jekou-20251105
python tools\convert_dp_template.py
```

### 方法2：使用批处理脚本

```powershell
cd d:\data\jekou-20251105
.\tools\convert_md_to_docx.bat "docs\templates\DP_文档计划模板.md" "docs\templates\DP_文档计划模板.docx"
```

### 方法3：直接使用Pandoc命令

```powershell
cd d:\data\jekou-20251105
pandoc "docs\templates\DP_文档计划模板.md" -o "docs\templates\DP_文档计划模板.docx" --reference-doc="templates\reference.docx" --toc --toc-depth=3 --number-sections
```

## ✅ 验证转换结果

转换成功后，请检查：

1. **文件是否生成**
   - 检查 `docs\templates\DP_文档计划模板.docx` 是否存在

2. **格式是否符合要求**
   - 打开生成的DOCX文件
   - 检查字体、字号、行距是否符合文档计划模板中的要求
   - 检查标题格式是否正确
   - 检查表格格式是否正确
   - 检查目录是否正确生成

3. **如果格式不符合要求**
   - 修改参考模板：`templates/reference.docx`
   - 重新运行转换脚本

## 🔍 查找Pandoc安装位置

如果不知道Pandoc安装在哪里，可以尝试以下方法：

### PowerShell命令

```powershell
# 方法1：搜索pandoc.exe
Get-ChildItem -Path C:\ -Filter pandoc.exe -Recurse -ErrorAction SilentlyContinue | Select-Object FullName

# 方法2：检查常见安装位置
$paths = @(
    "C:\ProgramData\chocolatey\bin\pandoc.exe",
    "$env:LOCALAPPDATA\Pandoc\pandoc.exe",
    "C:\Program Files\Pandoc\pandoc.exe",
    "C:\Program Files (x86)\Pandoc\pandoc.exe"
)

foreach ($path in $paths) {
    if (Test-Path $path) {
        Write-Host "找到Pandoc: $path"
    }
}
```

### CMD命令

```cmd
where pandoc
```

---

**创建日期**: 2025-11-05  
**版本**: v1.0

