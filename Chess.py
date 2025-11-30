import os
import json

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
import sys

import random

# Инициализация Pygame
pygame.init()

# Константы
WIDTH, HEIGHT = 800, 800
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH // COLS

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BROWN = (139, 69, 19)
BEIGE = (245, 245, 220)

# Окно
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Шахматы')
clock = pygame.time.Clock()

USERS_FILE = "users.json"

last_move = None
selected = None  # инициализация в начале программы


class TextInput:
        def __init__(self, rect, placeholder="", is_password=False):
                self.rect = rect
                self.text = ""
                self.placeholder = placeholder
                self.active = False
                self.is_password = is_password
                self.font = pygame.font.SysFont("Arial", 28)

        def handle_event(self, event):
                if event.type == pygame.MOUSEBUTTONDOWN:
                        self.active = self.rect.collidepoint(event.pos)
                if event.type == pygame.KEYDOWN and self.active:
                        if event.key == pygame.K_BACKSPACE:
                                self.text = self.text[:-1]
                        elif event.key == pygame.K_RETURN:
                                return "submit"
                        else:
                                # Ограничиваем неуправляемые символы
                                if len(event.unicode) == 1 and 31 < ord(event.unicode) < 127:
                                        self.text += event.unicode
                return None

        def draw(self, surface):
                pygame.draw.rect(surface, (255, 255, 255), self.rect, 2 if self.active else 1, border_radius=6)
                display_text = "*" * len(self.text) if self.is_password else self.text
                if not display_text:
                        display_text = self.placeholder
                        color = (160, 160, 160)
                else:
                        color = (255, 255, 255)
                text_surface = self.font.render(display_text, True, color)
                surface.blit(text_surface, (self.rect.x + 10, self.rect.y + (self.rect.height - text_surface.get_height()) // 2))


def load_users():
        if os.path.exists(USERS_FILE):
                try:
                        with open(USERS_FILE, "r", encoding="utf-8") as f:
                                return json.load(f)
                except (json.JSONDecodeError, OSError):
                        return {}
        return {}


def save_users(users):
        try:
                with open(USERS_FILE, "w", encoding="utf-8") as f:
                        json.dump(users, f, ensure_ascii=False, indent=2)
        except OSError:
                pass


def auth_screen():
        users = load_users()
        font = pygame.font.SysFont("Arial", 46)
        small_font = pygame.font.SysFont("Arial", 28)

        email_input = TextInput(pygame.Rect(WIDTH // 2 - 200, 260, 400, 50), "Почта")
        password_input = TextInput(pygame.Rect(WIDTH // 2 - 200, 340, 400, 50), "Пароль", is_password=True)

        mode = "register"  # или "login"
        message = ""

        register_btn = pygame.Rect(WIDTH // 2 - 210, 430, 200, 55)
        login_btn = pygame.Rect(WIDTH // 2 + 10, 430, 200, 55)
        submit_btn = pygame.Rect(WIDTH // 2 - 210, 510, 420, 55)
        quit_btn = pygame.Rect(WIDTH // 2 - 80, 590, 160, 45)

        while True:
                WINDOW.fill((20, 24, 35))

                title = font.render("Добро пожаловать", True, (255, 255, 255))
                WINDOW.blit(title, (WIDTH // 2 - title.get_width() // 2, 150))

                email_input.draw(WINDOW)
                password_input.draw(WINDOW)

                pygame.draw.rect(WINDOW, (70, 150, 220) if mode == "register" else (90, 90, 90), register_btn, border_radius=8)
                pygame.draw.rect(WINDOW, (70, 150, 220) if mode == "login" else (90, 90, 90), login_btn, border_radius=8)
                reg_text = small_font.render("Регистрация", True, (255, 255, 255))
                log_text = small_font.render("Вход", True, (255, 255, 255))
                WINDOW.blit(reg_text, reg_text.get_rect(center=register_btn.center))
                WINDOW.blit(log_text, log_text.get_rect(center=login_btn.center))

                pygame.draw.rect(WINDOW, (60, 200, 120), submit_btn, border_radius=8)
                submit_text = small_font.render("Продолжить", True, (20, 20, 20))
                WINDOW.blit(submit_text, submit_text.get_rect(center=submit_btn.center))

                pygame.draw.rect(WINDOW, (200, 70, 70), quit_btn, border_radius=8)
                quit_text = small_font.render("Выход", True, (255, 255, 255))
                WINDOW.blit(quit_text, quit_text.get_rect(center=quit_btn.center))

                if message:
                        msg_surface = small_font.render(message, True, (255, 200, 120))
                        WINDOW.blit(msg_surface, (WIDTH // 2 - msg_surface.get_width() // 2, 200))

                pygame.display.flip()

                for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                                pygame.quit()
                                sys.exit()

                        submit_triggered = False

                        if event.type == pygame.MOUSEBUTTONDOWN:
                                if register_btn.collidepoint(event.pos):
                                        mode = "register"
                                elif login_btn.collidepoint(event.pos):
                                        mode = "login"
                                elif submit_btn.collidepoint(event.pos):
                                        submit_triggered = True
                                elif quit_btn.collidepoint(event.pos):
                                        pygame.quit()
                                        sys.exit()

                        for input_box in (email_input, password_input):
                                result = input_box.handle_event(event)
                                if result == "submit":
                                        submit_triggered = True

                        if event.type == pygame.KEYDOWN and event.key == pygame.K_TAB:
                                if email_input.active:
                                        email_input.active = False
                                        password_input.active = True
                                elif password_input.active:
                                        password_input.active = False
                                        email_input.active = True
                                else:
                                        email_input.active = True

                        if submit_triggered:
                                email = email_input.text.strip()
                                password = password_input.text

                                if not email or not password:
                                        message = "Введите почту и пароль"
                                        continue

                                if mode == "register":
                                        if email in users:
                                                message = "Пользователь уже существует"
                                        else:
                                                users[email] = password
                                                save_users(users)
                                                return email
                                else:
                                        if email not in users:
                                                message = "Аккаунт не найден"
                                        elif users.get(email) != password:
                                                message = "Неверный пароль"
                                        else:
                                                return email


class Piece:
        def __init__(self, color, row, col, symbol):
                self.color = color
                self.row = row
                self.col = col
                self.symbol = symbol

                # Позиция в пикселях
                self.x = col * SQUARE_SIZE
                self.y = row * SQUARE_SIZE

                # Загружаем картинку
                self.image = self.load_image()

        def load_image(self):
                image_path = f"images/{self.color}_{self.__class__.__name__.lower()}.png"
                if os.path.exists(image_path):
                        return pygame.image.load(image_path)
                return None

        # Новый метод для обновления позиции
        def calc_pos(self):
                self.x = self.col * SQUARE_SIZE
                self.y = self.row * SQUARE_SIZE

        def move(self, row, col):
                self.row = row
                self.col = col
                self.calc_pos()  # Обновляем координаты

        def draw(self, win):
                if self.image:
                        # Масштабируем изображение под размер клетки
                        image_scaled = pygame.transform.scale(self.image, (SQUARE_SIZE, SQUARE_SIZE))
                        win.blit(image_scaled, (self.x, self.y))
                else:
                        font = pygame.font.SysFont("segoe ui emoji", SQUARE_SIZE - 10)
                        text = font.render(self.symbol, True,
                                                           (0, 0, 0) if self.color == "black" else (255, 255, 255))
                        # Центрируем символ в клетке
                        text_rect = text.get_rect(center=(self.x + SQUARE_SIZE // 2, self.y + SQUARE_SIZE // 2))
                        win.blit(text, text_rect)

        def get_valid_moves(self, board):
                moves = []
                # Движение вперед
                if 0 <= self.row + self.direction < ROWS:
                        if board[self.row + self.direction][self.col] is None:
                                moves.append((self.row + self.direction, self.col))
                                # Двойной ход с начальной позиции
                                if (self.row == 6 and self.color == 'white') or (self.row == 1 and self.color == 'black'):
                                        if board[self.row + 2 * self.direction][self.col] is None:
                                                moves.append((self.row + 2 * self.direction, self.col))
                # Взятие фигур по диагонали
                for dc in [-1, 1]:
                        new_row, new_col = self.row + self.direction, self.col + dc
                        if 0 <= new_row < ROWS and 0 <= new_col < COLS:
                                piece = board[new_row][new_col]
                                if piece is not None and piece.color != self.color:
                                        moves.append((new_row, new_col))
                return moves


class Pawn(Piece):
        def __init__(self, color, row, col):
                super().__init__(color, row, col, "♙" if color == "black" else "♟")
                self.value = 1
                self.direction = 1 if color == 'black' else -1


class Rook(Piece):
        def __init__(self, color, row, col):
                super().__init__(color, row, col, "♜" if color == "black" else "♖")

                self.value = 5
                self.has_moved = False

        # def draw(self, win):
        #   font = pygame.font.SysFont('segoe ui emoji', SQUARE_SIZE // 2)
        #  text = font.render(self.symbol, True,
        #                  (0, 0, 0) if self.color == 'black' else (255, 255, 255))
        # win.blit(text, (self.x + SQUARE_SIZE // 4, self.y + SQUARE_SIZE // 4))

        def get_valid_moves(self, board):
                moves = []
                # Movement along rows and columns
                directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
                for dr, dc in directions:
                        for i in range(1, 8):
                                new_row, new_col = self.row + dr * i, self.col + dc * i
                                if not (0 <= new_row < ROWS and 0 <= new_col < COLS):
                                        break
                                piece = board[new_row][new_col]
                                if piece is None:
                                        moves.append((new_row, new_col))
                                else:
                                        if piece.color != self.color:
                                                moves.append((new_row, new_col))
                                        break
                return moves


class Knight(Piece):
        def __init__(self, color, row, col):
                super().__init__(color, row, col, "♞" if color == "black" else "♘")
                self.value = 3

        # def draw(self, win):
        # Отображение коня
        # font = pygame.font.SysFont('Arial', SQUARE_SIZE // 2)
        # text = font.render('♞' if self.color == 'black' else '♘', True,
        #                 (0, 0, 0) if self.color == 'black' else (255, 255, 255))
        # win.blit(text, (self.x + SQUARE_SIZE // 4, self.y + SQUARE_SIZE // 4))

        def get_valid_moves(self, board):
                moves = []
                knight_moves = [
                        (2, 1), (2, -1), (-2, 1), (-2, -1),
                        (1, 2), (1, -2), (-1, 2), (-1, -2)
                ]
                for dr, dc in knight_moves:
                        new_row, new_col = self.row + dr, self.col + dc
                        if 0 <= new_row < ROWS and 0 <= new_col < COLS:
                                piece = board[new_row][new_col]
                                if piece is None or piece.color != self.color:
                                        moves.append((new_row, new_col))
                return moves


class Bishop(Piece):
        def __init__(self, color, row, col):
                super().__init__(color, row, col, "♗" if color == "black" else "♝")
                self.value = 3

        # def draw(self, win):
        # Отображение слона
        #   font = pygame.font.SysFont('Arial', SQUARE_SIZE // 2)
        #  text = font.render('♝' if self.color == 'black' else '♗', True,
        #                   (0, 0, 0) if self.color == 'black' else (255, 255, 255))
        # win.blit(text, (self.x + SQUARE_SIZE // 4, self.y + SQUARE_SIZE // 4))

        def get_valid_moves(self, board):
                moves = []
                # Движение по диагоналям
                directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
                for dr, dc in directions:
                        for i in range(1, 8):
                                new_row, new_col = self.row + dr * i, self.col + dc * i
                                if not (0 <= new_row < ROWS and 0 <= new_col < COLS):
                                        break
                                piece = board[new_row][new_col]
                                if piece is None:
                                        moves.append((new_row, new_col))
                                else:
                                        if piece.color != self.color:
                                                moves.append((new_row, new_col))
                                        break
                return moves


class Queen(Piece):
        def __init__(self, color, row, col):
                super().__init__(color, row, col, "♕" if color == "black" else "♛")
                self.value = 9

        # def draw(self, win):
        # Отображение ферзя
        #   font = pygame.font.SysFont('Arial', SQUARE_SIZE // 2)
        #  text = font.render('♛' if self.color == 'black' else '♕', True,
        #                   (0, 0, 0) if self.color == 'black' else (255, 255, 255))
        # win.blit(text, (self.x + SQUARE_SIZE // 4, self.y + SQUARE_SIZE // 4))

        def get_valid_moves(self, board):
                moves = []
                # Комбинация ходов ладьи и слона
                directions = [(0, 1), (1, 0), (0, -1), (-1, 0),  # По горизонтали и вертикали
                                          (1, 1), (1, -1), (-1, 1), (-1, -1)]  # По диагоналям
                for dr, dc in directions:
                        for i in range(1, 8):
                                new_row, new_col = self.row + dr * i, self.col + dc * i
                                if not (0 <= new_row < ROWS and 0 <= new_col < COLS):
                                        break
                                piece = board[new_row][new_col]
                                if piece is None:
                                        moves.append((new_row, new_col))
                                else:
                                        if piece.color != self.color:
                                                moves.append((new_row, new_col))
                                        break
                return moves


class King(Piece):
        def __init__(self, color, row, col):
                super().__init__(color, row, col, "♔" if color == "black" else "♚")
                self.value = 100
                self.has_moved = False

        def get_attack_squares(self, board):
                """Return squares the king controls (без учёта рокировки)."""
                moves = []
                for dr in [-1, 0, 1]:
                        for dc in [-1, 0, 1]:
                                if dr == 0 and dc == 0:
                                        continue
                                new_row, new_col = self.row + dr, self.col + dc
                                if 0 <= new_row < ROWS and 0 <= new_col < COLS:
                                        moves.append((new_row, new_col))
                return moves

        def get_castling_moves(self, board):
                moves = []
                if self.has_moved:
                        return []

                # нельзя рокировать, если король под шахом — проверяем вручную
                if is_square_attacked(board, self.row, self.col, self.color):
                        return []

                row = self.row

                # ----- КОРОТКАЯ РОКИРОВКА -----
                rook = board[row][7]
                if isinstance(rook, Rook) and not rook.has_moved:
                        if board[row][5] is None and board[row][6] is None:

                                # Проверяем: проходит ли король через шах
                                if not is_square_attacked(board, row, 5, self.color) and \
                                                not is_square_attacked(board, row, 6, self.color):
                                        moves.append((row, 6))

                # ----- ДЛИННАЯ РОКИРОВКА -----
                rook = board[row][0]
                if isinstance(rook, Rook) and not rook.has_moved:
                        if board[row][1] is None and board[row][2] is None and board[row][3] is None:

                                if not is_square_attacked(board, row, 3, self.color) and \
                                                not is_square_attacked(board, row, 2, self.color):
                                        moves.append((row, 2))

                return moves

        def get_valid_moves(self, board):
                moves = []
                # стандартные ходы на 1 клетку
                for dr in [-1, 0, 1]:
                        for dc in [-1, 0, 1]:
                                if dr == 0 and dc == 0:
                                        continue
                                new_row, new_col = self.row + dr, self.col + dc
                                if 0 <= new_row < ROWS and 0 <= new_col < COLS:
                                        piece = board[new_row][new_col]
                                        if piece is None or piece.color != self.color:
                                                moves.append((new_row, new_col))

                moves.extend(self.get_castling_moves(board))
                return moves


def is_in_check(board, color):
        king_pos = None
        # Находим короля
        for row in range(ROWS):
                for col in range(COLS):
                        piece = board[row][col]
                        if isinstance(piece, King) and piece.color == color:
                                king_pos = (row, col)
                                break
        # Проверяем, угрожает ли королю какая-либо фигура
        for row in range(ROWS):
                for col in range(COLS):
                        piece = board[row][col]
                        if piece is not None and piece.color != color:
                                if isinstance(piece, King):
                                        attacked = piece.get_attack_squares(board)
                                else:
                                        attacked = piece.get_valid_moves(board)

                                if king_pos in attacked:
                                        return True
        return False


def is_square_attacked(board, row, col, color):
        enemy = "white" if color == "black" else "black"

        for r in range(ROWS):
                for c in range(COLS):
                        piece = board[r][c]
                        if piece is not None and piece.color == enemy:
                                if isinstance(piece, King):
                                        attacked = piece.get_attack_squares(board)
                                else:
                                        attacked = piece.get_valid_moves(board)

                                if (row, col) in attacked:
                                        return True
        return False


def filter_safe_moves(board, piece, moves):
        safe_moves = []
        for row, col in moves:
                orig_row, orig_col = piece.row, piece.col
                captured = board[row][col]

                # делаем временный ход
                board[orig_row][orig_col] = None
                board[row][col] = piece
                piece.row, piece.col = row, col

                if not is_in_check(board, piece.color):
                        safe_moves.append((row, col))

                # отменяем ход
                board[orig_row][orig_col] = piece
                board[row][col] = captured
                piece.row, piece.col = orig_row, orig_col

        return safe_moves


def draw_board(board):

        for row in range(ROWS):
                for col in range(COLS):
                        color = BEIGE if (row + col) % 2 == 0 else BROWN
                        pygame.draw.rect(WINDOW, color,
                                                         (col * SQUARE_SIZE, row * SQUARE_SIZE,
                                                          SQUARE_SIZE, SQUARE_SIZE))

last_move_start = None
last_move_end = None
def draw_last_move(win, last_move):
        if last_move:
                (fr, fc), (tr, tc) = last_move
                s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
                s.set_alpha(120)
                s.fill((0, 200, 255))  # голубая подсветка
                win.blit(s, (fc * SQUARE_SIZE, fr * SQUARE_SIZE))
                win.blit(s, (tc * SQUARE_SIZE, tr * SQUARE_SIZE))


hovered_square = None

# Подсветка последних ходов
if last_move:
        (fr, fc), (tr, tc) = last_move
        s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
        s.set_alpha(150)
        s.fill((0, 200, 255))  # Цвет для последних ходов
        WINDOW.blit(s, (fc * SQUARE_SIZE, fr * SQUARE_SIZE))
        WINDOW.blit(s, (tc * SQUARE_SIZE, tr * SQUARE_SIZE))


def draw_pieces(win, board):
        for row in range(ROWS):
                for col in range(COLS):
                        piece = board[row][col]
                        if piece is not None:
                                piece.calc_pos()  # Обновляем координаты перед рисованием
                                piece.draw(win)


def initialize_board():
        # Создаем пустую доску
        board = [[None for _ in range(COLS)] for _ in range(ROWS)]

        # Расставляем черные фигуры
        board[0] = [
                Rook('black', 0, 0), Knight('black', 0, 1), Bishop('black', 0, 2),
                Queen('black', 0, 3), King('black', 0, 4),
                Bishop('black', 0, 5), Knight('black', 0, 6), Rook('black', 0, 7)
        ]
        # Черные пешки
        for col in range(COLS):
                board[1][col] = Pawn('black', 1, col)

        # Расставляем белые фигуры
        board[7] = [
                Rook('white', 7, 0), Knight('white', 7, 1), Bishop('white', 7, 2),
                Queen('white', 7, 3), King('white', 7, 4),
                Bishop('white', 7, 5), Knight('white', 7, 6), Rook('white', 7, 7)
        ]
        # Белые пешки
        for col in range(COLS):
                board[6][col] = Pawn('white', 6, col)

        return board


def is_checkmate(board, color):
        # Сначала проверяем, есть ли шах
        if not is_in_check(board, color):
                return False

        # Проверяем все возможные ходы игрока
        for row in range(ROWS):
                for col in range(COLS):
                        piece = board[row][col]
                        if piece is not None and piece.color == color:
                                moves = filter_safe_moves(board, piece, piece.get_valid_moves(board))
                                for move in moves:
                                        # Делаем временный ход
                                        orig_row, orig_col = piece.row, piece.col
                                        captured = board[move[0]][move[1]]

                                        board[orig_row][orig_col] = None
                                        board[move[0]][move[1]] = piece
                                        piece.row, piece.col = move[0], move[1]

                                        still_in_check = is_in_check(board, color)

                                        # Отменяем ход
                                        board[orig_row][orig_col] = piece
                                        board[move[0]][move[1]] = captured
                                        piece.row, piece.col = orig_row, orig_col

                                        # Если есть ход, выводящий из шаха — это не мат
                                        if not still_in_check:
                                                return False

        return True  # Шах + нет ходов = мат


def choose_promotion(color):
        selecting = True
        options = ["Queen", "Rook", "Bishop", "Knight"]
        selected_index = 0

        font = pygame.font.SysFont("segoe ui emoji", 40)

        while selecting:
                WINDOW.fill((30, 30, 30))

                text = font.render("Выберите фигуру для превращения:", True, (255, 255, 255))
                WINDOW.blit(text, (50, 100))

                for i, name in enumerate(options):
                        color_rect = (150, 200 + i * 70, 500, 60)
                        pygame.draw.rect(WINDOW, (70, 70, 70) if i != selected_index else (120, 120, 120), color_rect)

                        txt = font.render(name, True, (255, 255, 255))
                        WINDOW.blit(txt, (200, 210 + i * 70))

                pygame.display.update()

                for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                                pygame.quit()
                                sys.exit()

                        if event.type == pygame.KEYDOWN:
                                if event.key == pygame.K_UP:
                                        selected_index = (selected_index - 1) % 4
                                elif event.key == pygame.K_DOWN:
                                        selected_index = (selected_index + 1) % 4
                                elif event.key == pygame.K_RETURN:
                                        selecting = False

        choice = options[selected_index]

        if choice == "Queen":
                return Queen
        if choice == "Rook":
                return Rook
        if choice == "Bishop":
                return Bishop
        if choice == "Knight":
                return Knight


def animate_move(piece, start_pos, end_pos, board, duration=0.15):
        """
        Плавное перемещение фигуры.
        start_pos: (row, col)
        end_pos:   (row, col)
        """
        start_x = start_pos[1] * SQUARE_SIZE
        start_y = start_pos[0] * SQUARE_SIZE
        end_x = end_pos[1] * SQUARE_SIZE
        end_y = end_pos[0] * SQUARE_SIZE

        frames = int(duration * 60)  # 60 FPS

        for i in range(frames):
                t = (i + 1) / frames
                x = start_x + (end_x - start_x) * t
                y = start_y + (end_y - start_y) * t

                draw_board(board)
                draw_last_move(WINDOW, last_move)
                draw_pieces(WINDOW, board)

                # Рисуем двигаемую фигуру сверху
                WINDOW.blit(piece.image, (x, y))

                pygame.display.update()
                pygame.time.delay(int(1000 / 60))


def main():
        pygame.font.init()
        clock = pygame.time.Clock()
        board = initialize_board()
        selected = None
        valid_moves = []
        turn = 'white'

        running = True
        while running:
                draw_board(board)
                draw_pieces(WINDOW, board)

                if is_checkmate(board, turn):
                        winner = 'белых' if turn == 'black' else 'черных'
                        show_game_over(winner)
                        running = False
                        continue

                for row in range(ROWS):
                        for col in range(COLS):
                                piece = board[row][col]
                                if isinstance(piece, King) and is_in_check(board, piece.color):
                                        s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
                                        s.set_alpha(150)
                                        s.fill((255, 0, 0))
                                        WINDOW.blit(s, (col * SQUARE_SIZE, row * SQUARE_SIZE))

                for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                                running = False

                        if event.type == pygame.MOUSEBUTTONDOWN:
                                x, y = pygame.mouse.get_pos()
                                col, row = x // SQUARE_SIZE, y // SQUARE_SIZE

                                if selected is None:
                                        piece = board[row][col]
                                        if piece is not None and piece.color == turn:
                                                selected = piece
                                                valid_moves = filter_safe_moves(board, piece, piece.get_valid_moves(board))
                                else:
                                        if (row, col) in valid_moves:
                                                if isinstance(selected, King) and abs(col - selected.col) == 2:
                                                        kr, kc = selected.row, selected.col
                                                        if col == 6:
                                                                rook = board[kr][7]
                                                                animate_move(selected, (kr, kc), (kr, 6), board)
                                                                animate_move(rook, (kr, 7), (kr, 5), board)
                                                                board[kr][kc] = None
                                                                board[kr][7] = None
                                                                selected.move(kr, 6)
                                                                rook.move(kr, 5)
                                                                board[kr][6] = selected
                                                                board[kr][5] = rook
                                                        elif col == 2:
                                                                rook = board[kr][0]
                                                                animate_move(selected, (kr, kc), (kr, 2), board)
                                                                animate_move(rook, (kr, 0), (kr, 3), board)
                                                                board[kr][kc] = None
                                                                board[kr][0] = None
                                                                selected.move(kr, 2)
                                                                rook.move(kr, 3)
                                                                board[kr][2] = selected
                                                                board[kr][3] = rook

                                                start = (selected.row, selected.col)
                                                end = (row, col)
                                                animate_move(selected, start, end, board)
                                                board[selected.row][selected.col] = None
                                                selected.move(row, col)
                                                board[row][col] = selected

                                                if isinstance(selected, Pawn):
                                                        is_white_end = selected.color == "white" and row == 0
                                                        is_black_end = selected.color == "black" and row == 7
                                                        if is_white_end or is_black_end:
                                                                choice = promote_pawn_gui(selected.color)
                                                                if choice == "Q":
                                                                        board[row][col] = Queen(selected.color, row, col)
                                                                elif choice == "R":
                                                                        board[row][col] = Rook(selected.color, row, col)
                                                                elif choice == "B":
                                                                        board[row][col] = Bishop(selected.color, row, col)
                                                                elif choice == "N":
                                                                        board[row][col] = Knight(selected.color, row, col)

                                                if isinstance(selected, King) or isinstance(selected, Rook):
                                                        selected.has_moved = True

                                                turn = 'black' if turn == 'white' else 'white'
                                        selected = None
                                        valid_moves = []

                if selected:
                        s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
                        s.set_alpha(100)
                        s.fill((255, 255, 0))
                        WINDOW.blit(s, (selected.col * SQUARE_SIZE, selected.row * SQUARE_SIZE))

                        for (row, col) in valid_moves:
                                s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
                                s.set_alpha(100)
                                s.fill((0, 255, 0))
                                WINDOW.blit(s, (col * SQUARE_SIZE, row * SQUARE_SIZE))

                pygame.display.flip()
                clock.tick(60)

def show_game_over(winner):
        s = pygame.Surface((WIDTH, HEIGHT))
        s.set_alpha(200)
        s.fill((0, 0, 0))
        WINDOW.blit(s, (0, 0))

        font = pygame.font.SysFont('Arial', 50)
        text = font.render(f"Игра окончена! Победа {winner}!", True, (255, 255, 255))
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30))
        WINDOW.blit(text, text_rect)

        font_small = pygame.font.SysFont('Arial', 30)
        instruction = font_small.render("Нажмите любую кнопку для выхода", True, (200, 200, 200))
        inst_rect = instruction.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 30))
        WINDOW.blit(instruction, inst_rect)

        pygame.display.flip()

        waiting = True
        while waiting:
                for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                                pygame.quit()
                                sys.exit()
                        if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                                waiting = False
                                return


def main_menu(user_email=None):
        running = True
        selected_mode = None
        font = pygame.font.SysFont("Arial", 50)
        small_font = pygame.font.SysFont("Arial", 30)

        buttons = {
                "player_vs_player": {"text": "Игрок vs Игрок", "rect": pygame.Rect(WIDTH // 2 - 150, 200, 300, 60)},
                "player_vs_ai": {"text": "Игрок vs ИИ", "rect": pygame.Rect(WIDTH // 2 - 150, 300, 300, 60)},
                "training": {"text": "Тренировка", "rect": pygame.Rect(WIDTH // 2 - 150, 400, 300, 60)},
                "quit": {"text": "Выход", "rect": pygame.Rect(WIDTH // 2 - 150, 500, 300, 60)},
        }

        ai_elo = 600

        while running:
                WINDOW.fill((30, 30, 40))

                title = font.render("Шахматы", True, (255, 255, 255))
                title_rect = title.get_rect(center=(WIDTH // 2, 100))
                WINDOW.blit(title, title_rect)

                if user_email:
                        hello_text = small_font.render(f"Вы вошли как {user_email}", True, (200, 200, 200))
                        WINDOW.blit(hello_text, (WIDTH // 2 - hello_text.get_width() // 2, 140))

                mx, my = pygame.mouse.get_pos()
                for key, btn in buttons.items():
                        color = (70, 150, 220) if btn["rect"].collidepoint(mx, my) else (80, 80, 80)
                        pygame.draw.rect(WINDOW, color, btn["rect"], border_radius=10)
                        pygame.draw.rect(WINDOW, (255, 255, 255), btn["rect"], 3, border_radius=10)
                        text_surf = small_font.render(btn["text"], True, (255, 255, 255))
                        text_rect = text_surf.get_rect(center=btn["rect"].center)
                        WINDOW.blit(text_surf, text_rect)

                if selected_mode == "player_vs_ai":
                        difficulty_text = small_font.render("Уровень ИИ: Средний", True, (200, 200, 200))
                        WINDOW.blit(difficulty_text, (WIDTH // 2 - 80, 470))

                pygame.display.flip()

                for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                                pygame.quit()
                                sys.exit()

                        if event.type == pygame.MOUSEBUTTONDOWN:
                                mx, my = pygame.mouse.get_pos()
                                for key, btn in buttons.items():
                                        if btn["rect"].collidepoint(mx, my):
                                                if key == "quit":
                                                        pygame.quit()
                                                        sys.exit()
                                                selected_mode = key
                                                running = False

        return selected_mode, ai_elo


def get_ai_move(board, color, elo):
        moves = []
        for row in range(ROWS):
                for col in range(COLS):
                        piece = board[row][col]
                        if piece is not None and piece.color == color:
                                valid = filter_safe_moves(board, piece, piece.get_valid_moves(board))
                                for move in valid:
                                        moves.append((piece, move))

        if not moves:
                return None, None

        randomness = max(0, 1200 - elo) / 1200
        if random.random() < randomness:
                return random.choice(moves)

        best_score = -float('inf')
        best_move = None
        for piece, (r, c) in moves:
                captured = board[r][c]
                score = captured.value if captured is not None else 0
                if score > best_score:
                        best_score = score
                        best_move = (piece, (r, c))
        return best_move if best_move is not None else random.choice(moves)


def promote_pawn_gui(color):
        running = True
        size = 80

        images = {
                "Q": pygame.transform.scale(pygame.image.load(f"images/{color}_queen.png"), (size, size)),
                "R": pygame.transform.scale(pygame.image.load(f"images/{color}_rook.png"), (size, size)),
                "B": pygame.transform.scale(pygame.image.load(f"images/{color}_bishop.png"), (size, size)),
                "N": pygame.transform.scale(pygame.image.load(f"images/{color}_knight.png"), (size, size)),
        }

        positions = {
                "Q": (WIDTH // 2 - 160, HEIGHT // 2 - 40),
                "R": (WIDTH // 2 - 80, HEIGHT // 2 - 40),
                "B": (WIDTH // 2, HEIGHT // 2 - 40),
                "N": (WIDTH // 2 + 80, HEIGHT // 2 - 40),
        }

        while running:
                s = pygame.Surface((WIDTH, HEIGHT))
                s.set_alpha(180)
                s.fill((0, 0, 0))
                WINDOW.blit(s, (0, 0))

                font = pygame.font.SysFont("Arial", 42)
                text = font.render("Выберите фигуру", True, (255, 255, 255))
                rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 120))
                WINDOW.blit(text, rect)

                for key, (x, y) in positions.items():
                        WINDOW.blit(images[key], (x, y))
                        pygame.draw.rect(WINDOW, (255, 255, 255), (x, y, size, size), 2)

                pygame.display.flip()

                for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                                pygame.quit()
                                sys.exit()

                        if event.type == pygame.MOUSEBUTTONDOWN:
                                mx, my = pygame.mouse.get_pos()
                                for key, (x, y) in positions.items():
                                        if x <= mx <= x + size and y <= my <= y + size:
                                                return key


def main_ai(ai_elo, ai_color="black"):
        pygame.font.init()

        clock = pygame.time.Clock()
        board = initialize_board()
        selected = None
        valid_moves = []
        turn = 'white'

        running = True
        while running:
                draw_board(board)
                draw_pieces(WINDOW, board)

                if is_checkmate(board, turn):
                        winner = 'белых' if turn == 'black' else 'черных'
                        show_game_over(winner)
                        running = False
                        continue

                for row in range(ROWS):
                        for col in range(COLS):
                                piece = board[row][col]
                                if isinstance(piece, King) and is_in_check(board, piece.color):
                                        s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
                                        s.set_alpha(150)
                                        s.fill((255, 0, 0))
                                        WINDOW.blit(s, (col * SQUARE_SIZE, row * SQUARE_SIZE))

                if ai_color == turn:
                        pygame.time.delay(int(300 * 2.5))
                        piece, move = get_ai_move(board, ai_color, ai_elo)
                        if piece and move:
                                if isinstance(piece, King) and abs(move[1] - piece.col) == 2:
                                        if move[1] == 6:
                                                rook = board[piece.row][7]
                                                board[piece.row][7] = None
                                                rook.move(piece.row, 5)
                                                board[piece.row][5] = rook
                                        elif move[1] == 2:
                                                rook = board[piece.row][0]
                                                board[piece.row][0] = None
                                                rook.move(piece.row, 3)
                                                board[piece.row][3] = rook

                                board[piece.row][piece.col] = None
                                piece.move(*move)
                                board[move[0]][move[1]] = piece

                                if isinstance(piece, Pawn):
                                        if (piece.color == "white" and piece.row == 0) or (piece.color == "black" and piece.row == 7):
                                                PromoClass = choose_promotion(piece.color)
                                                board[piece.row][piece.col] = PromoClass(piece.color, piece.row, piece.col)

                                if isinstance(piece, King) or isinstance(piece, Rook):
                                        piece.has_moved = True

                                turn = 'white' if turn == 'black' else 'black'

                for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                                running = False
                        if ai_color != turn and event.type == pygame.MOUSEBUTTONDOWN:
                                x, y = pygame.mouse.get_pos()
                                col, row = x // SQUARE_SIZE, y // SQUARE_SIZE

                                if selected is None:
                                        piece = board[row][col]
                                        if piece is not None and piece.color == turn:
                                                selected = piece
                                                valid_moves = filter_safe_moves(board, piece, piece.get_valid_moves(board))
                                else:
                                        if (row, col) in valid_moves:
                                                if isinstance(selected, King) and abs(col - selected.col) == 2:
                                                        if col == 6:
                                                                rook = board[selected.row][7]
                                                                board[selected.row][7] = None
                                                                rook.move(selected.row, 5)
                                                                board[selected.row][5] = rook
                                                        elif col == 2:
                                                                rook = board[selected.row][0]
                                                                board[selected.row][0] = None
                                                                rook.move(selected.row, 3)
                                                                board[selected.row][3] = rook

                                                board[selected.row][selected.col] = None
                                                selected.move(row, col)
                                                board[row][col] = selected

                                                if isinstance(selected, Pawn):
                                                        is_white_end = selected.color == "white" and row == 0
                                                        is_black_end = selected.color == "black" and row == 7
                                                        if is_white_end or is_black_end:
                                                                board[row][col] = Queen(selected.color, row, col)

                                                if isinstance(selected, King) or isinstance(selected, Rook):
                                                        selected.has_moved = True

                                                turn = 'white' if turn == 'black' else 'black'
                                        selected = None
                                        valid_moves = []

                if selected:
                        s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
                        s.set_alpha(100)
                        s.fill((255, 255, 0))
                        WINDOW.blit(s, (selected.col * SQUARE_SIZE, selected.row * SQUARE_SIZE))
                        for (r, c) in valid_moves:
                                s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
                                s.set_alpha(100)
                                s.fill((0, 255, 0))
                                WINDOW.blit(s, (c * SQUARE_SIZE, r * SQUARE_SIZE))

                pygame.display.flip()
                clock.tick(60)


if __name__ == "__main__":
        user_email = auth_screen()
        mode, ai_elo = main_menu(user_email)
        if mode == "player_vs_ai":
                main_ai(ai_elo)
        else:
                main()
