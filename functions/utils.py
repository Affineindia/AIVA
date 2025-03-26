import ast

def clean_json(input):
    try:
        if "```json" in input:
            input = input.replace("```json", "")
        if "```" in input:
            input = input.replace("```", "")
        input = ast.literal_eval(input)
    except:
        pass
    try:
        input = ast.literal_eval(input)
    except:
        pass
    
    return input