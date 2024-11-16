from . import item, user

all_modules = (user, item)


def setup_app(app):
    for module in all_modules:
        if setup_func := getattr(module, "setup_app", None):
            setup_func(app)
