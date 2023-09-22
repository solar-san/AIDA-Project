import itertools

values = {(1, 1): 26, (2, 1): 22, (3, 1): 23, (4, 1): 24, (5, 1): 25, (6, 1): 28, (7, 1): 139, (8, 1): 20, (9, 1): 20, (10, 1): 139,
          (1, 2): 16, (2, 2): 12, (3, 2): 13, (4, 2): 14, (5, 2): 15, (6, 2): 18, (7, 2): 29, (8, 2): 10, (9, 2): 10, (10, 2): 10,
          (1, 3): 16, (2, 3): 12, (3, 3): 13, (4, 3): 14, (5, 3): 15, (6, 3): 18, (7, 3): 29, (8, 3): 10, (9, 3): 10, (10, 3): 10,
          (1, 4): 16, (2, 4): 12, (3, 4): 13, (4, 4): 14, (5, 4): 15, (6, 4): 18, (7, 4): 29, (8, 4): 10, (9, 4): 10, (10, 4): 10}

def Greedy(legalMoves, table, Standalone, values = values):
    if CheckForScopa(legalMoves, table, Standalone, values):
        return CheckForScopa(legalMoves, table, Standalone, values)
    else:
        return BestMove(BasicPlay(legalMoves, table)[0], BasicPlay(legalMoves, table)[1], legalMoves, Standalone, values)


def CheckForScopa(legalMoves, table, Standalone, values): # check if it's possible to do a scopa
    best_broom = None
    max_value = float('-inf')
    brooms = []
    for card in legalMoves:
        if card[0] == sum(rank_table[0] for rank_table in table):
            brooms.append(card)
        else:
            pass  
    if len(brooms) == 0:
        return False
    else:
        for broom in brooms:
            if broom in values:
                value = values[broom]
                if value > max_value:
                    max_value = value
                    best_broom = broom
                    
        if Standalone:
            return best_broom
        else:
            return {
                best_broom: table
            }


def BasicPlay(legalMoves, table):
    list_table = [rank[0] for rank in table]
    possible_picks = {}
    possible_plays = []
    # no_plays = [] Non è usato altrove
    for card in legalMoves:
        if card[0] in list_table:
            possible_plays.append(card)
            for pick in table:
                if pick[0] == card[0]:
                    possible_picks[card] = pick
                    break
        else:
            possible_plays.append(card)
            subsets = []
            for r in range(2, len(list_table) + 1):
                for subset in itertools.combinations(list_table, r):
                    if sum(subset) == card[0]:
                        possible_plays.append(card)
                        subsets.append(subset)
                        sums = []
                        for value_sum in subsets:
                            sub = []
                            for single_card in value_sum:
                                for pick in table:
                                    if single_card == pick[0]:
                                        single_card = pick
                                        sub.append(single_card)
                            sums.append(sub)
                        possible_picks[card] = sums
                    else:
                        possible_plays.append(card)
    
    possible_plays = list(set(possible_plays))
    return possible_picks, possible_plays


def BestMove(possible_picks, possible_plays, legalMoves, Standalone, values = values):
    
    new_p2 = {}
    risultato = []
    punteggi_di_ciascuna_value = []

    # nel prossimo ciclo if vedo se possible_picks è vuota: se non lo è allora vedo fra tutte le possibili tuple qual è 
    # quella che mi permette di ottenere più punti e creo un nuovo dizionario p2 in cui mi salvo solo (abbinata a ciascuna key) 
    # la combinazione che mi permette di fare più punti come value.
    if len(possible_picks) != 0:
        key_list = list(possible_picks.keys())
        val_list = list(possible_picks.values())
        
        for i in range(len(possible_picks)):
            key = (key_list[i])
            val = (val_list[i])

            
            if isinstance(val,tuple):
                new_p2[key] = val

            else:
                #[[(3, 1), (5, 3)], [(1, 1), (3, 1), (4, 1)]]
                values_of_each_el = []
                for el in val:
                    #[(3, 1), (5, 3)]
                    somma = 0
                    for tup in el:
                        #(3, 1)
                        somma = somma + values[tup]
                    #somma rappresenta tutti i punti presi prendendo quel set di carte
                    values_of_each_el.append(somma) #values_of_each_el in questo caso contiene [38, 73]
                massimo = max(values_of_each_el) #massimo è 73
                punteggi_di_ciascuna_value.append(massimo)
                index = values_of_each_el.index(massimo)
                new_p2[key] = val[index]
        
        key_list = list(new_p2.keys())
        val_list = list(new_p2.values())
        punteggi = []

        #qui calcolo per ogni carta quanti punti prende
        for i in range(len(possible_picks)):
            key = (key_list[i])
            val = (val_list[i])
        
            punti_della_key = int(values[key])
            somma = 0
            if isinstance(val,tuple):
                punti_della_value = values[val]
            else:
                for el in val:
                    somma = somma + values[el]
                punti_della_value = somma
        
        
            punti_presi = punti_della_key + punti_della_value
            #mi salvo i punti presi
            punteggi.append(punti_presi)
        #calcolo il max
        massimo = max(punteggi)
        index = punteggi.index(massimo)
        #creo l'output
        risultato = (key_list[index])

                
    
    else:
        #se possible_plays non è vuota, giochiamo la carta migliore in possible_plays 
        #altrimenti guardiamo fra tutte le carte in mano e scegliamo la migliore
        if len(possible_plays) != 0:
            #scrivi
            min_score = float('inf')
            for choice in possible_plays:
                value = values[choice]  # Otteniamo il valore corrispondente alla tupla
                if value < min_score:  # Se il valore è minore del valore massimo attuale
                    min_score = value  # Aggiorniamo il valore massimo
                    risultato = choice  # Aggiorniamo la tupla massima

            
        else:
            min_score = float('inf')
            for choice in legalMoves:
                value = values[choice]  # Otteniamo il valore corrispondente alla tupla
                if value < min_score:  # Se il valore è minore del valore massimo attuale
                    min_score = value  # Aggiorniamo il valore massimo
                    risultato = choice  # Aggiorniamo la tupla massima
    
    if len(possible_picks) != 0:
        cards_to_be_taken = new_p2[risultato]
    else:
        cards_to_be_taken = []

    if Standalone:
        return(risultato)
    else:
        return {
            risultato: cards_to_be_taken
        }


#############################################################

### ESEMPI0 1 ###

a = [
    (1, 2),
    (7, 1),
    (8, 2)
]
b = [
    # (1, 1), 
    # (3, 1), 
    # (4, 1), 
    # (6, 1),
    # (5, 3)
]
c = []

# values = {(1, 1): 26, (2, 1): 22, (3, 1): 23, (4, 1): 24, (5, 1): 25, (6, 1): 28, (7, 1): 139, (8, 1): 20, (9, 1): 20, (10, 1): 139,
#           (1, 2): 16, (2, 2): 12, (3, 2): 13, (4, 2): 14, (5, 2): 15, (6, 2): 18, (7, 2): 29, (8, 2): 10, (9, 2): 10, (10, 2): 10,
#           (1, 3): 16, (2, 3): 12, (3, 3): 13, (4, 3): 14, (5, 3): 15, (6, 3): 18, (7, 3): 29, (8, 3): 10, (9, 3): 10, (10, 3): 10,
#           (1, 4): 16, (2, 4): 12, (3, 4): 13, (4, 4): 14, (5, 4): 15, (6, 4): 18, (7, 4): 29, (8, 4): 10, (9, 4): 10, (10, 4): 10}

# # AvoidScopa(a,b,c)
# print(Greedy(a, b, Standalone=False, values = values))


#############################################################