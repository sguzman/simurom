import sys

with open('crates/simurom-schema/Cargo.toml', 'r') as f:
    content = f.read()

if 'serde_json' not in content:
    content += '\n[dev-dependencies]\nserde_json = "1.0"\n'

with open('crates/simurom-schema/Cargo.toml', 'w') as f:
    f.write(content)
