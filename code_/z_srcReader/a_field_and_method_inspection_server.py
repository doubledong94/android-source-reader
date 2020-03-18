#!/usr/bin/python
# -*- coding: UTF-8 -*-
import pickle
import socket

from code_.util.file_util import \
    LV2relations_file_path, LVKey2LVTypeKey_path, \
    fieldkey2fieldTypekey_path, typekey2fieldkey_path, \
    typekey2methodkey_path, superTypes_path, subTypes_path, fieldKey2typeKey_path, methodKey2typeKey_path, \
    type2instance_for_field_file_path, type2instance_for_local_file_path, methodKey2srcLoc_path, get_lines, src_abs_dir, \
    fieldKey2srcLoc_path, interfaceType_path, methodKey2methodFeature_file_path, fieldKey2fieldFeature_file_path, \
    method2lv_dependency_in_dir_file_path, method2lv_dependency_out_dir_file_path, \
    class2field_dependency_in_dir_file_path, class2field_dependency_out_dir_file_path, \
    class2method_dependency_in_dir_file_path, class2method_dependency_out_dir_file_path, read_relation_compressed_path, \
    written_relation_compressed_path, method2relations_compressed_path, method2global_relations_compressed_path, \
    methodKey2methodFeatureRelationList_compressed_path, fieldKey2fieldFeatureRelationList_compressed_path, \
    method_size_map_in_path, method_size_map_out_path, global_method_size_map_in_path, global_method_size_map_out_path, \
    class2self_responsibility_in_path, class2self_responsibility_out_path, class2self_dependency_in_sum_path, \
    class2self_dependency_out_sum_path, class2global_dependency_in_sum_path, class2global_dependency_out_sum_path, \
    get_method_clusters_path, method_clusters_path, method2methodFromOtherClass_in_dir_path, \
    method2methodFromOtherClass_out_dir_path
from code_.util.key_util import get_feature_key, is_parameter_key, is_return_key, get_method_key_from_parameter_key
from code_.y_data_compression_and_decompression.b_key_conversion import decompress_by_replace, to_shorter_key, \
    to_longer_key

host = ""


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


def get_method_cluster_html(mk):
    global method_clusters
    if mk in method_clusters and len(method_clusters[mk]) > 0:
        html_str = "<h1>accompanied by:</h1>"
        li = method_clusters[mk]
        li.sort(key=lambda e: e[1], reverse=True)
        countdown = 10
        for i in li:
            countdown -= 1
            if countdown < 0:
                break
            html_str += make_link_html(i[0], i[0]) + "&nbsp;&nbsp;" + str(i[1]) + '<br>'
        return html_str
    else:
        return ""


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

all_dependency_id_list = []


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
    global all_dependency_id_list, method_size_map_in, method_size_map_out
    # html_str = '|'.join([' '.join(['&nbsp;'] * 2)] * depth) + make_link_html(lv, lv) + "<br>"
    padding = '|'.join([' '.join(['&nbsp;'] * 2)] * depth)
    id = ':'.join(id_list)
    all_dependency_id_list.append(id)
    display_str = ""
    if len(super_list) > 0:
        display_str = 'style="display:none"'
    method_size = ""
    if lv in method_size_map:
        method_size_in_class = method_size_map_in[lv] if lv in method_size_map_in else 1
        method_size_out_class = method_size_map_out[lv] if lv in method_size_map_out else 1
        method_size_in_global = global_method_size_map_in[lv] if lv in global_method_size_map_in else 1
        method_size_out_global = global_method_size_map_out[lv] if lv in global_method_size_map_out else 1
        method_size = "&nbsp;&nbsp;" + \
                      str(method_size_in_class) \
                      + "&nbsp;:&nbsp;" + str(method_size_out_class) \
                      + "&nbsp;&nbsp;|&nbsp;&nbsp;" + \
                      str(method_size_in_global) \
                      + "&nbsp;:&nbsp;" + str(method_size_out_global) \
                      + "&nbsp;&nbsp;|&nbsp;&nbsp;" + \
                      str(round(method_size_in_class / method_size_in_global, 3)) \
                      + "&nbsp;:&nbsp;" + str(round(method_size_out_class / method_size_out_global, 3))
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
                    method_size_in_class = method_size_map_in[mk_from_other_class] \
                        if mk_from_other_class in method_size_map_in else 1
                    method_size_out_class = method_size_map_out[mk_from_other_class] \
                        if mk_from_other_class in method_size_map_out else 1
                    method_size_in_global = global_method_size_map_in[mk_from_other_class] \
                        if mk_from_other_class in global_method_size_map_in else 1
                    method_size_out_global = global_method_size_map_out[mk_from_other_class] \
                        if mk_from_other_class in global_method_size_map_out else 1
                    method_size = "&nbsp;&nbsp;" + \
                                  str(method_size_in_class) \
                                  + "&nbsp;:&nbsp;" + str(method_size_out_class) \
                                  + "&nbsp;&nbsp;|&nbsp;&nbsp;" + \
                                  str(method_size_in_global) \
                                  + "&nbsp;:&nbsp;" + str(method_size_out_global) \
                                  + "&nbsp;&nbsp;|&nbsp;&nbsp;" + \
                                  str(round(method_size_in_class / method_size_in_global, 3)) \
                                  + "&nbsp;:&nbsp;" + str(round(method_size_out_class / method_size_out_global, 3))
                html_str += '<text ' + 'style="display:none"' + ' onclick="dependency_click(\'' \
                            + other_id + '\')" id=' + other_id + '>' + padding + \
                            make_colored_text_html(mk_from_other_class, dependency_colors[depth]) \
                            + method_size + "<br></text>"
    return html_str


def get_dependency_html(dependency_in_dir, dependency_out_dir, id_str, type_key_len, id_start):
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
    html_str = '<h1>' + id_str + ' dependency in:</h1>'
    id_count = 0
    out_zero_lv_list = sort_dependency_by_method_size(out_zero_lv_list, global_method_size_map_in)
    in_zero_lv_list = sort_dependency_by_method_size(in_zero_lv_list, global_method_size_map_out)
    for lv in out_zero_lv_list:
        id_count += 1
        html_str += recur_for_dependency(lv, dependency_in_dir, 0, [],
                                         type_key_len, [id_start + str(id_count)], method_size_map_in,
                                         global_method_size_map_in, method2methodFromOtherClass_in_dir)
        html_str += '<br>'
    html_str += '<h1>' + id_str + ' dependency out:</h1>'
    for lv in in_zero_lv_list:
        id_count += 1
        html_str += recur_for_dependency(lv, dependency_out_dir, 0, [],
                                         type_key_len, [id_start + str(id_count)], method_size_map_out,
                                         global_method_size_map_out, method2methodFromOtherClass_out_dir)
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
    html_str += make_link_html('# 0: return=parameter ' + str(features[0]), get_feature_key(methodKey, 0)) + "<br>"
    html_str += make_link_html('# 1: return=local ' + str(features[1]), get_feature_key(methodKey, 1)) + "<br>"
    html_str += make_link_html('# 2: return=methodCall ' + str(features[2]), get_feature_key(methodKey, 2)) + "<br>"
    html_str += make_link_html('# 3: return=field ' + str(features[3]), get_feature_key(methodKey, 3)) + "<br><br>"

    html_str += make_link_html('# 4: condition=parameter ' + str(features[4]), get_feature_key(methodKey, 4)) + "<br>"
    html_str += make_link_html('# 5: condition=local ' + str(features[5]), get_feature_key(methodKey, 5)) + "<br>"
    html_str += make_link_html('# 6: condition=methodCall ' + str(features[6]), get_feature_key(methodKey, 6)) + "<br>"
    html_str += make_link_html('# 7: condition=field ' + str(features[7]), get_feature_key(methodKey, 7)) + "<br><br>"

    html_str += make_link_html('# 8: methodCall=parameter ' + str(features[8]), get_feature_key(methodKey, 8)) + "<br>"
    html_str += make_link_html('# 9: methodCall=local ' + str(features[9]), get_feature_key(methodKey, 9)) + "<br>"
    html_str += make_link_html('# 10: methodCall=methodCall ' + str(features[10]), get_feature_key(methodKey, 10)) \
                + "<br>"
    html_str += make_link_html('# 11: methodCall=field ' + str(features[11]), get_feature_key(methodKey, 11)) \
                + "<br><br>"

    html_str += make_link_html('# 12: field=parameter ' + str(features[12]), get_feature_key(methodKey, 12)) + "<br>"
    html_str += make_link_html('# 13: field=local ' + str(features[13]), get_feature_key(methodKey, 13)) + "<br>"
    html_str += make_link_html('# 14: field=methodCall ' + str(features[14]), get_feature_key(methodKey, 14)) + "<br>"
    html_str += make_link_html('# 15: field=field ' + str(features[15]), get_feature_key(methodKey, 15)) + "<br><br>"

    html_str += make_link_html('# 16: reference=parameter ' + str(features[16]),
                               get_feature_key(methodKey, 16)) + "<br>"
    html_str += make_link_html('# 17: reference=local ' + str(features[17]), get_feature_key(methodKey, 17)) + "<br>"
    html_str += make_link_html('# 18: reference=methodCall ' + str(features[18]),
                               get_feature_key(methodKey, 18)) + "<br>"
    html_str += make_link_html('# 19: reference=field ' + str(features[19]),
                               get_feature_key(methodKey, 19)) + "<br><br>"

    html_str += make_link_html('# 20: parameter=parameter ' + str(features[20]), get_feature_key(methodKey, 20)) + \
                "<br>"
    html_str += make_link_html('# 21: parameter=local ' + str(features[21]), get_feature_key(methodKey, 21)) + \
                "<br>"
    html_str += make_link_html('# 22: parameter=methodCall ' + str(features[22]), get_feature_key(methodKey, 22)) + \
                "<br>"
    html_str += make_link_html('# 23: parameter=field ' + str(features[23]), get_feature_key(methodKey, 23)) + \
                "<br><br>"

    html_str += make_link_html('# 24: local=methodCall ' + str(features[24]), get_feature_key(methodKey, 24)) \
                + "<br><br>"
    return html_str


def get_field_feature_html(fieldKey, features):
    html_str = "<h1>field features:</h1>"
    fieldKey += ':'
    html_str += '# genericField is read<br>'
    html_str += make_link_html('# 0: return=genericField ' + str(features[0]), get_feature_key(fieldKey, 0)) + '<br>'
    html_str += make_link_html('# 1: condition=genericField ' + str(features[1]), get_feature_key(fieldKey, 1)) + '<br>'
    html_str += make_link_html('# 2: methodCall=genericField ' + str(features[2]),
                               get_feature_key(fieldKey, 2)) + '<br>'
    html_str += make_link_html('# 3: field=genericField ' + str(features[3]), get_feature_key(fieldKey, 3)) + '<br>'
    html_str += make_link_html('# 4: reference=genericField ' + str(features[4]), get_feature_key(fieldKey, 4)) + '<br>'
    html_str += make_link_html('# 5: local=genericField(methodCall) ' + str(features[5]),
                               get_feature_key(fieldKey, 5)) + '<br><br>'
    html_str += '# genericField is written<br>'
    html_str += make_link_html('# 6: genericField=field ' + str(features[6]), get_feature_key(fieldKey, 6)) + '<br>'
    html_str += make_link_html('# 7: genericField=return ' + str(features[7]), get_feature_key(fieldKey, 7)) + '<br>'
    html_str += make_link_html('# 8: genericField=parameter ' + str(features[8]), get_feature_key(fieldKey, 8)) + '<br>'
    html_str += make_link_html('# 9: genericField=local ' + str(features[9]), get_feature_key(fieldKey, 9)) + '<br><br>'

    html_str += '# genericField is self assigned<br>'
    html_str += make_link_html('# 9: self assignment ' + str(features[10]), get_feature_key(fieldKey, 10)) + '<br><br>'
    html_str = html_str.replace('genericField', '<b>genericField</b>')
    return html_str


def convert_python_list2js_list(var_name, python_list):
    js_str = 'var ' + var_name + ' = ['
    for i in python_list:
        js_str += "'" + str(i) + "',"
    js_str += '];'
    return js_str


def get_js_code_str():
    global all_dependency_id_list
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


if __name__ == "__main__":
    host = get_host_ip()

    read_relation = pickle.load(open(read_relation_compressed_path, "rb"))
    written_relation = pickle.load(open(written_relation_compressed_path, "rb"))

    method2relations = pickle.load(open(method2relations_compressed_path, 'rb'))
    method2global_relations = pickle.load(open(method2global_relations_compressed_path, 'rb'))

    methodKey2methodFeatureRelationList = \
        pickle.load(open(methodKey2methodFeatureRelationList_compressed_path, 'rb'))
    fieldKey2fieldFeatureRelationList = \
        pickle.load(open(fieldKey2fieldFeatureRelationList_compressed_path, 'rb'))

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
    methodKey2methodFeature = pickle.load(open(methodKey2methodFeature_file_path, 'rb'))
    fieldKey2fieldFeature = pickle.load(open(fieldKey2fieldFeature_file_path, 'rb'))
    method2lv_dependency_in_dir = pickle.load(open(method2lv_dependency_in_dir_file_path, 'rb'))
    method2lv_dependency_out_dir = pickle.load(open(method2lv_dependency_out_dir_file_path, 'rb'))

    class2field_dependency_in_dir = pickle.load(open(class2field_dependency_in_dir_file_path, 'rb'))
    class2field_dependency_out_dir = pickle.load(open(class2field_dependency_out_dir_file_path, 'rb'))

    global_method_dependency_in_dir = pickle.load(open(class2method_dependency_in_dir_file_path, 'rb'))
    global_method_dependency_out_dir = pickle.load(open(class2method_dependency_out_dir_file_path, 'rb'))

    method_size_map_in = pickle.load(open(method_size_map_in_path, 'rb'))
    method_size_map_out = pickle.load(open(method_size_map_out_path, 'rb'))

    global_method_size_map_in = pickle.load(open(global_method_size_map_in_path, 'rb'))
    global_method_size_map_out = pickle.load(open(global_method_size_map_out_path, 'rb'))

    class2self_responsibility_in = pickle.load(open(class2self_responsibility_in_path, 'rb'))
    class2self_responsibility_out = pickle.load(open(class2self_responsibility_out_path, 'rb'))

    class2self_dependency_in_sum = pickle.load(open(class2self_dependency_in_sum_path, 'rb'))
    class2self_dependency_out_sum = pickle.load(open(class2self_dependency_out_sum_path, 'rb'))

    class2global_dependency_in_sum = pickle.load(open(class2global_dependency_in_sum_path, 'rb'))
    class2global_dependency_out_sum = pickle.load(open(class2global_dependency_out_sum_path, 'rb'))

    method2methodFromOtherClass_in_dir = pickle.load(open(method2methodFromOtherClass_in_dir_path, 'rb'))
    method2methodFromOtherClass_out_dir = pickle.load(open(method2methodFromOtherClass_out_dir_path, 'rb'))

    # method_clusters = pickle.load(open(method_clusters_path, 'rb'))

    HOST, PORT = '', 8888
    listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listen_socket.bind((HOST, PORT))
    listen_socket.listen(1)
    print('Serving HTTP on host:port  ' + str(host) + ':' + str(PORT) + ' ...')
    while True:
        all_dependency_id_list = []
        client_connection, client_address = listen_socket.accept()
        request = client_connection.recv(1024)
        request_str = request.decode("utf-8")
        request_str = request_str.split('\n')[0]
        request_str = request_str[5:-10]
        http_response = "HTTP/1.1 200 OK\r\n"
        http_response += "\r\n"
        shorter_key = to_shorter_key(request_str)
        if request_str == "classes":
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
        if request_str.endswith(":src"):  # 函数的源码
            http_response += "<h1>" + request_str + "</h1>\n\n"
            methodkey = request_str[:-3]
            if methodkey in methodKey2srcLoc:
                src_loc = methodKey2srcLoc[methodkey]
                http_response += get_lines(
                    src_abs_dir + src_loc["fileName"], src_loc["startLine"] + 1, src_loc["endLine"])
        elif request_str.endswith(":"):  # 函数的内容
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
            # http_response += get_method_cluster_html(request_str)
            if request_str in methodKey2methodFeature:
                http_response += get_method_feature_html(
                    request_str, methodKey2methodFeature[request_str])
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
        elif request_str in LVKey2LVTypeKey:  # 局部变量的历程
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
        elif shorter_key in methodKey2methodFeatureRelationList:
            http_response += "<h1>" + request_str + "</h1>"
            relation_list = methodKey2methodFeatureRelationList[shorter_key]
            relation_list.sort(key=lambda e: e[2])
            for r in relation_list:
                r0long = to_longer_key(r[0])
                r1long = to_longer_key(r[1])
                http_response += 's' + str(r[2]) + '&nbsp;&nbsp;' \
                                 + make_link_html(r0long, r0long) + ' <--- ' \
                                 + make_link_html(r1long, r1long) \
                                 + '&nbsp;&nbsp;' + r[3] + '<br><br>'
        elif shorter_key in fieldKey2fieldFeatureRelationList:
            http_response += "<h1>" + request_str + "</h1>"
            relation_list = fieldKey2fieldFeatureRelationList[shorter_key]
            relation_list.sort(key=lambda e: e[0])
            for r in relation_list:
                r0long = to_longer_key(r[0])
                r1long = to_longer_key(r[1])
                http_response += make_link_html(r0long, r0long) + ' <--- ' \
                                 + make_link_html(r1long, r1long) + '<br><br>'
        else:
            http_response += "<h1>" + request_str + "</h1>"
            if request_str in interfaceType:
                http_response += "<h1>" + "interface types" + "</h1>"
                interface_types = interfaceType[request_str]
                for st in interface_types:
                    http_response += '<a href="http://' + host + ':8888/' + st + '">' + st + "</a>"
                    http_response += "<br><br>"
            if request_str in superTypes:  # 类的父类
                http_response += "<h1>" + "super types" + "</h1>"
                super_types = superTypes[request_str]
                for st in super_types:
                    http_response += '<a href="http://' + host + ':8888/' + st + '">' + st + "</a>"
                    http_response += "<br><br>"
            if request_str in subTypes:  # 类的子类
                http_response += "<h1>" + "sub types" + "</h1>"
                super_types = subTypes[request_str]
                for st in super_types:
                    http_response += '<a href="http://' + host + ':8888/' + st + '">' + st + "</a>"
                    http_response += "<br><br>"
            if request_str in typekey2fieldkey:  # 类的属性
                http_response += "<h1>" + "fields" + "</h1>"
                field_keys = typekey2fieldkey[request_str]
                field_keys = list(set(field_keys))
                for fk in field_keys:
                    http_response += '<a href="http://' + host + ':8888/' + fk + '">' + fk + "</a>"
                    http_response += "<br>"
            if request_str in class2field_dependency_in_dir:
                http_response += get_dependency_html(
                    class2field_dependency_in_dir[request_str],
                    class2field_dependency_out_dir[request_str],
                    'field', len(request_str), 'f_id_')
            if request_str in typekey2methodkey:  # 类的方法
                http_response += "<h1>" + "methods" + "</h1>"
                field_keys = typekey2methodkey[request_str]
                field_keys = list(set(field_keys))
                for fk in field_keys:
                    http_response += '<a href="http://' + host + ':8888/' + fk + '">' + fk + "</a>"
                    http_response += "<br>"
            if request_str in global_method_dependency_in_dir:
                http_response += get_dependency_html(
                    global_method_dependency_in_dir[request_str],
                    global_method_dependency_out_dir[request_str],
                    'method', len(request_str), 'm_id_')
            if request_str in fieldkey2fieldTypekey:  # 属性
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
                        src_abs_dir + src_loc["fileName"], src_loc["startLine"] + 1, src_loc["endLine"])
                http_response += get_field_feature_html(request_str, fieldKey2fieldFeature[request_str])
            http_response += "<br><br>"
            if shorter_key in read_relation or shorter_key in written_relation:
                http_response += "<h1>is read and written by:</h1>"
                global_relation_list = read_relation[shorter_key] if shorter_key in read_relation else []
                global_written_relation_list = written_relation[shorter_key] if shorter_key in written_relation else []
                method2global_read_relation_list = {}
                is_read_relation = True
                for item in global_relation_list:
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
                    http_response += '<br>'
                    k_longer_key = to_longer_key(k)
                    http_response += make_link_html(k_longer_key, k_longer_key)
                    http_response += '<br>'
                    v.sort(key=lambda e: e[1])
                    for vi in v:
                        vi_long_key = to_longer_key(vi[0])
                        if vi[3]:
                            http_response += padding_of_4_space \
                                             + 's' + str(vi[1]) + ' ' \
                                             + make_link_html(vi_long_key, vi_long_key) \
                                             + ' <--- ' + request_str + ' (' + vi[2] + ')'
                        else:
                            http_response += padding_of_4_space \
                                             + 's' + str(vi[1]) + ' ' \
                                             + request_str + ' <--- ' \
                                             + make_link_html(vi_long_key, vi_long_key) + ' (' + vi[2] + ')'
                        http_response += '<br>'
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
