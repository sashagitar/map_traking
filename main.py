from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from models import Base, Route, RoutePoint, Database
from typing import List
import os
import dotenv

# Загрузка переменных из .env
dotenv.load_dotenv()

# Конфигурация приложения Flask
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'supersecretkey')

# Определяем URI для подключения к базе данных
DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///routes.db')

# Создание движка SQLAlchemy
engine = create_engine(DATABASE_URI)

# Создание сессии для работы с базой данных
Session = sessionmaker(bind=engine)
session = Session()

# Инициализация базы данных
Database.initialize(engine)

@app.route('/')
def index() -> str:
    """
    Главная страница приложения. Отображает список маршрутов.
    :return: HTML-шаблон с маршрутом.
    """
    try:
        routes: List[Route] = session.query(Route).all()
    except Exception as e:
        session.rollback()
        flash(f"Ошибка при загрузке маршрутов: {str(e)}", "error")
        routes = []
    return render_template('index.html', routes=routes)

@app.route('/route/<int:route_id>')
def edit_route(route_id: int) -> str:
    """
    Страница редактирования маршрута. Отображает карту с точками маршрута.
    :param route_id: ID маршрута для редактирования.
    :return: HTML-шаблон с редактированием маршрута.
    """
    try:
        route: Route = session.query(Route).get(route_id)
        points = session.query(RoutePoint).filter_by(route_id=route_id).order_by(asc(RoutePoint.id)).all()
        point_dicts = [point.to_dict() for point in points]
    except Exception as e:
        session.rollback()
        flash(f"Ошибка при загрузке маршрута: {str(e)}", "error")
        route, point_dicts = None, []

    return render_template('edit_route.html', route=route, points=points, point_dicts=point_dicts)

@app.route('/add_route', methods=['POST'])
def add_route() -> str:
    """
    Обработчик для добавления нового маршрута.
    :return: Перенаправление на главную страницу.
    """
    name: str = request.form.get('name')
    if name:
        try:
            new_route = Route(name=name)
            session.add(new_route)
            session.commit()
        except Exception as e:
            session.rollback()
            flash(f"Ошибка при добавлении маршрута: {str(e)}", "error")
    return redirect(url_for('index'))

@app.route('/delete_route/<int:route_id>', methods=['POST'])
def delete_route(route_id: int) -> str:
    """
    Обработчик для удаления маршрута.
    :param route_id: ID маршрута для удаления.
    :return: Перенаправление на главную страницу.
    """
    try:
        route = session.query(Route).get(route_id)
        session.delete(route)
        session.commit()
    except Exception as e:
        session.rollback()
        flash(f"Ошибка при удалении маршрута: {str(e)}", "error")
    return redirect(url_for('index'))

@app.route('/add_point', methods=['POST'])
def add_point() -> str:
    """
    Обработчик для добавления новой точки маршрута или редактирования существующей точки.
    :return: Перенаправление на страницу редактирования маршрута.
    """
    try:
        route_id = int(request.form.get('route_id'))
        point_id = request.form.get('point_id')
        point_type = request.form.get('point_type')
        latitude = float(request.form.get('latitude'))
        longitude = float(request.form.get('longitude'))

        if point_id:
            update_point(point_id, latitude, longitude)
        else:
            add_new_point(route_id, point_type, latitude, longitude)

        session.commit()
    except Exception as e:
        session.rollback()
        flash(f"Ошибка при добавлении точки: {str(e)}", "error")

    return redirect(url_for('edit_route', route_id=route_id))

def update_point(point_id: str, latitude: float, longitude: float):
    """
    Обновление существующей точки маршрута.
    """
    existing_point = session.query(RoutePoint).get(point_id)
    if existing_point:
        existing_point.latitude = latitude
        existing_point.longitude = longitude

def add_new_point(route_id: int, point_type: str, latitude: float, longitude: float):
    """
    Добавление новой точки маршрута.
    """
    existing_points = session.query(RoutePoint).filter_by(route_id=route_id).count()
    if existing_points == 0:
        point_type = 'start'
    
    if point_type == 'start':
        update_or_create_point(route_id, 'start', latitude, longitude)
    elif point_type == 'end':
        update_or_create_point(route_id, 'end', latitude, longitude)
    else:
        handle_intermediate_point(route_id, latitude, longitude)

def update_or_create_point(route_id: int, point_type: str, latitude: float, longitude: float):
    """
    Обновление или создание точки типа 'start' или 'end'.
    """
    existing_point = session.query(RoutePoint).filter_by(route_id=route_id, point_type=point_type).first()
    if existing_point:
        existing_point.latitude = latitude
        existing_point.longitude = longitude
    else:
        new_point = RoutePoint(route_id=route_id, point_type=point_type, latitude=latitude, longitude=longitude)
        session.add(new_point)

def handle_intermediate_point(route_id: int, latitude: float, longitude: float):
    """
    Обработка добавления промежуточной точки маршрута.
    """
    end_point = session.query(RoutePoint).filter_by(route_id=route_id, point_type='end').first()
    if end_point:
        old_end_latitude = end_point.latitude
        old_end_longitude = end_point.longitude

        end_point.point_type = 'point'
        end_point.latitude = latitude
        end_point.longitude = longitude
        session.commit()

        new_end = RoutePoint(route_id=route_id, point_type='end', latitude=old_end_latitude, longitude=old_end_longitude)
        session.add(new_end)
    else:
        new_point = RoutePoint(route_id=route_id, point_type='point', latitude=latitude, longitude=longitude)
        session.add(new_point)

@app.route('/delete_point/<int:point_id>', methods=['POST'])
def delete_point(point_id: int) -> str:
    """
    Обработчик для удаления точки маршрута.
    :param point_id: ID точки маршрута для удаления.
    :return: Перенаправление на страницу редактирования маршрута.
    """
    try:
        point = session.query(RoutePoint).get(point_id)
        route_id = point.route_id
        session.delete(point)
        session.commit()
    except Exception as e:
        session.rollback()
        flash(f"Ошибка при удалении точки: {str(e)}", "error")

    return redirect(url_for('edit_route', route_id=route_id))

if __name__ == '__main__':
    app.run(debug=True)
