import pygame
from pygame.locals import * # @UnusedWildImport
import string

KEY_INPUT_DICT = {6 : {0:K_q, 1:K_w, 2:K_e, 3:K_a, 4:K_s, 5:K_d},
                  7 : {0:K_q, 1:K_w, 2:K_e, 3:K_r, 4:K_a, 5:K_s, 6:K_d},
                  8 : {0:K_q, 1:K_w, 2:K_e, 3:K_r, 4:K_a, 5:K_s, 6:K_d, 7:K_f}}

class Letter_Square(object):
    def __init__(self, surface, rect, pos, num_letters, letter_font, letter, letter_color, bg_color=(0,0,0), mouseover_bg_color = (0,0,255), select_bg_color = (255,64,0)):
        self.surface = surface
        self.rect = rect
        self.pos = pos # index num in letter_list
        self.key_input_dict = KEY_INPUT_DICT[num_letters] # use num_letters
        self.font = letter_font
        self.letter_color = letter_color # Letter_Color object
        if len(letter) != 1 or (letter not in string.ascii_letters):
            raise ValueError(letter + ' is not an ASCII singleton string')
        self.letter = string.upper(letter)
        self.bg_color = bg_color
        self.mouseover_bg_color = mouseover_bg_color
        self.select_bg_color = select_bg_color
        
        self.mouseover = False
        self.selected = False
    
    def __repr__(self):
        return '(' + self.letter + ',' + str(self.pos) + ')'
    
    def update(self, events): # to be called before the main event processing loop
        self.mouseover = self.rect.collidepoint(pygame.mouse.get_pos())
        for event in events:
            if event.type == MOUSEBUTTONDOWN:
                return self.mouse_select()
            elif event.type == KEYDOWN:
                if event.key == self.key_input_dict[self.pos]:
                    return self.key_select()
        return ''
    
    def mouse_select(self):
        if not self.selected:
            self.selected = self.mouseover
            if self.selected:
                return self.get_letter()
        return ''
    
    def key_select(self):
        if not self.selected:
            self.selected = True
            return self.get_letter()
        return ''
    
    def deselect(self):
        self.selected = False
    
    def draw_square(self):
        if self.selected:
            bgcolor = self.select_bg_color
        elif self.mouseover:
            bgcolor = self.mouseover_bg_color
        else:
            bgcolor = self.bg_color
        pygame.draw.rect(self.surface, bgcolor, self.rect)
        text_surface = self.font.render(self.letter, True, self.letter_color.get_color())
        text_rect = text_surface.get_rect()
        y_offset = (self.rect.height - self.font.get_ascent()) / 2
        text_rect.midtop = (self.rect.midtop[0], self.rect.top + y_offset)
        self.surface.blit(text_surface, text_rect)
    
    def set_bg_color(self, color):
        if len(color) != 3:
            raise ValueError(color + ' is not a tuple of length 3')
        self.bg_color = color
    
    def set_letter(self, letter):
        if len(letter) != 1 or (letter not in string.ascii_letters):
            raise ValueError(letter + ' is not an ASCII singleton string')
        self.letter = string.upper(letter)
    
    def get_letter(self):
        return string.lower(self.letter)
    
    def get_rect(self):
        return self.rect


class Letter_Color(object):
    def __init__(self, color_change_duration = 30, neutral_color = (255,255,255), correct_color = (0,255,0),
                 wrong_color = (255,0,0), redundant_color = (255,255,0)):
        self.color_change_duration = color_change_duration # frames
        self.neutral_color = neutral_color
        self.correct_color = correct_color
        self.wrong_color = wrong_color
        self.redundant_color = redundant_color
        
        self.count = 0
        self.color = neutral_color
    
    def set_correct(self):
        self.color = self.correct_color
        self.count = self.color_change_duration
    
    def set_wrong(self):
        self.color = self.wrong_color
        self.count = self.color_change_duration
    
    def set_redundant(self):
        self.color = self.redundant_color
        self.count = self.color_change_duration
    
    def update(self):
        if self.count > 0:
            self.count -= 1
        else:
            self.count = 0
            self.color = self.neutral_color
    
    def get_color(self):
        return self.color
    
    def get_count(self): # DEBUG
        return self.count


def get_letter_square_arrangement(screen, letter_list, letter_font, letter_color, font_size, screen_width, screen_height): # TODO: extend for more than six squares
    leftmost = (screen_width - 3 * font_size) / 2
    center = (screen_width - font_size) / 2
    rightmost = (screen_width + font_size) / 2
    lower = screen_height / 2 - font_size # upper on the screen
    upper = screen_height / 2 # lower on the screen
    coords_list = [(leftmost,lower), (center,lower), (rightmost,lower), (leftmost,upper), (center,upper), (rightmost,upper)]
    
    letter_seq_dict = dict(zip(coords_list, letter_list))
    result = []
    for coords in letter_seq_dict:
        test_rect = (Rect(coords, (font_size,font_size)))
        result.append(Letter_Square(screen, test_rect, coords_list.index(coords), len(letter_list), letter_font, letter_seq_dict[coords], letter_color))
    return result

def render_history(screen, word_list, font, spacing, color=(0,0,0)):
    x, y = 20,20
    for word in word_list:
        history_label = font.render(word, True, color)
        screen.blit(history_label, (x,y))
        y += spacing