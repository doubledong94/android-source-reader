from code_.util.key_util import is_return_key, is_condition_key, is_parameter_key, is_field_key, \
    is_local_key_or_local_variable, is_reference_key, get_method_key_from_parameter_key

# 0: return         =parameter
# 1: return         =local
# 2: return         =field
# 3: return         =methodCall

# 4: return=        parameter
# 5: condition=     parameter
# 6: field=         parameter
# 7: methodCall=    parameter
# 8: reference=     parameter

# 9: condition      =parameter
# 10: condition     =local
# 11: condition     =field
# 12: condition     =methodCall

# 13: field         =parameter
# 14: field         =local
# 15: field         =field
# 16: field         =methodCall

# 17: return=       field
# 18: condition=    field
# 19: field=        field
# 20: methodCall=   field
# 21: reference=    field

# 22: methodCall    =parameter
# 23: methodCall    =local
# 24: methodCall    =field
# 25: methodCall    =methodCall

# 26: return=       methodCall
# 27: local=        methodCall
# 28: condition=    methodCall
# 29: field=        methodCall
# 30: methodCall=   methodCall
# 31: reference=    methodCall

# 32: reference     =parameter
# 33: reference     =local
# 34: reference     =field
# 35: reference     =methodCall

# 36: parameter     =parameter
# 37: parameter     =local
# 38: parameter     =field
# 39: parameter     =methodCall
from code_.util.key_conversion_util import to_longer_key_if_compressed

method_feature_len = 40


def get_method_feature_relation_list(method_key, method_relation_list):
    featured_relation_list = []
    for i in range(method_feature_len):
        featured_relation_list.append([])
    method_key = to_longer_key_if_compressed(method_key)
    for r in method_relation_list:
        written_key = to_longer_key_if_compressed(r[0])
        read_key = to_longer_key_if_compressed(r[1])
        if is_return_key(written_key):
            if is_parameter_key(read_key):
                index = 0
                featured_relation_list[index].append(r)
            elif is_local_key_or_local_variable(read_key):
                index = 1
                featured_relation_list[index].append(r)
            elif is_field_key(read_key):
                index = 2
                featured_relation_list[index].append(r)
            elif is_return_key(read_key):
                index = 3
                featured_relation_list[index].append(r)
        if is_parameter_key(read_key):
            if is_return_key(written_key):
                index = 4
                featured_relation_list[index].append(r)
            elif is_condition_key(written_key):
                index = 5
                featured_relation_list[index].append(r)
            elif is_field_key(written_key):
                index = 6
                featured_relation_list[index].append(r)
            elif is_parameter_key(written_key):
                index = 7
                featured_relation_list[index].append(r)
            elif is_reference_key(written_key):
                index = 8
                featured_relation_list[index].append(r)
        if is_condition_key(written_key):
            if is_parameter_key(read_key):
                index = 9
                featured_relation_list[index].append(r)
            elif is_local_key_or_local_variable(read_key):
                index = 10
                featured_relation_list[index].append(r)
            elif is_field_key(read_key):
                index = 11
                featured_relation_list[index].append(r)
            elif is_return_key(read_key):
                index = 12
                featured_relation_list[index].append(r)
        if is_field_key(written_key):
            if is_parameter_key(read_key):
                index = 13
                featured_relation_list[index].append(r)
            elif is_local_key_or_local_variable(read_key):
                index = 14
                featured_relation_list[index].append(r)
            elif is_field_key(read_key):
                index = 15
                featured_relation_list[index].append(r)
            elif is_return_key(read_key):
                index = 16
                featured_relation_list[index].append(r)
        if is_field_key(read_key):
            if is_return_key(written_key):
                index = 17
                featured_relation_list[index].append(r)
            elif is_condition_key(written_key):
                index = 18
                featured_relation_list[index].append(r)
            elif is_field_key(written_key):
                index = 19
                featured_relation_list[index].append(r)
            elif is_parameter_key(written_key):
                index = 20
                featured_relation_list[index].append(r)
            elif is_reference_key(written_key):
                index = 21
                featured_relation_list[index].append(r)
        if is_parameter_key(written_key):
            if get_method_key_from_parameter_key(written_key) == method_key:
                if is_parameter_key(read_key):
                    index = 36
                    featured_relation_list[index].append(r)
                elif is_local_key_or_local_variable(read_key):
                    index = 37
                    featured_relation_list[index].append(r)
                elif is_field_key(read_key):
                    index = 38
                    featured_relation_list[index].append(r)
                elif is_return_key(read_key):
                    index = 39
                    featured_relation_list[index].append(r)
            else:
                if is_parameter_key(read_key):
                    index = 22
                    featured_relation_list[index].append(r)
                elif is_local_key_or_local_variable(read_key):
                    index = 23
                    featured_relation_list[index].append(r)
                elif is_field_key(read_key):
                    index = 24
                    featured_relation_list[index].append(r)
                elif is_return_key(read_key):
                    index = 25
                    featured_relation_list[index].append(r)
        if is_return_key(read_key):
            if is_return_key(written_key):
                index = 26
                featured_relation_list[index].append(r)
            elif is_local_key_or_local_variable(written_key):
                index = 27
                featured_relation_list[index].append(r)
            elif is_condition_key(written_key):
                index = 28
                featured_relation_list[index].append(r)
            elif is_field_key(written_key):
                index = 29
                featured_relation_list[index].append(r)
            elif is_parameter_key(written_key):
                index = 30
                featured_relation_list[index].append(r)
            elif is_reference_key(written_key):
                index = 31
                featured_relation_list[index].append(r)
        if is_reference_key(written_key):
            if is_parameter_key(read_key):
                index = 32
                featured_relation_list[index].append(r)
            elif is_local_key_or_local_variable(read_key):
                index = 33
                featured_relation_list[index].append(r)
            elif is_field_key(read_key):
                index = 34
                featured_relation_list[index].append(r)
            elif is_return_key(read_key):
                index = 35
                featured_relation_list[index].append(r)
    return featured_relation_list


if __name__ == "__main__":
    pass
    # method2global_relations = pickle.load(open(method2global_relations_file_path, 'rb'))
    # methodKey2methodFeature = {}
    # methodKey2methodFeatureRelationList = {}
    # for methodKey, relations in method2global_relations.items():
    #     methodKey2methodFeature[methodKey], methodKey2methodFeatureRelation = \
    #         get_method_feature(methodKey,relations)
    #     for i in range(method_feature_len):
    #         methodKey2methodFeatureRelationList[get_feature_key(methodKey, i)] = \
    #             methodKey2methodFeatureRelation[i]
    # pickle.dump(methodKey2methodFeature, open(methodKey2methodFeature_file_path, 'wb'))
    # pickle.dump(methodKey2methodFeatureRelationList, open(methodKey2methodFeatureRelationList_file_path, 'wb'))
