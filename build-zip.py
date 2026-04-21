import zipfile, os
from pathlib import Path

src = Path(r'C:\Users\david.hayes\Projects\fourth-firecrawl-plugin')
dst = src / 'fourth-firecrawl-v1.2.1.zip'

exclude_dirs = {'.git', '.firecrawl', '__pycache__', 'node_modules'}
exclude_files = {'.DS_Store', 'Thumbs.db', 'build-zip.py'}
exclude_ext = {'.zip'}

if dst.exists():
    dst.unlink()

count = 0
with zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED) as z:
    for root, dirs, files in os.walk(src):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for fname in files:
            if fname in exclude_files or Path(fname).suffix in exclude_ext:
                continue
            fp = Path(root) / fname
            arcname = fp.relative_to(src).as_posix()
            z.write(fp, arcname)
            count += 1

size_kb = dst.stat().st_size / 1024
print(f'Zip: {dst}')
print(f'Size: {size_kb:.2f} KB ({count} entries)')

with zipfile.ZipFile(dst, 'r') as z:
    bad = [n for n in z.namelist() if chr(92) in n]
    print(f'Entries with backslashes: {len(bad)} (should be 0)')
