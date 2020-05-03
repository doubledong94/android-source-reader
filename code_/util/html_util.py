import socket

from code_.util.key_util import is_parameter_key, is_reference_key, is_index_key, get_method_key_from_parameter_key


def get_style_str(key, key_preprocess, mk):
    key = key_preprocess(key)
    style_str = ''
    if is_parameter_key(key):
        if not get_method_key_from_parameter_key(key) == mk:
            style_str += 'border-style:solid;border-width:2px;'
    elif is_reference_key(key):
        style_str += 'border-style:solid;border-width:2px;'
    elif is_index_key(key):
        style_str += 'border-style:solid;border-width:2px;'
    #    font_size = 0
    #    style_str += 'font-size:'+str(font_size)+'px;' if font_size > 0 else ''
    return style_str


def get_host_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 80))
    ip = s.getsockname()[0]
    s.close()
    return ip


host = get_host_ip()


def make_link_html(text, link):
    return '<a href="http://' + host + ':8888/' + link + '">' + text + "</a>"


def make_h1_html(text, id_=''):
    id_str = ''
    if id_:
        id_str = 'id="' + str(id_) + '"'
    return '<h1 ' + id_str + '>' + text + "</h1>"


def make_colored_text_html(text, color):
    return '<text style="background-color:' + color + '">' + text + '</text>'


def convert_pk_to_colored_text(pk):
    ret_str = ''
    pks = pk.split(':')
    level_count = 1
    for pk_level_i in pks:
        pks_level_i = pk_level_i.split(',')
        color_index = level_count * int(pks_level_i[0]) * int(pks_level_i[1])
        color_ = get_color(color_index)
        ret_str += make_colored_text_html(pk_level_i + ':', color_)
        level_count += 1
    return ret_str


def get_color(index):
    circle_index = index % len(dependency_colors)
    return dependency_colors[circle_index]


dependency_colors = ['#f5b7b1', '#d2b4de', '#a9cce3', '#abebc6', '#f9e79f', '#f5cba7', '#d5dbdb'] * 10
