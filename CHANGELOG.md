# 变更日志

本项目的所有重要变更都记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
并且遵循 [语义化版本控制](https://semver.org/lang/zh-CN/)。

## [Unreleased]

## [1.0.0] - 2025-06-20

### 新增
- 专为Cursor设计的人大金仓数据库MCP服务
- 多种安全模式支持（readonly、limited_write、full_access）
- Schema访问控制支持多种配置方式（*、auto、明确列表）
- 完整的数据库操作工具集：
  - `test_connection` - 数据库连接测试
  - `get_security_info` - 安全配置信息获取
  - `list_schemas` - 获取用户有权限访问的所有数据库模式
  - `list_tables` - 表列表查询
  - `describe_table` - 表结构详细信息
  - `generate_table_doc` - 表结构文档生成（支持Markdown、JSON、SQL格式）
  - `generate_database_overview` - 数据库概览文档生成
  - `execute_query` - SQL查询执行（受安全模式限制）
- 环境变量配置管理，支持Cursor MCP集成
- SQL语句安全验证和过滤
- 查询结果行数限制和日志记录
- 文档生成功能，支持保存为实际文件到用户工作目录
- 用户工作目录相对路径支持，适合多用户环境
- MIT许可证支持
- 完整的版权声明和项目治理文档
- 贡献指南和版本变更日志
- 完整的README文档和使用示例

### 特性
- 🔒 **安全第一**: 多级安全模式，默认只读保护
- 🎯 **Cursor优化**: 专为Cursor MCP协议设计
- 📊 **文档生成**: 自动生成多格式表结构文档
- 🔧 **灵活配置**: 支持环境变量和多种访问策略
- 🌐 **多用户友好**: 相对路径设计，适合团队协作

---

## 版本说明

### 语义化版本控制

- **主版本号**：当进行不兼容的API修改时
- **次版本号**：当以向后兼容的方式添加功能时  
- **修订号**：当进行向后兼容的问题修复时

### 变更类型

- **新增**：用于新功能
- **修复**：用于问题修复
- **改进**：用于现有功能的改进
- **移除**：用于已移除的功能
- **弃用**：用于即将移除的功能
- **安全**：用于安全相关的修复

[Unreleased]: https://github.com/Gcluowenqiang/Kingbase-mcp/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/Gcluowenqiang/Kingbase-mcp/releases/tag/v1.0.0 