import pickle

from code_.util.file_util import fieldkey2fieldTypekey_path, long_key2shorter_key_dict_path, \
    long_key2shorter_key_dict_reverse_path, read_relation_file_path, writen_relation_file_path, \
    read_relation_compressed_path, \
    written_relation_compressed_path, relation_path, method2relations_file_path, method2global_relations_file_path, \
    method2relations_compressed_path, method2global_relations_compressed_path, \
    methodKey2methodFeatureRelationList_file_path, fieldKey2fieldFeatureRelationList_file_path, \
    methodKey2methodFeatureRelationList_compressed_path, fieldKey2fieldFeatureRelationList_compressed_path


def make_shorter_key(count):
    return '#$%' + str(count) + '^&*'


def make_shorter_keys():
    count = 0
    field_key2shorter_key_dict = {}
    field_key2shorter_key_dict_reverse = {}

    read_relation = pickle.load(open(read_relation_file_path, "rb"))
    for k, v in read_relation.items():
        if k not in field_key2shorter_key_dict:
            count += 1
            shorter_key = make_shorter_key(count)
            field_key2shorter_key_dict[k] = shorter_key
            field_key2shorter_key_dict_reverse[shorter_key] = k
        for vi in v:
            if vi[0] not in field_key2shorter_key_dict:
                count += 1
                shorter_key = make_shorter_key(count)
                field_key2shorter_key_dict[vi[0]] = shorter_key
                field_key2shorter_key_dict_reverse[shorter_key] = vi[0]
            if vi[1] not in field_key2shorter_key_dict:
                count += 1
                shorter_key = make_shorter_key(count)
                field_key2shorter_key_dict[vi[1]] = shorter_key
                field_key2shorter_key_dict_reverse[shorter_key] = vi[1]

    relation = pickle.load(open(relation_path, "rb"))
    for r in relation:
        key = r['readFieldKey']
        if key not in field_key2shorter_key_dict:
            count += 1
            shorter_key = make_shorter_key(count)
            field_key2shorter_key_dict[key] = shorter_key
            field_key2shorter_key_dict_reverse[shorter_key] = key
        key = r['writenFieldKey']
        if key not in field_key2shorter_key_dict:
            count += 1
            shorter_key = make_shorter_key(count)
            field_key2shorter_key_dict[key] = shorter_key
            field_key2shorter_key_dict_reverse[shorter_key] = key

    fieldkey2fieldTypekey = pickle.load(open(fieldkey2fieldTypekey_path, "rb"))
    for k, v in fieldkey2fieldTypekey.items():
        count += 1
        shorter_key = make_shorter_key(count)
        field_key2shorter_key_dict[k] = shorter_key
        field_key2shorter_key_dict_reverse[shorter_key] = k

    # methodKey2methodFeatureRelationList = \
    #     pickle.load(open(methodKey2methodFeatureRelationList_file_path, 'rb'))
    # fieldKey2fieldFeatureRelationList = \
    #     pickle.load(open(fieldKey2fieldFeatureRelationList_file_path, 'rb'))
    # for k, v in methodKey2methodFeatureRelationList.items():
    #     count += 1
    #     shorter_key = make_shorter_key(count)
    #     field_key2shorter_key_dict[k] = shorter_key
    #     field_key2shorter_key_dict_reverse[shorter_key] = k
    # for k, v in fieldKey2fieldFeatureRelationList.items():
    #     count += 1
    #     shorter_key = make_shorter_key(count)
    #     field_key2shorter_key_dict[k] = shorter_key
    #     field_key2shorter_key_dict_reverse[shorter_key] = k
    print(len(field_key2shorter_key_dict))
    pickle.dump(field_key2shorter_key_dict, open(long_key2shorter_key_dict_path, 'wb'))
    pickle.dump(field_key2shorter_key_dict_reverse, open(long_key2shorter_key_dict_reverse_path, 'wb'))


def compress_read_and_written_relation():
    read_relation = pickle.load(open(read_relation_file_path, "rb"))
    written_relation = pickle.load(open(writen_relation_file_path, "rb"))
    field_key2shorter_key_dict = pickle.load(open(long_key2shorter_key_dict_path, 'rb'))

    read_relation_compressed = {}
    written_relation_compressed = {}

    for k, v in read_relation.items():
        if k in field_key2shorter_key_dict:
            k = field_key2shorter_key_dict[k]
        for vi in v:
            if vi[0] in field_key2shorter_key_dict:
                vi[0] = field_key2shorter_key_dict[vi[0]]
            if vi[1] in field_key2shorter_key_dict:
                vi[1] = field_key2shorter_key_dict[vi[1]]
        read_relation_compressed[k] = v
    for k, v in written_relation.items():
        if k in field_key2shorter_key_dict:
            k = field_key2shorter_key_dict[k]
        for vi in v:
            if vi[0] in field_key2shorter_key_dict:
                vi[0] = field_key2shorter_key_dict[vi[0]]
            if vi[1] in field_key2shorter_key_dict:
                vi[1] = field_key2shorter_key_dict[vi[1]]
        written_relation_compressed[k] = v
    pickle.dump(read_relation_compressed, open(read_relation_compressed_path, 'wb'))
    pickle.dump(written_relation_compressed, open(written_relation_compressed_path, 'wb'))


def compress_method2relation_and_global_relation():
    method2relations = pickle.load(open(method2relations_file_path, 'rb'))
    method2global_relations = pickle.load(open(method2global_relations_file_path, 'rb'))
    field_key2shorter_key_dict = pickle.load(open(long_key2shorter_key_dict_path, 'rb'))
    method2relations_compressed = {}
    method2global_relations_compressed = {}
    for k, v in method2relations.items():
        if k in field_key2shorter_key_dict:
            k = field_key2shorter_key_dict[k]
        for vi in v:
            vi[0] = field_key2shorter_key_dict[vi[0]]
            vi[1] = field_key2shorter_key_dict[vi[1]]
        method2relations_compressed[k] = v
    for k, v in method2global_relations.items():
        if k in field_key2shorter_key_dict:
            k = field_key2shorter_key_dict[k]
        for vi in v:
            vi[0] = field_key2shorter_key_dict[vi[0]]
            vi[1] = field_key2shorter_key_dict[vi[1]]
        method2global_relations_compressed[k] = v
    pickle.dump(method2relations_compressed, open(method2relations_compressed_path, 'wb'))
    pickle.dump(method2global_relations_compressed, open(method2global_relations_compressed_path, 'wb'))


def compress_feature_relation_list():
    methodKey2methodFeatureRelationList = \
        pickle.load(open(methodKey2methodFeatureRelationList_file_path, 'rb'))
    fieldKey2fieldFeatureRelationList = \
        pickle.load(open(fieldKey2fieldFeatureRelationList_file_path, 'rb'))
    field_key2shorter_key_dict = pickle.load(open(long_key2shorter_key_dict_path, 'rb'))
    methodKey2methodFeatureRelationList_compressed = {}
    fieldKey2fieldFeatureRelationList_compressed = {}
    for k, v in methodKey2methodFeatureRelationList.items():
        if k in field_key2shorter_key_dict:
            k = field_key2shorter_key_dict[k]
        for vi in v:
            if vi[0] in field_key2shorter_key_dict:
                vi[0] = field_key2shorter_key_dict[vi[0]]
            if vi[1] in field_key2shorter_key_dict:
                vi[1] = field_key2shorter_key_dict[vi[1]]
        methodKey2methodFeatureRelationList_compressed[k] = v
    for k, v in fieldKey2fieldFeatureRelationList.items():
        if k in field_key2shorter_key_dict:
            k = field_key2shorter_key_dict[k]
        for vi in v:
            if vi[0] in field_key2shorter_key_dict:
                vi[0] = field_key2shorter_key_dict[vi[0]]
            if vi[1] in field_key2shorter_key_dict:
                vi[1] = field_key2shorter_key_dict[vi[1]]
        fieldKey2fieldFeatureRelationList_compressed[k] = v
    pickle.dump(methodKey2methodFeatureRelationList_compressed,
                open(methodKey2methodFeatureRelationList_compressed_path, 'wb'))
    pickle.dump(fieldKey2fieldFeatureRelationList_compressed,
                open(fieldKey2fieldFeatureRelationList_compressed_path, 'wb'))


def check_compression():
    methodKey2methodFeatureRelationList_compressed = \
        pickle.load(open(methodKey2methodFeatureRelationList_compressed_path, 'rb'))
    fieldKey2fieldFeatureRelationList_compressed = \
        pickle.load(open(fieldKey2fieldFeatureRelationList_compressed_path, 'rb'))
    pass


if __name__ == '__main__':
    make_shorter_keys()
    compress_read_and_written_relation()
    compress_method2relation_and_global_relation()
    compress_feature_relation_list()
    # check_compression()
    pass
