import os
from flask_admin import Admin
from models import db, People, Planets, Users, Favorites
from flask_admin.contrib.sqla import ModelView

# Clase personalizada para mostrar favoritos
class FavoriteView(ModelView):
    column_list = ('id', 'user_id', 'people_id', 'planet_id')
    form_columns = ('user_id', 'people_id', 'planet_id')

def setup_admin(app):
    app.secret_key = os.environ.get('FLASK_APP_KEY', 'sample key')
    app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
    admin = Admin(app, name='4Geeks Admin', template_mode='bootstrap3')

    # Registro de modelos en el admin
    admin.add_view(ModelView(Users, db.session))
    admin.add_view(ModelView(People, db.session))
    admin.add_view(ModelView(Planets, db.session))
    admin.add_view(FavoriteView(Favorites, db.session))
