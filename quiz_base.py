import random


def create_data(file):
    filename = file
    with open(filename, 'r', encoding='koi8-r') as file:
        data = file.readlines()

    text = {}
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
            text[question] = answer.strip()
    return text


def write_data():
    data = create_data('zvonok17.txt')
    filename = 'quiz-questions.txt'
    with open(filename, 'a', encoding='utf-8') as file:
        for question, answer in data.items():
            file.write(f'{question}---{answer}\n')


def read_data():
    filename = 'quiz-questions.txt'
    with open(filename, 'r', encoding='utf-8') as file:
        data = file.readlines()

    questions_base = {}

    for pair in data:
        question = pair.split('---')[0]
        answer = pair.split('---')[1].replace('\n', '')
        questions_base[question] = answer

    return questions_base


def send_question(data):
    question = random.choice(list(data.keys()))
    return question
