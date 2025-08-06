import psycopg2
import csv
import os
import configparser

# 读取 database.ini 配置
def read_db_config(filename="database.ini", section="postgresql"):
    parser = configparser.ConfigParser()
    parser.read(filename)

    if not parser.has_section(section):
        raise Exception(f"配置文件 {filename} 中缺少 [{section}] 部分")

    return {key: value for key, value in parser.items(section)}

# 连接 PostgreSQL
def connect_db():
    """建立数据库连接"""
    db_config = read_db_config()
    return psycopg2.connect(**db_config)

def import_user_types(cursor):
    csv_file_path = '../CSV_FILES/UserTypes.csv'
    with open(csv_file_path, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # 跳过表头
        for row in reader:
            if len(row) == 5:
                try:
                    print(f"插入数据行: {row}")
                    query = """
                        INSERT INTO user_types (type_id, type_name, max_borrowings, max_borrowing_days, late_fee_per_day)
                        VALUES (%s, %s, %s, %s, %s)
                    """
                    cursor.execute(query, (row[0], row[1], row[2], row[3], row[4]))
                except Exception as e:
                    print(f"插入数据时发生错误: {e}")

def import_material_types(cursor):
    csv_file_path = '../CSV_FILES/MaterialTypes.csv'
    with open(csv_file_path, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # 跳过表头
        for row in reader:
            if len(row) == 2:
                try:
                    print(f"插入数据行: {row}")
                    query = """
                        INSERT INTO material_types (type_id, type_name)
                        VALUES (%s, %s)
                    """
                    cursor.execute(query, (row[0], row[1]))
                except Exception as e:
                    print(f"插入数据时发生错误: {e}")

def import_materials(cursor):
    # CSV 文件路径
    csv_file_path = '../CSV_FILES/Materials.csv'

    # 读取 CSV 文件并导入数据
    with open(csv_file_path, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # 跳过表头
        for row in reader:
            print(f"读取数据行: {row}")  # 打印每行数据
            print(f"当前行字段数量: {len(row)}")  # 打印字段数量

            if len(row) == 7:  # 确保每行有7个字段
                try:
                    # 插入 SQL 语句
                    query = """
                        INSERT INTO materials (material_name, author, publisher, publication_date, type_id, price)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(query, (row[0], row[1], row[2], row[3], row[4], row[6]))
                    print(f"成功插入: {row}")
                except Exception as e:
                    print(f"插入数据时发生错误: {e} - 失败数据行: {row}")


def import_users(cursor):
    csv_file_path = '../CSV_FILES/Users.csv'
    with open(csv_file_path, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # 跳过表头
        for row in reader:
            if len(row) == 3:
                try:
                    print(f"插入数据行: {row}")
                    query = """
                        INSERT INTO users (name, contact, user_type_id)
                        VALUES (%s, %s, %s)
                    """
                    cursor.execute(query, (row[0], row[1], row[2]))
                except Exception as e:
                    print(f"插入数据时发生错误: {e}")

def main():
    try:
        conn = connect_db()
        cursor = conn.cursor()

        import_user_types(cursor)
        import_material_types(cursor)
        import_materials(cursor)
        import_users(cursor)

        # 提交事务
        conn.commit()

    except Exception as e:
        print(f"发生错误: {e}")
        conn.rollback()

    finally:
        # 关闭连接
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()
