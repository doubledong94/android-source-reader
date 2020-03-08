import pickle

from code_.util.file_util import long_key2shorter_key_dict_reverse_path, long_key2shorter_key_dict_path

field_key2shorter_key_dict = pickle.load(open(long_key2shorter_key_dict_path, 'rb'))
field_key2shorter_key_dict_reverse = pickle.load(open(long_key2shorter_key_dict_reverse_path, 'rb'))


def decompress_by_replace(html_txt, shorter_key_list):
    for shorter_key in shorter_key_list:
        html_txt.replace(shorter_key, field_key2shorter_key_dict_reverse[shorter_key])
    return html_txt


def to_shorter_key(long_key):
    if long_key in field_key2shorter_key_dict:
        return field_key2shorter_key_dict[long_key]
    else:
        return long_key


def to_longer_key(short_key):
    if short_key in field_key2shorter_key_dict_reverse:
        return field_key2shorter_key_dict_reverse[short_key]
    else:
        return short_key
