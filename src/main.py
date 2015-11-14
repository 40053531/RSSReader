from flask import Flask, render_template, redirect, url_for, request, g
import feedparser, sqlite3

app = Flask(__name__)
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
  sql = "SELECT feed FROM UserFeeds WHERE user ='Neverminder'"

  for row in db.cursor().execute(sql):
    feeds.append(str(row)[2:-3])

  for url in feeds:
    entries.extend(feedparser.parse(url).entries)

  entries_sorted = sorted(entries, key=lambda e: e.published_parsed, reverse=True)

  return render_template('feed.html',entries=entries_sorted),200

if __name__ == "__main__":
  app.run(host='0.0.0.0', debug=True)
