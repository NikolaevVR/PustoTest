from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()

# Для связи многие-ко-многим между Player и Boost
player_boost_association = Table(
    'player_boost', Base.metadata,
    Column('player_id', Integer, ForeignKey('players.id')),
    Column('boost_id', Integer, ForeignKey('boosts.id')),
    Column('obtained_at', DateTime, default=datetime.now())
)


class Player(Base):
    __tablename__ = 'players'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))  # Связь с пользователем
    first_login = Column(DateTime, nullable=True)  # Дата первого входа
    points = Column(Integer, default=0)  # Баллы за ежедневные входы
    last_daily_login = Column(DateTime, nullable=True)

    # Связь с бустами через ассоциативную таблицу
    boosts = relationship("Boost", secondary=player_boost_association, back_populates="players")

    def mark_first_login(self):
        if not self.first_login:
            self.first_login = datetime.utcnow()

    def add_daily_points(self):
        today = DateTime.today()

        # Начисляем баллы только если сегодня еще не начисляли
        if self.last_daily_login != today:
            self.points += 10
            self.last_daily_login = today
            return True
        return False


class BoostType(enum.Enum):
    SPEED = "speed"
    DEFENSE = "defense"
    ATTACK = "attack"


class Boost(Base):
    __tablename__ = 'boosts'

    id = Column(Integer, primary_key=True)
    boost_type = Column(enum.Enum(BoostType))  # Тип буста
    effect = Column(Float)  # Эффект буста (например, множитель 1.5)
    source = Column(String)  # Источник получения ('level' или 'manual')

    # Связь с игроками через ассоциативную таблицу
    players = relationship("Player", secondary=player_boost_association, back_populates="boosts")