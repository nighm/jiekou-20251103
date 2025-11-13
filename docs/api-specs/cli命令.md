# CLI命令规范 v1.1

## 🎯 概述

JMeter和nmon性能测试数据收集与Excel报告生成工具v1.0的CLI命令规范，简单直接，只包含基础功能。

## 📋 命令概览

```bash
jmeter-test-suite <command> [options]
```

> `jmeter-test-suite` 来自 `pyproject.toml` 中的 `project.scripts` 配置，作用等同于执行 `python -m jmeter_test_suite.__main__`。

可用命令（与 `src/jmeter_test_suite/interfaces/cli/main.py` 保持一致）：
- `test`：执行单轮或批量 JMeter 测试
- `run`：批量执行 JMeter 测试并同步 nmon 监控（推荐默认入口）
- `report`：生成 Excel 报告（批量或指定目录）
- `all`：一键执行压测（run/distributed）并生成报告
- `distributed`：分布式压测（依赖配置文件启用）
- `config-info`：显示当前测试参数配置
- `mode-info`：显示单机/分布式模式信息
- `open-result`：跨平台打开结果目录
- `help`：打印帮助信息

## 🚀 核心命令

### 1. test - JMeter 测试执行（单轮 / 批量）

#### 命令语法
```bash
jmeter-test-suite test [threads loops]
```

#### 参数说明
| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| `threads` | int | 否 | - | 指定线程数，提供时须与 `loops` 搭配使用 |
| `loops` | int | 否 | - | 指定循环次数 |

参数使用规则：
- **不带参数**：从 `jmeter_config.yaml` 中读取 `test_plans`、`thread_range`、`loop_range`，执行批量测试。
- **带两个参数**：执行单轮测试，仅使用传入的线程/循环值；其他参数仍从配置读取。

#### 使用示例
```bash
# 使用配置默认值批量执行
jmeter-test-suite test

# 指定单轮测试
jmeter-test-suite test 200 5
```

#### 典型输出
- 日志中会打印 JMX 文件、线程/循环范围、执行进度与成功统计。
- 批量执行前会自动归档 `result/` 目录旧文件，仅保留最新结果。
- 返回码：成功返回 `0`，出现异常或部分失败返回 `1`。

### 2. run - 批量执行 JMeter + nmon（推荐）

#### 命令语法
```bash
jmeter-test-suite run [OPTIONS] [JMX_FILE]
```

#### 参数说明
| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| `JMX_FILE` | string | ❌ | 配置默认值 | JMX文件路径（可选，默认使用配置中的test_plans） |
| `--server` | string | ❌ | 配置默认值 | nmon服务器IP地址 |
| `--user` | string | ❌ | 配置默认值 | SSH用户名 |
| `--password` | string | ❌ | 配置默认值 | SSH密码 |
| `--output` | path | ❌ | ./result | 输出目录 |

执行流程：
1. 若未指定 `JMX_FILE`，自动取 `test_plans` 中第一个文件。
2. 调用 `test` 命令执行所有线程/循环组合。
3. 同步启动全局 nmon 监控，生成覆盖整个压测周期的单个 nmon 文件。
4. 输出批量执行摘要（JMeter、nmon 状态与总耗时）。

#### 使用示例
```bash
# 批量执行（使用配置默认值）
jmeter-test-suite run

# 指定JMX文件
jmeter-test-suite run test.jmx

# 指定服务器信息
jmeter-test-suite run test.jmx --server 192.168.24.45 --user root --password 1

# 指定输出目录
jmeter-test-suite run test.jmx --output ./my_result
```

#### 典型输出
- 终端输出包含 JMeter 结果、nmon 状态、总执行时长、同步状态。
- 成功返回 `0`，任何失败返回 `1`。

### 3. report - Excel 报告生成

#### 命令语法
```bash
jmeter-test-suite report [result_dir]
```

#### 参数说明
| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| `result_dir` | path | 否 | result | 结果目录路径；仅能传入 0 或 1 个参数 |

功能说明：
- 扫描指定目录（默认 `result/`），批量生成 Excel 报告。
- 报告输出路径由服务自动命名，无需手工指定。

#### 使用示例
```bash
# 批量生成Excel报告（默认目录）
jmeter-test-suite report

# 指定结果目录
jmeter-test-suite report D:\data\work\jiekou-20251103\result\20250912
```

#### 典型输出
- 控制台输出生成的 Excel 文件路径、处理耗时、是否包含图表等摘要。
- 成功返回 `0`，失败返回 `1`。

### 4. all - 一键执行压测 + 报告

#### 命令语法
```bash
jmeter-test-suite all
```

执行逻辑：
1. 根据 `distributed.enabled` 配置决定调用 `distributed` 或 `run`。
2. 压测完成后等待 5 秒，确保文件写入完毕。
3. 调用 `report` 命令生成 Excel 报告。
4. 全程设置 90 分钟超时保护（Unix 有效）。

#### 使用示例
```bash
jmeter-test-suite all
```

### 5. distributed - 分布式压测

仅当 `jmeter_config.yaml` 中 `distributed.enabled: true` 且配置了 `slaves` 时才可执行。

执行流程：
- 从配置读取 JMX、线程/循环范围、分布式目标机信息。
- 调用 `DistributedExecutionService` 完成压测，输出每个 slave 状态与汇总统计。

### 6. config-info - 配置信息

输出 `thread_range`、`loop_range`、默认 JMX，以及预估轮数与耗时，便于在流水线中快速确认配置。

### 7. mode-info - 模式信息

判断是否启用分布式模式，并列出所有 slave 信息，可作为 CI 前置检查。

### 8. open-result - 跨平台打开结果目录

语法：
```bash
jmeter-test-suite open-result [directory]
```

功能说明：
- Windows 使用 `explorer`，macOS 使用 `open`，Linux 依次尝试 `xdg-open` 等常见文件管理器。
- 如未指定目录，使用配置中的 `result_dir`。
- 找不到可用文件管理器时会提示手动打开。

### 9. help - 帮助信息

打印当前 CLI 可用命令、用途说明，与代码中 `print_help` 输出一致。

---

## 🔧 错误处理

`test`、`run`、`report`、`distributed`、`open-result` 等命令在执行失败时会打印明确的错误提示，并返回非零退出码。常见错误包含：
- 配置缺失（如 `test_plans` 未设置）
- JMX 文件或结果目录不存在
- SSH 连接失败/凭据错误
- nmon 执行异常
- Excel 生成失败（路径权限、磁盘空间）

CI 流水线中可根据退出码判断是否继续后续步骤。

## 📋 配置文件

### 配置文件格式 (jmeter_config.yaml)
```yaml
# JMeter配置
# jmeter_command配置说明：
# 1. 推荐方式：将JMeter添加到PATH，使用 "jmeter" (跨平台)
# 2. 环境变量方式：设置 JMETER_HOME 或 JMETER_PATH
# 3. 完整路径方式（仅当JMeter不在PATH中）：
#    Windows: "D:\\tools\\apache-jmeter-5.6.3\\bin\\jmeter.bat"
#    Linux: "/opt/apache-jmeter-5.6.3/bin/jmeter"
jmeter_command: "jmeter"  # 默认使用PATH中的jmeter命令（推荐）
result_dir: "./result"
test_plans_dir: "./src/jmeter_test_suite/infrastructure/config/test_plans"
thread_range: "7000 7000 1000"  # 当前默认：单一线程值
loop_range: "100 100 0"         # 当前默认：单一循环值
test_plans:
  - "09_device_heartbeat.jmx"

# nmon配置
nmon:
  server: "192.168.24.45"
  user: "test"
  password: "1"
  default_duration: 300
  nmon_package_path: "./data/tools/nmon16m_helpsystems.tar.gz"

# Excel报告配置
excel:
  output_dir: "./result"
  include_charts: true
  chart_types:
    - "line"
    - "bar"

# 系统配置
system:
  timeout:
    jmeter_execution: 1800  # 30分钟
    ssh_connection: 30      # 30秒
    excel_generation: 300   # 5分钟
```

---

**最后更新**：2025-11-10  
**文档版本**：v1.1（对齐 CLI 实际实现）
