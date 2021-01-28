from collections import defaultdict
import numpy as np

from dwave.system.samplers import DWaveSampler
from dwave.system.composites import EmbeddingComposite


# compat_matrix is an N x N matrix where the ith matrix indicates the "compatibility" score for male i and female j
# Each entry should be between 0 and 1
def bipartite_optimize(compat_matrix):
	numruns = 100 # Number of samples taken	
	pairing_cost = -1 # "cost" assigned for each pairing (should be negative)
	double_pairing_cost = 1 # "cost" assigned for each person who is paired with two people (should be positive)
	
	Q = defaultdict(float)
	N = compat_matrix.shape[0]
		
	# Initialize linear weights
	for i in range(N):
		for j in range(N):
			Q[((i,j), (i,j))] = pairing_cost - compat_matrix[i, j]
	print(Q)
	# Initialize quadratic weights			
	for i in range(N):
		for j in range(N):
			if i != j:
				for k in range(N):
					Q[((i,k), (j,k))] = double_pairing_cost
					Q[((k,i), (k,j))] = double_pairing_cost

	print(Q)
	# Execute problem
	sampler = EmbeddingComposite(DWaveSampler())
	response = sampler.sample_qubo(Q, num_reads=numruns)
	print(response)	

def get_qubit_name(i, j):
	return str(i) + "." + str(j)

compat = np.array([[.2, .1], [0, .3]])
bipartite_optimize(compat)
