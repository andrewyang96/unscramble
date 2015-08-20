import random
import itertools
import string
import cProfile
from constants import *  # @UnusedWildImport

def load_words():
    """
    Returns a list of valid words. Words are strings of lowercase letters.
    
    Depending on the size of the word list, this function may
    take a while to finish.
    """
    # print "Loading word list from file..." # DEBUG
    # open file
    the_file = open(WORDLIST_FILENAME, 'r', 0)
    # create word_list
    word_list = []
    # word_list: list of strings separated by line
    for line in the_file:
        word_list.append(string.strip(line))
    # print "  ", len(word_list), "words loaded." # DEBUG
    return word_list

def create_simple_dict_from_word_list(word_list):
    """
    DEPRECATED: Use create_dict_from_word_list
    
    word_list (list): a list of words
    
    Returns a dict of {'a':[words starting with 'a'], 'b':[words starting with 'b'], etc...}
    """
    word_dict = {}
    for word in word_list:
        if len(word) in word_dict:
            word_dict[len(word)].append(word)
        else:
            word_dict[len(word)] = [word]
    return word_dict

def create_dict_from_word_list(word_list):
    word_dict = {}
    for word in word_list:
        if len(word) in word_dict:
            if word[0] in word_dict[len(word)]:
                word_dict[len(word)][word[0]].append(word)
            else:
                word_dict[len(word)][word[0]] = [word]
        else:
            word_dict[len(word)] = {word[0] : [word]} # order by word length, then by first letter
    return word_dict

def choose_seq_letters(letter_freqs, num_letters):
    """
    letter_freqs (dict): a dictionary of the frequencies of letters appearing the English language (float)
    num_letters (int): number of letters to be included in the sequence
    
    Raises ValueError if num_letters is not in interval [0,26]
    
    Returns a list of letters
    """
    letter_freqs = letter_freqs.copy()
    if num_letters not in xrange(0,27):
        raise ValueError(str(num_letters) + ' is not in [0,26]')
    elif num_letters == 0:
        return []
    elif num_letters == 26:
        return letter_freqs.keys()
    else:
        letter_list = []
        for i in xrange(num_letters):  # @UnusedVariable
            pos = random.random() * 100
            s = 0
            letter = 'a'
            iter_keys = letter_freqs.iterkeys()
            iter_vals = letter_freqs.itervalues()
            while (s < pos):
                letter = iter_keys.next()
                s += iter_vals.next()
            letter_list.append(letter)
        return letter_list

def find_valid_words(letter_list, word_dict):
    """
    letter_list (list): a list of letters
    word_dict (dict): a dict. Supports simple and advanced word_dicts
    
    Raises ValueError if len(letter_list) < 3
    
    Returns all possible words of length 3 or greater that can be constructed using the letters in letter_list
    """
    if len(letter_list) < 3:
        raise ValueError('letter_list contains less than 3 elements.')
    word_matches  = set() # 3 letter matches only
    prefixes = [] # possible words based off of all 3 letter permutations
    
    iterator = itertools.permutations(letter_list, 3)
    while (True): # find 3 letter matches and prefixes
        try:
            candidate = iterator.next()
            candidate = string.join(candidate, '')
            prefixes.append(candidate) # all candidates are added to prefixes
            if is_word(candidate, word_dict):
                word_matches.add(candidate)
        except StopIteration:
            break
    
    return list(word_matches) + find_valid_words_helper(letter_list, prefixes, word_dict)

def find_valid_words_helper(letter_list, prefixes, word_dict):
    """
    Helper method to find_valid_words.
    """
    if len(letter_list) > len(prefixes[0]):
        candidates = set() # doubles as new prefixes to be passed into recursive call
        for prefix in prefixes:
            letter_dict = Letter_Dict(letter_list)
            for i in xrange(len(prefix)):
                letter_dict.decrement_letter(prefix[i])
            for letter in letter_dict.get_list():
                candidates.add(prefix + letter) # add prefix-letter combination to candidates
        new_word_matches = find_valid_words_helper(letter_list, list(candidates), word_dict)
        for candidate in candidates.copy():
            if not is_word(candidate, word_dict):
                candidates.remove(candidate)
        return list(candidates) + new_word_matches
    else:
        return []

def is_word(candidate, word_dict):
    word_dict_key_type = type(word_dict.values()[0])
    
    if word_dict_key_type == list: # backwards compatibility
        if candidate in word_dict[len(candidate)]:
            return True
        else:
            return False
    else:
        assert (word_dict_key_type == dict)
        if candidate in word_dict[len(candidate)][candidate[0]]:
            return True
        else:
            return False

def find_valid_words_brute_force(letter_list, word_list):
    """
    DEPRECATED: Brute force. Slows especially when len(letter_list > 7. Use with caution.
    letter_list (list): a list of letters
    
    Raises ValueError if len(letter_list) < 3
    
    Returns all possible words of length 3 or greater that can be constructed using the letters in letter_list
    """
    if len(letter_list) < 3:
        raise ValueError('letter_list contains less than 3 elements.')
    word_matches = set()
    for num_letters in xrange(3, len(letter_list)+1):
        hasNext = True
        iterator = itertools.permutations(letter_list, num_letters)
        while hasNext:
            try:
                candidate = iterator.next()
                candidate = string.join(candidate, '')
                if candidate in word_list:
                    word_matches.add(candidate)
            except StopIteration:
                hasNext = False
    return list(word_matches)

class Letter_Dict(object):
    def __init__(self, letter_list):
        self.letter_dict = {}
        for letter in letter_list:
            self.increment_letter(letter)
    
    def increment_letter(self, letter):
        if len(letter) == 1 and letter in string.ascii_lowercase:
            if letter in self.letter_dict:
                self.letter_dict[letter] += 1
            else:
                self.letter_dict[letter] = 1
        else:
            raise ValueError(letter + ' is not a single lowercase letter')
    
    def decrement_letter(self, letter):
        if letter in self.letter_dict:
            if len(letter) == 1 and letter in string.ascii_lowercase:
                if self.letter_dict[letter] > 0:
                    self.letter_dict[letter] -= 1
                    if self.letter_dict[letter] == 0:
                        self.letter_dict.pop(letter) # remove letter if its value is 0
                else:
                    raise ValueError(letter + '\'s value is not a positive number')
            else:
                raise ValueError(letter + ' is not a single lowercase letter')
        else:
            raise KeyError(letter + ' does not exist in letter_dict')
    
    def get_dict(self):
        return self.letter_dict
    
    def get_list(self):
        letter_list = []
        for letter in self.letter_dict:
            for i in xrange(self.letter_dict[letter]):  # @UnusedVariable
                letter_list.append(letter)
        return letter_list

# TEST SUITES
def test_suite_1(): # test choose_seq_letters
        try:
            print choose_seq_letters(LETTER_FREQS, 30) # raise error
        except ValueError:
            print 'Correctly raised error'
           
        print choose_seq_letters(LETTER_FREQS, 0), '0 letters'
        print choose_seq_letters(LETTER_FREQS, 26), '26 letters'

def test_suite_2(): # test Letter_Dict class
    letter_dict = Letter_Dict(['a','b','c','d','e','f'])
    print letter_dict.get_dict(), 'abcdef all 1s'
    letter_dict.increment_letter('g')
    print letter_dict.get_dict(), 'abcdefg all 1s'
    letter_dict.increment_letter('b')
    print letter_dict.get_dict(), 'acdefg all 1s, b is 2'
    letter_dict.decrement_letter('c')
    print letter_dict.get_dict(), 'adefg all 1s, b is 2'
    print letter_dict.get_list()

def test_suite_3(letter_list): # test brute force find_valid_words_brute_force function WITHOUT dictionary optimization
    if len(letter_list) <= 6: # time constraints... if len(letter_list) == 7, then it would take over 30 seconds for completion
        word_list = load_words()
        print 'Starting brute force function'
        bf = find_valid_words_brute_force(letter_list, word_list)
        print bf, len(bf)
    else:
        print 'Quit brute force function to save time.'

def test_suite_4(letter_list): # test optimized find_valid_words function WITH dictionary optimization
    if len(letter_list) <= 8: # time increases drastically at len(letter_list) == 9
        word_list = load_words()
        word_dict = create_simple_dict_from_word_list(word_list)
        print 'Starting optimized function'
        op = find_valid_words(letter_list, word_dict)
        print op, len(op)
    else:
        print 'Quit optimized w/ simple dict to save time.'

def test_suite_5(letter_list): # test optimized find_valid_words function WITH advanced dictionary optimization
    word_list = load_words()
    word_dict = create_dict_from_word_list(word_list)
    print 'Starting optimized function'
    adv = find_valid_words(letter_list, word_dict)
    print adv, len(adv)

def test_suite_6(): # cProfile test suites 3, 4, 5
    global letter_list
    # ['t','r','a','c','e','s']
    # ['b','o','m','b','a','r','d']
    # ['e','a','s','i','n','e','s','s']
    # ['v','a','r','i','a','b','l','e','s']
    letter_list = ['v','a','r','i','a','b','l','e','s']
    print 'Brute Force'
    cProfile.run('test_suite_3(letter_list)')
    print 'Optimized w/ Simple Dict'
    cProfile.run('test_suite_4(letter_list)')
    print 'Optimized w/ Advanced Dict'
    cProfile.run('test_suite_5(letter_list)') # at len(letter_list) == 8, time starts to increase more and more...

def test_suite_7(): # test simple_word_dict
    word_list = load_words()
    word_dict = create_simple_dict_from_word_list(word_list)
    print word_dict[3] # print all three letter words
    print word_dict[4] # print all four letter words

def test_suite_8(): # test word_dict
    word_list = load_words()
    word_dict = create_dict_from_word_list(word_list)
    print word_dict[3]
    print word_dict[3]['a']

def test_suite_final(): # test valid words
    word_dict = create_dict_from_word_list(load_words())
    round_to_num_letters = {1:6, 2:7, 3:8}
    for rnd in xrange(1, len(round_to_num_letters)+1):
        letter_seq = choose_seq_letters(LETTER_FREQS, round_to_num_letters[rnd])
        print 'Your letters for round', rnd, 'are', letter_seq
        all_words = find_valid_words(letter_seq, word_dict)
        print all_words
        print 'There are', len(all_words), 'possible words in this round\n'

if __name__ == '__main__':
    test_suite_final()