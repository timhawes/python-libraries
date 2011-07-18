#!/usr/bin/python
# -*- python -*-
#
# Tim Hawes
# 21st January 2011

def tableformat(data):
    widths = []

    for row in data:
        for col_i in range(0, len(row)):
            cell_size = len(str(row[col_i]))
            if len(widths)-1 < col_i:
                widths = widths + [0]
            if widths[col_i] < cell_size:
                widths[col_i] = cell_size

    formatter = []
    for i in range(0, len(widths)):
        formatter.append("%%-%ss" % (widths[i]))
    formatter_string = ' '.join(formatter)

    for row in data:
        yield formatter_string % tuple(row)

if __name__ == '__main__':
    data = [
        ["Index", "Name", "Number"],
        [1, "Aaaaa", 123],
        [2, "Bbb", 2]
        ]

    for line in tableformat(data):
        print line
