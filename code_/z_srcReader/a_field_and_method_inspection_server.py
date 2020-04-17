#!/usr/bin/python
# -*- coding: UTF-8 -*-
import pickle
import socket
import sys
import traceback

from code_.d_methodAndFieldFeature.a_methodFeature import get_method_feature_relation_list, method_feature_len
from code_.util.file_util import \
    LV2relations_file_path, LVKey2LVTypeKey_path, \
    fieldkey2fieldTypekey_path, typekey2fieldkey_path, \
    typekey2methodkey_path, superTypes_path, subTypes_path, fieldKey2typeKey_path, methodKey2typeKey_path, \
    type2instance_for_field_file_path, type2instance_for_local_file_path, methodKey2srcLoc_path, get_lines, src_abs_dir, \
    fieldKey2srcLoc_path, interfaceType_path, fieldKey2fieldFeatureCount_path, \
    method2lv_dependency_in_dir_file_path, method2lv_dependency_out_dir_file_path, \
    class2field_dependency_in_dir_file_path, class2field_dependency_out_dir_file_path, \
    read_relation_compressed_path, \
    written_relation_compressed_path, method2relations_compressed_path, method2global_relations_compressed_path, \
    fieldFeatureKey2fieldFeatureRelationList_compressed_path, \
    method_size_map_in_path, method_size_map_out_path, global_method_size_map_in_path, global_method_size_map_out_path, \
    class2self_responsibility_in_path, class2self_responsibility_out_path, class2self_dependency_in_sum_path, \
    class2self_dependency_out_sum_path, class2global_dependency_in_sum_path, class2global_dependency_out_sum_path, \
    method2methodFromOtherClass_in_dir_path, \
    method2methodFromOtherClass_out_dir_path, type_dependency_in_path, type_dependency_out_path, type_size_out_path, \
    type_size_in_path, global_field_consumption_dependency_out_dir_path, \
    global_field_consumption_dependency_in_dir_path, get_file_into_html, \
    method2dependency_in_inside_method_compressed_path, method2dependency_out_inside_method_compressed_path
from code_.util.html_util import host, make_h1_html
from code_.util.key_conversion_util import decompress_by_replace, to_shorter_key_if_compressed, \
    to_longer_key_if_compressed, convert_dependency_to_longer_key
from code_.util.key_util import get_method_feature_key, is_parameter_key, is_return_key, \
    get_method_key_from_parameter_key, is_method_feature_key, get_method_feature_index, get_method_key_from_feature, \
    get_field_feature_key, get_field_key_from_feature, is_condition_key, is_reference_key, is_lv_key, is_field_key, \
    is_field_reference_key, get_key_from_dependency_inside_method_key
from code_.z_srcReader import dependency_html_util
from code_.z_srcReader.big_method_separation_util import separation
from code_.z_srcReader.dependency_html_util import get_size_string, get_dependency_in_and_out_html, \
    dependency_colors, get_zero_degree, recur_for_dependency_inside_method
from code_.z_srcReader.field_consumption_html_util import get_field_consumption_html_in_and_out

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


def get_method_structure_html(relations):
    html_str = make_h1_html("method structure", 'ms')
    last_key = ''
    keys = []
    for r in relations:
        para_k = r[2]
        linear_k = r[3]
        if last_key == para_k:
            continue
        last_key = para_k
        k = str(linear_k).rjust(4) + ' : ' + '(' + para_k + ')'
        keys.append(k.replace(' ', '&nbsp;'))
    return html_str + "<br>".join(keys)


def get_parameter_and_return_html(method_key):
    html_str = ""
    html_str += make_h1_html("parameters and return:")
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
    html_str = make_h1_html("all local variables:")
    local_variables = []
    order_min_map = {}
    order_max_map = {}
    order_count_map = {}
    node2node = {}
    for r in relation_list:
        order = r[3]
        line_node = 's_' + str(order)
        if line_node not in node2node:
            node2node[line_node] = {}
        r0long = to_longer_key_if_compressed(r[0])
        r1long = to_longer_key_if_compressed(r[1])
        if r0long in LVKey2LVTypeKey:
            if is_parameter_key(r1long):
                local_variables.append(r1long)
            if r0long not in node2node:
                node2node[r0long] = {}
            node2node[r0long][line_node] = ''
            node2node[line_node][r0long] = ''
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
        if is_parameter_key(r1long):
            if r1long not in node2node:
                node2node[r1long] = {}
            node2node[line_node][r1long] = ''
            node2node[r1long][line_node] = ''
        if r1long in LVKey2LVTypeKey:
            if r1long not in node2node:
                node2node[r1long] = {}
            node2node[r1long][line_node] = ''
            node2node[line_node][r1long] = ''
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
    return html_str, node2node, local_variables


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
            else:
                dependency_in_dir_list.sort()
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


def get_dependency_html(all_lv_key, dependency_in_dir, dependency_out_dir, id_str, type_key_len, id_head):
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
    intersect = list(set.intersection(set(out_zero_lv_list), set(in_zero_lv_list)))
    html_str = make_h1_html(id_str + ' dependency in:', id_str[0] + 'd')
    id_count = 0
    for lv in out_zero_lv_list:
        if lv in intersect:
            continue
        id_count += 1
        html_str += recur_for_dependency(lv, dependency_in_dir, 0, [],
                                         type_key_len, [id_head + str(id_count)], method_size_in,
                                         global_method_size_in, method2methodFromOtherClass_in_dir)
        html_str += '<br>'
    html_str += '<h1>' + id_str + ' dependency out:</h1>'
    for lv in in_zero_lv_list:
        if lv in intersect:
            continue
        id_count += 1
        html_str += recur_for_dependency(lv, dependency_out_dir, 0, [],
                                         type_key_len, [id_head + str(id_count)], method_size_out,
                                         global_method_size_out, method2methodFromOtherClass_out_dir)
        html_str += '<br>'
    html_str += '<h1>' + id_str + ' not involved:</h1>'
    for k in all_lv_key:
        if k in intersect or (k not in dependency_in_dir and k not in dependency_out_dir):
            html_str += make_link_html(k, k)
            html_str += '<br>'
    return html_str


def get_relation_with_local_html(relation_list):
    html_str = make_h1_html("relations with local:")
    for r in relation_list:
        html_str += "s" + str(r[3]) + ": "
        r0long = to_longer_key_if_compressed(r[0])
        r1long = to_longer_key_if_compressed(r[1])
        html_str += '<a href="http://' + host + ':8888/' + r0long + '">' + r0long + "</a>" + " <--- " + \
                    '<a href="http://' + host + ':8888/' + r1long + '">' + r1long + "</a>"
        html_str += ' (' + r[2] + ')'
        html_str += "<br><br>"
    return html_str


def get_relation_without_local_html(relation_list, node2node):
    html_str = make_h1_html("relations without local:", 'rwl')
    sub_graphs, node_too_large = separate_method(node2node)
    html_str += "<h2>local variables too large:</h2>"
    resulted_relations_h_ = "<h3>resulted relations:</h3>"
    for n_too_large in node_too_large:
        html_str += make_link_html(n_too_large, n_too_large) + '  ' + str(len(node_too_large[n_too_large]))
        html_str += '<br>'
    for lines, local_vars in sub_graphs:
        resolved_local_str = ''
        delete_resolved_local_str_flag = False
        if len(local_vars) > 0:
            html_str += "<h2>resolved local variables:</h2>"
            resolved_local_str += "<h2>resolved local variables:</h2>"
            local_vars.sort()
            delete_resolved_local_str_flag = True
            for local_var in local_vars:
                link_html = make_link_html(local_var, local_var)
                html_str += link_html
                html_str += '<br>'
                resolved_local_str += link_html
                resolved_local_str += '<br>'
        html_str += resulted_relations_h_
        for r in relation_list:
            r0long = to_longer_key_if_compressed(r[0])
            r1long = to_longer_key_if_compressed(r[1])
            order_str = str(r[2])
            if 's_' + order_str in lines:
                if is_reference_key(r0long) or is_condition_key(r0long):
                    continue
                delete_resolved_local_str_flag = False
                html_str += r[4] + '<br>' if r[4] else ''
                html_str += 's' + order_str + ": " + \
                            make_link_html(r0long, r0long) + " <--- " + make_link_html(r1long, r1long) + \
                            ' (' + r[3] + ')'
                html_str += "<br>"
        if html_str.endswith(resulted_relations_h_):
            html_str = html_str[:-len(resulted_relations_h_)]
        if delete_resolved_local_str_flag:
            html_str = html_str[:-len(resolved_local_str)]
    html_str += make_h1_html("about conditions:")
    for lines, local_vars in sub_graphs:
        resolved_local_str = ''
        delete_resolved_local_str_flag = False
        if len(local_vars) > 0:
            html_str += "<h2>resolved local variables:</h2>"
            resolved_local_str += "<h2>resolved local variables:</h2>"
            local_vars.sort()
            delete_resolved_local_str_flag = True
            for local_var in local_vars:
                link_html = make_link_html(local_var, local_var)
                html_str += link_html
                html_str += '<br>'
                resolved_local_str += link_html
                resolved_local_str += '<br>'
        html_str += resulted_relations_h_
        for r in relation_list:
            r0long = to_longer_key_if_compressed(r[0])
            r1long = to_longer_key_if_compressed(r[1])
            order_str = str(r[2])
            if 's_' + order_str in lines:
                if not is_condition_key(r0long):
                    continue
                delete_resolved_local_str_flag = False
                html_str += r[4] + '<br>' if r[4] else ''
                html_str += 's' + order_str + ": " + \
                            make_link_html(r0long, r0long) + " <--- " + make_link_html(r1long, r1long) + \
                            ' (' + r[3] + ')'
                html_str += "<br>"
        if html_str.endswith(resulted_relations_h_):
            html_str = html_str[:-len(resulted_relations_h_)]
        if delete_resolved_local_str_flag:
            html_str = html_str[:-len(resolved_local_str)]
    return html_str


def make_link_html(text, link):
    return '<a href="http://' + host + ':8888/' + link + '">' + text + "</a>"


def get_method_feature_html(methodKey, features):
    html_str = make_h1_html("method features:", 'mf')
    rjust = 10
    return_str = "return".rjust(rjust)
    condition_str = "condition".rjust(rjust)
    field_str = "field".rjust(rjust)
    method_call_str = "methodCall".rjust(rjust)
    reference_str = "reference".rjust(rjust)
    parameter_str = "parameter".rjust(rjust)
    local_str = "local".rjust(rjust)
    str_list = [
        "# 0: " + return_str + " = parameter",
        "# 1: " + return_str + " = local",
        "# 2: " + return_str + " = field",
        "# 3: " + return_str + " = methodCall",

        "# 4: " + return_str + " = parameter",
        "# 5: " + condition_str + " = parameter",
        "# 6: " + field_str + " = parameter",
        "# 7: " + method_call_str + " = parameter",
        "# 8: " + reference_str + " = parameter",

        "# 09: " + condition_str + " = parameter",
        "# 10: " + condition_str + " = local",
        "# 11: " + condition_str + " = field",
        "# 12: " + condition_str + " = methodCall",

        "# 13: " + field_str + " = parameter",
        "# 14: " + field_str + " = local",
        "# 15: " + field_str + " = field",
        "# 16: " + field_str + " = methodCall",

        "# 17: " + return_str + " = field",
        "# 18: " + condition_str + " = field",
        "# 19: " + field_str + " = field",
        "# 20: " + method_call_str + " = field",
        "# 21: " + reference_str + " = field",

        "# 22: " + method_call_str + " = parameter",
        "# 23: " + method_call_str + " = local",
        "# 24: " + method_call_str + " = field",
        "# 25: " + method_call_str + " = methodCall",

        "# 26: " + return_str + " = methodCall",
        "# 27: " + local_str + " = methodCall",
        "# 28: " + condition_str + " = methodCall",
        "# 29: " + field_str + " = methodCall",
        "# 30: " + method_call_str + " = methodCall",
        "# 31: " + reference_str + " = methodCall",

        "# 32: " + reference_str + " = parameter",
        "# 33: " + reference_str + " = local",
        "# 34: " + reference_str + " = field",
        "# 35: " + reference_str + " = methodCall",

        "# 36: " + parameter_str + " = parameter",
        "# 37: " + parameter_str + " = local",
        "# 38: " + parameter_str + " = field",
        "# 39: " + parameter_str + " = methodCall",
    ]
    for i in range(len(str_list)):
        str_list[i] = str_list[i].replace(' ', '&nbsp;')

    blank_space_index = [3, 8, 12, 16, 21, 25, 31, 35]
    for i in range(method_feature_len):
        feature_count = len(features[i])
        if feature_count > 0:
            feature_count_str = ' ' + str(feature_count)
            html_str += make_link_html(str_list[i] + feature_count_str,
                                       get_method_feature_key(methodKey, i)) + "<br>"
            if i in blank_space_index:
                html_str += "<br>"
    return html_str


def get_field_feature_html(fieldKey, features):
    html_str = make_h1_html("field features:")
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
    html_str += make_link_html('# 10: self assignment ' + str(features[10]),
                               get_field_feature_key(fieldKey, 10)) + '<br><br>'
    html_str = html_str.replace('genericField', '<b>genericField</b>')
    return html_str


def convert_python_list2js_list(var_name, python_list):
    js_str_list = ['var ' + var_name + ' = [']
    for i in python_list:
        js_str_list.append("'" + str(i) + "',")
    js_str_list.append('];')
    return ''.join(js_str_list)


def get_js_code_str():
    print('get_js_code_str')
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
        is_read_relation = to_longer_key_if_compressed(item[1]) == field_key
        relation_key = item[0] if is_read_relation else item[1]
        if item[1] in method2global_read_relation_list:
            method2global_read_relation_list[item[4]].append([relation_key, item[2], item[3], is_read_relation])
        else:
            method2global_read_relation_list[item[4]] = [[relation_key, item[2], item[3], is_read_relation]]
    padding_of_4_space = "".join(['&nbsp;'] * 4)
    for k, v in method2global_read_relation_list.items():
        http_str += '<br>'
        k_longer_key = to_longer_key_if_compressed(k)
        http_str += make_link_html(k_longer_key, k_longer_key)
        http_str += '<br>'
        v.sort(key=lambda e: e[1])
        for vi in v:
            vi_long_key = to_longer_key_if_compressed(vi[0])
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
        k_longer_key = to_longer_key_if_compressed(k)
        http_str += make_link_html(k_longer_key, k_longer_key)
        http_str += '<br>'
        v.sort(key=lambda e: e[1])
        for vi in v:
            vi_long_key = to_longer_key_if_compressed(vi[0])
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


def separate_method(node2node):
    sub_graphs, node_too_large = separation(node2node)
    sub_graphs_return = []
    for g in sub_graphs:
        variable_node = []
        line_node = []
        for node in g:
            if node.startswith('s_'):
                line_node.append(node)
            else:
                variable_node.append(node)
        sub_graphs_return.append([line_node, variable_node])
    return sub_graphs_return, node_too_large


def get_dependency_html_inside_method(dependency_in, dependency_out):
    dependency_in = convert_dependency_to_longer_key(dependency_in)
    dependency_out = convert_dependency_to_longer_key(dependency_out)
    all_key = {}
    for k, v in dependency_in.items():
        all_key[k] = ''
        for vi in v:
            all_key[vi] = ''
    out_zero_key_list = get_zero_degree(all_key, dependency_out)
    id_count = 0
    id_index_head = 'insm_id_'
    html_str_list = [make_h1_html('method actions', 'ma')]
    out_zero_key_list.sort()
    for key in out_zero_key_list:
        pos_key = get_key_from_dependency_inside_method_key(key)
        if is_lv_key(pos_key):
            continue
        if is_field_key(pos_key) and len(dependency_in[key]) == 1:
            reference = list(dependency_in[key].keys())[0]
            reference = reference[reference.find(' ') + 1:reference.rfind(' ')]
            if is_field_reference_key(reference):
                continue
        if is_condition_key(pos_key):
            continue
        id_count += 1
        print(key)
        html_str_list.extend(
            recur_for_dependency_inside_method(key, [id_index_head + str(id_count)], [], dependency_in))
        html_str_list.append('<br>')
    html_str_list.append(make_h1_html('method conditions', 'mc'))
    for key in out_zero_key_list:
        pos1 = key.find(' ')
        pos = key.rfind(' ')
        if not is_condition_key(key[pos1 + 1:pos]):
            continue
        id_count += 1
        print(key)
        html_str_list.extend(
            recur_for_dependency_inside_method(key, [id_index_head + str(id_count)], [], dependency_in))
        html_str_list.append('<br>')
    return ''.join(html_str_list)


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

    field_consumption_dependency_in_dir = pickle.load(open(global_field_consumption_dependency_in_dir_path, 'rb'))
    field_consumption_dependency_out_dir = pickle.load(open(global_field_consumption_dependency_out_dir_path, 'rb'))

    method2methodFromOtherClass_in_dir = pickle.load(open(method2methodFromOtherClass_in_dir_path, 'rb'))
    method2methodFromOtherClass_out_dir = pickle.load(open(method2methodFromOtherClass_out_dir_path, 'rb'))

    type_dependency_in = pickle.load(open(type_dependency_in_path, 'rb'))
    type_dependency_out = pickle.load(open(type_dependency_out_path, 'rb'))

    type_size_in = pickle.load(open(type_size_in_path, 'rb'))
    type_size_out = pickle.load(open(type_size_out_path, 'rb'))

    method2dependency_in_inside_method = pickle.load(open(method2dependency_in_inside_method_compressed_path, 'rb'))
    method2dependency_out_inside_method = pickle.load(open(method2dependency_out_inside_method_compressed_path, 'rb'))

    HOST, PORT = '', 8888
    listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listen_socket.bind((HOST, PORT))
    listen_socket.listen(1)
    print('Serving HTTP on host:port  ' + str(host) + ':' + str(PORT) + ' ...')
    while True:
        dependency_html_util.all_id_list_for_js_variable.clear()
        client_connection, client_address = listen_socket.accept()
        request = client_connection.recv(1024)
        request_str = request.decode("utf-8")
        request_str = request_str.split('\n')[0]
        request_str = request_str[5:-10]
        http_response = "HTTP/1.1 200 OK\r\n"
        http_response += "\r\n"
        try:
            shorter_key = to_shorter_key_if_compressed(request_str)
            if request_str.startswith('parameter_generation_consumption:'):
                package_and_searching_method = request_str[33:].split('@')
                package_and_classes_list = package_and_searching_method[0].split('&')
                type_list = []
                starts_with_str = []
                for package_and_classes in package_and_classes_list:
                    package_and_classes = package_and_classes.split(':')
                    package_str = package_and_classes[0]
                    if len(package_and_classes) > 1:
                        classes_str = package_and_classes[1].split(',')
                        for class_str in classes_str:
                            starts_with_str.append(package_str + '.' + class_str + '.')
                            type_list.append(package_str + '.' + class_str)
                    else:
                        starts_with_str.append(package_str)
                for k, v in typekey2fieldkey.items():
                    for s in starts_with_str:
                        if k.startswith(s):
                            type_list.append(k)
                http_response += make_h1_html("parameter generation and consumption")
                type_list.sort()
                for type_key in type_list:
                    http_response += make_link_html(type_key, type_key)
                    http_response += '<br>'
                search_method_key = ''
                if len(package_and_searching_method) > 1:
                    search_method_key = package_and_searching_method[1]
                print('search field key :' + search_method_key)
                http_response += get_field_consumption_html_in_and_out(
                    field_consumption_dependency_in_dir, field_consumption_dependency_out_dir,
                    type_list, fieldkey2fieldTypekey.keys(), 'field', 'f_gc_id', search_method_key)
            elif request_str.startswith('package_classes_relation:'):
                # package_classes_relation:package&package:class&package:class,class,class@methodkey
                package_and_searching_method = request_str[25:].split('@')
                package_and_classes_list = package_and_searching_method[0].split('&')
                type_list = []
                starts_with_str = []
                for package_and_classes in package_and_classes_list:
                    package_and_classes = package_and_classes.split(':')
                    package_str = package_and_classes[0]
                    if len(package_and_classes) > 1:
                        classes_str = package_and_classes[1].split(',')
                        for class_str in classes_str:
                            starts_with_str.append(package_str + '.' + class_str + '.')
                            type_list.append(package_str + '.' + class_str)
                    else:
                        starts_with_str.append(package_str)
                for k, v in typekey2fieldkey.items():
                    for s in starts_with_str:
                        if k.startswith(s):
                            type_list.append(k)
                http_response += make_h1_html("package classes relation")
                type_list.sort()
                for type_key in type_list:
                    http_response += make_link_html(type_key, type_key)
                    http_response += '<br>'
                search_method_key = ''
                if len(package_and_searching_method) > 1:
                    search_method_key = package_and_searching_method[1]
                print('search method key :' + search_method_key)
                http_response += get_dependency_in_and_out_html(
                    method2global_relations, type_list, typekey2methodkey,
                    method_size_in, method_size_out, global_method_size_in, global_method_size_out,
                    'method', 'm_id_', search_method_key=search_method_key)
                print('done join html')
            elif request_str.startswith('package:'):
                type_list = []
                package_str = request_str[8:]
                for k, v in typekey2fieldkey.items():
                    if k.startswith(package_str):
                        type_list.append(k)
                http_response += make_h1_html("classes relation")
                type_list.sort()
                for type_key in type_list:
                    http_response += make_link_html(type_key, type_key)
                    http_response += '<br>'
                http_response += get_dependency_in_and_out_html(
                    method2global_relations, type_list, typekey2methodkey,
                    method_size_in, method_size_out, global_method_size_in, global_method_size_out,
                    'method', 'm_id_')
            elif request_str.startswith('classes_relation:'):
                type_list_str = request_str[17:]
                type_list = type_list_str.split('&')
                http_response += make_h1_html("classes relation")
                type_list.sort()
                for type_key in type_list:
                    http_response += make_link_html(type_key, type_key)
                    http_response += '<br>'
                http_response += get_dependency_in_and_out_html(
                    method2global_relations, type_list, typekey2methodkey,
                    method_size_in, method_size_out, global_method_size_in, global_method_size_out,
                    'method', 'm_id_')
            elif request_str.startswith("classes"):
                classes_finding_str = request_str.split('@')
                if len(classes_finding_str) > 1:
                    classes_finding_str = classes_finding_str[1]
                else:
                    classes_finding_str = ''
                classes_resp_in = [[i, j] for i, j in class2global_dependency_in_sum.items()]
                classes_resp_in.sort(key=lambda e: e[1], reverse=True)
                classes_resp_out = [[i, j] for i, j in class2global_dependency_out_sum.items()]
                classes_resp_out.sort(key=lambda e: e[1], reverse=True)
                http_response += make_h1_html("class self responsibility in")
                for i in range(len(classes_resp_in)):
                    mk = classes_resp_in[i][0]
                    if not mk.find(classes_finding_str) > -1:
                        continue
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
                http_response += make_h1_html("class self responsibility out")
                for i in range(len(classes_resp_out)):
                    mk = classes_resp_out[i][0]
                    if not mk.find(classes_finding_str) > -1:
                        continue
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
                http_response += make_h1_html(request_str)
                methodkey = request_str[:-3]
                if methodkey in methodKey2srcLoc:
                    src_loc = methodKey2srcLoc[methodkey]
                    http_response += get_lines(
                        src_abs_dir + src_loc["fileName"], src_loc["startLine"], src_loc["endLine"])
            # type src
            elif request_str.endswith("-src"):
                http_response += make_h1_html(request_str)
                type_key = request_str[:-4]
                src_found_flag = False
                for fk in typekey2fieldkey[type_key]:
                    if fk in fieldKey2srcLoc:
                        src_loc = fieldKey2srcLoc[fk]
                        src_found_flag = True
                if not src_found_flag:
                    for mk in typekey2methodkey[type_key]:
                        if mk in methodKey2srcLoc:
                            src_loc = methodKey2srcLoc[mk]
                            src_found_flag = True
                if src_found_flag:
                    http_response += get_file_into_html(src_abs_dir + src_loc["fileName"])
            # 函数的内容
            elif request_str.endswith(":"):
                http_response += make_h1_html(request_str)
                return_type = fieldkey2fieldTypekey[request_str + "Return"]
                http_response += 'return type: <a href="http://' + host + ':8888/' + return_type + '">' \
                                 + return_type + "</a><br><br>"
                in_type = methodKey2typeKey[request_str]
                http_response += 'in type: <a href="http://' + host + ':8888/' + in_type + '">' + in_type + "</a><br><br>"
                src_ = request_str + "src"
                http_response += 'src: <a href="http://' + host + ':8888/' + src_ + '">' + src_ + "</a><br>"
                http_response += "<br>"
                if shorter_key in method2relations:
                    http_response += get_method_structure_html(method2relations[shorter_key])
                http_response += get_parameter_and_return_html(request_str)
                # method features
                if shorter_key in method2global_relations:
                    method_features = get_method_features(shorter_key)
                    http_response += get_method_feature_html(request_str, method_features)
                if shorter_key in method2relations:
                    all_local_html, local_node2node, all_lv_key = \
                        get_all_local_variable_html(method2relations[shorter_key])
                    http_response += all_local_html
                    all_lv_key.sort()
                    http_response += get_dependency_html(
                        all_lv_key,
                        method2lv_dependency_in_dir[request_str],
                        method2lv_dependency_out_dir[request_str],
                        'local variable', len(request_str), 'lv_id_')
                if shorter_key in method2dependency_in_inside_method:
                    http_response += get_dependency_html_inside_method(
                        method2dependency_in_inside_method[shorter_key],
                        method2dependency_out_inside_method[shorter_key])
                if shorter_key in method2global_relations:
                    if shorter_key not in method2relations:
                        local_node2node = {}
                    relation_list = method2global_relations[shorter_key]
                    relation_list.sort(key=lambda e: e[2])
                    http_response += get_relation_without_local_html(relation_list, local_node2node)
                if shorter_key in method2relations:
                    http_response += get_relation_with_local_html(method2relations[shorter_key])
            # 局部变量的历程
            elif request_str in LVKey2LVTypeKey:
                http_response += make_h1_html(request_str)
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
                http_response += make_h1_html(request_str)
                method_features = get_method_features(
                    to_shorter_key_if_compressed(get_method_key_from_feature(request_str)))
                relation_list = method_features[get_method_feature_index(request_str)]
                relation_list.sort(key=lambda e: e[2])
                for r in relation_list:
                    r0long = to_longer_key_if_compressed(r[0])
                    r1long = to_longer_key_if_compressed(r[1])
                    http_response += 's' + str(r[2]) + '&nbsp;&nbsp;' \
                                     + make_link_html(r0long, r0long) + ' <--- ' \
                                     + make_link_html(r1long, r1long) \
                                     + '&nbsp;&nbsp;' + r[3] + '<br><br>'
            # field feature
            elif request_str in fieldFeatureKey2fieldFeatureRelationList:
                http_response += make_h1_html(request_str)
                relation_list = fieldFeatureKey2fieldFeatureRelationList[request_str]
                http_response += get_field_relation_html(get_field_key_from_feature(request_str), relation_list)
                # for r in relation_list:
                #     print(r)
                #     r0long = to_longer_key(r[2])
                #     r1long = to_longer_key(r[3])
                #     http_response += make_link_html(r0long, r0long) + ' <--- ' \
                #                      + make_link_html(r1long, r1long) + '<br><br>'
            else:
                http_response += make_h1_html(request_str)
                if request_str in typekey2fieldkey or request_str in typekey2methodkey:
                    src_ = request_str + "-src"
                    http_response += 'src: <a href="http://' + host + ':8888/' + src_ + '">' + src_ + "</a><br>"
                if request_str in interfaceType:
                    http_response += make_h1_html("interface types")
                    interface_types = interfaceType[request_str]
                    interface_types = remove_duplicated_item_from_list_retaining_order(interface_types)
                    for st in interface_types:
                        http_response += '<a href="http://' + host + ':8888/' + st + '">' + st + "</a>"
                        http_response += "<br><br>"
                if request_str in superTypes:  # 类的父类
                    http_response += make_h1_html("super types")
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
                    all_lv_key = []
                    for k, v in class2field_dependency_in_dir[request_str].items():
                        all_lv_key.append(k)
                        for vi in v:
                            all_lv_key.append(vi)
                    all_lv_key = list(set(all_lv_key))
                    http_response += get_dependency_html(
                        all_lv_key,
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
                        'method', 'm_id_', len(request_str))
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
                    global_written_relation_list = written_relation[
                        shorter_key] if shorter_key in written_relation else []
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
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            error = '<br>'.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            http_response += error
        http_response += get_js_code_str()
        http_response = decompress_by_replace(http_response, [])
        print(request_str)
        client_connection.sendall(http_response.encode("utf-8"))
        client_connection.close()
