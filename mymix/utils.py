def strip_off_punc(string):
        
    punctuations = '''!()-[]{};:'"\,<>./?~'''
    no_punct = ""
    for char in string:
       if char not in punctuations:
           no_punct = no_punct + char
    
    return no_punct



def remove_comments(string):
    punctuations = '-('
    new_string = ""
    for char in string:
        if char not in punctuations:
            new_string += char
        else:
            return new_string.strip().lower()

    return new_string.lower()    