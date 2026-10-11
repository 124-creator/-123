"""Artificial checks for descriptive arithmetic; no market fitting."""
import unittest
from decimal import Decimal
import importlib.util
from pathlib import Path

class DescriptiveTests(unittest.TestCase):
    def test_linear_quantiles_mean_and_signed_zero(self):
        path=Path(__file__).with_name('describe_reported_prices.py')
        self.assertTrue(path.exists(), 'Descriptor implementation is not yet present')
        spec=importlib.util.spec_from_file_location('descriptor',path)
        if spec is None or spec.loader is None:
            raise RuntimeError('Descriptor module could not be loaded')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        actual=module.describe([Decimal('-2'),Decimal('-0.00'),Decimal('0'),Decimal('2')])
        self.assertEqual(actual['n'],4)
        self.assertEqual(actual['mean'],0.0)
        self.assertEqual(actual['q25'],-0.5)
        self.assertEqual(actual['median'],0.0)
        self.assertEqual(actual['q75'],0.5)
        self.assertEqual(actual['negative_count'],1)
        self.assertEqual(actual['positive_count'],1)
        self.assertEqual(actual['reported_zero_count'],2)
        self.assertEqual(actual['reported_zero_share'],0.5)
        self.assertAlmostEqual(actual['sample_sd'],(8/3)**0.5)

if __name__=='__main__':
    unittest.main(verbosity=2)
