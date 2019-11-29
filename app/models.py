from datetime import datetime
from app import db, login 
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

	# la classe UserMixin contiene un po' di cose generiche che vanno bene per le tabelle utenti. come in questo caso.
class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64), index=True, unique=True)
	email = db.Column(db.String(120), index=True, unique=True)
	password_hash = db.Column(db.String(128))

	# repr serve solo ad aiutare python a capire come leggere le info del database
	def __repr__(self):
		return '<User {}>'.format(self.username)

	def set_password(self, password):
		self.password_hash = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.password_hash, password)


@login.user_loader
def load_user(id):
	return User.query.get(int(id))