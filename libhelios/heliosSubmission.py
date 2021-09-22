# when code is sent to the server, submission is instantiated with:
# user, challenge, code sent
from time import sleep

import docker
from libhelios import heliosLanguages, heliosChallenge

class heliosSubmission:

    # docker is used to isolate instances. Class level
    dockerClient=None

    # constants


    def __init__(self, user, challenge, submission : str):
        self.user=user
        self.challenge=challenge
        self.submission=submission

        # if no docker client, create
        if heliosSubmission.dockerClient is None:
            heliosSubmission.dockerClient=docker.from_env()
            heliosSubmission.dockerClient.images.pull("frolvlad/alpine-gcc")


    # check submission by passing code to a container and checking against challenge output
    def check(self):
        correct=False

        # check for c programs. Make container, compile, check output
        if(self.challenge["language"] == "C"):
            return all([
                self.testC(test["userInput"],test["cmdLineArgs"], test["output"])
                for test in self.challenge["tests"]])




    def testC(self,userin,cmdline, neededOutput):
        compileCprogram = f"echo '{self.submission}' > submit.c && " \
                          f"echo -e '{userin}' > userin.doc && " \
                          "gcc --static submit.c -o submit && " \
                          "chmod +x submit && " \
                          f"./submit < userin.doc {cmdline}"
        newContainer = heliosSubmission.dockerClient.containers.run("frolvlad/alpine-gcc",
                                                                    ["/bin/sh", "-c", compileCprogram],
                                                                    detach=True,
                                                                    ports={"5000/tcp": "5000"}
                                                                    )
        # sleep to allow compilation before container removal
        sleep(3)
        programOutput = newContainer.logs()
        newContainer.stop()
        newContainer.remove()
        return programOutput.decode('utf-8') == neededOutput