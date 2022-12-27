import collections
import os
import re
import string
import advertools as adv


def compute_exact_counts(text):
    # Compute the exact number of occurrences of each letter with collections library
    letter_counts = collections.Counter(text.lower())
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
        text = ' '.join([word for word in text.split() if word.lower() not in stopwords])
        text = text.translate(str.maketrans('', '', string.punctuation)).upper()
    return text

def estimate_frequent_letters(text, k):
    # Estimate the k most frequent letters using a data stream algorithm
    letter_counts = collections.Counter()
    for letter in text.lower():
        letter_counts[letter] += 1
        if len(letter_counts) > k:
            # Remove the least frequent letter using the Space-Saving Count algorithm with a Decreasing probability counter of 1/2^k
            min_count = min(letter_counts.values())
            for letter, count in list(letter_counts.items()):
                if count == min_count:
                    del letter_counts[letter]
    return letter_counts

def test_estimate_frequent_letters(text, k):
    # Start by computing the exact count for future comparison with estimates
    exact_counts = compute_exact_counts(text)
    total_error = 0
    # Repeat the approximate count 10 times:
    for i in range(10):
        estimate_counts = estimate_frequent_letters(text, k)
        print(estimate_counts)
        error = sum(abs(estimate_counts[letter] - exact_counts[letter]) for letter in string.ascii_lowercase)
        total_error += error
    average_error = total_error / 26
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
