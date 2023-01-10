import os
import re
import string
import advertools as adv
import random
import sys
import matplotlib.pyplot as plt
from time import time

DATA_STREAM_REPETITIONS = 10
K_VALUES = [3, 5, 10]

def compute_exact_counts(text):

    # Compute the exact number of occurrences of each letter using collections library
    counter = {}
    for char in text:
        char = char.upper()
        if char not in counter:
            counter[char] = 1
        else:
            counter[char] += 1
    return counter

def process_file(filename):

    with open(f'files/{filename}', 'r') as f:
        text = f.read()

        # Extract the language from the Project Gutenberg's file using a regular expression
        regex = r'Language: ([a-zA-Z]+)'
        match = re.search(regex, text)

        # Find the start and end indexes of header and footer for removal and extract the body
        header_end = text.find('*** START OF TH')
        footer_start = text.find('*** END OF TH')
        text = text[header_end+50:footer_start+50]

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
            count = 0
            if char in counter:
                count = counter[char]
            p = random.uniform(0, 1)
            if p < 1/(2**count):
                if char not in counter:
                    counter[char] = 1
                else:
                    counter[char] += 1

        error = calculate_error(exact_counts,counter)
        if not best_counter or error < min(errors):
            best_counter = counter

        errors.append(error)

    average_error = sum(errors) / DATA_STREAM_REPETITIONS
    highest_error = max(errors)
    lowest_error = min(errors)

    print()
    print("Decreasing probability counter errors:")
    print(f"average_error error | {average_error}")
    print(f"highest_error | {highest_error}")
    print(f"lowest_error | {lowest_error}")
    print()

    return best_counter, lowest_error, average_error, highest_error

def space_saving_count(text, k):

    counter = {}

    for char in text:
        # Update letter count
        if char in counter:
            counter[char] += 1
        else:
            if len(counter) >= k:
                # Get the smallest count of the counter and replace it if the new character has a bigger count
                smallest_char = min(counter, key=counter.get)
                smallest_value = counter[smallest_char]
                del counter[smallest_char]
                counter[char] = smallest_value + 1
            else:
                # Push if the counter is not full yet
                counter[char] = 1

    return counter

def execute_methods(text, filename):
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

    print("exact counts size")
    print(sys.getsizeof(exact_counts))
    print()
    print("decreasing_probability_counter size")
    print(sys.getsizeof(decreasing_probability_counter) )
    print()
    print("space_saving_counts size for k=10")
    print(sys.getsizeof(space_saving_counts[10]))


    # Compare performance between algorithms
    compare_performance(exact_counts,decreasing_probability_counter,space_saving_counts,filename)

def calculate_error(exact_counts, method_count):

    error = sum(abs(method_count[letter] - exact_counts[letter]) for letter in method_count)
    return error

def compare_performance(exact_counts,decreasing_probability_counter,space_saving_counts, filename):
    
    print("==================== EXACT COUNT =====================")
    # for k,v in sorted(exact_counts.items(), key=lambda item: -item[1])[:10]:
    #     print(f"{k} | {v}")

    print("==================== DECREASING PROBABILITY COUNT =====================")
    # for k,v in sorted(decreasing_probability_counter.items(), key=lambda item: -item[1])[:10]:
    #     print(f"{k} | {v}")
    compute_errors(exact_counts, decreasing_probability_counter,filename,"decreasing_probability")

    print("==================== SPACE-SAVING COUNT =====================")
    for i in space_saving_counts:
        print()
        print("FOR K = ", i)
        # for k,v in sorted(space_saving_counts[i].items(), key=lambda item: -item[1])[:10]:
        #     print(f"{k} | {v}")
        compute_errors(exact_counts, space_saving_counts[i],filename,f"space_saving_k{i}")

def store_graph(name, dictionary):

    dictionary = dict(sorted(dictionary.items(), key=lambda item: -item[1]))

    # Define the data to plot
    characters = list(dictionary.keys())[:20]
    values = list(dictionary.values())[:20]

    # Create a figure and axis
    fig, ax = plt.subplots()

    # Plot the data
    ax.bar(characters, values)
    plt.ylabel('Count')
    plt.savefig(f"images/{name}.png")

def compute_errors(exact_counts, approximate_counts,filename,methodname):
    absolute_errors = { char : abs(exact_counts[char] - approximate_counts[char]) for char in approximate_counts }
    relative_errors = { char : (absolute_errors[char]/exact_counts[char]) for char in approximate_counts }
    min_absolute_error, avg_absolute_error, max_absolute_error = min(absolute_errors.values()), sum(absolute_errors.values())/len(absolute_errors), max(absolute_errors.values())
    min_relative_error, avg_relative_error, max_relative_error = min(relative_errors.values()), sum(relative_errors.values())/len(relative_errors), max(relative_errors.values())
    # print(f"min_absolute_error | {min_absolute_error}")
    # print(f"avg_absolute_error | {avg_absolute_error}")
    # print(f"max_absolute_error | {max_absolute_error}")
    # print(f"min_relative_error | {min_relative_error}")
    # print(f"avg_relative_error | {avg_relative_error}")
    # print(f"max_relative_error | {max_relative_error}")
    store_graph(f"{filename[:-4]}_{methodname}_absolute", absolute_errors)
    store_graph(f"{filename[:-4]}_{methodname}_relative", relative_errors)
    return min_absolute_error, avg_absolute_error, max_absolute_error, min_relative_error, avg_relative_error, max_relative_error

def main():

    for filename in os.listdir('files'):
        print("=========================================")
        print("Processing ", filename)
        print()
        text = process_file(filename)
        execute_methods(text, filename)

if __name__ == '__main__':
    main()
