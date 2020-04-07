# d2->d1 {k,v}中的v是一个list
def merge_dict_with_value_merged(d1, d2):
    for k, v in d2.items():
        if k in d1:
            for vi in v:
                if vi not in d1[k]:
                    d1[k].append(vi)
        else:
            d1[k] = v
