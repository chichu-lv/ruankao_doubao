import unittest

from architectpass_acceptance import run_accelerated_pilot


class AcceleratedPilotTests(unittest.TestCase):
    def test_seven_logical_days_pass_without_claiming_real_pilot(self) -> None:
        report = run_accelerated_pilot()
        self.assertEqual("PASS", report["status"])
        self.assertEqual(7, report["simulated_period"]["logical_days"])
        self.assertTrue(all(report["checks"].values()))
        self.assertEqual(0, report["production_writes"])
        self.assertEqual(0, report["external_service_calls"])
        self.assertEqual(0, report["cheko_answers_or_submissions"])
        self.assertFalse(report["authoritative_learning_state"])
        self.assertFalse(report["real_seven_day_independent_pilot_satisfied"])
        self.assertEqual("FIXED_AND_REGRESSION_TESTED", report["issues"][0]["status"])


if __name__ == "__main__":
    unittest.main()
