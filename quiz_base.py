import os
import re


def read_data():

    filename = os.environ['PATH_TXT']
    with open(filename, 'r', encoding='koi8-r') as file:
        data = file.readlines()

    questions = {}
    for i, j in enumerate(data):
        if 'Вопрос' in data[i]:
            index = i
            question = data[index + 1]
            while 'Комментарий' not in question:
                index += 1
                question += data[index + 1]
            question = question.replace('\n', ' ')
            question = question.split('Ответ:')
            answer = question[1].split('.')[0]
            question = question[0]
            question = re.sub(r"[\(\[].*?[\)\]]", "", question).strip()
            if 'Источник' in question or 'Дуплет' in question:
                continue
            questions[question] = answer.strip()

    return questions
