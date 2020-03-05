#!/usr/bin/python
# -*- coding: UTF-8 -*-
import pickle
import socket

from code_.util.file_util import writen_file_path, read_file_path, \
    method2relations_file_path, method2global_relations_file_path, \
    LV2relations_file_path, LVKey2LVTypeKey_path, \
    fieldkey2fieldTypekey_path, typekey2fieldkey_path, \
    typekey2methodkey_path, superTypes_path, subTypes_path, fieldKey2typeKey_path, methodKey2typeKey_path, \
    type2instance_for_field_file_path, type2instance_for_local_file_path, methodKey2srcLoc_path, get_lines, src_abs_dir, \
    fieldKey2srcLoc_path, interfaceType_path, methodKey2methodFeature_file_path, fieldKey2fieldFeature_file_path, \
    methodKey2methodFeatureRelationList_file_path, fieldKey2fieldFeatureRelationList_file_path, \
    method2lv_dependency_in_dir_file_path, method2lv_dependency_out_dir_file_path, \
    class2field_dependency_in_dir_file_path, class2field_dependency_out_dir_file_path, \
    class2method_dependency_in_dir_file_path, class2method_dependency_out_dir_file_path
from code_.util.key_util import get_feature_key, is_parameter_key, is_return_key, get_method_key_from_parameter_key

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


def get_all_local_variable_html(relation_list):
    html_str = "<h1>all local variables:</h1>"
    local_variables = []
    for r in relation_list:
        if r[0] in LVKey2LVTypeKey:
            local_variables.append(r[0])
        if r[1] in LVKey2LVTypeKey:
            local_variables.append(r[1])
        local_variables = list(set(local_variables))
        local_variables.sort()
    for lv in local_variables:
        html_str += '<a href="http://' + host + ':8888/' + lv + '">' + lv + "</a>"
        html_str += "<br><br>"
    return html_str

dependency_colors=['#f5b7b1','#d2b4de','#a9cce3','#abebc6','#f9e79f','#f5cba7','#d5dbdb']*10

def recur_for_dependency(lv, lv_dependency_in_dir, depth, super_list):
    # html_str = '|'.join([' '.join(['&nbsp;'] * 2)] * depth) + make_link_html(lv, lv) + "<br>"
    html_str = '|'.join([' '.join(['&nbsp;'] * 2)] * depth) + make_colored_text_html(lv, dependency_colors[depth]) + "<br>"
    if lv not in super_list:
        super_list.append(lv)
        if lv in lv_dependency_in_dir:
            for child_node in lv_dependency_in_dir[lv]:
                super_list_copy = super_list.copy()
                html_str += recur_for_dependency(child_node, lv_dependency_in_dir, depth + 1, super_list_copy)
    return html_str


def get_dependency_html(lv_dependency_in_dir, lv_dependency_out_dir, id_str):
    all_lv_key = []
    for k, v in lv_dependency_out_dir.items():
        all_lv_key.append(k)
        for vi in v:
            all_lv_key.append(vi)
    all_lv_key = list(set(all_lv_key))
    out_zero_lv_list = []
    in_zero_lv_list = []
    for lv_key in all_lv_key:
        if lv_key not in lv_dependency_out_dir.keys() or len(lv_dependency_out_dir[lv_key]) == 0:
            out_zero_lv_list.append(lv_key)
        elif lv_key in lv_dependency_out_dir[lv_key] and len(lv_dependency_out_dir[lv_key]) == 1:
            out_zero_lv_list.append(lv_key)
    for lv_key in all_lv_key:
        if lv_key not in lv_dependency_in_dir.keys() or len(lv_dependency_in_dir[lv_key]) == 0:
            in_zero_lv_list.append(lv_key)
        elif lv_key in lv_dependency_in_dir[lv_key] and len(lv_dependency_in_dir[lv_key]) == 1:
            in_zero_lv_list.append(lv_key)
    html_str = '<h1>' + id_str + ' dependency in:</h1>'
    for lv in out_zero_lv_list:
        html_str += recur_for_dependency(lv, lv_dependency_in_dir, 0, [])
        html_str += '<br>'
    html_str += '<h1>' + id_str + ' dependency out:</h1>'
    for lv in in_zero_lv_list:
        html_str += recur_for_dependency(lv, lv_dependency_out_dir, 0, [])
        html_str += '<br>'
    return html_str


def get_relation_with_local_html(relation_list):
    html_str = "<h1>relations with local:</h1>"
    for r in relation_list:
        html_str += "s" + str(r[3]) + ": "
        html_str += '<a href="http://' + host + ':8888/' + r[0] + '">' + r[0] + "</a>" + " <--- " + \
                    '<a href="http://' + host + ':8888/' + r[1] + '">' + r[1] + "</a>"
        html_str += ' (' + r[2] + ')'
        html_str += "<br><br>"
    return html_str


def get_relation_without_local_html(relation_list):
    html_str = "<h1>relations without local:</h1>"
    for r in relation_list:
        html_str += 's' + str(r[2]) + ": " + \
                    '<a href="http://' + host + ':8888/' + r[0] + '">' + r[0] + "</a>" + " <--- " + \
                    '<a href="http://' + host + ':8888/' + r[1] + '">' + r[1] + "</a>"
        html_str += "<br><br>"
    return html_str


def make_link_html(text, link):
    return '<a href="http://' + host + ':8888/' + link + '">' + text + "</a>"


def make_colored_text_html(text, color):
    return '<text style="background-color:' + color + '">' + text + '</text>'


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

    html_str += make_link_html('# 16: guest=parameter ' + str(features[16]), get_feature_key(methodKey, 16)) + "<br>"
    html_str += make_link_html('# 17: guest=local ' + str(features[17]), get_feature_key(methodKey, 17)) + "<br>"
    html_str += make_link_html('# 18: guest=methodCall ' + str(features[18]), get_feature_key(methodKey, 18)) + "<br>"
    html_str += make_link_html('# 19: guest=field ' + str(features[19]), get_feature_key(methodKey, 19)) + "<br><br>"

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
    html_str += make_link_html('# 4: guest=genericField ' + str(features[4]), get_feature_key(fieldKey, 4)) + '<br>'
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


if __name__ == "__main__":
    host = get_host_ip()
    read_relation = pickle.load(open(read_file_path, "rb"))
    writen_relation = pickle.load(open(writen_file_path, "rb"))
    method2relations = pickle.load(open(method2relations_file_path, 'rb'))
    method2global_relations = pickle.load(open(method2global_relations_file_path, 'rb'))
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
    methodKey2methodFeatureRelationList = \
        pickle.load(open(methodKey2methodFeatureRelationList_file_path, 'rb'))
    fieldKey2fieldFeatureRelationList = \
        pickle.load(open(fieldKey2fieldFeatureRelationList_file_path, 'rb'))
    method2lv_dependency_in_dir = pickle.load(open(method2lv_dependency_in_dir_file_path, 'rb'))
    method2lv_dependency_out_dir = pickle.load(open(method2lv_dependency_out_dir_file_path, 'rb'))

    class2field_dependency_in_dir = pickle.load(open(class2field_dependency_in_dir_file_path, 'rb'))
    class2field_dependency_out_dir = pickle.load(open(class2field_dependency_out_dir_file_path, 'rb'))

    class2method_dependency_in_dir = pickle.load(open(class2method_dependency_in_dir_file_path, 'rb'))
    class2method_dependency_out_dir = pickle.load(open(class2method_dependency_out_dir_file_path, 'rb'))

    HOST, PORT = '', 8888
    listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listen_socket.bind((HOST, PORT))
    listen_socket.listen(1)
    print('Serving HTTP on host:port  ' + str(host) + ':' + str(PORT) + ' ...')
    while True:
        client_connection, client_address = listen_socket.accept()
        request = client_connection.recv(1024)
        request_str = request.decode("utf-8")
        request_str = request_str.split('\n')[0]
        request_str = request_str[5:-10]
        http_response = "HTTP/1.1 200 OK\r\n"
        http_response += "\r\n"
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
            if request_str in methodKey2methodFeature:
                http_response += get_method_feature_html(request_str,
                                                         methodKey2methodFeature[request_str])
            if request_str in method2relations:
                relation_list = method2relations[request_str]
                http_response += get_all_local_variable_html(relation_list)
                http_response += get_dependency_html(
                    method2lv_dependency_in_dir[request_str],
                    method2lv_dependency_out_dir[request_str],
                    'local variable')
                http_response += get_relation_with_local_html(relation_list)
            if request_str in method2relations:
                relation_list = method2global_relations[request_str]
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
        elif request_str in methodKey2methodFeatureRelationList:
            http_response += "<h1>" + request_str + "</h1>"
            relation_list = methodKey2methodFeatureRelationList[request_str]
            relation_list.sort(key=lambda e: e[0])
            for r in relation_list:
                http_response += r[0] + ' <--- ' + r[1] + '<br><br>'
        elif request_str in fieldKey2fieldFeatureRelationList:
            http_response += "<h1>" + request_str + "</h1>"
            relation_list = fieldKey2fieldFeatureRelationList[request_str]
            relation_list.sort(key=lambda e: e[0])
            for r in relation_list:
                http_response += r[0] + ' <--- ' + r[1] + '<br><br>'
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
                for fk in field_keys:
                    http_response += '<a href="http://' + host + ':8888/' + fk + '">' + fk + "</a>"
                    http_response += "<br>"
            if request_str in class2field_dependency_in_dir:
                http_response += get_dependency_html(
                    class2field_dependency_in_dir[request_str],
                    class2field_dependency_out_dir[request_str],
                    'field')
            if request_str in typekey2methodkey:  # 类的方法
                http_response += "<h1>" + "methods" + "</h1>"
                field_keys = typekey2methodkey[request_str]
                for fk in field_keys:
                    http_response += '<a href="http://' + host + ':8888/' + fk + '">' + fk + "</a>"
                    http_response += "<br>"
            if request_str in class2method_dependency_in_dir:
                http_response += get_dependency_html(
                    class2method_dependency_in_dir[request_str],
                    class2method_dependency_out_dir[request_str],
                    'method')
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
            if request_str in read_relation:
                http_response += "<h1>be read by:</h1>"
                reads = [
                    '<b><a href="http://' + host + ':8888/' + a[0] + '">' + a[0] + "</a></b>" + " ||| " +
                    '<br>' +
                    '<a href="http://' + host + ':8888/' + a[1] + '">' + a[1] + "</a>"
                    for a in read_relation[request_str]]
                reads.sort()
                http_response += "<br><br>".join(reads) + "<br><br>"
            if request_str in writen_relation:
                http_response += "<h1>be writen by:</h1>"
                writes = [
                    '<b><a href="http://' + host + ':8888/' + a[0] + '">' + a[0] + "</a></b>" + " ||| " +
                    '<br>' +
                    '<a href="http://' + host + ':8888/' + a[1] + '">' + a[1] + "</a>"
                    for a in writen_relation[request_str]]
                writes.sort()
                http_response += "<br><br>".join(writes) + "<br><br>"
            if request_str in type2instance_for_field:  # 类的实例 属性
                http_response += "<h1>" + "instance for field" + "</h1>"
                field_keys = type2instance_for_field[request_str]
                for fk in field_keys:
                    http_response += '<a href="http://' + host + ':8888/' + fk + '">' + fk + "</a>"
                    http_response += "<br>"
            if request_str in type2instance_for_local:  # 类的实例 局部变量
                http_response += "<h1>" + "instance for local" + "</h1>"
                field_keys = type2instance_for_local[request_str]
                for fk in field_keys:
                    http_response += '<a href="http://' + host + ':8888/' + fk + '">' + fk + "</a>"
                    http_response += "<br>"
        print(request_str)
        client_connection.sendall(http_response.encode("utf-8"))
        client_connection.close()
