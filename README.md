# 人大金仓数据库 MCP 服务

这是一个专为 Cursor 设计的人大金仓数据库 MCP (Model Context Protocol) 服务，提供表结构查询、文档生成和数据查询功能。

## 功能特性

- **Cursor 专用集成**: 专为 Cursor MCP 协议设计的数据库服务
- **多种安全模式**: 支持只读、限制写入、完全访问三种安全级别
- **表结构查询**: 获取数据库表的详细结构信息
- **文档生成**: 生成 Markdown、JSON、SQL 格式的表结构文档
- **数据库概览**: 生成整个数据库的概览文档
- **SQL 查询执行**: 根据安全模式执行不同级别的 SQL 操作

## 安全模式

### 1. 只读模式 (readonly) - 默认模式
- 仅允许 SELECT、SHOW、DESCRIBE、EXPLAIN 等查询操作
- 禁止所有写入和危险操作
- 适用于数据分析和报表查询

### 2. 限制写入模式 (limited_write)
- 允许 SELECT、INSERT、UPDATE 操作
- 禁止 DELETE、DROP、CREATE、ALTER 等危险操作
- 适用于需要数据录入但要保护结构的场景

### 3. 完全访问模式 (full_access)
- 允许所有 SQL 操作
- 谨慎使用，仅在完全信任的环境中启用
- 适用于数据库管理和维护

## 安装和配置

### 1. 安装依赖

```bash
cd kingbase-mcp
pip install -r requirements.txt
```

### 2. 在 Cursor 中配置

在 Cursor 的设置中找到 MCP 配置，添加以下内容：

```json
{
  "mcpServers": {
    "kingbase-mcp": {
      "command": "python",
      "args": ["F:/student/kingbase-mcp/main.py"],
      "env": {
        "KINGBASE_HOST": "IP地址",
        "KINGBASE_PORT": "端口",
        "KINGBASE_USERNAME": "用户名",
        "KINGBASE_PASSWORD": "密码",
        "KINGBASE_DATABASE": "数据库名称",
        "KINGBASE_SECURITY_MODE": "安全模式",
        "KINGBASE_ALLOWED_SCHEMAS": "允许访问的模式列表",
        "KINGBASE_ENABLE_QUERY_LOG": "是否启用查询日志"
      }
    }
  }
}
```

### 3. 环境变量说明

**必需环境变量：**
- `KINGBASE_HOST`: 数据库主机地址
- `KINGBASE_PORT`: 数据库端口
- `KINGBASE_USERNAME`: 数据库用户名
- `KINGBASE_PASSWORD`: 数据库密码
- `KINGBASE_DATABASE`: 数据库名称

**可选环境变量：**
- `KINGBASE_SECURITY_MODE`: 安全模式 (readonly/limited_write/full_access，默认：readonly)
- `KINGBASE_ALLOWED_SCHEMAS`: 允许访问的模式列表，支持三种配置方式：
  - `"*"`: 允许访问所有有权限的模式（推荐）
  - `"auto"`: 自动发现有权限的模式  
  - `"public,HR_BASE,SS"`: 明确指定模式列表（逗号分隔）
- `KINGBASE_CONNECT_TIMEOUT`: 连接超时时间（秒，默认：30）
- `KINGBASE_QUERY_TIMEOUT`: 查询超时时间（秒，默认：60）
- `KINGBASE_MAX_RETRIES`: 最大重试次数（默认：3）
- `KINGBASE_ENABLE_QUERY_LOG`: 是否启用查询日志（true/false，默认：false）
- `KINGBASE_MAX_RESULT_ROWS`: 最大返回行数（默认：1000）

## 可用工具

1. **test_connection**: 测试数据库连接
2. **get_security_info**: 获取当前安全配置信息
3. **list_schemas**: 获取用户有权限访问的所有数据库模式
4. **list_tables**: 列出指定模式中的所有表
5. **describe_table**: 获取表的详细结构信息
6. **generate_table_doc**: 生成表结构文档并保存到当前工作目录的docs文件夹
7. **generate_database_overview**: 生成数据库概览文档并保存到当前工作目录的docs文件夹
8. **execute_query**: 执行 SQL 语句（受安全模式限制）

## 使用示例

### 获取安全信息
在 Cursor 中输入：
```
@kingbase-mcp 获取当前安全配置信息
```

### 查看可访问的模式
```
@kingbase-mcp 获取所有可访问的数据库模式
```

### 查询表列表
```
@kingbase-mcp 列出 HR_BASE 模式中的所有表
```

### 查看表结构
```
@kingbase-mcp 描述 employees 表的结构
```

### 执行查询（只读模式）
```
@kingbase-mcp 查询员工表前10条记录
```

### 执行插入（限制写入模式）
```
@kingbase-mcp 向员工表插入一条新记录
```

### 生成表文档
```
@kingbase-mcp 为T_SS_HRAREA表生成Markdown文档
```

### 生成数据库概览
```
@kingbase-mcp 生成SS模式的数据库概览文档
```

## 文档生成说明

文档生成功能会将生成的文档保存为实际文件：

- **保存位置**: 当前工作目录下的 `docs/` 文件夹
- **文件命名**: `{schema}_{table_name}_{timestamp}.{ext}` 格式
- **支持格式**: Markdown (.md)、JSON (.json)、SQL (.sql)
- **多用户友好**: 每个用户在自己的项目目录下都会生成独立的docs文件夹

**示例输出**:
```
✅ 文档生成成功!
📁 文件路径: /your/project/docs/SS_T_SS_HRAREA_20250620_142000.md
📂 工作目录: /your/project
📊 表名: SS.T_SS_HRAREA
📝 格式: markdown
⏰ 生成时间: 2025-06-20 14:20:00
```

## 不同环境配置示例

### 开发环境配置
```json
{
  "env": {
    "KINGBASE_HOST": "dev-db.company.com",
    "KINGBASE_SECURITY_MODE": "limited_write",
    "KINGBASE_ALLOWED_SCHEMAS": "*",
    "KINGBASE_ENABLE_QUERY_LOG": "true",
    "KINGBASE_MAX_RESULT_ROWS": "100"
  }
}
```

### 生产环境配置
```json
{
  "env": {
    "KINGBASE_HOST": "prod-db.company.com",
    "KINGBASE_SECURITY_MODE": "readonly",
    "KINGBASE_ALLOWED_SCHEMAS": "HR_BASE,SS,FA,PB,RP",
    "KINGBASE_ENABLE_QUERY_LOG": "false",
    "KINGBASE_MAX_RESULT_ROWS": "1000"
  }
}
```

### 管理环境配置
```json
{
  "env": {
    "KINGBASE_HOST": "admin-db.company.com",
    "KINGBASE_SECURITY_MODE": "full_access",
    "KINGBASE_ALLOWED_SCHEMAS": "*",
    "KINGBASE_ENABLE_QUERY_LOG": "true",
    "KINGBASE_MAX_RESULT_ROWS": "10000"
  }
}
```

## 错误处理

- **配置错误**: 检查 Cursor MCP 配置中的环境变量设置
- **连接失败**: 验证数据库连接参数和网络连通性
- **权限不足**: 检查数据库用户权限和安全模式设置
- **SQL 被拒绝**: 当前安全模式不允许执行该类型的 SQL 操作

## 安全注意事项

1. **生产环境**建议使用 `readonly` 模式
2. **敏感环境**中避免使用 `full_access` 模式
3. **密码安全**：避免在配置中使用弱密码
4. **网络安全**：确保数据库连接使用安全的网络通道
5. **权限最小化**：数据库用户只应获得必要的最小权限

## 开发和调试

启用查询日志：
```json
{
  "env": {
    "KINGBASE_ENABLE_QUERY_LOG": "true"
  }
}
```

调试配置问题：
1. 检查 Cursor 的 MCP 配置语法
2. 验证所有必需的环境变量都已设置
3. 确认数据库连接参数正确
4. 查看 Cursor 的开发者工具中的 MCP 日志

## 技术架构

### 核心模块
- `main.py`: MCP服务主程序
- `config.py`: 环境变量配置模块
- `database.py`: 数据库操作和安全控制模块
- `document_generator.py`: 文档生成模块

### 安全控制
- 多级安全模式验证
- SQL语句类型检查
- 模式访问权限控制
- 查询结果行数限制
- 连接超时和重试机制

## 许可证

本项目基于 [MIT 许可证](./LICENSE) 开源发布。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

- ✅ **自由使用**: 允许任何人免费使用、复制、修改本软件
- ✅ **商业友好**: 支持商业使用和分发
- ✅ **修改自由**: 可以修改源代码并发布衍生作品
- ✅ **最小限制**: 只需保留版权声明即可

详细条款请参阅 [LICENSE](./LICENSE) 文件。

## 贡献

欢迎贡献代码、报告问题或提出建议！请阅读 [贡献指南](./CONTRIBUTING.md) 了解详细信息。

---

**版本**: 1.0.0  
**更新时间**: 2025-06-20  
**设计目标**: 专为 Cursor MCP 集成优化，简化配置管理