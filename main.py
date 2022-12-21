import collections
import os
import string

def compute_exact_counts(text):
    # Compute the exact number of occurrences of each letter
    letter_counts = collections.Counter(text.lower())
    return letter_counts

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
    # Perform a set of tests to evaluate the quality of estimates
    exact_counts = compute_exact_counts(text)
    total_error = 0
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
        print(filename)
        with open(f'files/{filename}', 'r') as f:
            text = f.read()
            errors = compare_performance(text)
            print(errors)

if __name__ == '__main__':
    main()
