import math


# real world datasets characteristics
def get_data(h=6):
    # dataset number [dataset name, #users, #permissions, max#perm-per-user, max#users-have-perm]
    datasets = { 1: ['datasets/fire1.txt', 365, 709, 617, 251],
                 2: ['datasets/fire2.txt', 325, 590, 590, 298],
                 3: ['datasets/domino.txt', 79, 231, 209, 52],
                 4: ['datasets/apj.txt', 2044, 1164, 58, 291],
                 5: ['datasets/emea.txt', 35, 3046, 554, 32],
                 6: ['datasets/hc.txt', 46, 46, 46, 45],
                 7: ['datasets/customer.txt', 10021, 277, 25, 4184],
                 8: ['datasets/americas_small.txt', 3477, 1587, 310, 2866],
                 9: ['datasets/americas_large.txt', 3485, 101127, 733, 2812],
                10: ['datasets/amazon1.txt', 9298, 7226, 36, 836],
                11: ['datasets/amazon1_b.txt', 9298, 7226, 36, 839],
                12: ['datasets/amazon1_test.txt', 11797, 4971, 46, 1989]
    }

    return datasets[h]


# return characteristics of the optimal solution [dataset name, #roles, min-rpu, max-rpu, min-ppr, max-ppr]
def get_data_opt(h=6):
    if h in (7, 10, 11, 12):
        print('WARNING: the optimal cover for this dataset is missing - using UPA\'s values')

    # dataset number [dataset name, #roles, min-rpu, max-rpu, min-ppr, max-ppr]
    datasets = { 1: ['datasets/fire1.txt', 64, 1, 9, 1, 395],
                 2: ['datasets/fire2.txt', 10, 1, 3, 2, 307],
                 3: ['datasets/domino.txt',20, 1, 9, 1, 201],
                 4: ['datasets/apj.txt',  453, 1, 8, 1,  52],
                 5: ['datasets/emea.txt',  34, 1, 1, 9, 554],
                 6: ['datasets/hc.txt',    14, 1, 6, 1,  32],
                 7: ['datasets/customer.txt', 0, 1, 25, 1, 25],     # not optimal solution
                 8: ['datasets/americas_small.txt', 178, 1, 12, 1, 263],
                 9: ['datasets/americas_large.txt', 398, 1,  4, 1, 733],
                10: ['datasets/amazon1.txt', 0, 1, 36, 1, 36],      # not optimal solution
                11: ['datasets/amazon1_b.txt', 0, 1, 36, 1, 36],    # not optimal solution
                12: ['datasets/amazon1_test.txt', 0, 1, 46, 1, 46]  # not optimal solution
                }

    return datasets[h]

# generate mpr/mru values to test heuristics PRUCC1 and PRUCC2, see the paper for details
def get_test_sets(h=6, n_mpr=5, n_pru=5, fix='mpr', u_l='opt'):
    #n_mpr number of values for the mpr parameter
    #n_pru number of values for the mru parameter

    dataset = get_data(h)
    # print(dataset)

    #[dataset name, #roles, min-rpu, max-rpu, min-ppr, max-ppr]
    dataset_opt = get_data_opt(h)
    # print(dataset_opt)

    to_test = dict()
    if u_l == 'opt':
        upper_limit = dataset_opt[5] if fix == 'mpr' else dataset_opt[3]
    else:
        upper_limit = dataset[3]

    upper_limit = upper_limit - 1
    if fix == 'mpr':
        fixed_constraint = n_mpr - 2
        derived_constraint = n_pru - 2
        opt_val = dataset_opt[5]
        der_ul_val = dataset_opt[3] - 1
    else:
        fixed_constraint   = n_pru - 2
        derived_constraint = n_mpr - 2
        opt_val = dataset_opt[3]
        der_ul_val = dataset_opt[5] - 1

    fixed_list = [2]
    if upper_limit > 2:
        for _ in range(fixed_constraint):
            v = fixed_list[-1] + upper_limit // (fixed_constraint + 1)
            if v not in fixed_list:
                fixed_list.append(v)
        if upper_limit not in fixed_list:
            fixed_list.append(upper_limit)

   # print(fixed_list, opt_val)

    for t in fixed_list:
        derived_list = [math.ceil(dataset[3] / t)]  # max#P/mpr or max#P/mru
        if t != 1:
            delta = (dataset[3] - derived_list[0]) // (derived_constraint + 1)
            limit = dataset[3] - 1
            for _ in range(derived_constraint):
                tmp_val = derived_list[-1] + delta
                if tmp_val not in derived_list:
                    derived_list.append(tmp_val)
            if limit not in derived_list:
                derived_list.append(limit)
        #print(t, derived_list)

        to_test[t] = derived_list

    return dataset[0], fixed_list, to_test


# another way to generate mpr/mru values to test PRUCC1 and PRUCC2
def compute_test_sets(h=6, n_mpr=3, n_pru=3, fix='mpr'):
    dataset = get_data(h)
    to_test = dict()

    fixed_constraint = n_mpr if fix == 'mpr' else n_pru
    derived_constraint = n_pru if fix == 'mpr' else n_mpr

    fixed_list = [1]
    for _ in range(fixed_constraint):
        fixed_list.append(fixed_list[-1] + dataset[3] // (fixed_constraint + 1))
    fixed_list.append(dataset[3])

    for t in fixed_list:
        derived_list = [math.ceil(dataset[3] / t)]
        if dataset[3] // t != dataset[3]:
            for _ in range(derived_constraint):
                tmp_val = derived_list[-1] + dataset[3] // (derived_constraint + 1)
                if tmp_val not in derived_list:
                    derived_list.append(tmp_val)
            derived_list.append(dataset[3])

        to_test[t] = derived_list

    return dataset[0], fixed_list, to_test


# return a sorted by value dictionary obtanied by the union
# of the (variable number) dictionaries received as input
def union(*dict_tuple):
    new_dict = dict()
    dn = 1
    for d in dict_tuple:
        for (k, v) in d.items():
            new_dict[k + '_e' + str(dn)] = v
        dn += 1
    return sorted(new_dict.items(), key=lambda x: x[1])


# return a dictionary of ranked heuristics-variants
# results is a dictionary where
#    key is a heuristic-variant
#    value is the  number of roles (or the wsc) obtained
#          by the given heuristic-variant
def rank(results):
    num_elem = len(results)
    pos1 = 0
    pos2 = 0
    r = 0
    to_return = list()
    new_dic = dict()
    while pos1 < num_elem:
        r += 1
        pos2 = pos1 + 1
        t_r = r
        while pos2 < num_elem and results[pos1][1] == results[pos2][1]:
            r += 1
            t_r += r
            pos2 += 1

        num_eq = pos2 - pos1

        for i in range(pos1, pos2):
            to_return.append((results[i][0], t_r / num_eq))
        pos1 = pos2

    for e in to_return:
        new_dic[e[0]] = e[1]
    return new_dic

