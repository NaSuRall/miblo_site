# Le site de Miblo

Présentation et documentation françaises de Miblo 0.9, avec un style terminal
ASCII, un enregistrement de l’application et 16 pages de documentation.

Le site est statique : HTML, CSS et JavaScript natif, sans dépendance à installer,
police distante, outil de suivi ou service externe nécessaire à la lecture.
Les fichiers générés sont versionnés et peuvent être servis tels quels.

## Voir le site localement

Depuis ce dossier, avec Python 3.10+ :

```sh
python3 -m http.server 4173 --bind 127.0.0.1
```

Ouvrir `http://127.0.0.1:4173/`. Arrêter avec Ctrl+C. Utiliser un serveur HTTP
pour la recherche (le chargement de son index peut être bloqué via `file://`).

## Modifier le contenu

- `content/home.html` : présentation et lecteur de la démonstration.
- `content/pages.py` : chapitres de documentation, sections et exemples.
- `scripts/build.py` : en-tête, navigation, sommaire et pied de page communs.
- `style.css` : thème et mises en page adaptatives.
- `docs.css` : lecture des guides, tableaux et exemples dépliables.
- `demo.css` : accueil et interface de démonstration.
- `app.js` : recherche et copie des commandes.
- `demo.js` : lecture, pause, navigation et chapitres de l’enregistrement.
- `assets/miblo-demo.json` : cellules capturées dans le vrai terminal Miblo.
- `assets/miblo-demo.css` : couleurs du terminal, générées par le build.
- `assets/miblo-logo.svg` : logo bleu, issu des caractères de l’écran de lancement du CLI.

Après une modification du contenu ou du générateur :

```sh
python3 scripts/build.py
python3 scripts/check.py
node --check app.js
node --check demo.js
```

Le générateur utilise uniquement la bibliothèque standard Python. Il produit
`index.html`, `docs/*.html`, `search-index.json` et `sitemap.xml`. Modifier les
sources plutôt que les pages générées. Le vérificateur contrôle tous les liens
internes, les ancres, les identifiants, les métadonnées et les liens de recherche.
Node n’est utilisé que pour vérifier la syntaxe JavaScript ; aucun bundler.

## Navigation et accessibilité

La documentation et les liens fonctionnent sans JavaScript. La recherche
s’ouvre avec `/` ou Cmd/Ctrl+K ; flèches pour parcourir, Entrée pour ouvrir,
Échap pour fermer. Les écrans de démo se parcourent avec les flèches,
Home et End dans la barre de progression. La lecture démarre uniquement à la
demande et peut être mise en pause. Elle s’arrête quand la démo sort de l’écran
ou que l’onglet est masqué. Les chapitres et les flèches changent d’écran.
Le bouton Agrandir ouvre le lecteur dans une fenêtre modale ; Échap la ferme.
Sur petit écran, le terminal conserve sa taille lisible et défile horizontalement.
Les guides renvoient directement au chapitre concerné, par exemple
`index.html?demo=migration#demo`. Ces liens ouvrent la démo en pause.
Le menu documentaire se replie sur mobile. Les mouvements respectent
`prefers-reduced-motion`. Aucun appel à une API utilisateur n’est effectué :
le navigateur lit un enregistrement et ne lance aucune API.

## Réenregistrer la démonstration

La démo provient du binaire Miblo 0.9.0, exécuté dans un PTY de 120 × 36.
Les textes, couleurs et panneaux viennent de sa sortie terminal. Les touches
sont envoyées à Miblo ; aucun menu ni résultat HTTP n’est reconstitué dans le
site. Les pauses entre écrans sont raccourcies, les étapes sont chapitrées.

Le scénario télécharge les templates GitHub Releases, crée Group et User,
ajoute la relation, consulte le schéma, crée POST /members, lance la vraie API,
envoie un POST et fait évoluer User. Il vérifie la clé étrangère dans SQLite,
le statut HTTP 201, la conservation de la ligne et sa lecture après migration.

Pour le refaire, avec Rust, le binaire Miblo et `pyte==0.8.2` dans un environnement
Python de développement :

```sh
python scripts/record_demo.py --miblo ../Miblo/target/debug/miblo --target-dir /tmp/miblo-demo-target
python3 scripts/build.py
python3 scripts/check.py
```

L’enregistrement utilise un projet temporaire supprimé à la fin, une vraie
base SQLite et un port local libre. Le répertoire de compilation est conservé
pour les prises suivantes. Les dépendances Cargo doivent être en cache pour
la compilation hors ligne ; le téléchargement des templates nécessite le réseau.
`pyte` sert uniquement à la capture, pas au build ni au fonctionnement du site.

## Distribution et publication

Le domaine canonique existant est `https://miblo.fr`. Les liens locaux sont
relatifs et fonctionnent aussi dans un sous-dossier. Pour changer de domaine,
modifier `BASE` dans `scripts/build.py`, `robots.txt`, puis régénérer.

Publier les fichiers statiques et le dossier `docs/` sur l’hébergement existant.
Le dossier `content/` et les scripts ne sont pas requis pour servir les pages.
Ce dépôt ne déploie ni ne publie de crate automatiquement.

Au 17 novembre 2026, l’API crates.io ne contient pas `miblo_cli_v2` et la recherche
Miblo ne renvoie aucun paquet. Le site indique donc l’installation GitHub et
renvoie vers la recherche crates.io. Après publication, remplacer les mentions
dans `content/home.html` et `content/pages.py`, puis le lien `CRATES` du générateur
par la fiche officielle et régénérer. Vérifier la commande de registre avant
de la recommander.

La documentation est fondée sur le code et le README du dépôt `Miblo`, ainsi que
sur les templates 0.6.0. Conserver les versions et les limites cohérentes lors
des prochaines évolutions.
