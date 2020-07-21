import json
import os
from datetime import datetime

import tftpy
import wtforms
from flask import url_for, request, render_template, jsonify, send_from_directory
from flask_login import login_required, logout_user, login_user, current_user
from werkzeug.utils import redirect

from configurator import login_manager, app, db
from configurator.forms import LoginForm, StdForm, SaratovForm
from configurator.models import Users, Regions, Models, Accounting
from configurator.verify import render_data, vlan_check

# Input fields from json
with open("configurator/static/jsons/input_groups.json") as json_file:
    input_groups_dict = json.load(json_file)

# NAVBAR from SQL
macro_regions = [mr.mr_name for mr in Regions.query.all()]
regions_dict = {mr: {} for mr in macro_regions}
regions_list = []
for macro_region in macro_regions:
    for region in Regions.query.filter_by(mr_name=macro_region):
        regions_dict[macro_region].update({region.city_name: region.city})
        regions_list.append(region.city)


@app.route('/')
@login_required
def standart():
    region_models_dict = {}
    for region in Regions.query.all():
        region_models_dict[region.city_name] = {}
        for model in region.models:
            try:
                region_models_dict[region.city_name][model.vendor].append(f'{model.model}')
            except KeyError:
                region_models_dict[region.city_name][model.vendor] = []
                region_models_dict[region.city_name][model.vendor].append(f'{model.model}')


    return render_template('index.html',
                           regions=regions_dict,
                           supported_regions=region_models_dict,
                           title='OAS AutoConfig')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(user=form.username.data).first()
        if user:
            if user.password == form.password.data:
                user.authenticated = True
                login_user(user, remember=True)
                next = request.args.get('next')
                return redirect(next or url_for('standart'))
    return render_template('login.html',
                           title='Login',
                           form=form)


# Regions block
@app.route('/autoconfig/<path:region>', methods=['GET', 'POST'])
@login_required
def forms(region):
    print(current_user.user)
    # This is supported vendors for current region.
    region_query = Regions.query.filter_by(city=region).first()
    vendors_list = []
    path = f'{region_query.mr}/{region}'
    for model in region_query.models:
        vendors_list.append(model.vendor)
    vendors_list = list(set(vendors_list))

    # TODO redirect into error page
    if not region in regions_list:
        return 'Регион не существует'
    error_count = 0

    if region == 'SAR':
        form = SaratovForm()
    else:
        form = StdForm()

    http_response = {'errors': {},
                     'result': {},
                     'path': ''}
    data_list = {}
    # form.vendor.choices = vendors_list

    # Action for submit button.
    if request.method == 'POST':
        # validation optional fields
        if form.multicast_vlan.data:
            mvlan = form.multicast_vlan.data
            if not vlan_check(mvlan):
                error_count += 1
                http_response['errors'].update({'multicast_vlan': ['vlan is between 1 and 4094']})
            else:
                http_response['errors'].update({'multicast_vlan': ''})

        # validate form and send it to render_data, or return error for fields
        if form.validate_on_submit() and error_count == 0:
            data_list.update({"vendor": form.vendor.data,
                              "msk": form.msk.data,
                              "model": form.model.data,
                              "hostname": form.hostname.data,
                              "ip_mask": form.ip_mask.data,
                              "user_vlan": form.user_vlan.data,
                              "region": f'{region_query.mr}/{region_query.city}'
                              })

            try:
                data_list.update({"mgmt_vlan": form.mgmt_vlan.data})
            except AttributeError as error:
                pass
            try:
                data_list.update({"trunk_vlan": form.trunk_vlan.data})
            except AttributeError as error:
                pass

            path_to_configs = render_data(data_list)
            config = open(path_to_configs[1], 'r')
            print(path_to_configs[0])
            http_response['result'] = config.readlines()
            http_response['errors'].update({"vendor": '',
                                            'msk': '',
                                            "model": '',
                                            "hostname": '',
                                            "ip_mask": '',
                                            "user_vlan": '',
                                            "mgmt_vlan": '',
                                            "trunk_vlan": ''
                                            })
            log = Accounting(user=current_user.user,
                             region=region,
                             msk=form.msk.data,
                             ip=form.ip_mask.data,
                             hostname=form.hostname.data,
                             date=datetime.utcnow(),
                             accounting=','.join([f'{key}:{value}' for key, value in data_list.items()])
                             )
            db.session.add(log)
            db.session.commit()


            http_response['path'] = path_to_configs[0]
            return jsonify(http_response)
        else:
            http_response['errors'].update({"vendor": form.vendor.errors,
                                            "model": form.model.errors,
                                            "msk": form.msk.errors,
                                            "hostname": form.hostname.errors,
                                            "ip_mask": form.ip_mask.errors,
                                            "user_vlan": form.user_vlan.errors,
                                            })

            try:
                http_response['errors'].update({"mgmt_vlan": form.mgmt_vlan.errors})
            except AttributeError as error:
                pass
            try:
                http_response['errors'].update({"trunk_vlan": form.trunk_vlan.errors})
            except AttributeError as error:
                pass

            http_response['result'] = ''
            return jsonify(http_response)

    # Action for load page
    elif request.method == 'GET':
        recommendation_list = []
        for recommendation in region_query.recommendations:
            recommendation_list.append(recommendation.recommendation)
        return render_template('region.html',
                               regions=regions_dict,
                               fields=input_groups_dict[region],
                               form=form,
                               region_name=region_query.city_name,
                               recommendations=recommendation_list,
                               title=region,
                               vendors=vendors_list
                               )




