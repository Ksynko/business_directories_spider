import unittest
from matcher import Matcher 

class MatcherTests(unittest.TestCase):

    def test_filter_noise_words(self):
        """Test that the various noise words are correctly removed from a string"""
        test_string = "THE ADAM LTD BOB LIMITED FT/AS T/AS CLAIRE T/A T/S DAVE PLC"
        expected_result = "ADAM BOB CLAIRE DAVE"
        self.assertEqual(Matcher.filter_noise_words(test_string), expected_result)

    def test_preprocess(self):
        """
        Test that the preprocess step sets up all the variations of the test strings correctly
        """
        pass

    def test_replace_and(self):
        """
        Test that & is replaced with AND
        """
        test_string = "BOB & DAVE & CLAIRE"
        expected_result = "BOB AND DAVE AND CLAIRE"
        self.assertEqual(Matcher.replace_and(test_string), expected_result)
        pass

    def test_replace_co(self):
        """
        Test that CO etc is replaced with COMPANY
        """
        test_string = "BOB CO DAVE CO. CLAIRE"
        expected_result = "BOB COMPANY DAVE COMPANY CLAIRE"
        self.assertEqual(Matcher.replace_co(test_string), expected_result)
        pass

    def test_replace_bro(self):
        """ Test that BROS etc is replaced with BROTHERS"""
        test_string = "BOB BROS DAVE BRO. BOB AND DAVE BRO CLAIRE BROTHERS"
        expected_result = "BOB BROTHERS DAVE BROTHERS BOB AND DAVE BROTHERS CLAIRE BROTHERS" 
        self.assertEqual(Matcher.replace_bro(test_string), expected_result)

    def test_remove_special_characters(self):
        """
        Test that anything non-numeric is removed and replaced with a space 
        """
        
        test_string = "BOB-DAVE DAVE_CLAIRE (ELAINE)"
        # I'm not sure that all special characters shoud be removed; start with the above
        expected_result = "BOB DAVE DAVE CLAIRE ELAINE" 
        self.assertEqual(Matcher.remove_special_chars(test_string), expected_result)
        pass

    def test_remove_final_s(self):
        """Remove S if it is the final character"""
        test_string = "BOB DAVES CLAIRES"
        expected_result = "BOB DAVES CLAIRE" 
        self.assertEqual(Matcher.remove_final_s(test_string), expected_result)

    def test_remove_double_spaces(self):
        """Test that all spaces more than one are replaced"""
        test_string = "BOB     DAVE  CLAIRE TOM"
        expected_result = "BOB DAVE CLAIRE TOM"
        self.assertEqual(Matcher.remove_double_spaces(test_string), expected_result)

    def test_canonicise_string(self):
        """Test the function that basically just does all the above"""
        test_string = "BOB    DAVE  & CLAIRE-TOM ELAINE BROS. &  THOMAS JAMES LIMITED T/AS"
        expected_result = "BOB DAVE AND CLAIRE TOM ELAINE BROTHERS AND THOMAS JAME"
        self.assertEqual(Matcher.canonicise_string(test_string), expected_result) 

def main():
    unittest.main()

if __name__ == '__main__':
    main()
