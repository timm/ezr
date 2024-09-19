import sys,random
from ezr import the, DATA, csv, dot

# Function to randomly pick N rows and sort by chebyshev
def guess(N, data):
    some = random.choices(data.rows, k=N)
    return data.clone().adds(some).chebyshevs().rows

# Conduct experiments
def run_experiment():

    for N in (20, 30, 40, 50):
        d = DATA().adds(csv('data/optimize/config/SS-H.csv')) # Update file path here

        dumb = [guess(N, d) for _ in range(20)]
        smart = [d.shuffle().activeLearning() for _ in range(20)]
        dumb = [d.chebyshev(lst[0]) for lst in dumb]
        smart = [d.chebyshev(lst[0]) for lst in smart]
        the_Last = N
        
        # Aggregate results
        combined_results = dumb + smart
        # Output results for each setting
        for label, lst in zip(["dumb", "smart"], [dumb, smart]):
                with open(f'{label}_{N}.txt', 'w') as file:
                    for row in lst:
                        file.write(str(row) + '\n')

run_experiment()