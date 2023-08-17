import json

def process_text_data():
    #Load the word_data_dict from the saved JSON file
    #loaded_word_data_dict = {}
    with open('last.json', 'r') as file:
        loaded_word_data_dict = json.load(file)



    while True:
        provided_text = input("Enter a text (or 'NULL' to stop): ")
        
        if provided_text == "NULL":
            break

        # Split the provided text into words
        text_words = provided_text.split()
        
        batch_size = 10000
        for batch_start in range(0, len(text_words), batch_size):
            batch_words = text_words[batch_start:batch_start + batch_size]
            for i in range(1, len(batch_words)):
                previous_word = batch_words[i - 1].lower()
                current_word = batch_words[i].lower()

                if current_word in loaded_word_data_dict:
                    if 'count' in loaded_word_data_dict[current_word]:
                        loaded_word_data_dict[current_word]['count'] += 1
                    else:
                        loaded_word_data_dict[current_word]['count'] = 1
                    if previous_word in loaded_word_data_dict:
                        if current_word in loaded_word_data_dict[previous_word]['other_words']:
                            if current_word not in loaded_word_data_dict[previous_word]['other_words']:
                                loaded_word_data_dict[previous_word]['other_words'][current_word] = 1
                            else:
                                loaded_word_data_dict[previous_word]['other_words'][current_word] += 1
                                for word in loaded_word_data_dict:
                                    if current_word not in loaded_word_data_dict[word]['other_words']:
                                        loaded_word_data_dict[word]['other_words'][current_word] = 1
                                    else:
                                        loaded_word_data_dict[word]['other_words'][current_word] += 1
                        else:
                            loaded_word_data_dict[previous_word]['other_words'][current_word] = 1
                    else:
                        for word in loaded_word_data_dict:
                            loaded_word_data_dict[current_word]['other_words'][word]= 1
                else:
                    loaded_word_data_dict[current_word] = {
                        'cleaned_words': [],
                        'other_words': {}
                    }
                    loaded_word_data_dict[previous_word] = {
                        'cleaned_words': [],
                        'other_words': {}
                    }
                    for word in loaded_word_data_dict:
                        loaded_word_data_dict[current_word]['other_words'][word] = 1
                    loaded_word_data_dict[current_word]['other_words'][previous_word] = 1
                    for word in loaded_word_data_dict:
                        if current_word not in loaded_word_data_dict[word]['other_words']:
                            loaded_word_data_dict[word]['other_words'][current_word] = 1
                        else:
                            loaded_word_data_dict[word]['other_words'][current_word] += 1
                    loaded_word_data_dict[current_word]['count'] = 1

        # Save the updated word_data_dict to the JSON file
        with open('last.json', 'w') as file:
            json.dump(loaded_word_data_dict, file, indent=4)

if __name__ == "__main__":
    process_text_data()








