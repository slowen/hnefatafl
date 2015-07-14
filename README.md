# hnefatafl
Hnefatafl is an ancient Viking strategy board game. There are two teams- an attacking team and a defending team. The attacking team tries to capture the other team's king, whereas the defending team tries to get their king to one of the corners of the board.

![startgame](https://cloud.githubusercontent.com/assets/5671974/8666780/faf2ba88-29c3-11e5-8d53-a7349d4e76b4.png)

#Rules of the Game

The game is played on an 11x11 board, and the initial layout is shown above. The attacking team (red) starts first.

Every piece can move in the same way- just like a rook in chess. They can move horizontally or vertically as far as they want, but they cannot jump over any other pieces. The king (green) is the only piece that can move *onto* the center and corner tiles, but all of the other pieces can move *through* the center tile.

Players can capture their opponents pieces by sandwiching an opponents piece. The center and corners are considered hostile territory, so they can be used to sandwich/capture an opponent. For instance, if the defending player moves their piece such that they sandwich an attacking piece between their piece and the corner, then the attacking piece is removed from the board.

The king is captured when is is enclosed on all four sides.

#Running the Game
The only imported packages are sys and pygame. To install pygame on Unix: 
```
sudo apt-get install python-pygame
```

To run the file, simply run:
```
python hnefatafl.py
```

While in the game, pressing ```r``` will ask the user if they want to restart the game, which they can confirm with ```y``` or ```n```. Also, when one player has won the game, they can start a new game by pressing ```y``` or exit the game by pressing ```n```.

The text on the bottom will tell you whose turn it is (red is the attacker, blue is the defender, and the king is green).

#Limitations
The game is not quite finished yet. It cannot detect if there is a draw game. Other than that, it is fully functional.

#Future
Some of the underlying data representations will be altered. In order to detect draws quickly and for AI to be implemented intelligently, it makes sense to store the move states as bitboards. That way, it is very simple and computationally cheap to determine what moves are valid, and the computer can quickly iterate through many possible playouts to chose its next move.

#Resources
If you want to learn more about Hnefatafl, check out http://tafl.cyningstan.com/. It explains the game really well and has some great advice on strategy for both sides.
