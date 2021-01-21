import pygame
import random
import sys
import logging
import os
import traceback

def edit(file, w, h, color):
    image = pygame.image.load(file).convert()
    if color == None:
        image.set_colorkey(image.get_at((0, 0)))
    else:
        image.set_colorkey(color)
    image = pygame.transform.scale(image, (w, h))
    return image

class Room(pygame.sprite.Sprite):
    def __init__(self, file):
        global BROWN
        super().__init__()
        self.image = edit(file, 1000, 600, (255, 255, 255))
        BROWN = self.image.get_at((0, 0))
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)


class Hero(pygame.sprite.Sprite):
    def __init__(self, file1, file2, file3):
        super().__init__(heroes)
        self.image1 = edit(file1, 40, 70, None)
        self.image2 = edit(file2, 40, 70, None)
        self.image3 = edit(file3, 40, 70, None)
        self.mask1 = pygame.mask.from_surface(self.image1)
        self.mask2 = pygame.mask.from_surface(self.image2)
        self.mask3 = pygame.mask.from_surface(self.image3)
        self.mask = self.mask1
        self.image = self.image1
        self.im = self.image
        self.rect = self.image.get_rect()
        self.rect.x = 200
        self.rect.y = 200
        self.view = 1

    def move(self, x, y):
        self.rect.x += x
        self.rect.y += y
        for i in mas[INDEX]:
            if pygame.sprite.collide_mask(self, i) and i not in keys and i not in portals:
                self.rect.x -= x
                self.rect.y -= y
                break
        if self.rect.x > size[0]:
            self.transit(-size[0], 0, g[INDEX]['right'])
        elif self.rect.x < 0:
            self.transit(size[0], 0, g[INDEX]['left'])
        elif self.rect.y > size[1] - 100:
            self.transit(0, -size[1] + 100, g[INDEX]['down'])
        elif self.rect.y < 0:
            self.transit(0, size[1] - 100, g[INDEX]['up'])

    def transit(self, x, y, ind):
        global INDEX
        self.rect.x += x
        self.rect.y += y
        yes = True
        for i in mas[ind]:
            if pygame.sprite.collide_mask(self, i):
                self.rect.x -= x
                self.rect.y -= y
                yes = False
                break
        if yes:
            INDEX = ind

    def rescue(self, group):
        yes = 0
        for i in group:
            if pygame.sprite.collide_mask(self, i) and i not in keys and i not in portals:
                yes = 1
        if not yes:
            return
        dx = [10, -10, 0, 0]
        dy = [0, 0, 10, -10]
        for j in range(4):
            self.rect.x += dx[j]
            self.rect.y += dy[j]
            yes = 0
            for i in group:
                if pygame.sprite.collide_mask(self, i) and i not in keys and i not in portals:
                    yes = 1
            if not yes:
                return
            self.rect.x -= dx[j]
            self.rect.y -= dy[j]

class Door(pygame.sprite.Sprite):
    def __init__(self, file, index, x, y, w, h, rotate):
        super().__init__(mas[index])
        self.i = index
        self.w = w
        self.h = h
        self.file = file
        self.image = edit(file, w, h, (255, 255, 255))
        self.image = pygame.transform.rotate(self.image, rotate)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.mask = pygame.mask.from_surface(self.image)


class Key(pygame.sprite.Sprite):
    def __init__(self, file, index, x, y, w, h, door):
        super().__init__(mas[index])
        keys.append(self)
        self.i = index
        self.image = edit(file, w, h, (255, 255, 255))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.door = door
        self.mask = pygame.mask.from_surface(self.image)

    def to_inventory(self):
        catch_key.play()
        mas[self.i].remove(self)
        inventory.add(self)
        self.image = pygame.transform.scale(self.image, (60, 60))
        self.rect.y = iy
        for i in range(len(saved)):
            if type(saved[i]) == int:
                saved[i] = self
                self.rect.x = ix + i * ixp
                break

    def check(self):
        if pygame.sprite.collide_mask(peng, self) and self.i == INDEX and self not in inventory:
            self.to_inventory()

    def use(self):
        if pygame.sprite.collide_mask(self, self.door) and self.door.i == INDEX:
            open_door.play()
            mas[INDEX].remove(self.door)
            for i in range(len(keys)):
                if keys[i] == self:
                    del keys[i]
                    break
            inventory.remove(self)
            return True
        return False

    def back_to_inventory(self):
        self.rect.x = ix + ixp * moving_key
        self.rect.y = iy

    def to_cursor(self, x, y):
        self.rect.x = x
        self.rect.y = y


class Final_Door(Door):
    def open(self, t):
        if t == 'up':
            self.h -= 1
        elif t == 'down':
            self.h -= 1
            self.rect.y += 1
        self.image = edit(self.file, self.w, self.h, (255, 255, 255))
        


class Form_Key(Key):
    def use(self):
        global FINAL
        if pygame.sprite.collide_mask(self, self.door) and self.door.i == INDEX:
            form_sound.play()
            FINAL += 1
            mas[INDEX].add(self)
            mas[INDEX].remove(self.door)
            self.rect = self.door.rect
            for i in range(len(keys)):
                if keys[i] == self:
                    del keys[i]
                    break
            inventory.remove(self)
            return True
        return False


class Portal(pygame.sprite.Sprite):
    def __init__(self, file, index, x, y, w, h, pair):
        super().__init__(mas[index])
        portals.append(self)
        self.i = index
        self.image = edit(file, w, h, None)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.pair = pair
        self.active = 0
        self.timer = 0
        self.mask = pygame.mask.from_surface(self.image)
        self.timer2 = 0

    def check(self):
        if pygame.sprite.collide_mask(peng, self) and self.i == INDEX:
            if self.active == 0:
                self.activate()
            else:
                
                self.count()
        else:
            if self.active == 1:
                self.reset()
        if peng.view == 0:
            peng.view = 1

    def activate(self):
        self.active = 1

    def reset(self):
        self.active = 0
        self.timer = 0

    def count(self):
        self.timer += 1 / fps
        self.timer2 += 1
        if self.timer2 % 10 < 5:
            peng.view = -1
        else:
            peng.view = 1
        if self.timer >= 2:
            self.teleport()

    def teleport(self):
        global INDEX
        teleport.play()
        INDEX = self.pair.i
        peng.rect.x = self.pair.rect.x
        peng.rect.y = self.pair.rect.y

    def connect(self, other):
        self.pair = other
        other.pair = self


class Button(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, text):
        super().__init__(buttons)
        self.x = x
        self.y = y
        self.h = h
        self.w = w
        self.text = text
        self.image = pygame.Surface((w, h))
        pygame.draw.rect(self.image, (0, 0, 0), (x, y, w, h))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
def format_exception(e):
    exception_list = traceback.format_stack()
    exception_list = exception_list[:-2]
    exception_list.extend(traceback.format_tb(sys.exc_info()[2]))
    exception_list.extend(traceback.format_exception_only(sys.exc_info()[0], sys.exc_info()[1]))

    exception_str = "Traceback (most recent call last):\n"
    exception_str += "".join(exception_list)
    # Removing the last \n
    exception_str = exception_str[:-1]

    return exception_str

if __name__ == '__main__':
     try:
        logging.basicConfig(filename="labirint_log.log", level=logging.INFO)
        pygame.mixer.pre_init(44100, 16, 1, 512)
        pygame.init()
    
        filepath = os.path.abspath("c:\\Users\\aleks\\OneDrive\\Desktop\\project_labirint\\lab_music.mp3")
        pygame.mixer.music.load(filepath)
        pygame.mixer.music.set_volume(0.2)
        pygame.mixer.music.play(-1)

       
        to_button = pygame.mixer.Sound('касание_кнопки.wav')
        press_button = pygame.mixer.Sound('нажатие_на_кнопку.wav')
        catch_key = pygame.mixer.Sound('взятие_ключа.wav')
        open_door = pygame.mixer.Sound('открытие_двери.wav')
        win_sound = pygame.mixer.Sound('победа.wav')
        form_sound = pygame.mixer.Sound('звук_форм_ключа.wav')
        teleport = pygame.mixer.Sound('телепорт.wav')

        size = 1000, 700
        screen = pygame.display.set_mode(size)
        pygame.display.set_caption('Лабиринт')
        
        game_on = True
        clock = pygame.time.Clock()
        fps = 60
        RUNNING = True
        BROWN = (110, 60, 0)
        begin = True
        CONTIN = False
        touch_button = False
        while RUNNING:
            GAME_NOT_ON = True
            GAME_ON = True
            buttons = pygame.sprite.Group()
            btns = []
            new_game = Button(200, 300, 300, 100, 'ИГРАТЬ')
            if not begin:
                continue_game = Button(600, 300, 300, 100, 'ПРОДОЛЖИТЬ')
            quit_game = Button(400, 500, 300, 100, 'ВЫЙТИ')
            btns.append(new_game)
            if not begin:
                btns.append(continue_game)
            btns.append(quit_game)
            colors = []
            if not begin:
                colors = [(255, 255, 255), (255, 255, 255), (255, 255, 255)]
            else:
                colors = [(255, 255, 255), (255, 255, 255)]
            while GAME_NOT_ON:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        logging.info("Quit")
                        GAME_NOT_ON = 0
                        RUNNING = False
                        GAME_ON = 0
                    if event.type == pygame.MOUSEMOTION:
                        x = event.pos[0]
                        y = event.pos[1]
                        touch = False
                        for i in range(len(btns)):
                            if btns[i].x <= x <= btns[i].x + btns[i].w and btns[i].y <= y <= btns[i].y + btns[i].h:
                                touch = True
                                colors[i] = (255, 255, 0)
                                if btns[i] == quit_game:
                                    colors[i] = (200, 0, 0)
                            else:
                                colors[i] = (255, 255, 255)
                        if touch and not touch_button:
                            to_button.play()
                        touch_button = touch
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        x = event.pos[0]
                        y = event.pos[1]
                        for i in range(len(btns)):
                            if btns[i].x <= x <= btns[i].x + btns[i].w and btns[i].y <= y <= btns[i].y + btns[i].h:
                                press_button.play()
                                colors[i] = (0, 255, 0)
                                GAME_NOT_ON = 0
                                if btns[i] == quit_game:
                                    logging.info("Quit2")
                                    pygame.quit()
                                elif not begin and btns[i] == continue_game:
                                    CONTIN = True
                                elif btns[i] == new_game:
                                    CONTIN = False
                pygame.font.init()
#                font = pygame.font.Font("C:\Windows\Fonts\Arial.ttf", 50)
#                fnt2 = pygame.font.Font("C:\Windows\Fonts\Arial.ttf", 30)
                font = pygame.font.Font(None, 70)
                fnt2 = pygame.font.Font(None, 50)
                name = font.render('ЛАБИРИНТ С ПИНГВИНОМ', True, (255, 255, 0))
                ng = fnt2.render('ИГРАТЬ', True, colors[0])
                cq = 0
                qg = 0
                if not begin:
                    cg = fnt2.render('ПРОДОЛЖИТЬ', True, colors[1])
                    qg = fnt2.render('ВЫЙТИ', True, colors[2])
                else:
                    qg = fnt2.render('ВЫЙТИ', True, colors[1])
                screen.fill(BROWN)
                new_game.image.blit(ng, (new_game.w // 4, new_game.h // 3))
                if not begin:
                    continue_game.image.blit(cg, (continue_game.w // 12, new_game.h // 3))
                quit_game.image.blit(qg, (quit_game.w // 4, quit_game.h // 3))
                screen.blit(name, (200, 100))
                buttons.draw(screen)
                pygame.display.flip()
                clock.tick(fps)
            begin = False
            if not CONTIN:
                mas = []
                for i in range(11):
                    a = pygame.sprite.Group()
                    mas.append(a)
                heroes = pygame.sprite.Group()
                inventory = pygame.sprite.Group()
                keys = []
                portals = []
                saved = [0] * 10
                iy = 610
                ix = 20
                ixp = 80
                peng = Hero('hero_standing.jpg', 'hero_left.jpg', 'hero_right.jpg')
                INDEX = 0
                FINAL = 0
                
                mas[0].add(Room('room0.png'))
                mas[1].add(Room('room1.png'))
                mas[2].add(Room('room2.png'))
                mas[3].add(Room('room3.png'))
                mas[4].add(Room('room4.png'))
                mas[5].add(Room('room5.png'))
                mas[6].add(Room('room6.png'))
                mas[7].add(Room('room7.png'))
                mas[8].add(Room('room8.png'))
                mas[9].add(Room('room9.png'))
                mas[10].add(Room('room10.png'))

                blue_door = Door('blue door.png', 0, 850, 120, 80, 250, 0)
                pink_door = Door('pink door.png', 0, 500, 350, 100, 300, 90)
                red_door = Door('red door.png', 1, 300, 0, 80, 190, 90)
                yellow_door = Door('yellow door.png', 4, 650, 180, 80, 180, 0)
                green_door = Door('green door.png', 5, 680, 200, 80, 180, 0)
                grey_door = Door('grey door.png', 2, 120, 80, 100, 220, 0)
                black_door = Door('black door.png', 8, 160, 250, 80, 180, -30)

                blue_key = Key('blue key.png', 0, 330, 40, 100, 100, blue_door)
                pink_key = Key('pink key.png', 3, 200, 300, 100, 100, pink_door)
                black_key = Key('black key.png', 5, 100, 250, 100, 100, black_door)
                yellow_key = Key('yellow key.png', 6, 200, 300, 100, 100, yellow_door)
                red_key = Key('red key.png', 8, 50, 200, 100, 100, red_door)
                grey_key = Key('grey key.png', 8, 300, 50, 100, 100, grey_door)
                green_key = Key('green key.png', 10, 200, 140, 100, 100, green_door)

                blue_portal_first = Portal('blue portal.png', 1, 800, 230, 100, 100, None)
                blue_portal_second = Portal('blue portal.png', 10, 450, 150, 100, 100, None)
                red_portal_first = Portal('red portal.png', 4, 750, 200, 100, 100, None)
                red_portal_second = Portal('red portal.png', 7, 500, 250, 125, 125, None)

                star_hole = Door('star hole.png', 9, 370, 50, 65, 65, 0)
                triangle_hole = Door('triangle hole.png', 9, 420, 50, 65, 65, 0)
                circle_hole = Door('circle hole.png', 9, 470, 50, 65, 65, 0)
                square_hole = Door('square hole.png', 9, 530, 50, 65, 65, 0)

                star_key = Form_Key('star key.png', 0, 615, 440, 75, 75, star_hole)
                square_key = Form_Key('square key.png', 3, 700, 250, 75, 75, square_hole)
                circle_key = Form_Key('circle key.png', 6, 700, 200, 75, 75, circle_hole)
                triangle_key = Form_Key('triangle key.png', 8, 600, 100, 75, 75, triangle_hole)

                Part_1 = Final_Door('final door 1.png', 9, 660, 120, 110, 230, 0)
                Part_2 = Final_Door('final door 2.png', 9, 660, 330, 115, 230, 0)

                blue_portal_first.connect(blue_portal_second)
                red_portal_first.connect(red_portal_second)
                
                g = [dict() for i in range(11)]
                g[0]['right'] = 1  
                g[1]['up'] = 2
                g[1]['down'] = 4
                g[1]['left'] = 0
                g[2]['left'] = 3
                g[2]['right'] = 6
                g[2]['down'] = 1
                g[3]['right'] = 2
                g[4]['up'] = 1
                g[4]['left'] = 5
                g[5]['right'] = 4
                g[6]['left'] = 2
                g[6]['down'] = 7
                g[7]['up'] = 6
                g[7]['down'] = 8
                g[8]['down'] = 10
                g[8]['right'] = 9
                g[8]['up'] = 7
                g[9]['left'] = 8
                g[10]['up'] = 8
                STEP = 3
                k_left = False
                k_right = False
                k_up = False
                k_down = False
                mouse_down = False
                moving_key = -1
                beg_timer = 0
            while GAME_ON:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        logging.info("Quit3")
                        pygame.quit()
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_LEFT:
                            k_left = True
                        elif event.key == pygame.K_RIGHT:
                            k_right = True
                        elif event.key == pygame.K_UP:
                            k_up = True
                        elif event.key == pygame.K_DOWN:
                            k_down = True
                        elif event.key == pygame.K_BACKSPACE:
                            press_button.play()
                            GAME_ON = 0
                    elif event.type == pygame.KEYUP:
                        if event.key == pygame.K_LEFT:
                            k_left = False
                        elif event.key == pygame.K_RIGHT:
                            k_right = False
                        elif event.key == pygame.K_UP:
                            k_up = False
                        elif event.key == pygame.K_DOWN:
                            k_down = False
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        mouse_down = True
                        x = event.pos[0]
                        y = event.pos[1]
                        if y >= 600:
                            x //= 80
                            if x < len(saved) and type(saved[x]) != int:
                                moving_key = x
                    elif event.type == pygame.MOUSEBUTTONUP:
                        mouse_down = False
                        if moving_key != -1:
                            saved[moving_key].back_to_inventory()
                    elif event.type == pygame.MOUSEMOTION:
                        if mouse_down and moving_key != -1:
                            x = event.pos[0]
                            y = event.pos[1]
                            saved[moving_key].to_cursor(x, y)
                if mouse_down and moving_key != -1:
                    if saved[moving_key].use():
                        saved[moving_key] = 0
                        moving_key = -1
                if k_left:
                    peng.image = peng.image2
                    peng.mask = peng.mask2
                    peng.move(-STEP, 0)
                elif k_right:
                    peng.image = peng.image3
                    peng.mask = peng.mask3
                    peng.move(STEP, 0)
                elif k_up:
                    peng.image = peng.image1
                    peng.mask = peng.mask1
                    peng.move(0, -STEP)
                elif k_down:
                    peng.image = peng.image1
                    peng.mask = peng.mask1
                    peng.move(0, STEP)
                peng.rescue(mas[INDEX])
                for i in range(len(keys)):
                    keys[i].check()
                for i in range(len(portals)):
                    portals[i].check()  
                screen.fill((255, 255, 255))
                mas[INDEX].draw(screen)
                if peng.view == 1:
                    heroes.draw(screen)
                else:
                    peng.view = 0
                pygame.draw.rect(screen, (200, 200, 200), (0, 600, 1000, 100))
                inventory.draw(screen)
                if beg_timer < 3:
                    font = pygame.font.Font(None, 25)
                    warning = font.render('Нажмите BACKSPACE для выхода', True, (255, 0, 0))
                    beg_timer += 1 / fps
                    screen.blit(warning, (200, 300))
                pygame.display.flip()
                clock.tick(fps)
                if FINAL == 4:
                    break
            if FINAL == 4: 
                for i in range(100):
                    Part_1.open('up')
                    Part_2.open('down')
                    screen.fill((255, 255, 255))
                    mas[INDEX].draw(screen)
                    heroes.draw(screen)
                    pygame.draw.rect(screen, (200, 200, 200), (0, 600, 1000, 100))
                    inventory.draw(screen)
                    pygame.display.flip()
                    clock.tick(fps)
                while peng.rect.x <= 1000:
                    if peng.rect.y > 310:
                        peng.image = peng.image1
                        peng.mask = peng.mask1
                        peng.rect.y -= 5
                    elif peng.rect.y < 290:
                        peng.image = peng.image1
                        peng.mask = peng.mask1
                        peng.rect.y += 5
                    else:
                        peng.image = peng.image3
                        peng.mask = peng.mask3
                        peng.rect.x += 5
                    screen.fill((255, 255, 255))
                    mas[INDEX].draw(screen)
                    heroes.draw(screen)
                    pygame.draw.rect(screen, (200, 200, 200), (0, 600, 1000, 100))
                    inventory.draw(screen)
                    pygame.display.flip()
                    clock.tick(fps)
                WIN = True
                win_sound.play()
                while WIN:
                    for event in pygame.event.get():
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_BACKSPACE:
                                press_button.play()
                                WIN = False
                                begin = True
                        if event.type == pygame.QUIT:
                            logging.info("Quit4")
                            pygame.quit()
                    font = pygame.font.Font(None, 200)
                    winning = font.render('ПОБЕДА', True, (0, 255, 0))
                    screen.fill(BROWN)
                    screen.blit(winning, (200, 250))
                    pygame.display.flip()
                    clock.tick(fps)
        logging.info("Quit5")
        pygame.quit()

     except Exception as e:        
        logging.info("Error occured!")
        logging.info("".join(traceback.format_exception(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])))
        logging.info("Error trace:")
        logging.info(format_exception(e))
        pygame.quit()
           
