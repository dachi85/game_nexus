from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///game_nexus.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'super-secret-key'

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    platform = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f'<Game {self.title}>'


@app.route('/')
def index():
    games_list = Game.query.all()
    return render_template('index.html', games=games_list)



@app.route('/add', methods=['GET', 'POST'])
def add_game():
    if request.method == 'POST':
        title = request.form.get('title')
        platform = request.form.get('platform')
        status = request.form.get('status')


        new_game = Game(title=title, platform=platform, status=status)
        db.session.add(new_game)
        db.session.commit()

        return redirect(url_for('index'))
    return render_template('add_game.html')


if __name__ == '__main__':
    app.run(debug=True)