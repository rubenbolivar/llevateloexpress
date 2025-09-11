import re

# Read original file
with open('detalle-producto.html', 'r') as f:
    content = f.read()

# Read the corrected block
with open('spec_fix_block.txt', 'r') as f:
    corrected_block = f.read()

# Define the pattern to match the problematic section
pattern = r'(// Procesar especificaciones técnicas\s+)if \(apiProduct\.specs_general\) \{[^}]+\}\s+if \(apiProduct\.specs_engine\) \{[^}]+\}\s+if \(apiProduct\.specs_comfort\) \{[^}]+\}\s+if \(apiProduct\.specs_safety\) \{[^}]+\}'

# Replace the block
new_content = re.sub(pattern, corrected_block.strip(), content, flags=re.MULTILINE | re.DOTALL)

# Write back to file
with open('detalle-producto.html', 'w') as f:
    f.write(new_content)

print('Specification fix applied successfully!')
