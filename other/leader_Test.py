import pandas as pd
user_score = { 'Username':'ABCDE','Score':0}
username = 'ABCDE'
score = 0
# df = pd.DataFrame(user_score)
df = pd.read_csv ('leaderboard.csv')
print(df)
old_df = df
df = df.append(user_score, ignore_index = True)
# df = df.sort_values(by='Score',ascending=False)

# print(len(old_df))
# print(len(df))
# for index, row in df.iterrows():
#      if index !=len(df):
#         row.replace = [username,score]
df.to_csv('leaderboard.csv', mode='a', index=False, header=False)