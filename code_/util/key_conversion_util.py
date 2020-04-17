import pickle

from code_.util.file_util import long_key2shorter_key_dict_reverse_path, long_key2shorter_key_dict_path
from code_.util.key_util import get_key_from_dependency_inside_method_key, is_condition_key, \
    get_method_key_from_condition_key, is_method_reference_key, get_key_from_reference, is_field_reference_key, \
    get_field_key_from_reference

long_key2shorter_key_dict = pickle.load(open(long_key2shorter_key_dict_path, 'rb'))
long_key2shorter_key_dict_reverse = pickle.load(open(long_key2shorter_key_dict_reverse_path, 'rb'))


def decompress_by_replace(html_txt, shorter_key_list):
    for shorter_key in shorter_key_list:
        html_txt.replace(shorter_key, long_key2shorter_key_dict_reverse[shorter_key])
    return html_txt


def to_shorter_key_by_replacement(long_key, replacement):
    if replacement in long_key2shorter_key_dict:
        return long_key.replace(replacement, long_key2shorter_key_dict[replacement])
    elif is_condition_key(replacement):
        k = get_method_key_from_condition_key(replacement)
        return to_shorter_key_by_replacement(long_key, k)
    elif is_method_reference_key(replacement):
        k = get_key_from_reference(replacement)
        return to_shorter_key_by_replacement(long_key, k)
    elif is_field_reference_key(replacement):
        k = get_field_key_from_reference(replacement)
        return to_shorter_key_by_replacement(long_key, k)

    elif replacement.endswith(":Local"):
        k = replacement[:-len('Local')]
        return to_shorter_key_by_replacement(long_key, k)

    # elif replacement.endswith(".this"):
    #     k = replacement[:-len('.this')]
    #     return to_shorter_key_by_replacement(long_key, k)
    #
    # elif replacement.endswith(".super"):
    #     k = replacement[:-len('.super')]
    #     return to_shorter_key_by_replacement(long_key, k)
    #
    # elif replacement.endswith(".length"):
    #     k = replacement[:-len('.length')]
    #     return to_shorter_key_by_replacement(long_key, k)
    #
    # elif replacement.endswith("-Index"):
    #     k = replacement[:-len('-Index')]
    #     return to_shorter_key_by_replacement(long_key, k)

    else:
        return long_key


def to_longer_key_by_replacement(short_key, replacement):
    if replacement in long_key2shorter_key_dict_reverse:
        return short_key.replace(replacement, long_key2shorter_key_dict_reverse[replacement])

    elif replacement.endswith('Condition'):
        k = replacement[:-len('Condition')]
        return to_longer_key_by_replacement(short_key, k)
    elif replacement.endswith('Case'):
        k = replacement[:-len('Case')]
        return to_longer_key_by_replacement(short_key, k)
    elif replacement.endswith('Switch'):
        k = replacement[:-len('Switch')]
        return to_longer_key_by_replacement(short_key, k)
    elif replacement.endswith('-Reference'):
        k = replacement[:-len('-Reference')]
        return to_longer_key_by_replacement(short_key, k)
    elif replacement.endswith('Reference'):
        k = replacement[:-len('Reference')]
        return to_longer_key_by_replacement(short_key, k)

    elif replacement.endswith('Local'):
        k = replacement[:-len('Local')]
        return to_longer_key_by_replacement(short_key, k)

    # elif replacement.endswith('.this'):
    #     k = replacement[:-len('.this')]
    #     return to_longer_key_by_replacement(short_key, k)
    #
    # elif replacement.endswith('.super'):
    #     k = replacement[:-len('.super')]
    #     return to_longer_key_by_replacement(short_key, k)
    #
    # elif replacement.endswith('.length'):
    #     k = replacement[:-len('.length')]
    #     return to_longer_key_by_replacement(short_key, k)
    #
    # elif replacement.endswith('-Index'):
    #     k = replacement[:-len('-Index')]
    #     return to_longer_key_by_replacement(short_key, k)

    else:
        return short_key


def to_shorter_key_if_compressed(long_key):
    if long_key in long_key2shorter_key_dict:
        return long_key2shorter_key_dict[long_key]
    elif is_condition_key(long_key):
        k = get_method_key_from_condition_key(long_key)
        return to_shorter_key_by_replacement(long_key, k)
    elif is_method_reference_key(long_key):
        k = get_key_from_reference(long_key)
        return to_shorter_key_by_replacement(long_key, k)
    elif is_field_reference_key(long_key):
        k = get_field_key_from_reference(long_key)
        return to_shorter_key_by_replacement(long_key, k)

    elif long_key.endswith(":Local"):
        k = long_key[:-len('Local')]
        return to_shorter_key_by_replacement(long_key, k)

    # elif long_key.endswith(".this"):
    #     k = long_key[:-len('.this')]
    #     return to_shorter_key_by_replacement(long_key, k)
    #
    # elif long_key.endswith(".super"):
    #     k = long_key[:-len('.super')]
    #     return to_shorter_key_by_replacement(long_key, k)
    #
    # elif long_key.endswith(".length"):
    #     k = long_key[:-len('.length')]
    #     return to_shorter_key_by_replacement(long_key, k)
    #
    # elif long_key.endswith("-Index"):
    #     k = long_key[:-len('-Index')]
    #     return to_shorter_key_by_replacement(long_key, k)

    else:
        return long_key


def to_longer_key_if_compressed(short_key):
    if short_key in long_key2shorter_key_dict_reverse:
        return long_key2shorter_key_dict_reverse[short_key]
    elif short_key.endswith('Condition'):
        k = short_key[:-len('Condition')]
        return to_longer_key_by_replacement(short_key, k)
    elif short_key.endswith('Case'):
        k = short_key[:-len('Case')]
        return to_longer_key_by_replacement(short_key, k)
    elif short_key.endswith('Switch'):
        k = short_key[:-len('Switch')]
        return to_longer_key_by_replacement(short_key, k)
    elif short_key.endswith('-Reference'):
        k = short_key[:-len('-Reference')]
        return to_longer_key_by_replacement(short_key, k)
    elif short_key.endswith('Reference'):
        k = short_key[:-len('Reference')]
        return to_longer_key_by_replacement(short_key, k)
    elif short_key.endswith('Local'):
        k = short_key[:-len('Local')]
        return to_longer_key_by_replacement(short_key, k)

    # elif short_key.endswith('.this'):
    #     k = short_key[:-len('.this')]
    #     return to_longer_key_by_replacement(short_key, k)
    #
    # elif short_key.endswith('.super'):
    #     k = short_key[:-len('.super')]
    #     return to_longer_key_by_replacement(short_key, k)
    #
    # elif short_key.endswith('.length'):
    #     k = short_key[:-len('.length')]
    #     return to_longer_key_by_replacement(short_key, k)
    #
    # elif short_key.endswith('-Index'):
    #     k = short_key[:-len('-Index')]
    #     return to_longer_key_by_replacement(short_key, k)

    else:
        return short_key


def to_shorter_key_for_dependency_inside_method(long_key):
    key_rep = get_key_from_dependency_inside_method_key(long_key)
    return to_shorter_key_by_replacement(long_key, key_rep)


def to_longer_key_for_dependency_inside_method(short_key):
    key_rep = get_key_from_dependency_inside_method_key(short_key)
    return to_longer_key_by_replacement(short_key, key_rep)


def convert_dependency_to_longer_key(dependency):
    dependency_long_key = {}
    for d1, d2 in dependency.items():
        d1 = to_longer_key_for_dependency_inside_method(d1)
        d2_compressed = {}
        for d3 in d2.keys():
            d3 = to_longer_key_for_dependency_inside_method(d3)
            d2_compressed[d3] = ''
        dependency_long_key[d1] = d2_compressed
    return dependency_long_key
