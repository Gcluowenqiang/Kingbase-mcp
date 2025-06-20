# 贡献指南

感谢您考虑为人大金仓数据库MCP服务项目做出贡献！

## 🤝 如何贡献

### 1. 报告问题

如果您发现了bug或有功能建议，请：

1. 检查 [Issues](../../issues) 确保问题未被报告
2. 创建新的Issue，详细描述：
   - 问题的具体表现
   - 重现步骤
   - 预期行为
   - 实际行为
   - 环境信息（数据库版本、Python版本、Cursor版本）

### 2. 提交代码

1. **Fork项目**
   ```bash
   git clone https://github.com/Gcluowenqiang/Kingbase-mcp.git
   cd kingbase-mcp
   ```

2. **创建功能分支**
   ```bash
   git checkout -b feature/新功能名称
   # 或
   git checkout -b fix/修复问题名称
   ```

3. **编写代码**
   - 遵循现有的代码风格
   - 添加必要的注释
   - 确保代码通过测试

4. **提交更改**
   ```bash
   git commit -m "feat: 添加新功能描述"
   # 或
   git commit -m "fix: 修复问题描述"
   ```

5. **推送到远程仓库**
   ```bash
   git push origin feature/新功能名称
   ```

6. **创建Pull Request**
   - 清晰描述更改内容
   - 引用相关的Issue编号
   - 确保CI检查通过

## 📋 代码规范

### Python代码风格
- 遵循 [PEP 8](https://www.python.org/dev/peps/pep-0008/) 规范
- 使用有意义的变量和函数名
- 添加文档字符串和注释
- 最大行长度：88字符

### 提交信息格式
使用约定式提交格式：
```
type(scope): description

[optional body]

[optional footer]
```

类型：
- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `style`: 代码格式（不影响功能）
- `refactor`: 重构
- `test`: 添加测试
- `chore`: 构建过程或辅助工具的变动

示例：
```
feat(database): 添加对新数据类型的支持

增加对JSON和JSONB数据类型的解析和文档生成支持

Closes #123
```

## 🧪 测试

运行测试：
```bash
python -m pytest tests/
```

添加新功能时，请同时添加相应的测试用例。

## 📝 文档

- 更新相关的文档文件
- 确保README.md保持最新
- 在代码中添加必要的注释

## 🛡️ 许可证

通过贡献代码，您同意您的贡献将基于MIT许可证进行许可。

## 💬 讨论

如有疑问，可以通过以下方式联系：
- 创建Issue进行讨论
- 发送邮件至维护者

---

再次感谢您的贡献！🎉 