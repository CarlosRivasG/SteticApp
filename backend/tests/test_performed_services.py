from decimal import Decimal

import pytest

from app.performed_services import calculate_distribution


def test_commission_at_fifty_percent():
    assert calculate_distribution(25_000, 0, Decimal("50")) == (25_000, 12_500, 12_500)


def test_commission_at_seventy_percent():
    assert calculate_distribution(25_000, 0, Decimal("70")) == (25_000, 17_500, 7_500)


def test_commission_rounds_half_up_to_the_next_peso():
    assert calculate_distribution(1, 0, Decimal("50")) == (1, 1, 0)


def test_discount_cannot_exceed_list_price():
    with pytest.raises(ValueError, match="descuento"):
        calculate_distribution(25_000, 25_001, Decimal("50"))
