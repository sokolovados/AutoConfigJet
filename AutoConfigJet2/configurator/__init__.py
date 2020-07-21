from flask import Flask
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_login import LoginManager
from flask_login import current_user
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
app.config['SECRET_KEY'] = '57d85fdff6a569344239f9ec8eb84add'
app.config['WTF_CSRF_ENABLED'] = True

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///config.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

app.config['FLASK_ADMIN_SWATCH'] = 'superhero'
admin = Admin(app, name='Configurator adminKA', template_mode='bootstrap3',)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)


from configurator.models import *
admin.add_view(ModelView(Regions, db.session))
admin.add_view(ModelView(Users, db.session))
admin.add_view(ModelView(Models, db.session))
admin.add_view(ModelView(Recommendations, db.session))
admin.add_view(ModelView(Accounting, db.session))




@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(user_id)


@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for('login'))

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
    return send_from_directory('/'+path[0]+'/',
                               path[1],
                               as_attachment=True)

from .routes import *

