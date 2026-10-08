import random 
import os 
import pickle 

def get_word(num):
    words_found=[]
    fin = open("words.txt")
    for line in fin:
        word = line.strip()
        if len(word) == num:
            words_found.append(word)
    fin.close()		
    return words_found

def replace_all(guess, word, letter):
    for pos in range(len(guess)):
        if word[pos] == letter:
            guess = guess[:pos] + letter + guess[pos+1:]
    return guess

# read the high scores from the file into a dictionary
if os.path.exists("hangman_scores_dictionary.txt"):
    fin = open("hangman_scores_dictionary.txt", "rb")
    high_scores = pickle.load(fin)
    fin.close()
else:
    high_scores = {}

number_of_letters = int(input("Enter word length: "))
words = get_word(number_of_letters)
print("There are {} words with {} letters".format(len(words), number_of_letters))

guess_word = words[random.randint(0, len(words) - 1)]

lives = 6 
# initialise the string of letters available
letters_available = "abcdefghijklmnopqrstuvwxyz"
guess_string = "_" * number_of_letters
while lives > 0:
    # show the string of letters available 
    print("Letters available: {}".format(letters_available))
    this_letter = input("Guess a letter: ")
    if this_letter in guess_word:
        guess_string = replace_all(guess_string, guess_word, this_letter)
        if guess_string == guess_word:
            print("You guessed the word!")
            break
    else:
        lives = lives-1
        print("Letter not found - lives remaining: {}".format(lives))
    print(guess_string)
    # replace the guessed letter with _ in the string of letters available
    letters_available = letters_available.replace(this_letter, "_")
print("\nGame over!\n")

if guess_string == guess_word:
    # game is over and word was guessed 
    player = input("Enter player name: ")
    score = lives * number_of_letters

    # check if the player is already in the high scores dictionary
    if player in high_scores:
        # update the player's score
        high_scores[player] += score
    else:
        # add the player to the dictionary with their score
        high_scores[player] = score

    # write the updated high scores back to the file
    fout = open("hangman_scores_dictionary.txt", "wb")
    pickle.dump(high_scores, fout)
    fout.close()

else: 
    print("The word was: {}".format(guess_word))

print("\nHigh Scores:")
for player, score in high_scores.keys():
    print (str(high_scores[player]).rjust(4) + " - " + player)
