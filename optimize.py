from collections import defaultdict
import numpy as np

from dwave.system.samplers import DWaveSampler
from dwave.system.composites import EmbeddingComposite


# compat_matrix is an N x N matrix where the ij entry indicates the "compatibility" score for male i and female j
# Each entry should be between 0 and 1
def bipartite_optimize(compat_matrix, pairing_cost, double_pairing_cost, numruns):
    Q = defaultdict(float)
    N = compat_matrix.shape[0]
        
    # Initialize linear weights
    for i in range(N):
        for j in range(N):
            Q[((i,j), (i,j))] = pairing_cost - compat_matrix[i, j]
    
    # Initialize quadratic weights          
    for i in range(N):
        for j in range(N):
            if i != j:
                for k in range(N):
                    Q[((i,k), (j,k))] = double_pairing_cost
                    Q[((k,i), (k,j))] = double_pairing_cost

    # Execute problem
    sampler = EmbeddingComposite(DWaveSampler())
    response = sampler.sample_qubo(Q, num_reads=numruns)
    return response

def bipartite_optimize_iterated(compat_matrix):
    numruns = 100 # Number of samples taken 
    pairing_cost = -0.1 # "cost" assigned for each pairing (should be negative)
    double_pairing_cost = 1 # "cost" assigned for each person who is paired with two people (should be positive)

    # Run sampler
    N = compat_matrix.shape[0]
    result = bipartite_optimize(compat_matrix, pairing_cost, double_pairing_cost, numruns)
    print(result)
        
    # Get Best Result
    best_dict = result.first.sample
    best_list = [key for key in best_dict if best_dict[key]]
    
    # Test Validity
    no_overlaps = all_unique([x[0] for x in best_list]) and all_unique([x[1] for x in best_list]) 
    sufficient_pairs = len(best_list) >= N
    print("No Overlap: " + str(no_overlaps))
    print("Sufficient Pairs: " + str(sufficient_pairs))
    return best_list    
    
def get_qubit_name(i, j):
    return str(i) + "." + str(j)
def all_unique(x):
    return len(x) == len(set(x))

# compat_matrix is an 2N x 2N symmetric matrix where the ij entry indicates the "compatibility" score for person i and person j, Each entry need not be between 0 and 1
def general_optimize(compat_matrix, mps_matrix, pairing_cost, double_pairing_cost, numruns):
    Q = defaultdict(float)
    N = int(compat_matrix.shape[0] / 2) 
        
    # Initialize linear weights
    for i in range(2 * N):
        for j in range(i):
            if (mps_matrix[i, j]):
                Q[((i,j), (i,j))] = pairing_cost - compat_matrix[i, j]
    
    # Initialize quadratic weights          
    for i in range(2 * N):
        for j in range(i):
            for k in range(j):
                if mps_matrix[i,j] and mps_matrix[j,k]:
                    Q[((i,j), (j,k))] = double_pairing_cost
                if mps_matrix[i,k] and mps_matrix[j,k]:
                    Q[((i,k), (j,k))] = double_pairing_cost
                if mps_matrix[i,j] and mps_matrix[i,k]:
                    Q[((i,j), (i,k))] = double_pairing_cost

    # Execute problem
    sampler = EmbeddingComposite(DWaveSampler())
    response = sampler.sample_qubo(Q, num_reads=numruns)
    return response

def general_optimize_iterated(compat_matrix, mps_matrix):
    numruns = 1000 # Number of samples taken    
    pairing_cost = -0.1 # "cost" assigned for each pairing (should be negative)
    double_pairing_cost = 1 # "cost" assigned for each person who is paired with two people (should be positive)

    # Run sampler
    N = compat_matrix.shape[0] / 2
    result = general_optimize(compat_matrix, mps_matrix, pairing_cost, double_pairing_cost, numruns)
    print(result)
        
    # Get Best Result
    best_dict = result.first.sample
    best_list = [key for key in best_dict if best_dict[key]]
    
    # Test Validity
    no_overlaps = all_unique([x[0] for x in best_list] + [x[1] for x in best_list]) 
    sufficient_pairs = len(best_list) >= N
    mps_satisfied = all(mps_matrix[x[0], x[1]] == 1 for x in best_list)
    print("No Overlap: " + str(no_overlaps))
    print("Sufficient Pairs: " + str(sufficient_pairs))
    print("MPS Satisfied: " + str(mps_satisfied))
    return best_list    
#compat = np.array([[.2, .1], [0, .3]])
#compat = np.random.rand(4, 4)
#print(compat)
#best = bipartite_optimize_iterated(compat)
#print(best)
#best = bipartite_optimize_iterated(compat)
#print(best)
if __name__ == '__main__':
    compat = np.random.rand(8, 8)
    compat = (compat + compat.T) / 2

    genders = [1, 1, 1, 1, 2, 2, 2, 2]
    orientations = [2, 3, 3, 1, 1, 3, 3, 2]
    mps = np.zeros([8, 8])
    for i in range(8):
        for j in range(8):
            mps[i, j] = (genders[i] & orientations[j] > 0) and (genders[j] & orientations[i] > 0) and i != j

    best = general_optimize_iterated(compat, mps)
    print(best)

    best = general_optimize_iterated(compat, mps)
    print(best)
    best = general_optimize_iterated(compat, mps)
    print(best)
