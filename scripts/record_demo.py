#!/usr/bin/env python3
"""Record the real Miblo TUI, generated SQLite API and HTTP responses.

Requires pyte 0.8.2, Rust and a built Miblo binary. No mocked process or API.
The player keeps these terminal cells intact; only pauses are shortened.
"""
import argparse
import errno
import fcntl
import hashlib
import json
import os
from pathlib import Path
import pty
import select
import signal
import socket
import sqlite3
import struct
import subprocess
import tempfile
import termios
import time

import pyte

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--miblo', type=Path, required=True)
parser.add_argument('--target-dir', type=Path, required=True)
parser.add_argument('--output', type=Path, default=Path('assets/miblo-demo.json'))
args = parser.parse_args()
binary = args.miblo.resolve()
WIDTH, HEIGHT = 120, 36
DOWN, UP, ENTER, CLEAR = '\x1b[B', '\x1b[A', '\r', '\x15'
frames, styles, chapters = [], [], []


class Terminal:
    def __init__(self, cwd, env):
        self.screen = pyte.Screen(WIDTH, HEIGHT)
        self.stream = pyte.ByteStream(self.screen)
        self.pid, self.fd = pty.fork()
        if self.pid == 0:
            os.chdir(cwd)
            os.execve(str(binary), [str(binary)], env)
        fcntl.ioctl(self.fd, termios.TIOCSWINSZ, struct.pack('HHHH', HEIGHT, WIDTH, 0, 0))
        os.kill(self.pid, signal.SIGWINCH)

    def pump(self, timeout=.05):
        if select.select([self.fd], [], [], timeout)[0]:
            try:
                self.stream.feed(os.read(self.fd, 65536))
            except OSError as e:
                if e.errno != errno.EIO:
                    raise

    def settle(self):
        until = time.monotonic() + .16
        while time.monotonic() < until:
            self.pump()

    def text(self):
        return '\n'.join(self.screen.display)

    def wait(self, text, timeout=30):
        until = time.monotonic() + timeout
        while time.monotonic() < until:
            self.pump()
            if text in self.text():
                self.settle()
                return
        raise AssertionError(f'Missing {text!r}\n{self.text()}')

    def send(self, keys):
        os.write(self.fd, keys.encode())
        self.settle()

    def capture(self, caption, key='', seconds=1.6):
        self.settle()
        rows = []
        for y in range(HEIGHT):
            runs = []
            for x in range(WIDTH):
                c = self.screen.buffer[y][x]
                style = [c.fg, c.bg, c.bold, c.italics, c.underscore, c.reverse]
                if style not in styles:
                    styles.append(style)
                index = styles.index(style)
                if runs and runs[-1][0] == index:
                    runs[-1][1] += c.data
                else:
                    runs.append([index, c.data])
            rows.append(runs)
        frames.append(dict(rows=rows, caption=caption, key=key, seconds=seconds))
        print(f'{len(frames):02d} {caption}', flush=True)

    def go(self, keys, expected, caption, key='', seconds=1.6, timeout=30):
        self.send(keys)
        self.wait(expected, timeout)
        self.capture(caption, key, seconds)

    def chapter(self, title):
        chapters.append(dict(title=title, frame=len(frames)))

    def close(self):
        self.send('\x03')
        until = time.monotonic() + 5
        while time.monotonic() < until:
            self.pump()
            pid, _ = os.waitpid(self.pid, os.WNOHANG)
            if pid:
                os.close(self.fd)
                return
        os.kill(self.pid, signal.SIGKILL)
        os.close(self.fd)
        os.waitpid(self.pid, 0)


with tempfile.TemporaryDirectory(prefix='miblo-demo-', dir='/private/tmp') as directory:
    root = Path(directory)
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        port = sock.getsockname()[1]
    env = dict(os.environ, TERM='xterm-256color', CARGO_TARGET_DIR=str(args.target_dir.resolve()), CARGO_NET_OFFLINE='true', MIBLO_CONFIG_DIR=str(root / 'preferences'))
    for name in ['DATABASE_URL', 'SERVER_PORT', 'SERVER_ADDRESS', 'MIBLO_TEMPLATE_DIR', 'MIBLO_TEMPLATE_BASE_URL', 'MIBLO_LANGUAGE', 'MIBLO_NO_ANIMATION', 'NO_COLOR']:
        env.pop(name, None)
    ui = Terminal(root, env)
    try:
        ui.chapter('Langue')
        ui.wait('API workspace')
        ui.capture('Miblo au lancement', seconds=2.2)
        ui.go('L', 'Applies immediately', 'Choisir English ou Français', 'Maj+L', 3)
        ui.go(DOWN + ENTER, 'Langue enregistrée : français', 'Passer en français, choix mémorisé', '↓ Entrée', 3)
        assert json.loads((root / 'preferences/settings.json').read_text())['language'] == 'fr'
        ui.chapter('Projet')
        ui.go('n', 'Nom de la nouvelle API', 'Créer une API', 'n')
        ui.go(CLEAR + 'team-api' + ENTER, 'Dossier à créer', 'Choisir le dossier', 'Entrée')
        ui.go(ENTER, 'Port du serveur', 'Configurer le port', 'Entrée')
        ui.go(CLEAR + str(port) + ENTER, 'Base de données', 'Choisir SQLite ou MySQL', 'Entrée', 2.5)
        ui.go(ENTER, 'Source du template', 'Choisir les templates GitHub Releases', 'Entrée', 2.5)
        ui.go(ENTER, 'Créer cette API ?', 'Confirmer la création', 'Entrée', 2.5)
        ui.go(ENTER, 'Migrations à jour', 'Projet créé, SQLite initialisé', 'Entrée', 3, timeout=120)
        ui.wait('Aucune action en cours')
        project = root / 'team-api'
        assert (project / 'miblo.sqlite').is_file()

        ui.chapter('Modèles')
        ui.go('a', 'Nom du modèle', 'Ajouter le modèle Group', 'a')
        ui.go('Group' + ENTER, 'Nom du champ', 'Ajouter le champ name', 'Entrée')
        ui.go('name' + ENTER, 'Type du champ', 'Choisir le type du champ', 'Entrée', 2.2)
        ui.go(ENTER, 'Options du champ', 'Choisir les options du champ', 'Entrée', 2.2)
        ui.go(ENTER, 'Champs de la ressource', 'Terminer les champs de Group', 'Entrée')
        ui.go(DOWN + ENTER, 'Adresse de la collection', 'Choisir /groups', '↓ Entrée')
        ui.go(ENTER, 'Ajouter cette ressource ?', 'Vérifier la génération du modèle et du CRUD', 'Entrée', 2.5)
        ui.go(ENTER, '1 ressource(s)', 'Group et ses routes générés', 'Entrée')
        ui.wait('Migrations à jour'); ui.wait('Aucune action en cours')
        ui.go('a', 'Nom du modèle', 'Ajouter User', 'a')
        ui.go('User' + ENTER, 'Nom du champ', 'Définir les champs de User', 'Entrée')
        ui.go('name' + ENTER, 'Type du champ', 'name : texte court', 'Entrée')
        ui.send(ENTER); ui.wait('Options du champ')
        ui.send(ENTER); ui.wait('Champs de la ressource')
        ui.send(ENTER); ui.wait('Nom du champ')
        ui.go('email' + ENTER, 'Type du champ', 'email : texte court', 'Entrée')
        ui.send(ENTER); ui.wait('Options du champ')
        ui.go(DOWN + ' ', '[×] Unique', 'Interdire les doublons sur email', '↓ Espace', 2.5)
        ui.send(ENTER); ui.wait('Champs de la ressource')

        ui.chapter('Relation')
        ui.go(DOWN * 3 + ENTER, 'Modèle / table à référencer', 'Relier User au modèle Group', '↓ Entrée', 2.5)
        ui.go(ENTER, 'Nom de la clé étrangère', 'Nom proposé : group_id', 'Entrée')
        ui.send(ENTER); ui.wait('Options du champ')
        ui.go(' ', '[×] Facultatif', 'Autoriser une relation facultative', 'Espace')
        ui.go(ENTER, 'Si la ligne référencée', 'Choisir la règle de suppression', 'Entrée', 2.5)
        ui.send(ENTER); ui.wait('Champs de la ressource')
        ui.send(DOWN + ENTER); ui.wait('Adresse de la collection')
        ui.go(ENTER, 'Ajouter cette ressource ?', 'Vérifier User et sa clé étrangère', 'Entrée', 3)
        ui.go(ENTER, '2 ressource(s)', 'User, sa table et ses routes générés', 'Entrée')
        ui.wait('Migrations à jour'); ui.wait('Aucune action en cours')
        with sqlite3.connect(project / 'miblo.sqlite') as db:
            assert db.execute("PRAGMA foreign_key_list(users)").fetchone()[2:5] == ('groups', 'group_id', 'id')

        ui.chapter('Schéma')
        ui.send('d'); ui.wait('Schéma réel'); ui.wait('Tables (2)')
        ui.go('j', 'TABLE users', 'Lire le schéma réel et la relation', 'd ↓', 4)
        ui.send('d'); ui.wait('Réponse HTTP')

        ui.chapter('Route')
        ui.go('g', 'Créer une route — modèle associé', 'Créer une route liée à un modèle', 'g', 2.5)
        ui.go(DOWN + ENTER, 'Action de la route pour ce modèle', 'Choisir l’action CRUD de User', '↓ Entrée', 2.5)
        ui.go(DOWN * 2 + ENTER, 'Chemin de la route', 'Créer une ligne : POST', '↓ ↓ Entrée')
        ui.go(CLEAR + '/members' + ENTER, 'Nom de la route / fonction', 'Nommer la fonction', 'Entrée')
        ui.go(ENTER, 'Créer cette route ?', 'Confirmer POST /members', 'Entrée', 3)
        ui.go(ENTER, 'Création de route : exit status: 0', 'Route générée avec le CRUD de User', 'Entrée', 2)
        ui.wait('Aucune action en cours')

        ui.chapter('POST')
        ui.send('r')
        ui.wait('API en cours', timeout=240)
        ui.capture('API compilée et lancée', 'r', 3)
        ui.send(':routes' + ENTER)
        # Routes: health, five Group routes, five User routes, then POST /members.
        ui.send('j' * 11)
        ui.go('x', 'Préparer la requête', 'Champs préremplis depuis User', 'x', 3.5)
        ui.wait('/members')
        # Edit values through the actual typed request editor (no JSON entry).
        ui.send('jj' + ENTER); ui.wait('Saisis uniquement la valeur')
        ui.send(CLEAR + 'Léa' + ENTER); ui.wait('Envoyer la requête')
        ui.send('j' + ENTER); ui.wait('Saisis uniquement la valeur')
        ui.go(CLEAR + 'lea@example.test' + ENTER, 'Envoyer la requête', 'Modifier les valeurs du formulaire', 'Entrée', 3)
        ui.go('kkk' + ENTER, 'POST : HTTP 201', 'Réponse réelle de POST /members', 'Entrée', 4)
        with sqlite3.connect(project / 'miblo.sqlite') as db:
            row = db.execute('SELECT id,name,email,group_id FROM users').fetchone()
            assert row == (1, 'Léa', 'lea@example.test', None), row

        ui.chapter('Migration')
        ui.go('s', 'API arrêtée', 'Arrêter l’API avant de modifier User', 's')
        ui.go('m', 'Modifier un modèle existant', 'Modifier le modèle User', 'm')
        ui.go(DOWN + ENTER, 'champs existants', 'Ajouter un champ facultatif', '↓ Entrée', 2.5)
        ui.send(ENTER); ui.wait('Nom du nouveau champ')
        ui.send('nickname' + ENTER); ui.wait('Type du champ')
        ui.go(ENTER, 'anciennes lignes à NULL', 'nickname : facultatif, anciennes lignes à NULL', 'Entrée', 2.5)
        ui.send(ENTER); ui.wait('Champs de la ressource')
        ui.go(DOWN + ENTER, 'Générer la modification du modèle', 'Vérifier la migration ALTER TABLE', '↓ Entrée', 3)
        ui.go(ENTER, 'Mise à jour BDD requise', 'Migration générée, base à mettre à jour', 'Entrée', 3)
        ui.wait('Aucune action en cours')
        ui.go('b', 'Appliquer les migrations', 'Ouvrir les actions de la base', 'b')
        ui.go(DOWN + ENTER, 'Confirmer', 'Confirmer l’application de la migration', '↓ Entrée', 2)
        ui.go(ENTER, 'Migrations à jour', 'Migration appliquée', 'Entrée', 2.5)
        ui.wait('Aucune action en cours')
        with sqlite3.connect(project / 'miblo.sqlite') as db:
            assert db.execute('SELECT id,name,email,group_id,nickname FROM users').fetchone() == (*row, None)
        ui.send('r'); ui.wait('API en cours', timeout=240)
        ui.send(':routes' + ENTER)
        # Currently /members is selected: three moves up reach GET /users/{id}.
        ui.send('kkk'); ui.send('x'); ui.wait('Chemin HTTP')
        ui.go(ENTER, 'GET : HTTP 200', 'Ligne conservée, nickname à null', 'Entrée', 4)
        ui.wait('nickname')

        ui.chapter('Code')
        ui.send(':routes' + ENTER)
        # Select the model panel and open its generated handler in the code preview.
        ui.send('\x1b[Z\x1b[Z' + ENTER)
        ui.capture('Fichiers du projet et aperçu du code', 'Tab · Entrée', 3)
        ui.go(' ', 'Actions', 'Les actions disponibles dans Miblo', 'Espace', 3)
        ui.send('\x1b'); ui.send('s'); ui.wait('API arrêtée')
        ui.capture('Fin de la démonstration', 's', 2)
        state = json.loads((project / '.miblo/state.json').read_text())
        cli_version = subprocess.check_output([str(binary), '--version'], text=True).strip().split()[-1]
        payload = dict(version=1, cliVersion=cli_version, templateVersion=state['template']['version'],
                       binarySha256=hashlib.sha256(binary.read_bytes()).hexdigest(),
                       columns=WIDTH, lines=HEIGHT, styles=styles, chapters=chapters, frames=frames,
                       verification={'source':'real-pty', 'database':'sqlite', 'templateUrl':state['template']['url'],
                                     'postStatus':201, 'readAfterMigrationStatus':200,
                                     'rowPreserved':True, 'foreignKeyVerified':True,
                                     'defaultLanguage':'en', 'savedLanguage':'fr', 'languageSwitchVerified':True})
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(payload, ensure_ascii=False, separators=(',', ':')) + '\n')
        print(f'Saved {len(frames)} real screens to {args.output}', flush=True)
    except BaseException:
        print(ui.text(), flush=True)
        raise
    finally:
        ui.close()
