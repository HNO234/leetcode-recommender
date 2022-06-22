import psycopg2
import pandas as pd
import requests
from rds_config import *
import json

# username = input().strip()
username = 'dreamoon'

data = {"query": "\n    query recentAcSubmissions($username: String!, $limit: Int!) {\n  recentAcSubmissionList(username: $username, limit: $limit) {\n   titleSlug\n     }\n}\n    ", "variables": {
    "username": f"{username}", "limit": 20}}
r = requests.post('https://leetcode.com/graphql', json=data).json()

if 'errors' in r:
    message = r['errors'][0]['message']
    raise ValueError(f'{message}')

recent_ac = []
for i in range(20):
    recent_ac.append(
        '\'' + r['data']['recentAcSubmissionList'][i]['titleSlug'] + '\'')
placeholders = ', '.join(recent_ac)

conn = psycopg2.connect(host=host,
                        database=database,
                        user=user,
                        password=password)
cur = conn.cursor()


cur.execute(f'''
SELECT s.problem_id_a AS problem_id, MAX(s.similarity) AS similarity
FROM Similarity AS s
WHERE s.problem_id_b IN (
SELECT problem_id FROM problem
WHERE problem_name_slug in ({placeholders}))
GROUP BY problem_id
ORDER BY similarity DESC
''')

print(cur.fetchall())

conn.close()
cur.close()
