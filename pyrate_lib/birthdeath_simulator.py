#!/usr/bin/env python 
# Created by Daniele Silvestro on 20/01/2017 => daniele.silvestro@bioenv.gu.se
from numpy import *
import numpy as np
import random as rand
import sys, os
from scipy.special import gdtr, gdtrix
print "Birth-Death Sampler 18\n"


##########################################################################
###########                 SIMULATION SETTINGS                 ##########
##########################################################################

n_reps = 10 # number of simulations

# CONSTRAINTS on DATA SIZE
s_species=4   # number of starting species
minSP=200     # min size data set
maxSP=300     # max size data set
minEX_SP=0    # minimum number of extinct lineages allowed

# SETTINGS for BD-SHIFT SIMULATIONS
root_age = 30
shift_speciation = [20]      # specify times of rate shifts (speciation)
shift_extinction = [5]       # specify times of rate shifts (extinction)
speciation_rates = [0.4,0.2] # if using rate shifts, the first rate is that closest to the root age
extinction_rates = [0.1,0.3] # 

# SETTINGS for RANDOM SIMUATIONS
randomSettings=0 # set to 1 to use random settings (see below)
poiL = 1 # expected number of shifts (if 0: constant rate BD; if -1 use empirical Prob vec)
poiM = 1 # expected number of shifts (if 0: constant rate BD; if -1 use empirical Prob vec)
root_r=np.array([30.,30.]) # range root ages
minL,maxL = 0.4 , 0.4
minM,maxM = 0.3 , 0.3
useDD = 0 # set to 1 to use model diversity dependence
# example empirical Prob vectors
p_vec_l = np.array([0.569,0.254,0.136,0.040])
p_vec_m = np.array([0.440,0.343,0.189,0.029])

scale=100.


#################### SIMULATION  FUNCTIONS #########################################

def trans_rate_linear(l0,gl,D):
	#print l0,D,max(0.0001, l0+l0*(gl/270. * (D-s_species)))
	return max(0.0000001, l0+l0*(gl * D))

def get_DT(T,s,e): # returns the Diversity Trajectory of s,e at times T (x10 faster)
	B=np.sort(np.append(T,T[0]+1))+.0001
	ss1 = np.histogram(s,bins=B)[0]
	ee2 = np.histogram(e,bins=B)[0]
	DD=(ss1-ee2)[::-1]
	#return np.insert(np.cumsum(DD),0,0)[0:len(T)]
	return np.cumsum(DD)[0:len(T)] 

def simulate(L,M,timesL, timesM,root,scale,s_species, maxSP,gl=0,gm=0,Dtraj=[0],Tcomp_clade=[0]):
	ts=list()
	te=list()
	l_t=L[0]
	m_t=M[0]
	
	L,M,root=L/scale,M/scale,int(root*scale)

	for i  in range(s_species): 
		ts.append(root)
		te.append(0)
	
	
	for t in range(root,0): # time
		if gl==0 and gm==0:
			for j in range(len(timesL)-1):
				if -t/scale<=timesL[j] and -t/scale>timesL[j+1]: l=L[j]
			for j in range(len(timesM)-1):
				if -t/scale<=timesM[j] and -t/scale>timesM[j+1]: m=M[j]

		elif max(Dtraj)>0:
			try: D=Dtraj[Tcomp_clade== -int(t/scale)][0]
			except(IndexError): D=0 # if curves do not overlap, no competition
			te_temp = np.array(te)
			D_l=len(te_temp[te_temp==0])
			l = trans_rate_linear(l_t,gl,D)
			#l = trans_rate_linear(l,-0.05,D_l)
			m = trans_rate_linear(m_t,gm,D)
			l,m = l/scale, m/scale
			#if t%100==0: print t*scale, D, l*scale, m*scale,gl,gm
		else:
			te_temp = np.array(te)
			D=len(te_temp[te_temp==0])
			l = trans_rate_linear(l_t,gl,D)
			m = trans_rate_linear(m_t,gm,D)
			#if t%100==0: print l_t,l,m,D,gl
			l,m = l/scale, m/scale			
			
		#if t % 100 ==0: print t/scale, -times[j], -times[j+1], l, m
		TE=len(te)
		if TE>maxSP: 
			break
		for j in range(TE): # extant lineages
			if te[j]==0:
				ran=random.random()
				if ran<l: 
					te.append(0) # add species
					ts.append(t) # sp time
				elif ran>l and ran < (l+m): # extinction
					te[j]=t
	te=array(te)
	return -array(ts)/scale, -(te)/scale

############### SIMULATION SETTINGS ########################################
def write_to_file(f, o):
	sumfile = open(f , "wb") 
	sumfile.writelines(o)
	sumfile.close()

def get_random_settings(root,poiL,poiM):
	root=abs(root)
	timesL_temp= [ root,0.]
	timesM_temp= [ root,0.]
	
	if poiL==-1: nL = random_choice_P(p_vec_l)[1]
	elif poiL==0: nL = 0 
	else: nL = np.random.poisson(poiL)
	
	if poiM==-1: nM = random_choice_P(p_vec_m)[1]
	elif poiM==0: nM = 0 
	else: nM = np.random.poisson(poiM)

	shift_time_L= np.random.uniform(0,root,nL)
	shift_time_M= np.random.uniform(0,root,nM)
	
	timesL=sort(np.concatenate((timesL_temp,shift_time_L),axis=0))[::-1]
	timesM=sort(np.concatenate((timesM_temp,shift_time_M),axis=0))[::-1]
	
	L=np.random.uniform(minL,maxL,nL+1)
	M=np.random.uniform(minM,maxM,nM+1)
	#M[0] = np.random.uniform(0,.1*L[0])
	
	return timesL,timesM, L,M



# select random element based on fixed probabilities
def random_choice_P(vector):
	probDeath=np.cumsum(vector/sum(vector)) # cumulative prob (used to randomly sample one 
	r=rand.random()                          # parameter based on its deathRate)
	probDeath=sort(append(probDeath, r))
	ind=np.where(probDeath==r)[0][0] # just in case r==1
	return [vector[ind], ind]



for sim in range(n_reps):
	i=0
	LOtrue,i=[0],0
	n_extinct=-0
	while len(LOtrue) < minSP or len(LOtrue) > maxSP or n_extinct < minEX_SP: 
		#print len(LOtrue),n_extinct
		if i > 100: 
			i = 0
			clade = 0
		if i % 10==0: # if it doesn't get the right range of species in 5 attempts, draw new rates (+shifts)
			if randomSettings==1:
				root = -random.uniform(min(root_r),max(root_r)) # ROOT AGES
				timesL,timesM,L,M = get_random_settings(root,poiL,poiM)
			else:
				timesL = np.sort(np.array([float(root_age),0.]+shift_speciation))[::-1]
				timesM = np.sort(np.array([float(root_age),0.]+shift_extinction))[::-1]
				L = np.array(speciation_rates)
				M = np.array(extinction_rates)
				root = -root_age	
			
			if useDD==1:
				timesL,timesM, L,M = get_random_settings(root,0,0)
				L=np.random.uniform(.75,1,1) #np.array([.25]) # .25,.5,1
				M= np.random.uniform(.05,.1,1) #np.array([.01])
				gl=np.random.uniform(-.05,-0.025,1)   # -0.15
				gm=np.random.uniform(.3,.5,1)   #0.3
				FAtrue,LOtrue=simulate(L,M,timesL,timesM,root,scale,s_species, maxSP,gl,gm)
			else:
				FAtrue,LOtrue=simulate(L,M,timesL,timesM,root,scale,s_species, maxSP)
		
		n_extinct = len(LOtrue[LOtrue>0])
	print "\nSim %s:" % (sim)
	print "L", L, "M",M, "tL",timesL,"tM",timesM
	ltt=""
	for i in range(int(max(FAtrue))):
		n=len(FAtrue[FAtrue>i])-len(LOtrue[LOtrue>i])
		#nlog=int((n))
		ltt += "\n%s\t%s\t%s" % (i, n, "*"*n)
	print ltt
	#print "simulation:",i, "total no.", len(LOtrue),root
	i += 1

	print len(LOtrue),len(L),len(M)
	o="clade	species	ts	te\n"
	for i in range(len(FAtrue)):
		o+= "%s\t%s\t%s\t%s\n" % (0,i+1,FAtrue[i],LOtrue[i])
	write_to_file("sim_%s" % (sim), o) 	

quit()