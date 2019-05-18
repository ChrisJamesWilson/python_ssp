
import numpy as np
import matplotlib.pyplot as plt
import scipy.interpolate as interp
import os
from astropy.io import fits
import retrieve_irtf as ret
import stpars
from astropy.io import ascii
#from mpl_toolkits.mplot3d import Axes3D



# t is a table of the stars in the irtf library. The coloumns are: ID,   Teff(K),   logg,   Z/Zsun

def interpall(n_ms, n_rg, feh, afe, age, Z):
	parsfile = stpars.set_stpars_filename(n_ms, n_rg, feh, afe, age)

	t = ascii.read(parsfile)

	nstars = len(t)

	for i in range(nstars):
		interpolate(t[i][0],t[i][1],Z)

def interpolate(Teff_new, logg_new, Z_new):

	t = ret.param_retrieve()

	Teff = np.array(t[1])
	logg = np.array(t[2])
	g = 10**logg
	Z = np.array(t[3])

	ID = t[0]
	t = np.stack((Teff,logg,Z), axis=1)

	file_spectra = ret.set_spectra_name(Teff_new, logg_new, Z_new)

	exists = os.path.exists('./Stellar_Spectra/' + file_spectra)

	if exists is False:

		range_Teff = max(Teff)-min(Teff)
		#Teff_new = input('Please enter a Teff between ' + str(max(Teff)) + ' and ' + str(min(Teff)))
		#Teff_new = 3810
		range_logg = max(logg)-min(logg)
		#logg_new = input('Please enter a logg between ' + str(max(logg)) + ' and ' + str(min(logg)))
		#logg_new = 4.65
		range_Z = max(Z)-min(Z)
		#Z_new = input('Please enter a Z between ' + str(max(Z)) + ' and ' + str(min(Z)))
		#Z_new = 0.00
		g_new = 10**logg_new
		new_point = np.array([Teff_new, logg_new, Z_new])


		print('Calculating Spectra for:')
		print('Teff: ' + str(Teff_new))
		print('logg: ' + str(logg_new))
		print('Z: ' + str(Z_new))




		# Removed IRL152 for testing





		#plt.figure()

		#cm = plt.cm.get_cmap('PRGn')
		#plot = plt.scatter(Teff, logg, c=Z, cmap=cm)
		#plt.colorbar(plot)
		#plt.scatter(Teff_new,logg_new, c='r')
		#plt.xlabel('Teff')
		#plt.ylabel('logg')
		#plt.gca().invert_xaxis()
		#plt.gca().invert_yaxis()

		#plt.show()

		length = len(t[:,0])
		#one = np.ones((length,3))
		#t_big = np.dot(one, new_point, out=None)
		new_point_big = np.tile(new_point,(length,1))
		#Creates an array of a chosen point of length of orginal data, to directly
		#compare the two

		Tn = 1
		gn = 1
		Zn = 1

		Diff = new_point_big - t

		Diff[:,0] = Diff[:,0]**Tn
		Diff[:,1] = Diff[:,1]**gn
		Diff[:,2] = Diff[:,2]**Zn

		# nth power
		compare = np.array([Diff[:,0]/(max(Diff[:,0])-min(Diff[:,0])), Diff[:,1]/(max(Diff[:,1])-min(Diff[:,1])), Diff[:,2]/(max(Diff[:,2])-min(Diff[:,2]))])
		# Normalises values based on the parameters respective ranges

		#mean = np.sum(compare, axis=1)/3
		dist = np.sqrt(compare[0,:]**2 + compare[1,:]**2 + compare[2,:]**2)
		theta = np.arctan(compare[0,:]/compare[1,:]) # angle between the temperature and logg
		phi = np.arctan(compare[0,:]/compare[2,:]) # angle between the temperature and metallicity
		# Finds the relative normalised differences of any empirical star to the defined point
		diff_sort = np.sort(dist)

		radii = 0.1

		if diff_sort[0] == 0:
			stars = np.where(dist == 0)[0]
		else:
			stars = np.where(dist < radii)[0]

		###############################################################################################
		#### Improved angular code to be placed here, replacing the below "if len(stars)" segments ####
		###############################################################################################
		
		if len(stars) > 3:
			print(str(radii))
			radii = diff_sort[2] + 0.001
			if diff_sort[0] == 0:
				stars = np.where(dist == 0)[0]
			else:
				stars = np.where(dist < radii)[0]

		if len(stars) == 0 and radii < 0.7:
			print('No stars within the selected radius: ' + str(radii))
			radii = diff_sort[0] + 0.001
			if diff_sort[0] == 0:
				stars = np.where(dist == 0)[0]
			else:
				stars = np.where(dist < radii)[0]

	
		if len(stars) == 1 and diff_sort[0] != 0:
			print('Selecting star from other side of object for interpolation')
		
			angsep = np.pi/2

			newstars = dist[(abs(theta[stars]-theta) > angsep) & (abs(phi[stars]-phi) > angsep)]
			#newstars2 = dist[np.where(abs(phi[stars]-phi) > np.pi/2)[0]]

			#newstars = np.concatenate([newstars,newstars2])

			newdistsort = np.sort(newstars)

			if len(newdistsort) > 0:
				if newdistsort[0] < 5*dist[stars]:
					stars = np.concatenate([stars,np.where(dist == newdistsort[0])[0]])
				else:
					print('No suitable additional star in range')
			else:
				print('No suitable additional star in range')
		
#		if len(stars) == 2:
#			angsep = abs(theta[stars[0]]-theta[stars[1]])
#			if angsep < 3*np.pi/4:
#				angsep = (2*np.pi-angsep)/4
#				print('2 close stars selected, finding another star for interpolation')
#				newstars = dist[(abs(theta[stars[0]]-theta) >


		print('Stars selected = ' + str(len(stars)))

		if radii >= 0.5:
			print('Insufficient stars within local parameter space to create a sufficient spectra')
		else:
			#close = 5

			#star = np.zeros(close)

			#for i in range(close):
				#star[i] = int(np.where(mean == diff_sort[i])[0][0])

			# Square and squareroot would probably be a better idea here

			#########
			# Method 1 #
			#########

			# Method 1 is such that ALL stars are considered for a single point.
			# We do so by again normalising the relative differences (mean) to now be
			# relative to each other, and using that as a basis for interpolation

			n = 1
			# pol = (n-1)**3
			pol = 1

			#print('n = ' + str(n))
			#print('pol = ' + str(pol))

			if diff_sort[0] == 0:
				rel_weight = np.zeros(len(dist))
				rel_weight[stars] = 1/len(stars)
			else:
				rel_weight = (1/dist**pol)
				rel_weight = rel_weight/np.sum(rel_weight[stars])

			 # Now each of these stars are indexed according to their position in the original
			 # data, and this rel_mean value should be a multiplier of their spectral values,
			 # summative to the final star

			#########
			# Method 2 #
			#########
			 
			# # Method 2 is similar to 1, but instead picks a few of the closest values.
			#
			#ind = np.argsort(mean)
			#closest = np.array([np.where(ind==0)[1], np.where(ind==1)[1], np.where(ind==2)[1]])
			# # Location of the 3 closest 
			#stars = np.array([t[closest[0][0]], t[closest[1][0]], t[closest[2][0]]])
			#
			#rel_weight = np.array([compare[0][2][closest[0][0]], compare[0][2][closest[1][0]],\
			#             compare[0][2][closest[2][0]]])
			#             
			#rel_weight = rel_weight/sum(rel_weight)
			#
			# # Has normalised the weighting of these 3 stars vs the chosen point. These 
			# # weights must then be multiplies with the corresponding stars
			#spec_ID = np.array([ID[closest[0][0]], ID[closest[1][0]], ID[closest[2][0]]])


			##########################
			 # Dealing with the files
			##########################

			int_spectra = np.zeros(15000)

			for i in stars:
				int_spectra = int_spectra + ret.get_spectra(ID[int(i)])[:,1]*rel_weight[int(i)]

				# Sets up a length x (i+1) array of the spectras, where the first column
				# is the x axis and the other columns are the chosen stars in order of
				# closest to farthest 
				# Also multiplies the spectra by their relative weights to the chosen point


			#for i in range(3):
			#	plt.figure()
			#	plt.plot(chosen_spectra[:,0],chosen_spectra[:,i+1]/rel_weight[i])


			#int_spectra = np.array([chosen_spectra[:,0], chosen_spectra[:,1:].sum(axis=1)]).T

			#t_1 = ret.get_spectra(ID[int(stars[0])])
			#t_2 = ret.get_spectra(ID[int(stars[1])])
			#t_3 = ret.get_spectra(ID[int(stars[2])])
			t_rl = ret.get_spectra('IRL001')

			#t2 = np.loadtxt('sometxt.txt')

			#t2[:,1][abs(t2[:,1])>9e2] = 0

			#x = np.linspace(0,len(t2),len(t_1))

			#fp = t2[:,0]

			#xp = np.linspace(0,len(t2),len(t2))

			#gp = np.interp(x,xp,fp)

			#gp = np.arange(0,len(t_1))


			ttt = np.zeros((len(t_rl),2))
			ttt[:,0] = t_rl[:,0]
			ttt[:,1] = int_spectra

			np.savetxt('./Stellar_Spectra/' + file_spectra, ttt)

			plt.figure()

			ax = plt.subplot(111)
			ax.plot(t_rl[:,0], int_spectra,'b', label = 'Interpolated Spectra', linewidth = 0.5)
			#plt.title('Comparison of Means-Interpolated vs Empirical Spectra for: ' + 
			#	  '$Teff =$ ' + str(Teff_new) + ', $log g =$ ' + str(logg_new) + ', $Z =$ ' + str(Z_new))
			plt.xlabel('Wavelength ($\AA$)')
			plt.ylabel('Flux')

			plt.savefig('./Stellar_Spectra/' + file_spectra + '.png')
			plt.close()

			print('Succesfully created a star with the chosen paramaters located in: ./Stellar_Spectra/' + file_spectra + '.txt')
			print('-------------------------------------------------------------------------------')

			#plt.show()

			#plt.figure()
			#plt.plot(gp,diffs)
			#plt.show()
	else:

		print('Spectra located at: ' + file_spectra)

#####################
## Appendixed code ##
#####################

#		radii = 1
#        sample = 3
#
#		if diff_sort[0] == 0:
#			stars = np.where(dist == 0)[0]
#		else:
#			stars = np.where(dist < radii)[0]
#            
#		if len(stars) == 0 and radii < 0.7:
#			print('No stars within the selected radius: ' + str(radii))
#			radii = diff_sort[0] + 0.001
#			if diff_sort[0] == 0:
#				stars = np.where(dist == 0)[0]
#			else:
#				stars = np.where(dist < radii)[0]
#  
#		angsep = np.pi/2
#
#        	nstars = 5
#        	ang_diff = np.ones((nstars,nstars,2))
#		  # Set up so that rather than repeat a star consideration, if the code 
#		  # is looking at star combinations that have already been considered they will be ignored
#		  # as the multiplied of 10 ensures the angle is way too large to be accepted.
#		    ## This *10 functionality has been changed
#		  # Also maintains the index of stars across the data cube
#		repeat = 1
#		while repeat = 1 & nstars > 1:
#		        
#			for i in range(nstars):
#				theta_big = np.tile(thetasort[i],(range(nstars), 1))
#				phi_big = np.tile(phisort[i],(range(nstars), 1))
#				ang_diff[i,:,0] = theta_big - thetasort[:nstars]
#				ang_diff[i,:,1] = phi_big - phisort[:nstars]
#				# Creates a datacube of angular differences for all combinations of stars in the set
#				# Each layer is a 2xN of thetas and phi differences, with consecutive layers being the 
#				# next sequential star being compared with all others
#				#        size = len(ang_diff[0,0,:])
#
#			for i in range(len(ang_diff[0, :, 0])):
#			# for j in range(len(ang_diff[0,0,:])):
#				ang_diff[:, i, 0] = np.roll(ang_diff[:, i, 0], i)
#				ang_diff[:, i, 1] = np.roll(ang_diff[:, i, 1], i)
#			# Rotates cube such that each layer is now the differences of sequencial stars, rather than diagonal
#
#			ang_diff = ang_diff[1:, :, :]
#			# Slices out the first face, which after rotating should be a face of
#			# zeros (angular difference between a star vs itself)
#			ang_diff = ang_diff[:(math.trunc(len(ang_diff[:,0,0])/2)), :, :]
#			# Takes the first half (rounded down to nearest integer if initially odd)
#			# to ignore repeated calculations
#			temp = ang_diff
#			#            iterations = (len((ang_diff[:,0,0]))**2)*len(ang_diff[0,:,0])
#
#			#            sums = np.ones(len(ang_diff[:, 0, 0]), len(ang_diff[0, :, 0]), 2))
#			min_comb = 100
#			for k in range(len(ang_diff[:, 0, 0])): # x in this plane
#				for j in range(len(ang_diff[0, :, 0])): # y in this plane
#					sums = abs(np.sum(np.sum(temp, axis = 1), axis = 1))
#					# Truncates dimensions to use a sum of both phi and theta
#					sums = abs(4*pi - sums)
#					if min(sums) < min_comb:
#						min_comb = min(sums)
#            					  # Calculates the minimum
##						index = (np.where(sums == min_comb))[0]
#            			if abs(4*pi - min_comb)/(4*pi) < 0.2  :
#            				repeat = 0
##            				chosen = temp[index,:,:]
##            				jj = j
##            				kk = k
#
#            				print('Optimal combination found') #, angles sum to ' + str(4*pi-min_comb))
#                
#            			else :
#                                temp = ang_diff
#                                temp[:, j+1, 0] = np.roll(temp[:, j+1, 0], k+1)
#                                temp[:, j+1, 1] = np.roll(tmep[:, j+1, 1], k+1)
#                                # Rotates each section by amount k
#                                # Can be done prior to j loop, but need to be careful and 
#                                # change where minimum is calculated
#                                nstars = nstars - 1
#                                print('No suitable combination found, reduce number of stars to ' + str(nstars))
#                                
#           # So here's the deal. As it stands, this code is a very long-winded way of saying 
#           # "If N stars does not work, try N-2, then N-2, etc.. Except it is missing the key
#           # feature. Right now, it looks at a set of N closest stars, which does not allow for optimisation.
#           # Instead, we would like for it to try N stars out of a larger set. If this is not optimal,
#           # test out N-1 stars from this same set, and so on, until an optimal combination is found.
#           # In essence, if we have 10 stars this code, right now, looks at all closest 10, if it is not optimal,
#           # it then looks at the closest 9, repeats. 
#           # What we would like it to do is look at all 10 and if it is not optimal look at every combination
#           # of 9 out of those 10, then 8 out of 10, then 7, etc.
#           # While this is possible, the methods we can conjure in the little time we have are god-awful,
#           # with an extremely high computational complexity that simply is not worthwhile.
#           # The possible functionality remains, but must be extended. Future users may wish to try
#           # continuing this to find the optimal set, but it is highly recommended that you first 
#           # vectorise the functions. The greatest difficulty is working out what set you have used without
#           # trying to save all of the information to written files or memory. We started implementing 
#           # a method to find the index of the final value and work backwards (allowing us to not save information),
#           # before realising we were missing looking at ALL combinations.




