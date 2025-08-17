import random
from copy import deepcopy
import collections
import math

class Mining:
    def __init__(self, dataset, unique = False):
        self._dataset = dataset
        self._users = set()
        self._permissions = set()
        self._upa = {}  # dictionary (user, set of permissions)
        self._upa_unique = {}  # dictionary (user, set of permissions) only users with distinct set of permissions
        self._pua = {}  # dictionary (permission, set of users)
        self._ua = {}   # dictionary (user, set of roles)
        self._pa = {}   # dictionary (role, set of permissions)
        self._k = 0     # mined roles so far
        self._n = 0     # total number of granted access to resources (i.e., number of pairs in dataset)
        self._load_upa()
        if unique:  #remove dupliceted users
            self._unique_users()
        self._unc_upa = deepcopy(self._upa)
        self._unc_pua = deepcopy(self._pua)
        self._unc_users = deepcopy(self._users)
        self._unc_permissions = deepcopy(self._permissions)

    # initialize UPA matrix according to the dataset 'self._dataset'
    def _load_upa(self):
        with open(self._dataset) as f:
            for u_p in f:
                (user, permission) = u_p.split()
                user = int(user.strip())
                permission = int(permission.strip())

                if user in self._users:
                    if permission not in self._upa[user]:
                        self._upa[user].add(permission)
                        self._n = self._n + 1
                else:
                    self._users.add(user)
                    self._upa[user] = {permission}
                    self._n = self._n + 1

                if permission in self._permissions:
                    self._pua[permission].add(user)
                else:
                    self._permissions.add(permission)
                    self._pua[permission] = {user}
            f.closed

    # remove dupliceted users
    def _unique_users(self):
        self._users_bk = deepcopy(self._users)  # users backup
        self._upa_bk = deepcopy(self._upa)      # upa backup
        self._users_map = dict()                #key = user, value=list of users with identical permissions
        equal_prms = dict()
        for u in self._users:
            equal_prms[u] = u
        self._upa = dict()

        for u_i in sorted(self._upa_bk.keys()):
            for u_j in sorted(self._upa_bk.keys()):
                if u_j > u_i and equal_prms[u_j] == u_j and self._upa_bk[u_j] == self._upa_bk[u_i]:
                    equal_prms[u_j] = u_i #u_j's permissions are identical to u_i's ones


        for k, v in equal_prms.items():
            if v not in self._users_map:
                self._users_map[v] = [k]
            else:
             self._users_map[v].append(k)

        # reduced user-permission association
        for u in self._users_map:
            self._upa[u] = deepcopy(self._upa_bk[u])

        self._users = set(self._users_map.keys())

    # used by the mining algorithms, update ua and pa matrices assinging permissions 'prms' to users 'usrs'
    def _update_ua_pa(self, usrs, prms):
        idx_f = 0
        found = False
        for (idx, r) in self._pa.items():
            if r == prms:
                idx_f = idx
                found = True
                break

        if found == False:
            self._k = self._k + 1
            self._pa[self._k] = prms
            idx_f = self._k

        for u in usrs:
            if u in self._ua:
                self._ua[u].add(idx_f)
            else:
                self._ua[u] = {idx_f}

    # after a role has been assigned, look for users and permissions not coverd yet
    def _update_unc(self, usrs, prms):
        for u in usrs:
            self._unc_upa[u] = self._unc_upa[u] - prms
            if len(self._unc_upa[u]) == 0:
                self._unc_users.remove(u)
        for p in prms:
            self._unc_pua[p] = self._unc_pua[p] - usrs
            if len(self._unc_pua[p]) == 0 and p in self._unc_permissions:
                self._unc_permissions.remove(p)


    def _clear(self):  #try to remove redundant role and to lower wsc
        contains = {} # dictionary (role, set of roles contained in role)
        roles = list(self._pa.items())
        for i in range(0, len(roles) - 1):   #for each role compute all roles it contains
            ri = roles[i]
            for j in range(i + 1, len(roles)):
                rj = roles[j]
                if len(ri[1]) < len(rj[1]) and ri[1].issubset(rj[1]):
                    if rj[0] in contains:
                        contains[rj[0]].add(ri[0])
                    else:
                        contains[rj[0]] = {ri[0]}
                if len(rj[1]) < len(ri[1]) and rj[1].issubset(ri[1]):
                    if ri[0] in contains:
                        contains[ri[0]].add(rj[0])
                    else:
                        contains[ri[0]] = {rj[0]}
        f1 = False
        for u in self._users:
            for r in self._ua[u]:
                if r in contains:
                    intersection = self._ua[u].intersection(contains[r])
                    if intersection:    #some roles contained in r also are assigned to u
                        f1 = True #reduced wsc
                    self._ua[u] = self._ua[u].difference(intersection)   #remove contained roles, wsc is lowered

        id_roles = set(self._pa.keys())
        assigned_roles = set()
        f2 = False
        for u in self._users:
            assigned_roles.update(self._ua[u])
        if len(id_roles) != len(assigned_roles):   #one or more roles are not needed (they are not assigned to any user)
            f2 = True  #reduced number of roles
            to_delete = id_roles.difference(assigned_roles)
            #print('There exist unassigned roles', to_delete, end='')
            #print()
            for r in to_delete:
                del self._pa[r]

        return f1, f2


    def _reduction__no_print(self):
        self._copy_pa = deepcopy(self._pa)
        self._copy_ua = deepcopy(self._ua)

        roles = set(self._pa.keys())
        assigned_roles = set()
        for u in self._users:
            assigned_roles.update(self._ua[u])

        if len(roles) != len(assigned_roles):
            print('There exist unassigned roles', end='')


        contains = {} # dictionary (role, set of roles contained in role)
        roles = list(self._copy_pa.items())
        for i in range(0, len(roles) - 1):
            ri = roles[i]
            for j in range(i + 1, len(roles)):
                rj = roles[j]
                if len(ri[1]) < len(rj[1]) and ri[1].issubset(rj[1]):
                    if rj[0] in contains:
                        contains[rj[0]].add(ri[0])
                    else:
                        contains[rj[0]] = {ri[0]}
                if len(rj[1]) < len(ri[1]) and rj[1].issubset(ri[1]):
                    if ri[0] in contains:
                        contains[ri[0]].add(rj[0])
                    else:
                        contains[ri[0]] = {rj[0]}

        for u in self._users:
            for r in self._copy_ua[u]:
                if r in contains:
                    intersection = self._copy_ua[u].intersection(contains[r])
                    self._copy_ua[u] = self._copy_ua[u].difference(intersection)

        for u in self._users:
            if len(self._copy_ua[u]) != len(self._ua[u]):
                print(' WSC reduced!' ,end='')
                break

        roles = set(self._copy_pa.keys())
        assigned_roles = set()
        for u in self._users:
            assigned_roles.update(self._copy_ua[u])

        if len(roles) != len(assigned_roles):
            print(' - #roles reduced')
        else:
            print('')

    # return weighed structural complexity of the mined roles and |Roles|, |UA|, and |PA|
    def get_wsc(self):
        nroles = len(self._pa.keys())
        ua_size = 0
        for roles in self._ua.values():
            ua_size += len(roles)
        pa_size = 0
        for prms in self._pa.values():
            pa_size += len(prms)
        return nroles + ua_size + pa_size, nroles, ua_size, pa_size

    # chech whether ua and pa cover upa
    def _check_solution(self):
        for u in self._users:
            if u not in self._ua.keys():
                return False
            perms = set()
            for r in self._ua[u]:
                perms.update(self._pa[r])
            if perms != self._upa[u]:
                return False
        return True

    def print_roles(self):
        sr = sorted(self._pa.items(), key = lambda role : len(role[1]))
        for r in sr:
            print(r)



class PRUCC(Mining):
    def __init__(self, dataset, mpr=0, mru=0, access_matrix ='upa', minimum='len', selection='first', unique=False):
        # dataset = real-world dataset's filename
        # mpr = maximum # of permissions per role, mru = maximum roles per user
        # mpr/mru = 0 => no mpr/mru constraint
        # access_matrix = 'upa' => use original user-permission association matrix
        # access_matrix != 'upa' => use the matrix of the original UPA's entries left uncovered
        # criterion = 'first' => select the first mpr permissions from the picked UPA's row
        # criterion != 'first' => select mpr random permissions from the picked UPA's row
        # unique = True => remove from upa duplicated usesr

        super().__init__(dataset, unique)
        self._mpr = len(self._permissions) if mpr == 0 else mpr
        self._mru = len(self._permissions) if mru == 0 else mru
        if self._incompatible():
            exit('ERROR: UPA is incompatible with constraints t1: {0} t2: {1}'.format(self._mpr, self._mru))

        # use the original UPA or the entries left uncovered in UPA
        self._matrix = self._upa if access_matrix == 'upa' else self._unc_upa
        self.access_matrix = access_matrix

        self._minUser = 'idf' if minimum == 'idf' else 'len'  # user selection strategy

        if minimum == 'idf' or selection == 'idf':
            self._idf_matrix = self._pua if access_matrix == 'upa' else self._unc_pua
            self._compute_idf()

        # permissions selection strategy
        self.selection = selection
        if selection == 'first':
            self._selection = self._first
        elif selection == 'rnd':
            self._selection = self._random
        elif selection == 'idf':
            self._selection = self._idf
        else:  # unknown strategy
            raise Exception(f'ERROR: Unknown strategy --> {selection}')


    def _update_unc(self, usrs, prms):
        for u in usrs:
            self._unc_upa[u] = self._unc_upa[u] - prms
            if len(self._unc_upa[u]) == 0:
                self._unc_users.remove(u)
                if self._minUser == 'idf' or self._selection is self._idf:
                    del self._unc_upa[u]  # aggiunto


        for p in prms:
            if p in self._unc_pua:
                self._unc_pua[p] = self._unc_pua[p] - usrs
                if len(self._unc_pua[p]) == 0 and p in self._unc_permissions:
                    self._unc_permissions.remove(p)
                    if self._minUser == 'idf' or self._selection is self._idf:
                        del self._unc_pua[p] # aggiunto



    def _compute_idf_OLD(self):
        # a permission with a small idf value is assigned to more users
        # than a permission with a higher idf value
        self._p_IDF = {p: -math.log(len(self._idf_matrix[p]) / len(self._unc_users), 2) for p in self._idf_matrix}

    def _compute_idf(self):  # IDF values computed up to fourth decimal digit
        self._p_IDF = dict()
        # a permission with a small idf value is assigned to more users than a permission with a higher idf value
        #self._p_IDF = {p: round(-math.log(len(self._unc_pua[p]) / len(self._unc_users), 2), 4) for p in self._unc_pua}
        #"""
        for p in self._unc_pua:
            try:
                self._p_IDF[p] = round(-math.log(len(self._unc_pua[p]) / len(self._unc_users), 2), 4)
            except:
                print('len(self._unc_pua[p])', len(self._unc_pua[p]))
        #"""
        self._sumIDF = dict()
        for u in self._unc_users:
            self._sumIDF[u] = sum([self._p_IDF[p] for p in self._unc_upa[u]])


    def _first(self, prms):
        return prms if len(prms) <= self._mpr else set(sorted(list(prms))[0:self._mpr])

    def _random(self, prms):
        return prms if len(prms) <= self._mpr else set(random.sample(sorted(prms), self._mpr))

    # aggiunto
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

            # smallest_mpr = set()
            # smallest = sorted(prms, key=lambda p: self._p_IDF[p])
            # return smallest_mpr


        return prms if len(prms) <= self._mpr else set(sorted(prms, key=lambda p: self._p_IDF[p])[:self._mpr])

    # check whether the constraints mpr and mru are compatible with the UPA matrix
    def _incompatible(self):
        for u in self._upa.keys():
            if self._mpr * self._mru < len(self._upa[u]):
                print(self._mpr, self._mru, len(self._upa[u]))
                return True
        return False

    # straw-man heuristic applyed to user u
    def _fix(self, u):
        self._ua[u] = set()
        tmp_u = deepcopy(self._upa[u])
        self._unc_upa[u] = deepcopy(self._upa[u])
        if self.access_matrix == 'uncupa' and self.selection == 'idf':
            tmp_p_IDF = {p: -math.log(len(self._pua[p]) / len(self._users), 2) for p in tmp_u}

        for r in self._pa.keys():
            if len(self._pa[r]) == self._mpr and self._pa[r].issubset(tmp_u):
                self._ua[u].add(r)
                tmp_u = tmp_u.difference(self._pa[r])
                self._unc_upa[u] = self._unc_upa[u].difference(self._pa[r])
        while len(tmp_u) >= self._mpr:
            if self.access_matrix == 'uncupa' and self.selection == 'idf':
                prms = set(sorted(tmp_u, key=lambda p: tmp_p_IDF[p])[:self._mpr])
            else:
                prms = self._selection(tmp_u)
            self._update_ua_pa({u}, prms)
            tmp_u = tmp_u.difference(prms)
            self._unc_upa[u] = self._unc_upa[u].difference(prms)

        if len(tmp_u):
            self._update_ua_pa({u}, tmp_u)
            self._unc_upa[u] = self._unc_upa[u].difference(tmp_u)

        if len(self._ua[u]) > self._mru:
            print(f'     mru constraint violated for user {u}: assigned {len(self._ua[u])} roles instead of {self._mru}', end='')
            print(f'     mpr = {self._mpr} |UPA[u]| = {len(self._upa[u])}')


    # verify whether mru and mpr constraints are satisfied
    def _verify_solution(self):
        flag = False
        for u in self._users:
            if len(self._ua[u]) > self._mru:
                print(u, f'mru = {self._mru} constraint violated', 'ua', len(self._ua[u]))
                flag = True
            if u in self._unc_upa and len(self._unc_upa[u]):  # prima era if len(self._unc_upa[u]):
                print(u, f'mru ({self._mru}) constraint violated', 'unc_upa', len(self._unc_upa[u]), end=' ')
                perms = set()
                for r in self._ua[u]:
                    perms.update(self._pa[r])
                if perms != self._upa[u]:
                    print(' UPA NOT COVERED')
                else:
                    print()
                flag = True
            if flag:
                return

        for r in self._pa.keys():
            if len(self._pa[r]) > self._mpr:
                print(f'mpr ({self._mpr}) constraint violated')
                return

    # check whether pa contains unused roles, if so remove them
    def _remove_unassigned_roles(self):
        # we remove all roles in _pa that are not assigned to any user
        id_roles = set(self._pa.keys())
        assigned_roles = set()
        for u in self._users:
            assigned_roles.update(self._ua[u])
        if len(id_roles) != len(assigned_roles):  # one or more roles are not needed (they are not assigned to any user)
            to_delete = id_roles.difference(assigned_roles)
            for r in to_delete:
                del self._pa[r]

    def _pick_role(self):
        pass

    # select the user with the minimum number of assigned permissions
    # ties are broken at random
    def _min_uncovered(self):
        if self._minUser != 'idf':
            m = float('inf')
            min_usrs = {}  # users with minimum uncovered permissions
            for u in self._unc_users:
                if 0 < len(self._matrix[u]) < m:
                    m = len(self._matrix[u])
                    min_usrs = {u}
                if len(self._matrix[u]) == m:
                    min_usrs.add(u)
            u = random.sample(sorted(min_usrs), 1) # u is a list, we need the user, hence u[0]
            return u[0]  #min_usrs[-1], last user found, non-deterministic choice
        else:   # user selection strategy is IDF
            #return min(self._unc_users, key=lambda u: sum([self._p_IDF[p] for p in self._matrix[u]]))
            return min(self._unc_users, key=lambda u: self._sumIDF[u])
            # max total IDF value for user selection is non a good combination with PUCC problem
            # return max(self._unc_users, key=lambda u: self._sumIDF[u])


#enforce mpr first
class PRUCC_1(PRUCC):
    def _pick_role(self):
        u = self._min_uncovered()
        usrs = {u}
        prms = self._selection(self._unc_upa[u])
        # look for other users having permissions prms
        for u in self._unc_users:
            if prms.issubset(self._upa[u]):
                usrs.add(u)
        return usrs, prms

    def mine(self):
        while len(self._unc_users) > 0:
            usrs, prms = self._pick_role()
            if usrs:
                self._update_ua_pa(usrs, prms)
                self._update_unc(usrs, prms)
                if (self._matrix is self._unc_upa and
                        (self._minUser == 'idf' or self._selection is self._idf)):
                    self._compute_idf()

        for u in self._users:
            if len(self._ua[u]) > self._mru:
                self._fix(u)
                # aggiungere self._compute_idf()?

        self._remove_unassigned_roles()
        self._verify_solution()


class PRUCC_2(PRUCC):
    def _pick_role(self):
        u = self._min_uncovered()
        #usrs = {u}
        usrs = set()
        usrs_to_fix = set()
        prms = self._selection(self._unc_upa[u])
        # look for other users having permissions prms
        for u in self._unc_users:
            if prms <= self._upa[u]:
                if u not in self._ua or len(self._ua[u]) < self._mru:
                    usrs.add(u)
                else:
                    usrs_to_fix.add(u)

        return usrs, usrs_to_fix, prms

    def mine(self):
        while len(self._unc_users) > 0:
            usrs, usrs_to_fix, prms = self._pick_role()
            if usrs:
                self._update_ua_pa(usrs, prms)
                self._update_unc(usrs, prms)

            for u in usrs_to_fix:
                self._fix(u)
                self._update_unc({u}, self._upa[u])

            if (self._matrix is self._unc_upa and
                    (self._minUser == 'idf' or self._selection is self._idf)):
                self._compute_idf()

        self._remove_unassigned_roles()
        self._verify_solution()


