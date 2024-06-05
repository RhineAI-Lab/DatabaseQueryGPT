import pandas as pd
from sqlalchemy import create_engine

db_url = 'mysql+mysqlconnector://root:henry0313MYSQL@182.92.3.33/gpt_sql_test'
engine = create_engine(db_url)

excel_path = 'tables.xlsx'
xls = pd.ExcelFile(excel_path)

for sheet_name in xls.sheet_names:
  data = pd.read_excel(xls, sheet_name=sheet_name)
  data.to_sql(sheet_name, con=engine, index=False, if_exists='replace')
