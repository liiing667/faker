import random

from faker import Faker


class TestInstanceRandomIsolation:
    """Faker instances seeded via ``seed_instance`` must not share random
    state, neither through the generator layer nor through providers
    reaching for the global ``random`` module."""

    def test_same_seed_same_sequence(self):
        fake1 = Faker("es_MX")
        fake2 = Faker("es_MX")
        fake1.seed_instance(1234)
        fake2.seed_instance(1234)

        assert [fake1.curp() for _ in range(10)] == [fake2.curp() for _ in range(10)]

    def test_interleaved_instances_do_not_interfere(self):
        reference = Faker("es_MX")
        reference.seed_instance(7)
        expected = [reference.curp() for _ in range(5)]

        busy = Faker("es_MX")
        busy.seed_instance(999)
        target = Faker("es_MX")
        target.seed_instance(7)

        # Heavy usage of one instance must not advance another's random stream
        for _ in range(1000):
            busy.curp()

        assert [target.curp() for _ in range(5)] == expected

    def test_providers_do_not_touch_global_random_state(self):
        random.seed(12345)
        state_before = random.getstate()

        es_mx = Faker("es_MX")
        es_mx.seed_instance(1)
        es_mx.curp()
        es_mx.rfc()
        es_mx.elector_code()
        es_mx.ssn()

        sv_se = Faker("sv_SE")
        sv_se.seed_instance(1)
        sv_se.org_id()
        sv_se.ssn()

        es_es = Faker("es_ES")
        es_es.seed_instance(1)
        es_es.nif()
        es_es.nie()
        es_es.cif()
        es_es.nuss()

        uk_ua = Faker("uk_UA")
        uk_ua.seed_instance(1)
        uk_ua.ssn()
        uk_ua.license_plate()
        uk_ua.diplomatic_license_plate()

        el_gr = Faker("el_GR")
        el_gr.seed_instance(1)
        el_gr.tin()
        el_gr.vat_id()

        en_us = Faker("en_US")
        en_us.seed_instance(1)
        en_us.passport_gender()
        en_us.passport_gender(seed=5)

        assert random.getstate() == state_before

    def test_passport_gender_seed_argument_is_self_contained(self):
        """The ``seed`` argument of ``passport_gender`` must be deterministic
        without disturbing the instance's own random stream."""
        fake = Faker("en_US")
        fake.seed_instance(0)
        expected = [fake.passport_gender() for _ in range(3)]

        fake.seed_instance(0)
        assert fake.passport_gender(seed=5) == fake.passport_gender(seed=5)
        assert [fake.passport_gender() for _ in range(3)] == expected

    def test_multilocale_instances_are_isolated(self):
        reference = Faker(["en_US", "ja_JP"])
        reference.seed_instance(42)
        expected = [reference.name() for _ in range(5)]

        busy = Faker(["en_US", "ja_JP"])
        busy.seed_instance(1337)
        target = Faker(["en_US", "ja_JP"])
        target.seed_instance(42)

        for _ in range(1000):
            busy.name()

        assert [target.name() for _ in range(5)] == expected
