import py4mc
import pytest

from py4mc.types import Statistics
from py4mc.exceptions import InvalidMetric

mojang = py4mc.MojangApi()


class TestStatistics:

    def test_statistics(self):
        metrics = ["item_sold_minecraft", "prepaid_card_redeemed_minecraft"]
        statistics = mojang.get_statistics(metrics)
        assert isinstance(statistics, Statistics)
        with pytest.raises(InvalidMetric):
            mojang.get_statistics(["Invalid_Metric"])
        assert mojang.get_statistics("item_sold_minecraft") is not None

    def test_statistic_results(self):
        statistics = mojang.get_statistics(Statistics.VALID_METRICS)
        assert isinstance(statistics, Statistics)
        assert isinstance(statistics.total, int)
        assert isinstance(statistics.last_24h, int)
        assert isinstance(statistics.sale_velocity, float)
