# Modified from https://github.com/whyjay17/leetcode_recommender
import requests
import json
import csv

# request question list from the api
req = requests.get(url='https://leetcode.com/api/problems/algorithms/')

# get json data
json_data = json.loads(req.text)

# get question list
questions = json_data['stat_status_pairs']

with open('../data/leetcode_problems.csv', 'w', newline='', encoding='UTF-8') as csvfile:
    writer = csv.writer(csvfile, delimiter=',')

    # header
    writer.writerow(["id", "name", "name-slug"])

    for json in questions:
        # get the meta info of algorithm
        stat = json['stat']
        id = stat['frontend_question_id']
        name = stat['question__title']
        name_slug = stat['question__title_slug']
        writer.writerow([id, name, name_slug])
