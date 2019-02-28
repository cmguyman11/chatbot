# PA6, CS124, Stanford, Winter 2019
# v.1.0.3
# Original Python code by Ignacio Cases (@cases)
######################################################################
import movielens
import sys
import os
import re
import math
import random

import numpy as np
from nltk.tokenize import word_tokenize
from PorterStemmer import PorterStemmer


class Chatbot:
    """Simple class to implement the chatbot for PA 6."""

    def __init__(self, creative=False):
      # The chatbot's default name is `moviebot`. Give your chatbot a new name.
      self.name = 'Lit!'

      self.creative = creative

      # This matrix has the following shape: num_movies x num_users
      # The values stored in each row i and column j is the rating for
      # movie i by user j
      self.titles, ratings = movielens.ratings()

      self.problems_list = []
      self.problem = 0
      self.confirmation_list = []
      self.suggested = []
      self.currentMovies = []

      #self.extreme_sentiment = movielens.extract_sentiment()

      self.sentiment = {}
      self.porter_stemmer = PorterStemmer()
      sentimentCopy = movielens.sentiment()

      for k, v in sentimentCopy.items():
        key = self.porter_stemmer.stem(k)
        self.sentiment[key] = v


      self.user_ratings = []
      #############################################################################
      # TODO: Binarize the movie ratings matrix.                                  #
      #############################################################################
      ratings = self.binarize(ratings)
      # Binarize the movie ratings before storing the binarized matrix.
      self.ratings = ratings
      #############################################################################
      #                             END OF YOUR CODE                              #
      #############################################################################

    #############################################################################
    # 1. WARM UP REPL                                                           #
    #############################################################################

    def greeting(self):
      """Return a message that the chatbot uses to greet the user."""
      #############################################################################
      # TODO: Write a short greeting message                                      #
      #############################################################################

      greeting_message = "Well hello there! Let's talk about movies! Is there a movie you've enjoyed recently?"

      #############################################################################
      #                             END OF YOUR CODE                              #
      #############################################################################
      return greeting_message

    def goodbye(self):
      """Return a message that the chatbot uses to bid farewell to the user."""
      #############################################################################
      # TODO: Write a short farewell message                                      #
      #############################################################################

      goodbye_message = "Have an awesome day, and I hope you enjoy your film!"

      #############################################################################
      #                             END OF YOUR CODE                              #
      #############################################################################
      return goodbye_message

    ###############################################################################
    # 2. Modules 2 and 3: extraction and transformation                           #
    ###############################################################################

    def process(self, line):
      """Process a line of input from the REPL and generate a response.

      This is the method that is called by the REPL loop directly with user input.

      You should delegate most of the work of processing the user's input to
      the helper functions you write later in this class.

      Takes the input string from the REPL and call delegated functions that
        1) extract the relevant information, and
        2) transform the information into a response to the user.

      Example:
        resp = chatbot.process('I loved "The Notebok" so much!!')
        print(resp) // prints 'So you loved "The Notebook", huh?'

      :param line: a user-supplied line of text
      :returns: a string containing the chatbot's response to the user input
      """
      #############################################################################
      # TODO: Implement the extraction and transformation in this method,         #
      # possibly calling other functions. Although modular code is not graded,    #
      # it is highly recommended.                                                 #
      #############################################################################
      if self.creative:
        #if there's a current problem to be addressed, return the required text and update global vars.
        titles = []
        response = ""
        if self.problem: 
          self.handle_problem(line)
        #if multiple movies in one line, extract sentiment [("the notebook", 1), ("Titanic", -1)]
        else:
          if re.match('.*"([^"]*)"(.*"([^"]*)")+', line):
            titles = self.extract_sentiment_for_movies(line)
            for i in range(len(titles)): titles[i] = ([titles[i][0]], titles[i][1])
          #if not multiple movies, simply update
          else:
            titles = [(self.extract_titles(line), self.extract_sentiment(line))]
          
          if titles == []:return "Let's talk more about movies!"
          id_list = []

          #titles = [(["title_a", "title_b", "title_c"] , 1), (["title"], -1), etc.]
          #title = ([title list], sentiment)
          for title in titles:   
            id_list = []
            #i = string "title_a"
            for i in title[0]:
              #add all possible movies to the list of titles.
              
              id_list = id_list + self.find_movies_by_title(i)
              if id_list == []:
                id_list = id_list + self.find_movies_closest_to_title(i)

              id_list = list(set(id_list))

            if id_list == []: return "I'm sorry, I don't think I quite understood that. Would you tell me about a movie you enjoyed?"
            #if something is ambiguous--either id_list is longer than 1 movie or sentiment is 0, add to problems list
            if len(id_list) > 1 or (title[1] == 0): 
              self.problem += 1
              self.problems_list.append((id_list, title[1]))
            #if not ambigous, add to list of movies to be confirmed.
            elif len(id_list) == 1 and title[1] != 0:
              self.confirmation_list.append((id_list[0], title[1]))      
              self.user_ratings.append((id_list[0], title[1]))
          if id_list == []: return "I'm sorry, I don't think I quite understood that. Would you tell me about a movie you like?"


          # # Creative addition: return a drink and snack suggestion
          # if len(self.user_ratings) >= 5 and len(self.problems_list) == 0:
          #   self.rating_vec = np.zeros(len(self.titles))
          #   for movie in self.user_ratings:
          #     self.rating_vec[movie[0]] = movie[1]
          #   suggestions = self.recommend(self.rating_vec, self.ratings)
          #   response = "Based on your movie recommendation, we'd recommend \"{}\" paired with \"{}\"".format(self.snack_recommendation(self.titles[suggestions[0]][0]), self.drink_recommendation(self.titles[suggestions[0]][0]))
        
          #   ## make this be a complex response
          #   drink = drink_recommendation(suggestions[0][0])
          #   snack = snack_recommendation(suggestions[0][0])
        return self.complex_response()
       
      ##NORMAL MODE!!
      else:
        titles = self.extract_titles(line)
        if len(titles) > 1:
          return "Woah there, let's talk about one movie at a time please!"

        sentiment = self.extract_sentiment(line)

        movies = []
        id_list = []
        # emma
        print("wrong")
        # broken here
        if titles == []:return "I'm sorry, I don't recognize that movie. Can you tell me about a different one?"
        print("no titles")
        if titles == []:return "I'd love to talk about movies!"
        for i in titles:

          id_list = self.find_movies_by_title(i)
          if id_list == []:return "I'm sorry, I don't recognize that movie. Can we talk about a different one?"
            #for simple mode: no disambiguate, just choose first id!
          if len(id_list) > 1:
            return self.ambiguous_entry(id_list)

          movies = (self.find_movies_by_title(i)[0], sentiment)        
          self.user_ratings.append(movies)
            
        
        if len(self.user_ratings) >= 5:
          self.rating_vec = np.zeros(len(self.titles))
          for movie in self.user_ratings:
            self.rating_vec[movie[0]] = movie[1]
          suggestions = self.recommend(self.rating_vec, self.ratings)
          return "I think you would really love watching \"{}\" based on what you've told me!".format(self.titles[suggestions[0]][0])

        if sentiment > 0:
          return "I loved \"{}\" too! What's another movie you've seen?".format(self.titles[id_list[0]][0])
        else:
          return "Okay, so you you don't want to watch another movie like \"{}\". Any other movies you've seen recently?".format(self.titles[id_list[0]][0])

      #############################################################################
      #                             END OF YOUR CODE                              #
      #############################################################################

    
    #handle complex problem responses in creative mode 

    def complex_response(self):
      result = "Let's talk about some movies you've enjoyed!"
      if len(self.user_ratings) >= 5 and len(self.problems_list) == 0:
        self.rating_vec = np.zeros(len(self.titles))
        for movie in self.user_ratings:
          self.rating_vec[movie[0]] = movie[1]
        suggestions = self.recommend(self.rating_vec, self.ratings)
        print(suggestions)
        #print(str(self.titles[suggestions[0]]))
        #drink = self.drink_recommendation(self.titles[suggestions[0]])
        #drink = self.drink_recommendation(self.titles[suggestions[0]])
        #snack = self.snack_recommendation(self.titles[suggestions[0]][0])
        return "I suggest you watch \"{}\" based on your current preferences.".format(self.titles[suggestions[0]][0])
        # return "I suggest you watch \"{}\" based on your current preferences. For a bonus, based on your movie recommendation, we'd recommend you pair your viewing with \"{}\" and \"{}\"".format(self.titles[suggestions[0]][0], snack, drink)

      if len(self.problems_list) > 0:
        if len(self.problems_list[-1][0]) > 1:
          self.problem = 1
          return self.ambiguous_entry(self.problems_list[-1][0])
        elif self.problems_list[-1][1] == 0:
          self.problem = 2
          return "I'm not sure how you felt about \"{}\". Could you tell me a bit more about your feeling?".format(self.titles[self.problems_list[-1][0][0]][0])

      if len(self.confirmation_list) > 0:
        if self.confirmation_list[-1][1] > 0:
          result = "Great, I'm glad to hear you enjoyed \"{}\". What's another movie you've seen recently?".format(self.titles[self.confirmation_list[-1][0]][0])
        else:
          result = "Okay, so you didn't like \"{}\". What's another movie you've seen recently?".format(self.titles[self.confirmation_list[-1][0]][0])
        self.confirmation_list.pop()
      return result
  
    #deal with follow-up conversation in creative mode
    def handle_problem(self, line):
      #get problem list's first id and sentiment
      problem = self.problems_list.pop()
      id_list = problem[0]
      sentiment = problem[1]

      #Fix one problem at a time
      if self.problem == 1:
        id_list = self.disambiguate(line, id_list)
      elif self.problem == 2:
        sentiment = self.extract_sentiment(line)

      if len(id_list) != 1 or sentiment == 0:
        if id_list == []: id_list = problem[0] 
        self.problems_list.append((id_list, sentiment))
      else:
        self.confirmation_list.append((id_list[0], sentiment))      
        self.user_ratings.append((id_list[0], sentiment))

      self.problem = 0
      return 
    
    def extract_titles(self, text):
      """Extract potential movie titles from a line of text.

      Given an input text, this method should return a list of movie titles
      that are potentially in the text.

      - If there are no movie titles in the text, return an empty list.
      - If there is exactly one movie title in the text, return a list
      containing just that one movie title.
      - If there are multiple movie titles in the text, return a list
      of all movie titles you've extracted from the text.

      Example:
        potential_titles = chatbot.extract_titles('I liked "The Notebook" a lot.')
        print(potential_titles) // prints ["The Notebook"]
      
      :param text: a user-supplied line of text that may contain movie titles
      :returns: list of movie titles that are potentially in the text
      """
      titles = []
      if self.creative:
        # strip text of case and punctuation
        text = text.lower()
        text = re.sub(r'[,\'!?:]', '', text)
        alt_title_dict = {}

        movie_list = movielens.titles()
        for i in range(len(movie_list)):
          movie_stripped = ""
          matched = False
          # strip movie of case and year
          original_movie = movie_list[i][0].lower() # make lowercase
          original_movie = self.process_title_reverse(original_movie)

          date = re.findall(' \(\d{4}\)', original_movie)

          # turn Notebook, The into The Notebook
          movie_stripped = self.process_title_reverse(re.sub(' \(\d{4}\)', '', original_movie))

          movie_stripped = re.sub(r'[.,\':]', '', movie_stripped)

          movie_with_date = movie_stripped
          #The Notebook (2007)
          if len(date) > 0:
            movie_with_date = movie_stripped + date[0]

          alt_titles = re.findall(' \(.[^\)\(]*\)', movie_stripped) # find foreign titles in parenthesis
          
          if len(alt_titles) > 0:
            for i in range(len(alt_titles)):
              alt_title = re.sub('[\(\)]', '', alt_titles[i])
              alt_title = self.process_title_reverse(re.sub('aka ', '', alt_title).lstrip())

              if alt_title in text.split():
                titles.append(movie_stripped)
                matched = True
                #Original movies is a list of the official names of all movies theyre currently asking about
                self.currentMovies.append(original_movie)

          movie_with_parens = movie_stripped
          movie_stripped = re.sub(' \(.*\)', '', movie_stripped) # remove any extra parenthesis

          # if they entered it in with the date, we want to return the date
          if movie_with_date in text and not matched:
            titles.append(movie_with_date)
            self.currentMovies.append(original_movie)
            matched = True
          
          movie_with_date_no_parens = re.sub('\(.[^\d{4}]*.\)', '', original_movie)
          if movie_with_date_no_parens in text and not matched:
            titles.append(movie_with_date_no_parens)
            self.currentMovies.append(original_movie)
            matched = True
          
          # # handles case of one movie
          if re.search(r"\b" + re.escape(movie_stripped) + r"\b", text) and not matched:
            titles.append(movie_stripped)
            self.currentMovies.append(original_movie)

      else: # just quotations
      # #pattern regular = '[\"\'].+[\"\']'
        titles = re.findall('"([^"]*)"', text)

      print("titles: " + str(titles))
      return titles


    # Helper function 
    def process_title(self, title):
      title = title.lower()
      word_list = title.split()
      if (word_list[0] in ['and', 'the', 'a', 'an', 'le', 'la']):
        word_list[-1] = word_list[-1] + ','
        word_list.append(word_list[0])
        word_list.pop(0)

      title = " ".join(word_list)
      return title

    # move words in list to start of sentence
    def process_title_reverse(self, title):
      title = title.lower()
      word_list = title.split()
      lastIndex = len(word_list) - 1
      if (word_list[lastIndex] in ['and', 'the', 'a', 'an', 'le', 'la']):
        word_list[lastIndex] = re.sub("," , '', word_list[lastIndex])
        word_list = [word_list[lastIndex]] + word_list
        word_list.pop(lastIndex + 1)

      title = " ".join(word_list)
      return title


    def find_movies_by_title(self, title):
      """ Given a movie title, return a list of indices of matching movies.

      - If no movies are found that match the given title, return an empty list.
      - If multiple movies are found that match the given title, return a list
      containing all of the indices of these matching movies.
      - If exactly one movie is found that matches the given title, return a list
      that contains the inidex of that matching movie.

      Example:
        ids = chatbot.find_movies_by_title('Titanic')
        print(ids) // prints [1359, 1953]

      :param title: a string containing a movie title
      :returns: a list of indices of matching movies
      """
      if self.creative:
        # handles incorrect capitalization already
        # todo: handle alternate/foreign titles
        # if it's a substring of the entire movie 
        # extraction also extracts the proper movie

        title = self.process_title(title)
        id_list = []
        movie_list = movielens.titles()
        for i in range(len(movie_list)):
          movie_with_year = movie_list[i][0].lower()
          movie = re.sub(' \(\d{4}\)', '', movie_with_year)

          # Singular movie case 
          if title == movie or title == movie_with_year: 
            id_list.append(i)


      # NORMAL MODE
      else:
        title = self.process_title(title)
        id_list = []
        for i in range(len(self.titles)):
          movie_with_year = self.titles[i][0].lower()
          movie = re.sub(' \(\d{4}\)', '', movie_with_year)
          movie_noalt = re.sub(' \(.*\)', '', movie)
          if title in [movie, movie_with_year, movie_noalt]: 
            id_list.append(i)
            
      return id_list

    def extract_sentiment(self, text):
      """Extract a sentiment rating from a line of text.

      You should return -1 if the sentiment of the text is negative, 0 if the
      sentiment of the text is neutral (no sentiment detected), or +1 if the
      sentiment of the text is positive.

      As an optional creative extension, return -2 if the sentiment of the text
      is super negative and +2 if the sentiment of the text is super positive.

      Example:
        sentiment = chatbot.extract_sentiment('I liked "The Titanic"')
        print(sentiment) // prints 1

      :param text: a user-supplied line of text
      :returns: a numerical value for the sentiment of the text
      """
      neg_words = ["n't", "not", "no", "never"]
      punctuation = [".", ",", "!", "?", ";"]

      # for creative mode, add intensifiers
      extra_pos_words = ["loved", "fantastic", "incredible", "amazing", "great", "outstanding", "superb", "brilliant", "terrific"]
      extra_neg_words = ["awful", "terrible", "bad", "horrible", "disastrous", "hated", "sucked"]
      intensifiers = ["so", "very", "really", "extremely", "totally", "extra", "absolutely", "completely", "utterly"]

      extra_pos_words = [self.porter_stemmer.stem(s) for s in extra_pos_words]
      extra_neg_words = [self.porter_stemmer.stem(s) for s in extra_neg_words]
      intensifiers = [self.porter_stemmer.stem(s) for s in intensifiers]

      found_extra_pos = False
      found_extra_neg = False

      title = self.extract_titles(text) #remove title so its not included in sentiment
      if len(title) > 0: text = text.replace(title[0], "")

      tokens = re.findall(r"[\w']+|[.,!?;]", text)
      words = []
      for t in tokens:
        words = words + word_tokenize(t)

      pos_count = 0
      neg_count = 0
      i = 0
      foundIntensifier = False
      while i < len(words):
        w = self.porter_stemmer.stem(words[i])
        # check if really pos or really neg
        if self.creative:
          if w in extra_pos_words: found_extra_pos = True
          if w in extra_neg_words: found_extra_neg = True
          if w in intensifiers and i != len(words)-1:
            foundIntensifier = True
            nextWord = words[i+1]
            if nextWord in self.sentiment:
              if self.sentiment[nextWord] == "pos":
                found_extra_pos = True
              else:
                found_extra_neg = True
        #NORMAL mode starts
        if w in neg_words and i != len(words)-1: #Take opposite meaning of all words after
          j = i+1
          wordToNegate = self.porter_stemmer.stem(words[j])
          while wordToNegate not in punctuation and j < len(words):
            if wordToNegate in self.sentiment:
              if self.sentiment[wordToNegate] == "pos":
                if self.creative and foundIntensifier: 
                  found_extra_neg = True
                  foundIntensifier = False
                neg_count += 1
              else:
                if self.creative and foundIntensifier: 
                  found_extra_pos = True
                  foundIntensifier = False
                pos_count += 1
            j = j+1
            if j <= (len(words)-1): wordToNegate = self.porter_stemmer.stem(words[j])
          i = j #Jump ahead

        else: #find straight sentiment of words
          if w in self.sentiment:
            if self.sentiment[w] == "pos":
              pos_count += 1
            else:
              neg_count += 1
          i = i+1

      if self.creative and (found_extra_neg or found_extra_pos):
        if found_extra_neg and found_extra_pos:
          return 0
        elif found_extra_pos:
          return 2
        else:
          return -2

      if pos_count > neg_count:
        return 1
      elif neg_count > pos_count:
        return -1
      else:
        return 0

    def extract_sentiment_for_movies(self, text):
      """Creative Feature: Extracts the sentiments from a line of text
      that may contain multiple movies. Note that the sentiments toward
      the movies may be different.

      You should use the same sentiment values as extract_sentiment, described above.
      Hint: feel free to call previously defined functions to implement this.

      Example:
        sentiments = chatbot.extract_sentiment_for_text('I liked both "Titanic (1997)" and "Ex Machina".')
        print(sentiments) // prints [("Titanic (1997)", 1), ("Ex Machina", 1)]

      :param text: a user-supplied line of text
      :returns: a list of tuples, where the first item in the tuple is a movie title,
        and the second is the sentiment in the text toward that movie
      """

      pattern = '(.*"([^"]*)".*)(and|but|or|nor|yet)(.*"([^"]*)")'
      split = re.findall(pattern, text)[0]

      sentiment_one = self.extract_sentiment(split[0])
      sentiment_two = self.extract_sentiment(split[4])
      title_one = split[1]
      title_two = split[4]

      #if sentiment unclear, clarify. 
      if sentiment_one == 0 and sentiment_two != 0:
        if split[2] == "but":
          sentiment_one = -sentiment_two
        else:
          sentiment_one = sentiment_two
      elif sentiment_two == 0 and sentiment_one != 0:
        if split[2] == "but": 
          sentiment_two = -sentiment_one
        else:
          sentiment_two = sentiment_one

      sentiment = [(title_one, sentiment_one), (title_two, sentiment_two)]
      print(sentiment)
      return(sentiment)

    def edit_distance(self, movie1, movie2, max_distance):
      rows = len(movie1) + 1
      cols = len(movie2) + 1
      grid = [[0 for col in range(cols)] for row in range(rows)]

      for row in range(1, rows):
        grid[row][0] = row
      
      for col in range(1, cols):
        grid[0][col] = col
      
      for col in range(1, cols):
        for row in range(1, rows):
          cost = 2
          if movie1[row-1] == movie2[col-1]:
            cost = 0
          deletion = 1 + grid[row-1][col]
          insertion = 1 + grid[row][col-1]
          sub = cost + grid[row-1][col-1]
          grid[row][col] = min(deletion, insertion, sub)
          # if grid[row][col] > max_distance:
          #   return -1
      #print(grid)
      return grid[row][col]

    def find_movies_closest_to_title(self, title, max_distance=3):
      """Creative Feature: Given a potentially misspelled movie title,
      return a list of the movies in the dataset whose titles have the least edit distance
      from the provided title, and with edit distance at most max_distance.

      - If no movies have titles within max_distance of the provided title, return an empty list.
      - Otherwise, if there's a movie closer in edit distance to the given title 
        than all other movies, return a 1-element list containing its index.
      - If there is a tie for closest movie, return a list with the indices of all movies
        tying for minimum edit distance to the given movie.

      Example:
        chatbot.find_movies_closest_to_title("Sleeping Beaty") # should return [1656]

      :param title: a potentially misspelled title
      :param max_distance: the maximum edit distance to search for
      :returns: a list of movie indices with titles closest to the given title and within edit distance max_distance
      """

      title = self.process_title(title)

      id_list = []
      movie_list = movielens.titles()
      editDistances = {}
      minEditDistance = math.inf
      for i in range(len(movie_list)):
        movie = self.process_title(movie_list[i][0]).lower()

        editDistance = self.edit_distance(movie, title, max_distance)

        movie = re.sub("\s\((\d{4})\)", "", movie) # remove date
        movie = self.process_title_reverse(movie) # move "the" "an", etc to start

        editDistance_YearRemoved = self.edit_distance(movie, title, max_distance)

        # update new minimum edit distance
        if editDistance < minEditDistance and editDistance != -1:
          minEditDistance = editDistance
        if editDistance_YearRemoved < minEditDistance and editDistance_YearRemoved != -1:
          minEditDistance = editDistance_YearRemoved

        if editDistance <= max_distance and editDistance != -1:
          if editDistance in editDistances:
            editDistances[editDistance].append(i)
          else:
            editDistances[editDistance] = [i]

        elif editDistance_YearRemoved <= max_distance and editDistance_YearRemoved != -1:
          if editDistance_YearRemoved in editDistances:
            editDistances[editDistance_YearRemoved].append(i)
          else:
            editDistances[editDistance_YearRemoved] = [i]
      
      #Find all movies that are the minimum edit distance away
      if minEditDistance <= max_distance:
        options = editDistances[minEditDistance]
        for i in options:
          id_list.append(i)

      return id_list

    def ambiguous_entry(self, id_list):
      response = "I found a few movies that fit that description. Did you mean "
      for i in range(len(id_list)):
        response += "\"" + self.titles[id_list[i]][0] + "\""
        if i < len(id_list) - 1:
          response += ", "
        if i == len(id_list) - 2:
          response += "or "
      response += "?"
      return response

    def disambiguate(self, clarification, candidates):
      """Creative Feature: Given a list of movies that the user could be talking about 
      (represented as indices), and a string given by the user as clarification 
      (eg. in response to your bot saying "Which movie did you mean: Titanic (1953) 
      or Titanic (1997)?"), use the clarification to narrow down the list and return 
      a smaller list of candidates (hopefully just 1!)

      - If the clarification uniquely identifies one of the movies, this should return a 1-element
      list with the index of that movie.
      - If it's unclear which movie the user means by the clarification, it should return a list
      with the indices it could be referring to (to continue the disambiguation dialogue).

      Example:
        chatbot.disambiguate("1997", [1359, 2716]) should return [1359]
      
      :param clarification: user input intended to disambiguate between the given movies
      :param candidates: a list of movie indices
      :returns: a list of indices corresponding to the movies identified by the clarification
      """

      fitting = []
      year = ""
      for movie in candidates:
        alt_titles = []
        title = self.titles[movie][0].lower()
        #year = re.findall("\d{4}", title.split()[-1])[0]
        alts = re.findall(' \(.[^\)\(]*\)', title) # find foreign titles in parenthesis
        title = re.sub("\(.*\)",'', title)
        for i in range(len(alts)):
              alt_title = re.sub('[\(\)]','', alts[i])
              alts[i] = self.process_title_reverse(re.sub('aka ', '', alt_title).lstrip())
        if (clarification in title) or (clarification in alts) or (alts[-1] in clarification):
          fitting.append(movie)
      if clarification.isdigit() and int(clarification) <= len(candidates):
        fitting.append(candidates[int(clarification) - 1])
      return fitting


    #############################################################################
    # 3. Movie Recommendation helper functions                                  #
    #############################################################################

    def binarize(self, ratings, threshold=2.5):
      """Return a binarized version of the given matrix.

      To binarize a matrix, replace all entries above the threshold with 1.
      and replace all entries at or below the threshold with a -1.

      Entries whose values are 0 represent null values and should remain at 0.

      :param x: a (num_movies x num_users) matrix of user ratings, from 0.5 to 5.0
      :param threshold: Numerical rating above which ratings are considered positive

      :returns: a binarized version of the movie-rating matrix
      """
      #############################################################################
      # TODO: Binarize the supplied ratings matrix.                               #
      #############################################################################

      # The starter code returns a new matrix shaped like ratings but full of zeros.
      binarized_ratings = np.where(np.logical_or(ratings > threshold, ratings == 0), ratings, -1 )
      binarized_ratings = np.where(binarized_ratings < threshold, binarized_ratings, 1)


      #############################################################################
      #                             END OF YOUR CODE                              #
      #############################################################################
      return binarized_ratings


    def similarity(self, u, v):
      """Calculate the cosine similarity between two vectors.

      You may assume that the two arguments have the same shape.

      :param u: one vector, as a 1D numpy array
      :param v: another vector, as a 1D numpy array

      :returns: the cosine similarity between the two vectors
      """
      #############################################################################
      # TODO: Compute cosine similarity between the two vectors.
      #############################################################################
      denom = float(np.sqrt(np.dot(u,u) * np.dot(v, v))) 
      cos = 0
      if denom != 0:
        cos = (np.dot(u, v)) / denom
      #############################################################################
      #                             END OF YOUR CODE                              #
      #############################################################################
      return cos


    def recommend(self, user_ratings, ratings_matrix, k=10, creative=False):
      """Generate a list of indices of movies to recommend using collaborative filtering.

      You should return a collection of `k` indices of movies recommendations.

      As a precondition, user_ratings and ratings_matrix are both binarized.

      Remember to exclude movies the user has already rated!

      :param user_ratings: a binarized 1D numpy array of the user's movie ratings
      :param ratings_matrix: a binarized 2D numpy matrix of all ratings, where
        `ratings_matrix[i, j]` is the rating for movie i by user j
      :param k: the number of recommendations to generate
      :param creative: whether the chatbot is in creative mode

      :returns: a list of k movie indices corresponding to movies in ratings_matrix,
        in descending order of recommendation
      """

      #######################################################################################
      # TODO: Implement a recommendation function that takes a vector user_ratings          #
      # and matrix ratings_matrix and outputs a list of movies recommended by the chatbot.  #
      #                                                                                     #
      # For starter mode, you should use item-item collaborative filtering                  #
      # with cosine similarity, no mean-centering, and no normalization of scores.          #
      #######################################################################################

      # Populate this list with k movie indices to recommend to the user.
      recommendations = []
      user_movies = np.nonzero(user_ratings)[0]

      for movie_id in range(len(ratings_matrix)):

        if movie_id in user_movies: continue
        rating_xi = 0
        for j in user_movies:
          sim = self.similarity(ratings_matrix[j], ratings_matrix[movie_id])
          rating_xi += sim * user_ratings[j]
        
        recommendations.append([movie_id, rating_xi])

      sorted_recs = sorted(recommendations, key=lambda tup: tup[1], reverse = True) 
      #print(sorted_recs)
      
      top_recs = [x[0] for x in sorted_recs[0:k]]

      #############################################################################
      #                             END OF YOUR CODE                              #
      #############################################################################
      return top_recs

    drinks = {
    "Comedy": "Riesling, for the levity and dry humor.",
    "Romance": "Cabernet Sauvignon from Chateau Montelena, a California favorite.",
    "Drama": "Rosé, duh!",
    "Documentary": "Craft Beer, to connect with the local.",
    "Crime": "19 Crimes Cabernet Sauvignon",
    "Children": "Juice Box, to taste the fun!",
    "Sci-Fi": "Water, to stay grounded.",
    "Action": "a case of your favorite IPA.",
    "Adventure": "to get out there and whip up something in the kitchen yourself!",
    "Fantasy": "Champagne, for the light and whimsical.",
    "Horror": "Bloody Mary, to be in theme.",
    "Thriller": "Bloody Mary, to dull the senses.",
    "Mystery": "Merlot, to bring out distinguished depth and character.",
    "Animation": "Soda, for a little pep in your step.",
    "War": "Whiskey, because we know that's what the actors would be drinking."
    }

    def drink_recommendation(self, recommendation):
      # movie recommendation was passed in
      # this is just the movie name
      # find that movie name in movielens
      if (movielens.titles(recommendation[1]) != null):
        genres = movielens.titles(recommendation)[1]
        # get all genres
        genres = genres.split("|")
        # choose one of the genres
        genre = random.choice(genres)
        # map genre to recommendation
        drink = drinks[genre]
        # for {genre} movies, we'd recommend {response}
      return drink
    
    snacks = {
    "Comedy": "Popcorn",
    "Romance": "Dove Dark Chocolate",
    "Drama": "drama food",
    "Documentary": "doc food",
    "Crime": "crime food",
    "Children": "child food",
    "Sci-Fi": "scifi food",
    "Action": "action food",
    "Adventure": "adv food",
    "Fantasy": "fantasy food",
    "Horror": "horror food",
    "Thriller": "thriller food",
    "Mystery": "mystery food",
    "Animation": "anim food",
    "War": "war food"
    }

    def snack_recommendation (self, recommendation):
      # movie rec passed in - the full thing (the two part situation)
      # find movie in movielens
      # find genre
      # map genre to snack
      # find movie in movielens
      if (movielens[recommendation][1] != null):
        genres = movielens[recommendation][1]
        # get all genres
        genres = genres.split("|")
        # choose one of the genres
        genre = random.choice(genres)
        # map genre to recommendation
        snack = snacks[genre]
      return snack


    #############################################################################
    # 4. Debug info                                                             #
    #############################################################################

    def debug(self, line):
      """Return debug information as a string for the line string from the REPL"""
      # Pass the debug information that you may think is important for your
      # evaluators
      debug_info = 'debug info'
      return debug_info


    #############################################################################
    # 5. Write a description for your chatbot here!                             #
    #############################################################################
    def intro(self):
      """Return a string to use as your chatbot's description for the user.

      Consider adding to this description any information about what your chatbot
      can do and how the user can interact with it.
      """
      return """
      Your task is to implement the chatbot as detailed in the PA6 instructions.
      Remember: in the starter mode, movie names will come in quotation marks and
      expressions of sentiment will be simple!
      Write here the description for your own chatbot!
      """


if __name__ == '__main__':
  print('To run your chatbot in an interactive loop from the command line, run:')
  print('    python3 repl.py')
