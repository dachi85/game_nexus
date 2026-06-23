from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///game_nexus.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'super-secret-key'

db = SQLAlchemy(app)
migrate = Migrate(app, db)

purchases = db.Table('purchases',
                     db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
                     db.Column('game_id', db.Integer, db.ForeignKey('game.id'), primary_key=True)
                     )


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    balance = db.Column(db.Float, default=200.0)
    games = db.relationship('Game', secondary=purchases, backref=db.backref('buyers', lazy='dynamic'))

    def __repr__(self):
        return f'<User {self.username}>'


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    platform = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False, default=0.0)
    image_url = db.Column(db.String(500), nullable=True)

    def __repr__(self):
        return f'<Game {self.title}>'


def seed_database():
    Game.query.delete()
    default_games = [
        Game(title="The Witcher 3: Wild Hunt", platform="PC / PS5 / Xbox", status="In Stock", price=39.99,
             image_url="https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/292030/header.jpg"),
        Game(title="Cyberpunk 2077", platform="PC / PS5", status="In Stock", price=59.99,
             image_url="https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/1091500/header.jpg"),
        Game(title="Grand Theft Auto V", platform="PC / PS4 / Xbox", status="In Stock", price=29.99,
             image_url="https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/271590/header.jpg"),
        Game(title="Elden Ring", platform="PC / PS5 / Xbox", status="In Stock", price=59.99,
             image_url="https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/1245620/header.jpg"),
        Game(title="Hollow Knight", platform="PC / Switch", status="In Stock", price=14.99,
             image_url="https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/367520/header.jpg"),
        Game(title="Red Dead Redemption 2", platform="PC / PS4", status="In Stock", price=59.99,
             image_url="https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/1174180/header.jpg"),
        Game(title="Minecraft", platform="PC / Mobile / Console", status="In Stock", price=26.99,
             image_url="https://assets.xboxservices.com/assets/77/cb/77cbd36c-9af0-4e36-b51c-8af3b3f2ec8c.jpg?n=Minecraft_GLP-Page-Hero-0_1080p-Format-Update_1920x1080_02.jpg"),
        Game(title="Terraria", platform="PC / Mobile / Console", status="In Stock", price=9.99,
             image_url="https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/105600/header.jpg"),
        Game(title="Stardew Valley", platform="PC / Switch / Mobile", status="In Stock", price=14.99,
             image_url="https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/413150/header.jpg"),
        Game(title="Hades", platform="PC / PS5 / Switch", status="In Stock", price=24.99,
             image_url="https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/1145360/header.jpg"),
        Game(title="Celeste", platform="PC / Switch / PS4", status="In Stock", price=19.99,
             image_url="https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/504230/header.jpg"),
        Game(title="Portal 2", platform="PC / Switch", status="In Stock", price=9.99,
             image_url="https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/620/header.jpg")
    ]
    db.session.bulk_save_objects(default_games)
    db.session.commit()


@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('register'))

    user = User.query.get(session['user_id'])
    if not user:
        session.clear()
        return redirect(url_for('register'))

    budget = request.args.get('budget')

    if budget:
        try:
            budget_value = int(budget)
            all_games = Game.query.filter(Game.price <= budget_value).all()
        except ValueError:
            all_games = Game.query.all()
            budget = None
    else:
        all_games = Game.query.all()

    return render_template('index.html', games=all_games, user_games=user.games, username=user.username,
                           balance=round(user.balance, 2), current_budget=budget)


@app.route('/buy/<int:game_id>')
def buy_game(game_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    if not user:
        session.clear()
        return redirect(url_for('register'))

    game = Game.query.get_or_404(game_id)

    if game in user.games:
        return redirect(url_for('index'))

    if user.balance >= game.price:
        user.balance -= game.price
        user.games.append(game)
        db.session.commit()
        return redirect(url_for('index'))
    else:
        return "Not enough money in your balance!"


@app.route('/add_money', methods=['POST'])
def add_money():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    if not user:
        session.clear()
        return redirect(url_for('register'))

    amount = request.form.get('amount')
    if amount:
        try:
            amount_value = float(amount)
            if amount_value > 0:
                user.balance += amount_value
                db.session.commit()
        except ValueError:
            pass

    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        if "@" not in email:
            return "Invalid email! Email must contain @."

        has_digit = any(char.isdigit() for char in password)
        if not has_digit:
            return "Invalid password! Password must contain at least one digit."

        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            return "User or Email already exists!"

        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

        session['user_id'] = new_user.id
        session['username'] = new_user.username
        return redirect(url_for('index'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('index'))
        return "Invalid credentials!"

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('register'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_database()
    app.run(debug=True)