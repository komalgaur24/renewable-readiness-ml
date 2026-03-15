with open('dashboard/app_v2.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines, 1):
    if ('f"' in line or "f'" in line) and ('\\n' in line or '\\t' in line or "\\'" in line or '\\"' in line):
        print(f'Line {i}: {line.rstrip()}')

print("Done checking!")