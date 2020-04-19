from code_.util.dict_util import merge_dict_with_value_merged
from code_.z_srcReader.method_usage_html_util import get_zero_degree, all_id_list_for_js_variable, \
    dependency_colors, make_colored_text_html

done_key = {}


def recur_for_dependency(
        key, id_list, super_list, dependency_dict, dependency_from_other_class_dict, search_key=''):
    searched_flag = search_key == '' or search_key == key
    depth = len(super_list)
    padding = '|'.join([' '.join(['&nbsp;'] * 2)] * depth)
    id = ':'.join(id_list)
    all_id_list_for_js_variable.append(id)
    display_style_str = ""
    if len(super_list) > 0:
        display_style_str = 'style="display:none"'
    html_str_list = ['<text ' + display_style_str + ' onclick="dependency_click(\'' + id + '\')" id=' + id + '>' \
                     + padding + make_colored_text_html(key, dependency_colors[depth]) + "<br></text>"]
    if key in done_key:
        return html_str_list, searched_flag
    done_key[key] = ''
    id_count = 0
    if key not in super_list:
        if key in dependency_dict:
            dependency_in_dir_list = dependency_dict[key]
            for child_node in dependency_in_dir_list:
                id_count += 1
                id_list_copy = id_list.copy()
                super_list_copy = super_list.copy()
                id_list_copy.append(str(id_count))
                super_list_copy.append(key)
                recur_html, child_searched_flag = recur_for_dependency(
                    child_node, id_list_copy, super_list_copy, dependency_dict,
                    dependency_from_other_class_dict, search_key)
                searched_flag = searched_flag or child_searched_flag
                html_str_list.extend(recur_html)
    if key not in super_list and key in dependency_from_other_class_dict and len(
            dependency_from_other_class_dict[key]) > 0:
        from_other_class = ":from_other_class"
        depth += 1
        padding = '|'.join([' '.join(['&nbsp;'] * 2)] * depth)
        id += from_other_class
        all_id_list_for_js_variable.append(id)
        html_str_list.append(
            '<text ' + 'style="display:none"' + ' onclick="dependency_click(\'' + id + '\')" id=' + id + '>' \
            + padding + make_colored_text_html(from_other_class, dependency_colors[depth]) \
            + "<br></text>")
        depth += 1
        padding = '|'.join([' '.join(['&nbsp;'] * 2)] * depth)
        other_method_count = 0
        for key_from_other_class in dependency_from_other_class_dict[key]:
            other_method_count += 1
            other_id = id + ":" + str(other_method_count)
            all_id_list_for_js_variable.append(other_id)
            searched_flag = searched_flag or search_key == key_from_other_class
            html_str_list.append('<text ' + 'style="display:none"' + ' onclick="dependency_click(\'' \
                                 + other_id + '\')" id=' + other_id + '>' + padding + \
                                 make_colored_text_html(key_from_other_class, dependency_colors[depth]) \
                                 + "<br></text>")
    return html_str_list, searched_flag


def get_parameter_consumption_html_in_and_out(
        field_consumption_dependency_in_dir, field_consumption_dependency_out_dir,
        type_key_scope_list, all_field_key, id_shown_str, id_index_head, search_field_key=''):
    all_key = []
    for fk in all_field_key:
        for type_key in type_key_scope_list:
            if fk.startswith(type_key + '.'):
                if fk not in all_key:
                    all_key.append(fk)
    all_key_count = len(all_key)
    if all_key_count > 200000:
        return str(all_key_count) + 'methods, too many to show'
    print(all_key_count)
    dependency_in = {}
    dependency_out = {}
    dependency_in_from_other_class = {}
    dependency_out_from_other_class = {}
    for k in all_key:
        if k in field_consumption_dependency_in_dir:
            for vi in field_consumption_dependency_in_dir[k]:
                if vi in all_key:
                    merge_dict_with_value_merged(dependency_in, {k: [vi]})
                else:
                    merge_dict_with_value_merged(dependency_in_from_other_class, {k: [vi]})
    for k in all_key:
        if k in field_consumption_dependency_out_dir:
            for vi in field_consumption_dependency_out_dir[k]:
                if vi in all_key:
                    merge_dict_with_value_merged(dependency_out, {k: [vi]})
                else:
                    merge_dict_with_value_merged(dependency_out_from_other_class, {k: [vi]})
    in_zero_key_list = get_zero_degree(all_key, dependency_in)
    out_zero_key_list = get_zero_degree(all_key, dependency_out)
    intersect = list(set.intersection(set(out_zero_key_list), set(in_zero_key_list)))
    id_count = 0
    html_str_list = ['<h1>' + id_shown_str + ' come from:</h1>']
    for k in out_zero_key_list:
        if k in intersect:
            continue
        id_count += 1
        done_key.clear()
        dependency_str, searched_flag = recur_for_dependency(
            k, [id_index_head + str(id_count)], [], dependency_in,
            dependency_in_from_other_class, search_field_key)
        if len(dependency_str) > 0 and searched_flag:
            html_str_list.extend(dependency_str)
            html_str_list.append('<br>')
    html_str_list.append('<h1>' + id_shown_str + ' come to:</h1>')
    for key in in_zero_key_list:
        if key in intersect:
            continue
        id_count += 1
        done_key.clear()
        dependency_str, searched_flag = recur_for_dependency(
            key, [id_index_head + str(id_count)], [], dependency_out,
            dependency_out_from_other_class, search_field_key)
        if len(dependency_str) > 0 and searched_flag:
            html_str_list.extend(dependency_str)
            html_str_list.append('<br>')
    html_str_list.append('<h1>' + id_shown_str + ' not involved in:</h1>')
    for k in all_key:
        if k in intersect or (k not in dependency_in and k not in dependency_out):
            id_count += 1
            done_key.clear()
            dependency_str, searched_flag = recur_for_dependency(
                k, [id_index_head + str(id_count)], [], dependency_in,
                dependency_out_from_other_class, search_field_key)
            if len(dependency_str) > 0 and searched_flag:
                html_str_list.extend(dependency_str)
                html_str_list.append('<br>')
    html_str_list.append('<h1>' + id_shown_str + ' not involved out:</h1>')
    for k in all_key:
        if k in intersect or (k not in dependency_in and k not in dependency_out):
            id_count += 1
            done_key.clear()
            dependency_str, searched_flag = recur_for_dependency(
                k, [id_index_head + str(id_count)], [], dependency_out,
                dependency_out_from_other_class, search_field_key)
            if len(dependency_str) > 0 and searched_flag:
                html_str_list.extend(dependency_str)
                html_str_list.append('<br>')
    return ''.join(html_str_list)
