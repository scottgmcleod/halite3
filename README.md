# Schildpad

## TODO
- (Stefan) Isolate parameters that should be trained.
- (Stefan) Check qualitative behavior, check if parameters are broad enough, or that rules needs to reimplemented. Check if some features can be removed (global factor, expand_radius, ..).
- (Stefan/Jonne/Renko) Check lost games and see what goes wrong (check mlomb for timeouts):
    - Ship graveyards (mostly with reCurs3)(maybe let him solve it?)
- (Renko/Jonne) Improve ship spawn decision. Estimate return_on_investment(n_turns_left, n_ships, halite_available, n_players, map). Make a fit on real data, plot measured return_on_investment vs predicted return_on_investment.
- (Jonne) Optimize constants: Use gradient decent algorithm. One constant/dimension at the time, one step all together. Define constants per map size and players. Train parameter subset at a time? Train against fixed opponents (old versions)?

## NOT TODO
- Performance improvements (linear_sum_assignment in Cython)(simpler/faster shortest path algorithm)(PyCUDA GPU)(avoid calculations: not can_move() implies stay_still(), so no neighbour index shortest path necessary)(reuse calculations: attempt for simple_distances was probably slow because it made a slice, make python list of 1D arrays instead)(smaller clusters for linear_sum_assignment, ships in the smaller cluster cannot use all moves to avoid collisions in Schedule).
- Improve attack and enemy_threat (Tit-for-tat, keep track of attacks on stationary ships as indication of aggressiveness)(distinction 2player and 4player: for example, attack more aggressively when you have more ships than the opponent in 2player games)(loop over enemy ships and find good targets, taking into consideration our ships and their dropoffs, pick attacking ships based on their distance/best_average_halite/ship.halite_amount and make sure there is a ship to pick up the loot)(increase aggressiveness in endgame)(find a balance with threat_edge_costs, so that it correctly supports both attacking and fleeing)
- Predict what enemy ship will do (based on cell/ship halite, ships nearby, distance to dropoff, can_move)(use ML, possibly even predict against whom we are playing)(make a cost array like for our own ships to predict next move).
- Better manage tanking turns for ships with very low cargo.
- Make sure you never end up with slightly less than 1000 halite when you need 1000 to create a ship.
- Estimate investment return for dropoffs.
- Do more with ships that have nothing to lose: Troll/attack the enemy base. Protect full ships.
- Time dependent parameters (parameters such as those in threat_edge_costs, because losing a ship at the beginning of the game is much worse than at the end)(a+(b-a)(t/T) if t<T else b+(c-b)(t-T)/(Tmax-T))(instead of depending on time/turnnumber, let a parameter depend on available halite on the map, or something else)(find patterns in training data to determine what the parameters should depend on)
- Try to get bonus without giving the opponent a bonus (Encourage spreading of ships when near the enemy).
- Avoid going to high halite cells with ships that are nearly full (only mine cells that you can mine to the bottom).
- Calculate cost array for fake ship on dropoff, to be used in the return to dropoff decision (estimate average halite for even more turns, including dropping off halite at a dropoff).

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
* mapdata.py, module with useful general functions and MapData

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
