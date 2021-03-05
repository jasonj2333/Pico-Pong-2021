################################################
####### Pico Pong 2021 by Jerzy Jasonek ########
#######        version 0.1              ########
#######   This is alfa simple version   ########
####### Check pong and pong 2 version   ########
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

###################################   Game Settings
game_over = False

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

###################################   Function

#Map function        
def convert(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


###################################   Start Screen

oled.fill(0)
x = int((WIDTH-4)/2)
y = int((HEIGHT-4)/2)
oled.text('Pico Pong 2021', 10,21)
oled.text('by Jerzy Jasonek', 0,41)

oled.show()

sleep(2)

###################################   Game loop
while not game_over:
        #update player position
        player1Y = (Pot.read_u16() * conversion_factor)
        player1Y = convert(player1Y, 0, 3.3, 0, 44)
       
        
        player2Y = (Pot2.read_u16() * conversion_factor) 
        player2Y = convert(player2Y, 0, 3.3, 0, 44)
        
        #draw screen
        oled.fill(0)
        oled.text(str(player1_score), 40,3)
        oled.text(str(player2_score), 88,3)
        oled.blit(ball_buff, x, y)
        oled.blit(player1_buff, player1X, int(player1Y))
        oled.blit(player2_buff, player2X, int(player2Y))
        
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
    
                
        if player2X-5 <= x and player2X-4 >= x and player2Y-1 <= y and player2Y+21 >= y:
            ball_x *= -1
                
            
        x += ball_x
        y += ball_y
    

###################################   Game over screen
oled.fill(0)
oled.text(str(player1_score), 40,3)
oled.text(str(player2_score), 88,3)
oled.text('Game over', 30,31)
oled.show()
