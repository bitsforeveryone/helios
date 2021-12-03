# Turtles All The Way Down 
- Category : Forensics
- Points : 100
- Flag: `ACI{47133f6a2c3f90f653381681705}`

## Challenge
Early this morning, a breach occurred on the server hosting our next-gen drone development repository. It is your job to figure out what was taken: challenge.zip

## First Steps
The challenge starts with a compressed file that, when extracted, provides a PCAP file.

The file format led to the idea of using Wireshark for analysis.

## The Right Path
The first step was reading the IRC messages that the analysts sent in the PCAP, which specified another log PCAP file that was compressed and given the password 'dronehack2019.'

Reading the HTTP packets, there was also mention of the attacker obtaining a file from file.io at an invalid link. 

## Solve

The next step was to use Wireshark's export function to recreate the filestreams and export the HTTP object 'jlngsr' from host file.io. Using the hints and the file signature, it was evident that this file was another compressed file. Upon trying to extract it, it asked for a password, and the aforementioned 'dronehack' successfully allowed the extraction of another PCAP file.

Opening this new PCAP file with Wireshark, there are FTP packets given, which were referenced in the hints. Parsing through these packets, we see the attacker looking through various directories before finding the flag.zip and flag.txt files. 

We are able to look at the hexdump of the packet where the attacker accessed this file, and inside it reads the flag: ACI{47133f6a2c3f90f653381681705}

## Thoughts

This challenge was interesting, as I got the opportunity to learn how to use a new tool: Wireshark, along with combining a few different methods, such as analyzing file signatures and PCAP analysis to solve a problem. Throughout the course of this problem, I learned about TCP, FTP, IRC, and HTTP. I also learned how to use Wireshark to recreate packets, read messages, and obtain files. 
