import pytest

from faker import Faker


class TestInstanceRandomIsolation:
    """Providers must draw randomness from their own generator's random
    source, so that seeded instances never affect each other's sequences."""

    @pytest.mark.parametrize(
        "locale,method_name",
        [
            ("es_MX", "curp"),
            ("es_MX", "rfc"),
            ("es_MX", "elector_code"),
            ("es_ES", "nie"),
            ("es_ES", "nif"),
            ("es_ES", "cif"),
            ("es_ES", "nuss"),
            ("el_GR", "vat_id"),
            ("el_GR", "tin"),
            ("sv_SE", "org_id"),
            ("uk_UA", "ssn"),
            ("th_TH", "ssn"),
            ("en_US", "passport_gender"),
            ("uk_UA", "license_plate"),
        ],
    )
    def test_interleaved_instances_do_not_interfere(self, locale, method_name):
        # Reference sequence from a lone instance
        lone = Faker(locale)
        lone.seed_instance(42)
        expected = [getattr(lone, method_name)() for _ in range(5)]

        # Same seed, but another instance generates values in between
        instance = Faker(locale)
        instance.seed_instance(42)
        other = Faker(locale)
        other.seed_instance(7)
        actual = []
        for _ in range(5):
            actual.append(getattr(instance, method_name)())
            getattr(other, method_name)()

        assert actual == expected

    def test_same_seed_same_sequence(self):
        fake1 = Faker("es_MX")
        fake1.seed_instance(1234)
        fake2 = Faker("es_MX")
        fake2.seed_instance(1234)

        assert [fake1.curp() for _ in range(5)] == [fake2.curp() for _ in range(5)]

    def test_multi_locale_instances_are_isolated(self):
        lone = Faker(["en_US", "es_MX"])
        lone.seed_instance(42)
        expected = [lone.curp() for _ in range(5)]

        instance = Faker(["en_US", "es_MX"])
        instance.seed_instance(42)
        other = Faker(["en_US", "es_MX"])
        other.seed_instance(7)
        actual = []
        for _ in range(5):
            actual.append(instance.curp())
            other.curp()

        assert actual == expected
