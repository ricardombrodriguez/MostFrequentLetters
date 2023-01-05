import collections
import os
import re
import string
import advertools as adv
import random
from time import time
from heapq import heappush, heappop

DATA_STREAM_REPETITIONS = 10
K_VALUES = [3, 5, 10]

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

def decreasing_probability_count(exact_counts,text):
    errors = []
    best_counter = None
    for _ in range(DATA_STREAM_REPETITIONS):
        counter = {}
        for char in text:
            if char not in counter:
                counter[char] = 0
            count = counter[char]
            p = random.uniform(0, 1)
            if p < 1/(2**count):
                counter[char] += 1
        print("decreasing")
        print(counter)
        print(exact_counts)
        error = calculate_error(exact_counts,counter)
        if not best_counter or error < min(errors):
            best_counter = counter
        errors.append(error)
    average_error = sum(errors) / DATA_STREAM_REPETITIONS
    highest_error = max(errors)
    lowest_error = min(errors)
    print("decreasing")
    print(best_counter)
    return best_counter, lowest_error, average_error, highest_error

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
    print(heap)
    return heap

def execute_methods(text):
    # Compare the performance of the approximate counters and the data stream algorithm
    
    # Exact count
    start = time()
    exact_counts = compute_exact_counts(text)
    exact_counts_time = time() - start
    
    # Decreasing probability counter (approximate count)
    start = time()
    decreasing_probability_counter, lowest_error, average_error, highest_error = decreasing_probability_count(exact_counts,text)
    decreasing_probability_counter_time = time() - start

    # Space-Saving count for each k € [3,5,10]
    start = time()
    space_saving_counts =  { k : space_saving_count(text, k) for k in K_VALUES }
    space_saving_counts_time = time() - start

    # Compare performance between algorithms
    compare_performance(exact_counts,decreasing_probability_counter,space_saving_counts)

def calculate_error(exact_counts, method_count):
    error = sum(abs(method_count[letter] - exact_counts[letter]) for letter in exact_counts)
    return error

def compare_performance(exact_counts,decreasing_probability_counter,space_saving_counts):
    
    print("==================== EXACT COUNT =====================")
    print(exact_counts.keys())

    print("==================== DECREASING PROBABILITY COUNT =====================")
    print(decreasing_probability_counter.keys())

    print("==================== SPACE-SAVING COUNT =====================")
    for k in space_saving_counts:
        print(f"k={k} | {space_saving_counts[k]}")

def main():
    for filename in os.listdir('files'):
        text = process_file(filename)
        execute_methods(text)

if __name__ == '__main__':
    main()
