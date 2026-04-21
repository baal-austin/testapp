import psycopg
from psycopg.rows import dict_row  # 可选：将查询结果以字典形式返回

# 数据库连接配置（请根据你的 PostgreSQL 设置修改）
DB_CONFIG = {
    "host": "localhost",      # 如果 PostgreSQL 不在本机，改为 IP 地址
    "port": 5432,             # 默认端口
    "dbname": "word_graph",     # 数据库名称（默认安装后有一个 postgres 库）
    "user": "postgres",       # 用户名（通常默认是 postgres）
    "password": "123456"  # 安装时设置的密码
}

def main():
    # 连接数据库（使用 with 语句会自动提交事务并关闭连接）
    with psycopg.connect(**DB_CONFIG) as conn:
        # 打开游标执行操作
        with conn.cursor() as cur:
            # 1. 创建测试表（如果不存在）
            cur.execute("""
                CREATE TABLE IF NOT EXISTS test_table (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(50) NOT NULL,
                    age INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            print("✅ 表 test_table 已存在或创建成功")

            # 2. 插入单条数据
            cur.execute(
                "INSERT INTO test_table (name, age) VALUES (%s, %s)",
                ("Alice", 25)
            )
            print("✅ 插入单条数据成功")

            # 3. 批量插入多条数据
            data = [("Bob", 30), ("Charlie", 28), ("Diana", 22)]
            cur.executemany(
                "INSERT INTO test_table (name, age) VALUES (%s, %s)",
                data
            )
            print("✅ 批量插入数据成功")

            # 4. 查询数据（普通方式，返回元组）
            cur.execute("SELECT id, name, age, created_at FROM test_table")
            rows = cur.fetchall()
            print("\n🔍 普通查询结果（每行是一个元组）：")
            for row in rows:
                print(f"ID: {row[0]}, Name: {row[1]}, Age: {row[2]}, Created: {row[3]}")

            # 5. 使用字典游标查询（更直观）
            # 需要重新创建一个使用 row_factory=dict_row 的游标
            with conn.cursor(row_factory=dict_row) as dict_cur:
                dict_cur.execute("SELECT id, name, age FROM test_table WHERE age > %s", (25,))
                dict_rows = dict_cur.fetchall()
                print("\n🔍 字典查询结果（age > 25）：")
                for r in dict_rows:
                    print(f"ID: {r['id']}, Name: {r['name']}, Age: {r['age']}")

            # 6. 更新数据
            cur.execute("UPDATE test_table SET age = %s WHERE name = %s", (26, "Alice"))
            print("✅ 更新数据成功")

            # 7. 删除数据
            cur.execute("DELETE FROM test_table WHERE name = %s", ("Diana",))
            print("✅ 删除数据成功")

            # 8. 查询表的总行数
            cur.execute("SELECT COUNT(*) FROM test_table")
            count = cur.fetchone()[0]
            print(f"\n📊 当前表中总行数: {count}")

    # 连接会自动关闭（with 块结束）
    print("\n🎉 所有操作完成，连接已关闭")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ 发生错误: {e}")