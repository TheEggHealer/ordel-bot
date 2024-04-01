from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import time
import random


# Load all words
words = []
special_characters = " !\"#$%&'()*+,-./:;<=>?@[\]^_`{|}~éáíóú"
with open('swe_wordlist', encoding='utf-8') as f:
  for line in f:
    if len(line) == 6 and not any(c in special_characters for c in line):
      words.append(line.strip())


def press_button_by_css(css):
  try:
    button = ff.find_element(By.CSS_SELECTOR, css)
    button.click()
  except Exception as e:
    print(f"Could not find button with css '{css}'")

def send_letter(letter):
  actions = ActionChains(ff)
  actions.send_keys(letter)
  actions.perform()

def send_word(word):
  for letter in word:
    send_letter(letter)
    time.sleep(0.5)
  send_letter(Keys.ENTER)

def clear_input():
  for i in range(5):
    send_letter(Keys.BACKSPACE)

def check_guess(guess_number):
  board = ff.find_element(By.CSS_SELECTOR, ".tiles")
  guessed_tiles = board.find_elements(By.CSS_SELECTOR, "div")[guess_number * 5:guess_number * 5 + 5]
  return [tile.get_attribute("class") for tile in guessed_tiles]

def is_word_possible(word, current_word, included_letters, impossible_letters, previous_guesses):
  for i, letter in enumerate(word):
    if current_word[i] != None and letter != current_word[i]:
      return False
    if letter in impossible_letters:
      return False
    if any(letter == guess[i] and current_word[i] != guess[i] for guess in previous_guesses):
      return False
  
  if any(l not in word for l in included_letters):
    return False
  return True

def rank_words(possible_words, current_word, included_letters, impossible_letters):
  letter_ranking = 'eantrsildomkgväfhupåöbcyjxwzq'
  scores = {}
  for word in possible_words:
    scores[word] = [len(included_letters.intersection(word)), 0]
    scores[word][0] += 5 - len(set(word))

    scores[word][1] = sum(letter_ranking.index(letter) for letter in set(word))
  
  return sorted(possible_words, key=lambda x: (scores[x][0], scores[x][1]), reverse=False)

# Setup selenium
ff = webdriver.Firefox()
ff.get("http://www.ordel.se")
ff.implicitly_wait(5)
press_button_by_css(".fc-cta-consent")
press_button_by_css(".play")

# Algorithm
impossible_letters = set()
included_letters = set()
current_word = [None, None, None, None, None]
previous_guesses = []
possible_words = words.copy()

for i in range(0, 6):
  guess = random.choice(possible_words) if i == 0 else possible_words[0]
  previous_guesses.append(guess)
  send_word(guess)
  time.sleep(5)
  result = check_guess(i)
  for place, ans in enumerate(result):
    if ans == 'correct':
      current_word[place] = guess[place]
      if guess[place] in impossible_letters:
        impossible_letters.remove(guess[place])
      included_letters.add(guess[place])
    elif ans == 'kinda':
      included_letters.add(guess[place])
    else:
      if guess[place] not in current_word and guess[place] not in included_letters:
        impossible_letters.add(guess[place])
  
  if all(letter != None for letter in current_word):
    print('Found the word!', ''.join(current_word))
    break

  possible_words = [word for word in possible_words if is_word_possible(word, current_word, included_letters, impossible_letters, previous_guesses) and word != guess]
  possible_words = rank_words(possible_words, current_word, included_letters, impossible_letters)

  print(len(possible_words), 'possible words left.')
  print(possible_words[:10])

ff.quit()