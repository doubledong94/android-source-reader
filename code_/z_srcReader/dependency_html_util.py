from code_.util.dict_util import merge_dict_with_value_merged
from code_.util.key_util import is_return_key, is_method_reference_key, get_method_key_from_return_key, \
    get_key_from_reference
from code_.y_data_compression_and_decompression.b_key_conversion import to_longer_key


def get_size_string(k, size_in, size_out, global_size_in, global_size_out):
    method_size_in_class = size_in[k] if k in size_in else 1
    method_size_out_class = size_out[k] if k in size_out else 1
    method_size_in_global = global_size_in[k] if k in global_size_in else 1
    method_size_out_global = global_size_out[k] if k in global_size_out else 1
    return "&nbsp;&nbsp;" + \
           str(method_size_in_class) \
           + "&nbsp;:&nbsp;" + str(method_size_out_class) \
           + "&nbsp;&nbsp;|&nbsp;&nbsp;" + \
           str(method_size_in_global) \
           + "&nbsp;:&nbsp;" + str(method_size_out_global) \
           + "&nbsp;&nbsp;|&nbsp;&nbsp;" + \
           str(round(method_size_in_class / method_size_in_global, 3)) \
           + "&nbsp;:&nbsp;" + str(round(method_size_out_class / method_size_out_global, 3))


def sort_dependency_by_method_size(key_list, size_dict, reverse=True):
    key_list_with_size = []
    for key in key_list:
        key_list_with_size.append([
            key,
            size_dict[key] if key in size_dict else 1
        ])
    key_list_with_size.sort(key=lambda e: e[1], reverse=reverse)
    sorted_key_list = {}
    for i in key_list_with_size:
        sorted_key_list[i[0]] = ''
    return sorted_key_list


all_id_list_for_js_variable = []


def make_colored_text_html(text, color):
    return '<text style="background-color:' + color + '">' + text + '</text>'


dependency_colors = ['#f5b7b1', '#d2b4de', '#a9cce3', '#abebc6', '#f9e79f', '#f5cba7', '#d5dbdb'] * 10

recur_back_color = '#ff5555'


def recur_for_dependency(
        key, id_list, super_list, dependency_dict, dependency_from_other_class_dict,
        dependency_dict_p, dependency_from_other_class_dict_p, parallel_key,
        size_in, size_out, global_size_in, global_size_out, omit_len=0, search_key=''):
    searched_flag = search_key == '' or search_key == key
    depth = len(super_list)
    is_recurred = key in super_list
    back_color = recur_back_color if is_recurred else dependency_colors[depth]
    padding = '|'.join([' '.join(['&nbsp;'] * 2)] * depth)
    id = ':'.join(id_list)
    all_id_list_for_js_variable.append(id)
    display_style_str = ""
    if len(super_list) > 0:
        display_style_str = 'style="display:none"'
    method_size = ""
    if key in global_size_in or key in global_size_out:
        method_size = get_size_string(key, size_in, size_out, global_size_in, global_size_out)
    else:
        return '', searched_flag
    html_str = '<text ' + display_style_str + ' onclick="dependency_click(\'' + id + '\')" id=' + id + '>' \
               + padding + make_colored_text_html(key[omit_len:], back_color) + parallel_key + method_size \
               + "<br></text>"
    id_count = 0
    if not is_recurred:
        if key in dependency_dict:
            dependency_in_dir_list = dependency_dict[key]
            dependency_in_dir_list = sort_dependency_by_method_size(dependency_in_dir_list,
                                                                    dependency_dict_p[key], False)
            for child_node in dependency_in_dir_list:
                id_count += 1
                id_list_copy = id_list.copy()
                super_list_copy = super_list.copy()
                id_list_copy.append(str(id_count))
                parallel_key = "&nbsp;&nbsp;"+dependency_dict_p[key][child_node]
                super_list_copy.append(key)
                recur_html, child_searched_flag = recur_for_dependency(
                    child_node, id_list_copy, super_list_copy, dependency_dict, dependency_from_other_class_dict,
                    dependency_dict_p, dependency_from_other_class_dict_p, parallel_key,
                    size_in, size_out, global_size_in, global_size_out, omit_len, search_key)
                searched_flag = searched_flag or child_searched_flag
                html_str += recur_html
    #    if depth < 5 and key in dependency_from_other_class_dict and len(dependency_from_other_class_dict[key]) > 0:
    if key not in super_list and key in dependency_from_other_class_dict \
            and len(dependency_from_other_class_dict[key]) > 0:
        from_other_class = ":from_other_class"
        depth += 1
        padding = '|'.join([' '.join(['&nbsp;'] * 2)] * depth)
        id += from_other_class
        all_id_list_for_js_variable.append(id)
        html_str += '<text ' + 'style="display:none"' + ' onclick="dependency_click(\'' + id + '\')" id=' + id + '>' \
                    + padding + make_colored_text_html(from_other_class, dependency_colors[depth]) \
                    + "<br></text>"
        depth += 1
        padding = '|'.join([' '.join(['&nbsp;'] * 2)] * depth)
        other_method_count = 0
        other_class_dict_keys = dependency_from_other_class_dict[key]
        other_class_dict_keys = sort_dependency_by_method_size(other_class_dict_keys,
                                                               dependency_from_other_class_dict_p[key], False)
        for key_from_other_class in other_class_dict_keys:
            other_method_count += 1
            other_id = id + ":" + str(other_method_count)
            all_id_list_for_js_variable.append(other_id)
            searched_flag = searched_flag or search_key == key_from_other_class
            parallel_key = "&nbsp;&nbsp;" + dependency_from_other_class_dict_p[key][key_from_other_class]
            if key_from_other_class in size_in or key_from_other_class in size_out:
                method_size = get_size_string(
                    key_from_other_class, size_in, size_out, global_size_in, global_size_out)
            html_str += '<text ' + 'style="display:none"' + ' onclick="dependency_click(\'' \
                        + other_id + '\')" id=' + other_id + '>' + padding + \
                        make_colored_text_html(key_from_other_class, dependency_colors[depth]) + parallel_key \
                        + method_size + "<br></text>"
    return html_str, searched_flag


def handle_method_dependency_in(
        global_relation_list, mk_calling, all_self_method_key,
        dependency_in_from_self, dependency_in_from_other_class,
        dependency_in_from_self_p, dependency_in_from_other_class_p,
        dependency_out_from_self, dependency_out_from_other_class,
        dependency_out_from_self_p, dependency_out_from_other_class_p):
    if mk_calling in all_self_method_key:
        if mk_calling not in dependency_in_from_self:
            dependency_in_from_self[mk_calling] = {}
            dependency_in_from_self_p[mk_calling] = {}
        if mk_calling not in dependency_in_from_other_class:
            dependency_in_from_other_class[mk_calling] = {}
            dependency_in_from_other_class_p[mk_calling] = {}
        for relation in global_relation_list:
            # written_key = to_longer_key(relation[0])
            read_key = to_longer_key(relation[1])
            linear_order = relation[2]
            parallel_key = relation[3]
            parallel_key = '{:0>4d}'.format(linear_order) + ' (' + parallel_key+') '
            is_read_key_return = is_return_key(read_key)
            # is_written_key_reference = is_method_reference_key(written_key)
            # if is_read_key_return or is_written_key_reference:
            if is_read_key_return:
                # if is_read_key_return:
                mk_called = get_method_key_from_return_key(read_key)
                # else:
                #     mk_called = get_key_from_reference(written_key)
                if mk_called in all_self_method_key:  # self call self
                    dependency_in_from_self[mk_calling][mk_called] = ''
                    dependency_in_from_self_p[mk_calling][mk_called] = parallel_key
                    if mk_called not in dependency_out_from_self:
                        dependency_out_from_self[mk_called] = {}
                        dependency_out_from_self_p[mk_called] = {}
                    dependency_out_from_self[mk_called][mk_calling] = ''
                    dependency_out_from_self_p[mk_called][mk_calling] = parallel_key
                else:  # self call other
                    dependency_in_from_other_class[mk_calling][mk_called] = ''
                    dependency_in_from_other_class_p[mk_calling][mk_called] = parallel_key
    else:
        for relation in global_relation_list:
            # written_key = to_longer_key(relation[0])
            read_key = to_longer_key(relation[1])
            parallel_key = relation[3]
            is_read_key_return = is_return_key(read_key)
            # is_written_key_reference = is_method_reference_key(written_key)
            # if is_read_key_return or is_written_key_reference:
            if is_read_key_return:
                # if is_read_key_return:
                mk_called = get_method_key_from_return_key(read_key)
                # else:
                #     mk_called = get_key_from_reference(written_key)
                if mk_called in all_self_method_key:  # other call self
                    if mk_called not in dependency_out_from_other_class:
                        dependency_out_from_other_class[mk_called] = {}
                        dependency_out_from_other_class_p[mk_called] = {}
                    dependency_out_from_other_class[mk_called][mk_calling] = ''
                    dependency_out_from_other_class_p[mk_called][mk_calling] = parallel_key
                pass
                # else: # other call other, we don't need that
                #     pass


def get_zero_degree(all_key, dependency_dict):
    zero_degree = []
    for key in all_key:
        if key not in dependency_dict.keys() or len(dependency_dict[key]) == 0:
            zero_degree.append(key)
        elif key in dependency_dict[key] and len(dependency_dict[key]) == 1:
            zero_degree.append(key)
        else:
            flag_dependency_on_all_key = False
            for d_key in dependency_dict[key]:
                if d_key in all_key:
                    flag_dependency_on_all_key = True
            if not flag_dependency_on_all_key:
                zero_degree.append(key)
    return zero_degree


def get_dependency_in_and_out_html(
        method2global_relation, type_key_scope_list, typ_key2method_key_list,
        size_in, size_out, global_size_in, global_size_out,
        id_shown_str, id_index_head, omit_len=0, search_method_key=''):
    all_key = {}
    for type_key in type_key_scope_list:
        for method_key in typ_key2method_key_list[type_key]:
            all_key[method_key] = ''
    all_key_count = len(all_key)
    if all_key_count > 2000:
        return str(all_key_count) + 'methods, too many to show'
    print(all_key_count)
    dependency_in = {}
    dependency_out = {}
    dependency_in_p = {}
    dependency_out_p = {}
    dependency_in_from_other_class = {}
    dependency_out_from_other_class = {}
    dependency_in_from_other_class_p = {}
    dependency_out_from_other_class_p = {}
    for mk, global_relation_of_a_method in method2global_relation.items():
        mk = to_longer_key(mk)
        handle_method_dependency_in(
            global_relation_of_a_method, mk, all_key,
            dependency_in, dependency_in_from_other_class,
            dependency_in_p, dependency_in_from_other_class_p,
            dependency_out, dependency_out_from_other_class,
            dependency_out_p, dependency_out_from_other_class_p)
    print('done searching, now joining html')
    out_zero_key_list = get_zero_degree(all_key, dependency_out)
    in_zero_key_list = get_zero_degree(all_key, dependency_in)
    intersect = list(set.intersection(set(out_zero_key_list), set(in_zero_key_list)))
    out_zero_key_list = sort_dependency_by_method_size(out_zero_key_list, global_size_in)
    in_zero_key_list = sort_dependency_by_method_size(in_zero_key_list, global_size_out)
    # print(out_zero_key_list)
    # print(in_zero_key_list)
    id_count = 0
    html_str = '<h1>' + id_shown_str + ' dependency in:</h1>'
    for key in out_zero_key_list:
        if key in intersect:
            continue
        id_count += 1
        dependency_str, searched_flag = recur_for_dependency(
            key, [id_index_head + str(id_count)], [], dependency_in, dependency_in_from_other_class,
            dependency_in_p, dependency_in_from_other_class_p, '', size_in, size_out, global_size_in,
            global_size_out, omit_len, search_method_key)
        if not dependency_str == "" and searched_flag:
            html_str += dependency_str
            html_str += '<br>'
    html_str += '<h1>' + id_shown_str + ' dependency out:</h1>'
    for key in in_zero_key_list:
        if key in intersect:
            continue
        id_count += 1
        dependency_str, searched_flag = recur_for_dependency(
            key, [id_index_head + str(id_count)], [], dependency_out, dependency_out_from_other_class,
            dependency_out_p, dependency_out_from_other_class_p, '', size_in, size_out, global_size_in,
            global_size_out, omit_len, search_method_key)
        if not dependency_str == "" and searched_flag:
            html_str += dependency_str
            html_str += '<br>'
    html_str += '<h1>' + id_shown_str + ' not involved in:</h1>'
    all_key = sort_dependency_by_method_size(all_key, global_size_in)
    for k in all_key:
        if k in intersect or (k not in dependency_in and k not in dependency_out):
            id_count += 1
            dependency_str, searched_flag = recur_for_dependency(
                k, [id_index_head + str(id_count)], [], dependency_in, dependency_in_from_other_class,
                dependency_in_p, dependency_in_from_other_class_p, '', size_in, size_out, global_size_in,
                global_size_out, omit_len, search_method_key)
            if not dependency_str == "" and searched_flag:
                html_str += dependency_str
                html_str += '<br>'
    html_str += '<h1>' + id_shown_str + ' not involved out:</h1>'
    all_key = sort_dependency_by_method_size(all_key, global_size_out)
    for k in all_key:
        if k in intersect or (k not in dependency_in and k not in dependency_out):
            id_count += 1
            dependency_str, searched_flag = recur_for_dependency(
                k, [id_index_head + str(id_count)], [], dependency_out, dependency_out_from_other_class,
                dependency_out_p, dependency_out_from_other_class_p, '', size_in, size_out, global_size_in,
                global_size_out, omit_len, search_method_key)
            if not dependency_str == "" and searched_flag:
                html_str += dependency_str
                html_str += '<br>'
    return html_str
