from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_bootstrap import Bootstrap
from wtforms import StringField, SelectField, IntegerField
from wtforms.validators import DataRequired, NumberRange, Regexp
from flask_wtf import FlaskForm
import os
import choices
import requests
import json
import random
from dotenv import load_dotenv

app = Flask(__name__, static_folder='static/')

load_dotenv()
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
app.config['SECRET_KEY'] = os.getenv('CSRF_SECRET_KEY')

db = SQLAlchemy(app)
CORS(app)
Bootstrap(app)


def get_problems(form):
    username = form.username.data.strip()
    tag = form.tag.data
    difficulty = form.difficulty.data
    similarity = form.similarity.data

    graphql_data = {"query": "\n    query recentAcSubmissions($username: String!, $limit: Int!) {\n  recentAcSubmissionList(username: $username, limit: $limit) {\n   titleSlug\n     }\n}\n    ", "variables": {
        "username": f"{username}", "limit": 20}}
    r = requests.post('https://leetcode.com/graphql', json=graphql_data).json()
    if 'errors' in r:
        error_message = r['errors'][0]['message']
        return error_message, []

    recent_ac = []
    for i in range(len(r['data']['recentAcSubmissionList'])):
        recent_ac.append(
            '\'' + r['data']['recentAcSubmissionList'][i]['titleSlug'] + '\'')

    if recent_ac:
        placeholders = ', '.join(recent_ac)
        db.engine.execute(f'''
        DROP TABLE IF EXISTS solved_problems;
        CREATE TEMP TABLE solved_problems AS
        (SELECT problem_id FROM problem
        WHERE problem_name_slug in ({placeholders}));
        ''')
        db.engine.execute(f'''
        DROP TABLE IF EXISTS candidates;
        CREATE TEMP TABLE candidates AS
        (SELECT s.problem_id_a AS problem_id, MAX(s.similarity) AS similarity
        FROM Similarity AS s
        WHERE s.problem_id_b IN (SELECT * FROM solved_problems)
        AND s.problem_id_a NOT IN (SELECT * FROM solved_problems)
        GROUP BY problem_id);
        ''')
    else:
        db.engine.execute(f'''
        DROP TABLE IF EXISTS candidates;
        CREATE TEMP TABLE candidates AS
        (SELECT problem_id, RANDOM() AS similarity
        FROM problem);
        ''')

    tag = f"'{tag}'" if tag != 'any' else choices.all_tags
    difficulty = difficulty if difficulty != '0' else choices.all_difficulties
    problem_list = db.engine.execute(f'''
        SELECT DISTINCT n.problem_id AS problem_id, n.similarity AS similarity
        FROM (candidates NATURAL JOIN tag NATURAL JOIN difficulty) AS n
        WHERE ((n.tag IN ({tag})) AND (n.difficulty IN ({difficulty})))
        ORDER BY n.similarity ASC;
        ''').fetchall()

    middle = int(len(problem_list) / 100 * similarity)
    rangel, ranger = max(0, middle - 10), min(len(problem_list), middle + 10)
    problem_num = min(5, len(problem_list))
    problem_list = random.sample(problem_list[rangel:ranger + 1], problem_num)

    if not problem_list:
        error_message = 'No problems match the query.'
        return error_message, []
    else:
        placeholders = ','.join([str(x[0]) for x in problem_list])
        problem_list = db.engine.execute(f'''
            SELECT * FROM Problem
            WHERE problem_id in ({placeholders});
            ''').fetchall()
        error_message = 'ok'
        return error_message, problem_list


class RegForm(FlaskForm):
    username = StringField('Username', validators=[
                           DataRequired(), Regexp('^(\ *[0-9a-zA-Z_\-]*\ *)$', message='Please enter a valid username.')])
    tag = SelectField('Tag', choices=choices.tags)
    difficulty = SelectField('Difficulty',
                             choices=choices.difficulties)
    similarity = IntegerField(validators=[NumberRange(0, 100)])


@app.route('/', methods=['GET', 'POST'])
def index():
    form = RegForm()
    if form.validate_on_submit():
        status, problems = get_problems(form)
        return render_template('home.html', form=form, status=status, problems=problems)
    return render_template('home.html', form=form)


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
