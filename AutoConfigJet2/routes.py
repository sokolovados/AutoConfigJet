import json
import os
from datetime import datetime

import re
import tftpy
import wtforms
from flask import url_for, request, render_template, jsonify, send_from_directory
from flask_login import login_required, logout_user, login_user, current_user
from werkzeug.utils import redirect
from collections import OrderedDict

from configurator import login_manager, app, db
from configurator.forms import LoginForm, StdForm, SaratovForm, PenzaForm
from configurator.models import Users, Regions, Models, Accounting, Checkboxes, Fields
from configurator.verify import render_data, vlan_check,trunk_check, hostname

def input_groups(region):
    input_groups = {'fields': OrderedDict(), 'check_box_input': {}, 'simple_check_box': {}}
    for region in Regions.query.filter_by(city=region):
        for field in region.fields:
            input_groups['fields'].update({field.field: field.field_name})
        for input_checkbox in region.inputcheckbox:
            input_groups['check_box_input'].update(
                {input_checkbox.inputcheckbox: [
                    input_checkbox.inputcheckbox_name,
                    input_checkbox.inputcheckbox + '_checkbox']})
        for checkbox in region.checkbox:
            input_groups['simple_check_box'].update(
                {checkbox.checkbox: [
                    checkbox.checkbox_name,
                    checkbox.checkbox + '_checkbox']})
        print(input_groups)
        return(input_groups)




# NAVBAR from SQL
def navbar():
    macro_regions = [mr.mr_name for mr in Regions.query.all()]
    regions_dict = {mr: {} for mr in macro_regions}
    regions_list = []
    for macro_region in macro_regions:
        for region in Regions.query.filter_by(mr_name=macro_region):
            regions_dict[macro_region].update({region.city_name: region.city})
            regions_list.append(region.city)
    return(macro_regions, regions_dict, regions_list)

@app.route('/')
@login_required
def standart():
    macro_regions, regions_dict, regions_list = navbar()
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
#генерирующий страницы регионов#
@app.route('/autoconfig/<path:region>', methods=['GET', 'POST'])
@login_required
def forms(region):
    macro_regions, regions_dict, regions_list = navbar()
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
    elif region == 'PNZ':
        form = PenzaForm()
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
        #Опциональные для регионов поля#
        if form.multicast_vlan.data:
            mvlan = form.multicast_vlan.data
            if not vlan_check(mvlan):
                error_count += 1
                http_response['errors'].update({'multicast_vlan': ['vlan is between 1 and 4094']})
            else:
                http_response['errors'].update({'multicast_vlan': ''})

        if form.snmp_location.data:
            snmp_loc = form.snmp_location.data
            print(hostname(snmp_loc))
            if not hostname(snmp_loc):
                error_count += 1
                http_response['errors'].update({'snmp_location': ['incorrect symbols']})
            else:
                http_response['errors'].update({'snmp_location': ''})
        
        if region == 'SAR':
            if form.user_vlan.data:
                match = re.search(r'^((?:\b(?:\d|[1-9]\d|[1-9]\d|[1-9]\d\d|[1-3]\d\d\d|40[0-8][0-9]|409[0-5])\b,?)+)$',form.user_vlan.data)
                if not match:
                    http_response['errors'].update({'user_vlan': ["vlan is between 1 and 4094"]})
                    error_count += 1
            else:
                if form.model.data != 'S5320':
                    print('DEBUG OTHER MODEL')
                    http_response['errors'].update({"user_vlan": ["This field is required."]})
                    error_count += 1

        if region != 'SAR':
            if form.trunk_vlan.data:
                trunk_vlan = form.trunk_vlan.data
                if not trunk_check(trunk_vlan):
                    error_count += 1
                    http_response['errors'].update({'trunk_vlan': ["Incorrect format. Example: 1-2,3 to 10,11.Whitespaces don't match"]})
                else:
                    http_response['errors'].update({'trunk_vlan': ''})           
            else:
                http_response['errors'].update({'trunk_vlan': ['This field is required.']})
                error_count += 1


        if region == 'PNZ':
            if form.user_vlan.data:
                user_vlan = form.user_vlan.data
                if not trunk_check(user_vlan):
                    error_count += 1
            else:
                error_count += 1

        # validate form and send it to render_data, or return error for fields
        if form.validate_on_submit() and error_count == 0:
            data_list.update({"region": f'{region_query.mr}/{region_query.city}'})
            for field in form.data:
                try:
                    data_list.update({field: form[field].data})
                except AttributeError:
                    continue

            path_to_configs = render_data(data_list)
            config = open(path_to_configs[1], 'r')
            http_response['result'] = config.readlines()
            http_response['errors'].update({"vendor": '',
                                            'msk': '',
                                            "model": '',
                                            "hostname": '',
                                            "ip_mask": '',
                                            "user_vlan": ''
                                            })
            try:
                http_response['errors'].update({"mgmt_vlan": '' })
            except AttributeError as error:
                pass
            try:
                http_response['errors'].update({"trunk_vlan":'' })
            except AttributeError as error:
                pass

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
                                            })
            if region != 'PNZ':
                http_response['errors'].update({'user_vlan': form.user_vlan.errors})
            else:
                if region != 'SAR':
                    if form.user_vlan.data:
                        user_vlan = form.user_vlan.data
                        print(trunk_check(user_vlan))
                        if not trunk_check(user_vlan):
                            error_count += 1
                            http_response['errors'].update(
                                {'user_vlan': ["Incorrect format. Example: 1-2,3-10,11 MAX- 4095"]})
                        else:
                            http_response['errors'].update({'user_vlan': ''})
                    else:
                        http_response['errors'].update({'user_vlan': ['This field is required.']})
                        error_count += 1



            try:
                http_response['errors'].update({"mgmt_vlan": form.mgmt_vlan.errors})
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
                               fields=input_groups(region),
                               form=form,
                               region_name=region_query.city_name,
                               recommendations=recommendation_list,
                               title=region,
                               vendors=vendors_list
                               )




