################################################
####### Pico Pong 2021 by Jerzy Jasonek ########
#######        version 1.0              ########
################################################

from machine import Pin, I2C, ADC
from ssd1306 import SSD1306_I2C
import framebuf
from utime import sleep
from random import randint

###################################   Hardware Settings
WIDTH  = 128                                         
HEIGHT = 64
i2c = I2C(1, scl = Pin(3), sda = Pin(2), freq=400000)
oled = SSD1306_I2C(WIDTH, HEIGHT, i2c)

Pot = ADC(26)
Pot2 = ADC(27)
conversion_factor = 3.3 / (65535) # Conversion from Pin read to proper voltage
button = machine.Pin(16, machine.Pin.IN, machine.Pin.PULL_DOWN)
start_button = machine.Pin(15, machine.Pin.IN, machine.Pin.PULL_DOWN)

global level1, level2,level3
level1 = machine.Pin(14, machine.Pin.OUT)
level2 = machine.Pin(13, machine.Pin.OUT)
level3 = machine.Pin(11, machine.Pin.OUT)

###################################   Game Settings
one_player_game = True # training mode - you control player2
one_player_game_score = 0
game_over = False

#ball = bytearray(b'?\x00\x7f\x80\xff\xc0\xff\xc0\xff\xc0\xff\xc0\xff\xc0\xff\xc0\x7f\x80?\x00')
ball = bytearray(b'x\xfc\xfc\xfc\xfcx')
ball_x = 1
ball_y = 1

player1 = bytearray(b'\xe0\xe0\xe0\xe0\xe0\xe0\xe0\xe0\xe0\xe0\xe0\xe0\xe0\xe0\xe0\xe0\xe0\xe0\xe0\xe0')
player1X = 5
player1Y = int((HEIGHT-20)/2)

player2X = WIDTH-8
player2Y = int((HEIGHT-20)/2)

player1_score = 0
player2_score = 0

ball_buff = framebuf.FrameBuffer(ball, 6, 6, framebuf.MONO_HLSB)

player1_buff = framebuf.FrameBuffer(player1, 3, 20, framebuf.MONO_HLSB)

player2_buff = framebuf.FrameBuffer(player1, 3, 20, framebuf.MONO_HLSB)

global level
level = 1
level1.value(0)
level2.value(0)
level3.value(0)

global start
start = False

###################################   Function
def button_handler(pin):
    global level
    level +=1
    if level == 4:
        level=1
        
def button_start(pin):
    global start
    if not start:
        start = True
    
button.irq(trigger=machine.Pin.IRQ_RISING, handler=button_handler)
start_button.irq(trigger=machine.Pin.IRQ_RISING, handler=button_start)

def check_level(level):
    global level1, level2,level3
    if level == 1:
        level1.value(1)
        level2.value(0)
        level3.value(0)
    elif level == 2:
        level1.value(1)
        level2.value(1)
        level3.value(0)
    elif level == 3:
        level1.value(1)
        level2.value(1)
        level3.value(1)

#Map function        
def convert(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def set_ball_y(y, playerY):
    if (y >= playerY and y <= playerY+4) or (y >= playerY+16 and y <= playerY+20):
        return 2
    elif y >= playerY+8 and y <= playerY+12:
        return 0
    else:
        return 1


###################################   Start Screen

oled.fill(0)
x = int((WIDTH-4)/2)
y = int((HEIGHT-4)/2)
oled.text('Pico Pong 2021', 10,21)
oled.text('by Jerzy Jasonek', 0,41)

oled.show()

check_level(level)

sleep(2)

###################################   Game loop
while not game_over:
    check_level(level)
    if start:
        #update player position
        if not one_player_game:
            player1Y = (Pot.read_u16() * conversion_factor)
            player1Y = convert(player1Y, 0, 3.3, 0, 44)
        else:
            player1Y = y-10
        
        player2Y = (Pot2.read_u16() * conversion_factor) 
        player2Y = convert(player2Y, 0, 3.3, 0, 44)
        
        #draw screen
        oled.fill(0)
        oled.text(str(player1_score), 40,3)
        oled.text(str(player2_score), 88,3)
        oled.blit(ball_buff, x, y)
        oled.blit(player1_buff, player1X, int(player1Y))
        oled.blit(player2_buff, player2X, int(player2Y))
        if one_player_game:
            oled.text('Score:'+str(one_player_game_score), 25,55)
        
        oled.show()
        
        #check collinsion with z wall
        if y > HEIGHT-6 or y < 0:
            ball_y *= -1
            
            
        if x < 0 or x > WIDTH-6:
            if x < 0:
                player2_score +=1
            else:
                player1_score +=1
            x = int((WIDTH-4)/2)
            y = int((HEIGHT-4)/2)
            ball_x *= -1
            if player1_score == 15 or player2_score == 15:
                game_over = True
            else:
             sleep(1)

        #collision with player       
        if player1X+3 <=x and player1X+4 >=x and player1Y-1 <= y and player1Y+21 >= y:
            ball_x *= -1
            ball_y = set_ball_y(y, player1Y)
            if one_player_game:
                ball_y = randint(0,2)
                
        if player2X-5 <= x and player2X-4 >= x and player2Y-1 <= y and player2Y+21 >= y:
            ball_x *= -1
            ball_y = set_ball_y(y, player2Y)
            if one_player_game:
                one_player_game_score +=level
                
            
        x += ball_x*level
        y += ball_y*level
    

###################################   Game over screen
oled.fill(0)
oled.text(str(player1_score), 40,3)
oled.text(str(player2_score), 88,3)
if one_player_game:
            oled.text('Score:'+str(one_player_game_score), 25,55)
oled.text('Game over', 30,31)
oled.show()
