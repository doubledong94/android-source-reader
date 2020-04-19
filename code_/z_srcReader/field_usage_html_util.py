from code_.util.key_conversion_util import to_longer_key_if_compressed, convert_dependency_to_longer_key, \
    to_shorter_key_if_compressed
from code_.z_srcReader.inside_method_html_util import get_dependency_html_inside_method
from code_.z_srcReader.method_usage_html_util import handle_method_dependency_in, get_zero_degree, \
    sort_dependency_by_method_size, dependency_colors, all_id_list_for_js_variable, \
    make_colored_text_html

done_key = {}


def field_found(mk, fk_list, global_read_relation, global_written_relation):
    mk_short = to_shorter_key_if_compressed(mk)
    for fk in fk_list:
        fk_short = to_shorter_key_if_compressed(fk)
        if fk_short in global_read_relation:
            for i in global_read_relation[fk_short]:
                if i[1] == mk_short:
                    return True
        if fk_short in global_written_relation:
            for i in global_written_relation[fk_short]:
                if i[1] == mk_short:
                    return True
    return False


def recur_for_field_usage(
        current_key, id_list, super_list, method_dependency_dict, method_dependency_pk, search_field_keys,
        global_read_relation, global_written_relation, mk2dependency_in_inside, mk2dependency_out_inside, parallel_key):
    if current_key in super_list:
        return []
    if current_key in done_key:
        return []
    done_key[current_key] = ''
    sub_node_str_list = []
    if current_key in method_dependency_dict:
        id_count = 0
        dependency_in_dir_list = method_dependency_dict[current_key]
        dependency_in_dir_list = sort_dependency_by_method_size(
            dependency_in_dir_list, method_dependency_pk[current_key], False)
        for sub_node in dependency_in_dir_list:
            id_count += 1
            id_list_copy = id_list.copy()
            id_list_copy.append(str(id_count))
            super_list_copy = super_list.copy()
            super_list_copy.append(current_key)
            sub_parallel_key = "&nbsp;&nbsp;" + method_dependency_pk[current_key][sub_node]
            sub_node_str_list.extend(recur_for_field_usage(
                sub_node, id_list_copy, super_list_copy, method_dependency_dict, method_dependency_pk,
                search_field_keys,
                global_read_relation, global_written_relation, mk2dependency_in_inside, mk2dependency_out_inside,
                sub_parallel_key))
    return_list = []
    field_found_in_this_key = field_found(current_key, search_field_keys, global_read_relation, global_written_relation)
    depth = len(super_list)
    padding = '|'.join([' '.join(['&nbsp;'] * 2)] * depth)
    id = ':'.join(id_list)
    back_color = dependency_colors[depth]
    display_style_str = ""
    if depth > 0:
        display_style_str = 'style="display:none"'
    self_str = '<text ' + display_style_str + ' onclick="dependency_click(\'' + id + '\')" id=' + id + '>' \
               + padding + make_colored_text_html(current_key, back_color) + parallel_key + "<br></text>"
    if len(sub_node_str_list) > 0:
        all_id_list_for_js_variable.append(id)
        return_list.append(self_str)
    elif field_found_in_this_key:
        all_id_list_for_js_variable.append(id)
        return_list.append(self_str)
    if field_found_in_this_key:
        current_key_short = to_shorter_key_if_compressed(current_key)
        super_list_copy = super_list.copy()
        super_list_copy.append(current_key)
        return_list.extend(get_dependency_html_inside_method(
            id_list, super_list_copy,
            convert_dependency_to_longer_key(mk2dependency_in_inside[current_key_short]),
            convert_dependency_to_longer_key(mk2dependency_out_inside[current_key_short]),
            search_field_keys, len(sub_node_str_list)))
    return_list.extend(sub_node_str_list)
    return return_list


def get_field_usage_html(type_key_scope_list, typ_key2method_key_list,
                         method2global_relation, global_size_in, id_shown_str, id_index_head,
                         search_field_keys,
                         global_read_relation, global_written_relation, mk2dependency_in_inside,
                         mk2dependency_out_inside):
    all_id_list_for_js_variable.clear()
    all_key = {}
    for type_key in type_key_scope_list:
        for method_key in typ_key2method_key_list[type_key]:
            all_key[method_key] = ''
    all_key_count = len(all_key)
    if all_key_count > 10000:
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
        mk = to_longer_key_if_compressed(mk)
        handle_method_dependency_in(
            global_relation_of_a_method, mk, all_key,
            dependency_in, dependency_in_from_other_class,
            dependency_in_p, dependency_in_from_other_class_p,
            dependency_out, dependency_out_from_other_class,
            dependency_out_p, dependency_out_from_other_class_p)
    out_zero_key_list = get_zero_degree(all_key, dependency_out)
    in_zero_key_list = get_zero_degree(all_key, dependency_in)
    intersect = list(set.intersection(set(out_zero_key_list), set(in_zero_key_list)))
    out_zero_key_list = sort_dependency_by_method_size(out_zero_key_list, global_size_in)
    # print(out_zero_key_list)
    # print(in_zero_key_list)
    id_count = 0
    html_str_list = ['<h1>' + id_shown_str + ' dependency in:</h1>']

    for key in out_zero_key_list:
        if key in intersect:
            continue
        done_key.clear()
        id_count += 1
        field_usage_list = recur_for_field_usage(
            key, [id_index_head + str(id_count)], [], dependency_in,
            dependency_in_p,
            search_field_keys, global_read_relation, global_written_relation,
            mk2dependency_in_inside, mk2dependency_out_inside, '')
        if len(field_usage_list) > 0:
            print(key)
            html_str_list.extend(field_usage_list)
            html_str_list.append('<br>')
    return ''.join(html_str_list)
