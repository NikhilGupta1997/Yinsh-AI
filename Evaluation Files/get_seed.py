import math

group = {}
seed = {}
count = 1
val = 1

def branch(seed, level, limit):
	global count
	global val
	global adder
	levelSum = 2**level + 1;
	if limit <= level + 1:
		group[seed] = int(count)
		group[levelSum - seed] = int(count)
		if val % adder == 0:
			val = 0
			count += 1
		val += 1
		return
	elif seed % 2 == 1:
		branch(seed, level + 1, limit)
		branch(levelSum - seed, level + 1, limit)
	else:
		branch(levelSum - seed, level + 1, limit)
		branch(seed, level + 1, limit)

with open('rank.txt', 'r') as fin:
	for i, line in enumerate(fin.readlines()):
		line = str(line.strip())
		seed[line] = i+1

teams = len(seed)
limit = int(math.log(teams, 2));
if 2**limit != teams:
	limit += 2
else:
	limit += 1
adder = int(2**(limit-6))
branch(1, 1, limit)

with open('seeds.txt', 'w') as fout:
	for bot in seed.keys():
		fout.write(bot + ' ' + str(group[seed[bot]]) + '\n')
		print(bot + ' ' + str(group[seed[bot]]))

