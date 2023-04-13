import string
import io
import csv
import matplotlib.pyplot as plt
import pandas as pd
import atexit
import os
import create_plots
import warnings
import base64
from json import dumps
from PIL import Image
from flask import Flask, render_template, app, url_for, request, redirect, send_file


warnings.filterwarnings("ignore")


app = Flask(__name__)

PORT = 8080
HOST = '127.0.0.1'

@app.route('/index')
def index(): # Страница с графиками
    global cur_user
    tablo = []
    buy = []
    sale = []
    try:
        with open('static/csv/tablo.csv', 'r') as f: # Формирую данные для табло
            reader = csv.reader(f)
            for row in reader:
                tablo.append(row)

        with open('static/csv/buy.csv', 'r') as f: # Формирую данные для покупки
            reader = csv.reader(f)
            for row in reader:
                buy.append(row)

        with open('static/csv/sale.csv', 'r') as f: # Формирую данные для продажи
            reader = csv.reader(f)
            for row in reader:
                sale.append(row)

        tablo = tablo[1:]
        buy = buy[1:]
        sale = sale[1:]

        for i, e in enumerate(buy):
            buy[i] = [e[0], e[1], str(round(float(e[2]), 2))]

        for i, e in enumerate(sale):
            sale[i] = [e[0], e[1], str(round(float(e[2]), 2))]



    except Exception as ex:
        print(ex)
        print('Я в открытии данных для таблиц!!!!!!')


    return render_template('index.html', tablo=tablo, buy=buy, sale=sale, user=cur_user)


def create_HHTP_tablet(name): # Функция подготавливающая данные для HTML графика
    d100 = pd.read_csv('static/csv/d100.csv')
    data = []
    diff = []
    last = 0
    for i, e in enumerate(d100[name]):
        if i == 0:
            diff.append([i, 0])
        else:
            diff.append([i, e - last])
        data.append([i, e])
        last = e
    return data, diff


@app.route('/ticket/<name>')
def ticket(name): # Главная страница
    data, diff = create_HHTP_tablet(name) # Подготовка данных для HTTP графика
    create_plots.save_plot_by_name(name) # Создание графика цен
    create_plots.save_predict_by_name(name) # Создание графика предсказанных цен

    return render_template('ticket.html', name=name, data=data, diff=diff)


def goodbye():
    path = 'static/Pictures/temp'

    f = os.listdir(path)
    for i in f:
        if i not in 'чтоб была папка':
            os.remove(path + '/' + i) # Удаление графиков


@app.route('/register', methods=['post', 'get'])
def register():
    message = ''
    if request.method == 'POST':
        name = request.form.get('name')
        mail = request.form.get('mail')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        message = valid_pass_and_mail(name, mail, password1, password2)
        if message == '':
            addUser(name, mail, password1)
            return redirect('/login')

    return render_template('register.html', message=message)

@app.route('/login', methods=['post', 'get'])
def login():
    global cur_user
    message = ''
    if request.method == 'POST':
        mail = request.form.get('mail')
        password = request.form.get('password')
        message = check_pass_and_mail(mail, password)
        if message == '':
            for i in users:
                if i[1] == mail:
                    cur_user = i[0]
            return redirect('/index')

    return render_template('login.html', message=message)


def valid_pass_and_mail(name, mail, password, password2) -> str:
    message = ''
    if name == '':
        return 'Имя не указано'
    if mail == '':
        return 'Почта не указана'
    if password == '':
        return 'Пароль не указан'
    if password2 == '':
        return 'Пароль не указан'

    if '@' in mail and '.'  in mail:
        if not(1 < mail.index('@') < mail.index('.') - 1 and mail.index('.') + 1 < len(mail)):
            message = 'Неверная почта'
    else:
        message = 'Неверная почта'

    if password == password2:
        if not any([x in password for x in string.digits]) or not any(
                [x in password for x in string.ascii_letters]) or len(password) < 5:
            if message != '':
                message = 'Неверные почта и пароль'
            else:
                message = 'Неверный пароль'
    else:
        message = 'Пароли не совпадают'

    return message

def check_pass_and_mail(mail, password) -> str:
    for i in users:
        if mail == i[1]:
            if password ==  i[2]:
                return ''
    return 'Неверные почта или пароль'



def openUsers() -> list:
    with open('static/csv/users.csv', 'r', encoding='UTF-8') as f:
        reader = csv.reader(f)
        users = []
        for row in reader:
            users.append(row[0].split(';'))
    return users

def addUser(name, mail, password):
    global users
    with open("static/csv/users.csv", mode="w", encoding='utf-8') as f:
        file_writer = csv.writer(f, delimiter=";", lineterminator="\n")
        for i in users:
            file_writer.writerow(i)
        file_writer.writerow([name, mail, password])
    users = openUsers()


@app.route('/api/ticker/<name>', methods=['get'])
def rest_get_ticker(name):
    name = name.upper()
    p = pd.read_csv('static/csv/d100.csv')
    if name in p.keys():
        data, diff = create_HHTP_tablet(name)  # Подготовка данных для HTTP графика
        create_plots.save_plot_by_name(name)  # Создание графика цен
        create_plots.save_predict_by_name(name)  # Создание графика предсказанных цен

        img1 = getImageBytes(f'static/Pictures/temp/{name}.png')
        img2 = getImageBytes(f'static/Pictures/temp/{name}1.png')

        ans = {
            'name': name,
            'data': data,
            'diff': diff,
            'url-plot1': img1,
            'url-plot2': img2
        }
        return dumps(ans)
    else:
        return dumps({'error': 'Name not found'})


def getImageBytes(filePath):
    pil_img = Image.open(filePath, mode='r')  # reads the PIL image
    byte_arr = io.BytesIO()
    pil_img.save(byte_arr, format='PNG')  # convert the PIL image to byte array
    encoded_img = base64.encodebytes(byte_arr.getvalue()).decode('ascii')  # encode as base64
    return encoded_img


atexit.register(goodbye) # Перехват выхода из приложения



if __name__ == '__main__':
    # import parser
    # import recommendation
    users = openUsers()
    cur_user = 'Аноним'
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)