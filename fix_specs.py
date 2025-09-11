import re

# Read the original file
with open('detalle-producto.html', 'r') as f:
    content = f.read()

# Fix specs_general
content = re.sub(
    r'(if \(apiProduct\.specs_general\) \{\s*specs\.general = typeof apiProduct\.specs_general === \'string\' \?\s*JSON\.parse\(apiProduct\.specs_general\) : apiProduct\.specs_general;\s*)(})',
    r'\1} else {\n                            specs.general = [];\n                        }',
    content,
    flags=re.MULTILINE | re.DOTALL
)

# Fix specs_engine
content = re.sub(
    r'(if \(apiProduct\.specs_engine\) \{\s*specs\.engine = typeof apiProduct\.specs_engine === \'string\' \?\s*JSON\.parse\(apiProduct\.specs_engine\) : apiProduct\.specs_engine;\s*)(})',
    r'\1} else {\n                            specs.engine = [];\n                        }',
    content,
    flags=re.MULTILINE | re.DOTALL
)

# Fix specs_comfort
content = re.sub(
    r'(if \(apiProduct\.specs_comfort\) \{\s*specs\.comfort = typeof apiProduct\.specs_comfort === \'string\' \?\s*JSON\.parse\(apiProduct\.specs_comfort\) : apiProduct\.specs_comfort;\s*)(})',
    r'\1} else {\n                            specs.comfort = [];\n                        }',
    content,
    flags=re.MULTILINE | re.DOTALL
)

# Fix specs_safety
content = re.sub(
    r'(if \(apiProduct\.specs_safety\) \{\s*specs\.safety = typeof apiProduct\.specs_safety === \'string\' \?\s*JSON\.parse\(apiProduct\.specs_safety\) : apiProduct\.specs_safety;\s*)(})',
    r'\1} else {\n                            specs.safety = [];\n                        }',
    content,
    flags=re.MULTILINE | re.DOTALL
)

# Write the fixed file
with open('detalle-producto.html', 'w') as f:
    f.write(content)

print("Fix applied successfully")
