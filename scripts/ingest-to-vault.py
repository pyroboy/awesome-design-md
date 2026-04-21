#!/usr/bin/env python3
"""
ingest-to-vault.py
Converts all fetched DESIGN.md files from the fork into Obsidian notes
with proper frontmatter, then syncs to the vault.
"""

import os, re
from pathlib import Path
from datetime import datetime

FORK_DIR = Path('/Users/arjomagno/Documents/github-repos/awesome-design-md')
DESIGNS_DIR = FORK_DIR / 'design-md'
OBSIDIAN_DIR = Path('/Users/arjomagno/Documents/ArjoSecondBrain/03-ArjoStyle/Design/VoltAgent Design MD')
OBSIDIAN_BRANDS = OBSIDIAN_DIR / 'brands'
INDEX_FILE = OBSIDIAN_DIR / '00-Index.md'

BRAND_TAGS = {
    'airbnb': ['travel', 'hospitality', 'brand'],
    'airtable': ['spreadsheet', 'database', 'saas'],
    'apple': ['hardware', 'consumer', 'premium', 'minimal'],
    'bmw': ['automotive', 'luxury', 'dark'],
    'cal': ['scheduling', 'calendar', 'saas', 'developer'],
    'claude': ['ai', 'anthropic', 'developer'],
    'clay': ['design', 'agency', 'creative', 'gradient'],
    'clickhouse': ['database', 'analytics', 'developer'],
    'cohere': ['ai', 'llm', 'developer', 'gradient'],
    'coinbase': ['crypto', 'fintech', 'blue'],
    'composio': ['integration', 'ai', 'developer', 'tool'],
    'cursor': ['ai', 'code-editor', 'developer', 'dark'],
    'elevenlabs': ['ai', 'audio', 'voice', 'dark'],
    'expo': ['react-native', 'mobile', 'developer', 'dark'],
    'ferrari': ['automotive', 'luxury', 'racing', 'editorial'],
    'figma': ['design-tool', 'collaboration', 'saas'],
    'framer': ['web-builder', 'design', 'creative', 'bold'],
    'hashicorp': ['infrastructure', 'devops', 'enterprise'],
    'ibm': ['enterprise', 'carbon-design', 'blue'],
    'intercom': ['messaging', 'customer', 'saas', 'friendly'],
    'kraken': ['crypto', 'trading', 'dark', 'purple'],
    'lamborghini': ['automotive', 'luxury', 'racing', 'black'],
    'linear.app': ['project-management', 'saas', 'dark', 'minimal'],
    'lovable': ['ai', 'full-stack', 'developer', 'gradient'],
    'minimax': ['ai', 'video', 'neon'],
    'mintlify': ['docs', 'developer', 'documentation'],
    'miro': ['collaboration', 'canvas', 'saas', 'yellow'],
    'mistral.ai': ['ai', 'llm', 'french', 'minimal'],
    'mongodb': ['database', 'nosql', 'developer', 'green'],
    'notion': ['productivity', 'docs', 'saas', 'warm'],
    'nvidia': ['gpu', 'ai', 'hardware', 'green'],
    'ollama': ['ai', 'local-llm', 'developer', 'terminal'],
    'opencode.ai': ['ai', 'code', 'developer', 'dark'],
    'pinterest': ['social', 'visual', 'discovery', 'red'],
    'posthog': ['analytics', 'product', 'saas', 'playful'],
    'raycast': ['launcher', 'macos', 'developer', 'chrome'],
    'renault': ['automotive', 'french', 'gradient', 'ev'],
    'replicate': ['ai', 'ml', 'developer', 'white'],
    'resend': ['email', 'developer', 'transactional', 'dark'],
    'revolut': ['fintech', 'banking', 'saas', 'dark'],
    'runwayml': ['ai', 'video', 'creative', 'cinematic'],
    'sanity': ['cms', 'developer', 'content', 'red'],
    'sentry': ['monitoring', 'developer', 'errors', 'dark'],
    'spacex': ['aerospace', 'rockets', 'minimal'],
    'spotify': ['music', 'streaming', 'consumer', 'green'],
    'stripe': ['fintech', 'payments', 'developer', 'purple'],
    'supabase': ['database', 'firebase', 'developer', 'emerald'],
    'superhuman': ['email', 'productivity', 'minimal', 'dark'],
    'tesla': ['ev', 'automotive', 'premium', 'minimal'],
    'together.ai': ['ai', 'infrastructure', 'developer', 'technical'],
    'uber': ['mobility', 'marketplace', 'black', 'bold'],
    'vercel': ['hosting', 'developer', 'deploy', 'black'],
    'voltagent': ['ai', 'agents', 'developer', 'void'],
    'warp': ['terminal', 'developer', 'rust', 'dark'],
    'webflow': ['web-builder', 'designer', 'saas', 'blue'],
    'wise': ['fintech', 'remittance', 'saas', 'green'],
    'x.ai': ['ai', 'chat', 'monochrome'],
    'zapier': ['automation', 'integration', 'saas', 'orange'],
}

BRAND_CATEGORIES = {
    'Developer Tools': ['linear.app', 'vercel', 'warp', 'raycast', 'figma', 'sanity', 'supabase', 'sentry', 'posthog', 'mintlify', 'opencode.ai', 'ollama', 'clay', 'voltagent'],
    'AI & ML': ['claude', 'minimax', 'elevenlabs', 'mistral.ai', 'together.ai', 'replicate', 'cohere', 'cursor', 'x.ai', 'runwayml'],
    'Fintech & Payments': ['stripe', 'revolut', 'coinbase', 'wise', 'uber'],
    'Consumer & Social': ['airbnb', 'spotify', 'pinterest', 'notion', 'intercom', 'resend', 'zapier', 'lovable'],
    'Automotive & Luxury': ['tesla', 'bmw', 'ferrari', 'lamborghini', 'renault'],
    'Enterprise & B2B': ['ibm', 'hashicorp', 'mongodb', 'nvidia', 'clickhouse', 'kraken', 'composio', 'cal', 'expo'],
    'Platforms & Apps': ['apple', 'airtable', 'framer', 'webflow', 'miro'],
}

def slug(brand):
    return brand.replace('.', '-')

def display_name(brand):
    return brand.replace('.', ' ').replace('-', ' ')

def extract_meta(content, brand):
    title = display_name(brand).title() + ' Design System'
    h1 = re.search(r'^#\s+(.+?)$', content, re.MULTILINE)
    if h1:
        title = h1.group(1).strip()
    paras = re.findall(r'^(?!#)(.+?)(?:\n\n|\n(?=#))', content, re.MULTILINE)
    description = paras[0].strip()[:300] if paras else ''
    colors = list(set(re.findall(r'#[0-9a-fA-F]{6}', content)))[:20]
    rgba = re.findall(r'rgba?\([0-9,.\s]+\)', content)
    colors = (colors + rgba)[:20]
    fonts = list(set(re.findall(r'(?:Inter|Geist|SF\s*Pro|Berkeley Mono|JetBrains Mono|DM Sans|Bebas Neue|Apple System|Helvetica Neue|Roboto|Courier New|Mono)[\w\s]*', content, re.I)))[:8]
    fonts = [f.strip() for f in fonts if len(f.strip()) > 2]
    return {
        'title': title,
        'description': description,
        'colors': colors,
        'fonts': fonts,
    }

def build_frontmatter(brand, meta):
    today = datetime.now().strftime('%Y-%m-%d')
    slug_brand = slug(brand)
    tags = BRAND_TAGS.get(brand, ['design', 'reference'])
    category = next((cat for cat, brands in BRAND_CATEGORIES.items() if brand in brands), 'Other')
    qt = '"'
    tags_str = ', '.join(qt + t + qt for t in tags)
    colors_str = ', '.join(qt + c + qt for c in meta['colors'][:12])
    fonts_str = ', '.join(qt + f + qt for f in meta['fonts'][:6])
    desc = meta['description'][:200].replace('"', '""')
    fm_lines = [
        '---',
        f'title: "{meta["title"]}"',
        f'alias: "{display_name(brand).title()} Design System"',
        'source: VoltAgent/awesome-design-md',
        f'fork_url: "https://github.com/pyroboy/awesome-design-md"',
        f'live_url: "https://getdesign.md/{brand}/design-md"',
        f'brand: "{display_name(brand).title()}"',
        f'slug: "{slug_brand}"',
        f'category: "{category}"',
        f'fetched: "{today}"',
        f'tags: [{tags_str}]',
        f'description: "{desc}"',
        f'colors: [{colors_str}]',
        f'fonts: [{fonts_str}]',
        'type: design-reference',
        'vault_section: 03-ArjoStyle/Design',
        '---',
        '',
    ]
    return '\n'.join(fm_lines)

def build_index():
    categories = {}
    for brand_dir in sorted(DESIGNS_DIR.iterdir()):
        if not brand_dir.is_dir():
            continue
        design_file = brand_dir / 'DESIGN.md'
        if not design_file.exists() or design_file.stat().st_size < 1000:
            continue
        content = design_file.read_text(encoding='utf-8', errors='ignore')
        meta = extract_meta(content, brand_dir.name)
        cat = next((c for c, brands in BRAND_CATEGORIES.items() if brand_dir.name in brands), 'Other')
        if cat not in categories:
            categories[cat] = []
        categories[cat].append((brand_dir.name, meta['title']))

    today = datetime.now().strftime('%Y-%m-%d')
    lines = [
        '---',
        'title: "VoltAgent Awesome Design MD — Index"',
        f'fetched: "{today}"',
        'type: index',
        'vault_section: 03-ArjoStyle/Design',
        'tags: ["design-reference", "ai-agents", "design-systems"]',
        'description: "Full offline mirror of VoltAgent/awesome-design-md -- 58 curated DESIGN.md files from popular brands."',
        '---',
        '',
        '# VoltAgent Awesome Design MD -- Index',
        '',
        f'> 58 curated design systems from popular brands. Each note captures the complete visual language -- colors, typography, spacing, motion, components -- as a plain-text DESIGN.md that any AI coding agent can read.',
        '',
        '**Source fork:** [pyroboy/awesome-design-md](https://github.com/pyroboy/awesome-design-md)',
        '**Original:** [VoltAgent/awesome-design-md](https://github.com/VoltAgent/awesome-design-md)',
        '**Live preview:** [getdesign.md](https://getdesign.md)',
        '',
        '---',
        '',
    ]
    for cat, brands in sorted(categories.items()):
        lines.append(f'## {cat}')
        lines.append('')
        for brand, title in brands:
            s = slug(brand)
            lines.append(f'- [[brands/{s}|{title}]]')
        lines.append('')
    lines.extend([
        '---',
        '',
        '## Tags',
        '#design-reference #ai-agents #design-systems #typography #color-systems #component-patterns',
        '',
    ])
    return '\n'.join(lines)

def main():
    os.makedirs(str(OBSIDIAN_BRANDS), exist_ok=True)
    os.makedirs(str(OBSIDIAN_DIR), exist_ok=True)
    done = []
    skipped = []

    for brand_dir in sorted(DESIGNS_DIR.iterdir()):
        if not brand_dir.is_dir():
            continue
        design_file = brand_dir / 'DESIGN.md'
        if not design_file.exists():
            skipped.append(brand_dir.name)
            continue
        size = design_file.stat().st_size
        if size < 1000:
            skipped.append(f"{brand_dir.name} ({size} bytes)")
            continue
        content = design_file.read_text(encoding='utf-8', errors='ignore')
        meta = extract_meta(content, brand_dir.name)
        fm = build_frontmatter(brand_dir.name, meta)
        obsidian_note = fm + '\n' + content
        out_file = OBSIDIAN_BRANDS / (slug(brand_dir.name) + '.md')
        out_file.write_text(obsidian_note, encoding='utf-8')
        done.append((brand_dir.name, size))

    index_content = build_index()
    INDEX_FILE.write_text(index_content, encoding='utf-8')

    print(f'DONE: {len(done)} notes written to vault')
    if skipped:
        print(f'SKIPPED: {skipped}')
    print()
    print('Top 5 by content size:')
    for brand, size in sorted(done, key=lambda x: x[1], reverse=True)[:5]:
        print(f'  {size:>6} bytes -- {brand}')
    print()
    print(f'Index: {INDEX_FILE}')
    print(f'Notes: {OBSIDIAN_BRANDS}/')

if __name__ == '__main__':
    main()
