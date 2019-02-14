import cherrypy
import os
import redis
import datetime
import json

from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader('templates'))


def get_yesterday_data():
        conn = redis.Redis(host='localhost', port=6379, db=0)
        today = datetime.datetime.now().date()
        yesterday = today - datetime.timedelta(1)

        year = str(yesterday.year)[2:]
        month = yesterday.month
        if month < 10:
            month = "0%s" % month
        day = yesterday.day
        if day < 10:
            day = "0%s" % day

        top_10_high_stocks = []

        key = "equity-bhavcopy-%s%s%s" % (day, month, year)
        data = conn.get(key)
        return {
            "data": data, "day": day, "month": month,
            "year": year, "key": key, "conn": conn,
            "today": today, "yesterday": yesterday}

class MyApplication(object):
    @cherrypy.expose
    def index(self):
        yesterday_data = get_yesterday_data()
        data = yesterday_data['data']
        day = yesterday_data['day']
        month = yesterday_data['month']
        year = yesterday_data['year']
        conn = yesterday_data['conn']
        key = yesterday_data['key']
        today = yesterday_data['today']
        yesterday = yesterday_data['yesterday']

        top_10_high_stocks = []

        if data:
            data = json.loads(conn.get(key).decode('utf-8'))

            high_data = {}
            for x in data.keys():
                high = float(data[x]['high'])
                if high not in high_data:
                    high_data[high] = []
                high_data[high].append(data[x])

            high_arr = list(high_data.keys())
            high_arr.sort()
            high_arr.reverse()

            print("high_arr")
            print(high_arr[:10])

            i = 0
            for x in high_arr:
                if i >= 10:
                    break
                for item in high_data[x]:
                    top_10_high_stocks.append(item)
                    print(x)
                    i += 1

            print("top_10_high_stocks")
            print(top_10_high_stocks)



        tmpl = env.get_template('index.html')
        return tmpl.render(data=data, yesterday=yesterday, top_10_high_stocks=top_10_high_stocks)

    @cherrypy.expose
    def search(self, name=None):
        yesterday_data = get_yesterday_data()
        data = yesterday_data['data']
        day = yesterday_data['day']
        month = yesterday_data['month']
        year = yesterday_data['year']
        conn = yesterday_data['conn']
        key = yesterday_data['key']

        name = name.lower()

        results = []

        if data:
            data = json.loads(conn.get(key).decode('utf-8'))

            i = 0
            for x in data.keys():
                if i >= 10:
                    # limit to 10 results
                    break
                if name in data[x]['name'].lower():
                    results.append(data[x])
                    i += 1

        tmpl = env.get_template('search_results.html')
        return tmpl.render(data=results, name=name)


conf = {
    '/':
        {
            'tools.staticdir.root': os.path.dirname(os.path.abspath(__file__))
    },
    '/static': {
      'tools.staticdir.on': True,
      'tools.staticdir.dir': 'static'
    }
}

if __name__ == '__main__':
    cherrypy.quickstart(MyApplication(), config=conf)