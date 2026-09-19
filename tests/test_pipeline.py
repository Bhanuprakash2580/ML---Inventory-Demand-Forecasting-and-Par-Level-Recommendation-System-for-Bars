import unittest
from pathlib import Path

import pandas as pd

from src.data_preprocessing import aggregate_daily, load_and_clean
from src.evaluation import evaluate_forecasts, simulate_inventory
from src.par_level import compute_par_level


ROOT = Path(__file__).resolve().parents[1]


class InventoryPipelineTests(unittest.TestCase):
    def test_source_quality_and_daily_coverage(self):
        raw, quality = load_and_clean(ROOT / "Consumption Dataset.xlsx")
        daily = aggregate_daily(raw)
        self.assertEqual(quality["rows_loaded"], 6575)
        self.assertAlmostEqual(quality["max_conservation_error_ml"], 0.0, places=6)
        self.assertEqual(len(daily), 35136)
        self.assertTrue(daily["Consumed (ml)"].ge(0).all())

    def test_metrics_and_par_level(self):
        actual = pd.Series([10.0, 20.0, 30.0])
        metrics = evaluate_forecasts(actual, {"baseline": actual})
        self.assertEqual(metrics.loc["baseline", "MAE_ml"], 0.0)
        par, safety_stock = compute_par_level(10, 2, lead_time_days=2, review_period_days=1)
        self.assertGreater(par, 30)
        self.assertGreaterEqual(safety_stock, 0)

    def test_inventory_simulation_tracks_stockouts(self):
        result = simulate_inventory([10, 10, 10], par_level=5, lead_time_days=2)
        self.assertGreater(result["stockout_days"], 0)
        self.assertGreater(result["lost_volume_ml"], 0)


if __name__ == "__main__":
    unittest.main()
