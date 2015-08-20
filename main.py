import pygame, sys, os, shutil, math, random  # @UnusedImport
from pygame.locals import *  # @UnusedWildImport
from constants import *  # @UnusedWildImport
from graphics import *  # @UnusedWildImport
import engine

pygame.init()
TOTAL_TIME = 90000

# load screen
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('UN-Scramble')
bg_img = pygame.image.load(BG_IMG_FILENAME)

# load fonts
LETTER_FONT_SIZE = 100
CANDIDATE_FONT_SIZE = 72
GUI_FONT_SIZE = 32
letter_font = pygame.font.Font('freesansbold.ttf', LETTER_FONT_SIZE)
candidate_font = pygame.font.Font('freesansbold.ttf', CANDIDATE_FONT_SIZE)
gui_font = pygame.font.Font('freesansbold.ttf', GUI_FONT_SIZE)

# load letter sequence
def load_letter_seq():
    global letters, word_dict
    word_dict = engine.create_dict_from_word_list(engine.load_words())
    letters = []
    letters = engine.choose_seq_letters(engine.LETTER_FREQS, 6)
    while (len(engine.find_valid_words(letters, word_dict)) < 60): # letter list must contain at least 60 possible words
        letters = engine.choose_seq_letters(engine.LETTER_FREQS, 6)
    # print 'There are', str(len(engine.find_valid_words(letters, word_dict))), 'words in this set' # DEBUG
load_letter_seq()

# set up game
def reset_game():
    global candidate, words, game_started, game_over, show_high_score
    candidate = ''
    words = []
    # use FSM?
    game_started = False
    game_over = 0
    show_high_score = False
reset_game()

# load sounds
def load_sounds():
    global correct_sfx, wrong_sfx, countdown_sfx, go_sfx, STARTRESULTSBGM
    pygame.mixer.music.load(random.choice(BGM_FILENAMES))
    correct_sfx = pygame.mixer.Sound(CORRECT_SFX_FILENAME)
    correct_sfx.set_volume(0.5)
    wrong_sfx = pygame.mixer.Sound(WRONG_SFX_FILENAME)
    wrong_sfx.set_volume(0.5)
    countdown_sfx = pygame.mixer.Sound(COUNTDOWN_SFX_FILENAME)
    go_sfx = pygame.mixer.Sound(GO_SFX_FILENAME)
    STARTRESULTSBGM = pygame.USEREVENT + 1
    pygame.mixer.music.set_endevent(STARTRESULTSBGM)
load_sounds()

# load graphics
def load_graphics():
    global letter_color, list_of_squares
    letter_color = Letter_Color()
    list_of_squares = get_letter_square_arrangement(screen, letters, letter_font, letter_color, LETTER_FONT_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT * 3/4)
    # TODO: shuffle and go! buttons
load_graphics()

# write file
def write_savefile():
    global savefile
    if os.path.exists('scores.dat'):
        savefile = open('scores.dat', 'r+')
    else:
        savefile = open('scores.dat', 'w')
        savefile.write('0')
        savefile.flush()
        savefile = open('scores.dat', 'r+')
write_savefile()

# set up timing... DO THIS LAST
def set_timing():
    global clock, time_remaining, countdown_list
    clock = pygame.time.Clock()
    time_remaining = 3000
    countdown_list = [3,2,1]
set_timing()

while True:
    events = pygame.event.get()
    if not game_over and game_started:
        for square in list_of_squares:
            candidate += square.update(events)
    
    for event in events:
        if event.type == QUIT:
            savefile.close()
            pygame.quit()
            sys.exit()
        elif event.type == KEYDOWN:
            if event.key == K_0 and game_over == 2: # TODO: entirely replace with "restart" button
                load_letter_seq()
                reset_game()
                load_sounds()
                load_graphics()
                write_savefile()
                set_timing()
            if event.key == K_SLASH and game_over == 0:
                random.shuffle(letters)
                list_of_squares = get_letter_square_arrangement(screen, letters, letter_font, letter_color, LETTER_FONT_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT * 3/4)
            if event.key == K_RETURN and game_over == 0:
                for square in list_of_squares:
                    square.deselect()
                if len(candidate) >= 3 and engine.is_word(candidate, word_dict):
                    if candidate in words:
                        letter_color.set_redundant()
                    else:
                        words.insert(0, candidate)
                        letter_color.set_correct()
                    correct_sfx.play()
                else:
                    letter_color.set_wrong()
                    wrong_sfx.play()
                candidate = ''
        elif event.type == STARTRESULTSBGM:
            pygame.mixer.music.load(BGM_RESULTS_FILENAME)
            pygame.mixer.music.play()
            game_over = 2
    
    # draw background
    screen.blit(bg_img, (0,0))
    
    # draw letter squares
    letter_color.update()
    if game_started:
        for square in list_of_squares:
            square.draw_square()
    
    # play sounds
    if game_started:
        if not pygame.mixer.music.get_busy() and (game_over == 0 or game_over == 2):
            pygame.mixer.music.play()
    
    # draw labels
    if game_started:
        render_history(screen, words, gui_font, GUI_FONT_SIZE)
        time_label = gui_font.render('Time: ' + str(int(math.ceil(time_remaining / 1000.))),
                                     True, (0,0,0))
        screen.blit(time_label, (480,10))
        score_label = gui_font.render('Score: ' + str(len(words)), True, (0,0,0))
        screen.blit(score_label, (480,40))
        if not game_over:
            if len(candidate) < 3:
                word_label_color = (255,0,0)
            else:
                word_label_color = (64,0,255)
            word_label = candidate_font.render(candidate, True, word_label_color)
            screen.blit(word_label, (320-word_label.get_width()/2,320))
    
    # keep track of time and countdown label (before game)
    if game_started:
        if time_remaining > 0 and not game_over:
            time_remaining -= clock.tick(60)
            # game_over's statement's clock.tick already handled
        else:
            time_remaining = 0
            time_up_label = candidate_font.render('TIME UP!', True, (255,0,0))
            screen.blit(time_up_label, (320-time_up_label.get_width()/2,320))
            if show_high_score:
                high_score_label = candidate_font.render('HIGH SCORE!', True, (0,255,0))
                screen.blit(high_score_label, (320-high_score_label.get_width()/2,400))
            if not game_over:
                game_over = 1
                pygame.mixer.music.fadeout(1000)
                savefile.seek(0)
                if int(savefile.readline()) < len(words): # update high score
                    newsavefile = open('scores_temp.dat', 'w')
                    newsavefile.write(str(len(words)))
                    savefile.close()
                    newsavefile.close()
                    os.remove('scores.dat')
                    shutil.move('scores_temp.dat', 'scores.dat')
                    savefile = open('scores.dat', 'r+')
                    show_high_score = True
    else:
        if time_remaining > 0:
            if len(countdown_list) > 0 and math.ceil(time_remaining/1000.) == countdown_list[0]:
                countdown_list.remove(math.ceil(time_remaining/1000.))
                countdown_sfx.play()
            countdown_label = letter_font.render(str(int(math.ceil(time_remaining / 1000.))), True, (255,255,255))
            screen.blit(countdown_label, (320-countdown_label.get_width()/2,240-countdown_label.get_height()/2))
            time_remaining -= clock.tick(60)
        else:
            time_remaining = TOTAL_TIME
            game_started = True
            go_sfx.play()
    
    # pygame.display.set_caption('UN-Scramble' + ' ' + str(pygame.mouse.get_pos())) # DEBUG
    pygame.display.set_caption('UN-Scramble')
    pygame.display.update()