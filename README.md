# Le site de Miblo

Présentation et documentation bilingues de Miblo 0.9.1, avec un style terminal
ASCII, un enregistrement de l’application et 18 pages de documentation et d’information dans chaque langue.
L’anglais est la version par défaut ; le français reste accessible partout.

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

- `content/home.html` / `content/home_en.html` : accueil français / anglais.
- `content/pages.py` / `content/pages_en.py` : les 16 guides français / anglais.
- `content/locales.py` : textes partagés et correspondance des adresses.
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
`index.html`, `fr/index.html`, `docs/*.html`, `en/docs/*.html`, les index
de recherche des deux langues et `sitemap.xml`. Modifier les
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

La démo provient du binaire Miblo 0.9.1, exécuté dans un PTY de 120 × 36.
Les textes, couleurs et panneaux viennent de sa sortie terminal. Les touches
sont envoyées à Miblo ; aucun menu ni résultat HTTP n’est reconstitué dans le
site. Les pauses entre écrans sont raccourcies, les étapes sont chapitrées.

Le scénario démarre en anglais, choisit Français avec Maj+L et vérifie la
mémorisation, puis télécharge les templates GitHub Releases, crée Group et User,
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

Le site est hébergé sur Hostinger à `https://cli.miblo.fr`. Les liens locaux sont
relatifs et fonctionnent aussi dans un sous-dossier. Pour changer de domaine,
modifier `BASE` dans `scripts/build.py`, le contrôle dans `scripts/check.py`,
`robots.txt`, puis régénérer.

Dans hPanel, sélectionner **cli.miblo.fr** et ouvrir son gestionnaire de fichiers.
Sauvegarder `public_html` hors du dossier public avant une mise à jour, puis
y publier `index.html`, les fichiers CSS et JavaScript, `favicon.svg`,
`search-index.json`, `robots.txt`, `sitemap.xml`, ainsi que `docs/`, `en/`, `fr/`, `assets/` et `.htaccess`.
Vider le cache du site dans hPanel et vérifier l’accueil, la démo et la recherche.
Les archives de sauvegarde, `.git/`, `content/` et `scripts/` restent hors du
dossier public. Le dépôt ne déploie ni ne publie de crate automatiquement.

La bêta publique est distribuée sous le nom **miblo** sur crates.io, avec des
binaires Windows x64, Linux x64 et macOS Apple Silicon/Intel sur GitHub Releases.
La commande affichée est `cargo install miblo --version 0.9.1 --locked`. Les liens des archives
et leurs sommes SHA-256 sont centralisés dans `content/downloads.py`.
La version partagée dans `content/downloads.py` alimente les liens, les commandes
d’installation, les deux accueils et les métadonnées. Lors d’une release, mettre
à jour cette version, les guides concernés et l’enregistrement réel, puis vérifier
les téléchargements avant de déployer.

La documentation est fondée sur le code et le README du dépôt `Miblo`, ainsi que
sur les templates 0.6.0. Conserver les versions et les limites cohérentes lors
des prochaines évolutions.

## Langues et référencement

- `/` : accueil anglais ; `/en/docs/` : guides anglais.
- `/fr/` : accueil français ; `/docs/` : adresses des guides français conservées.
- EN / FR pointe vers la même page dans l’autre langue et conserve l’ancre.
- Pas de redirection selon le navigateur : chaque version est accessible aux
  visiteurs et aux robots, même sans JavaScript.
- Titres et descriptions propres à chaque page, URL canonique HTTPS, liens
  `hreflang` réciproques (`en`, `fr`, `x-default` anglais).
- Sitemap contenant les 34 pages canoniques ; aucun résultat de recherche
  interne ni paramètre de démo ne crée une page indexable supplémentaire.
- Données JSON-LD WebSite, SoftwareApplication, TechArticle et BreadcrumbList.
  Aucun avis, note ou résultat commercial inventé.
- Cartes Open Graph / Twitter de 1200 × 630 dans chaque langue. Pour les
  régénérer : `python3 scripts/social_assets.py` (Pillow, uniquement à l’édition).
- `.htaccess` redirige les adresses `index.html` vers leur répertoire canonique,
  désactive le listing et limite le cache HTML/JSON à cinq minutes. Le serveur
  Python de développement ne lit pas ce fichier ; le vérifier sur Hostinger.

La recherche utilise 105 entrées par langue. Les légendes et commandes du lecteur
sont traduites ; les cellules de l’enregistrement restent la sortie réelle de
l’application : démarrage en anglais, puis passage en français depuis son menu.
Les URL des données et légendes portent leur empreinte pour éviter un mélange
entre une ancienne démo en cache et ses nouveaux styles.

Créer une archive à publier après les contrôles :

```sh
python3 scripts/package_site.py --output /tmp/miblo-site.zip
```

L’archive exclut sources, Git, scripts, caches et sauvegardes. Extraire son contenu
dans `public_html` du site cli.miblo.fr, conserver la sauvegarde hors du dossier
public et purger le cache. Après mise en ligne, vérifier une page anglaise, sa
version française, la recherche, les liens d’installation et les redirections.

Dans Google Search Console, soumettre `https://cli.miblo.fr/sitemap.xml`, puis
suivre l’indexation et les Core Web Vitals. Le référencement technique ne garantit
ni une date d’indexation ni une position : les guides utiles, leur maintenance et
les liens depuis des projets pertinents comptent également.

Références : [versions localisées Google](https://developers.google.com/search/docs/specialty/international/localized-versions),
[URL canoniques](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls).


## Mesure d’audience et campagnes

Google Analytics utilise la propriété **Miblo CLI — cli.miblo.fr** (565008298),
le flux Web **Site Miblo CLI** (16365965729) et l’identifiant public
`G-1JWCJX6DQ7`, centralisé dans `content/analytics.py`. Cet identifiant n’est pas
un secret. Ne jamais ajouter de clé d’API ou de jeton au site statique.

`analytics.js` charge Google uniquement après acceptation, sur `cli.miblo.fr`.
La préférence expire après 180 jours et se modifie via le pied de page.
Les aperçus locaux n’envoient rien à Google. Les mesures améliorées automatiques
sont désactivées pour ce flux : les événements choisis sont `page_view`,
`demo_start`, `install_copy`, `install_click` et `download_click`. Les clics
ne prouvent ni un téléchargement terminé ni une installation réussie.
Le texte des recherches, les valeurs des formulaires et les corps de requêtes
ne sont pas collectés par ce code. La balise désactive les fonctions publicitaires.

Liens prêts pour les publications françaises :

- LinkedIn : https://cli.miblo.fr/fr/?utm_source=linkedin&utm_medium=social&utm_campaign=miblo_beta_091&utm_content=demo
- Instagram Reels : https://cli.miblo.fr/fr/?utm_source=instagram&utm_medium=social&utm_campaign=miblo_beta_091&utm_content=reel
- Instagram bio : https://cli.miblo.fr/fr/?utm_source=instagram&utm_medium=social&utm_campaign=miblo_beta_091&utm_content=bio

Pour une campagne payante, utiliser `utm_medium=paid_social`. Pour la page
anglaise, remplacer `/fr/` par `/`. Les valeurs UTM acceptées contiennent
uniquement lettres, chiffres, tirets et underscores, sur 80 caractères maximum.
Ne pas y placer de nom, d’e-mail ou d’autre donnée personnelle. La préférence
s’applique à tout le site ; seules les visites consenties apparaîtront dans GA4.

Contrôle : `node scripts/check_analytics.cjs` couvre acceptation, refus,
retrait, expiration, stockage indisponible, retrait depuis un autre onglet,
nettoyage des URL et désactivation en aperçu local. Dans Google Analytics,
consulter les rapports d’acquisition et les événements après réception des données.

## Référencement Google et assistants IA

- Le sitemap canonique est `https://cli.miblo.fr/sitemap.xml` (`xml`, pas `xlm`).
  Il est généré avec les versions EN/FR/x-default de chaque page. Pas de fausses
  dates de modification ni de pages dupliquées pour les campagnes UTM.
- La propriété Search Console `https://cli.miblo.fr/` est vérifiée par la balise
  déjà présente. Le sitemap était lu avec succès avant cette mise à jour.
- Titres, descriptions, canonical, hreflang, Open Graph, images sociales et
  données structurées sont générés depuis les mêmes sources. La FAQ structurée
  reprend exactement les réponses visibles ; elle ne garantit pas un résultat
  enrichi Google, dont l’affichage est restreint selon le type de site.
- `robots.txt` autorise les moteurs et les robots de recherche OpenAI/Anthropic.
  Le contenu et les liens essentiels sont servis en HTML sans JavaScript.
- `llms.txt` est un index facultatif des sources officielles et de la documentation,
  généré avec la version courante. Ce n’est ni un enregistrement auprès des IA,
  ni une garantie de citation ou d’entraînement des modèles.
- La génération concerne Rust/Axum/SQLx, SQLite et MySQL. La FAQ précise les
  limites pour éviter que des descriptions externes attribuent des fonctionnalités
  absentes à Miblo. Ne pas publier de notes, avis ou performances inventés.

À suivre après publication : indexation et requêtes dans Search Console,
visites depuis les moteurs/assistants et campagnes dans GA4. Les aperçus sociaux
utilisent les images 1200 × 630 existantes. Une publication avec un lien réel
vers la démo aide à faire découvrir le projet ; aucune campagne n’est envoyée
ni achetée automatiquement par ce dépôt.

Références de mise en œuvre :
[Google : recherche et IA](https://developers.google.com/search/docs/appearance/ai-features),
[OpenAI : robots de recherche](https://developers.openai.com/api/docs/bots),
[Anthropic : robots](https://support.claude.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler),
[Google : consentement](https://developers.google.com/tag-platform/security/guides/consent).
