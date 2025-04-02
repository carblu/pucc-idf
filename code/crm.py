from rm import Mining
from copy import deepcopy
from collections import defaultdict


class CRM(Mining):
    def __init__(self, dataset, mpr=0):
        super().__init__(dataset)
        self._mpr = len(self._permissions) if mpr == 0 else mpr
        self._cluster()

    def _cluster(self):
        self._users_bk = deepcopy(self._users)  # users backup
        self._upa_bk = deepcopy(self._upa)  # upa backup
        self._users_map = dict()
        cluster = defaultdict(set)  # permissions:users having such permissions

        for u, prms in self._upa.items():
            cluster[tuple(sorted(prms))].add(u)

        # mapping new user -> 'old' users in a cluster
        # building a reduced upa
        self._upa = dict()
        self._count_p = dict()
        self._count_u = dict()  # number of users in a cluster c
        for c, prms_users in enumerate(cluster.items(), 1):  # (i, (role, {users having role}))
            self._users_map[c] = deepcopy(prms_users[1])
            self._upa[c] = set(prms_users[0])
            self._count_p[c] = len(prms_users[0])  # len(self._unc_upa[u])
            self._count_u[c] = len(prms_users[1])

        self._users = set(self._users_map.keys())

        # we could compress the permissions as well

        # to remove we this method is moved to Mining
        self._unc_upa = deepcopy(self._upa)
        # Be careful, if we compute the cluster, we should recompute pua
        self._unc_pua = deepcopy(self._pua)
        self._unc_users = deepcopy(self._users)
        self._unc_permissions = deepcopy(self._permissions)

    def _pick_role(self):
        usrs_list = list()
        prms_list = list()

        def select_max(u):
            return sum(self._count_u[user] for user in selectable_users if self._unc_upa[u] <= self._upa[user])

        def max_cover(role):
            return sum(self._count_u[u] for u in self._unc_users if u != c and role <= self._upa[u])

        # check paper, maybe we just need FastMiner not CompleteMiner
        def generate_roles_CompleteMiner(role):
            def compact(roles):
                rt = list()
                for r in roles:
                    if r and r not in rt:
                        rt.append(r)

                return rt

            temp_roles = [role & permissions for permissions in self._unc_upa.values() if permissions is not role]
            #print('temp_roles', len(temp_roles), temp_roles)
            initial_roles = compact(temp_roles)
            #print('initial_roles', len(initial_roles), initial_roles)

            gen_roles = list()
            for i in initial_roles:
                gen_roles.extend(compact([i & j for j in initial_roles if i is not j]))
                gen_roles = compact(gen_roles)
                gen_roles.extend(compact([i & j for j in gen_roles]))
                gen_roles = compact(gen_roles)

            #print('gen_roles', len(gen_roles), gen_roles)

            initial_roles.extend(gen_roles)
            potential_roles = compact(initial_roles)

            #print('potential_roles', len(potential_roles), potential_roles)

            return [r for r in potential_roles if len(r) <= self._mpr]

        def generate_roles(role):
            def compact(roles):
                rt = list()
                for r in roles:
                    if r and r not in rt:
                        rt.append(r)

                return rt

            temp_roles = [role & permissions for permissions in self._unc_upa.values()]
            potential_roles = compact(temp_roles)
            return [r for r in potential_roles if len(r) <= self._mpr]


        # self._count_p[u] is the same as len(self._unc_upa[u])
        # selectable_users = [u for u in self._unc_users if self._count_p[u] <= self._mpr]
        selectable_users = [u for u in self._unc_users if len(self._unc_upa[u]) <= self._mpr]

        if selectable_users:
            u = max(selectable_users, key=select_max)
            prms = self._unc_upa[u]
            usrs = {u for u in self._unc_users if prms <= self._upa[u]}
            usrs_list.append(usrs)
            prms_list.append(prms)
        else:
            #potential_roles = generate_roles(r := min(self._unc_upa.values(), key=len)) # r corresponds to P(Q(c)) in the paper
            c, r = min(self._unc_upa.items(), key=lambda t: len(t[1]))
            potential_roles = generate_roles(r)

            if potential_roles:
                # do not consider r (associated to cluster c) in max cover
                # this is stated in the paper. Wrong choice!
                prms = max(potential_roles, key=max_cover)
                usrs = {u for u in self._unc_users if prms <= self._upa[u]}
                usrs_list.append(usrs)
                prms_list.append(prms)
            else:  # split r into k-sized roles
                permissions = list(r)
                # this is the assignment as in the paper
                for i in range(0, len(r), self._mpr):
                    usrs_list.append({c})
                    prms_list.append(set(permissions[i:i+self._mpr]))

                # this is the assignment as the other ones in our heuristics
                # we used this assignment in our IEEE ACCESS paper
                # for i in range(0, len(r), self._mpr):
                #     prms_list.append(prms := set(permissions[i:i+self._mpr]))
                #     usrs_list.append({u for u in self._unc_users if prms <= self._upa[u]})

                # print('No potential role found, we have to split')
                # print('the selected role:', r)
                # print('newly formed roles', prms_list)
                # print('assigned to user', usrs_list)
                #exit()

        return usrs_list, prms_list

    def get_wsc(self):
        _, nr, ua_size, pa_size = super().get_wsc()
        ua_size = sum(len(self._users_map[u]) * len(prms) for u, prms in self._ua.items())
        return nr + ua_size + pa_size, nr, ua_size, pa_size

    def mine(self):
        while self._unc_users:
            usrs_list, prms_list = self._pick_role()
            for usrs, prms in zip(usrs_list, prms_list):
                self._update_ua_pa(usrs, prms)
                self._update_unc(usrs, prms)
