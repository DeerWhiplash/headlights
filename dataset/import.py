import mysql.connector
import os
from dotenv import load_dotenv
import pandas as pd
import numpy as np

load_dotenv()

con = mysql.connector.connect(
  host="localhost",
  port="3307",
  user="root",
  password=os.getenv("MYSQL_ROOT_PASSWORD"),
  database=os.getenv("DATABASE_NAME")
)
mycursor = con.cursor()

claimData = pd.read_csv('ProcessedClaimData.csv')
claimData.fillna('', inplace=True)
cols = claimData.columns

colsString = ''.join(f"{col}, " for col in cols)
colsString = colsString[:-2]

valuePlaceholders = ''.join("%s, " for i in cols)
valuePlaceholders = valuePlaceholders[:-2]

sqlQuery = f"INSERT INTO Claim ({colsString}) VALUES ({valuePlaceholders})"
print(sqlQuery)

dataValues = claimData.values
for i in range(len(dataValues)):
    for j in range(len(dataValues[i])):
        if dataValues[i][j] == '':
            dataValues[i][j] = None
dataValues = [tuple(data) for data in dataValues]

mycursor.executemany(sqlQuery, dataValues)

print(mycursor.rowcount, "was inserted.")

con.commit()
con.close()