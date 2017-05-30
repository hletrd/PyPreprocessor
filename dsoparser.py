import sqlite3

dbc = sqlite3.connect('dso.db', check_same_thread=False)
dbc.text_factory = str
c = dbc.cursor()

try:
	c.execute('CREATE TABLE DSO(`id` INT AUTO_INCREMENT, name TEXT, RA REAL, DEC REAL, type TEXT, const TEXT, mag REAL, catalogue TEXT, cid INT, PRIMARY KEY (`id`))')
except:
	pass
dbc.commit()

cnt = 0
dsos = ['NGC', 'IC', 'M', 'C']

def parseint(string):
	return ''.join([x for x in string if x.isdigit()])

with open('dso.csv', 'r') as f:
	lst = f.read()
	lst = lst.replace('\r\n', '\n')
	lst = lst.replace('\r', '\n')
	lst = lst.split('\n')

	total = len(lst)
	now = 0
	for obj in lst:
		fields = obj.split(',')
		ra = fields[0]
		dec = fields[1]
		typ = fields[2]
		const = fields[3]
		mag = fields[4]
		name = fields[5].replace('"', '')
		pid = fields[8]
		dsolist1 = (fields[14], fields[13])
		dsolist2 = (fields[16], fields[15])
		if dsolist1[0] in dsos and parseint(dsolist1[1]) == dsolist1[1]:
			c.execute("INSERT INTO DSO VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)", (cnt, name, ra, dec, typ, const, mag, dsolist1[0], dsolist1[1]))
			cnt += 1
			dbc.commit()
			print(dsolist1[0], dsolist1[1])
		if dsolist2[0] in dsos and parseint(dsolist2[1]) == dsolist2[1]:
			c.execute("INSERT INTO DSO VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)", (cnt, name, ra, dec, typ, const, mag, dsolist2[0], dsolist2[1]))
			cnt += 1
			dbc.commit()
			print(dsolist2[0], dsolist2[1])
		print(str(now) + ' / ' + str(total))
		now += 1