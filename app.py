from flask import Flask, render_template

app=Flask(__name__)

@app.route('/')
def index():
  return render_template('pages/homepage.html')

@app.route('/clubcollection')
def get_all_games():
  return render_template('pages/clubcollection.html')



if __name__ == '__main__':
    app.run()