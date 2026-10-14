import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
path, start_pat, size = sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 5000
t = open(path, encoding='utf-8', errors='replace').read()
i = t.find(start_pat)
print(f'--- found at {i} ---')
print(t[i:i+size] if i >= 0 else 'NOT FOUND')
