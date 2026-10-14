import re, io, sys, os
root = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'mod', 'lightsworn', 'Scripts')
files = sys.argv[1:] or ['Cards1.cs','Cards2.cs','Cards3.cs','Cards4.cs','Cards5.cs','Cards6.cs','Cards7.cs','Cards8.cs','ShaddollBase.cs','LsUtil.cs','Ls.cs','Powers.cs']
for f in files:
    p = os.path.join(root, f)
    if not os.path.isfile(p):
        print('MISSING', p); continue
    print('=====', f)
    for i, l in enumerate(io.open(p, encoding='utf-8'), 1):
        if re.match(r'\s*(public|internal|abstract|sealed|partial|protected).*class ', l):
            print(i, l.rstrip()[:120])
