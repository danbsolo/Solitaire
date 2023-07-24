"""
Solitaire clone.
"""
import arcade
import random
from os import path

# Screen title and size
SCREEN_WIDTH = 1067
SCREEN_HEIGHT = 800
SCREEN_TITLE = "Slithery Solitaire"

# Constants for sizing
CARD_SCALE = 0.6

# How big are the cards?
CARD_WIDTH = 140 * CARD_SCALE
CARD_HEIGHT = 190 * CARD_SCALE

# How big is the mat we'll place the card on?
MAT_PERCENT_OVERSIZE = 1.25
MAT_HEIGHT = int(CARD_HEIGHT * MAT_PERCENT_OVERSIZE)
MAT_WIDTH = int(CARD_WIDTH * MAT_PERCENT_OVERSIZE)

# How much space do we leave as a gap between the mats?
# Done as a percent of the mat size.
VERTICAL_MARGIN_PERCENT = 0.10
HORIZONTAL_MARGIN_PERCENT = 0.10

# The Y of the bottom row (2 piles)
BOTTOM_Y = MAT_HEIGHT / 2 + MAT_HEIGHT * VERTICAL_MARGIN_PERCENT

# The X of where to start putting things on the left side
START_X = MAT_WIDTH / 2 + MAT_WIDTH * HORIZONTAL_MARGIN_PERCENT

# Card constants
CARD_VALUES = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
CLUBS = "Clubs"
HEARTS = "Hearts"
SPADES = "Spades"
DIAMONDS = "Diamonds"
CARD_SUITS = [CLUBS, HEARTS, SPADES, DIAMONDS]
BLACK_SUITS = [CLUBS, SPADES]
RED_SUITS = [HEARTS, DIAMONDS]

"""Constants for card mats -- using calculations instead of hard values so it can scale and be changed easily."""
# The Y of the top row (4 piles)
TOP_Y = SCREEN_HEIGHT - MAT_HEIGHT / 2 - MAT_HEIGHT * VERTICAL_MARGIN_PERCENT

# The Y of the middle row (7 piles)
MIDDLE_Y = TOP_Y - MAT_HEIGHT - MAT_HEIGHT * VERTICAL_MARGIN_PERCENT

# How far apart each pile goes
X_SPACING = MAT_WIDTH + MAT_WIDTH * HORIZONTAL_MARGIN_PERCENT

# where them piles are @
PILE_COUNT = 13
BOTTOM_FACE_DOWN_PILE = 0
BOTTOM_FACE_UP_PILE = 1
PLAY_PILE_1 = 2
PLAY_PILE_2 = 3
PLAY_PILE_3 = 4
PLAY_PILE_4 = 5
PLAY_PILE_5 = 6
PLAY_PILE_6 = 7
PLAY_PILE_7 = 8
TOP_PILE_1 = 9
TOP_PILE_2 = 10
TOP_PILE_3 = 11
TOP_PILE_4 = 12

# fanned card spacing
CARD_VERTICAL_OFFSET = CARD_HEIGHT * CARD_SCALE * 0.3

# back of card sprite
FACE_DOWN_IMAGE = ":resources:images/cards/cardBack_red2.png"


class Card(arcade.Sprite):
    """ Card sprite """

    def __init__(self, suit, value, scale=1):
        """ Card constructor """

        # Attributes for suit and value
        self.suit = suit
        self.value = value

        # Image to use for the sprite when face up
        self.image_file_name = f":resources:images/cards/card{self.suit}{self.value}.png"
        self.is_face_up = False
        super().__init__(FACE_DOWN_IMAGE, scale, hit_box_algorithm="None")

    def face_down(self):
        """ Turn card face-down """
        self.texture = arcade.load_texture(FACE_DOWN_IMAGE)
        self.is_face_up = False

    def face_up(self):
        """ Turn card face-up """
        self.texture = arcade.load_texture(self.image_file_name)
        self.is_face_up = True

    @property
    def is_face_down(self):
        """ Is this card face down? """
        return not self.is_face_up


class SolitaireGame(arcade.Window):
    """ Main application class. """

    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        # Sprite list with all the cards, no matter what pile they are in.
        self.card_list = None

        arcade.set_background_color(arcade.color.AMAZON)

        # List of cards we are dragging with the mouse
        self.held_cards = None

        # Original location of cards we are dragging with the mouse in case
        # they have to go back.
        self.held_cards_original_position = None

        # Sprite list with all the mats the cards lay on.
        self.pile_mat_list = None

        # list of lists for holding piles of cards
        self.piles = None

        # Score tally
        self.score = 0

    def setup(self):
        """ Set up the game here. Call this function to restart the game. """
        # List of cards we are dragging with the mouse
        self.held_cards = []

        # Original location of cards we are dragging with the mouse in case
        # they have to go back.
        self.held_cards_original_position = []

        # ---  Create the mats the cards go on.

        # Sprite list with all the mats tha cards lay on.
        self.pile_mat_list: arcade.SpriteList = arcade.SpriteList()

        # Create the mats for the bottom face down and face up piles
        pile = arcade.SpriteSolidColor(MAT_WIDTH, MAT_HEIGHT, arcade.color.DARK_MOSS_GREEN)
        pile.position = START_X, BOTTOM_Y
        self.pile_mat_list.append(pile)

        pile = arcade.SpriteSolidColor(MAT_WIDTH, MAT_HEIGHT, arcade.color.DARK_MOSS_GREEN)
        pile.position = START_X + X_SPACING, BOTTOM_Y
        self.pile_mat_list.append(pile)

        # Create the seven middle piles
        for i in range(7):
            pile = arcade.SpriteSolidColor(MAT_WIDTH, MAT_HEIGHT, arcade.color.DARK_MOSS_GREEN)
            pile.position = START_X + i * X_SPACING, MIDDLE_Y
            self.pile_mat_list.append(pile)

        # Create the top "play" piles
        for i in range(4):
            pile = arcade.SpriteSolidColor(MAT_WIDTH, MAT_HEIGHT, arcade.color.DARK_MOSS_GREEN)
            pile.position = START_X + i * X_SPACING, TOP_Y
            self.pile_mat_list.append(pile)

        # Sprite list with all the cards, no matter what pile they are in.
        self.card_list = arcade.SpriteList()

        # Create every card
        for card_suit in CARD_SUITS:

            for card_value in CARD_VALUES:
                card = Card(card_suit, card_value, CARD_SCALE)

                card.position = START_X, BOTTOM_Y

                self.card_list.append(card)

        # Shuffle the cards
        for pos1 in range(len(self.card_list)):
            pos2 = random.randrange(len(self.card_list))
            self.card_list.swap(pos1, pos2)

        # Create a list of lists, each holds a pile of cards.
        self.piles = [[] for _ in range(PILE_COUNT)]

        # Put all the cards in the bottom face-down pile
        for card in self.card_list:
            self.piles[BOTTOM_FACE_DOWN_PILE].append(card)

        # - Pull from that pile into the middle piles, all face-down
        # doing a loop for each pile
        for pile_no in range(PLAY_PILE_1, PLAY_PILE_7 + 1):
            # Deal proper number of cards for that pile
            for j in range(pile_no - PLAY_PILE_1 + 1):
                # Pop the card off the deck we are dealing from
                card = self.piles[BOTTOM_FACE_DOWN_PILE].pop()
                # Put in the proper pile
                self.piles[pile_no].append(card)
                # Move card to same position as pile we just put it in
                card.position = self.pile_mat_list[pile_no].position
                # Put on top in draw order
                self.pull_to_top(card)

        # Flip up the top cards
        for i in range(PLAY_PILE_1, PLAY_PILE_7 + 1):
            self.piles[i][-1].face_up()

    def on_draw(self):
        """ Render the screen. """
        # Clear the screen
        self.clear()

        # Draw Scoreboard
        arcade.draw_text('Score: ' + str(self.score), 750, 50,
                         arcade.color.WHITE, 30, 5000, 'left')

        # Draw Mats

        self.pile_mat_list.draw()

        # Draw the cards
        self.card_list.draw()

    def on_mouse_press(self, x, y, button, key_modifiers):
        """ Called when the user presses a mouse button. """

        # If button == 1, then the left-click was clicked. 
        # Any other click (i.e. right-click) should be ignored. Pressing multiple different kinds of clicks can lead to glitches otherwise.
        if button != 1:
            return

        # Better code for running the sound effect. Place this code somewhere else though; it's unnecessary here.
        # flipSound = path.dirname(path.abspath(__file__)) + "/flipSound.mp3"
        # arcade.load_sound(flipSound).play()

        # Get list of cards we've clicked on
        cards = arcade.get_sprites_at_point((x, y), self.card_list)

        # Have we clicked on a card?
        if len(cards) > 0:

            # Might be a stack of cards, get the top one
            primary_card = cards[-1]
            assert isinstance(primary_card, Card)

            # Figure out what pile the card is in

            pile_index = self.get_pile_for_card(primary_card)

            # Are we clicking on the bottom deck, to flip three cards?

            if pile_index == BOTTOM_FACE_DOWN_PILE:

                # Flip three cards
                for i in range(3):

                    # If we ran out of cards, stop
                    if len(self.piles[BOTTOM_FACE_DOWN_PILE]) == 0:
                        break

                    # Get top card
                    card = self.piles[BOTTOM_FACE_DOWN_PILE][-1]

                    # Flip face up
                    card.face_up()

                    # Move card position to bottom-right face up pile
                    card.position = self.pile_mat_list[BOTTOM_FACE_UP_PILE].position

                    # Remove card from face down pile
                    self.piles[BOTTOM_FACE_DOWN_PILE].remove(card)

                    # Move card to face up list
                    self.piles[BOTTOM_FACE_UP_PILE].append(card)

                    # Put on top draw-order wise
                    self.pull_to_top(card)

            elif primary_card.is_face_down:
                # Is the card face down? In one of those middle 7 piles? Then flip up
                primary_card.face_up()
            else:
                # All other cases, grab the face-up card we are clicking on
                self.held_cards = [primary_card]
                # Save the position
                self.held_cards_original_position = [self.held_cards[0].position]
                # Put on top in drawing order
                self.pull_to_top(self.held_cards[0])

                # Is this a stack of cards? If so, grab the other cards too
                card_index = self.piles[pile_index].index(primary_card)
                for i in range(card_index + 1, len(self.piles[pile_index])):
                    card = self.piles[pile_index][i]
                    self.held_cards.append(card)
                    self.held_cards_original_position.append(card.position)
                    self.pull_to_top(card)

        else:
            # Click on a mat instead of a card?
            mats = arcade.get_sprites_at_point((x, y), self.pile_mat_list)

            if len(mats) > 0:
                mat = mats[0]
                mat_index = self.pile_mat_list.index(mat)

                # Is it our turned over flip mat? and no cards on it?
                if mat_index == BOTTOM_FACE_DOWN_PILE and len(self.piles[BOTTOM_FACE_DOWN_PILE]) == 0:

                    # Flip the deck back over so we can restart
                    temp_list = self.piles[BOTTOM_FACE_UP_PILE].copy()

                    for card in reversed(temp_list):
                        card.face_down()
                        self.piles[BOTTOM_FACE_UP_PILE].remove(card)
                        self.piles[BOTTOM_FACE_DOWN_PILE].append(card)
                        card.position = self.pile_mat_list[BOTTOM_FACE_DOWN_PILE].position

    def on_mouse_release(self, x: float, y: float, button: int,
                         modifiers: int):


        # Commenting this out cause why have the sound play on mouse_press AND on mouse_release?
        # arcade.load_sound(r"C:\Users\mattw\Downloads\Deepwoken Talent Card Flip Sound Effect.mp3").play()


        """ Called when the user presses a mouse button. """
        # If we don't have any cards, who cares
        if len(self.held_cards) == 0:
            return

        # find the closest pile incase we are in contact with more than one
        pile, distance = arcade.get_closest_sprite(self.held_cards[0], self.pile_mat_list)
        reset_position = False  # Default was True. Changed it to False.
        
        # Pile we just came from.
        originalPile = self.get_pile_for_card(self.held_cards[0])


        # see if we are actually in contact with the closest pile
        if arcade.check_for_collision(self.held_cards[0], pile):

            # What pile is it?
            pile_index = self.pile_mat_list.index(pile)

            primaryHeldCard = self.held_cards[0]

            # Dropped onto pile we just came from?
            if pile_index == originalPile:
                    reset_position = True

            # Dropping onto a tableau?
            elif PLAY_PILE_1 <= pile_index <= PLAY_PILE_7:
                # Is droppedOntoPile empty and primaryHeldCard not a King?
                if not self.piles[pile_index] and primaryHeldCard.value != "K":
                    reset_position = True

                # Is droppedOntoPile not empty? Then set droppedOntoCard
                elif self.piles[pile_index]:
                    droppedOntoCard = self.piles[pile_index][-1]

                    # Enforce alternating colors
                    if (primaryHeldCard.suit in BLACK_SUITS and droppedOntoCard.suit in BLACK_SUITS) or (
                            primaryHeldCard.suit in RED_SUITS and droppedOntoCard.suit in RED_SUITS):
                        reset_position = True

                    # Enforce proper rank of King
                    # If card is King and pile is a tableau, then it's an error cause the pile isn't empty~
                    elif primaryHeldCard.suit == "K" and PLAY_PILE_1 <= pile_index <= TOP_PILE_4:
                        reset_position = True
                    # Enforce proper rank of cards (except King)
                    elif CARD_VALUES[CARD_VALUES.index(primaryHeldCard.value) + 1] != droppedOntoCard.value:
                        reset_position = True

            # Dropping onto a foundation?
            elif TOP_PILE_1 <= pile_index <= TOP_PILE_4:

                # Is pile empty?
                if not self.piles[pile_index]:
                    # Considering the pile is indeed empty, is primaryHeldCard not an Ace?
                    if primaryHeldCard.value != "A":
                        reset_position = True

                else:
                    droppedOntoCard = self.piles[pile_index][-1]

                    # Considering pile isn't empty, is primaryHeldCard not the same suit as the droppedOntoCard?
                    if droppedOntoCard.suit != primaryHeldCard.suit:
                        reset_position = True

                    # Considering pile isn't empty, is primaryHeldCard an Ace? (Illegal move).
                    elif primaryHeldCard.suit == "A":
                        reset_position = True 

                    # Considering pile isn't empty and isn't an Ace, is primaryHeldCard not one value higher than droppedOntoCard?
                    elif CARD_VALUES[CARD_VALUES.index(primaryHeldCard.value) -1] != droppedOntoCard.value:
                        reset_position = True

                    # Considering pile isn't empty, is length of held cards not just 1 card?
                    elif len(self.held_cards) != 1:
                        reset_position = True

                
            # Not dropping onto a tableau nor a foundation? (So, onto some random spot or other illegal deck). Reset.
            else:
                reset_position = True


            # if none of the flags from earlier set reset_position to True, proceed with attempting to move each card.
            # Note: reset_position can stil be set to True from within this block.
            if not reset_position:
                # Is it on a middle play pile?
                if PLAY_PILE_1 <= pile_index <= PLAY_PILE_7:
                    # Are there already cards there?
                    if len(self.piles[pile_index]) > 0:
                        # Move cards to proper position
                        top_card = self.piles[pile_index][-1]
                        for i, dropped_card in enumerate(self.held_cards):
                            dropped_card.position = top_card.center_x, \
                                top_card.center_y - CARD_VERTICAL_OFFSET * (i + 1)
                    else:
                        # Are there no cards in the middle play pile?
                        for i, dropped_card in enumerate(self.held_cards):
                            # Move cards to proper position
                            dropped_card.position = pile.center_x, \
                                pile.center_y - CARD_VERTICAL_OFFSET * i

                    for card in self.held_cards:
                        # Cards are in the right position, but we need to move them to the right list
                        self.move_card_to_new_pile(card, pile_index)

                # Release on top play pile? And only one card held?
                elif TOP_PILE_1 <= pile_index <= TOP_PILE_4 and len(self.held_cards) == 1:
                    # Move position of card to pile
                    self.held_cards[0].position = pile.position
                    # Move card to card list
                    for card in self.held_cards:
                        self.move_card_to_new_pile(card, pile_index)


        # The resetting of cards to previous valid state
        if reset_position:
            print("RESET THE CARDS")
            # Where-ever we were dropped, it wasn't valid. Reset the each card's position
            # to its original spot.
            for pile_index, card in enumerate(self.held_cards):
                card.position = self.held_cards_original_position[pile_index]

            # We are no longer holding cards
            self.held_cards = []

            # For each held card, move it to the pile we dropped on
            for i, dropped_card in enumerate(self.held_cards):
                # Move cards to proper position
                dropped_card.position = pile.center_x, pile.center_y

        # if we didn't end up resetting, pile we left is a tableau, and pile we left isn't empty, discover the top card of the pile we just left~
        else:
            if (PLAY_PILE_1 <= originalPile <= PLAY_PILE_7) and self.piles[originalPile]:
                self.piles[originalPile][-1].face_up()


        # We are no longer holding cards
        self.held_cards = []

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        """ User moves mouse """

        # move cards while holding down mouse button
        for card in self.held_cards:
            card.center_x += dx
            card.center_y += dy

    def pull_to_top(self, card: arcade.Sprite):
        """ Pull card to top of rendering order (last to render, looks on-top) """

        # Remove, and append to the end
        self.card_list.remove(card)
        self.card_list.append(card)

    def get_pile_for_card(self, card):
        """ What pile is this card in? """
        for index, pile in enumerate(self.piles):
            if card in pile:
                return index

    def remove_card_from_pile(self, card):
        """ Remove card from whatever pile it was in. """
        for pile in self.piles:
            if card in pile:
                pile.remove(card)
                break

    def move_card_to_new_pile(self, card, pile_index):
        """ Move the card to a new pile """
        self.remove_card_from_pile(card)
        self.piles[pile_index].append(card)

    def on_key_press(self, symbol: int, modifiers: int):
        """ User presses key """
        # Pressing R Will reset the game
        if symbol == arcade.key.R:
            # Restart
            self.setup()


def main():
    """ Main function """
    window = SolitaireGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
