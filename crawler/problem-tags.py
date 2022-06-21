# Modified from https://github.com/whyjay17/leetcode_recommender
import requests
import json
import csv
from bs4 import BeautifulSoup as bs

# request question list from the api
req = requests.get(url='https://leetcode.com/api/problems/algorithms/')

# get json data
json_data = json.loads(req.text)

# get question list
questions = json_data['stat_status_pairs']

with open('../data/leetcode_problem_tags.csv', 'w', newline='', encoding='UTF-8') as csvfile:
    writer = csv.writer(csvfile, delimiter=',')

    # header
    writer.writerow(["id", "tag"])

    for json in questions:
        # get the meta info of algorithm
        stat = json['stat']
        id = stat['frontend_question_id']
        question_name = stat['question__title_slug']
        # The pages does a POST request for dynamic content. Need to send a MySql query to database
        data = {"operationName": "questionData", "variables": {"titleSlug": "{}".format(question_name)}, "query": "query questionData($titleSlug: String!) {\n  question(titleSlug: $titleSlug) {\n    questionId\n    questionFrontendId\n    boundTopicId\n    title\n    titleSlug\n    content\n    translatedTitle\n    translatedContent\n    isPaidOnly\n    difficulty\n    likes\n    dislikes\n    isLiked\n    similarQuestions\n    contributors {\n      username\n      profileUrl\n      avatarUrl\n      __typename\n    }\n    langToValidPlayground\n    topicTags {\n      name\n      slug\n      translatedName\n      __typename\n    }\n    companyTagStats\n    codeSnippets {\n      lang\n      langSlug\n      code\n      __typename\n    }\n    stats\n    hints\n    solution {\n      id\n      canSeeDetail\n      __typename\n    }\n    status\n    sampleTestCase\n    metaData\n    judgerAvailable\n    judgeType\n    mysqlSchemas\n    enableRunCode\n    enableTestMode\n    envInfo\n    libraryUrl\n    __typename\n  }\n}\n"}
        r = requests.post('https://leetcode.com/graphql', json=data).json()
        if r['data']['question']['content']:
            topics = r['data']['question']['topicTags']  # get topic list
            topic_arr = [item['name'].lower() for item in topics]
            for topic in topic_arr:
                writer.writerow([id, topic])
