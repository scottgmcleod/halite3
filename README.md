# Schildpad
## 1. TODO
### 1.1. TODO - dropoff points
* location is right 
    * distance between enemy drop off points
    * closer to the enemy to 'steal' more halite with higher changes on bonus
    * other own ships in neighbourhood
    * ratio between density and number of ships in neighbourhood

### 1.2. TODO - optimize vars
* rethink independent variables and minimize amount 
* run some kind of monte carlo (ML) to determine optimal set of vars
### 1.3. TODO - ...
### 1.4. TODO - ...  
### Bug1
When cargo of ship == 1000
https://halite.io/play/?game_id=1669676&replay_class=1&replay_name=replay-20181110-193501%2B0000-1541878392-64-64-1669676
https://halite.io/play/?game_id=1672809&replay_class=1&replay_name=replay-20181110-205532%2B0000-1541883284-64-64-1672809


## Rationale
###

# Halite III
General information from Halite III adjusted to our project.

## Halite III components
* /docs, contains API of the game of Halite 
* /hlt, contains modifiable helper functions for your bot
* /misc, contains command scripts and executables to run and example game (.bat for windows) (.sh for MacOS, Linux)
* /replays, contains replays and error files
* MyBot.py, schildpad bot
* scheduler.py, module to assign ships to destinations (distance is 0 to mapsize)
* schedule.py, module to make next step schedule (distance is 0 or 1)
* utility.py, module with useful general functions and MapData

## Testing your bot locally
* Run run_game.bat (Windows) and run_game.sh (MacOS, Linux) to run a game of Halite III. By default, these scripts run a game of your MyBot.py bot vs. itself.  You can modify the board size, map seed, and the opponents of test games using the CLI.

## CLI
The Halite executable comes with a command line interface (CLI). Run `$ ./halite --help` to see a full listing of available flags.


## Local viewer
* Fluorine can be used to view replays locally https://github.com/fohristiwhirl/fluorine/releases

## Submitting your bot
* Zip your MyBot.{extension} file and /hlt directory together.
* Submit your zipped file here: https://beta.halite.io/play-programming-challenge

## Compiling your bot on our game servers
* Your bot has `10 minutes` to install dependencies and compile on the game server.
* You can run custom commands to set up your bot by including an `install.sh` file alongside `MyBot.{ext}`. This file will be executed and should be a Bash shell script. You must include the shebang line at the top: `#!/bin/bash`.
* For Python, you may install packages using pip, but you may not install to the global package directory. Instead, install packages as follows: `python3.6 -m pip install --system --target . numpy`