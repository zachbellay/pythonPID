import pygame as pg
from pygame.locals import *
import pygooey
import pylab
import numpy as np
import matplotlib
import matplotlib.backends.backend_agg as agg
import random
import queue
import time

class Ball(pg.sprite.Sprite):
	def __init__(self):
		pg.sprite.Sprite.__init__(self) #call Sprite initializer

		#load in the images (will do it for every instance, which isn't efficient if you have many)
		self.image = pg.image.load("ball.png")
		self.img_x, self.img_y = self.image.get_rect().size
		self.w, self.h = pg.display.get_surface().get_size()
		self.x = self.w/2 - (self.img_x/2)
		self.y = self.h/2 - (self.img_y/2)
		self.rect = self.image.get_rect() #sets the image size
		self.rect.topleft = (self.x,self.y) #sets the image location
		self.x_dest = self.x
		self.y_dest = self.y

		self.err_margin = 0.1

		self.kp=0.2
		self.ki=0.01
		self.kd=0.01

		self.prev_err=0
		self.integral = 0

	# Do PID calculation
	def err(self):
		err=self.x_dest - self.x
		self.integral += err
		self.derivative = err - self.prev_err
		output = self.kp * err + self.ki * self.integral + self.kd * self.derivative
		self.prev_err = err
		return output

	def setDest(self, x, y):
		self.x_dest = x - self.img_x/2
		self.y_dest = y - self.img_y/2

	def set_coefs(self,kp,ki,kd):
		self.kp=kp
		self.ki=ki
		self.kd=kd

	def update(self):
		self.rect.topleft = (self.x, self.h/2 - (self.img_y/2)) #sets the image location

		if abs(self.x_dest-self.x) > self.err_margin:
			dist = self.err()
			self.x += dist
		if self.x <= 600:
			self.x = 600

# Create MatPlotLib figure
def create_figure(x,y):
	pylab.plot(x,y)
	fig = pylab.figure(figsize=[6,6],dpi=100)
	ax = fig.gca()
	ax.plot(x,y)
	c=np.full((1,len(x)), ball.x_dest)[0]
	ax.plot(x,c)
	return fig

# Draw MatPlotLib figure to image and render in pygame
def draw_figure(fig, screen):
	canvas=agg.FigureCanvasAgg(fig)
	canvas.draw()
	renderer=canvas.get_renderer()
	raw_data=renderer.tostring_rgb()
	size=canvas.get_width_height()
	surf=pg.image.fromstring(raw_data, size, "RGB")
	imgrect=surf.get_rect()
	screen.blit(surf,imgrect)
	pg.display.flip()
	pylab.close(fig)

# Do nothing if enter pressed
def textbox_callback(id, final):
    pass


def button_callback():
	try:
		ball.set_coefs(float(entry_0.final),float(entry_2.final),float(entry_2.final))
	except:
		pass

if __name__ == "__main__":
	white=[255,255,255]
	pg.init()
	flags = DOUBLEBUF
	screen=pg.display.set_mode([1400,800], flags)


	widgets=[]

	# Pygooey, create button and text fields within pygame framework
	entry_settings = {
	    "inactive_on_enter" : False,
	    'active':False
	}

	entry_0 = pygooey.TextBox(rect=(10,700,150,30), command=textbox_callback, **entry_settings)
	widgets.append(entry_0)
	entry_1 = pygooey.TextBox(rect=(210,700,150,30), command=textbox_callback, **entry_settings)
	widgets.append(entry_1)
	entry_2 = pygooey.TextBox(rect=(410,700,150,30), command=textbox_callback, **entry_settings)
	widgets.append(entry_2)

	pg.font.init()
	entry_font=pg.font.Font(None, 25)
	kp_text=entry_font.render('kp:', False, white)
	ki_text=entry_font.render('ki:', False, white)
	kd_text=entry_font.render('kd:', False, white)
	screen.blit(kp_text,(70,680))
	screen.blit(ki_text,(270,680))
	screen.blit(kd_text,(470,680))
	

	btn_settings = {
	"clicked_font_color" : (0,0,0),
	"hover_font_color"   : (205,195, 100),
	'font'               : pg.font.Font(None,16),
	'font_color'         : (255,255,255),
	'border_color'       : (0,0,0),
	}

	btn = pygooey.Button(rect=(210,750,105,25), command=button_callback, text='OK', **btn_settings)
	widgets.append(btn)

	# Currently using queue, could be more efficient to simply use a list 
	# So that you don't have to convert from queue to list every iteration

	ball = Ball()
	t=queue.Queue(maxsize=100)
	ylist=queue.Queue(maxsize=100)

	
	running = True
	while running:
		for event in pg.event.get():
			if event.type == pg.QUIT:
				running=False
			if event.type == pg.KEYDOWN:
				if event.key == pg.K_q:
					running=False
			if event.type == pg.MOUSEBUTTONDOWN:
				x_setpoint,y_setpoint = pg.mouse.get_pos()
				if x_setpoint >= 600:
					print(x_setpoint, y_setpoint)
					ball.setDest(x_setpoint,y_setpoint)
			for w in widgets:
				w.get_event(event)
		for w in widgets:
			w.update()
			w.draw(screen)

		
		if t.full():
			t.get()
		if ylist.full():
			ylist.get()
		
		t.put(time.clock())
		ylist.put(ball.x)
		draw_figure(create_figure(list(t.queue),list(ylist.queue)),screen)

		ball.update()

		pg.draw.rect(screen,white,(600,0,800,600))

		screen.blit(ball.image, ball.rect)
		pg.display.update()


	pg.quit()
