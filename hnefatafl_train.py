"""
A two player version of Hnefatafl, a Viking board game.

A full description of the game can be found here: http://tinyurl.com/2lpvjb

Author: Jon Dumm
Date: 4/4/2019

"""

import sys
import pygame
from pygame.locals import *
import time
import random
import numpy as np
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Dense, Activation, Dropout
from tensorflow.keras.optimizers import SGD
from tensorflow.keras.models import load_model
import hnefatafl as tafl


def run_game_hahd(screen):
    """ Start a human vs human game
    """
    run_game(screen)

def run_game_hacd(screen):
    """ Start a human attacker vs computer defender game
    """
    #run_game(screen)
    pass

def run_game_cahd(screen):
    """ Start a computer attacker vs human defender game
    """
    #run_game(screen)
    pass

def run_game_random(screen=None):

    """Start a new game with random (legal) moves.

    TODO: Add description

    """
    board = tafl.Board()
    move = tafl.Move()
    talf.initialize_pieces(board)
    num_moves = 0
    while 1:
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
               pass
        
        '''
        if move.a_turn:
            text = "Attacker's Turn: Move {}".format(num_moves)
            print(text)
        if not move.a_turn:
            text = "Defender's Turn: Move {}".format(num_moves)
            print(text)
        '''
        #print(move.to_array())
        do_random_move(move)
        num_moves += 1
        if(num_moves >= 1000):
            print("Draw game after {} moves".format(num_moves))
            return False

        """Text to display on bottom of game."""
        text2 = None
        if move.escaped:
            text = "King escaped! Defenders win!"
            print(text)
            text2 = "Play again? y/n"
            return False
        if move.king_killed:
            text = "King killed! Attackers win!"
            print(text)
            text2 = "Play again? y/n"
            return False
        if move.restart:
            text = "Restart game? y/n"
            print(text)
            return False
        if screen is not None:
            talf.update_image(screen, board, move, text)
            pygame.display.update()
        #time.sleep(1)

def do_random_move(move):
    if move.a_turn:
        pieces = tafl.Attackers
    else:
        pieces = tafl.Defenders
    while 1:
        #rn = int(random.random() * len(pieces.sprites()))
        #piece = pieces.sprites()[rn]
        piece = random.choice(pieces.sprites())
        move.select(piece)
        tafl.Current.add(piece)
        #print("Piece at: {} {}".format(piece.x_tile,piece.y_tile))
        #print("  Valid Moves: {}".format(move.vm))
        if len(move.vm)==0:
            #print("No valid moves...")
            move.select(piece)
            tafl.Current.empty()
            continue
        else:
            pos = random.choice(tuple(move.vm))
            #print("Moving piece to: {}".format(pos))
            if move.is_valid_move(pos, tafl.Current.sprites()[0], True):
                if tafl.Current.sprites()[0] in tafl.Kings:
                    move.king_escaped(tafl.Kings)
                if move.a_turn:
                    move.remove_pieces(tafl.Defenders, tafl.Attackers, tafl.Kings)
                else:
                    move.remove_pieces(tafl.Attackers, tafl.Defenders, tafl.Kings)
                move.end_turn(tafl.Current.sprites()[0])
                tafl.Current.empty()
            break

def run_game_cacd_RL(attacker_model,defender_model,screen=None):
    """Start and run one game of computer vs computer hnefatafl.

    TODO: Add description

    """
    board = tafl.Board()
    move = tafl.Move()
    tafl.initialize_pieces(board)
    a_game_states = []
    a_predicted_scores = []
    d_game_states = []
    d_predicted_scores = []
    num_moves = 0
    while 1:
        if screen is not None:
            for event in pygame.event.get():
                if event.type == QUIT:
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    pass


        num_moves += 1
        if(num_moves >= 1000):
            print("Draw game after {} moves".format(num_moves))
            a_predicted_scores.append(0.0)
            d_predicted_scores.append(0.0)
            return a_game_states,a_predicted_scores[1:], d_game_states,d_predicted_scores[1:] # i.e. the corrected scores from RL

        if move.a_turn:
            #print("Attacker's Turn: Move {}".format(num_moves))
            game_state,predicted_score = do_best_move(move,attacker_model)
            a_game_states.append(game_state)
            a_predicted_scores.append(predicted_score)
        else:
            #print("Defender's Turn: Move {}".format(num_moves))
            #game_state,predicted_score = do_best_move(move,defender_model)
            game_state = do_random_move(move)
            predicted_score = (random.random()-0.5) * 2
            d_game_states.append(game_state)
            d_predicted_scores.append(predicted_score)

        """Text to display on bottom of game."""
        if move.escaped:
            print("King escaped! Defenders win!")
            attacker_outcome = -1.0
            #print(a_predicted_scores[-1])
            a_predicted_scores.append(-1.0)
            d_predicted_scores.append(+1.0)
            return a_game_states,a_predicted_scores[1:], d_game_states,d_predicted_scores[1:] # i.e. the corrected scores from RL
        if move.king_killed:
            print("King killed! Attackers win!")
            #print(a_predicted_scores[-1])
            a_predicted_scores.append(+1.0)
            d_predicted_scores.append(-1.0)
            return a_game_states,a_predicted_scores[1:], d_game_states,d_predicted_scores[1:] # i.e. the corrected scores from RL
        if screen is not None:
            tafl.update_image(screen, board, move, "", "")
            pygame.display.update()



def do_best_move(move,model):
    """ Function to try all possible moves and select the best according to the model provided
    """

    game_state = game_state_to_array() # Preserves the current game state

    if move.a_turn:
        pieces = tafl.Attackers
    else:
        pieces = tafl.Defenders

    best_score = -1.0
    best_piece = None
    best_move = None
    best_game_state = None
    #len("N Pieces: ",len(pieces))
    for piece in pieces:
        move.select(piece) # Move class defines all possible valid moves
        tafl.Current.add(piece)
        if len(move.vm)==0: # No valid moves for this piece, move on
            move.select(piece)
            tafl.Current.empty()
            continue
        else:
            for m in move.vm:
                # Swap game state for candidate move
                temp = game_state[piece.x_tile][piece.y_tile]
                game_state[piece.x_tile][piece.y_tile] = 0
                game_state[m[0]][m[1]] = temp

                try: # model.predict crashed once... 
                    score = model.predict(game_state.reshape(1,11*11))[0][0]
                except:
                    score = -1.0
                    #score = random.random()

                if score > best_score:
                    best_score = score
                    best_piece = piece
                    best_move  = m

                # Reverse swap to restore game state
                temp = game_state[m[0]][m[1]]
                game_state[piece.x_tile][piece.y_tile] = temp
                game_state[m[0]][m[1]] = 0
        move.select(piece) # Deselect
        tafl.Current.empty()

    move.select(best_piece)
    tafl.Current.add(best_piece)
    #print("Moving piece to: {}".format(pos))
    if move.is_valid_move(best_move,tafl.Current.sprites()[0], True):
        if tafl.Current.sprites()[0] in tafl.Kings:
            move.king_escaped(tafl.Kings)
        if move.a_turn:
            move.remove_pieces(tafl.Defenders, tafl.Attackers, tafl.Kings)
        else:
            move.remove_pieces(tafl.Attackers, tafl.Defenders, tafl.Kings)
        move.end_turn(tafl.Current.sprites()[0])
        tafl.Current.empty()
        #return best_score,game_state_to_array()
        # Just do this by hand for efficiency
        temp = game_state[best_piece.x_tile][best_piece.y_tile]
        game_state[best_piece.x_tile][best_piece.y_tile] = 0
        game_state[best_move[0]][best_move[1]] = temp

        #print(game_state,best_score)
        return game_state,best_score
    else:
        print("ERROR: Efficient move logic failed... Fix!")
        sys.exit(1)


def initialize_random_nn_model():

        print("Initializing randomized NN model")
        model = Sequential()
        model.add(Dense(2*11*11, input_dim=11*11,kernel_initializer='normal', activation='relu'))
        model.add(Dropout(0.1))
        model.add(Dense(11*11, kernel_initializer='normal',activation='relu'))
        model.add(Dropout(0.1))
        # model.add(Dense(9, kernel_initializer='normal',activation='relu'))
        # model.add(Dropout(0.1))
        # model.add(Dense(5, kernel_initializer='normal',activation='relu'))
        model.add(Dense(1,kernel_initializer='normal'))

        learning_rate = 0.001
        momentum = 0.8

        sgd = SGD(lr=learning_rate, momentum=momentum, nesterov=False)
        model.compile(loss='mean_squared_error', optimizer=sgd)
        model.summary()
        return model

def game_state_to_array():
    """2D Numpy array representation of game state for ML model.
    """
    if tafl.Attackers is None or tafl.Defenders is None or tafl.Kings is None:
        print("Game not properly initialized.  Exiting.")
        sys.exit(1)
    arr = np.zeros((11,11),dtype=int)

    for p in tafl.Attackers:
        arr[p.x_tile][p.y_tile] = '1'
    for p in tafl.Defenders:
        arr[p.x_tile][p.y_tile] = '2'
    for p in tafl.Kings:
        arr[p.x_tile][p.y_tile] = '3'

    return arr

def unison_shuffled_copies(a, b):
    assert len(a) == len(b)
    p = np.random.permutation(len(a))
    return a[p], b[p]

def smooth_corrected_scores(corrected_scores,num_to_smooth=10):
    """ Smooth out the lead up to the final state for faster learning
    """
    num_to_smooth = min(num_to_smooth ,len(corrected_scores))
    
    for i in range(num_to_smooth-1):
        corrected_scores[-1*(i+2)] = (corrected_scores[-1*(i+2)] + corrected_scores[-1*(i+1)]) / 2. # Average

def main():
    """Main function- initializes screen and starts new games."""
    interactive = True 
    if interactive:
        pygame.init()
        screen = pygame.display.set_mode(tafl.WINDOW_SIZE)
    else:
        screen = None
    tafl.initialize_groups()

    #attacker_model = initialize_random_nn_model()
    attacker_model = load_model('attacker_model_after_340_games.h5')
    defender_model = initialize_random_nn_model()

    #train = True
    num_train_games = 340
    #while train:
    while num_train_games < 10000:
        num_train_games += 1
        #play = tafl.run_game(screen)
        #play = run_game_cacd(screen)
        #a_game_states,a_corrected_scores, d_game_states,d_corrected_scores = run_game_cacd_RL(attacker_model,defender_model)
        a_game_states,a_corrected_scores, d_game_states,d_corrected_scores = run_game_cacd_RL(attacker_model,defender_model,screen)
        #play = run_game_cacd_RL(attacker_model,defender_model,screen)
        print("Game finished in {} moves".format(len(a_corrected_scores)+len(d_corrected_scores)))
        #a_game_states,a_corrected_scores = unison_shuffled_copies(a_game_states,a_corrected_scores)
        smooth_corrected_scores(a_corrected_scores)
        attacker_model.fit(np.array(a_game_states).reshape(-1,11*11),np.array(a_corrected_scores),epochs=1,batch_size=1,verbose=0)
        if(num_train_games%10==0):
            attacker_model.save('attacker_model_after_{}_games.h5'.format(num_train_games))

        #time.sleep(5)
        tafl.cleanup()

if __name__ == '__main__':
    main()
