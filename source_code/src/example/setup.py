# from flask import Flask
#
# from models import db
# from app import bp
# # import config - docker
#
# # ADDED MINE
# DATABASE_CONNECTION_URI = f'postgresql+psycopg2://{"mestrehackao"}:{"psqltest"}@{"localhost"}:{"5432"}/{"flaskdb"}'
#
#
# def create_app():
#     flask_app = Flask(__name__)
#     # flask_app.config['SQLALCHEMY_DATABASE_URI'] = config.DATABASE_CONNECTION_URI
#     flask_app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_CONNECTION_URI
#     flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#     flask_app.app_context().push()
#     flask_app.register_blueprint(bp)
#     db.init_app(flask_app)
#     db.create_all()
#     return flask_app