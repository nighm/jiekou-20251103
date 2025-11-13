# JMeter测试套件 v7.0.12

基于JMeter和nmon的性能测试数据收集与Excel报告生成工具。v7.0.12版本聚焦于批处理脚本与配置统一，强化日志落地与双远端同步策略。

## 🎯 核心功能

- **批量JMeter测试**：根据配置自动执行多轮测试，每轮生成独立JTL文件
- **同步nmon监控**：通过SSH连接服务器，与JMeter测试同步收集系统资源数据
- **自动文件管理**：智能归档旧文件，保持result目录整洁
- **强化Excel报告**：整合JMeter和nmon数据，生成专业级Excel报告，包含多种图表和数据分析
- **🆕 日志全量留存**：自动保存辅助端JMeter日志、stdout/stderr并拉取服务端关键日志，方便复现与排障
- **🆕 测试日报工具**：专业的测试日报生成工具，支持报告生成、问题分析、数据审核等功能

> 更早版本的改动说明已迁移至 `CHANGELOG.md`。

## 🏗️ 技术架构

- **架构模式**：领域驱动设计(DDD)四层架构
- **编程语言**：Python 3.12+
- **核心依赖**：JMeter、nmon、PyYAML、pandas、openpyxl、numpy、paramiko
- **数据来源**：JMeter测试数据 + nmon系统监控数据
- **最终输出**：Excel报告文件

## 📁 项目结构

```
jiekou-20250908/
├── src/jmeter_test_suite/          # 核心源代码
│   ├── domain/                     # 领域层
│   │   ├── entities/              # 实体类
│   │   └── services/               # 领域服务
│   ├── application/                # 应用层
│   │   └── services/               # 应用服务
│   ├── infrastructure/             # 基础设施层
│   │   ├── adapters/               # 适配器
│   │   └── config/                 # 配置管理
│   └── interfaces/                 # 接口层
│       └── cli/                    # 命令行接口
├── docs/                          # 文档
│   ├── README.md                  # 项目概览
│   ├── DEVELOPMENT_PROGRESS.md    # 开发进度
│   ├── requirements/               # 需求文档
│   ├── api-specs/                 # API规范
│   └── implementation/            # 实现文档
├── data/                          # 数据文件
│   ├── configs/                   # 配置文件
│   ├── test_plans/                # JMX测试计划
│   └── tools/                     # 工具文件
├── tests/                         # 测试文件
├── result/                        # 测试结果
├── pyproject.toml                 # 项目配置
└── README.md                      # 项目说明
```

## 🚀 超简单使用方法

### 一键运行 (推荐)

#### Windows用户
```bash
# 解压项目后，双击运行：
一键运行-单个接口.bat      # 双击即可

# 就这么简单！
```

#### Linux/macOS用户
```bash
# 解压项目后，执行：
bash 一键运行-单个接口.sh
# 或
chmod +x 一键运行-单个接口.sh
./一键运行-单个接口.sh
```

### 环境要求
- **操作系统**: Windows / Linux / macOS
- **Python**: 3.12+ (必须)
- **JMeter**: 5.0+ (必须)
  - Windows: 添加到PATH或设置`JMETER_HOME`环境变量
  - Linux/macOS: 添加到PATH或设置`JMETER_HOME`环境变量
- **SSH连接到nmon服务器**: (可选，用于系统资源监控)

### 日志采集说明
- 辅助端实时日志：`result/jmeter_latest.log`
- 辅助端归档：每轮生成 `result/<接口>_<线程>_<循环>_<时间>_jmeter.log`
- STDOUT/STDERR：分别写入 `result/<接口>_<线程>_<循环>_<时间>_stdout.log/_stderr.log`
- 服务端关键日志：命名为 `result/server_<原文件名>_<会话ID>_<时间>.log`
- 自定义规则：通过 `jmeter_config.yaml` 中 `log_capture`、`server_logs` 配置调整后缀与开关

### 命令行入口（推荐方式）
```bash
# 默认读取配置执行批量压测 + nmon（推荐入口）
jmeter-test-suite run

# 单轮测试（指定线程/循环）
jmeter-test-suite test 200 5

# 批量生成Excel报告（扫描result目录）
jmeter-test-suite report
```

> 如果未安装脚本入口，可使用 `python -m jmeter_test_suite run` 等等效命令。所有命令均依赖 `pyproject.toml` 中的 `dev` 依赖组，请先执行 `pip install -e .[dev]`。

### 详细步骤 (通常不需要)

#### Windows
```bash
# 1. 解压项目到目标目录
# 2. 双击 一键运行-单个接口.bat
# 3. 如需修改配置: 编辑 src/jmeter_test_suite/infrastructure/config/jmeter_config.yaml
# 4. 查看结果: result/目录中的Excel报告
```

#### Linux/macOS
```bash
# 1. 解压项目到目标目录
# 2. 执行: bash 一键运行-单个接口.sh
# 3. 如需修改配置: 编辑 src/jmeter_test_suite/infrastructure/config/jmeter_config.yaml
# 4. 查看结果: result/目录中的Excel报告
```

### 跨平台支持说明

项目已支持跨平台运行（Windows / Linux / macOS）：

- ✅ **核心功能**: 所有Python代码跨平台兼容
- ✅ **启动脚本**: Windows(.bat) 和 Linux/macOS(.sh) 版本都提供
- ✅ **配置管理**: 跨平台配置路径和命令检测
- ✅ **文件操作**: 使用Python标准库，自动适配平台差异

### 运行测试

#### 单元测试
```bash
# Windows
python -m pytest tests/unit/ -v

# Linux/macOS
python -m pytest tests/unit/ -v
```

#### 所有测试
```bash
# 安装依赖（首次）
pip install -e .[dev]

# 按需选择其它依赖组
# pip install -e .[test]      # 最小化测试环境
# pip install -e .[lint]      # 代码规范/静态检查
# pip install -e .[docs]      # 文档构建
# pip install -e .[ci]        # CI 自动化执行
# pip install -e .[security]  # 安全与合规扫描

# 运行所有单元测试
python -m pytest tests/unit/ -v
```

详细信息请参考 [跨平台兼容性文档](docs/CROSS_PLATFORM_ANALYSIS.md)

### 持续集成（CI）状态
- ✅ **阶段 0**：文档梳理与规范同步（已完成，详见 `docs/development/CI/CI/CD落地计划.md`）
- 🚧 **阶段 1**：Gitee Go 基础流水线搭建中（准备 `pip install -e .[dev]` → `pytest` → `ruff` → `ruff format --check` → `mypy`）
- 📌 流水线脚本完成后将在此处补充状态徽章和触发策略说明

### 依赖与安全管理

- **最低版本策略**：项目已对齐 Python 3.12 正式版本（2023-10-02 发布）[[python.org](https://www.python.org/downloads/)]，`pyproject.toml` 中所有依赖下限同步至 2025 年 11 月的最新稳定版，请确保使用 `pip install -e .[dev]` 安装时具备 Python 3.12 解释器。
- **PyPI 兼容性校验**：开发流程中将通过 `pip install -e .[dev]` + `pytest` 验证依赖在 Python 3.12 环境下的兼容性，如需进一步检查可使用 `pip index versions <package>` 手动确认。
- **锁定依赖**：使用 `pip-compile --extra dev --output-file requirements.lock pyproject.toml` 生成可复现的锁文件。
- **依赖审计**：执行 `pip-audit` 检测安全漏洞，推荐在 CI 中启用 `pip install -e .[security] && pip-audit`。
- **批量任务**：`tox -e py312` 运行指定 Python 版本测试，`tox -e lint` 执行 `ruff check`/`ruff format --check`/`mypy` 组合检查。
- **代码规范**：运行 `ruff check src tests`、`ruff format src tests`、`isort src tests` 保持格式一致。

## 📊 测试日报生成工具

### 快速开始

```bash
# 生成测试日报
python tools/generate_test_daily_report.py generate
```

### 功能说明

测试日报工具位于 `tools/generate_test_daily_report.py`，提供以下功能：

1. **生成测试日报**：生成完整的Excel报告，包含测试执行摘要、明细、问题分析等
2. **分析JTL文件**：分析JMeter测试结果，找出卡死位置
3. **分析nmon数据**：分析服务器硬件监控数据
4. **审核Excel报告**：专业审核报告质量
5. **检查服务器日志**：查询服务器错误日志

### 报告输出

- **Excel报告**：`reports/测试日报_心跳接口压测_YYYYMMDD_HHMMSS.xlsx`
- **数据压缩包**：`reports/心跳接口压测数据_YYYYMMDD.zip`

所有报告文件都会被Git跟踪，永久保存。

## 📊 项目状态

### 当前阶段：v7.0.12 基线发布
- ✅ 核心压测能力：批量 JMeter、同步 nmon、自动报告一键打通
- ✅ 跨平台支持：Windows/Linux/macOS 脚本与配置统一
- ✅ 依赖与安全：pyproject 多分组依赖、pip-tools/pip-audit 集成
- ✅ 自动化工具：tox、ruff、mypy、bandit、覆盖率统一在配置中心
- ✅ 文档精简：README 聚焦核心信息，历史变更迁移至 `CHANGELOG.md`

## 🚀 功能特性

### 批量测试执行
- **嵌套循环**：支持线程数和循环数的组合测试（如：5个线程值 × 3个循环值 = 15轮测试）
- **独立文件**：每轮测试生成独立的JTL和HTML文件，便于分析对比
- **纯JMeter测试**：test命令只执行JMeter测试，不包含nmon监控

### 自动文件管理
- **智能归档**：每次执行前自动将旧文件移动到`result/old/`目录
- **简洁命名**：文件名格式为`result_{线程数}threads_{循环数}loops_{时间戳}.jtl`
- **时间戳标识**：文件名包含执行时间，便于识别和管理

### 同步监控（run命令）
- **实时同步**：JMeter测试和nmon监控同时启动，确保数据一致性
- **动态时长**：nmon监控时长根据JMeter测试实际执行时间动态调整
- **精确文件匹配**：根据执行时间戳精确匹配nmon数据文件，避免文件混淆
- **SSH连接**：自动连接远程服务器执行nmon监控
- **统一会话**：每轮测试使用统一的会话ID，便于关联分析

## 🔗 相关链接

- [功能需求](docs/requirements/functional-requirements.md)
- [验收标准](docs/requirements/acceptance-criteria.md)
- [CLI命令规范](docs/api-specs/cli-commands.md)
- [开发进度](docs/DEVELOPMENT_PROGRESS.md)

## 📝 贡献指南

1. **代码规范**：遵循PEP 8，使用类型提示
2. **文档要求**：所有公共方法必须提供文档字符串
3. **测试要求**：新功能必须包含单元测试
4. **审查流程**：所有代码变更需要经过代码审查

## 📞 联系方式

- 项目负责人：nighm
- 邮箱：nighm@sina.com
- 手机：15290244446
- 项目仓库：https://gitee.com/nighm/jiekou-20251103

---

**最后更新**：2025-11-13  
**文档版本**：v7.0.12  
**项目版本**：v7.0.12（详细记录见 `CHANGELOG.md`）