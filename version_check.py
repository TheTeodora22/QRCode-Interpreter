import pandas as pd
import unicode_analyze as ua
import data_segment as ds

def version_check(input_text):
    # URL of the website
    url = "https://www.thonky.com/qr-code-tutorial/character-capacities"

    # Read all tables from the webpage
    tables = pd.read_html(url)

    # Display the first table
    df = tables[1]


    data_dict = df.to_dict(orient="records")

    modes = ua.analyze_encodings(input_text)
    unicode = ua.best_mode(modes)
    chosen_modes = ua.print_encodable_modes(modes)
    text_mode =''


    if chosen_modes == 1:
        text_mode = 'numeric'
    elif chosen_modes == 2:    
        text_mode = 'alphanumeric'
    elif chosen_modes == 3:
        text_mode = 'byte'
    elif chosen_modes == 4:
        text_mode = 'kanji'

    count = ds.binary_count(input_text, text_mode)
    count = count // 8 + 1


    found_value = None
    for dict in data_dict:
        for item in dict:
            if unicode in item and dict[unicode] >= count:
                found_value = dict['Version']
                break
        if found_value is not None:
            break
    return found_value


