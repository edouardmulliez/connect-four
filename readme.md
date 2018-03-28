# AI for connect4

## About the application

This app is a game of Connect Four, where the player plays against the computer. Different level of difficulty can be chosen.
It is written in Python3, using the Kivy for the interface.

## Installation

You will need an environment with Python 3 and Kivy installed. Instructions to install Kivy can be found [here](https://kivy.org/docs/installation/installation.html).

On OSX, you can use the file `install_kivy.sh` of this repository. You will however need to have [homebrew](https://brew.sh/index_fr) installed beforehand.

## Running the app

To start the app, in Terminal, type:

```bash
cd connect-four
python connect-four-app.py
```

## Application screenshots

**Start menu**:

![start menu](screenshots/start-menu.png)

**During the game**:

![animation.png](screenshots/animation.png)

**Game results**:

![results](screenshots/results.png)

## How does it work?

The AI of this app is built using the [minimax](https://en.wikipedia.org/wiki/Minimax) algorithm. To speed up the algorithm, the [alpha-beta pruning](https://en.wikipedia.org/wiki/Alpha%E2%80%93beta_pruning) is used. 

In the minimax algorithm, we need to define an evaluation function to score a given grid with coins from both players. The evaluation function is implemented as such:
- For each player, we count the number of alignment of 1, 2 or 3 coins which can be completed to obtain 4 coins in a row
- An alignment of 1 coin has a value of 1, 2 coins a value of 10, 3 coins a value of 100.
- The final score is the difference between the value of player 1 and player 2.

The different levels of difficulty that the user can choose correspond to the number of moves considered for the minimax algorithm. Easy, Medium and Hard levels respectively correspond to 3, 4 and 5 moves.

