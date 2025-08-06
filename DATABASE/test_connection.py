from database import Database


def test_connection():
    # 创建Database实例
    db = Database()

    try:
        # 建立连接
        connection = db.connect()

        if connection:
            print("Connection test successful!")

            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """)
                tables = cursor.fetchall()
                print("\nTables in the database:")
                for table in tables:
                    table_name = table[0]
                    print(f"\n=== 表: {table_name} ===")

                    try:
                        # 2. 获取表的前5行数据
                        cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
                        rows = cursor.fetchall()

                        # 3. 获取列名
                        col_names = [desc[0] for desc in cursor.description]
                        print("列名:", ", ".join(col_names))

                        # 4. 打印数据
                        print("返回前五行数据:")
                        for row in rows:
                            print(row)

                    except Exception as e:
                        print(f"  无法读取表 {table_name} 的数据: {e}")

    finally:
        # 确保连接被关闭
        db.disconnect()


if __name__ == "__main__":
    test_connection()