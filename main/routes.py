from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file
from flask_login import login_required, current_user
from models import db, Dataset, ModelData, User
from forms import UploadForm, TrainModelForm
from forms.main_forms import UploadForm, TrainModelForm
import os
import pandas as pd
import matplotlib.pyplot as plt
import pickle
import uuid
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, mean_squared_error
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('main/index.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    datasets = Dataset.query.filter_by(user_id=current_user.id).all()
    models = ModelData.query.filter_by(user_id=current_user.id).all()
    return render_template('main/dashboard.html', datasets=datasets, models=models)

@main_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    form = UploadForm()
    if form.validate_on_submit():
        f = form.file.data
        filename = f"{uuid.uuid4().hex}_{f.filename}"
        filepath = os.path.join('uploads/', filename)
        f.save(filepath)
        dataset = Dataset(filename=filename, user_id=current_user.id)
        db.session.add(dataset)
        db.session.commit()
        flash('Файлът е качен успешно.')
        return redirect(url_for('main.dashboard'))
    return render_template('main/upload.html', form=form)
@main_bp.route('/train/<int:dataset_id>', methods=['GET', 'POST'])
@login_required
def train(dataset_id):
    form = TrainModelForm()
    dataset = Dataset.query.get_or_404(dataset_id)
    filepath = os.path.join('uploads/', dataset.filename)
    data = pd.read_csv(filepath)
    X = data.iloc[:, :-1]
    y = data.iloc[:, -1]

    if form.validate_on_submit():
        if len(data) < 2 or form.test_size.data >= 1.0:
            flash('Размерът на тестовия сет е твърде голям или има твърде малко данни.')
            return redirect(url_for('main.train', dataset_id=dataset_id))

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=form.test_size.data)
        model_type = form.model_type.data

        acc, mse = None, None

        if model_type == 'linear':
            model = LinearRegression()
            model.fit(X_train, y_train)
            preds = model.predict(X_test)
            mse = mean_squared_error(y_test, preds)

        elif model_type == 'logistic':
            model = LogisticRegression(max_iter=1000)
            model.fit(X_train, y_train)
            preds = model.predict(X_test)
            acc = accuracy_score(y_test, preds)

        elif model_type == 'neural':
            model = Sequential()
            model.add(Dense(64, input_shape=(X_train.shape[1],), activation='relu'))
            model.add(Dense(1, activation='sigmoid' if set(y.unique()) <= {0, 1} else 'linear'))
            model.compile(loss='binary_crossentropy' if set(y.unique()) <= {0, 1} else 'mse',
                optimizer='adam', metrics=['accuracy'])
            model.fit(X_train, y_train, epochs=100, verbose=0)
            preds = model.predict(X_test).flatten()
            if set(y.unique()) <= {0, 1}:
                preds = [1 if p > 0.5 else 0 for p in preds]
                acc = accuracy_score(y_test, preds)
            else:
                mse = mean_squared_error(y_test, preds)

        model_id = f"{uuid.uuid4().hex}.pkl"
        model_path = os.path.join('models/', model_id)
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)

        model_record = ModelData(
            model_type=model_type,
            accuracy=acc,
            mse=mse,
            file_path=model_id,
            user_id=current_user.id
        )
        db.session.add(model_record)
        db.session.commit()
        flash('Моделът е обучен успешно.')
        return redirect(url_for('main.dashboard'))

    return render_template('main/train.html', form=form, dataset=dataset)

@main_bp.route('/admin/users')
@login_required
def admin_users():
    if current_user.role != 'admin':
        flash('Нямате достъп до тази страница.')
        return redirect(url_for('main.dashboard'))
        users = db.session.query(User).all()
        return render_template('main/admin_users.html', users=users)

@main_bp.route('/plot/<filename>')
@login_required
def plot(filename):
    return send_file(os.path.join('static/plots/', filename))