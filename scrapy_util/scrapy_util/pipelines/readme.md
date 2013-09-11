mongoSave pipeline
==================
1) 通过settings配置是否启用及mongo选项

2) gridfs使用

3) 处理流程

item.mongo_save(){not pymongo connenct/return dict}

mongo_save(){not save/collection name/unique/index}
-> before_save{一次初始化}

日志


sql save pipeline
==================
考虑非zs pymysql 或 sqlalchemy session

流程:
item.sql_save()

item_save(table_name/Fields/日志文件)

