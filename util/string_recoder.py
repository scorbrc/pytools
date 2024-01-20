from collections import defaultdict
from random import randint, Random


def string_recoder(data, delims=',-:.()" ', seed=randint(1, 2**32)):

    records = []
    for line in data:
        line = line.strip()
        rec = []
        while len(line):
            for delim in delims:
                if delim in line:
                    fval, _, line = line.partition(delim)
                    if len(fval.strip()):
                        rec.append((fval, delim))
                elif len(line):
                    rec.append((line, ''))
                    line = ''
        records.append(rec)

    fields = []
    fld_ct = max([len(rec) for rec in records])
    for i in range(fld_ct):
        lens = defaultdict(int)
        chars = set()
        for rec in records:
            if i < len(rec):
                lens[len(rec[i][0])]
                for c in rec[i][0]:
                    chars.add(c)

        fields.append(dict(
            i=i,
            min=min(lens.keys()),
            max=max(lens.keys()),
            mode=sorted(
                lens.items(),
                key=lambda nc: nc[1],
                reverse=True)[0][0],
            chars=list(chars)
        ))

    rnd = Random(seed)
    re_data = []
    for rec in records:
        values = []
        for i, (fval, delim) in enumerate(rec):
            fld = fields[i]
            ct = int(rnd.triangular(fld['min'], fld['max'], fld['mode']) + .5)
            nv = ''.join(rnd.choices(fld['chars'], k=ct))
            values.append(nv)
            values.append(delim)
        re_data.append(''.join(values))

    return re_data


if __name__ == '__main__':

    import csv

    data = (
        '855-896-343',
        '703-095-907',
        '576-327-888',
        '619-773-882',
        '322-584-144',
        '714-353-407',
        '059-962-861',
        '673-292-827',
        '307-292-752',
        '205-778-471',
        '114-449-947',
        '684-436-614',
        '216-197-152',
        '693-673-391',
        '532-481-995',
        '728-905-040',
        '021-350-664',
        '264-362-007',
        '099-542-890',
        '297-979-245'
    )

    for x in string_recoder(data, '-'):
        print(x)

    records = []
    fld_ct = 0
    with open('/Users/scobrc/sdg/data/titanic.csv') as fi:
        for rec in csv.DictReader(fi):
            fld_ct = max(fld_ct, len(rec))
            records.append(rec)
    for i in range(fld_ct):
        data = []
        for rec in records:
            if i < len(rec):
                k = list(rec.keys())[i]
                data.append(rec[k])
        if k in ('PassengerId', 'Name'):
            print()
            print(k)
            re_data = string_recoder(data)
            for j in range(20):
                print("%s | %s" % (data[j], re_data[j]))
