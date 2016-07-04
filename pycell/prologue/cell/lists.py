
lists = """
list1 = {:(a)             pair(a, None);};
list2 = {:(a, b)          pair(a, list1(b));};
list3 = {:(a, b, c)       pair(a, list2(b, c));};
list4 = {:(a, b, c, d)    pair(a, list3(b, c, d));};
list5 = {:(a, b, c, d, e) pair(a, list4(b, c, d, e));};

prepend = pair;

for = {:(xs, fn)
    fn(first(xs));
    tail = second(xs);
    if (equals(tail, None),
        {},
        {for(tail, fn);}
    );
};
"""