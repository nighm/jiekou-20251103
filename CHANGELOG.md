## [7.0.0] - 2025-11-07

### 新增
- 引入 `pyproject.toml` 完整优化：动态版本管理（`setuptools_scm`）、多分组依赖（test/lint/docs/ci/security/dev）、集中工具配置（ruff/isort/bandit/pytest/coverage/tox/pip-tools）。
- 增加 `tools/upgrade_all_packages.py`，支持一键升级当前 Python 环境中的所有第三方包。
- 新建变更日志，统一记录版本演进；README 只保留关键信息。

### 修改
- 入口包 `__init__.py` 兼容 `_version.py` 回退逻辑，确保在源码树或 fallback 环境中都能获取版本号。
- `.gitignore` 忽略动态生成的 `_version.py`。
- README/ docs README 更新安装指引、依赖分组、运维与安全建议。

### 注意
- 若需要正式发布，请创建 Git 标签 `v7.0.0` 并推送到仓库（`git tag -a v7.0.0 -m "Release 7.0.0" && git push origin v7.0.0`）。
- 推荐在独立虚拟环境中运行 `python tools/upgrade_all_packages.py --dry-run` 预览升级清单，再执行正式升级。

