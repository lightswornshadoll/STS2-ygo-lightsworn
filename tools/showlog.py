# 临时：输出指定日志文件的行区间（python showlog.py <文件名> <起> <止>）
import io, os, sys
name, start, end = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
path = os.path.join(os.environ["APPDATA"], "SlayTheSpire2", "logs", name)
lines = io.open(path, encoding="utf-8", errors="replace").read().splitlines()
for i in range(start - 1, min(end, len(lines))):
    print(f"{i+1}: {lines[i]}")
