import pygame
import random
import time
import sys

# 初始化 Pygame
pygame.init()
pygame.mixer.init()

# 定义常量
TILE_SIZE = 100
NUM_COLS = 9
NUM_ROWS_GAME = 5
NUM_ROWS_TOTAL = NUM_ROWS_GAME + 1
WIDTH, HEIGHT = 9 * TILE_SIZE, 6 * TILE_SIZE
FPS = 30
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BG_COLOR = (200, 200, 200)
MAX_SELECTION = 6  # 最大选择图片数
COUNTDOWN_TIME = 60  # 倒计时时间（秒）

# 创建窗口
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("k了个k小游戏")

# 初始化时钟
clock = pygame.time.Clock()

# 加载图案图片
patterns = []
for i in range(1, 4):
    try:
        img = pygame.image.load(f"pattern_{i}.png")
        img = pygame.transform.scale(img, (100, 100))
        patterns.append(img)
    except pygame.error as e:
        print(f"Failed to load pattern_{i}.png: {e}")

# 加载成功和失败背景图片
try:
    success_bg_img = pygame.image.load("success_background.png")
    success_bg_img = pygame.transform.scale(success_bg_img, (WIDTH, HEIGHT))
except pygame.error as e:
    print(f"Failed to load success_background.png: {e}")
    success_bg_img = pygame.Surface((WIDTH, HEIGHT))
    success_bg_img.fill(BG_COLOR)  # 使用默认背景色填充

try:
    failure_bg_img = pygame.image.load("failure_background.png")
    failure_bg_img = pygame.transform.scale(failure_bg_img, (WIDTH, HEIGHT))
except pygame.error as e:
    print(f"Failed to load failure_background.png: {e}")
    failure_bg_img = pygame.Surface((WIDTH, HEIGHT))
    failure_bg_img.fill(BG_COLOR)  # 使用默认背景色填充


# 加载背景图片
try:
    background_img = pygame.image.load("background.png")
    background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT - TILE_SIZE))
except pygame.error as e:
    print(f"Failed to load background.png: {e}")
    background_img = pygame.Surface((WIDTH, HEIGHT - TILE_SIZE))
    background_img.fill(BG_COLOR)

# 加载音效
try:
    click_sound = pygame.mixer.Sound("click_sound.wav")
    match_success_sound = pygame.mixer.Sound("match_success_sound.wav")
    game_success_sound = pygame.mixer.Sound("game_success_sound.wav")
    game_over_sound = pygame.mixer.Sound("game_over_sound.wav")
except pygame.error as e:
    print(f"Failed to load sound: {e}")

# 加载菜单背景图片
try:
    menu_background_img = pygame.image.load("menu_background.png")
    menu_background_img = pygame.transform.scale(menu_background_img, (WIDTH, HEIGHT))
except pygame.error as e:
    print(f"Failed to load menu_background.png: {e}")
    menu_background_img = pygame.Surface((WIDTH, HEIGHT))
    menu_background_img.fill(BG_COLOR)  # 使用默认背景色填充


def initialize_board():
    tiles = [pattern for pattern in patterns for _ in range((NUM_COLS * NUM_ROWS_GAME) // len(patterns))]
    random.shuffle(tiles)
    return [tiles[i * NUM_COLS:(i + 1) * NUM_COLS] for i in range(NUM_ROWS_GAME)]

def reset_game():
    global board, selected_images, selected_positions, score, start_time
    board = initialize_board()
    selected_images = []
    selected_positions = set()
    score = 0
    start_time = time.time()  # 记录游戏开始时间

def draw_board():
    screen.blit(background_img, (0, 0))
    for row in range(NUM_ROWS_GAME):
        for col in range(NUM_COLS):
            tile = board[row][col]
            if tile is not None:
                offset = (col % 2) * 20  # 示例偏移量
                screen.blit(tile, (col * TILE_SIZE + offset, row * TILE_SIZE + offset))

    

def draw_selection_box():
    global score_y
    pygame.draw.rect(screen, WHITE, (0, HEIGHT - TILE_SIZE, WIDTH, TILE_SIZE))
    for i in range(3, NUM_COLS):
        x = i * TILE_SIZE
        pygame.draw.line(screen, BLACK, (x, HEIGHT - TILE_SIZE), (x, HEIGHT), 2)
    
    font = pygame.font.SysFont(None, 36)
    text_img = font.render("Selected Images", True, BLACK)
    text_x = TILE_SIZE * 1.5 - text_img.get_width() // 2
    text_y = HEIGHT - TILE_SIZE + (TILE_SIZE - text_img.get_height()) // 2 - 30
    screen.blit(text_img, (text_x, text_y))
    
    score_img = font.render(f"Score: {score}", True, BLACK)
    score_x = TILE_SIZE * 1.5 - score_img.get_width() // 2
    score_y = text_y + text_img.get_height() +10
    screen.blit(score_img, (score_x, score_y))
    
    for i, tile in enumerate(selected_images):
        if i < NUM_COLS - 3:
            x = (i + 3) * TILE_SIZE
            y = HEIGHT - TILE_SIZE
            screen.blit(tile, (x, y))
            pygame.draw.rect(screen, BLACK, (x, y, TILE_SIZE, TILE_SIZE), 2)
    
    draw_countdown_timer(score_y+30)
    return score_y

def draw_game_board_border():
    pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, HEIGHT - TILE_SIZE), 2)

def draw_countdown_timer(y_position):
    elapsed_time = int(time.time() - start_time)
    remaining_time = max(COUNTDOWN_TIME - elapsed_time, 0)
    font = pygame.font.SysFont(None, 36)
    timer_img = font.render(f"Time: {remaining_time}", True, BLACK)
    screen.blit(timer_img, (TILE_SIZE * 1.5 - timer_img.get_width() // 2, y_position))
    return remaining_time <= 0

def add_to_selection(row, col):
    offset = (col % 2) * 50
    tile = board[row][col]

    if tile is not None:
        tile_rect = pygame.Rect(col * TILE_SIZE + offset, row * TILE_SIZE + offset, TILE_SIZE, TILE_SIZE)

        if tile_rect.collidepoint(pygame.mouse.get_pos()):
            # 对于奇数列，检查右边一列的图片是否之前被选择过
            if col % 2 == 1:
                if col + 1 < NUM_COLS and (row, col + 1) in selected_positions:
                    # 右边图片之前被选择过，可以选择当前图片
                    update_selection(row, col, tile)
                else:
                    # 右边的图片未被选择
                    print("You need to select the tile on the right first!")
            else:
                # 偶数列的图片可以直接选择
                update_selection(row, col, tile)

def update_selection(row, col, tile):
    # 选择当前图片
    board[row][col] = None
    index_to_insert = len(selected_images)
    for i, existing_tile in enumerate(selected_images):
        if existing_tile == tile:
            index_to_insert = i + 1
            break
    selected_images.insert(index_to_insert, tile)

    if len(selected_images) > NUM_COLS - 2:
        selected_images.pop(0)
    
    selected_positions.add((row, col))
    draw_selection_box()
    pygame.display.flip()

    if check_and_remove_from_selection():
        match_success_sound.play()

    if len(selected_images) >= MAX_SELECTION:
        display_interaction_screen("LOSE", game_over_sound)
        return

def check_and_remove_from_selection():
    global score
    counts = {}
    
    # 计算每种图片的出现次数
    for tile in selected_images:
        if tile in counts:
            counts[tile] += 1
        else:
            counts[tile] = 1
    
    # 确定需要移除的图片
    to_remove = [tile for tile, count in counts.items() if count >= 3]
    
    if to_remove:
        score += 10
        
        # 仅从选择列表中移除匹配的图片，不清除位置
        new_selection = [tile for tile in selected_images if tile not in to_remove]
        selected_images[:] = new_selection
        
        # 位置不变，只清除图片
        global selected_positions
        # 不需要对 selected_positions 进行修改，只需要确保状态一致

        if not any(tile is not None for row in board for tile in row):
            game_success_sound.play()
            display_interaction_screen("WIN", game_success_sound)
            return True
        
        return True
    
    return False



def display_interaction_screen(result, sound):
    # 选择背景图片
    if result == "WIN":
        background_img = success_bg_img
    elif result == "LOSE":
        background_img = failure_bg_img
    else:
        background_img = pygame.Surface((WIDTH, HEIGHT))
        background_img.fill(BG_COLOR)  # 默认背景色

    # 绘制背景图片
    screen.blit(background_img, (0, 0))
    
    # 绘制结果文本
    result_font = pygame.font.SysFont('Arial', 200, bold=True)
    result_text_img = result_font.render(result, True, (255, 215, 0))  # 金色文字
    result_text_rect = result_text_img.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 80))
    
    # 添加阴影效果
    shadow_offset = 5
    shadow_color = (50, 50, 50)  # 阴影颜色
    shadow_text_img = result_font.render(result, True, shadow_color)
    screen.blit(shadow_text_img, (result_text_rect.x + shadow_offset, result_text_rect.y + shadow_offset))
    
    screen.blit(result_text_img, result_text_rect)
    
    # 绘制分数文本
    score_font = pygame.font.SysFont('Arial', 50, bold=True)
    score_img = score_font.render(f"Your Score: {score}", True, (212, 175, 55))  # 浅金色文字
    score_rect = score_img.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 200))
    
    # 添加阴影效果
    screen.blit(score_img, score_rect)

    # 绘制按钮
    button_font = pygame.font.SysFont('Arial', 40, bold=True)
    restart_text = button_font.render("Restart", True, WHITE)
    quit_text = button_font.render("Quit", True, WHITE)
    
    button_width = 150
    button_height = 50
    restart_button_x = WIDTH // 2 - button_width // 2 - 100
    quit_button_x = WIDTH // 2 - button_width // 2 + 100
    button_y = HEIGHT // 2 + 50
    
    restart_button = pygame.Rect(restart_button_x, button_y, button_width, button_height)
    quit_button = pygame.Rect(quit_button_x, button_y, button_width, button_height)

    # 颜色定义
    button_color = (70, 130, 180)  # SteelBlue
    button_hover_color = (100, 149, 237)  # CornflowerBlue
    button_border_color = BLACK
    
    # 绘制按钮背景
    pygame.draw.rect(screen, button_color, restart_button, border_radius=10)
    pygame.draw.rect(screen, button_color, quit_button, border_radius=10)
    
    # 绘制按钮边框
    pygame.draw.rect(screen, button_border_color, restart_button, 2, border_radius=10)
    pygame.draw.rect(screen, button_border_color, quit_button, 2, border_radius=10)
    
    # 绘制按钮文本
    screen.blit(restart_text, (restart_button.x + (restart_button.width - restart_text.get_width()) // 2, 
                               restart_button.y + (restart_button.height - restart_text.get_height()) // 2))
    screen.blit(quit_text, (quit_button.x + (quit_button.width - quit_text.get_width()) // 2, 
                            quit_button.y + (quit_button.height - quit_text.get_height()) // 2))
    
    pygame.display.flip()
    
    if sound:
        sound.play()

    waiting_for_input = True
    while waiting_for_input:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if restart_button.collidepoint(x, y):
                    reset_game()
                    return
                elif quit_button.collidepoint(x, y):
                    pygame.quit()
                    sys.exit()
            elif event.type == pygame.MOUSEMOTION:
                x, y = event.pos
                if restart_button.collidepoint(x, y):
                    pygame.draw.rect(screen, button_hover_color, restart_button, border_radius=10)
                    pygame.draw.rect(screen, button_border_color, restart_button, 2, border_radius=10)
                else:
                    pygame.draw.rect(screen, button_color, restart_button, border_radius=10)
                    pygame.draw.rect(screen, button_border_color, restart_button, 2, border_radius=10)

                if quit_button.collidepoint(x, y):
                    pygame.draw.rect(screen, button_hover_color, quit_button, border_radius=10)
                    pygame.draw.rect(screen, button_border_color, quit_button, 2, border_radius=10)
                else:
                    pygame.draw.rect(screen, button_color, quit_button, border_radius=10)
                    pygame.draw.rect(screen, button_border_color, quit_button, 2, border_radius=10)

                # 确保按钮文本在更新后的按钮背景上正确显示
                screen.blit(restart_text, (restart_button.x + (restart_button.width - restart_text.get_width()) // 2, 
                                           restart_button.y + (restart_button.height - restart_text.get_height()) // 2))
                screen.blit(quit_text, (quit_button.x + (quit_button.width - quit_text.get_width()) // 2, 
                                        quit_button.y + (quit_button.height - quit_text.get_height()) // 2))

                pygame.display.flip()



def draw_text(text, font, color, surface, position):
    text_surface = font.render(text, True, color)
    surface.blit(text_surface, position)

def draw_mode_selection_screen():
    screen.blit(menu_background_img, (0, 0)) 

    # 字体设置
    mode_font = pygame.font.SysFont('SimHei', 50)
    button_font = pygame.font.SysFont('SimHei', 40)
    
    # 文本
    simple_mode_text = button_font.render("简单模式", True, WHITE)
    hard_mode_text = button_font.render("困难模式", True, WHITE)

    # 按钮位置和大小
    button_width = 200
    button_height = 50
    simple_mode_rect = pygame.Rect((WIDTH - button_width) // 2, HEIGHT // 2 - 75, button_width, button_height)
    hard_mode_rect = pygame.Rect((WIDTH - button_width) // 2, HEIGHT // 2 + 25, button_width, button_height)

    # 颜色定义
    button_color = (70, 130, 180)  # SteelBlue
    button_hover_color = (100, 149, 237)  # CornflowerBlue
    button_border_color = BLACK
    button_text_color = WHITE

    # 绘制按钮背景
    pygame.draw.rect(screen, button_color, simple_mode_rect, border_radius=10)
    pygame.draw.rect(screen, button_color, hard_mode_rect, border_radius=10)
    
    # 绘制按钮边框
    pygame.draw.rect(screen, button_border_color, simple_mode_rect, 2, border_radius=10)
    pygame.draw.rect(screen, button_border_color, hard_mode_rect, 2, border_radius=10)
    
    # 绘制按钮文本
    draw_text("简单模式", button_font, button_text_color, screen,
              (simple_mode_rect.x + (simple_mode_rect.width - simple_mode_text.get_width()) // 2,
               simple_mode_rect.y + (simple_mode_rect.height - simple_mode_text.get_height()) // 2))
    draw_text("困难模式", button_font, button_text_color, screen,
              (hard_mode_rect.x + (hard_mode_rect.width - hard_mode_text.get_width()) // 2,
               hard_mode_rect.y + (hard_mode_rect.height - hard_mode_text.get_height()) // 2))

    pygame.display.flip()

def draw_text_with_shadow(text, font, color, shadow_color, surface, position, shadow_offset=(2, 2)):
    # 绘制阴影
    shadow_position = (position[0] + shadow_offset[0], position[1] + shadow_offset[1])
    shadow_surface = font.render(text, True, shadow_color)
    surface.blit(shadow_surface, shadow_position)
    
    # 绘制文字
    text_surface = font.render(text, True, color)
    surface.blit(text_surface, position)

def draw_menu():
    screen.blit(menu_background_img, (0, 0))

    # 字体设置
    title_font = pygame.font.SysFont('SimHei', 70)
    button_font = pygame.font.SysFont('SimHei', 45)

    # 标题
    title_text = "欢迎来到k了个k游戏"
    title_color = (255, 105, 180)  # 粉色 (Hot Pink)
    shadow_color = (139, 0, 139)  # 紫色阴影 (Dark Orchid)
    title_img = title_font.render(title_text, True, title_color)
    title_x = (WIDTH - title_img.get_width()) // 2
    title_y = 100

    # 绘制带阴影的标题
    draw_text_with_shadow(title_text, title_font, title_color, shadow_color, screen, (title_x, title_y))

    # 按钮颜色和样式定义
    button_color = (70, 130, 180)  # SteelBlue
    button_hover_color = (100, 149, 237)  # CornflowerBlue
    button_border_color = BLACK
    button_text_color = WHITE
    button_width = 200
    button_height = 50

    # 开始游戏按钮
    start_button_rect = pygame.Rect((WIDTH - button_width) // 2, HEIGHT // 2 - 25, button_width, button_height)
    pygame.draw.rect(screen, button_color, start_button_rect, border_radius=10)
    pygame.draw.rect(screen, button_border_color, start_button_rect, 2, border_radius=10)
    start_text_img = button_font.render("开始游戏", True, button_text_color)
    start_text_x = start_button_rect.x + (start_button_rect.width - start_text_img.get_width()) // 2
    start_text_y = start_button_rect.y + (start_button_rect.height - start_text_img.get_height()) // 2
    screen.blit(start_text_img, (start_text_x, start_text_y))

    # 游戏介绍按钮
    info_button_rect = pygame.Rect((WIDTH - button_width) // 2, HEIGHT // 2 + 100, button_width, button_height)
    pygame.draw.rect(screen, button_color, info_button_rect, border_radius=10)
    pygame.draw.rect(screen, button_border_color, info_button_rect, 2, border_radius=10)
    info_text_img = button_font.render("游戏介绍", True, button_text_color)
    info_text_x = info_button_rect.x + (info_button_rect.width - info_text_img.get_width()) // 2
    info_text_y = info_button_rect.y + (info_button_rect.height - info_text_img.get_height()) // 2
    screen.blit(info_text_img, (info_text_x, info_text_y))

    pygame.display.flip()

def draw_info_screen():
    screen.blit(menu_background_img, (0, 0)) 

    # 信息文本
    info_text = [
        "游戏规则: ",
        "1. 点击图片选择。选择框最多可容纳六张图片，若超出则视为失败。",
        "2. 选择三张相同的图片会被移除。",
        "3. 游戏时间分为30秒和60秒，简单模式为30秒，困难模式为60秒。",
        "4. 在规定时间内消除所有图片即为获胜。"
    ]

    # 字体和颜色设置
    info_font = pygame.font.SysFont('SimHei', 25)
    text_color = (255, 105, 180)  # 粉色
    shadow_color = (139, 0, 139)  # 紫色阴影
    y = 50
    for line in info_text:
        draw_text_with_shadow(line, info_font, text_color, shadow_color, screen, (50, y))
        y += 50

    # 返回菜单按钮样式
    button_color = (70, 130, 180)  # 蓝色 (SteelBlue)
    button_hover_color = (100, 149, 237)  # 亮蓝色 (CornflowerBlue)
    button_border_color = BLACK
    button_text_color = WHITE
    button_width = 150
    button_height = 50

    # 返回菜单按钮
    back_button_rect = pygame.Rect((WIDTH - button_width) // 2, HEIGHT - 100, button_width, button_height)
    pygame.draw.rect(screen, button_color, back_button_rect, border_radius=10)
    pygame.draw.rect(screen, button_border_color, back_button_rect, 2, border_radius=10)
    back_font = pygame.font.SysFont('SimHei', 35)
    back_text_img = back_font.render("返回菜单", True, button_text_color)
    back_text_x = back_button_rect.x + (back_button_rect.width - back_text_img.get_width()) // 2
    back_text_y = back_button_rect.y + (back_button_rect.height - back_text_img.get_height()) // 2
    screen.blit(back_text_img, (back_text_x, back_text_y))

    pygame.display.flip()

# 主游戏循环
menu_active = True
info_active = False
game_active = False

def main():
    global COUNTDOWN_TIME
    state = "MENU"
    reset_game()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

            if state == "MENU":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    click_sound.play()  # 播放点击音效
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    start_button_rect = pygame.Rect((WIDTH - 200) // 2, HEIGHT // 2 - 25, 200, 50)
                    info_button_rect = pygame.Rect((WIDTH - 200) // 2, HEIGHT // 2 + 100, 200, 50)
                    if start_button_rect.collidepoint(mouse_x, mouse_y):
                        state = "MODE_SELECTION"
                    elif info_button_rect.collidepoint(mouse_x, mouse_y):
                        state = "INFO"
                
                draw_menu()

            elif state == "INFO":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    click_sound.play()  # 播放点击音效
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    back_button_rect = pygame.Rect((WIDTH - 150) // 2, HEIGHT - 100, 150, 50)
                    if back_button_rect.collidepoint(mouse_x, mouse_y):
                        state = "MENU"
                
                draw_info_screen()

            elif state == "MODE_SELECTION":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    click_sound.play()  # 播放点击音效
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    simple_mode_rect = pygame.Rect((WIDTH - 200) // 2, HEIGHT // 2 - 75, 200, 50)
                    hard_mode_rect = pygame.Rect((WIDTH - 200) // 2, HEIGHT // 2 + 25, 200, 50)
                    if simple_mode_rect.collidepoint(mouse_x, mouse_y):
                        COUNTDOWN_TIME = 60
                        state = "GAME"
                        reset_game()
                    elif hard_mode_rect.collidepoint(mouse_x, mouse_y):
                        COUNTDOWN_TIME = 30
                        state = "GAME"
                        reset_game()

                draw_mode_selection_screen()

            elif state == "GAME":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    click_sound.play()  # 播放点击音效
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    col = mouse_x // TILE_SIZE
                    row = mouse_y // TILE_SIZE
                    if 0 <= row < NUM_ROWS_GAME and 0 <= col < NUM_COLS:
                        add_to_selection(row, col)
                score_y=draw_selection_box()
                if draw_countdown_timer(score_y + 30):  # 检查倒计时
                    if any(tile is not None for row in board for tile in row):  # 检查是否有未消除的图片
                        state = "END_FAILURE"
                    else:
                        state = "END_SUCCESS"
                    continue
                
                draw_board()
                draw_selection_box()
                draw_game_board_border()
                pygame.display.flip()
                clock.tick(FPS)

            
            elif state == "END_SUCCESS":
                display_interaction_screen("WIN", game_success_sound)
                state = "MENU"

            elif state == "END_FAILURE":
                display_interaction_screen("LOSE", game_over_sound)
                state = "MENU"

if __name__ == "__main__":
    main()
