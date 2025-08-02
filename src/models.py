from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, DateTime, ForeignKey
from datetime import datetime
from sqlalchemy.orm import relationship, Mapped, mapped_column

db = SQLAlchemy()

class People(db.Model):
    __tablename__ = "people"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    height: Mapped[int] = mapped_column(nullable=True)
    eye_color: Mapped[str] = mapped_column(String(50))
    gender: Mapped[str] = mapped_column(String(50))

    # Relación inversa con Favorites
    favorites: Mapped[list["Favorites"]] = relationship("Favorites", back_populates="people")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "height": self.height,
            "eye_color": self.eye_color,
            "gender": self.gender
        } 
    
class Users(db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(50), nullable=True)
    last_name: Mapped[str] = mapped_column(String(50), nullable=True)
    email: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(80), nullable=False)
    subscription_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    favorites: Mapped[list["Favorites"]] = relationship(
        "Favorites",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    def serialize(self):
        return {
            "id": self.id,
            "name": self.first_name,
            "email": self.email
        }

    def all_user_favorites(self):
        results_favorites = [fav.serialize() for fav in self.favorites]
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "favorites": results_favorites
        }

    
class Planets(db.Model):
    __tablename__ = "planets"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    climate: Mapped[str] = mapped_column(String(50))
    gravity: Mapped[str] = mapped_column(String(50))
    terrain: Mapped[str] = mapped_column(String(50))

    # Relación inversa con Favorites
    favorites: Mapped[list["Favorites"]] = relationship("Favorites", back_populates="planet")
    
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "climate": self.climate,
            "gravity": self.gravity,
            "terrain": self.terrain
        }        

class Vehicles(db.Model):
    __tablename__ = "vehicles"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    model: Mapped[str] = mapped_column(String(50))
    crew: Mapped[str] = mapped_column(String(50))
    passengers: Mapped[str] = mapped_column(String(50))
    
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "model": self.model,
            "crew": self.crew,
            "passengers": self.passengers
        }    

class Favorites(db.Model):
    __tablename__ = "favorites"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    people_id: Mapped[int | None] = mapped_column(ForeignKey("people.id"), nullable=True)
    planet_id: Mapped[int | None] = mapped_column(ForeignKey("planets.id"), nullable=True)

    user: Mapped["Users"] = relationship("Users", back_populates="favorites")
    people: Mapped["People"] = relationship("People", back_populates="favorites")
    planet: Mapped["Planets"] = relationship("Planets", back_populates="favorites")

    def serialize(self):
        result = {
            "id": self.id
        }

        if self.people_id and self.people:
            result["resource_id"] = self.people_id
            result["type"] = "people"
            result["name"] = self.people.name

        elif self.planet_id and self.planet:
            result["resource_id"] = self.planet_id
            result["type"] = "planet"
            result["name"] = self.planet.name

        return result


# Para el diagrama ER
# from eralchemy2 import render_er

# try:
#     render_er(db.Model, "diagram.png")
#     print("Success! Check the diagram.png file")
# except Exception as e:
#     print("There was a problem generating the diagram")
#     raise e
