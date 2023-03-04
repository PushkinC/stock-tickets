from flask import Flask, render_template, app, url_for
import csv
import matplotlib.pyplot as plt
import pandas as pd
import atexit
import os

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

@app.route('/ticket/<name>')
def ticket(name):

    save_plot_by_name(name)

    return render_template('ticket.html', name=name)



d100 = pd.read_csv('static/csv/d100.csv')

def save_plot_by_name(name):
    fig = plt.figure(figsize=(12, 5))
    plt.plot([i for i in range(len(d100[name]))], d100[name])
    plt.fill_between([i for i in range(len(d100[name]))], d100[name])
    plt.legend()
    plt.title(name)
    plt.savefig(f'static/Pictures/temp/{name}.png')
    plt.savefig(f'static/Pictures/temp/{name}1.png')


def goodbye():
    path = 'static/Pictures/temp'

    f = os.listdir(path)
    for i in f:
        os.remove(path + '/' + i)


atexit.register(goodbye)




if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')







