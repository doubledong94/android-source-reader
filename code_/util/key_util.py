import pickle

from code_.util.file_util import fieldkey2fieldTypekey_path, LVKey2LVTypeKey_path

fieldkey2fieldTypekey = pickle.load(open(fieldkey2fieldTypekey_path, 'rb'))
LVKey2LVTypeKey = pickle.load(open(LVKey2LVTypeKey_path, 'rb'))


def is_lv_key_or_index(key):
    return key in LVKey2LVTypeKey or key.endswith("-Index")


def is_lv_key(key):
    return key in LVKey2LVTypeKey


def is_field_key(key):
    return key in fieldkey2fieldTypekey and ":" not in key


def is_parameter_key(key):
    for i in range(20):
        if key.endswith(":Parameter" + str(i)):
            return True
    return False


def is_condition_key(key):
    return key.endswith(":Condition") or key.endswith(":Case") or key.endswith(":Switch")


def is_return_key(key):
    return key.endswith(":Return")


def is_local_key_or_local_variable(key):
    return is_local_key(key) or is_lv_key(key)


def is_local_key(key):
    return key.endswith(":Local") or key == 'false' or key == 'true'


def is_method_reference_key(key):
    return key.endswith(':Reference')


def is_field_reference_key(key):
    return key.endswith('-Reference')


def is_reference_key(key):
    return is_method_reference_key(key) or is_field_reference_key(key)


def get_method_feature_key(method_key, i):
    return method_key + "Feature" + str(i)


def get_field_feature_key(field_key, i):
    return field_key + "-Feature" + str(i)


def get_method_key_from_parameter_key(parameter_key):
    if len(parameter_key) > 12:
        mk = parameter_key[0:-10]
        if not mk.endswith(':'):
            mk = mk[0:-1]
        return mk
    else:
        return ''


def get_method_key_from_return_key(return_key):
    if len(return_key) > 7:
        return return_key[0:-6]
    else:
        return ''


def get_key_from_reference(reference_key):
    k = reference_key[0:-9]
    if not k.endswith(':'):
        k = k[0:-1]
    return k


def is_method_feature_key(key):
    for i in range(40):
        if key.endswith(":Feature" + str(i)):
            return True
    return False


def get_method_feature_index(feature_key):
    if feature_key[-2] == 'e':
        return int(feature_key[-1:])
    else:
        return int(feature_key[-2:])


def get_method_key_from_feature(feature_key):
    if feature_key[-2] == 'e':
        return feature_key[0:-8]
    else:
        return feature_key[0:-9]


def get_field_key_from_feature(feature_key):
    if feature_key[-2] == 'e':
        return feature_key[0:-9]
    else:
        return feature_key[0:-10]


def is_field_feature_key(key):
    for i in range(40):
        if key.endswith("-Feature" + str(i)):
            return True
    return False
