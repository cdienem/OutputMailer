#!/bin/python

# Script sending an email for all finished jobs
# Is called by jobs.py.wrapper which loads the correct environment befor executing

import os
import subprocess
import re
import time




def run_command(command):
	p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
	return iter(p.stdout.readline, b'')

def getOutput(directory, ident_out, ident_err):
	ret = {"0": []}
	for f in os.listdir(directory):
		if f[0] != ".":
			pat_out = str(ident_out)+"\.(\d{7})$"
			pat_err = str(ident_err)+"\.(\d{7})$"
			match_out = re.search(pat_out, f)
			match_err = re.search(pat_err, f)
			if match_out != None:
				if str(match_out.group(1)) not in ret:
					ret[str(match_out.group(1))] = {}
				ret[str(match_out.group(1))]["out"] = f
			if match_err != None:
				if str(match_err.group(1)) not in ret:
					ret[str(match_err.group(1))] = {}
				ret[str(match_err.group(1))]["err"] = f
				pass
	return ret

def getLastJobs():
	with open("/usr/users/USER/cron_scripts/jobs.tmp","r") as f:
		jobs = f.read().replace("\n","").split(",")
		f.close()
		return jobs

def checkJobs(watchdir, email, id_o, id_e):
	
	
	processes = []
	command = "bjobs"
	# extract job ids
		
	for line in run_command(command):
		
		pat = "^(\d{7})\s\w{7}\sRUN"
		match = re.search(pat,line)
		if match != None:
			processes.append(match.group(1))

	if not os.path.isfile("/usr/users/USER/cron_scripts/jobs.tmp"):
		with open("/usr/users/USER/cron_scripts/jobs.tmp","w+") as f:
			f.write(",".join(processes))
			f.close()
 
	processes_new = []
	running = getLastJobs()
	# ckeck wether they are in running
	for pid in running:
		if pid not in processes:
			# process ended
			out_files = getOutput(watchdir, id_o, id_e)
			if str(pid) in out_files:
				# do email them here
				cmd = "cat "+watchdir+"/"+out_files[pid]["out"]+" "+watchdir+"/"+out_files[pid]["err"]+" | sed '/\015/d' | mailx -s 'Output from "+pid+"' "+email
				subprocess.call(cmd, shell=True)
		else:
			# add still running jobs to list
			processes_new.append(pid)
	
	# add the newly started jobs here
	for pid in processes:
		if pid not in processes_new:
			processes_new.append(pid)
	# write the new processes to jobs.tmp
	with open("/usr/users/USER/cron_scripts/jobs.tmp","w+") as f:
		f.write(",".join(processes_new))

checkJobs("/usr/users/USER/nfsscratch3/FOLDER", "USER@EMAIL.de", "output", "error")
