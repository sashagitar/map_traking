from sqlalchemy import Column, Integer, String, Numeric, Enum, ForeignKey, create_engine
from sqlalchemy.orm import relationship, declarative_base, sessionmaker
from sqlalchemy.sql import func
from sqlalchemy.inspection import inspect

Base = declarative_base()

class Route(Base):
    __tablename__ = 'Routes'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    points = relationship("RoutePoint", back_populates="route", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name
        }

class RoutePoint(Base):
    __tablename__ = 'RoutePoints'
    id = Column(Integer, primary_key=True, autoincrement=True)
    route_id = Column(Integer, ForeignKey('Routes.id'), nullable=False)
    point_type = Column(Enum('start', 'point', 'end', name='point_type'), nullable=False)
    latitude = Column(Numeric(10, 8), nullable=False)
    longitude = Column(Numeric(11, 8), nullable=False)
    route = relationship("Route", back_populates="points")

    def to_dict(self):
        return {
            'id': self.id,
            'route_id': self.route_id,
            'point_type': self.point_type,
            'latitude': float(self.latitude),
            'longitude': float(self.longitude)
        }

class Database:
    @staticmethod
    def initialize(engine):
        inspector = inspect(engine)
        if not inspector.get_table_names():
            Base.metadata.create_all(engine)
            print('''
                  +++++++++++++++++++++
                  +База данных создана+
                  +++++++++++++++++++++
                  ''')
        else:
            print('''
                  ++++++++++++++++++++++++
                  +Таблицы уже существуют+
                  ------------------------
                  +++Данные не тронуты +++
                  ++++++++++++++++++++++++
                  ''')

if __name__ == "__main__":
    DATABASE_URI = 'mysql+pymysql://routes_db:12345@localhost/routes_db'
    engine = create_engine(DATABASE_URI)
    Database.initialize(engine)
