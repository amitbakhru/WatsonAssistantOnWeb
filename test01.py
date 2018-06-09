import sqlite3
import pandas as pd

db_path = '/C:/pyfiles/for_watson.db'
conn = sqlite3.connect(db_path)
ques_cur = conn.cursor()
ques_cur.execute("SELECT * FROM user_ques WHERE user = ?", ("d11111", ))
rows = ques_cur.fetchall()
df = pd.DataFrame(rows, columns=['user', 'qnum', 'ques', 'answ'])
df.set_index('qnum', inplace=True)
print(rows)
print(df)
