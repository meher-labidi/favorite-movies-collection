from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests

api_key = "your key"
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///Movies_data.db"
db = SQLAlchemy(app)
Bootstrap(app)
class Movies(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True)
    year = db.Column(db.Integer)
    description = db.Column(db.String(500))
    rating = db.Column(db.Float, nullable=True)
    ranking = db.Column(db.Integer, nullable=True)
    review = db.Column(db.String(250), nullable=True)
    img_url = db.Column(db.String(250))


with app.app_context():
    db.create_all()

class RateMovieForm(FlaskForm):
    rating = StringField("Your Rating Out of 10 e.g. 7.5")
    review = StringField("Your Review")
    submit = SubmitField("Done")
class Add(FlaskForm):
    title = StringField("Movie Title", validators=[DataRequired()])
    submit = SubmitField("Add Movie")

@app.route("/")
def home():

    all_Movies = Movies.query.order_by(Movies.rating).all()
    for i in range(len(all_Movies)):
        all_Movies[i].ranking = len(all_Movies)-i
        db.session.commit()
    return render_template("index.html", movies=all_Movies)

@app.route("/edit", methods=["GET", "POST"])
def rate_movie():
    form = RateMovieForm()
    movie_id = request.args.get("id")
    movie = Movies.query.get(movie_id)
    if form.validate_on_submit():
        movie.rating = float(form.rating.data)
        movie.review = form.review.data
        db.session.commit()
        return redirect(url_for('home'))

    return render_template("edit.html", movie=movie, form=form)
@app.route("/delete")
def delete():
    movie_id = request.args.get("id")
    movie_to_delete = Movies.query.get(movie_id)
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for("home"))
@app.route("/add",  methods=["GET", "POST"])
def add():
    form = Add()
    if form.validate_on_submit():
        movie_title = form.title.data
        response = requests.get("https://api.themoviedb.org/3/search/movie", params={"api_key":api_key, "query": movie_title})
        data = response.json()["results"]
        return render_template("select.html", option=data)
    return render_template("add.html", form=form)
@app.route("/find")
def find_movie():
    movie_api_id = request.args.get("id")

    if movie_api_id:
        movie_api_url = f"{'https://api.themoviedb.org/3/movie'}/{movie_api_id}"
        response = requests.get(movie_api_url, params={"api_key": api_key, "language": "en-US"})
        data = response.json()
        print(data)
        new_movie = Movies(
            title=data["title"],
            year=data["release_date"].split("-")[0],
            img_url=f"{'https://image.tmdb.org/t/p/w500'}{data['poster_path']}",
            description=data["overview"],
            rating=0.0,
            ranking=0,
            review=""
        )

        db.session.add(new_movie)
        db.session.commit()
        return redirect(url_for('rate_movie', id=new_movie.id))
if __name__ == '__main__':
    app.run(debug=True)
