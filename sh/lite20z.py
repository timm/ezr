import sys, pandas as pd, matplotlib.pyplot as plt

df = pd.read_csv(sys.stdin, sep=r'\s+')
df.insert(0, 'idx', range(1, len(df)+1))  # number rows 1..N

for col in df.columns[1:]:  # skip 'idx'
    plt.plot(df['idx'], df[col], label=col)

plt.xlabel('Data set #')
plt.legend()
plt.grid()
plt.tight_layout()
plt.savefig('plot.png', dpi=150)
