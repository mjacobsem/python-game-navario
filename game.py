import pygame
import os
import random

# Iniciar pygame
pygame.init()

# Configurar a tela
width = 600
height = 600
canvas = pygame.display.set_mode((width, height))
pygame.display.set_caption("Navário")

# Imagens
player_image = pygame.image.load("images/mario.png")
tire_image = pygame.image.load("images/fireball.gif")
enemy_image = pygame.image.load("images/bloco.png")
score_image = pygame.image.load("images/moeda.png")
vida_image = pygame.image.load("images/vida.png")
fundo_image = pygame.image.load("images/fundo.png")

# Som de acerto
acertou_sound = pygame.mixer.Sound("sounds/som_moeda.mp3")

# Carregar música de fundo
pygame.mixer.music.load("sounds/musica_fundo.mp3")
pygame.mixer.music.set_volume(1)
pygame.mixer.music.play(-1)

# Define cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
TRANSPARENT = (0, 0, 0, 0)

# Classe player
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_image
        self.rect = self.image.get_rect()
        self.rect.x = 50
        self.rect.y = height // 2
        self.shooting = False
        self.speed = 5

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.rect.y -= self.speed * 0.6
        if keys[pygame.K_s]:
            self.rect.y += self.speed * 0.6
        if keys[pygame.K_a]:
            self.rect.x -= self.speed * 0.6
        if keys[pygame.K_d]:
            self.rect.x += self.speed * 0.6
        # Impede que o jogador saia da tela
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > height:
            self.rect.bottom = height
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > width:
            self.rect.right = width


        # Dispara o tiro quando a tecla de espaço for pressionada
        if keys[pygame.K_SPACE] and not self.shooting:
            self.shooting = True
            shot = Tiro(self.rect.centerx, self.rect.centery)
            all_sprites.add(shot)
            shots.add(shot)
        elif not keys[pygame.K_SPACE]:
            self.shooting = False

# Tiro class
class Tiro(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = tire_image
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y

    def update(self):
        self.rect.y -= 5
        if self.rect.bottom < 0:
            self.kill()

        if pygame.sprite.spritecollide(self, enemies, True):
            acertou_sound.play()
            global score
            score += 5
            shots.remove(self)
            self.kill()

# Enemy class
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = enemy_image
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, width - self.rect.width)
        self.rect.y = -self.rect.height
        self.speed = 2

    def update(self):
        self.rect.y += int(self.speed * 1.5)  # Velocidade do inimigo aumentada em 1.5 vezes
        if self.rect.y > height:
            self.kill()

# Criar grupos
all_sprites = pygame.sprite.Group()
shots = pygame.sprite.Group()
enemies = pygame.sprite.Group()

# Criar objeto de jogador
player = Player()
all_sprites.add(player)

# Variáveis do jogo
score = 0
lives = 1
enemy_spawn_timer = pygame.time.get_ticks()
enemy_spawn_delay = 1000

# Looping do jogo
running = True
game_over = False
start_game = False
clock = pygame.time.Clock()
selecting_difficulty = False

# Função para atualizar vidas
def update_lives():
    global lives
    global game_over
    # Desenhar imagem das vidas
    canvas.blit(vida_image, (10, 50))

    # Desenhar texto das vidas
    font = pygame.font.Font(None, 36)
    lives_text = font.render("Vidas: " + str(lives), True, (255, 255, 255))
    canvas.blit(lives_text, (10 + vida_image.get_width() + 10, 60))

    if pygame.sprite.spritecollide(player, enemies, False) or any(enemy.rect.bottom > height for enemy in enemies):
        lives -= 1
        if lives == 0:
            game_over = True

# Function para atualizar score
def update_score():
    # Desenhar imagem score
    canvas.blit(score_image, (10, 10))

    # Texto score
    font = pygame.font.Font(None, 36)
    score_text = font.render("Pontuação: " + str(score), True, (255, 255, 255))
    canvas.blit(score_text, (10 + score_image.get_width() + 10, 10))

# Função para renderizar texto com alfa (transparência)
def render_text_with_alpha(text, font, color, background_color):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()

    # Crie uma nova superfície com canal alfa (transparência)
    alpha_surface = pygame.Surface((text_rect.width, text_rect.height), pygame.SRCALPHA)
    alpha_surface.fill(background_color)
    alpha_surface.blit(text_surface, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
    return alpha_surface

# Função para reiniciar o jogo
def reset_game():
    global all_sprites, shots, enemies, player, score, lives, enemy_spawn_timer, game_over
    all_sprites.empty()
    shots.empty()
    enemies.empty()
    player = Player()
    all_sprites.add(player)
    score = 0
    lives = 1
    enemy_spawn_timer = pygame.time.get_ticks()
    game_over = False

# Função de seleção de dificuldade
def select_difficulty():
    # Limpar a tela
    canvas.fill(BLACK)

    # Texto acima dos botões
    font = pygame.font.Font(None, 30)
    difficulty_text = render_text_with_alpha("Selecione a dificuldade:", font, WHITE, TRANSPARENT)
    difficulty_rect = difficulty_text.get_rect(center=(width // 2, height // 2 - 100))
    canvas.blit(difficulty_text, difficulty_rect)

    # Botões de dificuldade
    easy_button = pygame.Rect(width // 2 - 100, height // 2, 200, 50)
    medium_button = pygame.Rect(width // 2 - 100, height // 2 + 70, 200, 50)
    hard_button = pygame.Rect(width // 2 - 100, height // 2 + 140, 200, 50)

    pygame.draw.rect(canvas, WHITE, easy_button)
    pygame.draw.rect(canvas, WHITE, medium_button)
    pygame.draw.rect(canvas, WHITE, hard_button)

    font = pygame.font.Font(None, 36)
    easy_text = font.render("Fácil", True, BLACK)
    medium_text = font.render("Médio", True, BLACK)
    hard_text = font.render("Difícil", True, BLACK)

    canvas.blit(easy_text, (width // 2 - easy_text.get_width() // 2, height // 2 + 15))
    canvas.blit(medium_text, (width // 2 - medium_text.get_width() // 2, height // 2 + 85))
    canvas.blit(hard_text, (width // 2 - hard_text.get_width() // 2, height // 2 + 155))

    # Atualizar tela
    pygame.display.flip()

    # Aguarde o jogador selecionar uma dificuldade
    difficulty_selected = False
    while not difficulty_selected:
        global enemy_spawn_delay
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if easy_button.collidepoint(mouse_pos):
                    enemy_spawn_delay = 1500  # Dificuldade fácil
                    difficulty_selected = True
                elif medium_button.collidepoint(mouse_pos):
                    enemy_spawn_delay = 1000  # Dificuldade médio
                    difficulty_selected = True
                elif hard_button.collidepoint(mouse_pos):
                    enemy_spawn_delay = 500  # Dificuldade dificil
                    difficulty_selected = True

# Looping do jogo
while running:
    clock.tick(60)

    # Manipulação de eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if not start_game and event.key == pygame.K_SPACE:
                start_game = True
                select_difficulty()
            if game_over:
                if event.key == pygame.K_SPACE:
                    reset_game()
                elif event.key == pygame.K_d and not selecting_difficulty:
                    selecting_difficulty = True
                    select_difficulty()
    if start_game:
        if not game_over:
            # Spawnar inimigos
            current_time = pygame.time.get_ticks()
            if current_time - enemy_spawn_timer > enemy_spawn_delay:
                enemy = Enemy()
                all_sprites.add(enemy)
                enemies.add(enemy)
                enemy_spawn_timer = current_time

            # Atualizar player
            player.update()

            # Atualizar sprites
            all_sprites.update()

            # Verifique a colisão entre tiros e inimigos
            pygame.sprite.groupcollide(shots, enemies, True, True)

            # Desenhar plano de fundo
            canvas.blit(fundo_image, (0, 0))

            # Desenhar vidas
            update_lives()

            # Desenhar score
            update_score()

            # Desenhar sprites
            all_sprites.draw(canvas)

        if game_over:
            # Tela de game over
            canvas.fill(BLACK)
            font = pygame.font.Font(None, 48)
            message = render_text_with_alpha("Você perdeu! Pontuação: " + str(score), font, WHITE, TRANSPARENT)
            message_rect = message.get_rect(center=(width // 2, height // 2))
            canvas.blit(message, message_rect)

            font = pygame.font.Font(None, 24)
            restart_message = render_text_with_alpha("Pressione ESPAÇO para jogar novamente", font, WHITE, TRANSPARENT)
            restart_rect = restart_message.get_rect(center=(width // 2, height // 2 + 50))
            canvas.blit(restart_message, restart_rect)

            difficulty_message = render_text_with_alpha("Pressione D para selecionar outra dificuldade", font, WHITE, TRANSPARENT)
            difficulty_rect = difficulty_message.get_rect(center=(width // 2, height // 2 + 100))
            canvas.blit(difficulty_message, difficulty_rect)

            if selecting_difficulty:
                select_difficulty()
                reset_game()
                selecting_difficulty = False

    else:
        # Tela de início
        canvas.blit(fundo_image, (0, 0))
        font = pygame.font.Font(None, 60)
        start_message = render_text_with_alpha("Navário", font, WHITE, TRANSPARENT)
        start_rect = start_message.get_rect(center=(width // 2, height // 2))
        canvas.blit(start_message, start_rect)

        font = pygame.font.Font(None, 24)
        start_message = render_text_with_alpha("Pressione ESPAÇO para começar", font, WHITE, TRANSPARENT)
        start_rect = start_message.get_rect(center=(width // 2, height // 2 + 227))
        canvas.blit(start_message, start_rect)

    # Atualizar tela
    pygame.display.flip()

# Sair do jogo
pygame.quit()
exit()
