from flask import *
from db.db_handler import DB
from flask_httpauth import HTTPBasicAuth
import os
import json

app = Flask(__name__, template_folder='template')
auth = HTTPBasicAuth()
db = DB()
categories = ['None'] + db.get_from_db("""SELECT DISTINCT category FROM news""").iloc[:, 0].values.tolist()
sources = ['None'] + db.get_from_db("""SELECT DISTINCT source_name FROM news""").iloc[:, 0].values.tolist()
db.connection.close()
users_dict = {}


@app.route('/')
def index():
    category = request.args.get('category', default='None', type=str)
    source = request.args.get('source', default='None', type=str)
    db = DB()
    news = db.get_from_db(f"""SELECT *
                                    FROM (
                                        SELECT *, ROW_NUMBER() OVER (PARTITION BY category ORDER BY published_at DESC) AS n
                                        FROM news
                                        WHERE TRUE {"AND category = '" + category + "'" if category != 'None' else ''} 
                                                 {"AND source_name = '" + source + "'" if source != 'None' else ''}
                                        ORDER BY published_at DESC
                                    ) AS x
                                    WHERE n <= 5""")
    news_list = []
    db.connection.close()
    for cat in news['category'].unique():
        news_list.append(news[news['category'] == cat].values.tolist())

    return render_template('home.html', news=news_list, categories=categories,
                           sources=sources, curr_category=category, curr_source=source)


@app.route('/show_all/<category>/<page>')
def show_all(category, page):
    source = request.args.get('source', default='None', type=str)
    if page == '0':
        return redirect(url_for('show_all', category=category, page=1, source=source))
    db = DB()
    news = db.get_from_db(f"""SELECT *
                                        FROM news
                                        WHERE {"category = '" + category + "'"} 
                                        {"AND source_name = '" + source + "'" if source != 'None' else ''}
                                        ORDER BY published_at DESC
                                        LIMIT 10
                                        OFFSET {(int(page) - 1) * 10}""").values.tolist()
    db.connection.close()
    print(len(news))
    if len(news) == 0:
        return redirect(url_for('show_all', category=category, page=int(page) - 1, source=source))
    return render_template('all_news.html', category=category, news=news, page=page, int=int, sources=sources, source=source)


@auth.verify_password
def verify_password(username, password):
    db = DB()
    user = db.get_from_db(f"""SELECT *
                                        FROM admin
                                        WHERE login = '{username}'""")
    db.connection.close()
    if len(user) == 0 or user['password'].values[0] != password:
        return None
    else:
        return username


@app.route('/admin')
@auth.login_required
def admin_panel():
    db = DB()
    ids = db.get_from_db(f"""SELECT id FROM data_sources""").values.tolist()
    db.connection.close()
    ids = list(map(lambda x: x[0], ids))

    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    ROOT_DIR = '/'.join(ROOT_DIR.split('\\')[:-2]) + '/model/models'
    models = []
    for file in os.scandir(ROOT_DIR):
        models.append('/'.join(file.path.replace("\\", '/').split('/')[-3:]))
    return render_template('admin_panel.html', ids=ids, files=models)


@app.route('/admin_message')
@auth.login_required
def admin_message():
    type = request.args.get('type', default='None', type=str)
    db = DB()
    if type == 'Get all statuses':
        title = 'statuses'
        messages = db.get_from_db(f"""SELECT *
                                    FROM data_sources""").values.tolist()
    if type == 'Update status':
        title = 'Response'
        id = request.args.get('source_id', default='None', type=str)
        status = request.args.get('status', default='None', type=str)
        try:
            messages = db.execute_query(f"""UPDATE data_sources SET used={status} WHERE id='{id}';""")

            messages = [f'data source {id} now has status {status}']
        except Exception as e:
            messages = [str(e.__traceback__.tb_lineno) + str(e)]
    db.connection.close()
    if type == 'Update model':
        title = 'Response'
        model_name = request.args.get('model_name', default='None', type=str)
        file = request.args.get('file', default='None', type=str)

        try:
            ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
            ROOT_DIR = '/'.join(ROOT_DIR.split('\\')[:-2]) + '/model'
            with open(ROOT_DIR + '/version.json') as f:
                versions = json.load(f)
            versions[model_name] = file
            with open(ROOT_DIR + '/version.json', 'w') as f:
                json.dump(versions, f)
            messages = [f'model {model_name} set to {file}']
        except Exception as e:
            messages = [str(e.__traceback__.tb_lineno) + str(e)]

    return render_template('admin_message.html', title=title, messages=messages)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
