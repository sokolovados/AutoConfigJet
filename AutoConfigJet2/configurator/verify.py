"""Обработка значений заполненной формы"""
import os
import re
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
    print(vlan)
    regex_vlan = (r'^((?:\b(?:\d|[1-9]\d|[1-9]\d|'
                  r'[1-9]\d\d|[1-3]\d\d\d|'
                  r'40[0-8][0-9]|409[0-5])\b,?)+)$')
    match = re.search(regex_vlan, vlan)
    if match:
        return True
    else:
        return False


def hostname(host_name):
    """
    Arguments:
        'Нижний Новгрод Тонкинская 14а'
    Returns:  'Nizhnii_Novgrod_Tonkinskaja_14a'
    """
    regex_ru = re.compile('[а-яА-Я]+')
    match = regex_ru.search(host_name)
    if match:
        return transliterate(host_name)
    else:
        return host_name


def trunk_vlan(trunk_vlans):
    """
    Arguments:
        '1,2-10'
    Returns: {'dlink': ['1', '10', '2', '3', '4', '5', '6', '7', '8', '9'],
              'fiberhome': ['1', '2-10'],
              'huawei': ['1', '2 to 10']},
    """
    trunk_regex = re.compile(
        r'(?P<vlan_r>\d+ *[to-]+ *\d+)|(?P<vlan>\d+)[, ]*')
    trunk_vlans = trunk_regex.findall(trunk_vlans)
    result = {'huawei': [],
              'dlink': [],
              'fiberhome': []}

    for vlan_range, single_vlan in trunk_vlans:
        if vlan_range:
            vlan_range = vlan_range.replace(' ', '').replace('to', '-')
            vlan_range = vlan_range.split('-')
            for vlan in range(int(vlan_range[0]), int(vlan_range[1]) + 1):
                result['dlink'].append(str(vlan))
                result['huawei'].append(f'{vlan_range[0]} to {vlan_range[1]}')
                result['fiberhome'].append(f'{vlan_range[0]}-{vlan_range[1]}')
        elif single_vlan:
            result['dlink'].append(single_vlan)
            result['huawei'].append(single_vlan)
            result['fiberhome'].append(single_vlan)
    for vendor in result:
        # Remove duplicate vlan
        result[vendor] = sorted(set(result[vendor]))
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
    """
    Arguments:
        "vendor": form.vendor.data,
        "model": form.model.data,
        "hostname": form.hostname.data,
        "ip_mask": form.ip_mask.data,
        "user_vlan": form.user_vlan.data,
        "mgmt_vlan": form.mgmt_vlan.data,
        "trunk_vlan": form.trunk_vlan.data,
        "region": "URAL/KGN'}
    Action: render template
    Return:
        -Url for cfg file
        -Url for htmlCFG file
        """
    print(data)
    path_to_pattern = os.path.abspath(
        f"configurator/static/config_templates/{data['region']}/{data['vendor']}/{data['model']}/")
    env = Environment(loader=FileSystemLoader(
        os.path.abspath(path_to_pattern)),
        trim_blocks=True,
        lstrip_blocks=True)
    template = env.get_template('pattern.jinja2')
    templateHTML = env.get_template('patternHTML.jinja2')

    data_for_render = {
        'ip': ip_mask(data['ip_mask']),
        'hostname': hostname(data['hostname']),
        'user_vlan': data['user_vlan'],
        'mgmt_vlan': data['mgmt_vlan'],
        'trunk_vlans': trunk_vlan(data['trunk_vlan']),
    }
    # pprint(data_for_render)

    path_to_config = os.path.abspath(
        f'storage/configs/{data["region"]}/'
        f'{data["vendor"]}/{data["model"]}/'
        f'{data_for_render["ip"]["ip"]}.cfg'
    )
    path_to_config_HTML = os.path.abspath(
        f'storage/configs/{data["region"]}/'
        f'{data["vendor"]}/{data["model"]}/'
        f'{data_for_render["ip"]["ip"]}HTML.cfg'
    )
    try:
        os.makedirs(os.path.split(path_to_config)[0])
    except:
        pass

    with open(path_to_config, 'w') as config:
        config.write(template.render(data_for_render))

    with open(path_to_config_HTML, 'w') as config:
        config.write(templateHTML.render(data_for_render))

    return path_to_config, path_to_config_HTML
