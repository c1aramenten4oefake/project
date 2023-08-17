import json
import random
import language_tool_python

def random_text_gen():
    tool = language_tool_python.LanguageToolPublicAPI('en-UK')
    with open('last.json', 'r') as file:
        loaded_word_data_dict = json.load(file)

    def generate_random_output(outcomes):
        outcome_list = list(outcomes.keys())
        weights = list(outcomes.values())
        random_output = random.choices(outcome_list, weights=weights, k=1)
        return random_output[0]

    def generate_random_text(word_data_dict, start_word, num_words):
        generated_text = [start_word]

        for _ in range(num_words - 1):
            prev_word = generated_text[-1]
            possible_next_words = word_data_dict[prev_word]['other_words']

            if possible_next_words:
                next_word = generate_random_output(possible_next_words)
                generated_text.append(next_word)
            else:
                break  # No more possible words, exit loop

        return ' '.join(generated_text)

    start_word = random.choice(list(loaded_word_data_dict.keys()))

    # Get a random number of words for the generated text
    num_words = random.randint(15, 155)  # You can adjust the range as needed

    # Generate the random text
    random_text = generate_random_text(loaded_word_data_dict, start_word="anarcho-monarchism", num_words=23)

    # Correct the random text
    corrected_text = tool.correct(random_text)

    print(corrected_text)
    return corrected_text

if __name__ == "__main__":
    random_text_gen()

