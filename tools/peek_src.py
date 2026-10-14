import io, sys

path, kw = sys.argv[1], sys.argv[2]
before = int(sys.argv[3]) if len(sys.argv) > 3 else 1500
after = int(sys.argv[4]) if len(sys.argv) > 4 else 400
src = io.open(path, encoding='utf-8').read()
i = src.find(kw)
if i < 0:
    print('NOT FOUND')
else:
    print(src[max(0, i - before):i + after])
