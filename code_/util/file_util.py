import os

current_dir = os.path.abspath('.')

json_folder = '/root/CLionProjects/JParser/cmake-build-debug/json/'
fieldkey2fieldTypekey_json_path = json_folder + 'fieldkey2fieldTypekey.json'
fieldKey2typeKey_json_path = json_folder + 'fieldKey2typeKey.json'
LVKey2LVTypeKey_json_path = json_folder + 'LVKey2LVTypeKey.json'
LVKey2typeKey_json_path = json_folder + 'LVKey2typeKey.json'
methodKey2typeKey_json_path = json_folder + 'methodKey2typeKey.json'
packagelist_json_path = json_folder + 'packagelist.json'
relation_json_path = json_folder + 'relation.json'
interfaceType_json_path = json_folder + 'interfaceType.json'
superTypes_json_path = json_folder + 'superTypes.json'
typekey2fieldkey_json_path = json_folder + 'typekey2fieldkey.json'
typekey2methodkey_json_path = json_folder + 'typekey2methodkey.json'
typeKey2package_json_path = json_folder + 'typeKey2package.json'
methodKey2srcLoc_json_path = json_folder + 'methodKey2src.json'
fieldKey2srcLoc_json_path = json_folder + 'fieldKey2src.json'

data_abs_dir = current_dir + '/data_/'
compressed_data_abs_dir = current_dir + '/data_/compressed/'
txt_abs_dir = current_dir + '/txt_/'
src_abs_dir = current_dir + '/androidSrc/'
methodKey2srcLoc_path = data_abs_dir + 'methodKey2src.pkl'
fieldKey2srcLoc_path = data_abs_dir + 'fieldKey2src.pkl'
fieldkey2fieldTypekey_path = data_abs_dir + 'fieldkey2fieldTypekey.pkl'
fieldKey2typeKey_path = data_abs_dir + 'fieldKey2typeKey.pkl'
LVKey2LVTypeKey_path = data_abs_dir + 'LVKey2LVTypeKey.pkl'
LVKey2typeKey_path = data_abs_dir + 'LVKey2typeKey.pkl'
methodKey2typeKey_path = data_abs_dir + 'methodKey2typeKey.pkl'
packagelist_path = data_abs_dir + 'packagelist.pkl'
relation_path = data_abs_dir + 'relation.pkl'
interfaceType_path = data_abs_dir + 'interfaceType.pkl'
superTypes_path = data_abs_dir + 'superTypes.pkl'
subTypes_path = data_abs_dir + 'subTypes.pkl'
typekey2fieldkey_path = data_abs_dir + 'typekey2fieldkey.pkl'
typekey2methodkey_path = data_abs_dir + 'typekey2methodkey.pkl'
typeKey2package_path = data_abs_dir + 'typeKey2package.pkl'
read_relation_file_path = data_abs_dir + 'read_relation.pkl'
writen_relation_file_path = data_abs_dir + 'writen_relation.pkl'

particle_relations_file_path = data_abs_dir + 'particle_relations.pkl'
method2particle_relations_file_path = data_abs_dir + 'method2particle_relations.pkl'
method2relations_file_path = data_abs_dir + 'method2relations.pkl'
LV2relations_file_path = data_abs_dir + 'LV2relations.pkl'
method2global_relations_file_path = data_abs_dir + 'method2global_relations.pkl'
global_relations_file_path = data_abs_dir + 'global_relations.pkl'
type2instance_for_field_file_path = data_abs_dir + 'type2instance_for_field.pkl'
type2instance_for_local_file_path = data_abs_dir + 'type2instance_for_local.pkl'
methodKey2methodFeature_file_path = data_abs_dir + 'methodKey2methodFeature.pkl'
methodKey2methodFeatureRelationList_file_path = data_abs_dir + 'methodKey2methodFeatureRelationList.pkl'
fieldKey2fieldFeature_file_path = data_abs_dir + 'fieldKey2fieldFeature.pkl'
fieldKey2fieldFeatureRelationList_file_path = data_abs_dir + 'fieldKey2fieldFeatureRelationList.pkl'
feature_key2methodKeys_file_path = data_abs_dir + 'feature_key2methodKeys.pkl'
feature_key2fieldKeys_file_path = data_abs_dir + 'feature_key2fieldKeys.pkl'

method2lv_dependency_in_dir_file_path = data_abs_dir + 'method2lv_dependency_in_dir.pkl'
method2lv_dependency_out_dir_file_path = data_abs_dir + 'method2lv_dependency_out_dir.pkl'

class2field_dependency_in_dir_file_path = data_abs_dir + 'class2field_dependency_in_dir.pkl'
class2field_dependency_out_dir_file_path = data_abs_dir + 'class2field_dependency_out_dir.pkl'

class2method_dependency_in_dir_file_path = data_abs_dir + 'class2method_dependency_in_dir.pkl'
class2method_dependency_out_dir_file_path = data_abs_dir + 'class2method_dependency_out_dir.pkl'

method_size_map_path = data_abs_dir + 'method_size_map.pkl'
method_size_map_out_path = data_abs_dir + 'method_size_map_out.pkl'

long_key2shorter_key_dict_path = compressed_data_abs_dir + 'long_key2shorter_key_dict.pkl'
long_key2shorter_key_dict_reverse_path = compressed_data_abs_dir + 'long_key2shorter_key_dict_reverse.pkl'

read_relation_compressed_path = compressed_data_abs_dir + 'read_relation_compressed.pkl'
written_relation_compressed_path = compressed_data_abs_dir + 'written_relation_compressed.pkl'

method2relations_compressed_path = compressed_data_abs_dir + 'method2relations_compressed.pkl'
method2global_relations_compressed_path = compressed_data_abs_dir + 'method2global_relations_compressed.pkl'

methodKey2methodFeatureRelationList_compressed_path = \
    compressed_data_abs_dir + 'methodKey2methodFeatureRelationList_compressed.pkl'
fieldKey2fieldFeatureRelationList_compressed_path = \
    compressed_data_abs_dir + 'fieldKey2fieldFeatureRelationList_compressed.pkl'



def get_lines(file_path, start_line, end_line):
    f = open(file_path)
    ret_str = ''
    line_count = 0
    for line in f:
        line_count += 1
        if start_line <= line_count <= end_line:
            ret_str += line

    f.close()
    ret_str = ret_str.replace('\n', '<br>')
    ret_str = ret_str.replace('\t', '    ')
    ret_str = ret_str.replace(' ', '&nbsp;')
    return ret_str
