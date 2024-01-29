import copy
import itertools
import typing
import random

import Greedy_MOD
import Intermediate

from Greedy_MOD import values

from pandas import NA
from pandas._libs.missing import NAType


## Helper Functions and Variables

def print_attributes(obj):
    '''
    Traverses all attributes of an object and prints their name and its corresponding value.
    '''
    for attr in vars(obj):
        print(attr, getattr(obj, attr))
   
        
## Interfaces

class IGameState(object):
    '''
    The GameState wholly defines the game at a given moment.

    Moreover, passes informations from the current game state to the following one.
    '''

    def __init__(self) -> None:
        pass

    def __hash__(self) -> int:
        '''
        GameStates also play the role of nodes in the tree building. Nodes should be hashable.
        '''
        return 19

    def GetAvailableMoves(
        self
    ):
        raise NotImplementedError()

    def ApplyMove(
        self
    ):
        raise NotImplementedError()

    def IsTerminal(
        self
    ):
        '''
        Check if a terminal node is reached (10 turns have passed and this is the last turn).
        '''
        raise NotImplementedError()

    def GetScores(
        self
    ):
        raise NotImplementedError()

    def LastPlayer(
        self
    ):
        '''
        This methods know the last player to move.
        '''
        raise NotImplementedError()

    def CloneState(
        self
    ):
        '''
        This method clones the current IGameState.
        '''
        raise NotImplementedError()

class IGameMove(object):
    '''
    This interface class represents a MOVE in the game.

    It should contain the definition of legal moves
    and routines to evaluate them.

    It should be able to be passed as an argument to the IGameState and update its general state.

    It should be the output of the ITreeNode object that performs a tree search among the possible moves and chooses the optimal one.
    '''

    def __init__(self) -> None:
        pass
    
    def GetMoves(self) -> None:
        '''Simulate another player's strategy and returns a move.'''
        raise NotImplementedError()

    def EvalMoves(
        self
    ):
        '''Checks if two moves are equal.'''
        raise NotImplementedError()
    

## `Card`
    
class Card(object):
    """
    This object represent a card, which is defined by:
    
    - Rank: the number corresponding to the card.
    - Suit (Seme): the suit to which it belongs.
    """

    def __init__(
        self,
        Rank: int = NA,
        Suit: int = NA
        ) -> None:
        """
        To instantiate a Card object, a Rank and Suit have to be specified.
        It is possible to instantiate an "empty" card, in which both Rank and Suits NA.

        Args:
            Rank (int, optional): Defaults to NA.
            Suit (int, optional): Defaults to NA.
        """
        self.Rank = Rank
        self.Suit = Suit

    def __str__(self) -> str:
        """
        This method allows to obtain a custom representation of a Card object when passed as an argument to print.
        """
        Suits = {
            1: "Ori",
            2: "Coppe",
            3: "Spade",
            4: "Bastoni"
        }
        return f"{self.Rank} of {Suits[self.Suit]}, valued {self.Value()} rewards."

    def __repr__(self) -> str:
        """
        This method is used to obtain a compact representation of a Card object.
        """
        return f"Card: ({self.Rank}, {self.Suit})"

    def __hash__(self) -> int:
        """
        Card objects need to be hashable.
        """
        return 666

    def __iter__(self) -> list:
        """
        Card objects are iterable, only once, returning theirself.
        """
        self.n = 0
        return self

    def __next__(self) -> None:
        """
        Card objects are iterable, only once, returning theirself.
        """
        if self.n < 1:
            self.n += 1
            return self
        else:
            raise StopIteration

    def __len__(self) -> int:
        """
        Card objects have length 1.
        """
        return 1

    def Rank(self) -> int:
        return self.Rank

    def Suit(self) -> int:
        return self.Suit

    def Value(self) -> int:
        """
        This method is used to store and retrieve the reward associated with a Card.
        """
        values = {(1, 1): 26, (2, 1): 22, (3, 1): 23, (4, 1): 24, (5, 1): 25, (6, 1): 28, (7, 1): 139, (8, 1): 20, (9, 1): 20, (10, 1): 139,
          (1, 2): 16, (2, 2): 12, (3, 2): 13, (4, 2): 14, (5, 2): 15, (6, 2): 18, (7, 2): 29, (8, 2): 10, (9, 2): 10, (10, 2): 10,
          (1, 3): 16, (2, 3): 12, (3, 3): 13, (4, 3): 14, (5, 3): 15, (6, 3): 18, (7, 3): 29, (8, 3): 10, (9, 3): 10, (10, 3): 10,
          (1, 4): 16, (2, 4): 12, (3, 4): 13, (4, 4): 14, (5, 4): 15, (6, 4): 18, (7, 4): 29, (8, 4): 10, (9, 4): 10, (10, 4): 10}
        return values[self.Rank, self.Suit]

    def __add__(self, other) -> int:
        if isinstance(other, Card):
            return self.Rank + other.Rank
        raise TypeError(
            (f"unsupported operand type(s) for +: "
             f"{type(self)} and {type(other)}"))

    def __radd__(self, other) -> int:
        if other == 0:
            return self
        return self.__add__(other)

    def __mul__(self, other) -> int:
        if isinstance(other, Card):
            return self.Value() + other.Value()
        raise TypeError(
            (f"unsupported operand type(s) for *: "
             f"{type(self)} and {type(other)}"))

    def __eq__(self, other) -> bool:
        if isinstance(self, Card) and isinstance(other, Card):
            if self.Rank == other.Rank and self.Suit == other.Suit:
                return True
            else:
                return False
        elif isinstance(self, tuple) and isinstance(other, Card):
            rank, suit = other.Rank, other.Suit
            if self[0] == rank and self[1] == suit:
                return True
            else:
                return False
        elif isinstance(self, Card) and isinstance(other, tuple):
            rank, suit = self.Rank, self.Suit
            if other[0] == rank and other[1] == suit:
                return True
            else:
                return False

def convert_to_card(
    card: tuple
) -> Card:
    """
    This routine convert tuple object into Card object.
    If the object is already a Card, it returns its argument unmodified.

    Args:
        card (tuple): a tuple describing a card, (rank, suit).

    Returns:
        Card: a Card describing a card.
    """

    if not isinstance(card, Card):

        new_card = Card()
        new_card.Rank, new_card.Suit = card

        return new_card

    elif isinstance(card, Card):
        return card

def convert_to_tuple(
    card: Card
    ) -> tuple:

    temp = card.Rank, card.Suit
    return temp

def sum_combination_ranks(
    CardCombination: list
    ):
    """
    Given a combination of cards, returns the sum of their ranks.
    To be used to compare the Rank of a move (Card from a player's Hand) and the total Rank represented by the combination,
    to understand possible picks and compare.

    Args:
        CardCombination (list): a list of Card objects.

    Returns:
        int: sum of each Card object rank.
    """

    combination_sum = sum(card.Rank for card in CardCombination)

    return combination_sum

def unpack_moves(MovesDict: dict) -> dict:
    """
    This unpack a moves dictionary by yielding a simpler data structure.
    Args:
        MovesDict (dict): a dictionary of moves

            key: card to be played.
            values: card or combination of cards to be taken from the table.

    Yields:
        dict: a sequence of dictionaries each representing a single move.
    """

    for key in MovesDict.keys():
        if len(MovesDict[key]) == 0:
                yield {key: list()}
        else:
            for move in MovesDict[key]:
                if isinstance(move, Card):
                    yield {key: move}

                elif isinstance(move, list):
                    if key.Rank == sum_combination_ranks(move) or len(move) == 0:
                        yield {key: move}
                    
                    
## `ScoponeMove`

class ScoponeMove(IGameMove):
    '''
    This class inherits from IGameMove and, given the rules of Scopone and the definition of the current IGameState,
    either apply a strategy to select which card to play or evaluates whether two cards yield the same points.
    '''

    def __init__(
        self,
        LegalMoves: list = [],
        Table: list = [],
        Deck: list = [],
        values: dict = Greedy_MOD.values,
        ) -> None:
        """
        This section assigns all arguments needed to define the current state of the game.

        Args:
            values (dict, optional): a dictionary that contains the points associated with each card. Defaults to Greedy_MOD.values.
            LegalMoves (list, optional): A list of tuples containing the player's hand. Defaults to [].
            Table (list, optional): A list of tuples containing all the cards on the table. Defaults to [].
            Deck (list, optional): A list of tuples containing all the cards on the deck. Defaults to [].
        """

        super().__init__()

        self.Hand = LegalMoves
        self.Table = Table
        self.Deck = Deck
        self.values = values

    def GetMove(
        self,
        Greedy: bool = True,
        Standalone:bool = False
        ) -> tuple:
        """
        This method, given the elements of the game (LegalMoves, Table, Deck), outputs a tuple representing the card chosen by applying the Intermediate or Greedy (default) strategies.

        Args:
            game_mode (bool, optional): Decide whether to use the Greedy strategy or not. Defaults to False.

        Returns:
            tuple: a card, representing the move chosen by the AI.

        Yields:
            Iterator[tuple]: a card, as defined by points and rank.
        """

        if Greedy:
            return Greedy_MOD.Greedy(
                legalMoves = self.Hand,
                table = self.Table,
                Standalone=Standalone,
                values = values
                )

        # else:
        #     return Intermediate.Intermediate(
        #         legalMoves = self.Hand,
        #         table = self.Table,
        #         deck = self.Deck,
        #         standalone=standalone,
        #         values = values
        #         )

    def GetCombinations(
        Table: list
        ) -> dict:
        """
        This method returns all possible combinations of table cards

        Args:
            Table (tuple): a list of tuples representing cards.

        Returns:
            Combinations: a dictionary of summed ranks as keys and combinations of cards as values representing the legal combined picks.
        """

        available_combinations = []

        for L in range(2, len(Table) + 1):
            available_combinations.append(itertools.combinations(map(convert_to_card, Table), L))

        Combinations = {key: list() for key in range(1, 11)}

        for combinations in available_combinations:
            for combination in combinations:
                combination_sum = 0
                combination_cards = []
                for card in combination:
                    combination_sum += card.Rank
                    combination_cards.append(card)
                if combination_sum < 11:
                    Combinations[combination_sum].append(combination_cards)


        return Combinations

    def EvalMoves(
        move1: dict,
        move2: dict
        ) -> tuple:
        """
        This method takes two moves as arguments, in the form:

        move = {card to be played: card or list of cards (combination) to be picked from the table}

        Returns a tuple (bool, dict) with:
            - bool: truth value resulting from the comparison of the total reward corresponding to that move.
            - dict: the best move among the two inputs.

        Args:
            move1 (dict): a dict object representing a move.
            move2 (dict): a dict object representing a move.

        Returns:
            tuple(bool, dict):
            - bool: truth value resulting from the comparison of the total reward corresponding to that move.
            - dict: the best move among the two inputs.
        """

        move1_cards_list = list()
        move1_tot_reward = 0

        for move, combinations in move1.items():
            move1_cards_list.append(convert_to_card(move))
            if isinstance(combinations, list):
                for pick in combinations:
                    move1_cards_list.append(convert_to_card(pick))
            if isinstance(combinations, tuple):
                move1_cards_list.append(convert_to_card(combinations))


        move1_tot_reward = sum(card.Value() for card in move1_cards_list)

        move2_cards_list = list()
        move2_tot_reward = 0

        for move, combinations in move2.items():
            move2_cards_list.append(convert_to_card(move))
            if isinstance(combinations, list):
                for pick in combinations:
                    move2_cards_list.append(convert_to_card(pick))
            if isinstance(combinations, tuple):
                move2_cards_list.append(convert_to_card(combinations))

        move2_tot_reward = sum(card.Value() for card in move2_cards_list)

        if move1_tot_reward > move2_tot_reward:
            BestMove = move1
        elif move1_tot_reward < move2_tot_reward:
            BestMove = move2
        else:
            # If two cards yield the same value, flip a coin to decide which one to play.
            diceroll = random.randint(0, 1000)
            if diceroll < 500:
                BestMove = move1
            else:
                BestMove = move2

        return move1_tot_reward == move2_tot_reward, BestMove


## `ScoponeGameState`
    
class ScoponeGameState(IGameState):
    """
    This object completely defines the current game 'state' situation.

    It contains methods to:

    - get the available moves,
    - apply a move,
    - check if it is a terminal state,
    - get the scores fo the game,
    - know the last player to move,
    - clone the state.
    - compute the rewards.
    - find all the children of the current ScoponeGameState.
    - find a random children of the current ScoponeGameState.
    """
    # def __new__(cls, *args, **kwargs):
    #     print("####### I have created a new ScoponeGameState.")
    #     return super().__new__(cls)

    def __init__(
        self,
        PlayerPosition: int,
        PlayersCards: dict,
        Team: str,
        TeamScores: dict,
        Table: list = [],
        Deck: list = [],
        LastTaker: int = NA,
        ParentMove: dict = NA,
        values: dict = Greedy_MOD.values
        ) -> None:
        """
        This section assigns all arguments needed to define the current state of the game, for all players.

        Args:
            PlayerPosition (int): the position of the current player. Might be a number from 0 to 3, based on the starting turn.
            PlayersCards (dict): a dictionary containing a list of tuples representing each player's hand.
            Team(str): a string representing the current player's team.
            TeamScores (dict): a dictionary representing team A (player 0, 2) and team B (player 1, 3) scores.
            Table (list, optional): a list of tuples containing all the cards on the table. Defaults to [].
            Deck (list, optional): a list of tuples containing all the cards on the deck Defaults to [].
            LastTaker(int, optional): an integer indicator that stores the position of the last player that has picked cards from the table.
            ParentMove(dict, optional): a dictionary representing the MCTS move that originated the current GameState.
            values (dict, optional): points associated to each card. Defaults to Greedy_MOD.values.
        """

        self.PlayerPosition = PlayerPosition
        self.PlayersCards = PlayersCards
        self.Team = Team
        self.Hand = PlayersCards[PlayerPosition]
        self.TeamScores = TeamScores
        self.Reward = self.ComputeRewards()
        self.Table = Table
        self.Deck = Deck
        self.LastTaker = LastTaker
        self.ParentMove = ParentMove
        self.values = values

    def __eq__(self, other) -> bool:
        check = [self.PlayerPosition == other.PlayerPosition,
                self.PlayersCards == other.PlayersCards,
                self.Team == other.Team,
                self.Hand == other.Hand,
                self.TeamScores == other.TeamScores,
                self.Table == other.Table,
                self.Deck == other.Deck,
                self.values == other.values
        ]

        if all(check) == True:
            return True
        else:
            return False

    def __hash__(self) -> int:
        return super().__hash__()

    def __repr__(self) -> str:
        if isinstance(self.ParentMove, Card):
            return f"###\nScoponeGameState:\n###\n>Parent Move: {self.ParentMove}.\n> Current hand: {self.Hand}\n> Current table: {self.Table}\n> Points: {self.TeamScores}\nThe reward for this State is: {self.Reward}.\n###"
        elif isinstance(self.ParentMove, ScoponeGameState):
            state = self.ParentMove
            return f"###\nScoponeGameState:\n###\n>Parent State: {state.ParentMove}.\n> Current hand: {state.Hand}\n> Current table: {state.Table}\n> Points: {state.TeamScores}\nThe reward for this State is: {state.Reward}.\n###"
        else:
            return f"###\nScoponeGameState:\n###\n>Parent Move: {self.ParentMove}.\n> Current hand: {self.Hand}\n> Current table: {self.Table}\n> Points: {self.TeamScores}\nThe reward for this State is: {self.Reward}.\n###"

    def CloneState(self) -> IGameState:
        """
        This method creates a copy of the current game state and all its attributes.

        Returns:
            ScoponeGameState: a deepcopy of the current ScoponeGameState.
        """

        return copy.deepcopy(self)

    def IsTerminal(self) -> bool:
        """
        This is method to check whether the GameState corresponds to the last turn.

        Returns:
            bool: True if it is the last turn, otherwise False.
        """

        if len(self.Hand) == 0:
            return True
        else:
            return False

    def GetScores(self) -> tuple:
        """
        This EVEN BETTER method gets all the available scores to be rewarded to the player at the current game state.
        Given a table and the player's hand, it will return a list of scores, a dictionary of single picks moves, and a dictionary of combinations.

        Returns:
            A TUPLE with:

            Scores: A list of all the scores available for the taking.
            SinglePicks: A dictionary of all the single-pick moves that can be made and the correspondent points.
                - The dictionary key correspond to the rank, while the value is the card.
            TableCombinations: A list of all the combinations of cards that can be taken and their correspondent point.
                - The dictionary key correspond to the sum of the ranks of all the card in the combinations, while the values are the cards in that particular combination.
        """

        SinglePicks = {card.Rank: card for card in map(convert_to_card, self.Table)}

        TableCombinations = ScoponeMove.GetCombinations(self.Table)

        Scores = []

        for card in SinglePicks.values():
            Scores.append(card.Value())

        for combinations_list in TableCombinations.values():
            total_score = 0
            for combination in combinations_list:
                for card in combination:
                    total_score *= card.Value()
                Scores.append(total_score)

        return Scores, SinglePicks, TableCombinations

    def ComputeRewards(self) -> int:
        """
        This method takes the two teams' scores and computes their difference.
        
        Points scored for the player's team are positive integers, while the other's team are negative: this 
        is used to teach the algorithm the correct behaviour in a reinforcement learning setting.

        Returns:
            int: the difference between the player's and the other's teams scores.
        """

        if self.Team == "Hand":
            StateReward = self.TeamScores["Hand"] - self.TeamScores["Deck"]
        elif self.Team == "Deck":
            StateReward = self.TeamScores["Deck"] - self.TeamScores["Hand"]

        return StateReward


    def GetAvailableMoves(self) -> list[dict]:
        """
        This method indicates all the available cards to be played by the current player.

        Moves are represented by the card played to make that move.
        Given a game state, it will return all the available moves, single picks and combinations.

        Returns:
            list: list of CARDS that can be played at that particular turn.

        IMPORTANT: if a card is present more than once, it might pick either a single card or a combination.
        """


        AvailableMoves = {card: card for card in map(convert_to_card, self.Hand)}


        _, SinglePicks, TableCombinations = self.GetScores()


        LegalMoves = {move: list() for move in AvailableMoves.values()}

        for move in AvailableMoves.values():
            for pick in SinglePicks.values():
                if move.Rank == pick.Rank:
                    LegalMoves[move].append(pick)

        for combinations in TableCombinations.values():
            for combination in combinations:
                for move in LegalMoves.keys():
                    if move.Rank == sum_combination_ranks(combination):
                        LegalMoves[move].append(combination)

        return LegalMoves

    def ApplyMove(
            self,
            BestMove: dict
            ):
        """
        Given a move in the following format:

        {card to be played: card or combination of cards to be taken}

        returns a modified GameState object that applies it to the current GameState.
        This implies:

        - Removing the card from the player's hand.
        - Removing the picked card/s from the table.
        - Adding the resulting reward to that team score.

        Args:
            Move (dict): a dictionary in the form {card to be played: card or combination of cards to be taken}.
            The combination of cards is a list of tuples/Cards objects.

            - Move key = card in your hand to be played. Also called move.
            - Move value = card/combinations of cards to be taken from the table. Also called pick.
                           A pick can either be a combination or a single card. Single cards are iterable once.

        Returns:
            IGameState: a copy of the starting GameState modified by the effects of the BestMove.
        """

        # Reminder:
        #
        # BestMove key = card in your hand to be played.
        # BestMove value = card/combinations of cards to be taken from the table.

        new_game_state = self.CloneState()
        new_table = list(map(convert_to_card, new_game_state.Table))
        new_hand = list(map(convert_to_card, new_game_state.Hand))
        new_score = 0
        updated_scores = new_game_state.TeamScores

        picks_check = len(list(BestMove.values())[0])

        if picks_check == 0 or len(new_game_state.Table) == 0:
            card_to_be_played = [card for card in map(convert_to_card, BestMove.keys())][0]

            new_table.append(card_to_be_played)
            new_hand.remove(card_to_be_played)

            new_game_state.Hand = list(map(convert_to_tuple, new_hand))
            new_game_state.PlayersCards[new_game_state.PlayerPosition] = new_game_state.Hand
            new_game_state.Table = list(map(convert_to_tuple, new_table))

            return new_game_state

        else:
            self.LastTaker = new_game_state.PlayerPosition
            for card_to_be_taken in BestMove.values():
                card_to_be_played = list(map(convert_to_card, [BestMove.keys()][0]))


                for card in new_hand:
                    # scorre tutte le carte in mano e toglie dalla lista la carta che vuole giocare
                    for move in card_to_be_played:
                        if move == card:
                            new_hand.remove(card)
                            new_score += card.Value()



                    for card in card_to_be_taken:
                        #scorre tutte le carte in tavola e toglie dalla lista tavolo la carta/combinazione di carte
                        if isinstance(card_to_be_taken, tuple):
                            card_to_be_taken = convert_to_card(card_to_be_taken)
                        if isinstance(card, int):
                            card = card_to_be_taken
                        for pick in new_table:
                            if isinstance(pick, list):
                                for card_to_remove in pick:
                                    if card_to_remove == card:
                                        new_table.remove(pick)
                                        new_score += pick.Value()
                            elif isinstance(pick, Card) and pick == card:
                                new_table.remove(pick)
                                new_score += pick.Value()
                            elif isinstance(pick, tuple) and pick == card:
                                pick = convert_to_card(pick)
                                new_table.remove(pick)
                                new_score += pick.Value()

            if len(new_table) == 0 and not self.IsTerminal():
                #aggiungi un punto perché hai fatto scopa
                new_score += 1000

            new_players_cards = new_game_state.PlayersCards
            new_players_cards[new_game_state.PlayerPosition] = list(map(convert_to_tuple, new_hand))

            updated_scores[new_game_state.Team] += new_score

            new_game_state.PlayersCards = new_players_cards
            new_game_state.Hand = new_hand
            new_game_state.TeamScores = updated_scores
            new_game_state.Reward = new_game_state.ComputeRewards()
            new_game_state.Table = list(map(convert_to_tuple, new_table))
            
            return new_game_state

    def FindChildren(self) -> list:
        """
        This methods applies all available moves and returns a list containing
        each of the corresponding modified GameStates.

        IMPORTANT: this method is invoked to start a tree search as it considers all the possible
        moves.

        Returns:
            list: a list of modified GameStates.
        """

        AvailableMoves = list(unpack_moves(self.GetAvailableMoves()))

        Childrens = list()

        for move in AvailableMoves:
            new_child = self.ApplyMove(move)
            new_child.ParentMove = move
            Childrens.append(new_child)

        return Childrens

    def FindRandomChildren(self) -> IGameState:
        """
        To efficiently simulate a game, this method returns a random ScoponeGameState
        chosen from the available moves.

        Returns:
            IGameState: a ScoponeGameState.
        """

        AllChildren = self.FindChildren()

        RandomChild = AllChildren[random.randint(0, len(AllChildren) -1)]

        return RandomChild


## `MCTS`

class AgentCarletto(object):
    """
    This class represents a MonteCarlo Agent, which simulates a game-tree starting from
    a given ScoponeGameState.
    
    It contains methods to:
    
    - check whether the attributes have been correctly stored.
    - simulate a whole turn with all the other players' move.
    - expand a node by considering all the possible moves and the other players' reactions.
    - perform a complete rollout and backpropagate the corresponding parent move and its reward in the final
    state of the game.
    """

    def __init__(
        self,
        CurrentGameState: ScoponeGameState,
        ComputationalBudget: int = 500
        ) -> None:
        """

        Args:
            CurrentGameState (ScoponeGameState): a ScoponeGameState representing the current game in all its aspects, because
                AgentCarletto needs to know what is doing.
            ComputationalBudget (int, optional): the MCTS algorithm is simulation based; it will explore single branches until a computational budget is exausted.
                Defaults to 100. Higher budgets might lead to a significant slowdown.
        """
        
        self.CurrentGameState = CurrentGameState
        self.ComputationalBudget = ComputationalBudget

    # def __new__(
    #     cls, *args, **kwargs
    # ):
    #     newagent = "It's A Me, Carletto!"
    #     print(newagent)
    #     return super().__new__(cls)

    def __repr__(self) -> str:
        BadAssIntro = "Hi, my name is Carletto." + " I'm here to kick your ass at Scopone and chew bubble gum." + " And I'm all outta bubble gum."
        return BadAssIntro

    def TurnChecker(
        self,
        CurrentGameState: ScoponeGameState
    ) -> None:
        """
        This function checks that the player starting at a given turn is assigned to the correct team;
        if not, it corrects the assignment.

        Args:
            CurrentGameState (ScoponeGameState): a ScoponeGameState to be checked.
        """
        turn = CurrentGameState.PlayerPosition

        if turn == 0 or turn == 2:
            CurrentGameState.Team = "Hand"
        elif turn == 1 or turn == 3:
            CurrentGameState.Team = "Deck"

    def SimulateTurn(self) -> ScoponeGameState:
        """
        This function simulates all the player's turns. It takes as an input a ScoponeGameState,
        in which the MCTS agent has already made a move.

        Returns:
            ScoponeGameState: a ScoponeGameState resulting from all the players'moves.
        """

        ClonedCurrentGameState = self.CurrentGameState.CloneState()
        
        if ClonedCurrentGameState.PlayerPosition == 0:
            turns = range(ClonedCurrentGameState.PlayerPosition + 1, ClonedCurrentGameState.PlayerPosition + 4)
        else:
            turns = range(ClonedCurrentGameState.PlayerPosition % 1, ClonedCurrentGameState.PlayerPosition % 4)

        for turn in turns:
            ClonedCurrentGameState.PlayerPosition = turn
            if turn == 0 or turn == 2:
                ClonedCurrentGameState.Team = "Hand"
            elif turn == 1 or turn == 3:
                ClonedCurrentGameState.Team = "Deck"

            ClonedCurrentGameState.Hand = ClonedCurrentGameState.PlayersCards[turn]
            
            try:
                ClonedCurrentGameState = ClonedCurrentGameState.ApplyMove(
                    ScoponeMove(
                        LegalMoves=ClonedCurrentGameState.Hand,
                        Table=ClonedCurrentGameState.Table,
                    ).GetMove(
                        Greedy=True,
                        Standalone=False
                    )
                )
            except:
                pass

        ClonedCurrentGameState.PlayerPosition = self.CurrentGameState.PlayerPosition
        ClonedCurrentGameState.Team = self.CurrentGameState.Team
        ClonedCurrentGameState.Hand = ClonedCurrentGameState.PlayersCards[ClonedCurrentGameState.PlayerPosition]
        ClonedCurrentGameState.Reward = ClonedCurrentGameState.ComputeRewards()


        return ClonedCurrentGameState

    def Expand(self):
        """
        Expand your CarlettoAgent consciousness and search the Tree.
        
        This method takes all the possible moves and simulate the consequence of playing them,
        updating the GameState and moving the tree one step further down a given branch.
        It is used as a starter, to evaluate all the possible strategies when the Agent needs to play.
        """

        ClonedCurrentGameState = self.CurrentGameState.CloneState()
        self.TurnChecker(ClonedCurrentGameState)

        #@@@@@@@@@ GENERATING NEW CHILDREN @@@@@@@@@@#

        possible_moves_list = ClonedCurrentGameState.FindChildren()

        resulting_game_states = list()

        for move in possible_moves_list:

            ############ SELECTING NEW CHILDREN ############

            try:
                updated_game_state = AgentCarletto(move).SimulateTurn()
                updated_game_state.ParentMove = move
                resulting_game_states.append(updated_game_state)
            except TypeError:
                EndGame = "We're in the EndGame now.."
                print(EndGame)
                break

        return resulting_game_states

    def Simulate(self) -> tuple:
        """
        This methods performs the rollout (simulate a game until the end) 
        and backpropagation (computes the final scores, their rewards and maps them to the origin of the branch, 
        and the path).
        
        Returns:
            tuple: 
                - a dict with the simulated game state that started the branch and the reward of the finished game.
                - a list with all the nodes in the sequence, representing the complete branch.
        """
        
        Simulation = dict()
        TotalReward = 0
        Path = list()
        TablePoints = 0
        
        ExpandedGameState = self.CurrentGameState.CloneState()
        counter = 0
        
        while not ExpandedGameState.IsTerminal():
            ExpandedGameState = ExpandedGameState.FindRandomChildren()
            ExpandedGameState = AgentCarletto(ExpandedGameState).SimulateTurn()
            if counter == 0:
                Simulation = ExpandedGameState
                Path.append(ExpandedGameState)
            else:
                TotalReward = ExpandedGameState.Reward
                Path.append(ExpandedGameState)
            counter += 1
        
        ### This code block is used to compute the reward in the last turn.
        
        if ExpandedGameState.IsTerminal():
            if isinstance(ExpandedGameState.LastTaker, NAType):
                TakeAllTeam = "Deck"
            elif ExpandedGameState.LastTaker == 0 or ExpandedGameState.LastTaker == 2:
                TakeAllTeam = "Hand"
            elif ExpandedGameState.LastTaker == 1 or ExpandedGameState.LastTaker == 3:
                TakeAllTeam = "Deck"
            
            for leftover in ExpandedGameState.Table:
                TablePoints += convert_to_card(leftover).Value()
            
            ExpandedGameState.TeamScores[TakeAllTeam] += TablePoints
            ExpandedGameState.Reward = ExpandedGameState.ComputeRewards()
                
            
        return {Simulation:TotalReward}, Path
    
    def TreeSearch(self) -> dict:
        """
        This method performs the Monte Carlo Tree Search for our Agent and outputs the 
        resulting best move.
        
        Returns:
            dict: a game move {card to be played: card/s to be taken}.
        """
        
        maxBudget = self.ComputationalBudget
        
        Parents = self.Expand()
        BestMove = {key: 0 for key in Parents}
        
        Simulation, Path = self.Simulate()
        
        while maxBudget > 0:
            NeoSimulation, NeoPath = self.Simulate()
            for State in Simulation.keys():
                for NeoState in NeoSimulation.keys():
                    # No need to explore already seen branches.
                    if Path != NeoPath:
                        if State == NeoState:
                            BestMove[State] = max(Simulation[State], NeoSimulation[NeoState])
                        elif State != NeoState:
                            if Simulation[State] < NeoSimulation[NeoState]:
                                BestMove[NeoState] = NeoSimulation[NeoState]
                        
            maxBudget -= 1
        
        # points = BestMove[max(BestMove, key=BestMove.get)]
        BestMove = max(BestMove, key=BestMove.get)
        BestMove = BestMove.ParentMove
            
            
        return BestMove.ParentMove      