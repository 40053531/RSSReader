from flask import Flask, render_template, redirect, url_for, request, g, session
import feedparser, sqlite3, bcrypt

app = Flask(__name__)
app.secret_key = "1\xa5b\xeb\x1c\xdc\xbf>n%CN\x8a\x14\xbe\x0b\xc8ek\xf6:\cbd'O"
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
  db = get_db()
  sql = "SELECT feed FROM UserFeeds ORDER by RANDOM() LIMIT 1"
  db.text_factory = str
  feedlist = []
  for row in db.cursor().execute(sql):
    url = str(row[0])
  print url
  rndfeed = feedparser.parse(url)
  sql = "SELECT feed, COUNT(*) as count FROM UserFeeds GROUP BY feed ORDER BY count DESC LIMIT 5"
  for row in db.cursor().execute(sql):
    feedlist.append(str(row[0]))
  print feedlist
  return render_template('home.html',rndfeed=rndfeed,feedlist=feedlist),200

@app.route('/addfeed/', methods=['GET','POST'])
def addfeed():
  try:
    error = None
    db = get_db()
    user = str(session['User'])
    if  request.method == 'POST':
      logFeed = request.form['rssAddress']
      feed = feedparser.parse(logFeed)
      print feed.bozo
      if (feed.bozo == 1):
        error = "The url was not a RSS feed. Please try again"
      else:
        sql = "INSERT INTO UserFeeds (user, feed) VALUES ('"+user+"', '"+logFeed+"')"
        db.cursor().execute(sql)
        db.commit()
        return redirect(url_for('root'))
    return render_template('addfeed.html', error=error),200
  except KeyError:
    return redirect(url_for('root'))

@app.route('/rmfeed/', methods=['GET','POST'])
def rmfeed():
  db = get_db()
  feeds =[]
  user = str(session['User'])
  try:
    if request.method =='POST':
      print "POST"
      feed = request.form['rssAddress']
      print feed
      sql = "DELETE FROM UserFeeds WHERE user = '"+ user +"' AND feed = '"+ feed +"'"
      print sql
      db.cursor().execute(sql)
      db.commit()
      return redirect(url_for('root'))
    else:
      sql = "SELECT feed FROM UserFeeds WHERE user ='"+user+"'"
      if(len(db.cursor().execute(sql).fetchall())!=0):
        for row in db.cursor().execute(sql):
          feeds.append(str(row)[3:-3])

      return render_template('rmfeed.html',feeds=feeds)
  except KeyError:
    return redirect(url_for('root'))


@app.route('/feed/',methods=['GET','POST'])
def feed():
    db = get_db()
    feeds = []
    entries = []
    db.text_factory = str
    style = True
    if (request.method == 'POST'):
      if (request.form['btn'] == "block"):
        style = True
      else:
        style = False
      try:
        sql = "SELECT feed FROM UserFeeds WHERE user ='"+str(session['User'])+"'"
        for row in db.cursor().execute(sql):
          feeds.append(str(row)[2:-3])
        for url in feeds:
          entries.extend(feedparser.parse(url).entries)
          print url

        entries_sorted = sorted(entries, key=lambda e: e.published_parsed, reverse=True)
        return render_template('feed.html',entries=entries_sorted, style=style),200
      except:
        return render_template('feed.html'),200

    else:
      try:
        sql = "SELECT feed FROM UserFeeds WHERE user ='"+str(session['User'])+"'"

        if(len(db.cursor().execute(sql).fetchall())!=0):
          for row in db.cursor().execute(sql):
            feeds.append(str(row)[2:-3])
          for url in feeds:
            entries.extend(feedparser.parse(url).entries)
            print url

          entries_sorted = sorted(entries, key=lambda e: e.published_parsed,
          reverse=True)
          return render_template('feed.html',entries=entries_sorted, style=style),200
      except KeyError:
        return render_template('feed.html'),200

    return render_template('feed.html'),200

@app.route('/login/', methods=['GET','POST'])
def login():
  error = None
  db = get_db()
  dbpass = None
  if request.method == 'POST':
    logUser = request.form['username']
    logPass = request.form['password']
    sql = "SELECT user FROM Users WHERE user ='"+logUser+"'"
    if(len(db.cursor().execute(sql).fetchall()) == 0):
       error = 'Username not found, Please try again'
    else:
      sql = "SELECT password FROM Users WHERE user ='"+logUser+"'"
      for row in db.cursor().execute(sql):
        dbPass = str(row)[3:-3]
      if (dbPass != bcrypt.hashpw(logPass.encode('utf-8'),dbPass)):
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

@app.route('/signup/', methods=['GET','POST'])
def signup():
  error = None
  db = get_db()
  if request.method =='POST':
    signUser = request.form['username']
    sql = "SELECT user FROM Users WHERE user ='"+signUser+"'"
    if(len(db.cursor().execute(sql).fetchall()) != 0):
      error = 'Username already taken, try another name'
    else:
      pwhash = bcrypt.hashpw(request.form['password'], bcrypt.gensalt())
      sql = "INSERT INTO Users(user,password) VALUES ('"+signUser+"', '"+pwhash+"')"
      db.cursor().execute(sql)
      db.commit()
      return redirect(url_for('root'))
  return render_template('signup.html', error=error)

@app.errorhandler(404)
def page_not_found(error):
  return render_template('404.html')

if __name__ == "__main__":
  app.run(host='0.0.0.0', debug=True)
