import pygame, sys, os, random
from pygame.locals import *
from Actor import *
from Map import *

############################# GAME ############################
pygame.init()
WINDOW_SIZE = (800,600)
screen = pygame.display.set_mode(WINDOW_SIZE,0,32) # initiate the window
clock = pygame.time.Clock()
FPS = 60
display = pygame.Surface((300,200))

os.environ['SDL_VIDEO_CENTERED'] = '1'

def main_menu():
    # Game Fonts
    font = "Asset/Font/MinimalPixelFont.ttf"

    menu=True
    selected="start"
 
    while menu:
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                pygame.quit()
                quit()
            if event.type==pygame.KEYDOWN:
                if event.key==pygame.K_UP:
                    selected="start"
                elif event.key==pygame.K_DOWN:
                    selected="quit"
                if event.key==pygame.K_RETURN:
                    if selected=="start":
                        Game()
                    if selected=="quit":
                        pygame.quit()
                        quit()
 
        # Main Menu TEXT
        screen.fill((0, 0, 0))
        newFont=pygame.font.Font(font, 200)
        title=newFont.render("SHOOT", 0, (255, 255, 255))
        menuFont=pygame.font.Font(font, 75)
        if selected=="start":
            text_start = menuFont.render("START", 0, (255, 255, 255))
        else:
            text_start = menuFont.render("START", 0, (50, 50, 50))
        if selected=="quit":
            text_quit= menuFont.render("QUIT", 0, (255, 255, 255))
        else:
            text_quit = menuFont.render("QUIT", 0, (50, 50, 50))
 
        title_rect=title.get_rect()
        start_rect=text_start.get_rect()
        quit_rect=text_quit.get_rect()
 
        screen.blit(title, (800/2 - (title_rect[2]/2), 100))
        screen.blit(text_start, (800/2 - (start_rect[2]/2), 300))
        screen.blit(text_quit, (800/2 - (quit_rect[2]/2), 360))
        pygame.display.update()
        clock.tick(FPS)
        pygame.display.set_caption("SHOOT")

def Game():
    # Actors
    Actor.reset()
    background_sound = pygame.mixer.Sound('Asset/JokerDance.ogg')
    gun_sound = pygame.mixer.Sound('Asset/sfx_wpn_cannon4.wav')
    boom_sound = pygame.mixer.Sound('Asset/sfx_exp_short_hard6.wav')
    coin_sound = pygame.mixer.Sound('Asset/sfx_coin_cluster5.wav')
    boom_sound.set_volume(0.7)
    audiomanager = AudioManager(boom_sound, gun_sound, coin_sound)
    player = Player(400,300,3,0.2, screen)
    base = Base(400, 300, screen)
    monster_manager = EnemySpawner()
    hud = HUD(player, base, screen)   
    background_sound.set_volume(0.7)
    background_sound.play(-1)
    # setting
    true_scroll = [0, 0]
    font = "Asset/Font/MinimalPixelFont.ttf"
    map = TiledMap('Asset/Tileset/Map.tmx')
    map_img = map.make_map()
    map_img_rect = map_img.get_rect()
    map_img_rect.center = (400, 300)

    # Setting for Game Over
    gameover_elapsed = 0.0
    radius = 100
    cover_surf = pygame.Surface((radius*2, radius*2))
    cover_surf.fill(0)
    cover_surf.set_colorkey((255, 255, 255))
    pygame.draw.circle(cover_surf, (255, 255, 255), (radius, radius), radius)

    while True:
        dt = clock.tick(FPS)
        
        if player.HP.IsAlive() == False or base.hp <= 0:
            background_sound.stop()
            GameOver(HUD.Score)
            return
        else :
            #set True scroll
            if player.CanFire == False :
                true_scroll[0] += (player.rect.x - true_scroll[0]-380)/20
                true_scroll[1] += (player.rect.y - true_scroll[1]-280)/20
            else :
                subtract_x = abs(player.rect.x - scroll[0] - pygame.mouse.get_pos()[0])
                subtract_y = abs(player.rect.y - scroll[1]- pygame.mouse.get_pos()[1])
                if subtract_x < 700 and subtract_y < 500 :
                    true_scroll[0] += ((player.rect.x + pygame.mouse.get_pos()[0])/2 - true_scroll[0]-380)/20
                    true_scroll[1] += ((player.rect.y + pygame.mouse.get_pos()[1])/2- true_scroll[1]-280)/20
            scroll = true_scroll.copy()
            scroll[0] = int(scroll[0])
            scroll[1] = int(scroll[1])
    
            #Camera Shake
            if HUD.ScreenShake :
                scroll[0] += random.randint(0, 8) - 5
                scroll[1] += random.randint(0, 8) - 5
                HUD.ScreenShake = False

            for event in pygame.event.get():
                #quit game
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                #key Board Press
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_w:
                        player.move_dir[Player.direction['North']] = 1
                    if event.key == pygame.K_s:
                        player.move_dir[Player.direction['South']] = 1
                    if event.key == pygame.K_d:
                        player.move_dir[Player.direction['East']] = 1
                    if event.key == pygame.K_a:
                        player.move_dir[Player.direction['West']] = 1
                #Key Board Release
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_w:
                        player.move_dir[Player.direction['North']] = 0
                    if event.key == pygame.K_s:
                        player.move_dir[Player.direction['South']] = 0
                    if event.key == pygame.K_d:
                        player.move_dir[Player.direction['East']] = 0
                    if event.key == pygame.K_a:
                        player.move_dir[Player.direction['West']] = 0
                #Mouse Event
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    player.CanFire = True
                if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    player.CanFire = False
                    
            screen.blit(map_img, (map_img_rect.x - scroll[0], map_img_rect.y - scroll[1]))
            #Actor update
            monster_manager.update(dt, screen)
            base.draw(scroll)
            Actor.draw(dt, scroll)
            player.update_bullet(dt, scroll)
            #HUD
            player.HP.draw()
            hud.draw()
            #pygame update
            pygame.display.update()
            pygame.display.set_caption('SHOOT')

def GameOver(score):
    # Game Fonts
    font = "Asset/Font/MinimalPixelFont.ttf"
    pygame.mouse.set_visible(True)
 
    while True:
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                return
 
        # Main Menu TEXT
        screen.fill((0, 0, 0))
        newFont=pygame.font.Font(font, 150)
        title=newFont.render("GAME OVER", 0, (255, 0, 0))
        scoreFont=pygame.font.Font(font, 60)
        scoreText = "Score: {}".format(score)
        Text_Score=scoreFont.render(scoreText, 0, (255,255, 255))
        gotoFont = pygame.font.Font(font, 50)
        gotoMenu = gotoFont.render("Click Screen To Quit", 0, (255, 255, 255))
        goto_rect = gotoMenu.get_rect()
        title_rect=title.get_rect()
        score_rect = Text_Score.get_rect()
        screen.blit(Text_Score,(800/2 - (score_rect[2]/2), 300))
        screen.blit(gotoMenu, (800/2 - (goto_rect[2]/2), 400))
        screen.blit(title, (800/2 - (title_rect[2]/2), 100))
        pygame.display.update()
        clock.tick(FPS)
        pygame.display.set_caption("SHOOT")

if __name__ == '__main__':
    main_menu()


