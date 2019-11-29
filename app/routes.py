from flask import render_template, flash, redirect, url_for, request, Response
from app import app, db
from app.forms import LoginForm, RegistrationForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User 
from werkzeug.urls import url_parse
import io


@app.route('/')
@app.route('/index')
def index():
	return render_template("index.html", title='Home Page')


@app.route('/about_me')
def about_me():
	return render_template("about_me.html", title='About Me')


@app.route('/login', methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(username=form.username.data).first()
		if user is None or not user.check_password(form.password.data):
			flash('Invalid username or password')
			return redirect(url_for('login'))
		login_user(user, remember=form.remember_me.data)
		next_page = url_for('index')
		return redirect(next_page)
	return render_template("login.html", title='Sign In', form=form)


@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	form = RegistrationForm()
	if form.validate_on_submit():
		user = User(username=form.username.data, email=form.email.data)
		user.set_password(form.password.data)
		db.session.add(user)
		db.session.commit()
		flash('Congratulations, you are now a registered user!')
		flash('Please Login')
		return redirect(url_for('login'))
	return render_template('register.html', title='Register', form=form)

# ------------------------------


@app.route('/prediction_graph', methods=['GET'])
@login_required
def prediction_graph():
	render_template('prediction_graph.html', title='Graph')

@app.route('/trading')
@login_required
def trading():
	return render_template('trading.html', title='Trading')


import numpy as np
from alpha_vantage.timeseries import TimeSeries
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import pandas as pd

	# background process: visualizing the graph
@app.route('/trading_prediction', methods=['POST'])
@login_required
def trading_prediction():
	stock = request.form['namequery']
	ts = TimeSeries(key='7OMLEP6QI75IRS85', output_format='pandas')
	data, meta_data = ts.get_daily(symbol=stock, outputsize='full')
	data.to_csv('dataset.csv')
	#plot dei prezzi storici
	fig = Figure()
	ax = fig.add_subplot(1,1,1)
	ax.grid()
	ax.plot(data)
	ax.set_title(stock)

	FigureCanvasAgg(fig).print_png('app/static/api_data.png', dpi=200)
	return render_template('trading_prediction.html', title='Predict', stock_name = stock)


import tensorflow as tf 
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Dense, LSTM, Dropout
from sklearn.preprocessing import MinMaxScaler

@app.route('/predict_price', methods=['POST'])
@login_required
def predict_price():
	stock = request.form['stock_name_query']
	df = pd.read_csv('dataset.csv')
	days = 60  # GIORNI DI MEMORIA DEI LIVELLI LSTM
	epochs = 25
	multiplier = 1

	df = df[::-1]
	data_training = df[df['date']<'2019-01-01'].copy()
	data_test = df[df['date']>='2019-01-01'].copy()
	data_training_object = data_training

	data_training = data_training.drop('date', axis=1)
	scaler = MinMaxScaler(feature_range=(0,1))
	data_training = scaler.fit_transform(data_training)

	X_train = []
	y_train = []

	for i in range(days, data_training.shape[0]):
		X_train.append(data_training[i-days:i])
		y_train.append(data_training[i, 0])

	X_train, y_train = np.array(X_train), np.array(y_train)

	# Building the model

	regressior = Sequential()

	regressior.add(LSTM(units = 60, activation = 'relu', return_sequences = True, input_shape = (X_train.shape[1], 5)))
	regressior.add(Dropout(0.2))
	regressior.add(LSTM(units = 60, activation = 'relu', return_sequences = True))
	regressior.add(Dropout(0.2))
	regressior.add(LSTM(units = 80, activation = 'relu', return_sequences = True))
	regressior.add(Dropout(0.2))
	regressior.add(LSTM(units = 120, activation = 'relu'))
	regressior.add(Dropout(0.2))
	regressior.add(Dense(units = 1))

	regressior.compile(optimizer='adam', loss='mean_squared_error')
	regressior.fit(X_train, y_train, epochs=epochs, batch_size=32)

	past_x_days = data_training_object.tail(days)
	data = past_x_days.append(data_test, ignore_index= True )
	data = data.drop(['date'], axis=1)

	inputs = scaler.transform(data)

	X_test = []
	y_test = []

	for i in range(days, inputs.shape[0]):
		X_test.append(inputs[i-days:i])
		y_test.append(inputs[i, 0])

	X_test, y_test = np.array(X_test), np.array(y_test)

	# Faccio la prediction
	y_pred = regressior.predict(X_test)
	scale_factor = scaler.scale_[0]
	scale = 1/scale_factor

	y_pred = y_pred*scale * multiplier
	y_test = y_test*scale

	fig = Figure()
	ax = fig.add_subplot(1,1,1)
	ax.grid()
	ax.plot(y_test, color = 'red', label = 'Real Stock Price')
	ax.plot(y_pred, color = 'blue', label = 'Predicted Stock Price')
	ax.set_title(stock + ' Stock Price Prediction')
	ax.set_xlabel('Time (Days from 1st January, 2019)')
	ax.set_ylabel('Stock Price')
	ax.legend()
	FigureCanvasAgg(fig).print_png('app/static/prediction.png', dpi=400)

	return render_template('prediction_graph.html', title='Graph')











