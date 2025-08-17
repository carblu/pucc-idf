from rm import Mining
import random
import math



class PUCC_IDF(Mining):
    def __init__(self, dataset, mpr=0, access_matrix='upa', minimum='len', selection='first'):
        super().__init__(dataset)
        self._mpr = len(self._permissions) if mpr == 0 else mpr

        # added for the minimum selection idf-based
        self._idf_matrix = self._pua if access_matrix == 'upa' else self._unc_pua

        # use the original UPA or the entries left uncovered in UPA
        assert access_matrix.lower() in ('upa', 'uncupa'), 'Access matrix not recognized'
        self._matrix = self._upa if access_matrix == 'upa' else self._unc_upa

        # self._flag = True if access_matrix == 'uncupa' else False

        self._compute_idf()

        # select a user considering the number or the sum of the idf values
        # of his/her assigned permissions in _matrix
        assert minimum in ('len', 'idf'), 'minimum selection not recognized'
        if minimum == 'len':
            self._minimum = lambda u: len(self._matrix[u])
            self._min = 'len'
        else:
            self._minimum = lambda u: sum([self._p_IDF[p] for p in self._matrix[u]])
            self._min = 'idf'

        # how to select the permissions
        assert selection in ('first', 'rnd', 'idf'), 'Permission selection criterion not valid'
        if selection == 'first':
            self._selection = self._first
        elif selection == 'rnd':
            self._selection = self._random
        elif selection == 'idf':
            self._selection = self._idf


    def _compute_idf(self):
        # a permission with a small idf value is assigned to more users
        # than a permission with a higher idf value
        # self._p_IDF = {p: -math.log(len(self._idf_matrix[p]) / len(self._idf_matrix), 2) for p in self._idf_matrix}
        self._p_IDF = {p: -math.log(len(self._idf_matrix[p]) / len(self._unc_users), 2) for p in self._idf_matrix}

	self._sumIDF = dict()
        for u in self._unc_users:
            self._sumIDF[u] = sum([self._p_IDF[p] for p in self._matrix[u]])


    def _first(self, prms):  # first mpr permissions
        return prms if len(prms) <= self._mpr else set(sorted(prms)[:self._mpr])

    def _random(self, prms):  # mpr random permissions
        return prms if len(prms) <= self._mpr else set(random.sample(sorted(prms), self._mpr))

    def _idf(self, prms):  # mpr permissions with minimum idf
        if len(prms) <= self._mpr:
            return prms
        else:
            inv_idf = collections.defaultdict(list)
            for p in prms:
                inv_idf[self._p_IDF[p]].append(p)

            tmp_prms = list()
            for idf in sorted(inv_idf):
                tmp_prms.extend(sorted(inv_idf[idf]))

            return set(tmp_prms[:self._mpr])

        return prms if len(prms) <= self._mpr else set(sorted(prms, key=lambda p: self._p_IDF[p])[:self._mpr])



    # A permission with a small idf value is assigned to more users
    # than a permission with a higher idf value. Sorting the permissions
    # in increasing order and considering the first mpr selects the ones
    # assigned to many users
    def _pick_role(self):
        u = min(self._unc_users, key=self._minimum)
        prms = self._selection(self._unc_upa[u])
        usrs = {u for u in self._unc_users if prms <= self._matrix[u]}
        return usrs, prms

    def mine(self):
        while self._unc_users:
            usrs, prms = self._pick_role()
            self._update_ua_pa(usrs, prms)
            self._update_unc(usrs, prms)
            if self._matrix is self._unc_upa:
                self._compute_idf()



class PUCC_R(PUCC_IDF):
    def __init__(self, dataset, mpr=0):
        super().__init__(dataset, mpr)

    def _pick_role(self):
        u = min(self._unc_users, key=lambda u: len(self._upa[u]))
        prms = self._first(self._unc_upa[u])
        # prms = self._first(min(self._unc_upa.items(), key=lambda t:len(self._upa[t[0]]) )[1])
        usrs = {u for u in self._unc_users if prms <= self._upa[u]}
        return usrs, prms


class PUCC_C(PUCC_IDF):
    def __init__(self, dataset, mpr=0):
        super().__init__(dataset, mpr)
        self._g = 0

    def _pick_roLLle(self):
        # p_m permission assigned to the minimum number of users. It must belong to the mined role
        p_m, usrs = min([(p, self._pua[p]) for p in self._unc_permissions], key=lambda t: len(t[1]))
        # select any permission assigned to all users in usrs
        all_prms = [p for p in self._unc_permissions if p != p_m and usrs <= self._pua[p]]
        prms = set(all_prms[:self._mpr - 1]).union({p_m})
        usrs = usrs.intersection(self._unc_users)

        return usrs, prms

    def _pick_role(self):  # V2
        # p_m permission assigned to the minimum number of users. It must belong to the mined role
        p_m, usrs = min([(p, self._unc_pua[p]) for p in self._unc_permissions], key=lambda t: len(t[1]))
        # select any permission assigned to all users in usrs
        all_prms = [p for p in self._unc_permissions if p != p_m and usrs <= self._pua[p]]
        prms = set(all_prms[:self._mpr - 1]).union({p_m})
        usrs = usrs.intersection(self._unc_users)

        return usrs, prms

    def _pick_roLLLle(self):  # V3
        # p_m permission assigned to the minimum number of users. It must belong to the mined role
        p_m, usrs = min([(p, self._unc_pua[p]) for p in self._unc_permissions], key=lambda t: len(t[1]))
        # select any permission assigned to all users in usrs
        all_prms = [p for p in self._pua if p != p_m and usrs <= self._pua[p]]
        prms = set(all_prms[:self._mpr - 1]).union({p_m})
        usrs = usrs.intersection(self._unc_users)

        return usrs, prms

