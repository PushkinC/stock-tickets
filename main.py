from flask import Flask, render_template, app, url_for
import csv
import matplotlib.pyplot as plt
import pandas as pd
import atexit
import os
import create_plots

app = Flask(__name__)

PORT = 8080
HOST = '127.0.0.1'

@app.route('/')
@app.route('/index')
def index():
    global PORT, HOST
    tablo = []
    buy = []
    sale = []
    try:
        with open('static/csv/tablo.csv', 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                tablo.append(row)

        with open('static/csv/buy.csv', 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                buy.append(row)

        with open('static/csv/sale.csv', 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                sale.append(row)

        tablo = tablo[1:]
        buy = buy[1:]
        sale = sale[1:]


    except Exception as ex:
        print(ex)
        print('Я в открытии данных для таблиц!!!!!!')


    return render_template('index.html', tablo=tablo, buy=buy, sale=sale,
                           host=HOST, port=PORT)





def create_HHTP_tablet(name):
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
def ticket(name):
    data, diff = create_HHTP_tablet(name)
    create_plots.save_plot_by_name(name)
    create_plots.save_predict_by_name(name)

    return render_template('ticket.html', name=name, data=data, diff=diff)




def goodbye():
    path = 'static/Pictures/temp'

    f = os.listdir(path)
    for i in f:
        os.remove(path + '/' + i)


atexit.register(goodbye)




if __name__ == '__main__':
    if input() == 'yes':
        import parser

    if input() == 'yes':
        import recommendation
    app.run(port=8080, host='127.0.0.1')







