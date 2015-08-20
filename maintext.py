import engine
from constants import LETTER_FREQS

if __name__ == '__main__':
    word_dict = engine.create_dict_from_word_list(engine.load_words())
    letter_seq = engine.choose_seq_letters(LETTER_FREQS, 6)
    print 'Six Letter Sample Game w/out Time'
    print 'Quit by typing \'quitnow\''
    print 'Your letters are:', letter_seq
    input_str = ''
    word_matches = set()
    while (input != 'quitnow'):
        input_str = str(raw_input('Your Word Guess: ')) # enforce letter_seq restrictions
        if engine.is_word(input_str, word_dict):
            if input_str in word_matches:
                print input_str, 'is already in the correct list'
            else:
                print input_str, 'is a word'
                word_matches.add(input_str)
        else:
            print input_str, 'is NOT a word!'
    
    print 'Words:', list(word_matches)
    print 'Score:', len(word_matches)