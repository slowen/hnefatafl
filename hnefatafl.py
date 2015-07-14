"""
A two player version of Hnefatafl, a Viking board game.

A full description of the game can be found here: http://tinyurl.com/2lpvjb

Author: Sean Lowen
Date: 7/13/2015

"""

import sys
import pygame
from pygame.locals import *

WINDOW_SIZE = WIDTH, HEIGHT = 640, 700
MARGIN_COLOR = 128, 102, 69
GSIZE = WIDTH // 12
MARGIN = GSIZE // 12
SPECIALSQS = set([(5, 5), (0, 0), (0, 10), (10, 10), (10, 0)])


class Move(object):

    """The Move class contains all information about the current move state."""

    def __init__(self):
        """Initialized the Move object.

        a_turn: Bool which is true when its the Attacker's turn, false o.w.
        selected: Bool which is true if a piece has been selected to move.
        """
        self.a_turn = True
        self.selected = False

    def select(self, piece):
        """Allow players to select one of their pieces to move.

        When a player clicks on a piece, this function first checks if they
        have chosen a piece to move already. If they have not, the function
        determines if the piece is theirs or not, and if it is, its location
        is stored in the Move object, its color is changed so the player can
        see what they selected, and the valid moves for that piece are
        calculated.

        Args:
            piece (Piece): the playing piece that the player selected.
        """
        if not self.selected:
            self.selected = True
            piece.color = (71, 166, 169)
            self.row = piece.x_tile
            self.column = piece.y_tile
            self.vm = self.valid_moves(piece.special_sqs)
        else:
            self.selected = False
            piece.color = piece.base_color

    def valid_moves(self, special_sqs):
        """Determine the valid moves for the selected piece.

        Currently there are four very similar functions to determine all valid
        moves to the left, the right, above, and below. These functions need to
        be refactored.

        Args:
            special_sqs (bool): True if piece can move on special squares

        Returns:
            vm (set(int,int)): Set of valid moves.
        """
        vm = set()
        vm.update(self.left_bound())
        vm.update(self.right_bound())
        vm.update(self.up_bound())
        vm.update(self.down_bound())
        if not special_sqs:
            vm.difference_update(SPECIALSQS)
        return vm

    def is_valid_move(self, pos, piece):
        """Determine if the selected move is valid or not.

        The function finds the tile on the board where the player wants to move
        their piece and returns True if the tile is in the set of valid moves
        for the selected piece.

        Args:
            pos (int, int): x and y coordinates in pixels
            piece (Piece): the selected piece

        Returns:
            bool: True if valid move, false o.w.
        """
        row = pos[0] // (WIDTH // 11)
        col = pos[1] // (WIDTH // 11)
        if (row, col) in self.vm:
            piece.pos_cent(row, col)
            return True
        else:
            return False

    def left_bound(self):
        """Find the all valid moves to the left of the selected piece.

        Iterates through all spaces to the left until the space is either
        occupied or it has reached the edge of the board. Every valid move
        is added to a set of valid moves, which is returned.

        Returns:
            vm (set(int, int)): Set of tuples of the tile coordinates of
                                valid moves to the left.
        """
        vm = set()
        temp_row = self.row - 1
        while True:
            if temp_row < 0:
                return vm
            for p in Pieces:
                ppos = self.ppos_cent(temp_row, self.column)
                if p.rect.collidepoint(ppos):
                    return vm
            vm.add((temp_row, self.column))
            temp_row -= 1

    def right_bound(self):
        """Find the all valid moves to the right of the selected piece.

        Iterates through all spaces to the right until the space is either
        occupied or it has reached the edge of the board. Every valid move
        is added to a set of valid moves, which is returned.

        Returns:
            vm (set(int, int)): Set of tuples of the tile coordinates of
                                valid moves to the right.
        """
        vm = set()
        temp_row = self.row + 1
        clear = True
        while clear:
            if temp_row > 10:
                return vm
            for p in Pieces:
                ppos = self.ppos_cent(temp_row, self.column)
                if p.rect.collidepoint(ppos):
                    return vm
            vm.add((temp_row, self.column))
            temp_row += 1

    def up_bound(self):
        """Find the all valid moves above the selected piece.

        Iterates through all spaces above until the space is either
        occupied or it has reached the edge of the board. Every valid move
        is added to a set of valid moves, which is returned.

        Returns:
            vm (set(int, int)): Set of tuples of the tile coordinates of
                                valid moves above.
        """
        vm = set()
        temp_col = self.column - 1
        clear = True
        while clear:
            if temp_col < 0:
                return vm
            for p in Pieces:
                ppos = self.ppos_cent(self.row, temp_col)
                if p.rect.collidepoint(ppos):
                    return vm
            vm.add((self.row, temp_col))
            temp_col -= 1

    def down_bound(self):
        """Find the all valid moves below the selected piece.

        Iterates through all spaces below until the space is either
        occupied or it has reached the edge of the board. Every valid move
        is added to a set of valid moves, which is returned.

        Returns:
            vm (set(int, int)): Set of tuples of the tile coordinates of
                                valid moves below.
        """
        vm = set()
        temp_col = self.column + 1
        clear = True
        while clear:
            if temp_col > 10:
                return vm
            for p in Pieces:
                ppos = self.ppos_cent(self.row, temp_col)
                if p.rect.collidepoint(ppos):
                    return vm
            vm.add((self.row, temp_col))
            temp_col += 1

    def ppos(self, x):
        """Find the top or left pixel position of a given tile.

        Args:
            x (int): the row or column number

        Returns:
            (int): the top or left pixel location of the tile.
        """
        return x*(GSIZE + (GSIZE // 12)) + (GSIZE // 12)

    def ppos_cent(self, x, y):
        """Find the center pixel position of a given tile.

        Args:
            x (int): the row number
            y (int): the column number

        Returns:
            (int, int): tuple of the center pixel location of tile
        """
        return (self.ppos(x) + (GSIZE // 2), self.ppos(y) + (GSIZE // 2))

    def remove_pieces(self):
        """Determine if any pieces need to be removed from the board.

        Note: This function may exist outside of the Move class. Not sure yet.
        """
        pass

    def end_turn(self, piece):
        """Perform some cleanup to end the turn.

        Once the turn has been completed, the a_turn bool is flipped so the
        other player can go, the selected piece is deselected, and its color
        returns to normal.
        """
        self.a_turn = not self.a_turn
        self.selected = False
        piece.color = piece.base_color


class Board(object):

    """The Board class contains information about the physical board.

    Whereas the move class contains information about the state of the pieces,
    the Board class contains information for the look of the board.
    """

    def __init__(self):
        """Create a playing board and color code it.

        Attributes:
            grid (list(str)): A list of strings which classify each tile. Each
                              char in the string maps to a type of tile:
                                  x -> corner tile
                                  a -> initial attack tile
                                  d -> initial defend tile
                                  c -> center tile
            colors (dict): Maps the tiles to the appropriate color.
            dim (int): Dimension of the board (i.e. num of rows or cols.)
            piece (int): Size of playing piece.
        """
        self.grid = ["x..aaaaa..x",
                     ".....a.....",
                     "...........",
                     "a....d....a",
                     "a...ddd...a",
                     "aa.ddcdd.aa",
                     "a...ddd...a",
                     "a....d....a",
                     "...........",
                     ".....a.....",
                     "x..aaaaa..x"]

        self.colors = {'x': (25, 25, 25),
                       'a': (186, 169, 85),
                       'd': (218, 185, 23),
                       'c': (242, 240, 228),
                       '.': (250, 236, 163)}

        self.dim = len(self.grid)


class Piece(pygame.sprite.Sprite):

    """Class for all playing pieces.

    Pieces are pygame sprite objects. It makes grouping, determining
    collisions, and removing pieces very simple.
    """

    def __init__(self, x, y):
        """Create a piece at a given location.

        special_sqs, a bool which dermines if a piece is allowed to move
        onto the corners or center square, defaults to False.

        Args:
            x (int): the row that the piece will be placed
            y (int): the column that the piece will be placed.
        """
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.special_sqs = False
        self.pos_cent(x, y)

    def pos(self, x):
        """Find the top or left pixel position of a given tile.

        Args:
            x (int): the row or column number

        Returns:
            (int): the top or left pixel location of the tile.
        """
        return x*(GSIZE + (GSIZE // 12)) + (GSIZE // 12)

    def pos_cent(self, x, y):
        """Find the center pixel position of a given tile.

        Stores coordinates of the tile (x_tile and y_tile) as well as the
        center pixel locations of the tiles.

        Args:
            x (int): the row number
            y (int): the column number

        Returns:
            (int, int): tuple of the center pixel location of tile
        """
        self.x_tile = x
        self.y_tile = y
        self.x_px = self.pos(x) + (GSIZE // 2)
        self.y_px = self.pos(y) + (GSIZE // 2)
        self.rect = pygame.Rect([self.x_px - GSIZE/2,
                                 self.y_px - GSIZE/2,
                                 GSIZE,
                                 GSIZE])

    def draw(self, screen):
        """Draw the piece on the board in the correct location."""
        pygame.draw.circle(screen, self.color, [self.x_px, self.y_px],
                           GSIZE/2)


class Attacker(Piece):

    """Class for all attacking pieces; inherits from Piece."""

    def __init__(self, x, y):
        """Inherit from Piece and give attacking piece a color."""
        Piece.__init__(self, x, y)
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.base_color = (149, 19, 62)
        self.color = self.base_color


class Defender(Piece):

    """Class for all defending pieces; inherits from Piece."""

    def __init__(self, x, y):
        """Inherit from Piece and give attacking piece a color."""
        Piece.__init__(self, x, y)
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.base_color = (52, 134, 175)
        self.color = self.base_color


class King(Defender):

    """Class for king; inherits from Defender."""

    def __init__(self, x, y):
        """Inherit from Piece and give attacking piece a color.

        The king can move on special squares, so special_sqs is True.
        """
        Defender.__init__(self, x, y)
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.base_color = (19, 149, 62)
        self.color = self.base_color
        self.special_sqs = True


def initialize_groups():
    """Create global groups for different pieces.

    Notes:
        The groups are defined as follows:
            Pieces: all pieces
            Attackers: all attacking pieces
            Defenders: all defending pieces, including king
            Kings: the king piece
            Current: the current selected piece
    """
    global Pieces
    global Attackers
    global Defenders
    global Kings
    global Current

    Pieces = pygame.sprite.Group()
    Attackers = pygame.sprite.Group()
    Defenders = pygame.sprite.Group()
    Kings = pygame.sprite.Group()
    Current = pygame.sprite.Group()

    Piece.groups = Pieces
    Defender.groups = Pieces, Defenders
    Attacker.groups = Pieces, Attackers
    King.groups = Pieces, Defenders, Kings


def initialize_pieces(board):
    """Create all of the game pieces and put them in groups.

    Note:
        The board layout from Board class is used for initial placement of
        pieces.

    Args:
        board (Board): the game board object
    """
    for y in range(board.dim):
        for x in range(board.dim):
            p = board.grid[y][x]
            if p == "a":
                Attacker(x, y)
            elif p == "d":
                Defender(x, y)
            elif p == "c":
                King(x, y)


def update_image(screen, board, move):
    """Update the image that the users see.

    Note:
        Right now, it redraws the whole board every time it goes through this
        function. In the future, it should only update the necessary tiles.

    Args:
        screen (pygame.Surface): game window that the user interacts with
        board (Board): the board that the pieces are on
        move (Move): the move state data
    """
    screen.fill(MARGIN_COLOR)
    for y in range(board.dim):
        for x in range(board.dim):
            xywh = [x*(GSIZE + MARGIN) + MARGIN,
                    y*(GSIZE + MARGIN) + MARGIN,
                    GSIZE,
                    GSIZE]
            pygame.draw.rect(screen, board.colors[board.grid[x][y]], xywh)

    for piece in Pieces:
        piece.draw(screen)

    """Write which player's turn it is on the bottom of the window."""
    font = pygame.font.Font(None, 36)
    if move.a_turn:
        text = font.render("Attacker's Turn!", 1, (0, 0, 0))
    else:
        text = font.render("Defender's Turn!", 1, (0, 0, 0))
    textpos = text.get_rect()
    textpos.centerx = screen.get_rect().centerx
    textpos.centery = ((HEIGHT - WIDTH) / 2) + WIDTH

    screen.blit(text, textpos)
    pygame.display.flip()


def main():
    """Main function- initializes game, acts on events, and renders game.

    The game, groups, board, move info, screen, and pieces are initialized
    first. Then, the game starts. It runs in a while loop, which will exit
    if the user closes out of the game. The only other event that it listens
    for is a MOUSEBUTTONDOWN event; the game takes action when the user clicks
    on the board. If a piece has not been selected yet and the user clicks on
    one of his pieces, then the piece will be selected and change colors. The
    user can click on this piece again to deselect it, or they can click
    on a square that is a valid move for that piece. If it is a valid move,
    the piece will move there and it is the next person's turn.

    Note:
        Three more functions must be implemented for the game to be complete.
            1) Remove captured pieces from the board.
            2) End the game if the king makes it to a corner.
            3) End the game if the king is captured.
    """
    pygame.init()
    initialize_groups()
    board = Board()
    move = Move()
    screen = pygame.display.set_mode(WINDOW_SIZE)
    initialize_pieces(board)

    while 1:
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = pygame.mouse.get_pos()
                if not move.selected:
                    if move.a_turn:
                        for piece in Attackers:
                            if piece.rect.collidepoint(pos):
                                move.select(piece)
                                Current.add(piece)
                    else:
                        for piece in Defenders:
                            if piece.rect.collidepoint(pos):
                                move.select(piece)
                                Current.add(piece)
                else:
                    if Current.sprites()[0].rect.collidepoint(pos):
                        move.select(Current.sprites()[0])
                        Current.empty()
                    elif move.is_valid_move(pos, Current.sprites()[0]):
                        move.remove_pieces()
                        move.end_turn(Current.sprites()[0])
                        Current.empty()
        update_image(screen, board, move)

if __name__ == '__main__':
    main()
