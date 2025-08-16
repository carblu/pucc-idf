from erupdc_IDF import ERUPDC
import time

def get_dataset(h=6):
    datasets = {1: 'datasets/fire1.txt', 2: 'datasets/fire2.txt', 3: 'datasets/domino.txt', 4: 'datasets/apj.txt',
                5: 'datasets/emea.txt', 6: 'datasets/hc.txt', 7: 'datasets/customer.txt',
                8: 'datasets/americas_small.txt', 9: 'datasets/americas_large.txt', 10: 'datasets/amazon1.txt'}
    dataset = datasets[h]

    if (h == 1):
        # dataset = 'datasets/fire1.txt'
        set_mrcu = [617, 21, 16, 12, 8, 1]
        set_mrcp = [251, 26, 25, 21, 17, 13, 9, 1]

    if (h == 2):
        # dataset = 'datasets/fire2.txt'
        #set_mrcu =     [9, 8, 7, 6, 3, 1]
        set_mrcu = [590, 9, 8, 7, 6, 1]
        set_mrcp = [298, 3, 2, 1]

    if (h == 3):
        # dataset = 'datasets/domino.txt'
        #set_mrcu = [209, 11, 9, 7, 6, 3, 1]
        set_mrcu = [209, 11, 9, 7, 6, 1]
        set_mrcp = [52, 8, 7, 6, 5, 4, 1]
        #set_mrcu = [11, 9, 7, 6]
        #set_mrcp = [8, 7, 6, 5, 4]

    if (h == 4):
        # dataset = 'datasets/apj.txt'
        set_mrcu = [58, 11, 10, 8, 6, 1]
        set_mrcp = [291, 67, 65, 55, 45, 35, 25, 15, 5, 1]

    if (h == 5):
        # dataset = 'datasets/emea.txt'
        set_mrcu = [554, 200, 4, 3, 2, 1]
        set_mrcp = [32, 26, 21, 16, 11, 6, 1]

    if (h == 6):
        # dataset = 'datasets/hc.txt'
        set_mrcu = [7, 6, 5, 4]
        set_mrcp = [9, 8, 7, 6, 5, 4]

    if (h == 7):
        # dataset = 'datasets/customer.txt'
        set_mrcu = [25, 20, 16, 13, 7, 1]
        set_mrcp = [4184, 510, 225, 111, 80, 60, 40, 1]

    if (h == 8):
        # dataset = 'datasets/americas_small.txt'
        set_mrcu = [310, 22, 16, 12, 8, 1]
        set_mrcp = [2866, 75, 70, 60, 50, 40, 30, 20, 1]

    if (h == 9):
        # dataset = 'datasets/americas_large.txt'
        set_mrcu = [733, 6, 5, 4, 3, 1]
        set_mrcp = [2812, 144, 140, 130, 120, 110, 100, 1]

    if (h == 10):
        # dataset = 'datasets/amazon1.txt'
        set_mrcu = [36, 6, 5, 4, 3, 1]
        set_mrcp = [836, 400, 300, 200, 100, 50, 20, 1]

    return dataset, set_mrcu, set_mrcp


def compare_rupd(h=6):
    dataset, set_mrcu, set_mrcp = get_dataset(h)
    print(dataset)
    for mrcp in set_mrcp:
        for mrcu in set_mrcu:
            print('\nmrcp:', mrcp, 'mrcu:', mrcu)
            print('        NR    WSC    DUPA')
            for variant in ('nu', 'np', 'xr', 'nr', 'fiu', 'fip', 'diu', 'dip'):
                instance = ERUPDC(dataset, mrcu, mrcp, heuristic=variant)
                instance.mine()
                wsc, nroles, ua_size, pa_size = instance.get_wsc()
                dupa = instance.get_dupa()
                print('{:3s} {:6d} {:6d} {:6d}'.format(variant, nroles, wsc + dupa, dupa))



def print_latex_table(to_test = 6):
    dataset, set_mrcu, set_mrcp = get_dataset(to_test)
    print(dataset)
    their_heuristics = ['nu', 'np', 'xr', 'nr', 'fiu', 'fip', 'diu', 'dip']

    #their_heuristics = ['nu', 'np', 'xr', 'nr', 'fu', 'bu', 'fp', 'bp']
    #their_heuristics = ['nu', 'np', 'xr', 'nr', 'iu', 'ip']
    # our_heuristics = {'RUPD  ':RUPD, 'RUPD_M':RUPD_M, 'RUPD_U':RUPD_U, 'RUPD_P':RUPD_P}

    print("""
\\begin{table}[!h]
\\centering
\\small{
""")
    print('\\begin{tabular}{cc ', 'r'*len(their_heuristics), '}', sep='')
    print('$(mrcp, mrcu)$ & Measure  &', end = ' ' )
    for i, h in enumerate(their_heuristics):
        if i < len(their_heuristics) - 1:
            print('\\texttt{', h.upper(), '} &', sep='', end=' ')
        else:
            print('\\texttt{', h.upper(), '} ', sep='', end=' ')

    print('\\\ \\toprule')

    for mrcp in set_mrcp:
        for mrcu in set_mrcu:
            #print((mrcp,mrcu), '', end='')
            all_values_nr = list()
            all_values_ua = list()
            all_values_pa = list()
            all_values_dupa = list()
            all_values_time = list()
            r = ''
            uav = ''
            pav = ''
            #w = ''
            d = ''
            t = ''
            for h in their_heuristics:
                instance = ERUPDC(dataset, mrcu, mrcp, h)
                start = time.process_time()
                instance.mine()
                end = time.process_time()
                et = round((end - start)*1000)
                wsc, nroles, ua_size, pa_size = instance.get_wsc()
                dupa = instance.get_dupa()

                # store results
                all_values_nr.append(nroles)
                all_values_ua.append(ua_size)
                all_values_pa.append(pa_size)
                all_values_dupa.append(dupa)
                all_values_time.append(et)

                r = r + '& ' + str(nroles)
                uav = uav + '& ' + str(ua_size)
                pav = pav + '& ' + str(pa_size)
                d = d + '& ' + str(dupa)
                #w = w + '& ' + str(wsc)
                t = t + '& ' + str(et)

            best_value_nr = min(all_values_nr)
            best_value_ua = min(all_values_ua)
            best_value_pa = min(all_values_pa)
            best_value_dupa = min(all_values_dupa)
            best_value_time = min(all_values_time)

            # print role-set size
            print('\multirow{4}{*}{', (mrcp,mrcu),    '} & $|\\rRM|$',  end=' ')
            for i in range(len(their_heuristics)):
                if all_values_nr[i] == best_value_nr:
                    print('& \\textcolor{red}{', all_values_nr[i], '}', sep='', end=' ')
                else:
                    print('&', all_values_nr[i], end=' ')
            print('\\\ ')

            # print UA size
            print('                           & $|\\ur|$', end=' ')
            for i in range(len(their_heuristics)):
                if all_values_ua[i] == best_value_ua:
                    print('& \\textcolor{red}{', all_values_ua[i], '}', sep='', end=' ')
                else:
                    print('&', all_values_ua[i], end=' ')
            print('\\\ ')

            # print PA size
            print('                           & $|\\rp|$', end=' ')
            for i in range(len(their_heuristics)):
                if all_values_pa[i] == best_value_pa:
                    print('& \\textcolor{red}{', all_values_pa[i], '}', sep='', end=' ')
                else:
                    print('&', all_values_pa[i], end=' ')
            print('\\\ ')

            print('                           & $|\dup|$', end=' ')
            for i in range(len(their_heuristics)):
                if all_values_dupa[i] == best_value_dupa:
                    print('& \\textcolor{red}{', all_values_dupa[i], '}', sep='', end=' ')
                else:
                    print('&', all_values_dupa[i], end=' ')
            print('\\\ \midrule')


            #print('\multirow{4}{*}{', (mrcp,mrcu),    '} & $|\\rRM|$',    r, ' \\\ ')
            #print('                           & $|\\ur|$',  uav, ' \\\ ')
            #print('                           & $|\\rp|$',  pav, ' \\\ ')
            #print('                           & $|\dup|$', d, ' \\\ \midrule')
            #print('                           & time', t, ' \\\ \hline')



    print("""
\end{tabular}
}
\end{table}
    """)

    return True


'''
            1: firewall 1       6: healthcare
            2: firewall 2       7: customer
            3: domino           8: americas small
            4: apj              9: americas large
            5: emea            10: amazon UPA 1

'''

if __name__ == '__main__':
    to_test = 6
    # compare_rupd(to_test)
    print_latex_table(to_test)
