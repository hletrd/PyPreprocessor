import sqlite3

dbc = sqlite3.connect('star.db', check_same_thread=False)
dbc.text_factory = str
c = dbc.cursor()

try:
	c.execute('CREATE TABLE star(`id` INT AUTO_INCREMENT, name TEXT, RA REAL, DEC REAL, const TEXT, mag REAL, cname TEXT, PRIMARY KEY (`id`))')
except:
	pass
dbc.commit()

cnt = 0

def parseint(string):
	return ''.join([x for x in string if x.isdigit()])

with open('stars.txt', 'r') as f:
	lst = f.read()
	lst = lst.replace('\n', '')
	lst = lst.replace('\r', '')
	lst = lst.split('</tr>')

	total = len(lst)
	now = 0
	for obj in lst:
		fields = obj.split('</td><td>')
		ra = float(fields[4])/360.*24
		dec = fields[5]
		const = fields[1]
		mag = fields[6]
		name = fields[2]
		cname = fields[3]
		c.execute("INSERT INTO star VALUES(?, ?, ?, ?, ?, ?, ?)", (cnt, name, ra, dec, const, mag, cname))
		dbc.commit()
		cnt += 1
		print(str(now) + ' / ' + str(total))
		now += 1