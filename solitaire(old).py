from random import shuffle
from time import sleep

class Card:
    def __init__(self, rank, suit):
        
        self.rank = rank
        self.suit = suit
        self.isDiscovered = False

    def discoverCard(self):
        self.isDiscovered = True

    def undiscoverCard(self):
        self.isDiscovered = False

    def __str__(self):
        return self.rank + self.suit

    def __eq__(self, other):
        return (self.rank + self.suit) == other



class Deck:
    heart = "♥"  # alt+3
    diamond = "♦"  # alt+4
    club = "♣"  # alt+5
    spade = "♠"  # alt+6

    listOfSuits = [heart, diamond, club, spade]
    redSuits = [heart, diamond]
    blackSuits = [club, spade]
    
    rankOfCards = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]  # Low to High

    def __init__(self):
        self.allCards = []

        self.populateAllCards()
        self.shuffleAllCards()


    def populateAllCards(self):
        for rank in self.rankOfCards:
            for suit in self.listOfSuits:
                self.allCards.append(
                    Card(rank, suit)
                )

    def shuffleAllCards(self):
        shuffle(self.allCards)



class Solitaire:
    def __init__(self):
        # foundation, tableau, stockpile (in that order)
        self.initialDeck = Deck()
        
        self.allFoundations = []
        self.allTableaus = []
        self.allStockPiles = [[]]  # for now, combined with waste pile. There's only one stockPile.
        self.allPiles = [self.allFoundations, self.allStockPiles, self.allTableaus]
        self.populatePiles()

        while True:
            self.displayBoard()
            self.selectCard()

    
    def displayErrorMessage(self, errorMessage):
        print(errorMessage)
        sleep(1.5)

    def selectCard(self):
        selectedCard = input("\nSelect which card to move.\n")

        for i in range(len(self.allPiles)):
            for j in range(len(self.allPiles[i])):
                for k in range(len(self.allPiles[i][j])):

                    if self.allPiles[i][j][k] == selectedCard:
                        chosenCard = self.allPiles[i][j][k]
                        ## print("Card is at {}-{}-{}".format(i, j, k))
                        if not chosenCard.isDiscovered:
                            self.displayErrorMessage("Invalid card - not discovered.")
                        else:
                            # print("You selected {}{}".format(card.rank, card.suit))
                            self.moveCard(i, j, k, chosenCard)
                        return

    def moveCard(self, i, j, k, selectedCard):
        # f, t
        desPileType, desRowNumber = input("\nCard designation? Give pile type followed by row number.\n").split()
        desRowNumber = int(desRowNumber)

        if i == 0:
            originalPileType = "f"
        elif i == 1:
            originalPileType = "s"
        elif i == 2:
            originalPileType = "t"
        
        
        if desPileType == "f":
            desPileType = 0
            designationRow = self.allPiles[desPileType][desRowNumber]

            # # if row is not empty
            # if designationRow:
            #     designationCard = designationRow[-1]

            #     # TODO: if designationCard is same suit and one rank below. Perhaps for next sprint.

            
            # if designation is empty and selectedCard is an Ace
            if not designationRow and selectedCard.rank == "A":
                designationRow.append(
                    self.allPiles[i][j].pop(k)
                    )
                
                # if original row was a tableau and is not empty after having just moved a card
                if originalPileType == "t" and self.allPiles[i][j]:
                    self.allPiles[i][j][-1].discoverCard()
            else:
                self.displayErrorMessage("Only Aces can be placed in empty foundation slots.")
            

    
        elif desPileType == "t":
            desPileType = 2
            designationRow = self.allPiles[desPileType][desRowNumber]

            # if designation tableau row is not empty
            if designationRow:
                designationCard = designationRow[-1]
            else:
                # since it is indeed empty, only move selectedCard if King rank
                if not designationRow and selectedCard.rank == "K":
                    designationRow.append(
                        self.allPiles[i][j].pop(k)
                    )

                    # if original row was a tableau and is not empty after having just moved a card
                    if originalPileType == "t" and self.allPiles[i][j]:
                        self.allPiles[i][j][-1].discoverCard()

                else:
                    self.displayErrorMessage("Can only move King cards into empty Tableaus.")
                
                return


            # in designationTableau, the last discoveredCard must be one rank higher and a different colored suit than the chosen card
            if designationCard.rank == Deck.rankOfCards[Deck.rankOfCards.index(selectedCard.rank) + 1] and not (designationCard.suit in Deck.blackSuits and selectedCard.suit in Deck.blackSuits):
                    designationRow.append(
                        self.allPiles[i][j].pop(k)
                        )
                    
                    # if original row was a tableau and is not empty after having just moved a card
                    if originalPileType == "t" and self.allPiles[i][j]:
                        self.allPiles[i][j][-1].discoverCard()
            else:
                self.displayErrorMessage("Invalid play. Chosen card must be alternate color and precisely one rank lower.")


    def populatePiles(self):
        self.populateFoundations()
        self.populateTableaus()
        self.populateStockPile()
        
    def populateFoundations(self):
        for i in range(4):
            self.allFoundations.append([])

    def populateTableaus(self):
        for i in range(7):
            self.allTableaus.append([])

            for j in range(i+1):
                self.allTableaus[i].append(
                    self.initialDeck.allCards.pop()
                )

            self.allTableaus[i][-1].discoverCard()

    def populateStockPile(self):

        for i in range(len(self.initialDeck.allCards)):
            card = self.initialDeck.allCards.pop()
            card.discoverCard()
            self.allStockPiles[0].append(card)


    def displayBoard(self):
        print("\n" * 2)

        # print allFoundations
        for i in range(len(self.allFoundations)):
            print("Foundation{} -> ".format(i), end="")
            if self.allFoundations[i]:  # if list is not empty
                print("({})".format(self.allFoundations[i][-1]))
            else:
                print("()")

        print()

        # print stockPile
        print("Stockpile -> ")
        for card in self.allStockPiles[0]:
            print(card, end="\t")

        print("\n")

        # print allTableaus
        for i in range(len(self.allTableaus)):
            print("Tableau{} -> ".format(i), end="")

            for card in self.allTableaus[i]:
                if card.isDiscovered:
                    print(card, end="")
                else:
                    print("[]", end="")
                    
                print("\t", end="")
            print()

if __name__ == "__main__":
    newGame = Solitaire()