from . import user

all_modules = (user,)


def setup_app(app):
    for module in all_modules:
        module.setup_app(app)
