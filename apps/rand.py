import random
import numpy as np

member=['aaa','bbb','ccc','ddd','eee']
pay=np.array([0,0,0,0,0])
for i in range(51):
    menuman=random.choice(range(len(member)))
    randnum=pay//300
    randnum=randnum-min(randnum)
    if sum(randnum)<1:
        randnum=randnum+1
    randnum[menuman]=randnum[menuman]//2
    randlist = [i for i in range(len(member)) for j in range(randnum[i])]
    res=random.choice(randlist)
    print(pay)
    # print(member[menuman])
    print(member[res])

    pay=pay+300
    pay[res]=pay[res]-300*len(member)