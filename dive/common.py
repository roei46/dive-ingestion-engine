from enum import StrEnum


class Currency(StrEnum):
    ILS = "ILS"
    EUR = "EUR"
    USD = "USD"


class Tier(StrEnum):
    gold = "gold"
    silver = "silver"
    bronze = "bronze"
