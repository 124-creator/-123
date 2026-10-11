"""Synthetic checks ONLY; fixtures are not observations or statistical evidence."""
import copy, unittest
from price_pair_gate import validate_pair,gate,timestamp
class Tests(unittest.TestCase):
 def setUp(self):
  self.a={'auction_id':'TEST-ONLY','auction_date':'2024-01-04','auction_price_eur_per_tco2':'80',
   'mu_B':'10','sd_B':'5','V':'100','N':'10','S':'5','R':'2',
   'minimum_bid_price_eur_per_tco2':'70','maximum_bid_price_eur_per_tco2':'90'}
  self.r={'auction_id':'TEST-ONLY','reference_timestamp':'2024-01-04T09:59:30Z',
   'reference_product':'TEST_SPOT','reference_maturity':'spot','reference_quote_type':'midpoint',
   'reference_bid_eur':'79','reference_ask_eur':'81','reference_source_id':'fixture','reference_row_id':'synthetic1'}
  self.c={'auction_id':'TEST-ONLY','bidding_close_timestamp':'2024-01-04T11:00:00+01:00','calendar_source_id':'fixture'}
  self.p={'status':'LOCKED_AFTER_SOURCE_REVIEW','max_quote_age_seconds':60,
   'reference_sources':{'fixture':{'lawful_access_reviewed':True,'method_evidence':'SYNTHETIC_NOT_SOURCE',
      'product_compatibility_reviewed':True,'product':'TEST_SPOT','maturity':'spot','quote_type':'midpoint'}},
   'calendar_sources':{'fixture':{'close_semantics_reviewed':True}}}
 def calc(self):return validate_pair(self.a,self.r,self.c,self.p)
 def test_valid_zero_basis(self):self.assertEqual(self.calc()['price_deviation_bp'],0)
 def test_midpoint(self):self.assertEqual(self.calc()['reference_midpoint_eur'],80)
 def test_bid_price_spread(self):self.assertEqual(self.calc()['bid_price_spread_eur'],20)
 def test_positive_premium(self):
  self.a['auction_price_eur_per_tco2']='80.08';self.assertAlmostEqual(self.calc()['price_deviation_bp'],10)
 def test_naive_timestamp_rejected(self):
  self.r['reference_timestamp']='2024-01-04T10:00:00'
  with self.assertRaisesRegex(ValueError,'timezone'):self.calc()
 def test_future_reference(self):
  self.r['reference_timestamp']='2024-01-04T10:00:01Z'
  with self.assertRaisesRegex(ValueError,'after'):self.calc()
 def test_stale_reference(self):
  self.r['reference_timestamp']='2024-01-04T09:58:59Z'
  with self.assertRaisesRegex(ValueError,'stale'):self.calc()
 def test_futures_not_spot(self):
  self.r['reference_maturity']='December'
  with self.assertRaisesRegex(ValueError,'maturity'):self.calc()
 def test_close_not_accepted(self):
  self.r['reference_quote_type']='daily_close'
  with self.assertRaisesRegex(ValueError,'midpoint'):self.calc()
 def test_crossed_quote(self):
  self.r['reference_bid_eur']='82'
  with self.assertRaisesRegex(ValueError,'crossed'):self.calc()
 def test_nan(self):
  self.r['reference_ask_eur']='nan'
  with self.assertRaisesRegex(ValueError,'nonfinite'):self.calc()
 def test_missing_data_not_zero_result(self):
  s,_,_=gate([self.a],[],[],{'status':'UNLOCKED'});self.assertEqual(s['eligible_pairs'],0);self.assertIsNone(s['effect_estimates'])
 def test_duplicate_reference(self):
  with self.assertRaisesRegex(ValueError,'duplicate'):gate([self.a],[self.r,self.r],[self.c],self.p)
 def test_unmatched(self):
  self.r['auction_id']='OTHER'
  with self.assertRaisesRegex(ValueError,'unmatched'):gate([self.a],[self.r],[self.c],self.p)
 def test_calendar_required(self):
  s,_,_=gate([self.a],[self.r],[],self.p);self.assertEqual(s['eligible_pairs'],0)
 def test_unreviewed_rights(self):
  self.p['reference_sources']['fixture']['lawful_access_reviewed']=False
  with self.assertRaisesRegex(ValueError,'unreviewed'):self.calc()
 def test_unlocked(self):
  self.p['status']='DRAFT'
  with self.assertRaisesRegex(ValueError,'not_locked'):self.calc()
 def test_zero_sd_allowed(self):
  self.a['sd_B']='0';self.assertEqual(self.calc()['x_bid_log1p'],0)
 def test_dst_offset_conversion(self):
  self.assertEqual(timestamp('2024-07-04T11:00:00+02:00'),timestamp('2024-07-04T09:00:00Z'))
 def test_wrong_date(self):
  self.a['auction_date']='2024-01-05'
  with self.assertRaisesRegex(ValueError,'date_mismatch'):self.calc()
if __name__=='__main__':unittest.main(verbosity=2)
