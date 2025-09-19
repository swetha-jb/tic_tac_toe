import sys, os, types
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'py-tic-tac-toe')))

# Auto-mock tkinter for headless environments
try:
    import tkinter as tk
except ImportError:
    import sys, types
    class _WidgetMock:
        def __init__(self, *a, **k): self._text = ""
        def config(self, **kwargs): 
            if "text" in kwargs: self._text = kwargs["text"]
        def cget(self, key): return self._text if key == "text" else None
        def get(self): return self._text
        def grid(self, *a, **k): return []
        def pack(self, *a, **k): return []
        def place(self, *a, **k): return []
        def destroy(self): return None
        def __getattr__(self, item): return lambda *a, **k: None
    tk = types.ModuleType("tkinter")
    for widget in ["Tk","Label","Button","Entry","Frame","Canvas","Text","Scrollbar","Checkbutton",
                "Radiobutton","Spinbox","Menu","Toplevel","Listbox"]:
        setattr(tk, widget, _WidgetMock)
    for const in ["N","S","E","W","NE","NW","SE","SW","CENTER","NS","EW","NSEW"]:
        setattr(tk, const, const)
    sys.modules["tkinter"] = tk

import pytest
from unittest.mock import patch

# Assume the source code is in a file named Main.py
from Main import TicTacToe


@pytest.fixture
def tic_tac_toe_game():
    game = TicTacToe()
    game.create_board()
    return game


def test_create_board(tic_tac_toe_game):
    assert tic_tac_toe_game.board == [['-', '-', '-'], ['-', '-', '-'], ['-', '-', '-']]
    assert len(tic_tac_toe_game.board) == 3
    assert all(len(row) == 3 for row in tic_tac_toe_game.board)


@patch('Main.random.randint')
def test_get_random_first_player_returns_0_or_1(mock_randint):
    mock_randint.return_value = 0
    game = TicTacToe()
    assert game.get_random_first_player() in [0, 1]
    mock_randint.assert_called_once_with(0, 1)

    mock_randint.return_value = 1
    assert game.get_random_first_player() in [0, 1]
    assert mock_randint.call_count == 2


def test_fix_spot(tic_tac_toe_game):
    tic_tac_toe_game.fix_spot(0, 0, 'X')
    assert tic_tac_toe_game.board[0][0] == 'X'
    tic_tac_toe_game.fix_spot(1, 2, 'O')
    assert tic_tac_toe_game.board[1][2] == 'O'


def test_has_player_won_row(tic_tac_toe_game):
    tic_tac_toe_game.board = [['X', 'X', 'X'], ['-', '-', '-'], ['-', '-', '-']]
    assert tic_tac_toe_game.has_player_won('X') is True


def test_has_player_won_column(tic_tac_toe_game):
    tic_tac_toe_game.board = [['X', '-', '-'], ['X', '-', '-'], ['X', '-', '-']]
    assert tic_tac_toe_game.has_player_won('X') is True


def test_has_player_won_diagonal_main(tic_tac_toe_game):
    tic_tac_toe_game.board = [['X', '-', '-'], ['-', 'X', '-'], ['-', '-', 'X']]
    assert tic_tac_toe_game.has_player_won('X') is True


def test_has_player_won_diagonal_anti(tic_tac_toe_game):
    tic_tac_toe_game.board = [['-', '-', 'X'], ['-', 'X', '-'], ['X', '-', '-']]
    assert tic_tac_toe_game.has_player_won('X') is True


def test_has_player_won_no_win(tic_tac_toe_game):
    tic_tac_toe_game.board = [['X', 'O', '-'], ['-', 'X', 'O'], ['O', '-', 'X']]
    assert tic_tac_toe_game.has_player_won('X') is False
    assert tic_tac_toe_game.has_player_won('O') is False


def test_is_board_filled_when_full(tic_tac_toe_game):
    tic_tac_toe_game.board = [['X', 'O', 'X'], ['O', 'X', 'O'], ['O', 'X', 'O']]
    assert tic_tac_toe_game.is_board_filled() is True


def test_is_board_filled_when_not_full(tic_tac_toe_game):
    tic_tac_toe_game.board = [['X', 'O', '-'], ['O', 'X', 'O'], ['O', 'X', 'O']]
    assert tic_tac_toe_game.is_board_filled() is False


def test_swap_player_turn_x_to_o(tic_tac_toe_game):
    assert tic_tac_toe_game.swap_player_turn('X') == 'O'


def test_swap_player_turn_o_to_x(tic_tac_toe_game):
    assert tic_tac_toe_game.swap_player_turn('O') == 'X'


@patch('builtins.print')
@patch('builtins.input', return_value='1 1')
def test_start_makes_a_move(mock_input, mock_print, tic_tac_toe_game):
    # Mock get_random_first_player to always return 1 ('X' starts)
    tic_tac_toe_game.get_random_first_player = lambda: 1
    tic_tac_toe_game.start()
    mock_print.assert_any_call('Player X turn')
    assert tic_tac_toe_game.board[0][0] == 'X'


@patch('builtins.print')
@patch('builtins.input', side_effect=['1 1', '1 2', '2 1', '2 2', '3 1'])
def test_start_player_x_wins(mock_input, mock_print, tic_tac_toe_game):
    tic_tac_toe_game.get_random_first_player = lambda: 1  # X starts
    tic_tac_toe_game.start()
    mock_print.assert_any_call('Player X wins the game!')


@patch('builtins.print')
@patch('builtins.input', side_effect=['1 1', '1 2', '2 1', '2 2', '3 1', '3 2', '1 3', '2 3', '3 3'])
def test_start_draw(mock_input, mock_print, tic_tac_toe_game):
    tic_tac_toe_game.get_random_first_player = lambda: 1  # X starts
    tic_tac_toe_game.start()
    mock_print.assert_any_call('Match Draw!')


@patch('builtins.print')
@patch('builtins.input', side_effect=['1 1', '1 1', '1 2'])
def test_start_invalid_move_already_taken(mock_input, mock_print, tic_tac_toe_game):
    tic_tac_toe_game.get_random_first_player = lambda: 1  # X starts
    tic_tac_toe_game.start()
    mock_print.assert_any_call('Invalid spot. Try again!')
    assert tic_tac_toe_game.board[0][0] == 'X'
    assert tic_tac_toe_game.board[0][1] == 'O'


@patch('builtins.print')
@patch('builtins.input', side_effect=['1 4', '1 1'])
def test_start_invalid_move_out_of_bounds(mock_input, mock_print, tic_tac_toe_game):
    tic_tac_toe_game.get_random_first_player = lambda: 1  # X starts
    tic_tac_toe_game.start()
    mock_print.assert_any_call('Invalid spot. Try again!')
    assert tic_tac_toe_game.board[0][0] == 'X'
    assert tic_tac_toe_game.board[0][1] == '-'
