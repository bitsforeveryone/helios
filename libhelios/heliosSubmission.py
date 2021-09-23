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
        self.userID=user
        self.challenge=challenge
        self.submission=submission

        # if no docker client, create
        if heliosSubmission.dockerClient is None:
            heliosSubmission.dockerClient=docker.from_env()
            heliosSubmission.dockerClient.images.pull("frolvlad/alpine-gcc")
            heliosSubmission.dockerClient.images.pull("emilienmottet/nasm")


    # check submission by passing code to a container and checking against challenge output
    def check(self,db):
        correct=False
        print(self.challenge)
        # check for c programs. Make container, compile, check output
        if(self.challenge["language"] == "C"):
            testResult= self.testC(self.submission,self.challenge["tests"])
        if (self.challenge["language"] == "ASM64"):
            testResult = self.testASM64(self.submission, self.challenge["tests"])
        if testResult[0] == "Success":
            db.submissions.replace_one(
                {"challenge": self.challenge["_id"],
                 "userID": self.userID},
                {
                    "challenge": self.challenge["_id"],
                    "userID": self.userID,
                    "attempt": self.submission,
                    "language": self.challenge["language"]
                }, upsert=True)
        return testResult



    @staticmethod
    # given a set of tests and a submission, compile code using docker and test
    # return tuple of Success, Failure, or Error
    # if Error or Failure, second value in tuple is the return value
    def testC(submission,tests):
        # write submission to a source file, then write the challenge's userinput to a userin file for piping
        # then create a shell script that will run the target binary with command line args
        # then compile, make everything executable, and run shell script with specified args
        # TODO: re-use container between test attempts

        compileCprogram = f"echo '{submission}' > submit.c && " \
                          "gcc --static submit.c -o submit && " \
                          "chmod +x submit"

        testCprogram=[]
        for test in tests:
            # create the userin/shell script. Also communicate BREAK between outputs..
            testCprogram.append(f"echo -e '{ test['userInput'] }' > userin.doc && "
                                f"echo -e '#!/bin/sh\n\n./submit { test['cmdLineArgs'] }' > runscript.sh && "
                                f"chmod +x runscript.sh && "
                                f"./runscript.sh < userin.doc"
                                )

        testCprogram= " && echo 'BREAK' && ".join(testCprogram)
        finalCommand=compileCprogram+" && "+testCprogram

        newContainer = heliosSubmission.dockerClient.containers.run("frolvlad/alpine-gcc",
                                                        ["/bin/sh", "-c", finalCommand],
                                                        detach=True,
                                                        ports={"5000/tcp": "5000"}
                                                        )
        # sleep to allow compilation before container removal
        sleep(3)
        # split output on BREAK to get distinct lines
        programOutput = newContainer.logs().decode('utf-8').split('BREAK\n')
        # clean up
        newContainer.stop()
        newContainer.remove()

        # for each test, compare test expected output with actual output
        if len(programOutput)==len(programOutput):
            for index,test in enumerate(tests):
                if test['output']==programOutput[index]:
                    continue
                else:
                    return("Failure",(test['output'],programOutput[index]))
            return ("Success",(0,0))
        else:
            return ("Error",(0,programOutput[0]))

    @staticmethod
    def testASM64(submission,tests):
        compileASM64program = f"echo '{submission}' > submit.asm && " \
                            f"nasm -f elf64 -o submit.o submit.asm && " \
                            f"ld -o submit submit.o && " \
                            "chmod +x submit"

        testASM64program=[]
        for test in tests:
            # create the userin/shell script. Also communicate BREAK between outputs..
            testASM64program.append(f"echo -e '{ test['userInput'] }' > userin.doc && "
                                f"echo -e '#!/bin/sh\n\n./submit { test['cmdLineArgs'] }' > runscript.sh && "
                                f"chmod +x runscript.sh && "
                                f"./runscript.sh < userin.doc"
                                )

        testASM64program= " && echo 'BREAK' && ".join(testASM64program)
        finalCommand=compileASM64program+" && "+testASM64program

        print(finalCommand)

        newContainer = heliosSubmission.dockerClient.containers.run("emilienmottet/nasm",
                                                        ["/bin/bash", "-c", finalCommand],
                                                        detach=True,
                                                        ports={"5000/tcp": "5000"}
                                                        )
        # sleep to allow compilation before container removal
        sleep(3)
        # split output on BREAK to get distinct lines
        programOutput = newContainer.logs().decode('utf-8').split('BREAK\n')
        # clean up
        newContainer.stop()
        newContainer.remove()

        # for each test, compare test expected output with actual output
        if len(programOutput)==len(programOutput):
            for index,test in enumerate(tests):
                if test['output']==programOutput[index]:
                    continue
                else:
                    return("Failure",(test['output'],programOutput[index]))
            return ("Success",(0,0))
        else:
            return ("Error",(0,programOutput[0]))

    @staticmethod
    def testASM32(submission, tests):
        pass