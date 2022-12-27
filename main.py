import collections
import os
import re
import string
import advertools as adv
import random

def compute_exact_counts(text):
    # Compute the exact number of occurrences of each letter using collections library
    letter_counts = collections.Counter(text.upper())
    return letter_counts

def process_file(filename):
    with open(f'files/{filename}', 'r') as f:
        text = f.read()
        # Extract the language from the Project Gutenberg's file using a regular expression
        regex = r'Language: ([a-zA-Z]+)'
        match = re.search(regex, text)
        # Find the start and end indexes of header and footer for removal and extract the body
        header_end = text.find('*** START OF THIS PROJECT GUTENBERG EBOOK')
        footer_start = text.find('*** END OF THIS PROJECT GUTENBERG EBOOK')
        text = text[header_end+len('*** START OF THIS PROJECT GUTENBERG EBOOK'):footer_start+len('*** END OF THIS PROJECT GUTENBERG EBOOK')]
        # Removing stopwords, punctuation marks and convert text to uppercase
        stopwords = []
        if match:
            language = match.group(1).lower()
            stopwords = set(adv.stopwords[language])
        text = ''.join([word for word in text.split() if word.lower() not in stopwords])
        text = text.translate(str.maketrans('', '', string.punctuation)).upper()
    return text

def space_saving_count(text, k):
    probability = 1.0
    letter_counter = {}
    letter_probability = {}
    # Process the text
    for char in text:
        # Update letter count (and letter probability if the item is new)
        if char in letter_counter:
            letter_counter[char] += 1
        else:
            letter_counter[char] = 1
            letter_probability[char] = probability
            # Decrease probability with a 1/2^k factor
            probability *= 0.5
        # If the counter is full, start the letter removal procedure
        if len(letter_counter) > k:
            # Choose a letter to remove based on the probability counter
            p = random.uniform(0, 1)
            for char, prob in letter_probability.items():
                if p < prob:
                    del letter_counter[char]
                    del letter_probability[char]
                    break
    return letter_counter

def test_estimate_frequent_letters(text, k):
    # Start by computing the exact count for future comparison with estimates
    errors = []
    exact_counts = compute_exact_counts(text)
    total_error = 0
    # Repeat the approximate count 10 times:
    repetitions = 10
    for i in range(repetitions):
        estimate_counts = space_saving_count(text, k)
        error = sum(abs(estimate_counts[letter] - exact_counts[letter]) for letter in exact_counts)
        errors.append(error)
    average_error = sum(errors) / repetitions
    highest_error = max(errors)
    lowest_error = min(errors)
    print(f"k={k}\nLowest error: {lowest_error}\nAverage error: {average_error}\nHighest error: {highest_error}\n==========")
    return average_error

def compare_performance(text):
    # Compare the performance of the approximate counters and the data stream algorithm
    k_values = [3, 5, 10]
    errors = {}
    for k in k_values:
        errors[k] = test_estimate_frequent_letters(text, k)
    return errors

def main():
    for filename in os.listdir('files'):
        text = process_file(filename)
        errors = compare_performance(text)
        print(errors)

if __name__ == '__main__':
    main()
