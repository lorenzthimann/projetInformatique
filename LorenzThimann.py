
import curses
from curses import wrapper
#POUR WINDOWS: pip install windows-curses OU python -m pip...
import corpus_texte
import mots_francais

txt = corpus_texte.txt
f = mots_francais.f


def levenshtein_distance(mot1, mot2):
    m = len(mot1)
    n = len(mot2)
    distance = [[0] * (n+1) for _ in range(m+1)]

    for i in range(1, m+1):
        distance[i][0] = i
    for j in range(1, n+1):
        distance[0][j] = j

    for j in range(1, n+1):
        for i in range(1, m+1):
            if mot1[i-1] == mot2[j-1]:
                cout_de_substitution = 0
            else:
                cout_de_substitution = 1
            distance[i][j] = min(distance[i-1][j] + 1, # délétion
                                  distance[i][j-1] + 1, # insertion
                                  distance[i-1][j-1] + cout_de_substitution) # substitution
    return distance[m][n]


def tokenizeur(phrase):
    phrase += ' '
    phrase_token = []
    mot = ''
    for lettre in phrase:
        if lettre == ' ':
            phrase_token.append(mot)
            mot = ''
        else:
            if not lettre.isalpha():
                phrase_token.append(mot)
                phrase_token.append(lettre)
                mot = ''
            else:
                mot += lettre
    if len(phrase_token) > 0 and phrase_token[-1] == '':
        phrase_token = phrase_token[:-1]
    return phrase_token


def prochainsMots1(mot1):
    motsSuivants = {}
    ii = [i for i, x in enumerate(txt) if x == mot1]
    for i in ii[:-1]:
        prochainMot = txt[i+1]
        if prochainMot.isalpha():
            if prochainMot not in motsSuivants.keys():
                motsSuivants[prochainMot] = 1
            else:
                motsSuivants[prochainMot] += 1
    return motsSuivants


def prochainsMots2(s):
    motsSuivants = {}
    mot1 = s[0]
    mot2 = s[1]
    ii = [i for i, x in enumerate(txt) if x == mot1]
    if len(ii) < 90: 
        for mot in f:
            motsSuivants[mot] = 1 # que des poids de 1
        return motsSuivants
    else:
        for i in ii[:-1]:
            prochainMot = txt[i+1]
            apresProchainMot = txt[i+2]
            if prochainMot == mot2 and apresProchainMot.isalpha():
                if apresProchainMot not in motsSuivants.keys():
                    motsSuivants[apresProchainMot] = 1
                else:
                    motsSuivants[apresProchainMot] += 1
        return motsSuivants

def proposeSuite(texteL):
    if len(texteL) > 1:
        suite = prochainsMots2((texteL[-2], texteL[-1]))
        if len(suite) < 10:
            suite = prochainsMots1(texteL[-1])
    else: 
        suite = prochainsMots1(texteL[-1])
    if len(suite) > 0:
        n1 = max(suite, key=suite.get) 
    else:
        n1 = 'une'
    suite[n1] = 0
    if len(suite) > 1:
        n2 = max(suite, key=suite.get) 
        suite[n2] = 0
    else:
        n2 = 'le'
    return n1, n2


def prochainesLettres(mot1, debutMot2):
    motsSuivants = {}
    l = len(debutMot2)
    ii = [i for i, x in enumerate(txt) if x == mot1]
    for i in ii[:-1]:
        prochainMot = txt[i+1]
        if prochainMot[:l] == debutMot2:
            if prochainMot not in motsSuivants.keys():
                motsSuivants[prochainMot] = 1
            else:
                motsSuivants[prochainMot] += 1
    if motsSuivants != {}:
        return max(motsSuivants, key=motsSuivants.get)
    else:
        return ''
    

# PREMIER MOT
def corrige(mot):
    mieux = mot
    if mot in f: 
         pass
    else:
         min_sim = 3
         for i in f:
            sim = levenshtein_distance(i.lower(), mot.lower())
            if sim < min_sim:
                 mieux = i
                 min_sim = sim
    return mieux

# SECOND MOT
def corrigeMot2(mot1, mot2):
    motsSuivants = prochainsMots1(mot1)
    if len(motsSuivants) < 10:
        motsSuivants = {}
        for mot in f:
            motsSuivants[mot] = 1
    max_score = 1/2
    meilleurMot2 = mot2
    for k, v in motsSuivants.items():
        if levenshtein_distance(k.lower(), mot2.lower()) == 0:
            return k
        else:
            score = v/((levenshtein_distance(k.lower(), mot2.lower())) ** 3)
        if score > max_score:
            max_score = score
            meilleurMot2 = k
    return meilleurMot2 


def corrigerBoutDePhrase(mot1, mot2, mot3): 
    apresMot2 = prochainsMots2((mot1, mot2))
    if apresMot2 == {} or max(apresMot2.values()) < 3:
        apresMot2 = prochainsMots1(mot2)
    if apresMot2 == {} or max(apresMot2.values()) < 5:
        apresMot2 = {}
        for i in f:
            apresMot2[i] = 1
    


    max_score = 1/2
    meilleurMot3 = mot3
    for k, v in apresMot2.items():
        if levenshtein_distance(k.lower(), mot3.lower()) == 0:
            return k
        else:
            score = v/((levenshtein_distance(k.lower(), mot3.lower())) ** 3)
        if score >= max_score:
            max_score = score
            meilleurMot3 = k
    return meilleurMot3 


def corrigerPhrase(s):
    meilleurePhrase = ''
    meilleurePhrase_liste = []
    for i in range(len(s)):
        if i == 0:
            meilleurePhrase += (corrige(s[0]) + ' ') 
            meilleurePhrase_liste.append(corrige(s[0]))
        elif i == 1:
            meilleurePhrase += corrigeMot2(s[0], s[1]) + ' '
            meilleurePhrase_liste.append(corrigeMot2(s[0], s[1]))
            
        else:
            meilleurePhrase += corrigerBoutDePhrase(meilleurePhrase_liste[i - 2], meilleurePhrase_liste[i - 1], s[i]) + ' '
            meilleurePhrase_liste.append(corrigerBoutDePhrase(meilleurePhrase_liste[i - 2], meilleurePhrase_liste[i - 1], s[i]))
        
    return meilleurePhrase, meilleurePhrase_liste



def debut(stdscr):
    stdscr.clear()
    stdscr.addstr(0, 40, "Bienvenue sur l'éditeur de texte!")
    stdscr.addstr(2, 33, "Vous pourrez entrer:")
    stdscr.addstr(3, 33, "- deux espaces pour corriger le texte")
    stdscr.addstr(4, 33, '- La flèche droite pour accepter la proposition en gris')
    stdscr.addstr(5, 33, '- "1 " ou "2 " pour accepter les propositions en bleu')
    stdscr.addstr(6, 33, "- La touche ENTER pour fermer la fenètre")
    curses.curs_set(0)
    stdscr.getch()
    stdscr.refresh()


def editeur(stdscr):
    x = 0
    y = 0
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLACK)
    vert = curses.color_pair(1) 
    bleu = curses.color_pair(2) 
    rouge = curses.color_pair(3) 
    blanc = curses.color_pair(4) 
    texte = ''
    texteListe = []
    entree = ''
    suiteMotComplete = '   '
    entreeListe = []
    stdscr.clear()
    stdscr.refresh()
    n1 = '1 '
    n2 = '2 '
    while True:
        entreeListe = tokenizeur(entree)
        texteListe = tokenizeur(texte)
        curses.curs_set(1)
        x = 1
        for i in range(len(texteListe)):
            mot = texteListe[i]
            if len(entreeListe) > i and entreeListe[i] == mot:
                stdscr.addstr(y, x, mot, vert)
            else:
                stdscr.addstr(y, x, mot, rouge)
            x += len(mot)
            if len(texteListe) > i+1 and (texteListe[i+1].isalpha() or texteListe[i+1] == '1' or texteListe[i+1] == '2'):
                x += 1
        if texte != '' and texte[-1] == ' ':
            if x % 90 == 0:
                y += 1
                x = 1
            else:
                x +=1
        
        stdscr.move(y, x)
        char = stdscr.getkey()
        stdscr.clear()
        if char in ('^?', 'KEY_BACKSPACE', '\b', '\x7f') and len(txt) > 0:
            texte = texte[:-1]
            entree = entree[:-1]
        elif char == '\n':
            raise Exception('Au revoir!')
        elif '_' not in char:         
                texte += char
                entree += char
        if texte[-2:] == '2 ':
            texte = texte[:-2] + n2 + ' '
            entree = entree[:-2] + n2 + ' '
            texteListe = tokenizeur(texte)
        elif texte[-2:] == '1 ':
            texte = texte[:-2] + n1 + ' '
            entree = entree[:-2] + n1 + ' '
            texteListe = tokenizeur(texte)
            n1, n2 = proposeSuite(texteListe)
            stdscr.addstr(5, 9, '1: ' + n1, bleu)
            stdscr.addstr(5, 27, '2: ' + n2, bleu)
        if len(texte) > 2 and texte[-2] == " " and texte[-1] == " ":
            
            texte = texte[:-1]
            entree = entree[:-1]
            texteListe = tokenizeur(texte[:-1])
            texteListe = corrigerPhrase(texteListe)[1]
            texte = corrigerPhrase(texteListe)[0]
        
        elif char == 'KEY_RIGHT':
            texte += suiteMotComplete + ' '
            texteListe = tokenizeur(texte)
            entree += suiteMotComplete + ' '
            entreeListe = tokenizeur(entree)
        if len(texte) > 2 and texte[-1] == ' ':
            stdscr.move(1, x+1)
            n1, n2 = proposeSuite(texteListe)
            stdscr.addstr(5, 9, '1: ' + n1, bleu)
            stdscr.addstr(5, 27, '2: ' + n2, bleu)
        elif char == 'KEY_RIGHT':
            texte += suiteMotComplete + ' '
            entree += suiteMotComplete + ' '
        elif len(texteListe) > 1:
            texteListe = tokenizeur(texte)
            motComplete = prochainesLettres(texteListe[-2], texteListe[-1])
            
            if motComplete != '':
                suiteMotComplete = motComplete[len(texteListe[-1]):]
                x = len(texte) + 1
                for i, lettre in enumerate(suiteMotComplete):
                    stdscr.addstr(y, x+i, lettre, blanc)
            if len(char) > 1 and char[:2] == "  ":
                texte += suiteMotComplete
                entree += suiteMotComplete          
        



def main(stdscr):
            debut(stdscr)
            editeur(stdscr)

            stdscr.clear()
            key = stdscr.getkey()
            stdscr.refresh()
            stdscr.getch()

wrapper(main)