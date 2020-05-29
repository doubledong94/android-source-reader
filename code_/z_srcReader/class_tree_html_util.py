from code_.z_srcReader.method_usage_html_util import all_id_list_for_js_variable, make_colored_text_html
from code_.util.html_util import dependency_colors


def recur_for_class_tree(key, id_list, super_list, dependency_dict, search_key):
    depth = len(super_list)
    back_color = dependency_colors[depth]
    padding = '|'.join([' '.join(['&nbsp;'] * 2)] * depth)
    id = ':'.join(id_list)
    searched_flag = search_key == '' or search_key == key
    display_style_str = ""
    if depth > 0:
        display_style_str = 'style="display:none"'
    sub_str_list = ['<text ' + display_style_str+ ' onclick="dependency_click(\'' + id + '\')" id=' + id + '>' \
                    + padding + make_colored_text_html(key, back_color) + "<br></text>"]
    ids = [id]
    id_count = 0
    if key in dependency_dict:
        for child_node in dependency_dict[key]:
            id_count += 1
            id_list_copy = id_list.copy()
            super_list_copy = super_list.copy()
            id_list_copy.append(str(id_count))
            super_list_copy.append(key)
            recur_html, child_ids, child_searched_flag = recur_for_class_tree(
                child_node, id_list_copy, super_list_copy, dependency_dict, search_key)
            searched_flag = searched_flag or child_searched_flag
            sub_str_list.extend(recur_html)
            ids.extend(child_ids)
    return sub_str_list, ids, searched_flag


def get_class_tree_html(dependency_in, search_method_key, id_index_head):
    all_id_list_for_js_variable.clear()
    out_zero_key_list = dependency_in['java.lang.Object']
    id_count = 0
    html_str_list = []
    for key in out_zero_key_list:
        id_count += 1
        dependency_str, ids, searched_flag = recur_for_class_tree(
            key, [id_index_head + str(id_count)], [], dependency_in, search_method_key)
        if not dependency_str == "" and searched_flag:
            html_str_list.extend(dependency_str)
            html_str_list.append('<br>')
            all_id_list_for_js_variable.extend(ids)
    return ''.join(html_str_list)
