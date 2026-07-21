"""Business logic for the ant colony, traditional architecture.

One Colony object owns all state in memory: ants, larvae, a chamber count,
food stores, trails, and expeditions. Every operation is a method that
mutates that state directly, so consistency between entities comes for
free from sequential execution in a single process. There is deliberately
no math here, only rules and thresholds.

Time is command-driven: the new_day meta-command is the clock tick that
separates one day's command sequence from the next. Chambers are
anonymous, the colony only counts them; each holds at most one larva, and
freshly dug chambers open on the next day. Food is consumed only by the
queen (feed_queen) and by provisioning digging crews. Expeditions earn
|foragers| + |days away| food when they report back, and raise_alarm with
a threat above the soldier count wipes the stores and the brood.
"""

from shared.interpreter import CommandError

CASTES = ("worker", "forager", "soldier", "nurse")

# every relation in the colony is 1:1: one food buys one larva, one nurse
# covers one larva, one chamber houses one larva, one worker digs one
# chamber for one food


class Ant:
    def __init__(self, ant_id, caste):
        self.id = ant_id
        self.caste = caste
        self.status = "idle"  


class Larva:
    def __init__(self, larva_id):
        self.id = larva_id


class Expedition:
    def __init__(self, expedition_id, source, forager_ids, departed_day):
        self.id = expedition_id
        self.source = source
        self.forager_ids = forager_ids
        self.departed_day = departed_day
        self.status = "out"  


class Colony:
    def __init__(self):
        self.day = 0
        self.ants = {}
        self.larvae = {}
        self.num_chambers = 0
        self.pending_chambers = 0
        self.trails = set()
        self.expeditions = {}
        self.food = 0
        self._next_ant = 1
        self._next_larva = 1
        self._next_expedition = 1

    @classmethod
    def bootstrap(cls):
        colony = cls()
        colony.food = 20
        colony.num_chambers = 3
        colony.trails = {"oak", "bush"}
        for caste, count in (("worker", 4), ("forager", 3),
                             ("soldier", 2), ("nurse", 2)):
            for _ in range(count):
                colony._add_ant(caste)
        colony._add_larva()
        return colony

    def command_table(self):
        return {
            "new_day": self.new_day,
            "feed_queen": self.feed_queen,
            "hatch_ant": self.hatch_ant,
            "requalify_ant": self.requalify_ant,
            "get_ants": self.get_ants,
            "dispatch_foraging_party": self.dispatch_foraging_party,
            "return_expedition": self.return_expedition,
            "dig_chamber": self.dig_chamber,
            "scout_new_trail": self.scout_new_trail,
            "raise_alarm": self.raise_alarm,
            "colony_status": self.colony_status,
        }

    # ---- operations -----------------------------------------------------

    def new_day(self, args):
        self.day += 1
        opened = self.pending_chambers
        self.num_chambers += opened
        self.pending_chambers = 0
        return {"day": self.day, "chambers_opened": opened}

    def feed_queen(self, args):
        amount = self._int(args, "amount")
        if amount > self.food:
            raise CommandError(f"need {amount} food, only {self.food} in stores")
        nurse_slots = self._nursing_capacity() - len(self.larvae)
        if amount > nurse_slots:
            raise CommandError(f"the queen lays one larva per food eaten, "
                               f"but nurses can cover only {nurse_slots} more")
        available = self._available_chambers()
        if amount > available:
            raise CommandError(f"the queen lays one larva per food eaten, "
                               f"but only {available} chambers are available")
        self.food -= amount
        for _ in range(amount):
            self._add_larva()
        return {"consumed": amount, "larvae_laid": amount,
                "food_left": self.food}

    def hatch_ant(self, args):
        caste = self._caste(args)
        if not self.larvae:
            raise CommandError("no larvae to hatch")
        larva = min(self.larvae.values(), key=lambda l: l.id)
        del self.larvae[larva.id]
        ant = self._add_ant(caste)
        return {"ant_id": ant.id, "caste": caste, "from_larva": larva.id}

    def requalify_ant(self, args):
        ant = self._ant(args)
        profession = self._caste(args, key="profession")
        if ant.status != "idle":
            raise CommandError(f"ant {ant.id} is busy ({ant.status})")
        if profession != "nurse":
            self._check_brood_survives_losing(ant)
        previous = ant.caste
        ant.caste = profession
        return {"ant_id": ant.id, "from": previous, "to": profession}

    def get_ants(self, args):
        return {"ants": [{"id": a.id, "job": a.caste, "status": a.status}
                         for a in sorted(self.ants.values(),
                                         key=lambda a: a.id)]}

    def dispatch_foraging_party(self, args):
        source = self._require(args, "source")
        count = self._int(args, "count")
        if source not in self.trails:
            raise CommandError(f"no known trail to {source!r}")
        idle = [a for a in self.ants.values()
                if a.caste == "forager" and a.status == "idle"]
        if len(idle) < count:
            raise CommandError(f"need {count} foragers, only {len(idle)} idle")
        party = sorted(idle, key=lambda a: a.id)[:count]
        for ant in party:
            ant.status = "foraging"
        expedition = Expedition(self._next_expedition, source,
                                [a.id for a in party], self.day)
        self._next_expedition += 1
        self.expeditions[expedition.id] = expedition
        return {"expedition_id": expedition.id, "source": source,
                "foragers": expedition.forager_ids, "departed_day": self.day}

    def return_expedition(self, args):
        expedition = self._expedition(args)
        if expedition.status != "out":
            raise CommandError(
                f"expedition {expedition.id} already {expedition.status}")
        if self.day <= expedition.departed_day:
            raise CommandError(
                f"expedition {expedition.id} left today, "
                "it can return tomorrow at the earliest")
        days_out = self.day - expedition.departed_day
        gained = len(expedition.forager_ids) + days_out
        self.food += gained
        for ant_id in expedition.forager_ids:
            ant = self.ants.get(ant_id)
            if ant is not None:
                ant.status = "idle"
        expedition.status = "returned"
        return {"expedition_id": expedition.id, "days_out": days_out,
                "food_gained": gained, "food_total": self.food}

    def dig_chamber(self, args):
        idle = sum(1 for a in self.ants.values()
                   if a.caste == "worker" and a.status == "idle")
        if idle == 0:
            raise CommandError("no idle workers to dig")
        # every idle worker digs one chamber but needs provisioning,
        # so the crew size is capped by what the stores can feed
        crew = min(idle, self.food)
        if crew == 0:
            raise CommandError(f"cannot provision any digger, "
                               f"only {self.food} food in stores")
        self.food -= crew
        self.pending_chambers += crew
        return {"chambers_started": crew, "workers_digging": crew,
                "food_spent": crew}

    def scout_new_trail(self, args):
        source = self._require(args, "source")
        if source in self.trails:
            raise CommandError(f"trail to {source!r} already known")
        scout = next((a for a in self.ants.values()
                      if a.caste == "forager" and a.status == "idle"), None)
        if scout is None:
            raise CommandError("no idle forager available to scout")
        self.trails.add(source)
        return {"source": source, "scouted_by": scout.id}

    def raise_alarm(self, args):
        threat = self._int(args, "threat")
        soldiers = sum(1 for a in self.ants.values() if a.caste == "soldier")
        if threat > soldiers:
            food_lost, larvae_lost = self.food, len(self.larvae)
            self.food = 0
            self.larvae = {}
            return {"outcome": "overrun", "threat": threat,
                    "soldiers": soldiers, "food_lost": food_lost,
                    "larvae_lost": larvae_lost}
        return {"outcome": "repelled", "threat": threat, "soldiers": soldiers}

    def colony_status(self, args):
        by_caste = {caste: 0 for caste in CASTES}
        busy = 0
        for ant in self.ants.values():
            by_caste[ant.caste] += 1
            if ant.status != "idle":
                busy += 1
        return {
            "day": self.day,
            "food": self.food,
            "ants": by_caste,
            "busy_ants": busy,
            "larvae": len(self.larvae),
            "num_chambers": self.num_chambers,
            "num_available_chambers": self._available_chambers(),
            "pending_chambers": self.pending_chambers,
            "trails": sorted(self.trails),
            "expeditions_out": [
                {"id": e.id, "source": e.source,
                 "days_out": self.day - e.departed_day}
                for e in self.expeditions.values() if e.status == "out"],
        }

    # ---- internal helpers -----------------------------------------------

    def _add_ant(self, caste):
        ant = Ant(self._next_ant, caste)
        self._next_ant += 1
        self.ants[ant.id] = ant
        return ant

    def _add_larva(self):
        larva = Larva(self._next_larva)
        self._next_larva += 1
        self.larvae[larva.id] = larva
        return larva

    def _available_chambers(self):
        return self.num_chambers - len(self.larvae)

    def _nursing_capacity(self):
        return sum(1 for a in self.ants.values() if a.caste == "nurse")

    def _check_brood_survives_losing(self, ant):
        if ant.caste != "nurse":
            return
        remaining = self._nursing_capacity() - 1
        if len(self.larvae) > remaining:
            raise CommandError(
                f"cannot release nurse {ant.id}: {len(self.larvae)} larvae "
                f"need care, remaining nurses cover only {remaining}")

    # ---- argument parsing -----------------------------------------------

    def _require(self, args, key):
        if key not in args:
            raise CommandError(f"missing argument {key!r}")
        return args[key]

    def _int(self, args, key):
        value = self._require(args, key)
        if not value.isdigit() or int(value) < 1:
            raise CommandError(f"{key!r} must be a positive integer")
        return int(value)

    def _caste(self, args, key="caste"):
        caste = self._require(args, key)
        if caste not in CASTES:
            raise CommandError(f"{key} must be one of {', '.join(CASTES)}")
        return caste

    def _ant(self, args):
        ant_id = self._int(args, "id")
        ant = self.ants.get(ant_id)
        if ant is None:
            raise CommandError(f"no ant with id {ant_id}")
        return ant

    def _expedition(self, args):
        expedition_id = self._int(args, "id")
        expedition = self.expeditions.get(expedition_id)
        if expedition is None:
            raise CommandError(f"no expedition with id {expedition_id}")
        return expedition
