import re


def read_data(filename):

    with open(filename, 'r', encoding='koi8-r') as file:
        data = file.readlines()

    questions = {}
    for index, phrase in enumerate(data):
        if 'Вопрос' in phrase:
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
