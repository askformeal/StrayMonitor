import os

lines = {}

def get_lines(path: str):
    with open(path, 'r', encoding='utf-8') as f:
        cnt = len(f.readlines())
    return cnt

lines['app.py'] = get_lines('./app.py')

for filename in os.listdir('./src'):
    path = os.path.join('./src', filename)
    if os.path.isfile(path):
        lines[filename] = get_lines(path)

print(sum(list(lines.values())))