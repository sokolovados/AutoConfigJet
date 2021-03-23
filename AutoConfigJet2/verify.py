"""Обработка значений заполненной формы"""
import os
import re
from collections import OrderedDict
from ipaddress import IPv4Interface

from jinja2 import Environment, FileSystemLoader


def transliterate(name):
    # Словарь с заменами
    translit_dict = {'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e',
                     'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'i', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n',
                     'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'h',
                     'ц': 'c', 'ч': 'cz', 'ш': 'sh', 'щ': 'scz', 'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e',
                     'ю': 'u', 'я': 'ja', 'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'E',
                     'Ж': 'ZH', 'З': 'Z', 'И': 'I', 'Й': 'I', 'К': 'K', 'Л': 'L', 'М': 'M', 'Н': 'N',
                     'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U', 'Ф': 'F', 'Х': 'H',
                     'Ц': 'C', 'Ч': 'CZ', 'Ш': 'SH', 'Щ': 'SCH', 'Ъ': '', 'Ы': 'y', 'Ь': '', 'Э': 'E',
                     'Ю': 'U', 'Я': 'YA', ',': '', '?': '', ' ': '_', '~': '', '!': '', '@': '', '#': '',
                     '$': '', '%': '', '^': '', '&': '', '*': '', '(': '', ')': '', '-': '', '=': '', '+': '',
                     ':': '', ';': '', '<': '', '>': '', '\'': '', '"': '', '\\': '', '/': '', '№': '',
                     '[': '', ']': '', '{': '', '}': '', 'ґ': '', 'ї': '', 'є': '', 'Ґ': 'g', 'Ї': 'i',
                     'Є': 'e', '—': ''}
    # Циклически заменяем все буквы в строке
    for key in translit_dict:
        name = name.replace(key, translit_dict[key])
    return name


def vlan_check(vlan):
    regex_vlan = (r'^((?:\b(?:\d|[1-9]\d|[1-9]\d|'
                  r'[1-9]\d\d|[1-3]\d\d\d|'
                  r'40[0-8][0-9]|409[0-5])\b,?)+)$')
    match = re.search(regex_vlan, vlan)
    if match:
        return True
    else:
        return False

def trunk_check(trunk_vlans):

    trunk_vlans_isdigit = (trunk_vlans.replace(' to ', ',')
                    .replace(' ',',')
                    .replace('-',','))
    for vlan in trunk_vlans_isdigit.split(','):
        if not vlan.isdigit():
            return False
    list_of_vlans = re.findall("\d+",trunk_vlans)
    for vlan in list_of_vlans:
        if vlan_check(vlan) == True:
            continue
        else:
            return False
    else:
        return True


def hostname(host_name):
    """
    Arguments:
        'Нижний Новгород Тонкинская 14а'
    Returns:  'Nizhnii_Novgrod_Tonkinskaja_14a'
    """
    regex_correct = re.compile('^[.-zA-Z1-9\-_а-яА-Я ]+$')
    correct = regex_correct.search(host_name)
    host_name = host_name.replace(' ','_')
    if correct:
        regex_ru = re.compile('[а-яА-Я]+')
        match = regex_ru.search(host_name)
        if match:
            return transliterate(host_name)
        else:
            return host_name
    else:
        return False


def range_agregation(mgmt_vlan, user_vlan, all_vlan):
    all_vlan = [int(i) for i in all_vlan]
    all_vlan = list(set(all_vlan))
    all_vlan = sorted(all_vlan)
    count = 0
    i = iter(all_vlan)
    result_list = []
    startvlan = next(i)
    curvlan = startvlan
    loop = True
    while loop:
        try:
            nextvlan = next(i)
            if curvlan + 1 == nextvlan:
                curvlan = nextvlan
            else:
                if startvlan != curvlan:
                    result_list.append(str(startvlan) + '-' + str(curvlan))
                else:
                    result_list.append(str(startvlan))
                startvlan = nextvlan
                curvlan = startvlan
        except:
            if startvlan != curvlan:
                result_list.append(str(startvlan) + '-' + str(curvlan))
            else:
                result_list.append(str(startvlan))
            loop = False
    result_without_mgmt = [element for element in result_list if element != mgmt_vlan]
    result_without_mgmt_user = [element for element in result_without_mgmt if element != user_vlan]
    return all_vlan, result_list, result_without_mgmt, result_without_mgmt_user


def trunk_vlan(mgmt_vlan, user_vlan, *args):
    trunk_vlans = []
    for arg in args:
        if arg !=None:
            trunk_vlans.append(arg)
    trunk_vlans = ','.join(trunk_vlans)
    trunk_regex = re.compile(
        r'(?P<vlan_r>\d+ *[to-]+ *\d+)|(?P<vlan>\d+)[, ]*')
    trunk_vlans = trunk_regex.findall(trunk_vlans)

    all_vlan = []
    for vlan_range, single_vlan in trunk_vlans:
        if vlan_range:
            vlan_range = vlan_range.replace(' ', '').replace('to', '-')
            vlan_range = vlan_range.split('-')
            for vlan in range(int(vlan_range[0]), int(vlan_range[1]) + 1):
                all_vlan.append(vlan)
        elif single_vlan:
            all_vlan.append(single_vlan)

    result = {"all_vlans": {
        'huawei': [],
        'dlink': [],
        'fiberhome': []
    },
        "vlans_without_mgmt": {
            'huawei': [],
            'dlink': [],
            'fiberhome': []
        },
        "vlans_without_mgmt_user": {
            'huawei': [],
            'dlink': [],
            'fiberhome': []
        }
    }

    all_vlan, all_vlan_range, all_vlan_range_without_mgmt, all_vlan_range_without_mgmt_user = range_agregation(
        mgmt_vlan, user_vlan, all_vlan)
    for vlan in all_vlan:
        result["all_vlans"]["dlink"].append(vlan)
        
        if mgmt_vlan:
            if vlan != int(mgmt_vlan):
                result["vlans_without_mgmt"]["dlink"].append(vlan)
                if vlan != int(user_vlan):
                    result["vlans_without_mgmt_user"]["dlink"].append(vlan)

    for vlan in all_vlan_range:
        if vlan.isdigit():
            result["all_vlans"]["huawei"].append(vlan)
            result["all_vlans"]["fiberhome"].append(vlan)
        else:
            result["all_vlans"]["huawei"].append(vlan.replace('-', ' to '))
            result["all_vlans"]["fiberhome"].append(vlan)

    for vlan in all_vlan_range_without_mgmt:
        if vlan.isdigit():
            result["vlans_without_mgmt"]["huawei"].append(vlan)
            result["vlans_without_mgmt"]["fiberhome"].append(vlan)
        else:
            result["vlans_without_mgmt"]["huawei"].append(vlan.replace('-', ' to '))
            result["vlans_without_mgmt"]["fiberhome"].append(vlan)

    for vlan in all_vlan_range_without_mgmt_user:
        if vlan.isdigit():
            result["vlans_without_mgmt_user"]["huawei"].append(vlan)
            result["vlans_without_mgmt_user"]["fiberhome"].append(vlan)
        else:
            result["vlans_without_mgmt_user"]["huawei"].append(vlan.replace('-', ' to '))
            result["vlans_without_mgmt_user"]["fiberhome"].append(vlan)

    return result


def ip_mask(ip_netmask):
    """
    Arguments:
        '192.168.1.1/24'
    Returns:
     'ip': {'def_gateway_last': '192.168.1.254',
            'def_gateway_first': '192.168.1.1',
            'ip': '192.168.1.1',
            'ip_mask': '192.168.1.1/24',
            'network': '255.255.255.0'},
    """
    ip_netmask = IPv4Interface(ip_netmask)
    ip = ip_netmask.ip.compressed
    netmask = ip_netmask.netmask.compressed
    def_gateway_first = list(ip_netmask.network.hosts())[0].compressed
    def_gateway_last = list(ip_netmask.network.hosts())[-1].compressed
    return {
        'ip_mask': ip_netmask.compressed,
        'ip': ip,
        'network': netmask,
        'def_gateway_first': def_gateway_first,
        'def_gateway_last': def_gateway_last
    }


def render_data(data):
    print(data['region'])

    data.setdefault('snmp_location', hostname(data['hostname']))
    data.setdefault('trunk_vlan')
    data.setdefault('mvlan')
    data.setdefault('mgmt_vlan')
    data.setdefault('op_checkbox')
    data.setdefault('op_description')
    path_to_pattern = os.path.abspath(
        f"configurator/static/config_templates/{data['region']}/{data['vendor']}/{data['model']}/")
    env = Environment(loader=FileSystemLoader(
        os.path.abspath(path_to_pattern)),
        trim_blocks=True,
        lstrip_blocks=True)
    template = env.get_template('pattern.jinja2')
    with open(os.path.abspath(path_to_pattern) +'/pattern.jinja2', 'r') as default_template:
        default_template = default_template.read()
        default_template = default_template.replace('{{ ','startreplace{{').replace(' }}','}}endreplace')
        with open (os.path.abspath(path_to_pattern) + '/patternHTML.jinja2','w+') as htmlconfig:
            htmlconfig.write(default_template)


    templateHTML = env.get_template('patternHTML.jinja2')

    data_for_render = {
        'ip': ip_mask(data['ip_mask']),
        'hostname': hostname(data['hostname']),
        'mgmt_vlan': data['mgmt_vlan'],
        'mvlan': data['multicast_vlan']
    }
    if data['trunk_vlan'] or data['user_vlan'] or data['mgmt_vlan']:
        data_for_render.update({'trunk_vlans': trunk_vlan(data['mgmt_vlan'], data['user_vlan'], data['trunk_vlan'], data['user_vlan'], data['mgmt_vlan'])})
    if data['region'] == 'PV/PNZ':

        user_vlans = data['user_vlan'].replace(' ',',')
        user_vlans = user_vlans.split(',')
        user_vlan_list = []
        print(user_vlans)
        for vlan in user_vlans:
            if vlan.isdigit():
                user_vlan_list.append(vlan)
            elif '-' in vlan:
                vlan = vlan.split('-')
                for vid in range(int(vlan[0]), int(vlan[1])+1):
                    user_vlan_list.append(vid)
        vlan_port_dict = OrderedDict()
        for num,vlan in zip(range(1,len(user_vlan_list)+1),user_vlan_list):
            vlan_port_dict[num] = vlan
        print(vlan_port_dict)
        data_for_render.update({'user_vlan': vlan_port_dict})

    else:
        data_for_render.update({'user_vlan': data['user_vlan']})

    data_for_render.update({'op_checkbox': data['op_checkbox']})
    data_for_render.update({'op_description': data['op_description']})
    data_for_render.update({'op_description': data['op_description']})
    if hostname(data['snmp_location']) is False:
        data_for_render.update({'snmp_location': hostname(data['hostname'])})
    else:
        data_for_render.update({'snmp_location': hostname(data['snmp_location'])})
    print(data_for_render)

    path_to_config = os.path.abspath(
        f'storage/configs/{data["region"]}/'
        f'{data["vendor"]}/{data["model"]}/'
        f'{data_for_render["ip"]["ip"]}.cfg'
    )
    path_to_config_HTML = os.path.abspath(
        f'storage/configsHTML/{data["region"]}/'
        f'{data["vendor"]}/{data["model"]}/'
        f'{data_for_render["ip"]["ip"]}HTML.cfg'
    )
    try:
        os.makedirs(os.path.split(path_to_config)[0])
    except:
        pass
    try:
        os.makedirs(os.path.split(path_to_config_HTML)[0])
    except:
        pass

    with open(path_to_config, 'w') as config:
        config.write(template.render(data_for_render))

    with open(path_to_config_HTML, 'w') as config:
        config.write(templateHTML.render(data_for_render))

    return path_to_config, path_to_config_HTML
