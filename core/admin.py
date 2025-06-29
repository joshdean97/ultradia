from flask import redirect, url_for, request
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from core.extensions import db
from core.models import User, UserDailyRecord, UserCycleEvent, Leads


# FLASK ADMIN SETUP
class SecureModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for("auth.login", next=request.url))


def create_admin(app):
    admin = Admin(app, name="UltraDia Admin", template_mode="bootstrap4")
    admin.add_view(SecureModelView(User, db.session))
    admin.add_view(SecureModelView(UserDailyRecord, db.session))
    admin.add_view(SecureModelView(UserCycleEvent, db.session))
    admin.add_view(SecureModelView(Leads, db.session))
