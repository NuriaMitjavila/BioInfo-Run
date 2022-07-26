__author__ = "Núria and Mònica"

import os
import sys
import pygame
import random
from pygame import *
from time import time, sleep
pygame.init()

scr_size = (width,height) = (600,200)                               # the size of the screen game
FPS = 60
gravity = 0.6
black = (0,0,0)
white = (255,255,255)
background_col = (210,235,235)                                      # the colour of the background
high_score = 0                                                      # the high score of the game
screen = pygame.display.set_mode(scr_size)
clock = pygame.time.Clock()
pygame.display.set_caption("Girl Run Videogame, Núria and Mònica")  # title of the game
jump_sound = pygame.mixer.Sound('arxius/saltar.wav')                # sound used when you jump
die_sound = pygame.mixer.Sound('arxius/mario_mort.wav')             # sound used when you die
checkPoint_sound = pygame.mixer.Sound('arxius/smb_coin.wav')        # sound used when you arrive at 100 points
win_sound = pygame.mixer.Sound('arxius/mariofinal.wav')             # sound used when you arrive at 200 points
inici_sound = pygame.mixer.Sound('arxius/marioinici.wav')           # sound used when you start

def load_image(name, sizex=-1, sizey=-1, colorkey=None):            # loading images from the directory
    fullname = os.path.join('arxius', name)                         # load the image from the library desktop
    image = pygame.image.load(fullname)
    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey, RLEACCEL)
    if sizex != -1 or sizey != -1:
        image = pygame.transform.scale(image, (sizex, sizey))       # change scale if needed
    return (image, image.get_rect())                                # return the final image once is in scale

def load_sprite_sheet(sheetname, nx, ny, scalex = -1, scaley = -1, colorkey = None):
    fullname = os.path.join('arxius',sheetname)                     # load all the images from the library desktop
    sheet = pygame.image.load(fullname)
    sheet = sheet.convert()
    sheet_rect = sheet.get_rect()
    arxius = []
    sizex = sheet_rect.width/nx
    sizey = sheet_rect.height/ny
    for i in range(0,ny):
        for j in range(0,nx):
            rect = pygame.Rect((j*sizex,i*sizey,sizex,sizey))
            image = pygame.Surface(rect.size)
            image = image.convert()
            image.blit(sheet,(0,0),rect)
            if colorkey is not None:
                if colorkey is -1:
                    colorkey = image.get_at((0,0))
                image.set_colorkey(colorkey,RLEACCEL)
            if scalex != -1 or scaley != -1:
                image = pygame.transform.scale(image,(scalex,scaley))
            arxius.append(image)
    sprite_rect = arxius[0].get_rect()
    return arxius,sprite_rect                                       # return the sprites from the desktop library

def disp_perduda(retbutton_image,gameover_image):                   # define what to display when losing
    retbutton_rect = retbutton_image.get_rect()
    retbutton_rect.centerx = width / 2
    retbutton_rect.top = height*0.55
    gameover_rect = gameover_image.get_rect()
    gameover_rect.centerx = width / 2
    gameover_rect.centery = height*0.50
    screen.blit(retbutton_image, retbutton_rect)
    screen.blit(gameover_image, gameover_rect)

def disp_guanyada(imatge_victoria):                                 # define what to display when winning
    rectan_guanyada = imatge_victoria.get_rect() 
    rectan_guanyada.centerx = width / 2
    rectan_guanyada.centery = height*0.50
    screen.blit(imatge_victoria, rectan_guanyada)

def extractDigits(numero):                                          # count the score while you are playing
    if numero > -1:
        digits = []
        i = 0
        while(numero/10 != 0):
            digits.append(numero%10)
            numero = int(numero/10)
        digits.append(numero%10)
        for i in range(len(digits),5):
            digits.append(0)
        digits.reverse()
        return digits

class Girl():                                                       # loard the girl to play the game
    def __init__(self,sizex=-1,sizey=-1):
        self.images,self.rect = load_sprite_sheet('noiadino.png',5,1,sizex,sizey,-1) #mides i càrrega
        self.images1,self.rect1 = load_sprite_sheet('nena_estirada.png',2,1,30,sizey,-1) #mides i càrrega
        self.rect.bottom = int(0.98*height)
        self.rect.left = width/15
        self.image = self.images[0]
        self.index = 0
        self.counter = 0
        self.score = 0
        self.estasaltant = False
        self.isDead = False
        self.estaestirat = False
        self.estaparp = False
        self.movement = [0,0]
        self.jumpSpeed = 11.5
        self.stand_pos_width = self.rect.width
        self.duck_pos_width = self.rect1.width

    def draw(self): screen.blit(self.image,self.rect)

    def checkbounds(self):
        if self.rect.bottom > int(0.98*height):
            self.rect.bottom = int(0.98*height)
            self.estasaltant = False

    def update(self):
        if self.estasaltant: self.movement[1] = self.movement[1] + gravity
        if self.estasaltant: self.index = 0
        elif self.estaparp:
            if self.index == 0:
                if self.counter % 400 == 399: self.index = (self.index + 1)%2
            else:
                if self.counter % 20 == 19: self.index = (self.index + 1)%2
        elif self.estaestirat:
            if self.counter % 5 == 0: self.index = (self.index + 1)%2
        else:
            if self.counter % 5 == 0: self.index = (self.index + 1)%2 + 2
        if self.isDead: self.index = 4
        if not self.estaestirat:
            self.image = self.images[self.index]
            self.rect.width = self.stand_pos_width
        else:
            self.image = self.images1[(self.index)%2]
            self.rect.width = self.duck_pos_width
        self.rect = self.rect.move(self.movement)
        self.checkbounds()
        if not self.isDead and self.counter % 7 == 6 and self.estaparp == False:
            self.score += 1
            if self.score == 100 and self.score != 0:
                if pygame.mixer.get_init() != None: checkPoint_sound.play()
        self.counter = (self.counter + 1)

class Apps(pygame.sprite.Sprite):                                 # loard the applications to jump on it
    def __init__(self,speed=5,sizex=-1,sizey=-1):
        pygame.sprite.Sprite.__init__(self,self.containers)
        self.images,self.rect = load_sprite_sheet('app.png',6,2,sizex,sizey,-1)
        self.rect.bottom = int(0.93*height)
        self.rect.left = width + self.rect.width
        self.image = self.images[random.randrange(0,12)]
        self.movement = [-1*speed,0]
    def draw(self): screen.blit(self.image,self.rect)
    def update(self):
        self.rect = self.rect.move(self.movement)
        if self.rect.right < 0: self.kill()

class Birds(pygame.sprite.Sprite):                                 # loard the birds to have it in the ski
    def __init__(self,speed=5,sizex=-1,sizey=-1):
        pygame.sprite.Sprite.__init__(self,self.containers)
        self.images,self.rect = load_sprite_sheet('birds.png',2,1,sizex,sizey,-1)
        self.birds_height = [height*0.83,height*0.75,height*0.60]
        self.rect.centery = self.birds_height[random.randrange(0,3)]
        self.rect.left = width + self.rect.width
        self.image = self.images[0]
        self.movement = [-1*speed,0]
        self.index = 0
        self.counter = 0
    def draw(self): screen.blit(self.image,self.rect)
    def update(self):
        if self.counter % 10 == 0:
            self.index = (self.index+1)%2
        self.image = self.images[self.index]
        self.rect = self.rect.move(self.movement)
        self.counter = (self.counter + 1)
        if self.rect.right < 0: self.kill()

class Ground():                                                    # loard the ground of the game
    def __init__(self,speed=-5):
        self.image,self.rect = load_image('ground.png',-1,-1,-1)
        self.image1,self.rect1 = load_image('ground.png',-1,-1,-1)
        self.rect.bottom = height
        self.rect1.bottom = height
        self.rect1.left = self.rect.right
        self.speed = speed
    def draw(self):
        screen.blit(self.image,self.rect)
        screen.blit(self.image1,self.rect1)
    def update(self):
        self.rect.left += self.speed
        self.rect1.left += self.speed
        if self.rect.right < 0: self.rect.left = self.rect1.right
        if self.rect1.right < 0: self.rect1.left = self.rect.right

class Cloud(pygame.sprite.Sprite):                                  # loard the clouds as DNA in the sky
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self,self.containers)
        self.image,self.rect = load_image('dna.png',int(90*30/42),30,-1)
        self.speed = 1
        self.rect.left = x
        self.rect.top = y
        self.movement = [-1*self.speed,0]
    def draw(self): screen.blit(self.image,self.rect)
    def update(self):
        self.rect = self.rect.move(self.movement)
        if self.rect.right < 0: self.kill()

class Scoreboard():                                                 # loard the socreboard of the game
    def __init__(self,x=-1,y=-1):
        self.score = 0
        self.tempimages,self.temprect = load_sprite_sheet('numbers.png',12,1,11,int(11*6/5),-1)
        self.image = pygame.Surface((55,int(11*6/5)))
        self.rect = self.image.get_rect()
        if x == -1: self.rect.left = width*0.89
        else: self.rect.left = x
        if y == -1: self.rect.top = height*0.1
        else: self.rect.top = y
    def draw(self): screen.blit(self.image,self.rect)
    def update(self,score):
        score_digits = extractDigits(score)
        self.image.fill(background_col)
        for s in score_digits:
            self.image.blit(self.tempimages[s],self.temprect)
            self.temprect.left += self.temprect.width
        self.temprect.left = 0

def introscreen():                                                  # the introduction screen before starting
    temp_girl = Girl(44,47)
    temp_girl.estaparp = True
    gameStart = False
    temp_ground,temp_ground_rect = load_sprite_sheet('ground.png',15,1,-1,-1,-1)
    temp_ground_rect.left = width/20
    temp_ground_rect.bottom = height
    logo,logo_rect = load_image('Level 1.png',400,200,-1)
    logo_rect.centerx = width*0.47
    logo_rect.centery = height*0.559
    while not gameStart:
        if pygame.display.get_surface() == None:
            print("Couldn't load display surface")
            return True
        else:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: return True
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                        temp_girl.estasaltant = True
                        temp_girl.estaparp = False
                        temp_girl.movement[1] = -1*temp_girl.jumpSpeed
        temp_girl.update()
        if pygame.display.get_surface() != None:
            screen.fill(background_col)
            screen.blit(temp_ground[0],temp_ground_rect)
            if temp_girl.estaparp: screen.blit(logo,logo_rect)
            temp_girl.draw()
            pygame.display.update()
        clock.tick(FPS)
        if temp_girl.estasaltant == False and temp_girl.estaparp == False: gameStart = True

def gameplay():                                                     # how to roal and start the videogame
    global high_score
    gamespeed = 4
    startMenu = False 
    PERDUT = False
    gameWin = False
    gameQuit = False
    playerGirl = Girl(44,47)
    new_ground = Ground(-1*gamespeed)
    scb = Scoreboard()
    highsc = Scoreboard(width*0.78)
    counter = 0
    cacti = pygame.sprite.Group()
    birds = pygame.sprite.Group()
    clouds = pygame.sprite.Group()
    last_obstacle = pygame.sprite.Group()
    Apps.containers = cacti
    Birds.containers = birds
    Cloud.containers = clouds
    retbutton_image,retbutton_rect = load_image('replay_button.png',35,31,-1)
    gameover_image,gameover_rect = load_image('game_over1.png',260,150,-1)
    imatge_victoria,rectan_guanyada = load_image('Final3.png',600,200,-1)
    temp_images,temp_rect = load_sprite_sheet('numbers.png',12,1,11,int(11*6/5),-1)
    HI_image = pygame.Surface((22,int(11*6/5)))
    HI_rect = HI_image.get_rect()
    HI_image.fill(background_col)
    HI_image.blit(temp_images[10],temp_rect)
    temp_rect.left += temp_rect.width
    HI_image.blit(temp_images[11],temp_rect)
    HI_rect.top = height*0.1
    HI_rect.left = width*0.73

    while not gameQuit:                                             # meanwhile you are not die
        while startMenu: pass
        if pygame.mixer.get_init() != None: inici_sound.play()
        while not PERDUT and not gameWin:
            if pygame.display.get_surface() == None:
                print("Couldn't load display surface")
                gameQuit = True
                PERDUT = True
            else:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        gameQuit = True
                        PERDUT = True
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                            if playerGirl.rect.bottom == int(0.98*height):
                                playerGirl.estasaltant = True
                                if pygame.mixer.get_init() != None: jump_sound.play()
                                playerGirl.movement[1] = -1*playerGirl.jumpSpeed
                        if event.key == pygame.K_DOWN:
                            if not (playerGirl.estasaltant and playerGirl.isDead): playerGirl.estaestirat = True
                    if event.type == pygame.KEYUP:
                        if event.key == pygame.K_DOWN: playerGirl.estaestirat = False

            for c in cacti:
                c.movement[0] = -1*gamespeed
                if pygame.sprite.collide_mask(playerGirl,c):
                    playerGirl.isDead = True
                    if pygame.mixer.get_init() != None: die_sound.play()

            for p in birds:
                p.movement[0] = -1*gamespeed
                if pygame.sprite.collide_mask(playerGirl,p):
                    playerGirl.isDead = True
                    if pygame.mixer.get_init() != None: die_sound.play()

            if len(cacti) < 2:
                if len(cacti) == 0:
                    last_obstacle.empty()
                    last_obstacle.add(Apps(gamespeed,40,40))
                else:
                    for l in last_obstacle:
                        if l.rect.right < width*0.7 and random.randrange(0,50) == 10:
                            last_obstacle.empty()
                            last_obstacle.add(Apps(gamespeed, 40, 40))

            if len(birds) == 0 and random.randrange(0,200) == 10 and counter > 500:
                for l in last_obstacle:
                    if l.rect.right < width*0.8:
                        last_obstacle.empty()
                        last_obstacle.add(Birds(gamespeed, 46, 40))

            if len(clouds) < 5 and random.randrange(0,300) == 10: Cloud(width,random.randrange(height/5,height/2))

            playerGirl.update()
            cacti.update()
            birds.update()
            clouds.update()
            new_ground.update()
            scb.update(playerGirl.score)
            highsc.update(high_score)
            if playerGirl.score == 200: gameWin = True
            if pygame.display.get_surface() != None:
                screen.fill(background_col)
                new_ground.draw()
                clouds.draw(screen)
                scb.draw()
                if high_score != 0:
                    highsc.draw()
                    screen.blit(HI_image,HI_rect)
                cacti.draw(screen)
                birds.draw(screen)
                playerGirl.draw()
                pygame.display.update()
            clock.tick(FPS)

            if playerGirl.isDead: #if the girl has died, stop the game
                PERDUT = True
                if playerGirl.score > high_score: high_score = playerGirl.score
            if counter%700 == 699: #increase speed
                new_ground.speed -= 1
                gamespeed += 1
            counter = (counter + 1) #add 1 to the counter
        if gameQuit: break

        while PERDUT:                                               # if you die in the videogame
            if pygame.display.get_surface() == None:
                print("Couldn't load display surface")
                gameQuit = True
                PERDUT = False
            else:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        gameQuit = True
                        PERDUT = False
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            gameQuit = True
                            PERDUT = False
                        if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                            PERDUT = False
                            gameplay()
            highsc.update(high_score)
            if pygame.display.get_surface() != None:
                disp_perduda(retbutton_image,gameover_image)
                if high_score != 0:
                    highsc.draw()
                    screen.blit(HI_image,HI_rect)
                pygame.display.update()
            clock.tick(FPS)

        while gameWin:                                              # if you arrive to 200 points you win the game
            if pygame.mixer.get_init() != None: win_sound.play()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    gameQuit = True
                    PERDUT = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        gameQuit = True
                        PERDUT = False
                    if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                        PERDUT = False
                        gameplay()
            if pygame.display.get_surface() != None:
                disp_guanyada(imatge_victoria)
                pygame.display.update()
                sleep(4).pygame.quit()
    pygame.quit()
    quit()

def main():
    isGameQuit = introscreen()
    if not isGameQuit: gameplay()
main()
