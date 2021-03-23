from flask import Flask
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import LoginManager
from flask_login import current_user
from flask_sqlalchemy import SQLAlchemy
from flask_admin.contrib.fileadmin import FileAdmin
import os.path as op
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = '57d85fdff6a569344239f9ec8eb84add'
app.config['WTF_CSRF_ENABLED'] = True

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////app/configurator/db/config.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True


class MyHomeView(AdminIndexView):
    @expose('/')
    def index(self):
        return self.render('admin/index.html')


app.config['FLASK_ADMIN_SWATCH'] = 'flatly'
admin = Admin(app, name='Configurator adminKA', template_mode='bootstrap3',
              index_view=MyHomeView())
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(user_id)


@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for('login'))


class DevModelView(ModelView):
    def is_accessible(self):
        if current_user.is_authenticated:
            if current_user.user == 'vysokolo':
                return True


class AccountingModelView(ModelView):
    def is_accessible(self):
        if current_user.is_authenticated:
            if current_user.password == 'oasadmin' or current_user.user == 'vysokolo':
                return True

    can_delete = True
    page_size = 50
    column_searchable_list = ['ip', 'msk', 'user', 'region']


class OtherModelView(ModelView):
    column_hide_backrefs = False

    def is_accessible(self):
        if current_user.is_authenticated:
            if current_user.password == 'oasadmin' or current_user.user == 'vysokolo':
                return True


from configurator.models import *

class UserModelView(ModelView):
    can_delete = False
    page_size = 50
    column_searchable_list = ['ip', 'msk', 'user', 'region']

class FileForAdmin(FileAdmin):
    def is_accessible(self):
        if current_user.is_authenticated:
            if current_user.password == 'oasadmin' or current_user.user == 'vysokolo':
                return True
    can_delete = False

admin.add_view(OtherModelView(Regions, db.session))
admin.add_view(OtherModelView(Users, db.session))
admin.add_view(OtherModelView(Models, db.session))
admin.add_view(OtherModelView(Recommendations, db.session))
admin.add_view(UserModelView(Accounting, db.session))
admin.add_view(DevModelView(Checkboxes, db.session))
admin.add_view(DevModelView(Fields, db.session))
admin.add_view(DevModelView(InputCheckboxes, db.session))
path_to_configs = op.join(op.dirname(__file__), os.getcwd() + '/storage/configs')
admin.add_view(FileForAdmin(path_to_configs, name='Config Files'))
FileAdmin.can_download = True


class TemplateAdmin(FileAdmin):
    def is_accessible(self):
        if current_user.is_authenticated:
            if current_user.password == 'oasadmin' or current_user.user == 'vysokolo':
                return True


path_to_template = op.join(op.dirname(__file__), os.getcwd() + '/configurator/static/config_templates')
admin.add_view(TemplateAdmin(path_to_template, name='Template Files'))


# Load_to_tftp_button
@app.route('/tftpload', methods=['POST'])
def tftpload():
    url = request.get_data().decode('ascii')
    if request.method == 'POST':
        tftp = tftpy.TftpClient('127.0.0.1')
        tftp.upload('config', url)
        return 'success'

    # Logout_button


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))

    # This is supported models for region. list of tuples.


@app.route('/sqlmodel', methods=['POST'])
def sqlmodel():
    models_list = []
    data = json.loads(request.get_data().decode('ascii'))
    region_query = Regions.query.filter_by(city=data['region']).all()
    for region in region_query:
        for model in region.models:
            if model.vendor == data['vendor']:
                models_list.append(model.model)
    return jsonify(models_list)


@app.route('/config_download/<path:path>')
def config_download(path):
    path = os.path.split(os.path.normpath(path))
    return send_from_directory('/' + path[0] + '/',
                               path[1],
                               as_attachment=True)


from .routes import *
