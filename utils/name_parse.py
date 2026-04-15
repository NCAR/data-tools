
def split_name_string(name_string):
    """
    This function takes a person's full name, and if it has one whitespace separating two words and no commas,
    e.g. "John Doe", it returns (first_name="John", last_name="Doe").  If the full name
    has three words, no commas, and the middle word is in the form of a middle initial, e.g. "Jane L. Plain",
    then return (first_name="Jane", last_name="Plain"). .

    If the word string has a comma, e.g. "Plain, Jane L.", then return (first_name="Jane", last_name="Plain").
    This function also removes all occurrences of "Jr." in a name.
    """
    name_string = name_string.replace(", Jr.", "")
    name_string = name_string.replace(" Jr.", " ")
    first_name = None
    last_name = None

    no_comma = ',' not in name_string
    words = name_string.split()
    if no_comma and len(words) == 2 :
        first_name = words[0]
        last_name = words[1]
    elif no_comma and len(words) == 3:
        first_name = words[0]
        last_name = words[2]
    elif not no_comma:
        string_parts = name_string.split(',')
        last_name = string_parts[0].strip()
        # Take just the first part of what follows the comma.
        first_name = string_parts[1].split()[0]
    return first_name, last_name