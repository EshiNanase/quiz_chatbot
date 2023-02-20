
filename = 'quiz-questions.txt'
with open(filename, 'r', encoding='koi8-r') as file:
    data = file.readlines()

print(data)

text = {}
for i, j in enumerate(data):
    if 'Вопрос' in data[i]:
        index = i
        question = data[index + 1]
        while 'Комментарий' not in question:
            index += 1
            question += data[index + 1]
        question = question.replace('\n', ' ')
        question = question.replace('Комментарий', '')
        question = question.split('Ответ:')
        text[question[0]] = question[1].replace(' ', '', 1)

for i in text:
    print('Вопрос')
    print(i)
    print('Ответ')
    print(text[i])
    print('\n')
