#!/usr/bin/env python

import unittest
from convert_data_to_json import convert_full_county_name

class test_convert_data_to_json(unittest.TestCase):

   def test_convert_full_county_name_AL1(self):
      self.assertEqual(
          convert_full_county_name("Autauga County, AL"),
          "AL Autauga")

   def test_convert_full_county_name_AL2(self):
        self.assertEqual(
            convert_full_county_name("Baldwin County, AL"),
            "AL Baldwin")

   def test_convert_full_county_name_CA1(self):
        self.assertEqual(
            convert_full_county_name("Yolo County, CA"),
            "CA Yolo")
        
   def test_convert_full_county_name_LA1(self):
        self.assertEqual(
            convert_full_county_name("Acadia Parish, LA"),
            "LA Acadia")

   def test_convert_full_county_name_DC(self):
        self.assertEqual(
            convert_full_county_name("District of Columbia, DC"),
            "DC District of Columbia")

   def test_convert_full_county_name_AK1(self):
        self.assertEqual(
            convert_full_county_name("Aleutians East Borough, AK"),
                                     "AK Aleutians East")

   def test_convert_full_county_name_AK2(self):
        self.assertEqual(
            convert_full_county_name("Aleutians West Census Area, AK"),
                                     "AK Aleutians West")

   def test_convert_full_county_name_AK3(self):
        self.assertEqual(
            convert_full_county_name("Anchorage Municipality, AK"),
                                     "AK Anchorage")

   def test_convert_full_county_name_AK4(self):
        self.assertEqual(
            convert_full_county_name("Juneau City and Borough, AK"),
                                     "AK Juneau")

           
if __name__=="__main__":
    unittest.main()

