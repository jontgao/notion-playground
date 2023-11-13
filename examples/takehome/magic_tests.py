import unittest
from magic import *

SMALL_EX_FILE = "assets/baby_ratings.csv"

class TestMagic(unittest.TestCase):

    def test_prep_data_from_csv(self):
        expected_dict = {'Book Name': ["Gödel'S Proof",
                                  "Primed To Perform",
                                  "Design Patterns: Elements Of Reusable Object-Oriented Software",
                                  "Primed To Perform"],
                         'Member Name': ["Lauren O",
                                    "Jordan S",
                                    "Alex M",
                                    "David B"],
                         'Rating': [5,
                                    3,
                                    0.5,
                                    4.5]
                        }
        expected = pd.DataFrame(data=expected_dict)
        actual = prep_csv_to_df(SMALL_EX_FILE)

        self.assertTrue(expected.reset_index(drop=True).equals(actual.reset_index(drop=True)))

if __name__ == '__main__':
    unittest.main()