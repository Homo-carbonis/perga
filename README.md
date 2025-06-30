# Perga
A geometric strategy game.

## About
Perga is a concept for an abstract strategy game I thought of while doodling circles. The idea is that players take turns placing different sizes discs on a board. A disc touching more hostile than friendly neighbours is captured and a point is awarded to the capturing player. The strategy lies in using larger discs to block the other player and smaller discs to fit into narrower spaces, and in capturing multiple pieces at once in "cascades".

There is a lot of room for experimentation with the rules on capturing, boundaries, etc, to produce the most interesting game.

## How to play
Players take it in turns to drag discs from their pile onto the circular board. A piece touching more hostile than friendly pieces will be captured at the end of the turn. The player with the most pieces captured when both piles are empty wins the game.


## Name
Perga was an ancient city located in modern day Turkey. It was home to the Greek geometer Apollonius of Perga who gave his name to the Apollonian Gasket fractal which a game of Perga resembles.

## Implementation
To make experimentation easy I put together a quick implementation in pygame. Placing the discs on a virtual board requires a practical solution to the famous Problem of Apollonius for two fixed discs and a given radius.

## Running the game
```
python -m pip install -r requirements.txt
python main.py
```
