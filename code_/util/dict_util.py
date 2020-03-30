# d2->d1 {k,v}中的v是一个list
def merge_dict_with_value_merged(d1, d2):
    for k, v in d2.items():
        if k in d1:
            d1[k].extend(v)
            d1[k] = list(set(d1[k]))
        else:
            d1[k] = v
