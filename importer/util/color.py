def color(option, message):
    option_list = {
        "title_card" : "97;42m",
        "white": "97m",
        "magneta": "95m",
        "green": "92m",
        "red": "91m",
        "yellow": "93m",
        "blue": "94m",
        "grey": "90m",
        "cyan": "96m",
    }
    option_selected = option_list.get(option, None)

    result = f"\033[{option_selected}{message}\033[0m" if option_selected else message

    return result

def process_print_division():
   print(color("grey", "--------------------------------------------------------------------"))
   return