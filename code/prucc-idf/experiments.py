from library import *
from prucc import PRUCC_1, PRUCC_2
import time
import sys
import copy


# compare all twelve heuristics
def compare_prucc_idf_all(h=6, n_mpr=5, n_pru=5, fix='mpr', u_l='opt'):
    dataset_name, fixed_list, to_test = get_test_sets(h, n_mpr, n_pru, fix, u_l)
    print(dataset_name)
    print(to_test)

    for v1 in fixed_list:
        for v2 in to_test[v1]:
            if fix == 'mpr':
                mpr = v1
                mru = v2
            else:
                mpr = v2
                mru = v1
            print('mpr:', mpr, 'mru:', mru)
            min_type = 'len'
            for matrix in ('upa', 'uncupa'):
                for min_type in ('len', 'idf'):
                    for sel_type in ('first', 'rnd', 'idf'):
                    # for sel_type in ('first', 'rnd'):
                        name = matrix + '_' + min_type + '_' + sel_type
                        print('\t',name)
                        #     def __init__(self, dataset, mpr=0, mru=0, access_matrix='upa', selection='first', minimum='len', unique=False):
                        instance = PRUCC_1(dataset_name, mpr, mru, access_matrix=matrix, minimum=min_type, selection=sel_type)
                        instance.mine()
                        wsc, nroles, ua_size, pa_size = instance.get_wsc()
                        print(f'PRUCC1: {nroles:6d} {wsc:6d}', end=' ')
                        print('OK' if instance._check_solution() else 'NOT COVERED')

                        instance = PRUCC_2(dataset_name, mpr, mru, access_matrix=matrix, minimum=min_type, selection=sel_type)
                        instance.mine()
                        wsc, nroles, ua_size, pa_size = instance.get_wsc()
                        print(f'PRUCC2: {nroles:6d} {wsc:6d}', end=' ')
                        print('OK' if instance._check_solution() else 'NOT COVERED')

            print()


def print_table_prucc_TCJ(h=6, n_mpr=5, n_pru=5, fix='mpr', u_l='opt', out='s', runs=1):
    dataset_name, fixed_list, to_test = get_test_sets(h, n_mpr, n_pru, fix, u_l)

    min_val_r_1 = {'of': 0, 'or': 0, 'uf': 0, 'ur': 0}
    min_val_r_2 = {'of': 0, 'or': 0, 'uf': 0, 'ur': 0}
    min_val_w_1 = {'of': 0, 'or': 0, 'uf': 0, 'ur': 0}
    min_val_w_2 = {'of': 0, 'or': 0, 'uf': 0, 'ur': 0}
    min_r = {'<': 0, '=': 0, '>': 0}
    min_w = {'<': 0, '=': 0, '>': 0}

    labels = {
        'americas_large': 'Americas large',
        'americas_small': 'Americas small',
        'customer': 'Customer',
        'domino': 'Domino',
        'fire1': 'Firewall 1',
        'fire2': 'Firewall 2',
        'apj': 'Apj',
        'emea': 'Emea',
        'hc': 'Healthcare',
        'amazon1' : 'Amazon UPA 1',
        'amazon1_b': 'Amazon UPA 2',
        'amazon1_test' : 'Amazon UPA 3'
    }
    test_bed = [['of', 'upa', 'first'], ['or', 'upa', 'rnd'], ['uf', 'uncovered', 'first'],
                ['ur', 'uncovered', 'rnd']]

    ln = dataset_name.split('.')[0].split('/')[1]
    caption = labels[ln]
    if fix == 'mpr':
        f_c = '$mpr$'
        s_c = '$mru$'
    else:
        f_c = '$mru$'
        s_c = '$mpr$'
    # print('\\begin{landscape}')

    if out == 'f':  # output to a file
        stdout = sys.stdout
        sys.stdout = open('00_' + fix + '_' + ln + '.txt', 'w')

    # start table
    print('\\begin{table}[h]')
    print('\\centering')
    print('\\tiny{')
    print('\\begin{tabular}{ccc|rrrr|rrrr|}')
    print('\\cline{4-11}')
    # print('     & \multicolumn{1}{l}{}  & \multicolumn{1}{l|}{} & \multicolumn{4}{c|}{\eurA}   & \multicolumn{4}{c|}{\eurB} \\\ ')
    # print('\\cline{4-11}')
    print('& & & \multicolumn{4}{|c}{\multirow{2}{*}{\eurA}} & \multicolumn{4}{|c|}{\multirow{2}{*}{\eurB}} \\\ ')
    print('& & & \multicolumn{4}{|c}{} & \multicolumn{4}{|c|}{} \\\ \\cline{4-11}')

    print(f_c, ' & \multicolumn{1}{l}{', s_c,
          '}  & \multicolumn{1}{l|}{} & \multicolumn{1}{c|}{\eurof} & \multicolumn{1}{c|}{\euror}', end=' ')
    print(
        '& \multicolumn{1}{c|}{\euruf} & \multicolumn{1}{c|}{\eurur} & \multicolumn{1}{c|}{\eurof} & \multicolumn{1}{c|}{\euror} & \multicolumn{1}{c|}{\euruf} & \multicolumn{1}{c|}{\eurur} \\\ ')
    print('\\hline')

    all_results_nr = dict()
    all_results_wsc = dict()
    all_results_time = dict()
    all_ranks_nr = dict()
    all_ranks_wsc = dict()
    all_ranks_time = dict()

    nr1_min = {'of': [0, 0, 0, 0, 0], 'or': [0, 0, 0, 0, 0], 'uf': [0, 0, 0, 0, 0], 'ur': [0, 0, 0, 0, 0]}
    nr2_min = {'of': [0, 0, 0, 0, 0], 'or': [0, 0, 0, 0, 0], 'uf': [0, 0, 0, 0, 0], 'ur': [0, 0, 0, 0, 0]}
    wsc1_min = {'of': [0, 0, 0, 0, 0], 'or': [0, 0, 0, 0, 0], 'uf': [0, 0, 0, 0, 0], 'ur': [0, 0, 0, 0, 0]}
    wsc2_min = {'of': [0, 0, 0, 0, 0], 'or': [0, 0, 0, 0, 0], 'uf': [0, 0, 0, 0, 0], 'ur': [0, 0, 0, 0, 0]}

    for v1 in fixed_list:
        for v2 in to_test[v1]:
            if fix == 'mpr':
                mpr = v1
                mru = v2
            else:
                mpr = v2
                mru = v1

            # gen_pairs.add((mpr, mru))
            nr1 = {'of': 0, 'or': 0, 'uf': 0, 'ur': 0}
            wsc1 = {'of': 0, 'or': 0, 'uf': 0, 'ur': 0}
            time1 = {'of': 0, 'or': 0, 'uf': 0, 'ur': 0}
            nr2 = {'of': 0, 'or': 0, 'uf': 0, 'ur': 0}
            wsc2 = {'of': 0, 'or': 0, 'uf': 0, 'ur': 0}
            time2 = {'of': 0, 'or': 0, 'uf': 0, 'ur': 0}

            for test in test_bed:
                for _ in range(runs):
                    s1 = PRUCC_1(dataset_name, mpr, mru, access_matrix=test[1], minimum='', selection=test[2])

                    start = time.perf_counter()
                    s1.mine()
                    end = time.perf_counter()
                    nr1[test[0]] += s1.get_wsc()[1]
                    wsc1[test[0]] += s1.get_wsc()[0]
                    time1[test[0]] += round(end * 1000 - start * 1000)  # we get elapsed time in milliseconds
                    # s1._check_constraints()

                # print('>>>>>', nr1[test[0]], wsc1[test[0]], time1[test[0]])
                nr1[test[0]] = int(nr1[test[0]] // runs)
                wsc1[test[0]] = int(wsc1[test[0]] // runs)
                time1[test[0]] = int(time1[test[0]] // runs)

                for _ in range(runs):
                    s2 = PRUCC_2(dataset_name, mpr, mru, access_matrix=test[1], minimum='', selection=test[2])

                    start = time.perf_counter()
                    s2.mine()
                    end = time.perf_counter()
                    nr2[test[0]] += s2.get_wsc()[1]
                    wsc2[test[0]] += s2.get_wsc()[0]
                    time2[test[0]] += round(end * 1000 - start * 1000)  # we get elapsed time in milliseconds
                    # s2._check_constraints()

                nr2[test[0]] = int(nr2[test[0]] // runs)
                wsc2[test[0]] = int(wsc2[test[0]] // runs)
                time2[test[0]] = int(time2[test[0]] // runs)

            all_results_nr[(v1, v2)] = union(nr1, nr2)
            all_results_wsc[(v1, v2)] = union(wsc1, wsc2)
            all_results_time[(v1, v2)] = union(time1, time2)
            all_ranks_nr[(v1, v2)] = rank(all_results_nr[(v1, v2)])
            all_ranks_wsc[(v1, v2)] = rank(all_results_wsc[(v1, v2)])
            all_ranks_time[(v1, v2)] = rank(all_results_time[(v1, v2)])

            # compute min parameter of the four version
            min_r_1 = min(nr1.values())
            min_r_2 = min(nr2.values())
            min_w_1 = min(wsc1.values())
            min_w_2 = min(wsc2.values())

            cnt = 0
            l_m = []
            for (e, v) in nr1.items():
                if v == min_r_1:
                    min_val_r_1[e] = min_val_r_1[e] + 1
                    cnt += 1
                    l_m.append(e)
            # nr1_min[cnt] = nr1_min.get(cnt, 0) + 1
            for e in l_m: nr1_min[e][cnt] += 1

            cnt = 0
            l_m = []
            for (e, v) in nr2.items():
                if v == min_r_2:
                    min_val_r_2[e] = min_val_r_2[e] + 1
                    cnt += 1
                    l_m.append(e)
            # nr2_min[cnt] = nr2_min.get(cnt, 0) + 1
            for e in l_m: nr2_min[e][cnt] += 1

            cnt = 0
            l_m = []
            for (e, v) in wsc1.items():
                if v == min_w_1:
                    min_val_w_1[e] = min_val_w_1[e] + 1
                    cnt += 1
                    l_m.append(e)
            # wsc1_min[cnt] = wsc1_min.get(cnt, 0) + 1
            for e in l_m: wsc1_min[e][cnt] += 1

            cnt = 0
            l_m = []
            for (e, v) in wsc2.items():
                if v == min_w_2:
                    min_val_w_2[e] = min_val_w_2[e] + 1
                    cnt += 1
                    l_m.append(e)

            # wsc2_min[cnt] = wsc2_min.get(cnt, 0) + 1
            for e in l_m: wsc2_min[e][cnt] += 1

            if min_r_1 < min_r_2:
                min_r['<'] = min_r['<'] + 1
            elif min_r_1 == min_r_2:
                min_r['='] = min_r['='] + 1
            else:
                min_r['>'] = min_r['>'] + 1

            if min_w_1 < min_w_2:
                min_w['<'] = min_w['<'] + 1
            elif min_w_1 == min_w_2:
                min_w['='] = min_w['='] + 1
            else:
                min_w['>'] = min_w['>'] + 1

            # print table containing the results of the four heuristics
            print('\\multicolumn{1}{|c|}{\multirow{3}{*}{', v1, '}} & \multicolumn{1}{c|}{\multirow{3}{*}{', v2,
                  '}} & $|\\r|$ ')
            for val in nr1.values():
                print('& ', val, end=' ')
            for val in nr2.values():
                print('& ', val, end=' ')
            # print(' \\\ \cline{3-3}')
            print(' \\\ ')
            print('\\multicolumn{1}{|c|}{}                   & \multicolumn{1}{c|}{}                   & WSC ')
            for val in wsc1.values():
                print('& ', val, end=' ')
            for val in wsc2.values():
                print('& ', val, end=' ')
            # print(' \\\ \cline{3-3}')
            print(' \\\ ')
            print('\\multicolumn{1}{|c|}{}                   & \multicolumn{1}{c|}{}                   & time ')
            for val in time1.values():
                print('& ', val, end=' ')
            for val in time2.values():
                print('& ', val, end=' ')
            print(' \\\ \hline')
    print('\\end{tabular}')
    print('}')
    print('\\caption{Role-set size, WSC, and time value - Dataset ', caption, '}')
    print('\\label{label:', ln, '-all}', sep='')
    print('\\end{table}')
    # end table

    header = '''
\\begin{table}[h]
\centering
\\begin{tabular}{lccr}

\\begin{tabular}{lcccc|cccc|}
\cline{2-9}
   & \multicolumn{4}{|c|}{$|\\r|$}     & \multicolumn{4}{|c|}{WSC} \\\ \cline{2-9}
   & \multicolumn{1}{|c|}{\eurof} & \multicolumn{1}{c|}{\euror} & \multicolumn{1}{c|}{\euruf} & \multicolumn{1}{c|}{\eurur}
   & \multicolumn{1}{|c|}{\eurof} & \multicolumn{1}{c|}{\euror} & \multicolumn{1}{c|}{\euruf} & \multicolumn{1}{c|}{\eurur} \\\ \hline
   '''
    print(header)
    print('\multicolumn{1}{|c|}{\eurA}')
    for v in min_val_r_1.values():
        print('&', v, end=' ')
    for v in min_val_w_1.values():
        print('&', v, end=' ')
    print(' \\\ \hline')

    print('\multicolumn{1}{|c|}{\eurB}')
    for v in min_val_r_2.values():
        print('&', v, end=' ')
    for v in min_val_w_2.values():
        print('&', v, end=' ')
    print(' \\\ \hline')
    print('\end{tabular}')
    print('')
    print('& ~ & ~ &')
    print('')

    header = '''
\\begin{tabular}{l|c|c|}
\cline{2-3}
                             & $|\\r|$ & WSC \\\ \hline
    '''
    print(header)
    print('\multicolumn{1}{|l|}{better} &', min_r['<'], '&', min_w['<'], '\\\ \hline')
    print('\multicolumn{1}{|l|}{equal}  &', min_r['='], '&', min_w['='], '\\\ \hline')
    print('\multicolumn{1}{|l|}{worse}  &', min_r['>'], '&', min_w['>'], '\\\ \hline')
    print('\end{tabular}')
    print('')
    print('\end{tabular}')

    print('\\caption{Minumum values - Dataset ', caption, '}')
    print('\\label{', ln, ':min}', sep='')
    print('\end{table}')

    if out == 'f':  # output to a file
        sys.stdout = stdout
        print('DONE!')

    # end print_table_prucc_TCJ


def print_table_prucc_idf(h=6, n_mpr=5, n_pru=5, fix='mpr', u_l='#P', out='s', runs=1):
    dataset_name, fixed_list, to_test = get_test_sets(h, n_mpr, n_pru, fix, u_l)
    print(to_test)

    min_val_r_1 = {'olf': 0, 'olr': 0, 'oli': 0, 'oif': 0, 'oir': 0, 'oii': 0, 'ulf': 0, 'ulr': 0, 'uli': 0, 'uif': 0, 'uir': 0, 'uii': 0}
    min_val_r_2 = {'olf': 0, 'olr': 0, 'oli': 0, 'oif': 0, 'oir': 0, 'oii': 0, 'ulf': 0, 'ulr': 0, 'uli': 0, 'uif': 0, 'uir': 0, 'uii': 0}
    min_val_w_1 = {'olf': 0, 'olr': 0, 'oli': 0, 'oif': 0, 'oir': 0, 'oii': 0, 'ulf': 0, 'ulr': 0, 'uli': 0, 'uif': 0, 'uir': 0, 'uii': 0}
    min_val_w_2 = {'olf': 0, 'olr': 0, 'oli': 0, 'oif': 0, 'oir': 0, 'oii': 0, 'ulf': 0, 'ulr': 0, 'uli': 0, 'uif': 0, 'uir': 0, 'uii': 0}
    min_r = {'<': 0, '=': 0, '>': 0}
    min_w = {'<': 0, '=': 0, '>': 0}

    labels = {
        'americas_large': 'Americas large',
        'americas_small': 'Americas small',
        'customer': 'Customer',
        'domino': 'Domino',
        'fire1': 'Firewall 1',
        'fire2': 'Firewall 2',
        'apj': 'Apj',
        'emea': 'Emea',
        'hc': 'Healthcare'
    }

    test_bed = list()
    heuristics = list(min_val_r_1.keys())
    pos = 0
    for matrix in ('upa', 'uncupa'):
        for min_type in ('len', 'idf'):
            for sel_type in ('first', 'rnd', 'idf'):
                test_bed.append([heuristics[pos], matrix, min_type, sel_type])
                pos += 1
    print(test_bed)

    ln = dataset_name.split('.')[0].split('/')[1]
    caption = labels[ln]
    if fix == 'mpr':
        f_c = '$mpr$'
        s_c = '$mru$'
    else:
        f_c = '$mru$'
        s_c = '$mpr$'
    # print('\\begin{landscape}')


    if out == 'f':  # output to a file
        stdout = sys.stdout
        sys.stdout = open('00_' + fix + '_' + ln + '.txt', 'w')

    # start table
    print('\\begin{table}[h]')
    print('\\centering')
    print('\\tiny{')
    print('\\begin{tabular}{ccc|rrrrrrrrrrrr|rrrrrrrrrrrr|}')
    print('\\cline{4-27}')
    print('& & & \multicolumn{12}{|c}{\multirow{2}{*}{\eurA}} & \multicolumn{12}{|c|}{\multirow{2}{*}{\eurB}} \\\ ')
    print('& & & \multicolumn{12}{|c}{} & \multicolumn{12}{|c|}{} \\\ \\cline{4-27}')

    print(f_c, ' & \multicolumn{1}{l}{', s_c,'}  & \multicolumn{1}{l|}{} & ')
    for variant in min_val_r_1:
        print('\multicolumn{1}{c}{\\texttt{', variant.upper(), '}} &', end=' ')
    print()
    for variant in min_val_r_1:
        print('\multicolumn{1}{c}{\\texttt{', variant.upper(), '}} &', end=' ')
    print(' \\\ ')

    #print('\multicolumn{1}{c|}{\eurof} & \multicolumn{1}{c|}{\euror} & \multicolumn{1}{c|}{\euruf} & \multicolumn{1}{c|}{\eurur} &')
    # print('\multicolumn{1}{c|}{\eurof} & \multicolumn{1}{c|}{\euror} & \multicolumn{1}{c|}{\euruf} & \multicolumn{1}{c|}{\eurur} \\\ ')

    print('\\hline')

    all_results_nr = dict()
    all_results_wsc = dict()
    all_results_time = dict()
    all_ranks_nr = dict()
    all_ranks_wsc = dict()
    all_ranks_time = dict()

    template =  {'olf': [0, 0, 0, 0, 0], 'olr': [0, 0, 0, 0, 0], 'oli': [0, 0, 0, 0, 0],
                 'oif': [0, 0, 0, 0, 0], 'oir': [0, 0, 0, 0, 0], 'oii': [0, 0, 0, 0, 0],
                 'ulf': [0, 0, 0, 0, 0], 'ulr': [0, 0, 0, 0, 0], 'uli': [0, 0, 0, 0, 0],
                 'uif': [0, 0, 0, 0, 0], 'uir': 0, 'uii': [0, 0, 0, 0, 0]}

    template = dict()
    for h in heuristics:
        values = [0]
        for _ in range(len(heuristics)):
            values.append(0)
        template[h] = copy.deepcopy(values)

    nr1_min = copy.deepcopy(template) # {'of': [0, 0, 0, 0, 0], 'or': [0, 0, 0, 0, 0], 'uf': [0, 0, 0, 0, 0], 'ur': [0, 0, 0, 0, 0]}
    nr2_min = copy.deepcopy(template) # {'of': [0, 0, 0, 0, 0], 'or': [0, 0, 0, 0, 0], 'uf': [0, 0, 0, 0, 0], 'ur': [0, 0, 0, 0, 0]}
    wsc1_min = copy.deepcopy(template) # {'of': [0, 0, 0, 0, 0], 'or': [0, 0, 0, 0, 0], 'uf': [0, 0, 0, 0, 0], 'ur': [0, 0, 0, 0, 0]}
    wsc2_min = copy.deepcopy(template) # {'of': [0, 0, 0, 0, 0], 'or': [0, 0, 0, 0, 0], 'uf': [0, 0, 0, 0, 0], 'ur': [0, 0, 0, 0, 0]}

    for v1 in fixed_list:
        for v2 in to_test[v1]:
            if fix == 'mpr':
                mpr = v1
                mru = v2
            else:
                mpr = v2
                mru = v1

            # gen_pairs.add((mpr, mru))
            template2 = {'olf': 0, 'olr': 0, 'oli': 0, 'oif': 0, 'oir': 0, 'oii': 0,
                         'ulf': 0, 'ulr': 0, 'uli': 0, 'uif': 0, 'uir': 0, 'uii': 0}
            nr1 =   copy.deepcopy(template2) # {'of': 0, 'or': 0, 'uf': 0, 'ur': 0}
            wsc1 =  copy.deepcopy(template2) # {'of': 0, 'or': 0, 'uf': 0, 'ur': 0}
            time1 = copy.deepcopy(template2) # {'of': 0, 'or': 0, 'uf': 0, 'ur': 0}
            nr2 =   copy.deepcopy(template2) # {'of': 0, 'or': 0, 'uf': 0, 'ur': 0}
            wsc2 =  copy.deepcopy(template2) # {'of': 0, 'or': 0, 'uf': 0, 'ur': 0}
            time2 = copy.deepcopy(template2) # {'of': 0, 'or': 0, 'uf': 0, 'ur': 0}

            for test in test_bed:
                for _ in range(runs):
                    #s1 = PRUCC_1(dataset_name, mpr, mru, test[1], test[2])
                    s1 = PRUCC_1(dataset_name, mpr, mru, access_matrix=test[1], selection=test[3], minimum=test[2])

                    start = time.perf_counter()
                    s1.mine()
                    end = time.perf_counter()
                    nr1[test[0]] += s1.get_wsc()[1]
                    wsc1[test[0]] += s1.get_wsc()[0]
                    time1[test[0]] += round(end * 1000 - start * 1000)  # we get elapsed time in milliseconds
                    # s1._check_constraints()

                # print('>>>>>', nr1[test[0]], wsc1[test[0]], time1[test[0]])
                nr1[test[0]] = int(nr1[test[0]] // runs)
                wsc1[test[0]] = int(wsc1[test[0]] // runs)
                time1[test[0]] = int(time1[test[0]] // runs)

                for _ in range(runs):
                    s2 = PRUCC_2(dataset_name, mpr, mru, access_matrix=test[1], selection=test[3], minimum=test[2])
                    start = time.perf_counter()
                    s2.mine()
                    end = time.perf_counter()
                    nr2[test[0]] += s2.get_wsc()[1]
                    wsc2[test[0]] += s2.get_wsc()[0]
                    time2[test[0]] += round(end * 1000 - start * 1000)  # we get elapsed time in milliseconds
                    # s2._check_constraints()

                nr2[test[0]] = int(nr2[test[0]] // runs)
                wsc2[test[0]] = int(wsc2[test[0]] // runs)
                time2[test[0]] = int(time2[test[0]] // runs)

            all_results_nr[(v1, v2)] = union(nr1, nr2)
            all_results_wsc[(v1, v2)] = union(wsc1, wsc2)
            all_results_time[(v1, v2)] = union(time1, time2)
            all_ranks_nr[(v1, v2)] = rank(all_results_nr[(v1, v2)])
            all_ranks_wsc[(v1, v2)] = rank(all_results_wsc[(v1, v2)])
            all_ranks_time[(v1, v2)] = rank(all_results_time[(v1, v2)])

            # compute min parameter of the twelve versions
            min_r_1 = min(nr1.values())
            min_r_2 = min(nr2.values())
            min_w_1 = min(wsc1.values())
            min_w_2 = min(wsc2.values())

            cnt = 0
            l_m = []
            for (e, v) in nr1.items():
                if v == min_r_1:
                    min_val_r_1[e] = min_val_r_1[e] + 1
                    cnt += 1
                    l_m.append(e)
            # nr1_min[cnt] = nr1_min.get(cnt, 0) + 1
            for e in l_m: nr1_min[e][cnt] += 1

            cnt = 0
            l_m = []
            for (e, v) in nr2.items():
                if v == min_r_2:
                    min_val_r_2[e] = min_val_r_2[e] + 1
                    cnt += 1
                    l_m.append(e)
            # nr2_min[cnt] = nr2_min.get(cnt, 0) + 1
            for e in l_m: nr2_min[e][cnt] += 1

            cnt = 0
            l_m = []
            for (e, v) in wsc1.items():
                if v == min_w_1:
                    min_val_w_1[e] = min_val_w_1[e] + 1
                    cnt += 1
                    l_m.append(e)
            # wsc1_min[cnt] = wsc1_min.get(cnt, 0) + 1
            for e in l_m: wsc1_min[e][cnt] += 1

            cnt = 0
            l_m = []
            for (e, v) in wsc2.items():
                if v == min_w_2:
                    min_val_w_2[e] = min_val_w_2[e] + 1
                    cnt += 1
                    l_m.append(e)

            # wsc2_min[cnt] = wsc2_min.get(cnt, 0) + 1
            for e in l_m: wsc2_min[e][cnt] += 1

            if min_r_1 < min_r_2:
                min_r['<'] = min_r['<'] + 1
            elif min_r_1 == min_r_2:
                min_r['='] = min_r['='] + 1
            else:
                min_r['>'] = min_r['>'] + 1

            if min_w_1 < min_w_2:
                min_w['<'] = min_w['<'] + 1
            elif min_w_1 == min_w_2:
                min_w['='] = min_w['='] + 1
            else:
                min_w['>'] = min_w['>'] + 1

            # print table containing the results of the twelve versions
            print('\\multicolumn{1}{|c|}{\multirow{3}{*}{', v1, '}} & \multicolumn{1}{c|}{\multirow{3}{*}{', v2,
                  '}} & $|\\r|$ ')
            for val in nr1.values():
                print('& ', val, end=' ')
            for val in nr2.values():
                print('& ', val, end=' ')
            # print(' \\\ \cline{3-3}')
            print(' \\\ ')

            print('\\multicolumn{1}{|c|}{}                   & \multicolumn{1}{c|}{}                   & WSC ')
            for val in wsc1.values():
                print('& ', val, end=' ')
            for val in wsc2.values():
                print('& ', val, end=' ')
            # print(' \\\ \cline{3-3}')
            print(' \\\ ')
            print('\\multicolumn{1}{|c|}{}                   & \multicolumn{1}{c|}{}                   & time ')
            for val in time1.values():
                print('& ', val, end=' ')
            for val in time2.values():
                print('& ', val, end=' ')
            print(' \\\ \hline')
    print('\\end{tabular}')
    print('}')
    print('\\caption{Role-set size, WSC, and time value - Dataset ', caption, '}')
    print('\\label{label:', ln, '-all}', sep='')
    print('\\end{table}')
    # end table

    header = '''
\\begin{table}[h]
\centering
\\begin{tabular}{lccr}

\\begin{tabular}{lcccc|cccc|}
\cline{2-9}
   & \multicolumn{4}{|c|}{$|\\r|$}     & \multicolumn{4}{|c|}{WSC} \\\ \cline{2-9}
   & \multicolumn{1}{|c|}{\eurof} & \multicolumn{1}{c|}{\euror} & \multicolumn{1}{c|}{\euruf} & \multicolumn{1}{c|}{\eurur}
   & \multicolumn{1}{|c|}{\eurof} & \multicolumn{1}{c|}{\euror} & \multicolumn{1}{c|}{\euruf} & \multicolumn{1}{c|}{\eurur} \\\ \hline
   '''
    print(header)
    print('\multicolumn{1}{|c|}{\eurA}')
    for v in min_val_r_1.values():
        print('&', v, end=' ')
    for v in min_val_w_1.values():
        print('&', v, end=' ')
    print(' \\\ \hline')

    print('\multicolumn{1}{|c|}{\eurB}')
    for v in min_val_r_2.values():
        print('&', v, end=' ')
    for v in min_val_w_2.values():
        print('&', v, end=' ')
    print(' \\\ \hline')
    print('\end{tabular}')
    print('')
    print('& ~ & ~ &')
    print('')

    header = '''
\\begin{tabular}{l|c|c|}
\cline{2-3}
                             & $|\\r|$ & WSC \\\ \hline
    '''
    print(header)
    print('\multicolumn{1}{|l|}{better} &', min_r['<'], '&', min_w['<'], '\\\ \hline')
    print('\multicolumn{1}{|l|}{equal}  &', min_r['='], '&', min_w['='], '\\\ \hline')
    print('\multicolumn{1}{|l|}{worse}  &', min_r['>'], '&', min_w['>'], '\\\ \hline')
    print('\end{tabular}')
    print('')
    print('\end{tabular}')

    print('\\caption{Minumum values - Dataset ', caption, '}')
    print('\\label{', ln, ':min}', sep='')
    print('\end{table}')

    """
    print_table_minimum(fixed_list, to_test, nr1_min, nr2_min, ln + '_min__rn', caption)
    print_table_minimum(fixed_list, to_test, wsc1_min, wsc2_min, ln + '_min__wsc', caption)
    print_table_rank(compute_rank(all_ranks_nr), compute_rank(all_ranks_wsc), ln, caption)
    print_table_rank_single(compute_rank(all_ranks_nr), ln + '_rn', caption)
    print_table_rank_single(compute_rank(all_ranks_wsc), ln + '_wsc', caption)
    print_table_rank_single(compute_rank(all_ranks_time), ln + '_time', caption)
    """

    if out == 'f':  # output to a file
        sys.stdout = stdout
        print('DONE!')

    # end print_table_prucc


def print_single_table_prucc_idf(h=6, n_mpr=5, n_pru=5, fix='mpr', u_l='#P', out='s', runs=1, heuristic=1):
    dataset_name, fixed_list, to_test = get_test_sets(h, n_mpr, n_pru, fix, u_l)
    if out == 's':
        print(dataset_name)
        print(to_test)

    min_val_r_1 = {'olf': 0, 'olr': 0, 'oli': 0, 'oif': 0, 'oir': 0, 'oii': 0, 'ulf': 0, 'ulr': 0, 'uli': 0, 'uif': 0, 'uir': 0, 'uii': 0}
    min_val_r_2 = {'olf': 0, 'olr': 0, 'oli': 0, 'oif': 0, 'oir': 0, 'oii': 0, 'ulf': 0, 'ulr': 0, 'uli': 0, 'uif': 0, 'uir': 0, 'uii': 0}
    min_val_w_1 = {'olf': 0, 'olr': 0, 'oli': 0, 'oif': 0, 'oir': 0, 'oii': 0, 'ulf': 0, 'ulr': 0, 'uli': 0, 'uif': 0, 'uir': 0, 'uii': 0}
    min_val_w_2 = {'olf': 0, 'olr': 0, 'oli': 0, 'oif': 0, 'oir': 0, 'oii': 0, 'ulf': 0, 'ulr': 0, 'uli': 0, 'uif': 0, 'uir': 0, 'uii': 0}
    min_r = {'<': 0, '=': 0, '>': 0}
    min_w = {'<': 0, '=': 0, '>': 0}

    labels = {
        'americas_large': 'Americas large',
        'americas_small': 'Americas small',
        'customer': 'Customer',
        'domino': 'Domino',
        'fire1': 'Firewall 1',
        'fire2': 'Firewall 2',
        'apj': 'Apj',
        'emea': 'Emea',
        'hc': 'Healthcare',
        'amazon1' : 'Amazon UPA 1',
        'amazon1_b': 'Amazon UPA 2',
        'amazon1_test' : 'Amazon UPA 3'
    }

    test_bed = list()
    heuristics = list(min_val_r_1.keys())
    pos = 0
    for matrix in ('upa', 'uncupa'):
        for min_type in ('len', 'idf'):
            for sel_type in ('first', 'rnd', 'idf'):
                test_bed.append([heuristics[pos], matrix, min_type, sel_type])
                pos += 1
    # print(test_bed)

    ln = dataset_name.split('.')[0].split('/')[1]
    caption = labels[ln]
    if fix == 'mpr':
        f_c = '$mpr$'
        s_c = '$mru$'
    else:
        f_c = '$mru$'
        s_c = '$mpr$'
    # print('\\begin{landscape}')


    """
    if out == 'f':  # output to a file
        stdout = sys.stdout
        sys.stdout = open('00_' + fix + '_' + ln + '.txt', 'w')
    """

    if heuristic == 1:
        h_name = '\eurA'
        HEURISTIC_TYPE = PRUCC_1
    else:
        h_name = '\eurB'
        HEURISTIC_TYPE = PRUCC_2


    # start table
    print('\\begin{table}[h]')
    print('\\centering')
    print('\\tiny{')
    print('\\begin{tabular}{ccc|rrrrrrrrrrrr|}')
    print('\\cline{4-15}')
    print('& & & \multicolumn{12}{|c|}{\multirow{2}{*}{', h_name, '}} \\\ ')
    print('& & & \multicolumn{12}{|c|}{} \\\ \\cline{4-15}')

    print(f_c, ' & \multicolumn{1}{l}{', s_c,'}  & \multicolumn{1}{l|}{} & ')
    variants = list(min_val_r_1.keys())
    last = variants.pop()
    for variant in variants:
        if variant in ('olf', 'olr', 'ulf', 'ulr'):
            print('\\textcolor{blue}{', '\\texttt{', variant.upper(), '}} &', end=' ')
        else:
            print('\\texttt{', variant.upper(), '} &', end=' ')
    print('\multicolumn{1}{c|}{\\texttt{', last.upper(), '}} \\\ ')

    print('\\hline')

    all_results_nr = dict()
    all_results_wsc = dict()
    all_results_time = dict()
    all_ranks_nr = dict()
    all_ranks_wsc = dict()
    all_ranks_time = dict()

    template =  {'olf': [0, 0, 0, 0, 0], 'olr': [0, 0, 0, 0, 0], 'oli': [0, 0, 0, 0, 0],
                 'oif': [0, 0, 0, 0, 0], 'oir': [0, 0, 0, 0, 0], 'oii': [0, 0, 0, 0, 0],
                 'ulf': [0, 0, 0, 0, 0], 'ulr': [0, 0, 0, 0, 0], 'uli': [0, 0, 0, 0, 0],
                 'uif': [0, 0, 0, 0, 0], 'uir': 0, 'uii': [0, 0, 0, 0, 0]}

    template = dict()
    for h in heuristics:
        values = [0]
        for _ in range(len(heuristics)):
            values.append(0)
        template[h] = copy.deepcopy(values)

    nr1_min = copy.deepcopy(template) # {'of': [0, 0, 0, 0, 0], 'or': [0, 0, 0, 0, 0], 'uf': [0, 0, 0, 0, 0], 'ur': [0, 0, 0, 0, 0]}
    nr2_min = copy.deepcopy(template) # {'of': [0, 0, 0, 0, 0], 'or': [0, 0, 0, 0, 0], 'uf': [0, 0, 0, 0, 0], 'ur': [0, 0, 0, 0, 0]}
    wsc1_min = copy.deepcopy(template) # {'of': [0, 0, 0, 0, 0], 'or': [0, 0, 0, 0, 0], 'uf': [0, 0, 0, 0, 0], 'ur': [0, 0, 0, 0, 0]}
    wsc2_min = copy.deepcopy(template) # {'of': [0, 0, 0, 0, 0], 'or': [0, 0, 0, 0, 0], 'uf': [0, 0, 0, 0, 0], 'ur': [0, 0, 0, 0, 0]}


    for v1 in fixed_list:
        for v2 in to_test[v1]:
            if fix == 'mpr':
                mpr = v1
                mru = v2
            else:
                mpr = v2
                mru = v1

            # gen_pairs.add((mpr, mru))
            template2 = {'olf': 0, 'olr': 0, 'oli': 0, 'oif': 0, 'oir': 0, 'oii': 0,
                         'ulf': 0, 'ulr': 0, 'uli': 0, 'uif': 0, 'uir': 0, 'uii': 0}
            nr1 =   copy.deepcopy(template2) # {'of': 0, 'or': 0, 'uf': 0, 'ur': 0}
            wsc1 =  copy.deepcopy(template2) # {'of': 0, 'or': 0, 'uf': 0, 'ur': 0}
            time1 = copy.deepcopy(template2) # {'of': 0, 'or': 0, 'uf': 0, 'ur': 0}
            nr2 =   copy.deepcopy(template2) # {'of': 0, 'or': 0, 'uf': 0, 'ur': 0}
            wsc2 =  copy.deepcopy(template2) # {'of': 0, 'or': 0, 'uf': 0, 'ur': 0}
            time2 = copy.deepcopy(template2) # {'of': 0, 'or': 0, 'uf': 0, 'ur': 0}

            for test in test_bed:
                for _ in range(runs):
                    s1 = HEURISTIC_TYPE(dataset_name, mpr, mru, access_matrix=test[1], selection=test[3], minimum=test[2])

                    start = time.perf_counter()
                    s1.mine()
                    end = time.perf_counter()
                    nr1[test[0]] += s1.get_wsc()[1]
                    wsc1[test[0]] += s1.get_wsc()[0]
                    time1[test[0]] += round(end * 1000 - start * 1000)  # we get elapsed time in milliseconds
                    # s1._check_constraints()

                nr1[test[0]] = int(nr1[test[0]] // runs)
                wsc1[test[0]] = int(wsc1[test[0]] // runs)
                time1[test[0]] = int(time1[test[0]] // runs)


            # compute min parameter of the twelve versions
            min_r_1 = min(nr1.values())
            min_w_1 = min(wsc1.values())

            cnt = 0
            l_m = []
            for (e, v) in nr1.items():
                if v == min_r_1:
                    min_val_r_1[e] = min_val_r_1[e] + 1
                    cnt += 1
                    l_m.append(e)
            # nr1_min[cnt] = nr1_min.get(cnt, 0) + 1
            for e in l_m: nr1_min[e][cnt] += 1


            cnt = 0
            l_m = []
            for (e, v) in wsc1.items():
                if v == min_w_1:
                    min_val_w_1[e] = min_val_w_1[e] + 1
                    cnt += 1
                    l_m.append(e)
            # wsc1_min[cnt] = wsc1_min.get(cnt, 0) + 1
            for e in l_m: wsc1_min[e][cnt] += 1

            # print table containing the results of the twelve versions
            print('\\multicolumn{1}{|c|}{\multirow{3}{*}{', v1, '}} & \multicolumn{1}{c|}{\multirow{3}{*}{', v2,
                  '}} & $|\\r|$ ')
            min_val = min(nr1.values())
            for val in nr1.values():
                # print('& ', val, end=' ')
                if val == min_val:
                    print('& \\textcolor{red}{', val, '}', end=' ', sep='')
                else:
                    print('&', val, end=' ')
            print(' \\\ ')

            print('\\multicolumn{1}{|c|}{}                   & \multicolumn{1}{c|}{}                   & WSC ')
            min_val = min(wsc1.values())
            for val in wsc1.values():
                # print('& ', val, end=' ')
                if val == min_val:
                    print('& \\textcolor{red}{', val, '}', end=' ', sep='')
                else:
                    print('&', val, end=' ')
            print(' \\\ ')

            print('\\multicolumn{1}{|c|}{}                   & \multicolumn{1}{c|}{}                   & time ')
            min_val = min(time1.values())
            for val in time1.values():
                # print('& ', val, end=' ')
                if val == min_val:
                    print('& \\textcolor{red}{', val, '}', end=' ', sep='')
                else:
                    print('&', val, end=' ')
            print(' \\\ \hline')


    print('\\end{tabular}')
    print('}')
    print('\\caption{Role-set size, WSC value, and time spent -- Dataset ', caption, '}')
    print('\\label{label:', ln, '-all-', heuristic, '}', sep='')
    print('\\end{table}')
    # end table

    # table containing # of reached minimums
    print('\n')
    print('\\begin{table}[h]')
    print('\\centering')
    print('\\tiny{')

    print('\\begin{tabular}{lc cccc cccc cccc}')
    variants = list(min_val_r_1.keys())
    last = variants.pop()
    print(' & & ', end=' ')
    for variant in variants:
        if variant in ('olf', 'olr', 'ulf', 'ulr'):
            print('\\textcolor{blue}{', '\\texttt{', variant.upper(), '}} &', end=' ')
        else:
            print('\\texttt{', variant.upper(), '} &', end=' ')
    print('\multicolumn{1}{c}{\\texttt{', last.upper(), '}} \\\ ')

    print('\\hline')

    print('\multirow{2}{*}{', h_name, '}')
    print(' & $|\\r|$ ', end=' ')
    for v in min_val_r_1.values():
        print('&', v, end=' ')
    print(' \\\ ')

    print()
    print(' & WSC ', end=' ')
    for v in min_val_w_1.values():
        print('&', v, end=' ')
    print(' \\\ ')
    print('\\hline')

    print('\end{tabular}')
    print('}')  # end tiny
    print('\\caption{Number of times heuristic variants attain minumum $|\\r|$ and WSC - Dataset ', caption, '}')
    print('\\label{', ln, ':min_', heuristic, '}', sep='')
    print('\end{table}')

    # end print_table_prucc


def print_table_idf_both_heuristics(hb=6, n_mprb=5, n_prub=5, fixb='mpr', u_lb='#P', outb='s', runsb=1):
    if outb == 'f':  # output to a file
        ln = get_data(hb)[0].split('.')[0].split('/')[1]
        print('00_' + fixb + '_' + ln + '.txt')
        stdout = sys.stdout
        sys.stdout = open('00_' + fixb + '_' + ln + '.txt', 'w')

    print_single_table_prucc_idf(h=hb, n_mpr=n_mprb, n_pru=n_prub, fix=fixb, u_l=u_lb, out=outb, runs=runsb, heuristic=1)
    print('\n')
    print_single_table_prucc_idf(h=hb, n_mpr=n_mprb, n_pru=n_prub, fix=fixb, u_l=u_lb, out=outb, runs=runsb, heuristic=2)

    if outb == 'f':  # output to a file
        sys.stdout = stdout
        print('DONE!')



if __name__ == '__main__':
    pass
    start = time.perf_counter()

    # print_table_prucc_TCJ()

    # compare_prucc_idf_all()

    # print_table_prucc_idf()

    # print_single_table_prucc_idf(heuristic=1)

    print_table_idf_both_heuristics(hb=6, outb='s', runsb=1)
    end = time.perf_counter()
    print(end-start)
