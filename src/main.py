from flask import Flask, render_template, redirect, url_for, request, g, session
import feedparser, sqlite3

app = Flask(__name__)
app.secret_key = 'One day this might look more secret'
db_location = 'var/rssreader.db'


def get_db():
  db = getattr(g,'db',None)
  if db is None:
    db = sqlite3.connect(db_location)
    g.db = db
  return db

@app.teardown_appcontext
def close_db_connection(exeception):
  db= getattr(g,'db',None)
  if db is not None:
     db.close()

def init_db():
  with app.app_context():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
      db.cursor().executescript(f.read())
    db.commit()


@app.route('/')
def root():
  return render_template('home.html'),200

@app.route('/feed/')
def feed():
  db = get_db()
  feeds = []
  entries = []
  db.text_factory = str
  try:
    sql = "SELECT feed FROM UserFeeds WHERE user ='"+str(session['User'])+"'"
    if(len(db.cursor().execute(sql).fetchall())!=0):
      for row in db.cursor().execute(sql):
        feeds.append(str(row)[2:-3])

      for url in feeds:
        entries.extend(feedparser.parse(url).entries)

      entries_sorted = sorted(entries, key=lambda e: e.published_parsed, reverse=True)

      return render_template('feed.html',entries=entries_sorted),200
  except KeyError:
    return render_template('feed.html'),200

@app.route('/login/', methods=['GET','POST'])
def login():
  error = None
  db = get_db()
  if request.method == 'POST':
    logUser = request.form['username']
    logPass = request.form['password']
    sql = "SELECT user FROM Users WHERE user ='"+logUser+"'"
    if(len(db.cursor().execute(sql).fetchall()) == 0):
       error = 'Username not found, Please try again'
    else:
      sql = "SELECT password FROM Users WHERE user ='"+logUser+"' AND password='"+logPass+"'"
      if(len(db.cursor().execute(sql).fetchall()) ==0):
        error = 'Password was incorrect, Please try again'
      else:
        session['logged_in']= True
        session['User']= logUser
        return redirect(url_for('root'))
  return render_template('login.html',error=error)

@app.route('/logout/')
def logout():
  session.clear()
  return redirect(url_for('root'))




if __name__ == "__main__":
  app.run(host='0.0.0.0', debug=True)
