import random
from copy import deepcopy
import math


class Mining:
    def __init__(self, dataset, unique=False):
        self._dataset = dataset
        self._users = set()
        self._permissions = set()
        self._upa = {}  # dictionary (user, set of permissions)
        self._upa_unique = {}  # dictionary (user, set of permissions) only users with distinct set of permissions
        self._pua = {}  # dictionary (permission, set of users)
        self._ua = {}  # dictionary (user, set of roles)
        self._pa = {}  # dictionary (role, set of permissions)
        self._k = 0  # mined roles so far
        self._n = 0  # total number of granted access to resources (i.e., number of pairs in dataset)
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
        self._upa_bk = deepcopy(self._upa)  # upa backup
        self._users_map = dict()  #key = user, value=list of users with identical permissions
        equal_prms = dict()
        for u in self._users:
            equal_prms[u] = u
        self._upa = dict()

        for u_i in sorted(self._upa_bk.keys()):
            for u_j in sorted(self._upa_bk.keys()):
                if u_j > u_i and equal_prms[u_j] == u_j and self._upa_bk[u_j] == self._upa_bk[u_i]:
                    equal_prms[u_j] = u_i  #u_j's permissions are identical to u_i's ones

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
                del self._unc_upa[u]  # added
                self._unc_users.remove(u)
        for p in prms:
            self._unc_pua[p] = self._unc_pua[p] - usrs
            if len(self._unc_pua[p]) == 0 and p in self._unc_permissions:
                del self._unc_pua[p]  # addes
                self._unc_permissions.remove(p)

    def _clear(self):  #try to remove redundant role and to lower wsc
        contains = {}  # dictionary (role, set of roles contained in role)
        roles = list(self._pa.items())
        for i in range(0, len(roles) - 1):  #for each role compute all roles it contains
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
                    if intersection:  #some roles contained in r also are assigned to u
                        f1 = True  #reduced wsc
                    self._ua[u] = self._ua[u].difference(intersection)  #remove contained roles, wsc is lowered

        id_roles = set(self._pa.keys())
        assigned_roles = set()
        f2 = False
        for u in self._users:
            assigned_roles.update(self._ua[u])
        if len(id_roles) != len(assigned_roles):  #one or more roles are not needed (they are not assigned to any user)
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

        contains = {}  # dictionary (role, set of roles contained in role)
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
                print(' WSC reduced!', end='')
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

    def get_dupa(self):
        _dupa = 0
        for u in self._users:
            if u not in self._ua.keys():
                _dupa = _dupa + len(self._upa[u])
            else:
                prms = set()
                for r in self._ua[u]:
                    prms = prms.union(self._pa[r])
                if prms.issubset(self._upa[u]):
                    _dupa = _dupa + len(self._upa[u] - prms)
                else:
                    print('ERROR!!!')
                    exit(0)
        return _dupa

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
        sr = sorted(self._pa.items(), key=lambda role: len(role[1]))
        for r in sr:
            print(r)


class ERUPDC(Mining):
    def __init__(self, dataset, mrcu=0, mrcp=0, heuristic='nu'):  # t1 = mrcu, t2 = mrcp
        super().__init__(dataset)
        self._heuristic = heuristic
        self._deg_permission = {}
        self._deg_user = {}
        self._perm_role_count = [0] * (max(self._permissions) + 1)
        self._user_role_count = [0] * (max(self._users) + 1)
        self._mrcu = len(self._users) if mrcu == 0 else mrcu
        self._mrcp = len(self._permissions) if mrcp == 0 else mrcp
        if self._heuristic in ('fiu', 'fip', 'diu', 'dip'):
            self._compute_idf()

    # IDF-based methods
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

    # Phase 1 methods -- start

    # compute the node with the minimum number of uncovered incident edges
    def _min_uncovered(self, node):  # node='u' -> variant NU, node='p' -> variant NP
        if node == 'u':
            threshold = self._mrcu
            role_count = self._user_role_count
            nodes = self._unc_users
            opposite_threshold = self._mrcp
            opposite_role_count = self._perm_role_count
            opposite_nodes = self._unc_upa

        if node == 'p':
            threshold = self._mrcp
            role_count = self._perm_role_count
            nodes = self._unc_permissions
            opposite_threshold = self._mrcu
            opposite_role_count = self._user_role_count
            opposite_nodes = self._unc_pua

        m = float('inf')
        vertices = {}  # set of nodes in the biclique with minimum uncovered degree
        for n in nodes:
            if role_count[n] < (threshold - 1):
                adj = opposite_nodes[n]
                num_o_n = sum(1 for o_n in adj if opposite_role_count[o_n] < opposite_threshold - 1)
                # We check whether there exists at  least a pair (u,p) such that
                # UserRoleCount[u] < mrcu - 1 and PermissionRoleCount[p] < mrcp - 1
                if num_o_n and len(opposite_nodes[n]) < m:
                    m = len(opposite_nodes[n])
                    vertices = {n}
                if num_o_n and len(opposite_nodes[n]) == m:
                    vertices.add(n)

        # nodes set is empty if it doesn't exist any pair (u,p) such that
        # UserRoleCount[u] < mrcu - 1 and PermissionRoleCount[p] < mrcp - 1
        if vertices:  # pick a random vertex
            v = random.sample(sorted(vertices), 1)  # v is a list, we need the node, hence v[0]
            return v[0], m
        else:
            return 0, 0

    # compute the node with the maximum (total) IDF value
    def _max_idf_orig(self, node):  # node='u' -> variant NU-like, node='p' -> variant NP-like
        if node == 'u':
            threshold = self._mrcu
            role_count = self._user_role_count
            nodes = self._unc_users
            opposite_threshold = self._mrcp
            opposite_role_count = self._perm_role_count
            opposite_nodes = self._unc_upa
            idf_value = self._sumIDF

        if node == 'p':
            threshold = self._mrcp
            role_count = self._perm_role_count
            nodes = self._unc_permissions
            opposite_threshold = self._mrcu
            opposite_role_count = self._user_role_count
            opposite_nodes = self._unc_pua
            idf_value = self._p_IDF

        m = 0
        vertices = set()  # set of nodes in the biclique with IDF value
        for n in nodes:
            if role_count[n] < (threshold - 1):
                adj = opposite_nodes[n]
                num_o_n = sum(1 for o_n in adj if opposite_role_count[o_n] < opposite_threshold - 1)
                # We check whether there exists at  least a pair (u,p) such that
                # UserRoleCount[u] < mrcu - 1 and PermissionRoleCount[p] < mrcp - 1
                if num_o_n and idf_value[n] > m:
                    m = idf_value[n]
                    vertices = {n}
                if num_o_n and idf_value[n] == m:
                    vertices.add(n)

        # nodes set is empty if it doesn't exist any pair (u,p) such that
        # UserRoleCount[u] < mrcu - 1 and PermissionRoleCount[p] < mrcp - 1
        if vertices:  # pick a random vertex
            v = random.sample(sorted(vertices), 1)  # v is a list, we need the node, hence v[0]
            return v[0], m
        else:
            return 0, 0

    def _max_idf(self, node):  # node='u' -> variant IU, node='p' -> variant IP
        if node == 'u':
            threshold = self._mrcu
            role_count = self._user_role_count
            nodes = self._unc_users
            opposite_threshold = self._mrcp
            opposite_role_count = self._perm_role_count
            opposite_nodes = self._unc_upa

        if node == 'p':
            threshold = self._mrcp
            role_count = self._perm_role_count
            nodes = self._unc_permissions
            opposite_threshold = self._mrcu
            opposite_role_count = self._user_role_count
            opposite_nodes = self._unc_pua

        m = 0
        vertices = set()  # set of nodes in the biclique with IDF value
        for n in nodes:
            if role_count[n] < (threshold - 1):
                adj = opposite_nodes[n]
                num_o_n = sum(1 for o_n in adj if opposite_role_count[o_n] < opposite_threshold - 1)
                # We check whether there exists at  least a pair (u,p) such that
                # UserRoleCount[u] < mrcu - 1 and PermissionRoleCount[p] < mrcp - 1
                if node == 'p':
                    idf_value = self._p_IDF[n]
                else:
                    idf_value = sum([self._p_IDF[p] for p in self._unc_upa[n]])
                if num_o_n and idf_value > m:
                    m = idf_value
                    vertices = {n}
                if num_o_n and idf_value == m:
                    vertices.add(n)

        # nodes set is empty if it doesn't exist any pair (u,p) such that
        # UserRoleCount[u] < mrcu - 1 and PermissionRoleCount[p] < mrcp - 1
        if vertices:  # pick a random vertex
            v = random.sample(sorted(vertices), 1)  # v is a list, we need the node, hence v[0]
            return v[0], m
        else:
            return 0, 0

    # compute the node with the maximum number of roles left to reach the constraint value
    def _max_rtba(self, node):
        if node == 'u':
            threshold = self._mrcu
            role_count = self._user_role_count
            nodes = self._unc_users
            opposite_threshold = self._mrcp
            opposite_role_count = self._perm_role_count
            opposite_nodes = self._unc_upa

        if node == 'p':
            threshold = self._mrcp
            role_count = self._perm_role_count
            nodes = self._unc_permissions
            opposite_threshold = self._mrcu
            opposite_role_count = self._user_role_count
            opposite_nodes = self._unc_pua

        m = 0
        n_m = {}  # set of nodes in the biclique with the maximum number of roles left to reach the constraint value
        for n in nodes:
            if role_count[
                n] < threshold - 1:  # It has to be UserRoleCount[u] < mrcu - 1 or PermissionRoleCount[p] < mrcp - 1
                adj = opposite_nodes[n]
                num_o_n = sum(1 for o_n in adj if opposite_role_count[o_n] < opposite_threshold - 1)
                rtba = threshold - role_count[n]
                # We check whether there exists at  leat a pair (u,p) such that
                # UserRoleCount[u] < mrcu - 1 and PermissionRoleCount[p] < mrcp - 1
                if num_o_n and rtba > m:
                    m = rtba
                    n_m = {n}
                if num_o_n and rtba == m:
                    n_m.add(n)

        # n_m is empty if all nodes have reached the maximum number of roles
        if n_m:  #pick a random vertex
            v = random.sample(n_m, 1)  # v is a list, we need the node, hence v[0]
            return v[0], m
        else:
            return 0, 0

    # compute the node with the minimum number of roles left to reach the constraint value
    def _min_rtba(self, node):
        if node == 'u':
            threshold = self._mrcu
            role_count = self._user_role_count
            nodes = self._unc_users
            opposite_threshold = self._mrcp
            opposite_role_count = self._perm_role_count
            opposite_nodes = self._unc_upa

        if node == 'p':
            threshold = self._mrcp
            role_count = self._perm_role_count
            nodes = self._unc_permissions
            opposite_threshold = self._mrcu
            opposite_role_count = self._user_role_count
            opposite_nodes = self._unc_pua

        m = float('inf')
        n_m = {}  # set of nodes in the biclique with the maximum number of roles left to reach the constraint value
        for n in nodes:
            if role_count[
                n] < threshold - 1:  # It has to be UserRoleCount[u] < mrcu - 1 or PermissionRoleCount[p] < mrcp - 1
                adj = opposite_nodes[n]
                num_o_n = sum(1 for o_n in adj if opposite_role_count[o_n] < opposite_threshold - 1)
                rtba = threshold - role_count[n]
                # We check whether there exists at  leat a pair (u,p) such that
                # UserRoleCount[u] < mrcu - 1 and PermissionRoleCount[p] < mrcp - 1
                if num_o_n and rtba < m:
                    m = rtba
                    n_m = {n}
                if num_o_n and rtba == m:
                    n_m.add(n)

        # n_m is empty if all nodes have reached the maximum number of roles
        if n_m:  #pick a random vertex
            v = random.sample(n_m, 1)  # v is a list, we need the node, hence v[0]
            return v[0], m
        else:
            return 0, 0

    # compute the node with the minimum/maximum number of roles left to reach the constraint value
    def _rtba(self, node, comp):
        if node == 'u':
            threshold = self._mrcu
            role_count = self._user_role_count
            nodes = self._unc_users
            opposite_threshold = self._mrcp
            opposite_role_count = self._perm_role_count
            opposite_nodes = self._unc_upa

        if node == 'p':
            threshold = self._mrcp
            role_count = self._perm_role_count
            nodes = self._unc_permissions
            opposite_threshold = self._mrcu
            opposite_role_count = self._user_role_count
            opposite_nodes = self._unc_pua

        if comp == 'min':
            test = lambda x, y: True if x < y else False
            m = float('inf')

        if comp == 'max':
            test = lambda x, y: True if x > y else False
            m = 0

        n_m = {}  # set of nodes in the biclique with the maximum number of roles left to reach the constraint value
        for n in nodes:
            if role_count[
                n] < threshold - 1:  # It has to be UserRoleCount[u] < mrcu - 1 or PermissionRoleCount[p] < mrcp - 1
                adj = opposite_nodes[n]
                num_o_n = sum(1 for o_n in adj if opposite_role_count[o_n] < opposite_threshold - 1)
                rtba = threshold - role_count[n]
                # We check whether there exists at  leat a pair (u,p) such that
                # UserRoleCount[u] < mrcu - 1 and PermissionRoleCount[p] < mrcp - 1
                if num_o_n and test(rtba, m):
                    m = rtba
                    n_m = {n}
                if num_o_n and rtba == m:
                    n_m.add(n)

        # n_m is empty if all nodes have reached the maximum number of roles
        if n_m:  #pick a random vertex
            v = random.sample(sorted(n_m), 1)  # v is a list, we need the node, hence v[0]
            return v[0], m
        else:
            return 0, 0

    def _pick_role(self):
        u = p = 0
        u_min = p_min = u_max = p_max = 0
        usrs = prms = {}
        if self._heuristic == 'nu' or self._heuristic == 'np':
            (u, u_min) = self._min_uncovered('u')
            (p, p_min) = self._min_uncovered('p')

        if self._heuristic == 'xr':
            (u, u_max) = self._rtba('u', 'max')
            (p, p_max) = self._rtba('p', 'max')

        if self._heuristic == 'nr':
            (u, u_min) = self._rtba('u', 'min')
            (p, p_min) = self._rtba('p', 'min')

        if self._heuristic in ('fiu', 'fip', 'diu', 'dip'):
            (u, u_min) = self._max_idf('u')
            (p, p_min) = self._max_idf('p')

        if u == 0 or p == 0:  # it doesn't exist any pair (u,p) such that
            return {}, {}  # UserRoleCount[u] < mrcu - 1 and PermissionRoleCount[p] < mrcp - 1

        # heuristic u-preferred, if u_min == p_min we choose a user vertex
        #if self._heuristic == 'nu':
        if self._heuristic in ('nu', 'fiu', 'diu'):
            usrs, prms = self._pick_role_u(u, phase=1) if u_min <= p_min else self._pick_role_p(p, phase=1)

        # heuristic p-preferred, if u_min == p_min we choose a permission vertex
        #if self._heuristic == 'np':
        if self._heuristic in ('np', 'fip', 'dip'):
            usrs, prms = self._pick_role_u(u, phase=1) if u_min < p_min else self._pick_role_p(p, phase=1)

        # heuristic XR, if
        if self._heuristic == 'xr':
            if u_max > p_max:
                usrs, prms = self._pick_role_u(u, phase=1)
            if u_max < p_max:
                usrs, prms = self._pick_role_p(p, phase=1)
            if u_max == p_max:
                usrs, prms = self._pick_role_u(u, phase=1) if len(self._unc_upa[u]) <= len(
                    self._unc_pua[p]) else self._pick_role_p(p, phase=1)

        # heuristic NR, if
        if self._heuristic == 'nr':
            if u_min < p_min:
                usrs, prms = self._pick_role_u(u, phase=1)
            if u_min > p_min:
                usrs, prms = self._pick_role_p(p, phase=1)
            if u_min == p_min:
                usrs, prms = self._pick_role_u(u, phase=1) if len(self._unc_upa[u]) <= len(
                    self._unc_pua[p]) else self._pick_role_p(p, phase=1)

        return usrs, prms

    # Phase 1 methods -- end

    # Phase 2 methods -- start

    # compute the node with the maximum number of uncovered incident edges
    def _max_uncovered(self, node):
        if node == 'u':
            threshold = self._mrcu
            role_count = self._user_role_count
            nodes = self._unc_users
            opposite_threshold = self._mrcp
            opposite_role_count = self._perm_role_count
            opposite_nodes = self._unc_upa

        if node == 'p':
            threshold = self._mrcp
            role_count = self._perm_role_count
            nodes = self._unc_permissions
            opposite_threshold = self._mrcu
            opposite_role_count = self._user_role_count
            opposite_nodes = self._unc_pua

        m = 0
        vertices = {}  # set of nodes in the biclique with maximum uncovered incident edges
        for n in nodes:
            if role_count[n] == threshold - 1:
                adj = opposite_nodes[n]
                num_o_n = sum(1 for o_n in adj if opposite_role_count[o_n] <= opposite_threshold - 1)
                # We check whether there exists at  leat a pair (u,p) such that
                # UserRoleCount[u] == mrcu - 1 and PermissionRoleCount[p] <= mrcp - 1 # or PermissionRoleCount[p] == mrcp - 1???
                # UserRoleCount[u] <= mrcu - 1 and PermissionRoleCount[p] == mrcp - 1 # or UserRoleCount[p] == mrcp - 1???
                if num_o_n and len(opposite_nodes[n]) > m:
                    m = len(opposite_nodes[n])
                    vertices = {n}
                if num_o_n and len(opposite_nodes[n]) == m:
                    vertices.add(n)

        # set of nodes is empty if it doesn't exist any pair (u,p) such that
        # UserRoleCount[u] == mrcu - 1 and PermissionRoleCount[p] == mrcp - 1
        if vertices:  # pick a random vertex
            v = random.sample(sorted(vertices), 1)  # v is a list, we need the node, hence v[0]
            return v[0], m
        else:
            return 0, 0

    def _max_uncovered_IDF_orig(self, node):
        if node == 'u':
            threshold = self._mrcu
            role_count = self._user_role_count
            nodes = self._unc_users
            opposite_threshold = self._mrcp
            opposite_role_count = self._perm_role_count
            opposite_nodes = self._unc_upa
            idf_value = self._sumIDF

        if node == 'p':
            threshold = self._mrcp
            role_count = self._perm_role_count
            nodes = self._unc_permissions
            opposite_threshold = self._mrcu
            opposite_role_count = self._user_role_count
            opposite_nodes = self._unc_pua
            idf_value = self._p_IDF

        m = 0
        vertices = set()  # set of nodes in the biclique with maximum uncovered incident edges
        for n in nodes:
            if role_count[n] == threshold - 1:
                adj = opposite_nodes[n]
                num_o_n = sum(1 for o_n in adj if opposite_role_count[o_n] <= opposite_threshold - 1)
                # We check whether there exists at  leat a pair (u,p) such that
                # UserRoleCount[u] == mrcu - 1 and PermissionRoleCount[p] <= mrcp - 1 # or PermissionRoleCount[p] == mrcp - 1???
                # UserRoleCount[u] <= mrcu - 1 and PermissionRoleCount[p] == mrcp - 1 # or UserRoleCount[p] == mrcp - 1???
                if num_o_n and idf_value[n] > m:
                    m = idf_value[n]
                    vertices = {n}
                if num_o_n and idf_value[n] == m:
                    vertices.add(n)

        # set of nodes is empty if it doesn't exist any pair (u,p) such that
        # UserRoleCount[u] == mrcu - 1 and PermissionRoleCount[p] == mrcp - 1
        if vertices:  # pick a random vertex
            v = random.sample(sorted(vertices), 1)  # v is a list, we need the node, hence v[0]
            return v[0], m
        else:
            return 0, 0

    def _max_uncovered_IDF(self, node):
        if node == 'u':
            threshold = self._mrcu
            role_count = self._user_role_count
            nodes = self._unc_users
            opposite_threshold = self._mrcp
            opposite_role_count = self._perm_role_count
            opposite_nodes = self._unc_upa

        if node == 'p':
            threshold = self._mrcp
            role_count = self._perm_role_count
            nodes = self._unc_permissions
            opposite_threshold = self._mrcu
            opposite_role_count = self._user_role_count
            opposite_nodes = self._unc_pua

        m = 0
        vertices = set()  # set of nodes in the biclique with maximum uncovered incident edges
        for n in nodes:
            if role_count[n] == threshold - 1:
                adj = opposite_nodes[n]
                num_o_n = sum(1 for o_n in adj if opposite_role_count[o_n] <= opposite_threshold - 1)
                # We check whether there exists at  leat a pair (u,p) such that
                # UserRoleCount[u] == mrcu - 1 and PermissionRoleCount[p] <= mrcp - 1 # or PermissionRoleCount[p] == mrcp - 1???
                # UserRoleCount[u] <= mrcu - 1 and PermissionRoleCount[p] == mrcp - 1 # or UserRoleCount[p] == mrcp - 1???
                if node == 'p':
                    idf_value = self._p_IDF[n]
                else:
                    idf_value = sum([self._p_IDF[p] for p in self._unc_upa[n]])
                if num_o_n and idf_value > m:
                    m = idf_value
                    vertices = {n}
                if num_o_n and idf_value == m:
                    vertices.add(n)

        # set of nodes is empty if it doesn't exist any pair (u,p) such that
        # UserRoleCount[u] == mrcu - 1 and PermissionRoleCount[p] == mrcp - 1
        if vertices:  # pick a random vertex
            v = random.sample(sorted(vertices), 1)  # v is a list, we need the node, hence v[0]
            return v[0], m
        else:
            return 0, 0

    def _pick_role_phase_2(self):
        usrs = set()
        prms = set()
        u = p = 0
        if self._heuristic in ('fiu', 'fip', 'diu', 'dip'):
            (u, u_max) = self._max_uncovered_IDF('u')
            (p, p_max) = self._max_uncovered_IDF('p')
        else:
            (u, u_max) = self._max_uncovered('u')
            (p, p_max) = self._max_uncovered('p')
        #print('Phase #2 (u, u_max), (p, p_max)', (u, u_max), (p, p_max))

        #if u == 0 and p == 0:  # it doesn't exist any pair (u,p) such that
        if u == 0 or p == 0:
            return {}, {}  # UserRoleCount[u] == mrcu - 1 and PermissionRoleCount[p] <= mrcp - 1
            # UserRoleCount[u] <= mrcu - 1 and PermissionRoleCount[p] == mrcp - 1

        if u_max >= p_max:  # priority to user
            try:
                tmp_prms = self._unc_upa[u]
            except:
                print('user:', u)
                exit(1)
            tmp_prms_lte_mrcp = [tmp_p for tmp_p in tmp_prms if self._perm_role_count[tmp_p] <= self._mrcp - 1]
            # sum(1 for tmp_p in tmp_prms if self._perm_role_count[tmp_p] <= self._mrcp - 1)
            if len(tmp_prms) == len(tmp_prms_lte_mrcp):
                (usrs, prms) = self._pick_role_u(u, phase=2)
                # print('F2: scelto utente', u, u_max, usrs, prms)
            else:
                # pick a random permission in self._unc_upa[u] that can be assigned to a role
                # not specified in the TDSC paper, this is just a guess
                p_l = random.sample(tmp_prms_lte_mrcp, 1)
                p = p_l[0]  # p_l is a list, we need the unique permission in it, hence p_l[0]
                (usrs, prms) = self._pick_role_p(p, phase=2)
                # print('F2: scelto permesso', p, p_max, usrs, prms)
        else:
            (usrs, prms) = self._pick_role_p(p, phase=2)
            # print('F2: scelto permesso', p, p_max, usrs, prms)

        return usrs, prms

    # Phase 2 methods -- end

    # Phases 1 and 2 methods -- start

    #Form_Role procedure of TDSC paper
    def _pick_role_u(self, u, phase=1):  # the selected node is a user
        if phase == 1:
            test = lambda x, y: True if x < y else False

        if phase == 2:
            test = lambda x, y: True if x <= y else False

        usrs = {u}
        self._user_role_count[u] = self._user_role_count[u] + 1
        prms = set()
        # expand prms
        for p in self._unc_upa[u]:  # we could select permissions according to their IDF value
            if test(self._perm_role_count[p], self._mrcp - 1):
                prms.add(p)
                self._perm_role_count[p] = self._perm_role_count[p] + 1
        # expand usrs
        u_u_copy = deepcopy(self._unc_users)
        u_u_copy.remove(u)
        for tmp_u in u_u_copy:
            if prms.issubset(self._upa[tmp_u]) and \
                    len(prms.intersection(self._unc_upa[tmp_u])) and \
                    test(self._user_role_count[tmp_u], self._mrcu - 1):
                usrs.add(tmp_u)
                self._user_role_count[tmp_u] = self._user_role_count[tmp_u] + 1
            else:
                if prms.issubset(self._upa[tmp_u]) and \
                        self._unc_upa[tmp_u].issubset(prms) and \
                        self._user_role_count[tmp_u] <= self._mrcu - 1:  # prima era ==
                    usrs.add(tmp_u)
                    self._user_role_count[tmp_u] = self._user_role_count[tmp_u] + 1

        return usrs, prms

    #Dual of Form_Role procedure of TDSC paper
    def _pick_role_p(self, p, phase=1):  # the selected node is a permission
        if phase == 1:
            test = lambda x, y: True if x < y else False

        if phase == 2:
            test = lambda x, y: True if x <= y else False

        usrs = set()
        prms = {p}
        self._perm_role_count[p] = self._perm_role_count[p] + 1
        # expand usrs
        for u in self._unc_pua[p]:
            if test(self._user_role_count[u], self._mrcu - 1):
                usrs.add(u)
                self._user_role_count[u] = self._user_role_count[u] + 1
        #expand prms
        u_p_copy = deepcopy(self._unc_permissions)
        u_p_copy.remove(p)
        for tmp_p in u_p_copy:
            if usrs.issubset(self._pua[tmp_p]) and \
                    len(usrs.intersection(self._unc_pua[tmp_p])) and \
                    test(self._perm_role_count[tmp_p], self._mrcp - 1):
                prms.add(tmp_p)
                self._perm_role_count[tmp_p] = self._perm_role_count[tmp_p] + 1
            else:
                if usrs.issubset(self._pua[tmp_p]) and \
                        self._unc_pua[tmp_p].issubset(usrs) and \
                        self._perm_role_count[tmp_p] <= self._mrcp - 1:  #prima era ==
                    prms.add(tmp_p)
                    self._perm_role_count[tmp_p] = self._perm_role_count[tmp_p] + 1

        return usrs, prms

    #Implemented as described in the TDSC paper
    def _available_nodes(self, phase=1):
        if phase == 1:
            test = lambda x, y: True if x < y else False

        if phase == 2:
            test = lambda x, y: True if x == y else False

        for u in self._unc_users:
            if test(self._user_role_count[u], self._mrcu - 1):
                return True
        for p in self._unc_permissions:
            if test(self._perm_role_count[p], self._mrcp - 1):
                return True
        return False

    # Phases 1 and 2 methods -- end

    def mine(self):
        # Phase 1
        while self._available_nodes(phase=1):
            usrs, prms = self._pick_role()
            if not usrs or not prms:  # No new role to add, execute  Phase 2
                break
            self._update_ua_pa(usrs, prms)
            self._update_unc(usrs, prms)

            # update IDF values
            #"""
            if self._heuristic in ('diu', 'dip'):
                self._compute_idf()
            #"""

        #print(self._mrcp, self._mrcu, self._available_nodes(phase = 2))
        # Phase 2
        while self._available_nodes(phase=2):
            usrs, prms = self._pick_role_phase_2()
            #print('Phase #2, (usrs, prms)', (usrs, prms))
            if not usrs or not prms:  # No new role to add, mined all possible roles
                break
            self._update_ua_pa(usrs, prms)
            self._update_unc(usrs, prms)

            # update IDF values
            #"""
            if self._heuristic in ('diu', 'dip'):
                self._compute_idf()
            #"""
