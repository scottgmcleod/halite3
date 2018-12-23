import yaml
import time
from subprocess import check_output
import os

from tqdm import tqdm
import numpy as np
from parse import parse_replay_folder, parse_replay_file, evaluate_folder


class Calibrator:
    """Calibrator object to start or load a stopped Calibration of parameterrs for a halite bot.
    pars --> parameters
    args --> arguments
    iter --> iteration
    n    --> number
    dir  --> directory
    State of the parameters not managed in object, but in the yaml files.
    """

    def __init__(self, mapsize, n_player, n_games, n_iter,
                 pars_reference='parameters.yaml', dir_replay=r'replays', bot_path=r'MyBot.py'):
        self.param = None
        self.iter = 0
        self.bot_path = bot_path

        self.mapsize = mapsize
        self.n_player = n_player
        self.n_games = n_games
        self.n_iter = n_iter
        self._dir_replay = dir_replay
        self._dir_output = self.set_dir_output()
        self._dir_pars = os.path.join(self._dir_output, 'pars')
        self._pars_reference_file = pars_reference
        self._pars_reference = self.get_parameters(self._pars_reference_file)
        self._pars_default = self.get_parameters(self._pars_reference_file)

    def __repr__(self):
        """Representation of Calibrator object"""
        return f'Calibrator({self.mapsize}, {self.n_player}, {self.n_games}, {self.n_iter}'

    def set_dir_output(self):
        """Folder where the hlt and errorlogs will be written"""
        return os.path.join(self._dir_replay,
                            f'calibrator_'
                            f'p{self.n_player}_'
                            f's{self.mapsize}_'
                            f'd{time.strftime("%Y%m%d")}_'
                            f't{time.strftime("%H%M%S")}')

    @property
    def args(self):
        """cmd arguments to run a halite game"""
        args = ['misc/halite.exe', '-vvv',
                '--replay-directory', self._dir_iteration,
                '--width', str(self.mapsize),
                '--height', str(self.mapsize)]
        if self.n_player == 2:
            return args + [self.get_bot(self._pars_high_file), self.get_bot(self._pars_high_file)]
        elif self.n_player == 4:
            return args + [self.get_bot(self._pars_reference_file),
                           self.get_bot(self._pars_default_file),
                           self.get_bot(self._pars_low_file),
                           self.get_bot(self._pars_high_file)]
        raise NotImplementedError

    @property
    def _pars_default_file(self):
        """File with the default parameters, which update each iteration based on the gradients per parameter"""
        return os.path.join(self._dir_pars, f'parameters_{self.iter}_default.yaml')

    @property
    def _pars_high_file(self):
        """File with the parameters and a parameter with one high step"""
        return os.path.join(self._dir_pars, f'parameters_{self.iter}_high_{self.param}.yaml')

    @property
    def _pars_low_file(self):
        """File with the parameters and a parameter with one low step"""
        return os.path.join(self._dir_pars, f'parameters_{self.iter}_low_{self.param}.yaml')

    @property
    def _dir_iteration(self):
        """Folder for replay and error files for an iteration"""
        return os.path.join(self._dir_output, f'i{self.iter}_{self.param}')

    @property
    def _pars_low(self):
        """Parameters of the high iteration"""
        return self.get_parameters(self._pars_low_file)

    @property
    def _pars_high(self):
        """Parameters of the high iteration"""
        return self.get_parameters(self._pars_high_file)

    @property
    def _params(self):
        """Get list of the parameters used in the iteration"""
        params = []
        if self.n_player == 2:
            params.append(self._pars_low[self.param])
            params.append(self._pars_high[self.param])
        elif self.n_player == 4:
            params.append(self._pars_reference[self.param])
            params.append(self._pars_default[self.param])
            params.append(self._pars_low[self.param])
            params.append(self._pars_high[self.param])
        return np.array(params)

    def get_bot(self, pars):
        """cmd argument to the a single bot with certain parameters in a yaml file"""
        return f'python {self.bot_path} {pars}'

    def start(self):
        """Run game from commandline"""
        os.mkdir(self._dir_output)
        os.mkdir(self._dir_pars)
        while self.iter < self.n_iter:
            self.set_parameters(self._pars_default_file, self._pars_default)
            for param in self._pars_reference.keys():
                self.param = param
                os.mkdir(self._dir_iteration)
                if self.iter == 0:
                    step = self._pars_default[param] * 0.5
                self.set_parameter(file=self._pars_low_file, step=-step)
                self.set_parameter(file=self._pars_high_file, step=step)
                for _ in tqdm(range(self.n_games), total=self.n_games):
                    check_output(self.args).decode("ascii")
                # update default parameter
                self.set_parameter(
                    file=self._pars_default_file,
                    step=self._pars_default[self.param] - self.evaluate())
                self.evaluate()
                # determine gradient and step of pamam: step = +/-gradient * reference_params[param]
                # update step
            self.iter += 1
        return 0

    def load(self, folder):
        """Load a calibration state"""
        raise NotImplementedError

    def set_parameter(self, file, step):
        """Set the parameters to be used in a bot"""
        pars = self._pars_default.copy()
        pars[self.param] = pars[self.param] + step
        return self.set_parameters(file, pars)

    def reset_parameters(self, file):
        """Reset the parameters back to the default parameters"""
        with open(file, 'w') as f:
            return yaml.dump(self._pars_default, f, default_flow_style=False)

    def result(self):
        return evaluate_folder(self._dir_iteration)

    def evaluate(self):
        """Evaluates the result of the iteration step in the calibration"""
        result = self.result()
        return (self.n_player / result.sum() * result * self._params).mean()

    @staticmethod
    def set_parameters(file, pars):
        """Set a dict of parameters to be calibrated to file"""
        with open(file, 'w') as f:
            return yaml.dump(pars, f, default_flow_style=False)

    @staticmethod
    def get_parameters(file):
        """Get a dict of parameters to be calibrated"""
        with open(file) as f:
            return yaml.load(f)


if __name__ == '__main__':
    calibrator = Calibrator(mapsize=32, n_player=4, n_games=100, n_iter=1)
    calibrator.start()