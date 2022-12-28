import collections
import os
import re
import string
import advertools as adv
import random
from heapq import heappush, heappop

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

def decreasing_probability_count(text):
    counter = {}
    for char in text:
        if char not in counter:
            counter[char] = 0
        count = counter[char]
        p = random.uniform(0, 1)
        if p < 1/(2**count):
            counter[char] += 1
        

def space_saving_count(text, k):
    letter_counter = {}
    heap = []
    for char in text:
        # Update letter count
        if char in letter_counter:
            letter_counter[char] += 1
        else:
            letter_counter[char] = 1
            if len(heap) > k:
                # Get the smallest count of the heap and replace it if the new character has a bigger count
                smallest_count = heap[0][0]
                if smallest_count < letter_counter[char]:
                    heappop(heap)
                    heappush(heap,(letter_counter[char],char))
            else:
                # Push if the heap is not full yet
                heappush(heap,(letter_counter[char],char))
    return heap

def test_estimate_frequent_letters(text, k):
    # Start by computing the exact count for future comparison with estimates
    errors = []
    exact_counts = compute_exact_counts(text)
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
