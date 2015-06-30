import Levenshtein


class Matcher(object):

    """I can't seem to find a decent library to do this with synonyms, so here we are.
    Match one business name to another, removing noise words, matching on equivalents 
    and so forth."""

    noise_words = ['THE', 'LTD', 'LIMITED', 'FT/AS', 'T/AS', 'T/A', 'T/S', 'PLC', 'TEORANTA']

    @classmethod
    def filter_noise_words(self, string):
        """
        For a given string, return it with all the class noise words removed
        """
        for word in self.noise_words:
            string = string.replace(word, '')
        
        # Normalise the spaces as well, because the above leaves gaps
        return ' '.join(string.split())


    @classmethod
    def remove_double_spaces(self, string):
        """
        For a given string, remove any double spaces.
        The filter above also does this, but anyway
        """
        return ' '.join(string.split())

    @classmethod
    def replace_and(self, string):
        """
        # Replace & with AND  
        """
        return string.replace('&', 'AND')

    @classmethod
    def replace_co(self, string):
        """
        # Replace CO with COMPANY  
        """
        # Probably as easy to do this as a regex:
        string = string.replace(' CO. ', ' COMPANY ')
        string = string.replace(' CO ', ' COMPANY ')
        return string

    @classmethod
    def replace_bro(self, string):
        """
        # Replace BRO etc with BROTHERS  
        """
        # Probably as easy to do this as a regex:
        string = string.replace(' BRO ', ' BROTHERS ')
        string = string.replace(' BRO. ', ' BROTHERS ')
        string = string.replace(' BROS ', ' BROTHERS ')
        string = string.replace(' BROS. ', ' BROTHERS ')
        return string


    @classmethod
    def filter_noise_words(self, string):
        """
        For a given string, return it with all the class noise words removed
        """
        for word in self.noise_words:
            string = string.replace(word, '')
        
        # Normalise the spaces as well, because the above leaves gaps
        return ' '.join(string.split())

    @classmethod
    def remove_special_chars(self, string):
        """
        # Not sure that all special characters should go, but remove
        some of them
        """
        # Probably as easy to do this as a regex:
        string = string.replace('_', ' ')
        string = string.replace('-', ' ')
        string = string.replace('(', '')
        string = string.replace(')', '')
        return string

    @classmethod
    def remove_final_s(self, string):
        """
        If the last character is an S, remove it
        """
        if string[-1] == 'S':
            string = string[0:-1]
        return string

    @classmethod
    def canonicise_string(self, string):
        """
        Run all of the above methods to get a string ready for matching
        """
        string = self.filter_noise_words(string)      
        string = self.remove_final_s(string)
        string = self.remove_special_chars(string)
        string = self.replace_bro(string)
        string = self.replace_co(string)
        string = self.replace_and(string)
        string = self.remove_double_spaces(string)
        return string





    def __init__(self, string_1, string_2):
        """Send in the two strings to be matched"""
        # Always do it in upper case with leading and trailing spaces trimmed
        self.string_1 = string_1.strip().upper()
        self.string_2 = string_2.strip().upper()

    def _preprocess(self):
        """
        Get a final 'canonical' version of the strings ready for matching
        """
        self.string_1_canonical = self.canonicise_string(self.string_1)
        self.string_2_canonical = self.canonicise_string(self.string_2)
        
        pass

    def get_similarity_ratio(self):
        """
        The business end; preprocess the strings to get a final version and return a 
        :returns: TODO

        """
        self._preprocess()
        return Levenshtein.ratio(self.string_1_canonical, self.string_2_canonical)
        
        
