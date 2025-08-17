from pucc_idf import PUCC_IDF, PUCC_R, PUCC_C
from crm import CRM

# dataset number [dataset name, #roles, min-rpu, max-rpu, min-ppr, max-ppr]
datasets = (['datasets/americas_large.txt', 398, 1, 4, 1, 733],
            ['datasets/americas_small.txt', 178, 1, 12, 1, 310],
            ['datasets/apj.txt', 453, 1, 8, 1, 58],
            ['datasets/customer.txt', 0, 1, 25, 1, 25],  # not optimal solution
            ['datasets/domino.txt', 20, 1, 9, 1, 209],
            ['datasets/emea.txt', 34, 1, 1, 9, 554],
            ['datasets/fire1.txt', 64, 1, 9, 1, 617],
            ['datasets/fire2.txt', 10, 1, 3, 2, 590],
            ['datasets/hc.txt', 14, 1, 6, 1, 45],
            ['datasets/amazon1.txt', 0, 1, 36, 1, 36],
            ['datasets/amazon1_b.txt', 0, 1, 36, 1, 36],
            ['datasets/amazon1_test.txt', 0, 1, 46, 1, 46]  # min-rpu, max-rpu same as min#P, max#P -- min-ppr, max-ppr same as min#P, max#
            )

# dataset number [dataset name, #users, #permissions, max#perm-per-user, max#users-have-perm]
datasets_2 = (['datasets/americas_large.txt', 3485, 101127, 733, 2812],
              ['datasets/americas_small.txt', 3477, 1587, 310, 2866],
              ['datasets/apj.txt', 2044, 1164, 58, 291],
              ['datasets/customer.txt', 10021, 277, 25, 4184],
              ['datasets/domino.txt', 79, 231, 209, 52],
              ['datasets/emea.txt', 35, 3046, 554, 32],
              ['datasets/fire1.txt', 365, 709, 617, 251],
              ['datasets/fire2.txt', 325, 590, 590, 298],
              ['datasets/hc.txt', 46, 46, 46, 45]
              )


dn = dict()
dn['customer'] = 'Customer'
dn['americas_large'] = 'Americas large'
dn['americas_small'] = 'Americas small'
dn['apj'] = 'Apj'
dn['fire1'] = 'Firewall 1'
dn['fire2'] = 'Firewall 2'
dn['emea'] = 'Emea'
dn['domino'] = 'Domino'
dn['hc'] = 'Healthcare'
dn['amazon1'] = 'Amazon 1'
dn['amazon2'] = 'Amazon 2'
dn['amazon1_b'] = 'Amazon 1 both access'
dn['synt_6k_24k'] = 'Synthetic 6k users 24k permissions -- both access'
dn['synt_5k_4k'] = 'Synthetic 5k users 4k permissions -- granted access and operation o4'
dn['amazon1_test'] = 'UPA from Amazon test.csv'


def test_single(dsn, all_heuristics=False):
    for dataset in datasets:
        if dsn not in dataset[0]:
            continue
        max_ppr = dataset[-1]
        # for mpr in (int(max_ppr * p) for p in (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1)):
        for mpr in (int(max_ppr * p) for p in (0.2, 0.5, 1)):
            print('\t', mpr, dataset[0])
            test_all(dataset[0], mpr, all_heuristics)


def test_all(dataset, mpr, all_heuristics=True, solution=False):
    print('\t', mpr, dataset)
    if all_heuristics:
        sol = PUCC_R(dataset, mpr)
        sol.mine()
        wsc, nr, ua_size, pa_size = sol.get_wsc()
        print('        PUCC_R     ', f'{wsc:>5} {nr:>5} {ua_size:>5} {pa_size:>5}', sol.check_solution())
        if solution: print('ua:', sol._ua, '\n', 'pa', sol._pa)

        sol = PUCC_C(dataset, mpr)
        sol.mine()
        wsc, nr, ua_size, pa_size = sol.get_wsc()
        print('        PUCC_C     ', f'{wsc:>5} {nr:>5} {ua_size:>5} {pa_size:>5}', sol.check_solution())
        if solution: print('ua:', sol._ua, '\n', 'pa', sol._pa)

        sol = CRM(dataset, mpr)
        sol.mine()
        wsc, nr, ua_size, pa_size = sol.get_wsc()
        print('           CRM     ', f'{wsc:>5} {nr:>5} {ua_size:>5} {pa_size:>5}', sol.check_solution())
        if solution: print('ua:', sol._ua, '\n', 'pa', sol._pa)

    for matrix in ('upa', 'uncupa'):
        for minimum in ('len', 'idf'):
            for selection in ('first', 'rnd', 'idf'):
                # print(matrix, selection, dataset, mpr)
                sol = PUCC_IDF(dataset, mpr, matrix, minimum, selection)
                sol.mine()
                # print('Solution:', sol.check_solution())
                wsc, nr, ua_size, pa_size = sol.get_wsc()
                print(f'{matrix:>8}_{minimum}_{selection:6} {wsc:>5} {nr:>5} {ua_size:>5} {pa_size:>5}', sol.check_solution())
                if solution: print('ua:', sol._ua, '\n', 'pa', sol._pa)


def test_all_datasets(all_heuristics=True):
    for dataset in datasets:
        max_ppr = dataset[-1]
        # for mpr in (int(max_ppr * p) for p in (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1)):
        for mpr in (int(max_ppr * p) for p in (0.25, 0.50, 0.75, 1)):
            print('\t', mpr, dataset[0])
            test_all(dataset[0], mpr, all_heuristics)


def test_all_datasets_unconstrained():
    for dataset in datasets_2:
        mpr = dataset[-2]
        test_all(dataset[0], mpr)



if __name__ == '__main__':
    # experiments on all datasets, output on screen
    # test_all_datasets(all_heuristics=False)

    # experiments on a single dataset
    test_single('fire')

    # experiments on all datasets, output on screen, unconstrained scenario
    # test_all_datasets_unconstrained()




