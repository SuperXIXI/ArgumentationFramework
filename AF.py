from collections import defaultdict


class AF:
    def __init__(self):
        self.arguments = set()
        self.attacks = set()
        self.attackers = defaultdict(set)
        self.attacked = defaultdict(set)

    def add_argument(self, argument):
        if argument in self.arguments:
            return False
        self.arguments.add(argument)
        return True

    def add_arguments(self, arguments):
        added = False
        for arg in arguments:
            if arg not in self.arguments:
                self.arguments.add(arg)
                added = True
        return added

    def add_attack(self, attacker, attacked):
        if attacker not in self.arguments or attacked not in self.arguments:
            raise ValueError(f'Invalid arguments: ({attacker}, {attacked})')
        if (attacker, attacked) in self.attacks:
            return False
        self.attacks.add((attacker, attacked))
        self.attackers[attacker].add(attacked)
        self.attacked[attacked].add(attacker)
        return True

    def print_arguments(self):
        print('Arguments: ' + str(self.arguments))

    def print_attacks(self):
        print('Attacks: ' + str(self.attacks))

    def print_attacker(self, argument):
        print(f'Attackers of {argument}: {self.attacked[argument]}')

    def print_attacked(self, argument):
        print(f'Arguments attacked by {argument}: {self.attackers[argument]}')

    def _find_illegally_in(self, in_set, out_set):
        illegally_in = set()
        for arg in in_set:
            if not self.attacked[arg].issubset(out_set):
                illegally_in.add(arg)
        return illegally_in

    def _find_super_illegally_in(self, in_set, undec_set, illegally_in):
        super_illegally_in = set()
        for arg in in_set:
            attackers = self.attacked[arg]
            if (attackers & undec_set) or (attackers & (in_set - illegally_in)):
                super_illegally_in.add(arg)
        return super_illegally_in

    def _update_out_undec(self, new_in, out_set, undec_set):
        moved_to_undec = set()
        for out_arg in list(out_set):
            attackers = self.attacked[out_arg]
            if not (attackers & new_in):
                moved_to_undec.add(out_arg)
        new_out = out_set - moved_to_undec
        new_undec = undec_set | moved_to_undec
        return new_out, new_undec

    def _find_extensions(self, extension_type):
        candidates = set()
        initial = (
            frozenset(self.arguments),
            frozenset(),
            frozenset()
        )
        stack = [initial]
        while stack:
            in_set, out_set, undec_set = stack.pop()
            if extension_type == 'stable' and undec_set:
                continue
            elif extension_type == 'preferred' and any(cdt[0] > in_set for cdt in candidates):
                continue
            elif extension_type == 'semi_stable' and any(cdt[2] < undec_set for cdt in candidates):
                continue
            illegally_in = self._find_illegally_in(in_set, out_set)
            if not illegally_in:
                if extension_type == 'semi_stable':
                    if not any(cdt[2] < undec_set for cdt in candidates):
                        to_remove = [cdt for cdt in candidates if undec_set < cdt[2]]
                        for cdt in to_remove:
                            candidates.remove(cdt)
                        candidates.add((frozenset(in_set), frozenset(out_set), frozenset(undec_set)))
                elif extension_type == 'preferred':
                    if not any(cdt[0] > in_set for cdt in candidates):
                        to_remove = [cdt for cdt in candidates if in_set > cdt[0]]
                        for cdt in to_remove:
                            candidates.remove(cdt)
                        candidates.add((frozenset(in_set), frozenset(out_set), frozenset(undec_set)))
                elif extension_type == 'stable':
                    candidates.add((in_set, out_set, undec_set))
                continue
            super_illegally_in = self._find_super_illegally_in(in_set, undec_set, illegally_in)
            if super_illegally_in:
                arg = next(iter(super_illegally_in))
                next_args = [arg]
            else:
                next_args = illegally_in
            for arg in next_args:
                new_in = in_set - {arg}
                new_out = out_set | {arg}
                new_undec = undec_set.copy()
                new_out, new_undec = self._update_out_undec(new_in, new_out, new_undec)
                stack.append((new_in, new_out, new_undec))
        return [{'in': set(in_set), 'out': set(out_set), 'undec': set(undec_set)} for in_set, out_set, undec_set in
                candidates]

    def find_all_semi_stable(self):
        return self._find_extensions('semi_stable')

    def find_all_stable(self):
        return self._find_extensions('stable')

    def find_all_preferred(self):
        return self._find_extensions('preferred')

af = AF()
af.add_arguments(['A','B','C','D','E'])
af.add_attack('A','B')
af.add_attack('B','A')
af.add_attack('B','C')
af.add_attack('C','D')
af.add_attack('D','E')
af.add_attack('E','C')
af.print_arguments()
af.print_attacks()
af.print_attacker('C')
print(af.find_all_semi_stable())
print(af.find_all_stable())
print(af.find_all_preferred())