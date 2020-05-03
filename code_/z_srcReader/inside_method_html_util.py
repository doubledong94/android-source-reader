from code_.util.key_conversion_util import convert_dependency_to_longer_key
from code_.util.key_util import get_key_from_dependency_inside_method_key, is_lv_key, is_field_key, \
    is_field_reference_key, get_field_key_from_index_key, is_index_key, get_field_key_from_reference
from code_.z_srcReader.method_usage_html_util import recur_back_color, all_id_list_for_js_variable, \
    make_colored_text_html, get_zero_degree
from code_.util.html_util import dependency_colors

local_all_id_list = []
done_key = {}


def recur_for_dependency_inside_method(
        key, id_list, super_list, dependency_dict, search_field_list=None):
    field_found_because_nothing_to_find = search_field_list is None or len(search_field_list) == 0
    key_ = get_key_from_dependency_inside_method_key(key)
    field_found = not field_found_because_nothing_to_find and (
            (is_field_key(key_) and key_ in search_field_list) or
            (is_index_key(key_) and get_field_key_from_index_key(key_) in search_field_list) or
            (is_field_reference_key(key_) and get_field_key_from_reference(key_) in search_field_list))
    depth = len(super_list)
    is_recurred = key in super_list
    back_color = recur_back_color if is_recurred else dependency_colors[depth]
    padding = '|'.join([' '.join(['&nbsp;'] * 2)] * depth)
    id = ':'.join(id_list)
    local_all_id_list.append(id)
    display_style_str = ""
    if depth > 0:
        display_style_str = 'style="display:none"'
    sub_str_list = ['<text ' + display_style_str + ' onclick="dependency_click(\'' + id + '\')" id=' + id + '>' \
                    + padding + make_colored_text_html(key, back_color) + "<br></text>"]
    if key in done_key:
        return sub_str_list, field_found
    done_key[key] = ''
    id_count = 0
    if not is_recurred:
        if key in dependency_dict:
            dependency_in_dir_list = list(dependency_dict[key].keys())
            dependency_in_dir_list.sort()
            for child_node in dependency_in_dir_list:
                id_count += 1
                id_list_copy = id_list.copy()
                id_list_copy.append(str(id_count))
                super_list_copy = super_list.copy()
                super_list_copy.append(key)
                sub_node_list, child_node_found = recur_for_dependency_inside_method(
                    child_node, id_list_copy, super_list_copy, dependency_dict, search_field_list)
                sub_str_list.extend(sub_node_list)
                field_found = field_found or child_node_found
    return sub_str_list, field_found


def get_dependency_html_inside_method(
        id_list, super_list, dependency_in, dependency_out, search_fk_list, id_count):
    dependency_in = convert_dependency_to_longer_key(dependency_in)
    dependency_out = convert_dependency_to_longer_key(dependency_out)
    all_key = {}
    for k, v in dependency_in.items():
        all_key[k] = ''
        for vi in v:
            all_key[vi] = ''
    print(len(all_key))
    out_zero_key_list = get_zero_degree(all_key, dependency_out)
    html_str_list = []
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
        id_count += 1
        id_list_copy = id_list.copy()
        id_list_copy.append(str(id_count))
        super_list_copy = super_list.copy()
        local_all_id_list.clear()
        done_key.clear()
        html_list, field_found = \
            recur_for_dependency_inside_method(key, id_list_copy, super_list_copy, dependency_in, search_fk_list)
        if field_found:
            html_str_list.extend(html_list)
            all_id_list_for_js_variable.extend(local_all_id_list)

    return html_str_list
