文件夹内包含：
- Library数据库备份文件（无数据，仅结构）
- Library项目文件

注意：
如何连接数据库
- 找到DATABASE目录下的database.ini文件，将内容修改为自己的数据库信息，然后运行同目录下的test_connection.py文件，如果有返回信息，表示连接成功。
如何导入CSV初始文件
- 运行DATABASE目录下的initializer.py文件，然后可以在数据库中检查是否正确插入了相关表的数据。


Folder contents include:


- Library database backup file (structure only, no data)

- Library project files 


Note:
How to connect to the database:

1. Locate the database.ini file in the DATABASE directory

Modify the content with your own database information.

2. Run the test_connection.py file in the same directory - if return information is displayed, the connection is successful

How to import CSV initial files:


1. Run the initializer.py file in the DATABASE directory.


2. Verify in the database whether the data has been correctly inserted into the relevant tables.

