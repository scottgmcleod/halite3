from hlt import Direction, Position, constants
from scipy.optimize import linear_sum_assignment
from scipy.sparse.csgraph import dijkstra, shortest_path
from scipy.sparse import csr_matrix
import numpy as np
import logging, math, time


class Assignment:
    """An assignment of a ship to a destination."""

    def __init__(self, ship, destination):
        self.ship = ship
        self.destination = destination

    def to_command(self, target_cell):
        """Return command to move its ship to a target cell."""
        target_cell.mark_unsafe(self.ship)

        if target_cell == game_map[self.ship]:
            return self.ship.stay_still()

        origin = self.ship.position
        for direction in Direction.get_all_cardinals():
            if target_cell == target(origin, direction):
                return self.ship.move(direction)


class Schedule:
    """Keeps track of Assignments and translates them into a command list."""

    edge_data = None

    def __init__(self, _game):
        global game, game_map, me
        game = _game
        game_map = game.game_map
        me = game.me
        self.assignments = []
        self.halite = self.available_halite()
        self.graph = self.create_graph()
        self.dist_matrix, self.indices = self.shortest_path()

    def available_halite(self):
        """Get an array of available halite on the map."""
        m = game_map.height * game_map.width
        return np.array([index_to_cell(i).halite_amount for i in range(m)])

    def initialize_edge_data(self):
        """Store edge_data for create_graph() on the class for performance."""
        m = game_map.height * game_map.width
        col = np.array([j for i in range(m) for j in neighbours(i)])
        row = np.repeat(np.arange(m), 4)
        Schedule.edge_data = (row, col)

    def create_graph(self):
        """Create a matrix representing the game map graph.

        Note:
            The edge cost 1.0 + cell.halite_amount / 1000.0 is chosen such
            that the shortest path is mainly based on the number of steps
            necessary, but also slightly incorporates the halite costs of
            moving. Therefore, the most efficient path is chosen when there
            are several shortest distance paths.
        """
        if Schedule.edge_data is None:
            self.initialize_edge_data()
        edge_costs = np.repeat(1.0 + self.halite / 1000.0, 4)
        edge_data = Schedule.edge_data
        m = game_map.height * game_map.width
        return csr_matrix((edge_costs, edge_data), shape=(m, m))

    def shortest_path_indices(self):
        """Determine the indices for which to calculate the shortest path.

        Notes:
            - We also need the neighbours, because their results are used to
                generate the cost matrix for linear_sum_assignment().
            - list(set(a_list)) removes the duplicates from a_list.
        """
        indices = [cell_to_index(game_map[ship]) for ship in me.get_ships()]
        neighbour_indices = [j for i in indices for j in neighbours(i)]
        return list(set(indices + neighbour_indices))

    def shortest_path(self):
        """Calculate a perturbed distance from interesting cells to all cells.

        Possible performance improvements:
            - dijkstra's limit keyword argument.
            - reduce indices, for example by removing returning/mining ships.
            - reduce graph size, only include the relevant part of the map.
        """
        indices = self.shortest_path_indices()
        dist_matrix = dijkstra(self.graph, indices=indices)
        return dist_matrix, indices

    def get_distances(self, origin_index):
        """Get an array of perturbed distances from some origin cell."""
        return self.dist_matrix[self.indices.index(origin_index)]

    def get_distance(self, origin_index, target_index):
        """Get the perturbed distance from some cell to another."""
        return self.get_distances(origin_index)[target_index]

    def assign(self, ship, destination):
        """Assign a ship to a destination."""
        assignment = Assignment(ship, destination)
        self.assignments.append(assignment)

    def initial_cost_matrix(self):
        """Initialize the cost matrix with high costs for every move.

        Note:
            The rows/columns of the cost matrix represent ships/targets. An
            element in the cost matrix represents the cost of moving a ship
            to a target. Some elements represent moves that are not possible
            in a single turn. However, because these have high costs, they will
            never be chosen by the algorithm.
        """
        n = len(self.assignments)  # Number of assignments/ships.
        m = game_map.width * game_map.height  # Number of cells/targets.
        return np.full((n, m), 99999999999.9)

    def reduce_feasible(self, cost_matrix):
        """Reduce the cost of all feasible moves for all ships."""
        for k, assignment in enumerate(self.assignments):
            ship = assignment.ship
            destination = assignment.destination
            origin_index = cell_to_index(game_map[ship])
            target_index = cell_to_index(game_map[destination])
            cost = self.get_distance(origin_index, target_index)
            cost_matrix[k][origin_index] = cost - 0.1
            if can_move(ship):
                for neighbour_index in neighbours(origin_index):
                    cost = self.get_distance(neighbour_index, target_index)
                    cost_matrix[k][neighbour_index] = cost

    def create_cost_matrix(self):
        """"Create a cost matrix for linear_sum_assignment()."""
        cost_matrix = self.initial_cost_matrix()
        self.reduce_feasible(cost_matrix)
        return cost_matrix

    def to_commands(self):
        """Translate the assignments of ships to commands."""
        commands = []
        if self.allow_dropoff_collisions():
            self.resolve_dropoff_collisions(commands)
        cost_matrix = self.create_cost_matrix()
        row_ind, col_ind = linear_sum_assignment(cost_matrix)
        for k, i in zip(row_ind, col_ind):
            assignment = self.assignments[k]
            target = index_to_cell(i)
            commands.append(assignment.to_command(target))
        return commands

    def near_dropoff(self, ship):
        """Return True if the ship can reach a dropoff/shipyard this turn."""
        ship_index = cell_to_index(game_map[ship])
        shipyard_index = cell_to_index(game_map[me.shipyard])
        return ship_index in neighbours(shipyard_index)

    def resolve_dropoff_collisions(self, commands):
        """Handle endgame collisions at dropoff/shipyard."""
        remaining_assignments = []
        shipyard_cell = game_map[me.shipyard]
        for assignment in self.assignments:
            if self.near_dropoff(assignment.ship):
                commands.append(assignment.to_command(shipyard_cell))
            else:
                remaining_assignments.append(assignment)
        self.assignments = remaining_assignments

    def allow_dropoff_collisions(self):
        """Return True if we allow endgame dropoff collisions at a shipyard."""
        turns_left = constants.MAX_TURNS - game.turn_number
        ships_left = len(me.get_ships())
        return turns_left <= math.ceil(ships_left / 4.0)
