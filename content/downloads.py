"""Versioned native downloads shared by both installation guides."""

VERSION = '0.9.1'
RELEASE = f'https://github.com/NaSuRall/Miblo/releases/tag/v{VERSION}'
ASSETS = f'https://github.com/NaSuRall/Miblo/releases/download/v{VERSION}'
PLATFORMS = [
    ('Windows x64', 'x86_64-pc-windows-msvc', 'zip'),
    ('macOS Apple Silicon', 'aarch64-apple-darwin', 'tar.gz'),
    ('macOS Intel', 'x86_64-apple-darwin', 'tar.gz'),
    ('Linux x64 (glibc 2.35+)', 'x86_64-unknown-linux-gnu', 'tar.gz'),
]


def downloads(lang):
    items = []
    for label, target, extension in PLATFORMS:
        url = f'{ASSETS}/miblo-{VERSION}-{target}.{extension}'
        items.append(f'<li><a href="{url}">{label}</a> · <a href="{url}.sha256">SHA-256</a></li>')
    listing = '<ul>' + ''.join(items) + '</ul>'
    if lang == 'fr':
        return f'<p>Choisissez votre système pour télécharger <strong>Miblo {VERSION} bêta</strong> déjà compilé :</p>' + listing + '<p>Décompressez l’archive, puis placez <code>miblo</code> (ou <code>miblo.exe</code>) dans un dossier de votre <code>PATH</code>. Sous macOS/Linux, conservez le droit d’exécution du fichier. Lancez ensuite <code>miblo --version</code> dans un terminal.</p><p>Rust, Cargo, rustfmt et les outils natifs restent nécessaires pour compiler les API générées. Les binaires de cette bêta ne sont pas signés ni notariés ; <a href="https://crates.io/crates/miblo">l’installation avec Cargo</a> compile Miblo depuis ses sources.</p>' + f'<p><a href="{RELEASE}">Notes de version et toutes les archives</a>. Les <a href="https://github.com/NaSuRall/miblo_templates/releases">templates</a> sont téléchargés automatiquement au premier usage.</p>'
    return f'<p>Download a prebuilt <strong>Miblo {VERSION} beta</strong> for your system:</p>' + listing + '<p>Extract the archive and place <code>miblo</code> (or <code>miblo.exe</code>) in a directory on your <code>PATH</code>. On macOS/Linux, preserve its executable permission. Then run <code>miblo --version</code> in a terminal.</p><p>Rust, Cargo, rustfmt and native build tools are still required to compile generated APIs. These beta binaries are unsigned and not notarized; <a href="https://crates.io/crates/miblo">installation with Cargo</a> builds Miblo from source.</p>' + f'<p><a href="{RELEASE}">Release notes and all archives</a>. <a href="https://github.com/NaSuRall/miblo_templates/releases">Templates</a> are downloaded automatically on first use.</p>'
