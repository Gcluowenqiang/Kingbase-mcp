"""
数据库文档生成模块
生成表结构设计文档

Copyright (c) 2025 qyue
Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""
from typing import List, Dict, Any
from datetime import datetime
import json
from tabulate import tabulate
from jinja2 import Template


class DocumentGenerator:
    """文档生成器"""
    
    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def generate_table_structure_doc(self, table_name: str, structure: List[Dict[str, Any]], 
                                   indexes: List[Dict[str, Any]], 
                                   constraints: List[Dict[str, Any]]) -> str:
        """生成表结构文档"""
        
        # 基本信息
        doc = f"""# 表结构设计文档: {table_name}

**生成时间**: {self.timestamp}  
**数据库**: 人大金仓 (KingbaseES)  
**模式**: HR_BASE

---

## 表基本信息

**表名**: `{table_name}`  
**字段数量**: {len(structure)}  
**索引数量**: {len(indexes)}  
**约束数量**: {len(constraints)}

---

## 字段结构

"""
        
        # 字段信息表格
        if structure:
            headers = ['序号', '字段名', '数据类型', '长度', '精度', '标度', '可空', '默认值', '主键', '注释']
            rows = []
            
            for col in structure:
                row = [
                    col.get('ordinal_position', ''),
                    f"`{col.get('column_name', '')}`",
                    col.get('data_type', ''),
                    col.get('character_maximum_length', '') or '',
                    col.get('numeric_precision', '') or '',
                    col.get('numeric_scale', '') or '',
                    '是' if col.get('is_nullable') == 'YES' else '否',
                    col.get('column_default', '') or '',
                    '是' if col.get('is_primary_key') == 'YES' else '否',
                    col.get('column_comment', '') or ''
                ]
                rows.append(row)
            
            table_md = tabulate(rows, headers=headers, tablefmt='pipe')
            doc += table_md + "\n\n---\n\n"
        
        # 索引信息
        doc += "## 索引信息\n\n"
        if indexes:
            for idx in indexes:
                doc += f"### `{idx.get('indexname', '')}`\n\n"
                doc += f"**类型**: {'唯一索引' if idx.get('is_unique') == 'YES' else '普通索引'}\n\n"
                doc += f"**定义**: \n```sql\n{idx.get('indexdef', '')}\n```\n\n"
        else:
            doc += "暂无索引信息\n\n"
        
        doc += "---\n\n"
        
        # 约束信息
        doc += "## 约束信息\n\n"
        if constraints:
            constraint_types = {}
            for constraint in constraints:
                c_type = constraint.get('constraint_type', '')
                if c_type not in constraint_types:
                    constraint_types[c_type] = []
                constraint_types[c_type].append(constraint)
            
            for c_type, c_list in constraint_types.items():
                doc += f"### {self._get_constraint_type_name(c_type)}\n\n"
                for constraint in c_list:
                    doc += f"- **{constraint.get('constraint_name', '')}**: "
                    doc += f"字段 `{constraint.get('column_name', '')}`"
                    if constraint.get('foreign_key_references'):
                        doc += f" → 引用 `{constraint.get('foreign_key_references')}`"
                    doc += "\n"
                doc += "\n"
        else:
            doc += "暂无约束信息\n\n"
        
        doc += "---\n\n"
        doc += f"*文档生成时间: {self.timestamp}*\n"
        doc += "*由 Kingbase MCP 服务自动生成*\n"
        
        return doc
    
    def generate_database_overview_doc(self, tables: List[Dict[str, Any]]) -> str:
        """生成数据库概览文档"""
        
        doc = f"""# 数据库概览文档

**生成时间**: {self.timestamp}  
**数据库**: HR_BASE (人大金仓)  
**表数量**: {len(tables)}

---

## 数据库表清单

"""
        
        if tables:
            headers = ['序号', '表名', '所有者', '是否有索引', '是否有规则', '是否有触发器']
            rows = []
            
            for i, table in enumerate(tables, 1):
                row = [
                    i,
                    f"`{table.get('tablename', '')}`",
                    table.get('tableowner', ''),
                    '是' if table.get('hasindexes') else '否',
                    '是' if table.get('hasrules') else '否',
                    '是' if table.get('hastriggers') else '否'
                ]
                rows.append(row)
            
            table_md = tabulate(rows, headers=headers, tablefmt='pipe')
            doc += table_md + "\n\n---\n\n"
        
        # 统计信息
        doc += "## 统计信息\n\n"
        
        has_indexes = sum(1 for t in tables if t.get('hasindexes'))
        has_rules = sum(1 for t in tables if t.get('hasrules'))
        has_triggers = sum(1 for t in tables if t.get('hastriggers'))
        
        doc += f"- **包含索引的表**: {has_indexes} 个\n"
        doc += f"- **包含规则的表**: {has_rules} 个\n"
        doc += f"- **包含触发器的表**: {has_triggers} 个\n\n"
        
        doc += "---\n\n"
        doc += f"*文档生成时间: {self.timestamp}*\n"
        doc += "*由 Kingbase MCP 服务自动生成*\n"
        
        return doc
    
    def generate_json_structure(self, table_name: str, structure: List[Dict[str, Any]], 
                              indexes: List[Dict[str, Any]], 
                              constraints: List[Dict[str, Any]]) -> str:
        """生成JSON格式的表结构"""
        data = {
            "table_name": table_name,
            "generated_at": self.timestamp,
            "database": "HR_BASE",
            "schema": "public",
            "structure": {
                "columns": structure,
                "indexes": indexes,
                "constraints": constraints
            },
            "statistics": {
                "column_count": len(structure),
                "index_count": len(indexes),
                "constraint_count": len(constraints)
            }
        }
        return json.dumps(data, ensure_ascii=False, indent=2)
    
    def _get_constraint_type_name(self, constraint_type: str) -> str:
        """获取约束类型中文名称"""
        type_mapping = {
            'PRIMARY KEY': '主键约束',
            'FOREIGN KEY': '外键约束',
            'UNIQUE': '唯一约束',
            'CHECK': '检查约束',
            'NOT NULL': '非空约束'
        }
        return type_mapping.get(constraint_type, constraint_type)
    
    def generate_sql_create_statement(self, table_name: str, structure: List[Dict[str, Any]]) -> str:
        """生成建表SQL语句（仅用于文档参考）"""
        sql = f"-- 表结构参考SQL (仅供参考，不可执行)\n"
        sql += f"-- 表名: {table_name}\n"
        sql += f"-- 生成时间: {self.timestamp}\n\n"
        sql += f"CREATE TABLE {table_name} (\n"
        
        columns = []
        for col in structure:
            col_def = f"    {col.get('column_name', '')}"
            
            # 数据类型
            data_type = col.get('data_type', '')
            if col.get('character_maximum_length'):
                data_type += f"({col.get('character_maximum_length')})"
            elif col.get('numeric_precision') and col.get('numeric_scale'):
                data_type += f"({col.get('numeric_precision')},{col.get('numeric_scale')})"
            
            col_def += f" {data_type}"
            
            # 非空约束
            if col.get('is_nullable') == 'NO':
                col_def += " NOT NULL"
            
            # 默认值
            if col.get('column_default'):
                col_def += f" DEFAULT {col.get('column_default')}"
            
            # 注释
            if col.get('column_comment'):
                col_def += f" -- {col.get('column_comment')}"
            
            columns.append(col_def)
        
        sql += ",\n".join(columns)
        sql += "\n);\n\n"
        sql += "-- 注意: 此SQL仅为结构参考，实际建表请根据业务需求调整\n"
        
        return sql


# 全局文档生成器实例
doc_generator = DocumentGenerator() 