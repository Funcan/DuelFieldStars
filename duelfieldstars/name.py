"""Functions for the generation of pseudo-random names."""

from random import choice, randint
import string

VOWELS = ['a','e','i','o','u']
CONSONANTS = ['b','c','d','f','g','h','j','k','l','m','n','p','q','r','s','t','v','w','x','y','z']

GREEK = ["alpha", "beta", "gamma", "delta", "epsilon", "zeta", "eta", "theta", "iota", "kappa", "lambda",
         "mu", "nu", "xi", "omicron", "pi", "rho", "sigma", "tau", "upsilon", "phi", "chi", "psi", "omega"  ]

PHONECIAN = ["aleph", "beth", "gimel", "daleth", "he", "zayin", "heth", "teth", "yodh", "kaph", "lamedh",
             "mem", "nun", "samekh", "ayin", "pe", "resh", "sin", "taw", "waw"]

PHONEME_VOWEL = ['ea', 'i', 'oo', 'ere', 'ay', 'e', 'a', 'or', 'our', 'oy', 'o', 'u', 'ar', 'ear', 'y']
PHONEME_CONSONANT = ['p', 'b', 't', 'd', 'ch', 'dj', 'k', 'g', 'f', 'v', 'th', 's', 'z', 'sh', 'm', 'n',
                      'h', 'l', 'r', 'w', 'j', 'st', 'w', 'ng']

GOVERNMENTS = ['aristocracy', 'kingdom', 'principality', 'oligarchy', 'technocracy',
               'fiefdom', 'democracy', 'republic', 'union', 'theocracy',
               'council', 'regime', 'junta', 'hive', 'colonies', 'federation', 'commonwealth']

ADJECTIVE = ['adorable', 'beautiful', 'clean', 'drab', 'elegant', 'fancy',
            'glamorous', 'handsome', 'long', 'magnificent', 
            'plain', 'quant', 'sparkling', 'ugliest', 'unsightly', 'wide-eyed',
            'red', 'orange', 'yellow', 'green', 'blue', 'purple', 'gray', 'black',
            'white', 'golden', 'azure', 'marine', 'twisted', 'fierce',
            'worried', 'indefatigable', 'dauntless', 'brave', 'fearless',
            'clever', 'calm', 'eager', 'jolly', 'fat', 'sable']
NOUN = ['rose', 'disk', 'lizard', 'rock', 'paper', 'scissors', 'taboo',
        'spear', 'lance', 'ocean', 'void', 'mercury', 'venus', 'mars', 'terra',
        'jupiter', 'saturn', 'neptune', 'pluto']

"""def syllable():
    string = ""
    for i in range (0,random.choice([0,1]) ):
        string += random.choice(CONSONENTS)
    string += random.choice(VOWELS)
    for i in range (0, random.choice([1,2]) ):
        string += random.choice(CONSONENTS)
    return string

def root(syllables):
    string = ""
    for i in range(syllables):
        string += syllable()
    return string"""

def planet_name():
    string_ = choice(PHONECIAN) + choice(PHONECIAN) + " " + choice(GREEK) + " " + str(randint(1,9) )
    string_ = string.capwords(string_)
    return string_

def faction_name():
    string_ = choice(PHONEME_CONSONANT) + choice(PHONEME_VOWEL) + choice(PHONEME_CONSONANT)
    for i in range(randint(0,1) ):
        string_ += choice(PHONEME_VOWEL) + choice(PHONEME_CONSONANT) 
    string_ += ' '+choice(GOVERNMENTS)
    string_ = string.capwords(string_)
    return string_

def noun():
        return choice(PHONEME_CONSONANT) + choice(PHONEME_VOWEL) + choice(PHONEME_CONSONANT)

def name():
    if choice([True,False]):
        string_ = noun()
    else:
        string_ = choice(NOUN)
    return string.capwords(string_)

def ship_name():
    string_ = ""
    for _ in range (randint(0,1) ):
        string_ += choice(ADJECTIVE) + " "
    
    string_ += name()
    
    string_ = string.capwords(string_)
    return string_   
    

if __name__ == '__main__':
    print [planet_name() for i in range (10)]
    print [faction_name() for i in range(10)]
    print [ship_name() for i in range(10) ]