import pickle

from code_.util.file_util import fieldkey2fieldTypekey_path, LVKey2LVTypeKey_path

fieldkey2fieldTypekey = pickle.load(open(fieldkey2fieldTypekey_path, 'rb'))
LVKey2LVTypeKey = pickle.load(open(LVKey2LVTypeKey_path, 'rb'))


def is_lv_key(key):
    return key in LVKey2LVTypeKey


def is_field_key(key):
    return key in fieldkey2fieldTypekey and ":" not in key


def is_parameter_key(key):
    for i in range(20):
        if key.endswith(":Parameter" + str(i)):
            return True
    return False


def is_guest_key(key):
    return key.endswith(":Guest")


def is_condition_key(key):
    return key.endswith(":Condition") or key.endswith(":Case")


def is_return_key(key):
    return key.endswith(":Return")


def is_local_key(key):
    return key.endswith(":Local")


def get_feature_key(key, i):
    return key + "Feature" + str(i)
