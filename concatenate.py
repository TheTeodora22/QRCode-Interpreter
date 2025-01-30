import unicode_analyze as ua
import data_segment as ds
import version_check as vc

def concatenate(input_text):
    modes = ua.analyze_encodings(input_text)
    unicode = bin(ua.print_encodable_modes(modes))

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

    versiune,size = vc.version_check(input_text)
    size = int(size)
    count = ds.binary_count(input_text, text_mode)

    data = "".join(ds.string_to_binary(input_text, text_mode))

    terminator = min(4, size-len(data)-count-4)




input_text = input()
concatenate(input_text)