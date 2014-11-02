#!/usr/bin/env python

import sys, os, re
import time

import curses
from curses import panel

import json
import pandas as pd

##
# Text processing functions
from unidecode import unidecode

def strip_unicode(s):
    return "".join(x for x in s if ord(x) < 128)

def force_ascii(s):
    return strip_unicode(unidecode(s))

def clean_and_split(s):
    return force_ascii(s).split("\n")

##
# Selector Menu Class
class SelectorMenu(object):

    MENU_EXIT = "EXIT"
    MENU_CHOSEN = "CHOSEN"
    MENU_SKIP_BACK = "BACK"
    MENU_SKIP_FRWD = "FRWD"

    KEYS_MENU_CHOICE = [curses.KEY_ENTER, ord('\n')]
    KEYS_MENU_EXIT = [27, ord('q')]

    KEYS_CONFIRM_YES = [curses.KEY_ENTER, ord('\n')]
    KEYS_CONFIRM_NO = [27, ord(' '), ord('q')]

    def __init__(self, scr, items, header="",
                 hoffset=0, pad=(0,0),
                 skiplines=1, loc=(0,0), size=None,
                 option0="No Label", close_delay=0.0):
        # Initialize window
        if not size == None:
            self.window = scr.subwin(size[0], size[1], loc[0], loc[1])
        else:
            my, mx = scr.getmaxyx()
            self.window = scr.subwin(my - pad[0] - loc[0], mx - pad[1] - loc[1], loc[0], loc[1])

        self.window.keypad(1)
        # self.panel = panel.new_panel(self.window)
        # self.panel.hide()
        # panel.update_panels()

        # Current position in menu, finalized to choice on enter
        self.position = 0 # start at first entry
        self.choice = None

        # Expect items = [(label, key, keyname)]
        self.KEYS_SPECIAL_CHOICE = {v[1]:i for i,v in enumerate(items) if len(v) > 1}
        self.KEYS_SPECIAL_CHOICE_NAMES = {i:v[2] for i,v in enumerate(items) if len(v) > 2}

        # Menu items, as text
        self.items = [v[0] for v in items]
        self.items = map(clean_and_split, self.items)

        self.header = clean_and_split(header)
        self.skiplines = skiplines
        self.hoffset = hoffset
        self.close_delay = close_delay

    def get_choice(self):
        """Access the last-selected option."""
        return self.choice

    def get_status(self):
        """Exit status, to relay to controlling program for e.g. hard quit."""
        return self.status

    def _navigate(self, n):
        """Move up/down by n items."""
        self.position += n
        if self.position < 0:
            self.position = 0
        elif self.position >= len(self.items):
            self.position = len(self.items)-1

    def _navigate_to(self, pos, mode="sticky"):
        """Move to a target position."""
        if mode == 'loop':
            self.position = int(pos) % len(self.items)
        else: # sticky = default
            self.position = max(0, min(int(pos), len(self.items) - 1))

    def _confirm(self, msg, y, x, keys_yes=KEYS_CONFIRM_YES, keys_no=KEYS_CONFIRM_NO):
        """Display a confirmation dialog of msg at position x,y"""
        self.window.addstr(y, x+self.hoffset, msg, curses.A_NORMAL)

        ret = None
        while True:
            key = self.window.getch()
            if key in keys_yes:
                ret = True
                break
            if key in keys_no:
                ret = False
                break

        # Clear confirm message before return
        self.window.move(y,x)
        self.window.clrtoeol()
        return ret

    def _clip_line(self,line, maxlen):
        if len(line) <= maxlen: return line
        else:                   return line[:(maxlen-3)] + "..."


    def _draw_header(self,y,x):
        """Draw headers. Return next line to draw on."""
        for i, line in enumerate(self.header):
            line = self._clip_line(line, self.width)
            self.window.addstr(y+i, x+self.hoffset, line, curses.A_NORMAL)
        return y+i+1+self.skiplines

    def _draw_items(self,y,x):
        """Draw menu items, with appropriate highlighting. Return next line to draw on."""
        yloc = y
        for i, lines in enumerate(self.items):
            # Highlight current line
            if i == self.position:  mode = curses.A_REVERSE
            elif i == self.choice:  mode = curses.A_UNDERLINE
            else:                   mode = curses.A_NORMAL

            # Construct line prefixes
            prefix = "[%d/%s] " % (i, self.KEYS_SPECIAL_CHOICE_NAMES[i])
            prefixes = [prefix] + [" "*len(prefix)] * (len(lines)-1)

            # Draw lines
            for p,l in zip(prefixes, lines):
                line = self._clip_line(p+l, self.width)
                self.window.addstr(yloc, x+self.hoffset, line, mode)
                yloc += 1

            # Skip lines after entry
            yloc += self.skiplines

        return yloc

    def display(self):
        self.status = None

        # self.panel.top()
        # self.panel.show()
        self.window.clear()
        self.window.border(0)

        by, bx = self.window.getbegyx()
        my, mx = self.window.getmaxyx()
        self.height, self.width = (my - by, mx - bx)

        ##
        # "GUI" loop, refresh on each nav event
        while True:
            self.window.refresh()
            curses.doupdate()

            ##
            # Draw header
            nextline = self._draw_header(1,1)

            ##
            # Draw items
            nextline = self._draw_items(nextline, 1)

            ##
            # Wait for key input; execute command
            key = self.window.getch()

            if key in self.KEYS_MENU_EXIT:
                msg = "Confirm hard exit? (Esc/Enter)"
                if self._confirm(msg, nextline, 1,
                                 keys_yes=self.KEYS_CONFIRM_NO,
                                 keys_no=self.KEYS_CONFIRM_YES):
                    self.status = self.MENU_EXIT
                    break


            # Make choice from menu
            if key in self.KEYS_MENU_CHOICE:
                self.status = self.MENU_CHOSEN
                self.choice = self.position
                break
                # msg = "You chose [%d]. Confirm? (Enter/Esc)" % self.position
                # if self._confirm(msg, nextline, 1):
                #     self.status = self.MENU_CHOSEN
                #     self.choice = self.position
                #     break

            # Quick choice, with number key
            # choose 0,1,...,len(items)
            if key in [ord(str(i)) for i in range(min(len(self.items),10))]:
                idx = int(chr(key))
                self.status = self.MENU_CHOSEN
                self.choice = idx
                self._navigate_to(idx)
                break

            # Quick choice, with special key
            if key in self.KEYS_SPECIAL_CHOICE:
                idx = self.KEYS_SPECIAL_CHOICE[key]
                self.status = self.MENU_CHOSEN
                self.choice = idx
                self._navigate_to(idx)
                break

            # Navigate
            elif key == curses.KEY_UP:
                self._navigate(-1)

            elif key == curses.KEY_DOWN:
                self._navigate(1)

            elif key == curses.KEY_LEFT:
                self.status = self.MENU_SKIP_BACK
                break

            elif key == curses.KEY_RIGHT:
                self.status = self.MENU_SKIP_FRWD
                break


        self.window.refresh()
        curses.doupdate()
        time.sleep(self.close_delay)

        # Cleanup
        self.window.clear()
        self.window.refresh()
        # self.panel.hide()
        # panel.update_panels()
        # curses.doupdate()

def get_init_choice(key, choices, options):
    """Get starting position, given existing annotations."""
    try:
        return options.index(choices[key])
    except KeyError as e:
        return None # key not seen before
    except ValueError as e:
        return None # invalid choice recorded


class SelectorApp(object):

    MAX_ITEMS = 10

    def __init__(self, stdscreen, df, labels, options, continuity=True):
        self.screen = stdscreen
        curses.curs_set(0)

        # curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)
        curses.use_default_colors()

        # Loop over all rows, making selector menu each time
        menus = []
        counter = 0
        for df_idx,row in df.iterrows():
            counter += 1
            header = "Line [%d]:\n\n    >   %s   \n" % (df_idx,row.text)
            menu = SelectorMenu(self.screen, options, header=header,
                                hoffset=1, loc=(1,2), pad=(1,2),
                                close_delay=0.250)
            menus.append((df_idx,menu))

        # Display menus
        loc = 0
        lastmenu = None
        while True:
            df_idx, menu = menus[loc]

            # Show menu
            menu.display()

            status = menu.get_status()
            if status == menu.MENU_EXIT:
                break
            elif status == menu.MENU_SKIP_BACK:
                loc -= 1
            elif status == menu.MENU_SKIP_FRWD:
                loc += 1
            elif status == menu.MENU_CHOSEN: # OK
                # Record annotation
                choices[df.text[df_idx]] = options[menu.get_choice()][0]
                loc += 1
            else:
                loc += 1

            # Break loop
            if (loc >= len(menus) or loc < 0):
                exitmenu = SelectorMenu(self.screen, [], option0="Quit",
                                        loc=(10,10), size=(8, 40),
                                        header="All done? Press Enter to quit,\nor use arrow keys to return.")
                exitmenu.display()
                status = exitmenu.get_status()
                if status in [exitmenu.MENU_CHOSEN, exitmenu.MENU_EXIT]:
                    break
                elif status == exitmenu.MENU_SKIP_BACK:
                    loc = len(menus) - 1 # go back one
                elif status == exitmenu.MENU_SKIP_FRWD:
                    loc = 0 # wrap around

            lastmenu = menu


if __name__ == '__main__':

    infile = sys.argv[1]
    outfile = infile + ".annotated"

    print "Loading data from %s" % infile
    df = pd.read_pickle(infile)
    df = df[df.ntok >= 3]


    options = [("No Label", ord('n'), 'N'),
               ("Sentence", ord(' '), 'SPACE'),
               ("Nonsense/Fragment/Headline", ord('l'), 'L'),
               ("Porn/Explicit/Spam", ord('p'), 'P')]
    choices = {}
    if os.path.isfile(outfile):
        ans = raw_input("Output file found. Resume? [y/n]: ")
        if ans[0].lower() == 'y':
            with open(outfile) as f:
                choices = json.load(f)

    curses.wrapper(SelectorApp, df, choices, options)

    # DEBUG
    print json.dumps(choices, indent=1)

    print "Saving output to %s" % outfile
    with open(outfile, 'w') as f:
        json.dump(choices, f, indent=1)
