# *********************************************************************
# *  Daniel Río Alonso, Adrian Cañizares Salgado, Mario Calero López  *
# *********************************************************************

import arguments_manager as am
import game as g
import constants as ct

if __name__ == "__main__":
    n_stages, filename = am.parse_args()
    stages_ok, file_ok = am.check_args(n_stages, filename)

    if stages_ok and file_ok:
        print("Start the game with", n_stages, "stages and", ct.n_players, "players.")
        try:
            game = g.Game(n_stages, filename)
            game.play_game()
        except KeyboardInterrupt:
            print("Execution interrupted by user.")

    else:
        if not file_ok:
            print("The format of the chosen file is incorrect. You must provide a filename"
                  "that ends either with .txt or .json. Finishing program.")
            pass

        if not stages_ok:
            print("The number of stages must be between 1 and 10. Finishing program.")
            pass
