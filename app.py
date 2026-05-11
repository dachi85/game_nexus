from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)


games = [
    {'title': 'The Witcher 3', 'platform': 'PC', 'status': 'Completed'},
    {'title': 'Elden Ring', 'platform': 'PS5', 'status': 'Playing'}
]

@app.route('/')
def index():
    return render_template('index.html', games=games)

@app.route('/add', methods=['GET', 'POST'])
def add_game():
    if request.method == 'POST':
        title = request.form.get('title')
        platform = request.form.get('platform')
        status = request.form.get('status')
        games.append({'title': title, 'platform': platform, 'status': status})
        return redirect(url_for('index'))
    return render_template('add_game.html')

if __name__ == '__main__':
    app.run(debug=True)