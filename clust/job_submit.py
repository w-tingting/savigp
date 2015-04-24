# -*- coding: utf-8 -*-
import sys
from popen2 import popen2
import time

#many = int(sys.argv[1])
many=1
for i in range(0, many):

    # Open a pipe to the qsub command.
    output, input = popen2('qsub')

    # Customize your options here
    job_name = "adezfouli2%s_%s_test" % (str(i).zfill(3), '')
    walltime = "4:00:00"
    #processors = "nodes=1:ppn=1:scalemp" #can put avx2 here as well to use new computers
    processors = "nodes=1:ppn=1" #Currently avx2 is not working
    command = "./run_job.sh %s" % (str(i))
    #command = "StartConda;python myfile.py %s" % (str(i))
    job_string = "\"#!/bin/bash \n \
    #PBS -N %s \n\
    #PBS -l vmem =16gb \n\
    #PBS -l walltime=%s \n\
    #PBS -l %s \n\
    #PBS -q short48 \n\
    #PBS -o /home/z3510738/code/output/%s.out \n\
    #PBS -e /home/z3510738/code/error/%s.err \n\
    #PBS -M a.dezfouli@unsw.edu.au@unsw.edu.au \n\
    cd $PBS_O_WORKDIR \n\
    chmod +x ./run_job.sh \n\
    %s\"" % (job_name, walltime, processors, job_name, job_name, command)
    #"\&".join([command_N"\n"]*N) amd change ppn to N
    # Send job_string to qsub
    input.write(job_string)
    input.close()

    # Print your job and the response to the screen
    print job_string
    print output.read()

    time.sleep(0.1)

