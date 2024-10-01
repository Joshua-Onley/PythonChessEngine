**Overview**

This project is a chess AI built using Python and Pygame. The AI is designed to evaluate board positions and make decisions based on the minimax algorithm. This version of the program represents the board state using binary numbers also known as bitboards.

**GUI**

The GUI was implemented using Pygame.


<img width="804" alt="Screenshot 2024-10-01 at 15 06 53" src="https://github.com/user-attachments/assets/347ce1d5-9046-430c-bfee-b24185f88db8">

**Features**
* Play against an AI opponent
* Move generation and validation (no illegal moves can be played). For a few of the precomputed tables and a couple of the bit manipulation functions, I reused existing functions from an open-source project called Snakefish by cglouch which can be found [here](https://github.com/cglouch/snakefish).
* Implements castling and en-passant
* Simple graphical user interface using Pygame
* Implements the minimax algorithm and quiescence search
* currently does not support the 50 move draw rule or the threefold repitition rule

**Table of Contents**

1. Project Setup
2. How to Play
3. AI Mechanics
4. Technologies used

**Project Setup**

To run this project you must have:
* Python 3.0 or later.
* Pygame
* Numpy

Installation: 

1. Clone the repository: git clone https://github.com/Joshua-Onley/chess-ai.git

2. run the game by running the main.py file (python main.py)

**How to Play**

* Move pieces by clicking on the piece and then clicking on the square you want to move the piece to. If the move is legal, the piece will move to that square and the AI will respond.
* Currently the project only allows the user to play as white.
* When the game is over (stalemate or checkmate) the relevant message will flash appear on the screen indicating the winner

**AI Mechanics**

The chess AI uses the minimax algorithm with alpha-beta pruning to decide its move.
* Board evaluation: The program uses piece-square tables (PSTs) to evaluate a position. This evaluation function calculates the value of a position by considering the values of the pieces on the board and then assigning additional bonuses depending on what square a specific piece is on. The code for this can be found in the PST_evaluation.py file and the piece_square_tables.py file.
* Search: the algorithm uses the minimax algorithm to find all the possible moves and simulating all of them up to a specified depth. This depth can be altered in the computer_move.py file (increasing the search depth exponentially increases the time taken for the AI to calculate its move).
* Move ordering: the program orderes checks and captures before quiet moves using the MVV-LVA technique.

**Contributing**

This is my first big coding project so there are definately improvements to be made that i am unaware of. Therefore, contributions, issues, and feature requests are welcome! 
