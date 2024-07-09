from sqlalchemy import create_engine, text
from sqlalchemy.engine.reflection import Inspector
import pandas as pd

# 数据库连接 URL
db_url = open('secret/database_info.txt').read().strip()  # 'mysql+mysqlconnector://root:[SECRET]@[IP]/[DATABASE]'
engine = create_engine(db_url)


def get_structure_info():
  inspector = Inspector.from_engine(engine)
  tables = inspector.get_table_names()
  
  structure = ''
  for ti, table in enumerate(tables):
    structure += f"\nTable {ti}: {table}\n"
    for column in inspector.get_columns(table):
      comment = column.get('comment')
      col_type = column['type']
      length = getattr(col_type, 'length', None)
      display_type = f"{col_type}"
      if length is not None:
        display_type += f"({length})"
      text = f"  Column: {column['name']}  Type: {display_type}"
      if comment:
        text += f"  Comment: {comment}"
      structure += text + '\n'
  
  return structure


def execute_sql(sql_query):
  with engine.connect() as connection:
    try:
      result = connection.execute(text(sql_query))
      if sql_query.lower().strip().startswith('select'):
        df = pd.DataFrame(result.fetchall())
        df.columns = result.keys()
        query_result = str(df)
        return query_result
    except Exception as e:
      print(f"Execute SQL Error: {e}")
  return ''
