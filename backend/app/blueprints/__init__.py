from .auth import blueprint as auth_blueprint
from .item import blueprint as item_blueprint

blueprints = (auth_blueprint, item_blueprint)
