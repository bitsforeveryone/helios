from libhelios import heliosChallenge, heliosLanguages

class helloWorldC(heliosChallenge.heliosChallenge):
    name = "Hello World"
    prompt = "Why don't you say hi to me?"
    language = heliosLanguages.Languages.C
    output = "Hello World\n"
    userin = ""
    cmdline_in = ""
    points = 10

    def __init__(self):
        super().__init__()
