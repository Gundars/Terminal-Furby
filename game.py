#! /usr/bin/python

import curses
import sys
import pdb
import time
from math import sin, cos, pi
import random
import traceback
import datetime

dex=40
circle_coords = {}
circle_coords_o = [] 								#for wrong arc bug
circle_coords_o_current = [] 						#defines all current movable arc coords, for enemy collision
center = []											#@todo: make dynamic
enemy_counter = 0
enemies = {} 										#all coordinate data
#enemy_indexes={}									#current index in coordinates
enemy_timer = datetime.datetime.now()
score = [0,0] 										#score+ , score-
screen_h = 0
screen_w = 0

def fillwin(w, c):
	y, x = w.getmaxyx()
	s = c * (x - 1)
	for l in range(y):
		w.addstr(l, 0, s)

def start_curses():
	global center
	'''Init curses, return window object'''
	stdscr = curses.initscr()
	screen_hf,screen_wf = stdscr.getmaxyx()
	center = [round(screen_hf/2),round(screen_wf/2)]
	curses.noecho()
	stdscr.nodelay(True) 							#Do not pause main loop waiting for u input
	stdscr.keypad(True)
	curses.curs_set(0)
	curses.start_color()
	curses.use_default_colors()
	stdscr.clear() 									# Clear screen
	fillwin(stdscr, ' ') 							#Mark main screen
	stdscr.refresh()
	return stdscr

def end_curses(stdscr):
	#End on double touch
	stdscr.touchwin()
	stdscr.refresh()
	stdscr.getch()
	stdscr.touchwin()
	stdscr.refresh()
	stdscr.getch()

	curses.nocbreak()
	stdscr.keypad(False)
	curses.echo()
	curses.endwin()

def update_main(stdscr):
	global center
	stdscr.addstr(0, center[1], str(time.time()))
	stdscr.refresh()

def update_main_center(stdscr):
	global center
	stdscr.addstr(center[0], center[1]-3,'٩͡[๏̯͡๏]۶')
	stdscr.refresh()

def update_score():
	global center
	stdscr.addstr(2, center[1]-2,"SCORE: good:"+str(score[0])+", bad:"+str(score[1]))
	stdscr.refresh()

def update_dex(stdscr):
	global dex,center
	stdscr.addstr(1, center[1],'DEX: '+str(dex))
	stdscr.refresh()

def make_circle():
	global circle_coords,circle_coords_o,center
	radius = 7
	circle={}
	for i in range(0,359):
		x = center[1]+(cos(i*pi/180)*radius)
		y = center[0]+(sin(i*pi/180)*radius)
		v = [round(x),round(y)]
		if v not in circle.values():
			circle[i] = v
			circle_coords_o.append(v)
	circle_coords = circle

def draw_circle(stdscr):
	global dex,circle_coords,circle_coords_o,circle_coords_o_current
	total_arcp = len(circle_coords);
	needed_arcp = round(total_arcp/2) 				#for 180 degrees / 3?radians
	dex_initial = dex
	circle_coords_o_current	= []					#reset global currents

	if dex+needed_arcp > total_arcp: 				#big side
		leftover_arcpoints = (dex+needed_arcp)-total_arcp
		for i,x in enumerate(circle_coords_o):
			if (dex <= i <= total_arcp) or (0 <= i <= leftover_arcpoints):
				stdscr.addstr(x[1], x[0],"▒")
				circle_coords_o_current.append([x[1], x[0]])
			else:
				stdscr.addstr(x[1], x[0],' ')
	elif dex+needed_arcp <= total_arcp:				#small side
		for i,x in enumerate(circle_coords_o):
			if (dex <= i <= dex_initial+needed_arcp):
				stdscr.addstr(x[1], x[0],"▒")
				circle_coords_o_current.append([x[1], x[0]])
			else:
		 		stdscr.addstr(x[1], x[0],' ')	
	stdscr.refresh()

def handle_key_events(stdscr):
	global dex,circle_coords
	c = stdscr.getch()
	if (c == curses.KEY_UP) or (c == curses.KEY_RIGHT):
		dex += 1
		if dex >= len(circle_coords): 				#outside large boundry
			dex=0;
	elif (c == curses.KEY_DOWN) or (c == curses.KEY_LEFT):
		dex -= 1
		if dex <= -1: #outside small boundry
			dex=len(circle_coords);

def get_new_enemy_coordinates(): 
	global center
	e1m = [random.choice([0,center[0]*2]),random.choice(range(0,center[1]*2))]
	coords = [];
	distance_y = center[0]-e1m[0]
	distance_x = center[1]-e1m[1]
	steps = max(e1m[1],e1m[0],center[1],center[0])
	for i in range(0,steps):
		e1m[0]+=(distance_y/steps)
		e1m[1]+=(distance_x/steps)
		coords.append([round(e1m[0]),round(e1m[1])])
	return coords;

def launch_enemies():
	global enemies, enemy_timer, circle_coords_o_current, score

	stop = datetime.datetime.now()
	elapsed = stop - enemy_timer
	if elapsed > datetime.timedelta(seconds=0.04):

		if len(enemies)<3:
			enemies[len(enemies)+1] = get_new_enemy_coordinates()
		
		for enemy_i,enemy in enemies.items():		#loop all enemies

			leftovers = len(enemies[enemy_i])
			if leftovers>1:
				stdscr.addstr(enemy[1][0],enemy[1][1],"✇")#this step
				stdscr.addstr(enemy[0][0],enemy[0][1],' ')#revert previous move

				# collides with shield
				if [enemy[1][0],enemy[1][1]] in circle_coords_o_current: #@todo: swap x and y positions
					score[0] += 1 # increase positive score here

					# restart enemy
					enemies[enemy_i] = get_new_enemy_coordinates()

				del enemies[enemy_i][0]	#delete previous move, making 1 the new 0 and so on
			else:
				score[1] += 1 # increase negative score here

				#restart enemy
				enemies[enemy_i] = get_new_enemy_coordinates()
		

		stdscr.refresh()
		enemy_timer = datetime.datetime.now() #reset timer
			
				
		
def game_loop(stdscr):
	'''Main Game loop'''
	make_circle()
	update_main_center(stdscr)

	while True:
		#update_main(stdscr)
		handle_key_events(stdscr)
		#update_dex(stdscr)
		draw_circle(stdscr)
		launch_enemies()
		update_main_center(stdscr)
		update_score()
			

try:
	stdscr = start_curses()
	event, score = game_loop(stdscr)
	print("DBG Stopping game, end of game loop");
	end_curses(stdscr)
except OSError as err:
	end_curses(stdscr)
	print("OS error: {0}".format(err))
except ValueError:
	end_curses(stdscr)
	print("Could not convert data to an integer.")
except:
	end_curses(stdscr)
	print("Unexpected error:", sys.exc_info()[0])
	raise
