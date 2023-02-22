import os
import random


def read_data():
    filename = os.environ['PATH_TXT']
    with open(filename, 'r', encoding='utf-8') as file:
        data = file.readlines()

    questions_base = {}

    for pair in data:
        question = pair.split('---')[0]
        answer = pair.split('---')[1].replace('\n', '')
        questions_base[question] = answer

    return questions_base
