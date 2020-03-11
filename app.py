from flask import Flask, render_template

app=Flask(__name__)

@app.route('/')
def index():
  return render_template('pages/homepage.html')

@app.route('/clubcollection')
def get_all_games():
  return render_template('pages/clubcollection.html')

@app.route('/allmembers')
def get_all_members():
  return render_template('pages/members.html')

@app.route('/allevents')
def get_all_events():
  return render_template('pages/events.html')



if __name__ == '__main__':
    app.run()