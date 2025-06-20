"""
人大金仓数据库连接和查询模块
支持多种安全模式和灵活的访问控制

Copyright (c) 2025 qyue
Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""
import psycopg2
import psycopg2.extras
from typing import List, Dict, Any, Optional, Set
import logging
from contextlib import contextmanager
from config import get_config_instance, SecurityMode

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SQLValidator:
    """SQL语句验证器"""
    
    # 只读操作
    READONLY_OPERATIONS = {
        'SELECT', 'WITH', 'SHOW', 'DESCRIBE', 'EXPLAIN', 'ANALYZE'
    }
    
    # 写入操作
    WRITE_OPERATIONS = {
        'INSERT', 'UPDATE'
    }
    
    # 危险操作
    DANGEROUS_OPERATIONS = {
        'DELETE', 'DROP', 'CREATE', 'ALTER', 'TRUNCATE', 'GRANT', 'REVOKE'
    }
    
    @classmethod
    def validate_sql(cls, sql: str, security_mode: SecurityMode) -> bool:
        """验证SQL语句是否符合当前安全模式"""
        sql_upper = sql.upper().strip()
        
        # 提取SQL的第一个关键字
        first_keyword = cls._extract_first_keyword(sql_upper)
        
        if security_mode == SecurityMode.READONLY:
            return cls._validate_readonly(first_keyword, sql_upper)
        elif security_mode == SecurityMode.LIMITED_WRITE:
            return cls._validate_limited_write(first_keyword, sql_upper)
        elif security_mode == SecurityMode.FULL_ACCESS:
            return True  # 完全访问模式允许所有操作
        
        return False
    
    @classmethod
    def _extract_first_keyword(cls, sql_upper: str) -> str:
        """提取SQL的第一个关键字"""
        words = sql_upper.split()
        return words[0] if words else ""
    
    @classmethod
    def _validate_readonly(cls, first_keyword: str, sql_upper: str) -> bool:
        """验证只读模式的SQL"""
        if first_keyword not in cls.READONLY_OPERATIONS:
            return False
        
        # 对于SELECT查询，进行更精确的检查
        if first_keyword == 'SELECT':
            # 检查是否包含危险的SQL子句（而不是简单的关键字匹配）
            dangerous_patterns = [
                r'\bDROP\s+TABLE\b',
                r'\bTRUNCATE\s+TABLE\b', 
                r'\bDELETE\s+FROM\b',
                r'\bINSERT\s+INTO\b',
                r'\bUPDATE\s+\w+\s+SET\b',
                r'\bCREATE\s+TABLE\b',
                r'\bALTER\s+TABLE\b'
            ]
            
            import re
            for pattern in dangerous_patterns:
                if re.search(pattern, sql_upper):
                    return False
        else:
            # 对于其他只读操作，检查是否包含写入操作的关键子句
            forbidden_in_readonly = cls.WRITE_OPERATIONS.union(cls.DANGEROUS_OPERATIONS)
            for forbidden in forbidden_in_readonly:
                if forbidden in sql_upper:
                    return False
        
        return True
    
    @classmethod
    def _validate_limited_write(cls, first_keyword: str, sql_upper: str) -> bool:
        """验证限制写入模式的SQL"""
        allowed_operations = cls.READONLY_OPERATIONS.union(cls.WRITE_OPERATIONS)
        
        if first_keyword not in allowed_operations:
            return False
        
        # 检查是否包含危险操作
        for dangerous in cls.DANGEROUS_OPERATIONS:
            if dangerous in sql_upper:
                return False
        
        return True
    
    @classmethod
    def get_error_message(cls, sql: str, security_mode: SecurityMode) -> str:
        """获取具体的错误信息"""
        sql_upper = sql.upper().strip()
        first_keyword = cls._extract_first_keyword(sql_upper)
        
        if security_mode == SecurityMode.READONLY:
            if first_keyword in cls.WRITE_OPERATIONS:
                return f"只读模式下禁止写入操作: {first_keyword}"
            elif first_keyword in cls.DANGEROUS_OPERATIONS:
                return f"只读模式下禁止危险操作: {first_keyword}"
            else:
                return f"只读模式下不支持的操作: {first_keyword}"
        
        elif security_mode == SecurityMode.LIMITED_WRITE:
            if first_keyword in cls.DANGEROUS_OPERATIONS:
                return f"限制写入模式下禁止危险操作: {first_keyword}"
            else:
                return f"限制写入模式下不支持的操作: {first_keyword}"
        
        return "操作被安全策略禁止"


class KingbaseDatabase:
    """人大金仓数据库操作类"""
    
    def __init__(self):
        self.config = get_config_instance()
        self.sql_validator = SQLValidator()
        logger.info(f"数据库服务初始化完成，安全模式: {self.config.security_mode.value}")
    
    @contextmanager
    def get_connection(self):
        """获取数据库连接上下文管理器"""
        conn = None
        try:
            conn = psycopg2.connect(
                host=self.config.host,
                port=self.config.port,
                database=self.config.database,
                user=self.config.username,
                password=self.config.password,
                connect_timeout=self.config.connect_timeout,
                application_name=f"kingbase-mcp-{self.config.security_mode.value}"
            )
            
            # 根据安全模式设置事务属性
            if self.config.is_readonly_mode():
                with conn.cursor() as cur:
                    cur.execute("SET default_transaction_read_only = on;")
                    cur.execute("SET transaction_read_only = on;")
                    logger.info("已设置数据库连接为只读模式")
            
            conn.commit()
            logger.info(f"成功连接到人大金仓数据库（{self.config.security_mode.value}模式）")
            yield conn
            
        except psycopg2.Error as e:
            logger.error(f"数据库连接错误: {e}")
            raise
        finally:
            if conn:
                conn.close()
                logger.info("数据库连接已关闭")
    
    def execute_query(self, sql: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """执行查询语句"""
        # 安全检查：验证SQL是否符合当前安全模式
        if not self.sql_validator.validate_sql(sql, self.config.security_mode):
            error_msg = self.sql_validator.get_error_message(sql, self.config.security_mode)
            raise ValueError(f"SQL操作被安全策略禁止: {error_msg}")
        
        # 记录查询日志（如果启用）
        if self.config.enable_query_log:
            logger.info(f"执行SQL ({self.config.security_mode.value}): {sql[:200]}...")
        
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                try:
                    cur.execute(sql, params)
                    
                    # 对于查询操作，获取结果
                    if sql.upper().strip().startswith(('SELECT', 'WITH', 'SHOW', 'DESCRIBE', 'EXPLAIN')):
                        results = cur.fetchall()
                        
                        # 限制返回结果数量
                        if len(results) > self.config.max_result_rows:
                            logger.warning(f"查询结果超过限制({self.config.max_result_rows})，截断返回")
                            results = results[:self.config.max_result_rows]
                        
                        logger.info(f"查询执行成功，返回 {len(results)} 条记录")
                        return [dict(row) for row in results]
                    else:
                        # 对于非查询操作（INSERT、UPDATE等），提交事务并返回影响的行数
                        conn.commit()
                        affected_rows = cur.rowcount
                        logger.info(f"操作执行成功，影响 {affected_rows} 行")
                        return [{"affected_rows": affected_rows, "status": "success"}]
                        
                except psycopg2.Error as e:
                    logger.error(f"SQL执行失败: {e}")
                    raise
    
    def execute_safe_query(self, sql: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """执行安全查询（强制只读，用于系统查询）"""
        # 强制验证为只读操作
        if not self.sql_validator.validate_sql(sql, SecurityMode.READONLY):
            raise ValueError("系统查询必须是只读操作")
        
        return self.execute_query(sql, params)
    
    def get_all_tables(self, schema: str = 'public') -> List[Dict[str, Any]]:
        """获取所有表信息"""
        # 验证模式是否在允许列表中
        if not self._is_schema_allowed(schema):
            allowed_schemas = self._get_allowed_schemas_display()
            raise ValueError(f"不允许访问模式: {schema}，允许的模式: {allowed_schemas}")
        
        sql = """
        SELECT 
            schemaname,
            tablename,
            tableowner,
            hasindexes,
            hasrules,
            hastriggers,
            rowsecurity
        FROM pg_tables 
        WHERE schemaname = %s
        ORDER BY tablename;
        """
        return self.execute_safe_query(sql, (schema,))
    
    def _is_schema_allowed(self, schema: str) -> bool:
        """检查schema是否被允许访问"""
        # 如果配置为允许所有schema
        if self.config.is_all_schemas_allowed():
            return True
        
        # 如果配置为自动发现schema
        if self.config.is_auto_discover_schemas():
            # 尝试查询该schema是否存在且用户有权限访问
            try:
                test_sql = """
                SELECT schema_name 
                FROM information_schema.schemata 
                WHERE schema_name = %s;
                """
                result = self.execute_safe_query(test_sql, (schema,))
                return len(result) > 0
            except Exception:
                return False
        
        # 否则检查是否在明确允许的列表中
        return schema in self.config.allowed_schemas
    
    def _get_allowed_schemas_display(self) -> str:
        """获取允许的schema的显示字符串"""
        if self.config.is_all_schemas_allowed():
            return "所有模式(*)"
        elif self.config.is_auto_discover_schemas():
            return "自动发现(auto)"
        else:
            return str(self.config.allowed_schemas)
    
    def get_available_schemas(self) -> List[Dict[str, Any]]:
        """获取用户有权限访问的所有schema"""
        sql = """
        SELECT schema_name as schemaname
        FROM information_schema.schemata 
        WHERE schema_name NOT IN ('information_schema', 'pg_catalog', 'pg_toast', 'pg_temp_1', 'pg_toast_temp_1')
        ORDER BY schema_name;
        """
        return self.execute_safe_query(sql)

    def get_table_structure(self, table_name: str, schema: str = 'public') -> List[Dict[str, Any]]:
        """获取表结构信息"""
        # 验证模式是否在允许列表中
        if not self._is_schema_allowed(schema):
            allowed_schemas = self._get_allowed_schemas_display()
            raise ValueError(f"不允许访问模式: {schema}，允许的模式: {allowed_schemas}")
        
        # 尝试获取包含注释的完整表结构信息
        try:
            # 首先尝试使用pg_catalog获取注释
            sql_with_comments = """
            SELECT 
                c.column_name,
                c.data_type,
                c.character_maximum_length,
                c.numeric_precision,
                c.numeric_scale,
                c.is_nullable,
                c.column_default,
                c.ordinal_position,
                CASE 
                    WHEN pk.column_name IS NOT NULL THEN 'YES'
                    ELSE 'NO'
                END as is_primary_key,
                COALESCE(
                    (SELECT pg_catalog.col_description(pgc.oid, c.ordinal_position)
                     FROM pg_catalog.pg_class pgc
                     INNER JOIN pg_catalog.pg_namespace pgn ON pgn.oid = pgc.relnamespace
                     WHERE pgc.relname = c.table_name AND pgn.nspname = c.table_schema),
                    ''
                ) as column_comment
            FROM information_schema.columns c
            LEFT JOIN (
                SELECT ku.column_name
                FROM information_schema.table_constraints tc
                INNER JOIN information_schema.key_column_usage ku
                    ON tc.constraint_name = ku.constraint_name
                    AND tc.table_schema = ku.table_schema
                WHERE tc.constraint_type = 'PRIMARY KEY'
                    AND tc.table_name = %s
                    AND tc.table_schema = %s
            ) pk ON c.column_name = pk.column_name
            WHERE c.table_name = %s
                AND c.table_schema = %s
            ORDER BY c.ordinal_position;
            """
            
            result = self.execute_safe_query(sql_with_comments, (table_name, schema, table_name, schema))
            if result:
                logger.info(f"成功获取表结构（包含注释）：{len(result)} 个字段")
                return result
                
        except Exception as e:
            logger.warning(f"获取注释信息失败，使用基础查询: {e}")
        
        # 如果注释查询失败，使用简化查询
        sql_basic = """
        SELECT 
            c.column_name,
            c.data_type,
            c.character_maximum_length,
            c.numeric_precision,
            c.numeric_scale,
            c.is_nullable,
            c.column_default,
            c.ordinal_position,
            CASE 
                WHEN pk.column_name IS NOT NULL THEN 'YES'
                ELSE 'NO'
            END as is_primary_key,
            '' as column_comment
        FROM information_schema.columns c
        LEFT JOIN (
            SELECT ku.column_name
            FROM information_schema.table_constraints tc
            INNER JOIN information_schema.key_column_usage ku
                ON tc.constraint_name = ku.constraint_name
                AND tc.table_schema = ku.table_schema
            WHERE tc.constraint_type = 'PRIMARY KEY'
                AND tc.table_name = %s
                AND tc.table_schema = %s
        ) pk ON c.column_name = pk.column_name
        WHERE c.table_name = %s
            AND c.table_schema = %s
        ORDER BY c.ordinal_position;
        """
        return self.execute_safe_query(sql_basic, (table_name, schema, table_name, schema))
    
    def get_table_indexes(self, table_name: str, schema: str = 'public') -> List[Dict[str, Any]]:
        """获取表索引信息"""
        if not self._is_schema_allowed(schema):
            allowed_schemas = self._get_allowed_schemas_display()
            raise ValueError(f"不允许访问模式: {schema}，允许的模式: {allowed_schemas}")
        
        try:
            sql = """
            SELECT 
                indexname,
                indexdef,
                CASE 
                    WHEN indexdef LIKE '%UNIQUE%' THEN 'YES'
                    ELSE 'NO'
                END as is_unique
            FROM pg_indexes 
            WHERE tablename = %s 
                AND schemaname = %s
            ORDER BY indexname;
            """
            return self.execute_safe_query(sql, (table_name, schema))
        except Exception as e:
            logger.warning(f"获取索引信息失败: {e}")
            return []  # 返回空列表而不是抛出异常
    
    def get_table_constraints(self, table_name: str, schema: str = 'public') -> List[Dict[str, Any]]:
        """获取表约束信息"""
        if not self._is_schema_allowed(schema):
            allowed_schemas = self._get_allowed_schemas_display()
            raise ValueError(f"不允许访问模式: {schema}，允许的模式: {allowed_schemas}")
        
        try:
            sql = """
            SELECT 
                tc.constraint_name,
                tc.constraint_type,
                kcu.column_name,
                CASE 
                    WHEN tc.constraint_type = 'FOREIGN KEY' THEN
                        ccu.table_schema||'.'||ccu.table_name||'.'||ccu.column_name
                    ELSE NULL
                END as foreign_key_references
            FROM information_schema.table_constraints tc
            LEFT JOIN information_schema.key_column_usage kcu
                ON tc.constraint_name = kcu.constraint_name
                AND tc.table_schema = kcu.table_schema
            LEFT JOIN information_schema.constraint_column_usage ccu
                ON ccu.constraint_name = tc.constraint_name
                AND ccu.table_schema = tc.table_schema
            WHERE tc.table_name = %s
                AND tc.table_schema = %s
            ORDER BY tc.constraint_type, tc.constraint_name;
            """
            return self.execute_safe_query(sql, (table_name, schema))
        except Exception as e:
            logger.warning(f"获取约束信息失败: {e}")
            return []  # 返回空列表而不是抛出异常
    
    def test_connection(self) -> bool:
        """测试数据库连接"""
        try:
            result = self.execute_safe_query("SELECT 1 as test_connection;")
            return len(result) > 0 and result[0]['test_connection'] == 1
        except Exception as e:
            logger.error(f"连接测试失败: {e}")
            return False
    
    def get_security_info(self) -> Dict[str, Any]:
        """获取当前安全配置信息"""
        return {
            "security_mode": self.config.security_mode.value,
            "allowed_schemas": self.config.allowed_schemas,
            "readonly_mode": self.config.is_readonly_mode(),
            "write_allowed": self.config.is_write_allowed(),
            "dangerous_operations_allowed": self.config.is_dangerous_operation_allowed(),
            "max_result_rows": self.config.max_result_rows,
            "query_log_enabled": self.config.enable_query_log
        }


# 全局数据库实例 - 延迟初始化以避免配置未就绪问题
_db_instance = None

def get_db_instance() -> KingbaseDatabase:
    """获取全局数据库实例"""
    global _db_instance
    if _db_instance is None:
        _db_instance = KingbaseDatabase()
    return _db_instance


# 保持向后兼容性
db = None  # 将在首次使用时初始化 