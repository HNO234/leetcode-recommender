# Modified from https://github.com/whyjay17/leetcode_recommender
import csv
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

data = pd.read_csv(
    '../data/leetcode_problem_contents.csv', low_memory=False)

tfidf = TfidfVectorizer()
tfidf_matrix = tfidf.fit_transform(data['content'])

cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

with open('../data/leetcode_problem_simlarities.csv', 'w', newline='', encoding='UTF-8') as csvfile:
    writer = csv.writer(csvfile, delimiter=',')

    # header
    writer.writerow(['ida', 'idb', 'similarity'])

    problem_count = len(data)

    for i in range(problem_count):
        for j in range(problem_count):
            if i != j:
                writer.writerow(
                    [data['id'][i], data['id'][j], cosine_sim[i][j]])
