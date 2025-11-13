# JMeter测试套件 v7.0.12

## 📋 项目概览

基于JMeter和nmon的性能测试数据收集与Excel报告生成工具。v7.0.12版本在批处理脚本、日志输出与配置加载方面进一步统一。

### 🎯 核心功能
- **批量JMeter测试**：根据配置自动执行多轮测试，每轮生成独立JTL文件
- **同步nmon监控**：通过SSH连接服务器，与JMeter测试同步收集系统资源数据
- **自动文件管理**：智能归档旧文件，保持result目录整洁
- **Excel报告生成**：整合JMeter和nmon数据，生成Excel报告

### 🏗️ 技术架构
- **架构模式**：领域驱动设计(DDD)四层架构
- **编程语言**：Python 3.12+
- **核心依赖**：JMeter、nmon、PyYAML、pytest、openpyxl
- **数据来源**：JMeter测试数据 + nmon系统监控数据
- **最终输出**：Excel报告文件

## 📚 文档结构

```
docs/
├── README.md                       # 项目概览（本文件）
├── DEVELOPMENT_PROGRESS.md         # 开发进度记录
├── requirements/                   # 需求文档
│   ├── functional-requirements.md  # 功能需求
│   ├── acceptance-criteria.md      # 验收标准
│   └── batch-script-requirements.md # 批处理脚本需求
├── api-specs/                     # API规范文档
│   └── cli-commands.md            # CLI命令规范
├── implementation/                # 实现文档
│   ├── development-plan.md        # 开发计划
│   ├── batch-script-design.md     # 批处理脚本设计
│   └── batch-script-development-plan.md # 批处理脚本开发计划
├── testing/                       # 测试文档
│   └── batch-script-test-plan.md  # 批处理脚本测试计划
└── diagrams/                      # 图表文件
    └── sample-test-data.xlsx      # 示例测试数据
```

## 🚀 快速开始

### 环境要求
- Python 3.12+
- JMeter 5.0+
- Git
- SSH客户端（用于连接服务器）
- nmon工具（在服务器上）

### 安装步骤
```bash
# 1. 克隆项目
git clone https://github.com/nighm/jiekou-20250908.git
cd jiekou-20250908

# 2. 安装依赖
pip install -e .[dev]

# 可选依赖组（按需安装）
# pip install -e .[test]
# pip install -e .[lint]
# pip install -e .[docs]
# pip install -e .[ci]
# pip install -e .[security]

# 可选依赖组（按需安装）
# pip install -e .[test]
# pip install -e .[lint]
# pip install -e .[docs]
# pip install -e .[ci]
# pip install -e .[security]

# 3. 配置环境
# 确保JMeter在系统PATH中
# 配置jmeter_config.yaml文件（服务器信息、路径等）

# 4. 批量执行JMeter和nmon（推荐方式）
jmeter-test-suite run

# 5. 单次测试（可选）
jmeter-test-suite test 200 5

# 6. 生成Excel报告（批量处理result目录）
jmeter-test-suite report

# 如果未安装脚本入口，也可使用 python -m 方式
# python -m jmeter_test_suite run
# python -m jmeter_test_suite test 200 5
# python -m jmeter_test_suite report
```

### 依赖与自动化建议

- 使用 `pip-compile --extra dev --output-file requirements.lock pyproject.toml` 生成锁定文件。
- 安全扫描：`pip install -e .[security] && pip-audit`。
- 使用 `tox -e py312` 执行全流程测试，`tox -e lint` 运行规范检查。

## 📊 项目状态

### 当前阶段：v7.0.12 基线发布
- ✅ 压测执行链路一体化（JMeter + nmon + 报告）
- ✅ 跨平台脚本与配置统一（Windows/Linux/macOS）
- ✅ 依赖、测试、安全工具集中在 `pyproject.toml`
- ✅ 历史版本详见 `CHANGELOG.md`
- ⏳ CI/CD 流程规划中（详见 `docs/development/CI/CD落地计划.md`）

## 🚀 功能特性

### 批量测试执行
- **智能配置**：根据`jmeter_config.yaml`中的`thread_range`和`loop_range`自动执行多轮测试
- **嵌套循环**：支持线程数和循环数的组合测试（如：5个线程值 × 3个循环值 = 15轮测试）
- **独立文件**：每轮测试生成独立的JTL和nmon文件，便于分析对比

### 自动文件管理
- **智能归档**：每次执行前自动将旧文件移动到`result/old/`目录
- **简洁命名**：文件名格式为`result_{线程数}threads_{循环数}loops_{时间戳}.jtl`
- **时间戳标识**：文件名包含执行时间，便于识别和管理

### 同步监控
- **实时同步**：JMeter测试和nmon监控同时启动，确保数据一致性
- **动态时长**：nmon监控时长根据JMeter测试实际执行时间动态调整
- **精确文件匹配**：根据执行时间戳精确匹配nmon数据文件，避免文件混淆
- **SSH连接**：自动连接远程服务器执行nmon监控
- **统一会话**：每轮测试使用统一的会话ID，便于关联分析

### 技术改进说明

#### v7.0.12 批处理与日志优化
- **配置统一**：所有命令行与批处理脚本统一读取 `jmeter_config.yaml`，移除历史 `config.yaml`
- **日志增强**：批处理脚本输出全量日志，并通过Python入口同步写入 `logs/` 目录
- **远端同步**：Git 自动化脚本支持 GitHub + Gitee 双远端推送
- **流程提示**：批处理脚本新增执行阶段提示，便于定位问题

#### 进度跟踪
- [x] 项目架构设计
- [x] 核心功能设计
- [x] CLI命令设计
- [x] 验收标准制定
- [x] 批量测试功能实现
- [x] 同步监控功能实现
- [x] 自动文件管理实现
- [x] 配置管理系统实现
- [x] 批处理与日志优化（v7.0.12）
- [ ] 单元测试编写
- [ ] 集成测试验证
- [ ] Excel报告生成功能

## 🔗 相关链接

### 核心功能文档
- [功能需求](requirements/functional-requirements.md)
- [验收标准](requirements/acceptance-criteria.md)
- [CLI命令规范](api-specs/cli-commands.md)

### 批处理脚本文档（一键运行-单个接口.bat）
- [批处理脚本需求](requirements/batch-script-requirements.md) - 功能需求文档
- [批处理脚本设计](implementation/batch-script-design.md) - 架构设计文档
- [批处理脚本开发计划](implementation/batch-script-development-plan.md) - 开发实施文档
- [批处理脚本测试计划](testing/batch-script-test-plan.md) - 测试验证文档

## 📝 贡献指南

1. **代码规范**：遵循PEP 8，使用类型提示
2. **文档要求**：所有公共方法必须提供文档字符串
3. **测试要求**：新功能必须包含单元测试
4. **审查流程**：所有代码变更需要经过代码审查

## 📞 联系方式

- 项目负责人：nighm
- 邮箱：nighm@sina.com
- 手机：15290244446
- 项目仓库：https://github.com/nighm/jiekou-20250908

---

**最后更新**：2025-11-13  
**文档版本**：v7.0.12  
**项目版本**：v7.0.12（详见 `CHANGELOG.md`）
