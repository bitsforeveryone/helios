from libhelios import heliosChallenge, heliosLanguages

class calculatorC(heliosChallenge.heliosChallenge):
    name = "Calculator"
    prompt = "I need to know what these numbers are, stat"
    language = heliosLanguages.Languages.C
    output = "Enter two numbers: Product = 8.00"
    userin = "2 4"
    cmdline_in = ""
    points = 10

    def __init__(self):
        super().__init__()
