#!/usr/bin/python
# -*- coding: UTF-8 -*-
import pickle
import socket

from code_.d_methodAndFieldFeature.a_methodFeature import get_method_feature_relation_list, method_feature_len
from code_.util.file_util import \
    LV2relations_file_path, LVKey2LVTypeKey_path, \
    fieldkey2fieldTypekey_path, typekey2fieldkey_path, \
    typekey2methodkey_path, superTypes_path, subTypes_path, fieldKey2typeKey_path, methodKey2typeKey_path, \
    type2instance_for_field_file_path, type2instance_for_local_file_path, methodKey2srcLoc_path, get_lines, src_abs_dir, \
    fieldKey2srcLoc_path, interfaceType_path, fieldKey2fieldFeatureCount_path, \
    method2lv_dependency_in_dir_file_path, method2lv_dependency_out_dir_file_path, \
    class2field_dependency_in_dir_file_path, class2field_dependency_out_dir_file_path, \
    class2method_dependency_in_dir_file_path, class2method_dependency_out_dir_file_path, read_relation_compressed_path, \
    written_relation_compressed_path, method2relations_compressed_path, method2global_relations_compressed_path, \
    fieldFeatureKey2fieldFeatureRelationList_compressed_path, \
    method_size_map_in_path, method_size_map_out_path, global_method_size_map_in_path, global_method_size_map_out_path, \
    class2self_responsibility_in_path, class2self_responsibility_out_path, class2self_dependency_in_sum_path, \
    class2self_dependency_out_sum_path, class2global_dependency_in_sum_path, class2global_dependency_out_sum_path, \
    method2methodFromOtherClass_in_dir_path, \
    method2methodFromOtherClass_out_dir_path, type_dependency_in_path, type_dependency_out_path, type_size_out_path, \
    type_size_in_path
from code_.util.key_util import get_method_feature_key, is_parameter_key, is_return_key, \
    get_method_key_from_parameter_key, is_method_feature_key, get_method_feature_index, get_method_key_from_feature, \
    get_field_feature_key, get_field_key_from_feature
from code_.y_data_compression_and_decompression.b_key_conversion import decompress_by_replace, to_shorter_key, \
    to_longer_key
from code_.z_srcReader import dependency_html_util
from code_.z_srcReader.dependency_html_util import get_size_string, get_dependency_in_and_out_html, \
    all_id_list_for_js_variable
from code_.z_srcReader.html_util import host

method_key2method_features = {}


def get_method_features(method_key):
    global method_key2method_features
    if method_key in method_key2method_features:
        method_features = method_key2method_features[method_key]
    else:
        method_features = get_method_feature_relation_list(
            method_key, method2global_relations[method_key])
        method_key2method_features[method_key] = method_features
    return method_features


def get_host_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 80))
    ip = s.getsockname()[0]
    s.close()
    return ip


def get_parameter_and_return_html(method_key):
    html_str = ""
    html_str += "<h1>parameters and return:</h1>"
    parameter_str = method_key.split(":")[2]
    if not parameter_str == "":
        parameter_count = len(parameter_str.split(","))
        for i in range(parameter_count):
            parameter_i = method_key + "Parameter" + str(i + 1)
            html_str += '<a href="http://' + host + ':8888/' + parameter_i + '">' + parameter_i + "</a>"
            html_str += "<br><br>"
    return_str = method_key + "Return"
    html_str += '<a href="http://' + host + ':8888/' + return_str + '">' + return_str + "</a>"
    html_str += "<br><br>"
    return html_str


def get_all_local_variable_html(relation_list):
    html_str = "<h1>all local variables:</h1>"
    local_variables = []
    order_min_map = {}
    order_max_map = {}
    order_count_map = {}
    for r in relation_list:
        r0long = to_longer_key(r[0])
        if r0long in LVKey2LVTypeKey:
            order = r[3]
            # init order_min_map
            if r0long not in order_min_map:
                order_min_map[r0long] = 10000000
                order_max_map[r0long] = -1
                order_count_map[r0long] = []
            order_count_map[r0long].append(order)
            # search for max
            if order > order_max_map[r0long]:
                order_max_map[r0long] = order
            # search for min
            if order < order_min_map[r0long]:
                order_min_map[r0long] = order
            local_variables.append(r0long)
        r1long = to_longer_key(r[1])
        if r1long in LVKey2LVTypeKey:
            order = r[3]
            # init order_min_map
            if r1long not in order_min_map:
                order_min_map[r1long] = 10000000
                order_max_map[r1long] = -1
                order_count_map[r1long] = []
            order_count_map[r1long].append(order)
            # search for max
            if order > order_max_map[r1long]:
                order_max_map[r1long] = order
            # search for min
            if order < order_min_map[r1long]:
                order_min_map[r1long] = order
            local_variables.append(r1long)

        local_variables = list(set(local_variables))
        sorted_by_min_order = [[k, v] for k, v in order_min_map.items()]
        sorted_by_min_order.sort(key=lambda e: e[1])
    for lv, min_order in sorted_by_min_order:
        order_span = order_max_map[lv] - order_min_map[lv] + 1
        order_count_map[lv] = list(set(order_count_map[lv]))
        space3 = "&nbsp;&nbsp;"
        html_str += '<a href="http://' + host + ':8888/' + lv + '">' + lv + "</a>" \
                    + space3 + str(order_min_map[lv]) \
                    + space3 + '-' \
                    + space3 + str(order_max_map[lv]) \
                    + space3 + '=' \
                    + space3 + str(order_span) \
                    + space3 + ':' \
                    + space3 + str(len(order_count_map[lv]))
        html_str += "<br><br>"
    return html_str


dependency_colors = ['#f5b7b1', '#d2b4de', '#a9cce3', '#abebc6', '#f9e79f', '#f5cba7', '#d5dbdb'] * 10


def make_colored_text_html(text, color):
    return '<text style="background-color:' + color + '">' + text + '</text>'


def sort_dependency_by_method_size(dependency_list, method_size_map):
    dependency_in_dir_list_with_size = []
    for dependency_in_dir_i in dependency_list:
        dependency_in_dir_list_with_size.append([
            dependency_in_dir_i,
            method_size_map[dependency_in_dir_i] if dependency_in_dir_i in method_size_map else 1
        ])
    dependency_in_dir_list_with_size.sort(key=lambda e: e[1], reverse=True)
    dependency_in_dir_list = [i[0] for i in dependency_in_dir_list_with_size]
    return dependency_in_dir_list


def recur_for_dependency(lv, lv_dependency_in_dir, depth, super_list, type_key_len, id_list, method_size_map,
                         method_size_map_for_sorting, method2method_from_other_class):
    global method_size_in, method_size_out
    all_dependency_id_list = dependency_html_util.all_id_list_for_js_variable
    # html_str = '|'.join([' '.join(['&nbsp;'] * 2)] * depth) + make_link_html(lv, lv) + "<br>"
    padding = '|'.join([' '.join(['&nbsp;'] * 2)] * depth)
    id = ':'.join(id_list)
    all_dependency_id_list.append(id)
    display_str = ""
    if len(super_list) > 0:
        display_str = 'style="display:none"'
    method_size = ""
    if lv in method_size_map:
        method_size = get_size_string(lv, method_size_in, method_size_out,
                                      global_method_size_in, global_method_size_out)
    html_str = '<text ' + display_str + ' onclick="dependency_click(\'' + id + '\')" id=' + id + '>' + padding + \
               make_colored_text_html(lv[type_key_len:], dependency_colors[depth]) + method_size + "<br></text>"
    id_count = 0
    if lv not in super_list:
        super_list.append(lv)
        if lv in lv_dependency_in_dir:
            dependency_in_dir_list = lv_dependency_in_dir[lv]
            if not method_size == "":
                dependency_in_dir_list = \
                    sort_dependency_by_method_size(dependency_in_dir_list, method_size_map_for_sorting)
            for child_node in dependency_in_dir_list:
                id_count += 1
                id_list_copy = id_list.copy()
                id_list_copy.append(str(id_count))
                super_list_copy = super_list.copy()
                html_str += recur_for_dependency(
                    child_node, lv_dependency_in_dir, depth + 1, super_list_copy, type_key_len, id_list_copy,
                    method_size_map, method_size_map_for_sorting, method2method_from_other_class)
        if depth < 3 and lv in method2method_from_other_class and \
                len(method2method_from_other_class[lv]) > 0:
            from_other_class = ":from_other_class"
            depth += 1
            padding = '|'.join([' '.join(['&nbsp;'] * 2)] * depth)
            id += from_other_class
            all_dependency_id_list.append(id)
            html_str += '<text ' + 'style="display:none"' + ' onclick="dependency_click(\'' + id + '\')" id=' + id + '>' \
                        + padding + make_colored_text_html(from_other_class, dependency_colors[depth]) \
                        + "<br></text>"
            depth += 1
            padding = '|'.join([' '.join(['&nbsp;'] * 2)] * depth)
            other_method_count = 0
            for mk_from_other_class in method2method_from_other_class[lv]:
                other_method_count += 1
                other_id = id + ":" + str(other_method_count)
                all_dependency_id_list.append(other_id)
                if mk_from_other_class in method_size_map:
                    method_size = get_size_string(
                        mk_from_other_class, method_size_in, method_size_out,
                        global_method_size_in, global_method_size_out)
                html_str += '<text ' + 'style="display:none"' + ' onclick="dependency_click(\'' \
                            + other_id + '\')" id=' + other_id + '>' + padding + \
                            make_colored_text_html(mk_from_other_class, dependency_colors[depth]) \
                            + method_size + "<br></text>"
    return html_str


def get_dependency_html(dependency_in_dir, dependency_out_dir, id_str, type_key_len, id_head):
    all_lv_key = []
    for k, v in dependency_out_dir.items():
        all_lv_key.append(k)
        for vi in v:
            all_lv_key.append(vi)
    all_lv_key = list(set(all_lv_key))
    out_zero_lv_list = []
    in_zero_lv_list = []
    for lv_key in all_lv_key:
        if lv_key not in dependency_out_dir.keys() or len(dependency_out_dir[lv_key]) == 0:
            out_zero_lv_list.append(lv_key)
        elif lv_key in dependency_out_dir[lv_key] and len(dependency_out_dir[lv_key]) == 1:
            out_zero_lv_list.append(lv_key)
    for lv_key in all_lv_key:
        if lv_key not in dependency_in_dir.keys() or len(dependency_in_dir[lv_key]) == 0:
            in_zero_lv_list.append(lv_key)
        elif lv_key in dependency_in_dir[lv_key] and len(dependency_in_dir[lv_key]) == 1:
            in_zero_lv_list.append(lv_key)
    out_zero_lv_list = sort_dependency_by_method_size(out_zero_lv_list, global_method_size_in)
    in_zero_lv_list = sort_dependency_by_method_size(in_zero_lv_list, global_method_size_out)
    html_str = '<h1>' + id_str + ' dependency in:</h1>'
    id_count = 0
    for lv in out_zero_lv_list:
        id_count += 1
        html_str += recur_for_dependency(lv, dependency_in_dir, 0, [],
                                         type_key_len, [id_head + str(id_count)], method_size_in,
                                         global_method_size_in, method2methodFromOtherClass_in_dir)
        html_str += '<br>'
    html_str += '<h1>' + id_str + ' dependency out:</h1>'
    for lv in in_zero_lv_list:
        id_count += 1
        html_str += recur_for_dependency(lv, dependency_out_dir, 0, [],
                                         type_key_len, [id_head + str(id_count)], method_size_out,
                                         global_method_size_out, method2methodFromOtherClass_out_dir)
        html_str += '<br>'
    html_str += '<h1>' + id_str + ' not involved:</h1>'
    for k in all_lv_key:
        if k not in dependency_in_dir and k not in dependency_out_dir:
            html_str += make_link_html(k, k)
            html_str += '<br>'
    return html_str


def get_relation_with_local_html(relation_list):
    html_str = "<h1>relations with local:</h1>"
    for r in relation_list:
        html_str += "s" + str(r[3]) + ": "
        r0long = to_longer_key(r[0])
        r1long = to_longer_key(r[1])
        html_str += '<a href="http://' + host + ':8888/' + r0long + '">' + r0long + "</a>" + " <--- " + \
                    '<a href="http://' + host + ':8888/' + r1long + '">' + r1long + "</a>"
        html_str += ' (' + r[2] + ')'
        html_str += "<br><br>"
    return html_str


def get_relation_without_local_html(relation_list):
    html_str = "<h1>relations without local:</h1>"
    for r in relation_list:
        r0long = to_longer_key(r[0])
        r1long = to_longer_key(r[1])
        html_str += 's' + str(r[2]) + ": " + \
                    '<a href="http://' + host + ':8888/' + r0long + '">' + r0long + "</a>" + " <--- " + \
                    '<a href="http://' + host + ':8888/' + r1long + '">' + r1long + "</a>"
        html_str += "<br><br>"
    return html_str


def make_link_html(text, link):
    return '<a href="http://' + host + ':8888/' + link + '">' + text + "</a>"


def get_method_feature_html(methodKey, features):
    html_str = "<h1>method features:</h1>"
    str_list = [
        "# 0: return = parameter",
        "# 1: return = local",
        "# 2: return = field",
        "# 3: return = methodCall",

        "# 4: return = parameter",
        "# 5: condition = parameter",
        "# 6: field = parameter",
        "# 7: methodCall = parameter",
        "# 8: reference = parameter",

        "# 09: condition = parameter",
        "# 10: condition = local",
        "# 11: condition = field",
        "# 12: condition = methodCall",

        "# 13: field = parameter",
        "# 14: field = local",
        "# 15: field = field",
        "# 16: field = methodCall",

        "# 17: return = field",
        "# 18: condition = field",
        "# 19: field = field",
        "# 20: methodCall = field",
        "# 21: reference = field",

        "# 22: methodCall = parameter",
        "# 23: methodCall = local",
        "# 24: methodCall = field",
        "# 25: methodCall = methodCall",

        "# 26: return = methodCall",
        "# 27: local = methodCall",
        "# 28: condition = methodCall",
        "# 29: field = methodCall",
        "# 30: methodCall = methodCall",
        "# 31: reference = methodCall",

        "# 32: reference = parameter",
        "# 33: reference = local",
        "# 34: reference = field",
        "# 35: reference = methodCall",

        "# 36: parameter = parameter",
        "# 37: parameter = local",
        "# 38: parameter = field",
        "# 39: parameter = methodCall",
    ]
    for i in range(len(str_list)):
        str_list[i] = str_list[i].replace(' ', '&nbsp;')

    blank_space_index = [3, 8, 12, 16, 21, 25, 31, 35]
    for i in range(method_feature_len):
        feature_count = len(features[i])
        feature_count_str = ' ' + str(feature_count) if feature_count > 0 else ''
        html_str += make_link_html(str_list[i] + feature_count_str,
                                   get_method_feature_key(methodKey, i)) + "<br>"
        if i in blank_space_index:
            html_str += "<br>"
    return html_str


def get_field_feature_html(fieldKey, features):
    html_str = "<h1>field features:</h1>"
    html_str += '# genericField is read<br>'
    html_str += make_link_html('# 0: return=genericField ' + str(features[0]),
                               get_field_feature_key(fieldKey, 0)) + '<br>'
    html_str += make_link_html('# 1: condition=genericField ' + str(features[1]),
                               get_field_feature_key(fieldKey, 1)) + '<br>'
    html_str += make_link_html('# 2: methodCall=genericField ' + str(features[2]),
                               get_field_feature_key(fieldKey, 2)) + '<br>'
    html_str += make_link_html('# 3: field=genericField ' + str(features[3]),
                               get_field_feature_key(fieldKey, 3)) + '<br>'
    html_str += make_link_html('# 4: reference=genericField ' + str(features[4]),
                               get_field_feature_key(fieldKey, 4)) + '<br>'
    html_str += make_link_html('# 5: local=genericField(methodCall) ' + str(features[5]),
                               get_field_feature_key(fieldKey, 5)) + '<br><br>'
    html_str += '# genericField is written<br>'
    html_str += make_link_html('# 6: genericField=field ' + str(features[6]),
                               get_field_feature_key(fieldKey, 6)) + '<br>'
    html_str += make_link_html('# 7: genericField=return ' + str(features[7]),
                               get_field_feature_key(fieldKey, 7)) + '<br>'
    html_str += make_link_html('# 8: genericField=parameter ' + str(features[8]),
                               get_field_feature_key(fieldKey, 8)) + '<br>'
    html_str += make_link_html('# 9: genericField=local ' + str(features[9]),
                               get_field_feature_key(fieldKey, 9)) + '<br><br>'

    html_str += '# genericField is self assigned<br>'
    html_str += make_link_html('# 9: self assignment ' + str(features[10]),
                               get_field_feature_key(fieldKey, 10)) + '<br><br>'
    html_str = html_str.replace('genericField', '<b>genericField</b>')
    return html_str


def convert_python_list2js_list(var_name, python_list):
    js_str = 'var ' + var_name + ' = ['
    for i in python_list:
        js_str += "'" + str(i) + "',"
    js_str += '];'
    return js_str


def get_js_code_str():
    all_dependency_id_list = dependency_html_util.all_id_list_for_js_variable
    id_list_js_define_str = convert_python_list2js_list('id_list', all_dependency_id_list)
    js_str = "<script>"
    js_str += 'function dependency_click(id){' \
              + id_list_js_define_str + \
              '     var pick_first=true;' \
              '     var display_value="inline";' \
              '     for(let index in id_list){' \
              '         id_i=id_list[index];' \
              '         if(id_i.startsWith(id+":")){' \
              '             var to_be_hidden = document.getElementById(id_i);' \
              '             if(pick_first){' \
              '                 if(to_be_hidden.style.display=="none"){' \
              '                     display_value="inline";' \
              '                 }else{' \
              '                     display_value="none";' \
              '                 }' \
              '                 pick_first=false' \
              '             }' \
              '             to_be_hidden.style.display=display_value;' \
              '         }' \
              '     }' \
              '}'
    js_str += "</script>"
    return js_str


def remove_duplicated_item_from_list_retaining_order(list_):
    new_list = []
    for i in list_:
        if i not in new_list:
            new_list.append(i)
    return new_list


def get_field_relation_html(field_key, relation_list):
    http_str = ''
    method2global_read_relation_list = {}
    for item in relation_list:
        is_read_relation = to_longer_key(item[1]) == field_key
        relation_key = item[0] if is_read_relation else item[1]
        if item[1] in method2global_read_relation_list:
            method2global_read_relation_list[item[4]].append([relation_key, item[2], item[3], is_read_relation])
        else:
            method2global_read_relation_list[item[4]] = [[relation_key, item[2], item[3], is_read_relation]]
    padding_of_4_space = "".join(['&nbsp;'] * 4)
    for k, v in method2global_read_relation_list.items():
        http_str += '<br>'
        k_longer_key = to_longer_key(k)
        http_str += make_link_html(k_longer_key, k_longer_key)
        http_str += '<br>'
        v.sort(key=lambda e: e[1])
        for vi in v:
            vi_long_key = to_longer_key(vi[0])
            if vi[3]:
                http_str += padding_of_4_space \
                            + 's' + str(vi[1]) + ' ' \
                            + make_link_html(vi_long_key, vi_long_key) \
                            + ' <--- ' + field_key + ' (' + vi[2] + ')'
            else:
                http_str += padding_of_4_space \
                            + 's' + str(vi[1]) + ' ' \
                            + field_key + ' <--- ' \
                            + make_link_html(vi_long_key, vi_long_key) + ' (' + vi[2] + ')'
            http_str += '<br>'
    return http_str


def get_field_read_and_written_relation_html(global_read_relation_list, global_written_relation_list):
    http_str = ''
    method2global_read_relation_list = {}
    is_read_relation = True
    for item in global_read_relation_list:
        if item[1] in method2global_read_relation_list:
            method2global_read_relation_list[item[1]].append([item[0], item[2], item[3], is_read_relation])
        else:
            method2global_read_relation_list[item[1]] = [[item[0], item[2], item[3], is_read_relation]]
    is_read_relation = False
    for item in global_written_relation_list:
        if item[1] in method2global_read_relation_list:
            method2global_read_relation_list[item[1]].append([item[0], item[2], item[3], is_read_relation])
        else:
            method2global_read_relation_list[item[1]] = [[item[0], item[2], item[3], is_read_relation]]
    padding_of_4_space = "".join(['&nbsp;'] * 4)
    for k, v in method2global_read_relation_list.items():
        http_str += '<br>'
        k_longer_key = to_longer_key(k)
        http_str += make_link_html(k_longer_key, k_longer_key)
        http_str += '<br>'
        v.sort(key=lambda e: e[1])
        for vi in v:
            vi_long_key = to_longer_key(vi[0])
            if vi[3]:
                http_str += padding_of_4_space \
                            + 's' + str(vi[1]) + ' ' \
                            + make_link_html(vi_long_key, vi_long_key) \
                            + ' <--- ' + request_str + ' (' + vi[2] + ')'
            else:
                http_str += padding_of_4_space \
                            + 's' + str(vi[1]) + ' ' \
                            + request_str + ' <--- ' \
                            + make_link_html(vi_long_key, vi_long_key) + ' (' + vi[2] + ')'
            http_str += '<br>'
    return http_str


if __name__ == "__main__":

    read_relation = pickle.load(open(read_relation_compressed_path, "rb"))
    written_relation = pickle.load(open(written_relation_compressed_path, "rb"))

    method2relations = pickle.load(open(method2relations_compressed_path, 'rb'))
    method2global_relations = pickle.load(open(method2global_relations_compressed_path, 'rb'))

    fieldFeatureKey2fieldFeatureRelationList = \
        pickle.load(open(fieldFeatureKey2fieldFeatureRelationList_compressed_path, 'rb'))

    LV2relations = pickle.load(open(LV2relations_file_path, 'rb'))
    fieldkey2fieldTypekey = pickle.load(open(fieldkey2fieldTypekey_path, 'rb'))
    LVKey2LVTypeKey = pickle.load(open(LVKey2LVTypeKey_path, 'rb'))
    typekey2fieldkey = pickle.load(open(typekey2fieldkey_path, 'rb'))
    typekey2methodkey = pickle.load(open(typekey2methodkey_path, 'rb'))
    interfaceType = pickle.load(open(interfaceType_path, 'rb'))
    superTypes = pickle.load(open(superTypes_path, 'rb'))
    subTypes = pickle.load(open(subTypes_path, 'rb'))
    fieldKey2typeKey = pickle.load(open(fieldKey2typeKey_path, 'rb'))
    methodKey2typeKey = pickle.load(open(methodKey2typeKey_path, 'rb'))
    type2instance_for_field = pickle.load(open(type2instance_for_field_file_path, 'rb'))
    type2instance_for_local = pickle.load(open(type2instance_for_local_file_path, 'rb'))
    methodKey2srcLoc = pickle.load(open(methodKey2srcLoc_path, 'rb'))
    fieldKey2srcLoc = pickle.load(open(fieldKey2srcLoc_path, 'rb'))
    fieldKey2fieldFeatureCount = pickle.load(open(fieldKey2fieldFeatureCount_path, 'rb'))
    method2lv_dependency_in_dir = pickle.load(open(method2lv_dependency_in_dir_file_path, 'rb'))
    method2lv_dependency_out_dir = pickle.load(open(method2lv_dependency_out_dir_file_path, 'rb'))

    class2field_dependency_in_dir = pickle.load(open(class2field_dependency_in_dir_file_path, 'rb'))
    class2field_dependency_out_dir = pickle.load(open(class2field_dependency_out_dir_file_path, 'rb'))

    # global_method_dependency_in_dir = pickle.load(open(class2method_dependency_in_dir_file_path, 'rb'))
    # global_method_dependency_out_dir = pickle.load(open(class2method_dependency_out_dir_file_path, 'rb'))

    method_size_in = pickle.load(open(method_size_map_in_path, 'rb'))
    method_size_out = pickle.load(open(method_size_map_out_path, 'rb'))

    global_method_size_in = pickle.load(open(global_method_size_map_in_path, 'rb'))
    global_method_size_out = pickle.load(open(global_method_size_map_out_path, 'rb'))

    class2self_responsibility_in = pickle.load(open(class2self_responsibility_in_path, 'rb'))
    class2self_responsibility_out = pickle.load(open(class2self_responsibility_out_path, 'rb'))

    class2self_dependency_in_sum = pickle.load(open(class2self_dependency_in_sum_path, 'rb'))
    class2self_dependency_out_sum = pickle.load(open(class2self_dependency_out_sum_path, 'rb'))

    class2global_dependency_in_sum = pickle.load(open(class2global_dependency_in_sum_path, 'rb'))
    class2global_dependency_out_sum = pickle.load(open(class2global_dependency_out_sum_path, 'rb'))

    method2methodFromOtherClass_in_dir = pickle.load(open(method2methodFromOtherClass_in_dir_path, 'rb'))
    method2methodFromOtherClass_out_dir = pickle.load(open(method2methodFromOtherClass_out_dir_path, 'rb'))

    type_dependency_in = pickle.load(open(type_dependency_in_path, 'rb'))
    type_dependency_out = pickle.load(open(type_dependency_out_path, 'rb'))

    type_size_in = pickle.load(open(type_size_in_path, 'rb'))
    type_size_out = pickle.load(open(type_size_out_path, 'rb'))

    HOST, PORT = '', 8888
    listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listen_socket.bind((HOST, PORT))
    listen_socket.listen(1)
    print('Serving HTTP on host:port  ' + str(host) + ':' + str(PORT) + ' ...')
    while True:
        dependency_html_util.all_id_list_for_js_variable = []
        client_connection, client_address = listen_socket.accept()
        request = client_connection.recv(1024)
        request_str = request.decode("utf-8")
        request_str = request_str.split('\n')[0]
        request_str = request_str[5:-10]
        http_response = "HTTP/1.1 200 OK\r\n"
        http_response += "\r\n"
        shorter_key = to_shorter_key(request_str)
        if request_str.startswith('classes_relation:'):
            type_list_str = request_str[17:]
            type_list = type_list_str.split('&')
            http_response += "<h1>" + "classes relation" + "</h1>\n\n"
            type_list.sort()
            for type_key in type_list:
                http_response += make_link_html(type_key, type_key)
                http_response += '<br>'
            http_response += get_dependency_in_and_out_html(
                method2global_relations, type_list, typekey2methodkey,
                method_size_in, method_size_out, global_method_size_in, global_method_size_out,
                'method', 'm_id_')
        elif request_str == "classes":
            classes_resp_in = [[i, j] for i, j in class2global_dependency_in_sum.items()]
            classes_resp_in.sort(key=lambda e: e[1], reverse=True)
            classes_resp_out = [[i, j] for i, j in class2global_dependency_out_sum.items()]
            classes_resp_out.sort(key=lambda e: e[1], reverse=True)
            http_response += "<h1>" + "class self responsibility in" + "</h1>\n\n"
            for i in range(len(classes_resp_in)):
                mk = classes_resp_in[i][0]
                http_response += make_link_html(mk, mk) \
                                 + "&nbsp;&nbsp;" \
                                 + str(class2self_dependency_in_sum[mk]) \
                                 + "&nbsp;:&nbsp;" \
                                 + str(class2self_dependency_out_sum[mk]) \
                                 + "&nbsp;|&nbsp;" \
                                 + str(class2global_dependency_in_sum[mk]) \
                                 + "&nbsp;:&nbsp;" \
                                 + str(class2global_dependency_out_sum[mk]) \
                                 + "&nbsp;|&nbsp;" \
                                 + str(class2self_responsibility_in[mk]) \
                                 + "&nbsp;:&nbsp;" \
                                 + str(class2self_responsibility_out[mk])
                http_response += '<br>'
            http_response += '<br>'
            http_response += "<h1>" + "class self responsibility out" + "</h1>\n\n"
            for i in range(len(classes_resp_out)):
                mk = classes_resp_out[i][0]
                http_response += make_link_html(mk, mk) \
                                 + "&nbsp;&nbsp;" \
                                 + str(class2self_dependency_in_sum[mk]) \
                                 + "&nbsp;:&nbsp;" \
                                 + str(class2self_dependency_out_sum[mk]) \
                                 + "&nbsp;|&nbsp;" \
                                 + str(class2global_dependency_in_sum[mk]) \
                                 + "&nbsp;:&nbsp;" \
                                 + str(class2global_dependency_out_sum[mk]) \
                                 + "&nbsp;|&nbsp;" \
                                 + str(class2self_responsibility_in[mk]) \
                                 + "&nbsp;:&nbsp;" \
                                 + str(class2self_responsibility_out[mk])
                http_response += '<br>'
        # 函数的源码
        elif request_str.endswith(":src"):
            http_response += "<h1>" + request_str + "</h1>\n\n"
            methodkey = request_str[:-3]
            if methodkey in methodKey2srcLoc:
                src_loc = methodKey2srcLoc[methodkey]
                http_response += get_lines(
                    src_abs_dir + src_loc["fileName"], src_loc["startLine"], src_loc["endLine"])
        # 函数的内容
        elif request_str.endswith(":"):
            http_response += "<h1>" + request_str + "</h1>\n\n"
            return_type = fieldkey2fieldTypekey[request_str + "Return"]
            http_response += 'return type: <a href="http://' + host + ':8888/' + return_type + '">' \
                             + return_type + "</a><br><br>"
            in_type = methodKey2typeKey[request_str]
            http_response += 'in type: <a href="http://' + host + ':8888/' + in_type + '">' + in_type + "</a><br><br>"
            src_ = request_str + "src"
            http_response += 'src: <a href="http://' + host + ':8888/' + src_ + '">' + src_ + "</a><br>"
            http_response += "<br>"
            http_response += get_parameter_and_return_html(request_str)
            # method features
            if shorter_key in method2global_relations:
                method_features = get_method_features(shorter_key)
                http_response += get_method_feature_html(request_str, method_features)
            if shorter_key in method2relations:
                relation_list = method2relations[shorter_key]
                http_response += get_all_local_variable_html(relation_list)
                http_response += get_dependency_html(
                    method2lv_dependency_in_dir[request_str],
                    method2lv_dependency_out_dir[request_str],
                    'local variable', len(request_str), 'lv_id_')
                http_response += get_relation_with_local_html(relation_list)
            if shorter_key in method2global_relations:
                relation_list = method2global_relations[shorter_key]
                relation_list.sort(key=lambda e: e[0])
                http_response += get_relation_without_local_html(relation_list)
        # 局部变量的历程
        elif request_str in LVKey2LVTypeKey:
            http_response += "<h1>" + request_str + "</h1>"
            lvType = LVKey2LVTypeKey[request_str]
            http_response += 'type: <a href="http://' + host + ':8888/' + lvType + '">' + lvType + "</a>"
            http_response += "<br><br>"
            relation_list = LV2relations[request_str]
            relation_list.sort(key=lambda e: e[3])
            for r in relation_list:
                r0 = r[0]
                r1 = r[1]
                if not r0 == request_str:
                    r0 = make_link_html(r0, r0)
                if not r1 == request_str:
                    r1 = make_link_html(r1, r1)
                http_response += 's' + str(r[3]) + ": "
                http_response += r0 + " <--- " + r1
                http_response += ' (' + r[2] + ')'
                http_response += "<br><br>"
        # method feature
        elif is_method_feature_key(request_str):
            http_response += "<h1>" + request_str + "</h1>"
            method_features = get_method_features(to_shorter_key(get_method_key_from_feature(request_str)))
            relation_list = method_features[get_method_feature_index(request_str)]
            relation_list.sort(key=lambda e: e[2])
            for r in relation_list:
                r0long = to_longer_key(r[0])
                r1long = to_longer_key(r[1])
                http_response += 's' + str(r[2]) + '&nbsp;&nbsp;' \
                                 + make_link_html(r0long, r0long) + ' <--- ' \
                                 + make_link_html(r1long, r1long) \
                                 + '&nbsp;&nbsp;' + r[3] + '<br><br>'
        # field feature
        elif request_str in fieldFeatureKey2fieldFeatureRelationList:
            http_response += "<h1>" + request_str + "</h1>"
            relation_list = fieldFeatureKey2fieldFeatureRelationList[request_str]
            http_response += get_field_relation_html(get_field_key_from_feature(request_str), relation_list)
            # for r in relation_list:
            #     print(r)
            #     r0long = to_longer_key(r[2])
            #     r1long = to_longer_key(r[3])
            #     http_response += make_link_html(r0long, r0long) + ' <--- ' \
            #                      + make_link_html(r1long, r1long) + '<br><br>'
        else:
            http_response += "<h1>" + request_str + "</h1>"
            if request_str in interfaceType:
                http_response += "<h1>" + "interface types" + "</h1>"
                interface_types = interfaceType[request_str]
                interface_types = remove_duplicated_item_from_list_retaining_order(interface_types)
                for st in interface_types:
                    http_response += '<a href="http://' + host + ':8888/' + st + '">' + st + "</a>"
                    http_response += "<br><br>"
            if request_str in superTypes:  # 类的父类
                http_response += "<h1>" + "super types" + "</h1>"
                super_types = superTypes[request_str]
                super_types = remove_duplicated_item_from_list_retaining_order(super_types)
                for st in super_types:
                    http_response += '<a href="http://' + host + ':8888/' + st + '">' + st + "</a>"
                    http_response += "<br><br>"
            if request_str in subTypes:  # 类的子类
                http_response += "<h1>" + "sub types" + "</h1>"
                super_types = subTypes[request_str]
                super_types = remove_duplicated_item_from_list_retaining_order(super_types)
                for st in super_types:
                    http_response += '<a href="http://' + host + ':8888/' + st + '">' + st + "</a>"
                    http_response += "<br><br>"
            if request_str in type_dependency_in:
                http_response += "<h1>field types in order</h1>"
                order_list = []
                for tk in type_dependency_in[request_str]:
                    in_size = type_size_in[tk] if tk in type_size_in else 1
                    order_list.append([tk, in_size])
                order_list.sort(key=lambda e: e[1], reverse=True)
                for tk in order_list:
                    in_size = tk[1]
                    tk = tk[0]
                    out_size = type_size_out[tk] if tk in type_size_out else 1
                    http_response += make_link_html(tk, tk) + ' ' + \
                                     str(in_size) + ' | ' + str(out_size)
                    http_response += "<br>"
            if request_str in type_dependency_in:
                http_response += "<h1>field types out order</h1>"
                order_list = []
                for tk in type_dependency_in[request_str]:
                    out_size = type_size_out[tk] if tk in type_size_out else 1
                    order_list.append([tk, out_size])
                order_list.sort(key=lambda e: e[1], reverse=True)
                for tk in order_list:
                    out_size = tk[1]
                    tk = tk[0]
                    in_size = type_size_in[tk] if tk in type_size_in else 1
                    http_response += make_link_html(tk, tk) + ' ' + \
                                     str(in_size) + ' | ' + str(out_size)
                    http_response += "<br>"
            if request_str in type_dependency_out:
                http_response += "<h1>is field of types in order</h1>"
                order_list = []
                for tk in type_dependency_out[request_str]:
                    in_size = type_size_in[tk] if tk in type_size_in else 1
                    order_list.append([tk, in_size])
                order_list.sort(key=lambda e: e[1], reverse=True)
                for tk in order_list:
                    in_size = tk[1]
                    tk = tk[0]
                    out_size = type_size_out[tk] if tk in type_size_out else 1
                    http_response += make_link_html(tk, tk) + ' ' + \
                                     str(in_size) + ' | ' + str(out_size)
                    http_response += "<br>"
            if request_str in type_dependency_out:
                http_response += "<h1>is field of types out order</h1>"
                order_list = []
                for tk in type_dependency_out[request_str]:
                    out_size = type_size_out[tk] if tk in type_size_out else 1
                    order_list.append([tk, out_size])
                order_list.sort(key=lambda e: e[1], reverse=True)
                for tk in order_list:
                    out_size = tk[1]
                    tk = tk[0]
                    in_size = type_size_in[tk] if tk in type_size_in else 1
                    http_response += make_link_html(tk, tk) + ' ' + \
                                     str(in_size) + ' | ' + str(out_size)
                    http_response += "<br>"
            # 类的属性 field
            if request_str in typekey2fieldkey:
                http_response += "<h1>" + "fields" + "</h1>"
                field_keys = typekey2fieldkey[request_str]
                field_keys = remove_duplicated_item_from_list_retaining_order(field_keys)
                for fk in field_keys:
                    http_response += '<a href="http://' + host + ':8888/' + fk + '">' + fk + "</a>"
                    http_response += "<br>"
            if request_str in class2field_dependency_in_dir:
                http_response += get_dependency_html(
                    class2field_dependency_in_dir[request_str],
                    class2field_dependency_out_dir[request_str],
                    'field', len(request_str), 'f_id_')
            # 类的方法
            if request_str in typekey2methodkey:
                http_response += "<h1>" + "methods" + "</h1>"
                field_keys = typekey2methodkey[request_str]
                field_keys = remove_duplicated_item_from_list_retaining_order(field_keys)
                for fk in field_keys:
                    http_response += '<a href="http://' + host + ':8888/' + fk + '">' + fk + "</a>"
                    http_response += "<br>"
            if request_str in typekey2methodkey:
                http_response += get_dependency_in_and_out_html(
                    method2global_relations, [request_str], typekey2methodkey,
                    method_size_in, method_size_out, global_method_size_in, global_method_size_out,
                    'method', 'm_id_',len(request_str))
                # get_dependency_html(
                # global_method_dependency_in_dir[request_str],
                # global_method_dependency_out_dir[request_str],
                # 'method', len(request_str), 'm_id_')
            # 属性
            if request_str in fieldkey2fieldTypekey:
                fieldType = fieldkey2fieldTypekey[request_str]
                http_response += 'type: <a href="http://' + host + ':8888/' + fieldType + '">' + fieldType + "</a><br><br>"
                if request_str in fieldKey2typeKey:
                    in_type = fieldKey2typeKey[request_str]
                    http_response += 'in type: <a href="http://' + host + ':8888/' + in_type + '">' + in_type + "</a>"
                    http_response += "<br>"
                if is_parameter_key(request_str):
                    mk = get_method_key_from_parameter_key(request_str)
                    http_response += 'in method: <a href="http://' + host + ':8888/' + mk + '">' + mk + "</a>"
                    http_response += "<br>"
                if is_return_key(request_str):
                    mk = request_str[0:-6]
                    http_response += 'in method: <a href="http://' + host + ':8888/' + mk + '">' + mk + "</a>"
                    http_response += "<br>"
                if request_str in fieldKey2srcLoc:
                    http_response += "<h1>src</h1>"
                    src_loc = fieldKey2srcLoc[request_str]
                    http_response += get_lines(
                        src_abs_dir + src_loc["fileName"], src_loc["startLine"], src_loc["endLine"])
                if request_str in fieldKey2fieldFeatureCount:
                    http_response += get_field_feature_html(request_str, fieldKey2fieldFeatureCount[request_str])
            http_response += "<br><br>"
            if shorter_key in read_relation or shorter_key in written_relation:
                http_response += "<h1>is read and written by:</h1>"
                global_read_relation_list = read_relation[shorter_key] if shorter_key in read_relation else []
                global_written_relation_list = written_relation[shorter_key] if shorter_key in written_relation else []
                http_response += get_field_read_and_written_relation_html(global_read_relation_list,
                                                                          global_written_relation_list)
            if request_str in type2instance_for_field:  # 类的实例 属性
                field_keys = type2instance_for_field[request_str]
                instance_for_param = []
                instance_for_return = []
                instance_for_field = []
                for fk in field_keys:
                    if is_parameter_key(fk):
                        instance_for_param.append(fk)
                    elif is_return_key(fk):
                        instance_for_return.append(fk)
                    else:
                        instance_for_field.append(fk)
                if len(instance_for_param) > 0:
                    http_response += "<h1>" + "instance for paramter" + "</h1>"
                    for fk in instance_for_param:
                        http_response += make_link_html(fk, fk)
                        http_response += "<br>"
                if len(instance_for_return) > 0:
                    http_response += "<h1>" + "instance for return" + "</h1>"
                    for fk in instance_for_return:
                        http_response += make_link_html(fk, fk)
                        http_response += "<br>"
                if len(instance_for_field) > 0:
                    http_response += "<h1>" + "instance for field" + "</h1>"
                    for fk in instance_for_field:
                        http_response += make_link_html(fk, fk)
                        http_response += "<br>"
            if request_str in type2instance_for_local:  # 类的实例 局部变量
                http_response += "<h1>" + "instance for local" + "</h1>"
                field_keys = type2instance_for_local[request_str]
                for fk in field_keys:
                    http_response += '<a href="http://' + host + ':8888/' + fk + '">' + fk + "</a>"
                    http_response += "<br>"
        http_response += get_js_code_str()
        http_response = decompress_by_replace(http_response, [])
        print(request_str)
        client_connection.sendall(http_response.encode("utf-8"))
        client_connection.close()
