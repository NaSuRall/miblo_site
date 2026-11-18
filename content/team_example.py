"""A reproducible continuation of the first API guide, verified with CLI 0.9.1."""
from content.pages import p, code as fr_code, table as fr_table
from content.pages_en import code as en_code, table as en_table

ADD_RELATION = '''
miblo add Group name:string --yes
miblo edit User 'group_id:int?:ref=Group' --yes
miblo db migrate
miblo run
'''
LINK_USER = r'''
curl -i http://127.0.0.1:3000/groups \
  -H 'Content-Type: application/json' \
  -d '{"name":"Engineering"}'

curl -i -X PATCH http://127.0.0.1:3000/users/1 \
  -H 'Content-Type: application/json' \
  -d '{"group_id":1}'
'''
CUSTOM_ROUTE = '''
miblo route add create_member --resource User --action create --path /members --yes
miblo run
'''
CREATE_MEMBER = r'''
curl -i http://127.0.0.1:3000/members \
  -H 'Content-Type: application/json' \
  -d '{"name":"Bob","email":"bob@example.com","group_id":1}'
'''


def page(lang):
    en = lang == 'en'
    code, table = (en_code, en_table) if en else (fr_code, fr_table)
    if en:
        return p('exemple-equipes', 'Rust API example: users, groups and foreign keys', 'Get started',
            'Connect User and Group in a Rust API: generate a SQL foreign key, preserve existing rows and add POST /members with Miblo CLI.', [
            ('depart', 'Start from a working API', '<p>Follow the <a href="premiere-api.html">Axum and SQLite tutorial</a> first, including the POST that creates Alice. Run the commands below inside <code>team-api</code>. This example uses a local SQLite database and Miblo 0.9.1 with templates 0.6.0.</p><p>We will link each user to an optional group. Miblo generates the Rust types, SQL migration and CRUD queries. It does not infer permissions or group membership rules.</p>'),
            ('relation', '1. Add Group and the foreign key', '<p>Stop the API with <kbd>Ctrl+C</kbd> in its terminal, or <kbd>s</kbd> if Miblo started it. Then run:</p>' + code(ADD_RELATION) + '<p><code>int?</code> makes the field optional; <code>ref=Group</code> points to <code>groups.id</code>. Existing users keep their IDs, names and emails; their new <code>group_id</code> starts as <code>NULL</code>. The migration adds the foreign key and its index.</p>' + table(['Table', 'Primary key', 'Relationship'], [('groups', '<code>id</code>', 'One group can be referenced by several users.'), ('users', '<code>id</code>', '<code>group_id → groups.id</code>, optional.')]) + '<p>This is a foreign-key relationship, not an embedded Group object in the JSON response. The default deletion rule is <code>RESTRICT</code>: unlink users before deleting their group. <a href="relations.html">Relationship options →</a></p>'),
            ('verifier', '2. Check that Alice is still there', '<p>Keep the API running. In a second terminal:</p>' + code('curl http://127.0.0.1:3000/users/1') + '<p>For Alice created as the first user in the tutorial, the response is:</p>' + code('{"id":1,"name":"Alice","email":"alice@example.com","group_id":null}', 'json') + '<p>No existing row was deleted or replaced. See <a href="migrations.html">model updates and migrations</a> for changes to your own project.</p>'),
            ('lier', '3. Create a group and assign it', code(LINK_USER) + '<p>The group POST returns <strong>201</strong>; the user PATCH returns <strong>200</strong> with <code>group_id: 1</code>. Replace both IDs with the actual returned values if you already have records. A reference to a missing group returns <strong>400</strong>.</p><p>In the interface, create Group with <kbd>a</kbd>, then edit User with <kbd>m</kbd> and choose the relation field. Apply the migration with <kbd>b</kbd>, restart the API, and inspect the schema with <kbd>d</kbd>. Use <kbd>x</kbd> to test either route with a form.</p>'),
            ('route', '4. Add POST /members using the User model', '<p>Stop the API again. This command adds an alternative creation endpoint using the existing User SQL code:</p>' + code(CUSTOM_ROUTE) + '<p>In the second terminal:</p>' + code(CREATE_MEMBER) + '<p>Expected result: <strong>HTTP 201</strong>. Bob is inserted into <code>users</code> and appears in <code>GET /users</code>; no <code>members</code> table is created. In the interface, press <kbd>g</kbd>, choose User and the create action, then set <code>/members</code>.</p><p><code>--action create</code> connects the route to generated SQL. Associating a model without an action only creates a function to implement. <a href="routes.html">Custom route options →</a></p>'),
            ('adapter', 'Where your own code belongs', '<p>Add group membership rules in <code>src/resources/user/service.rs</code>, and custom SQL or joins in <code>repository.rs</code>. Authentication, access control and deployment remain part of your application work. <a href="architecture.html">Read the generated code →</a></p><p>This walkthrough was executed against SQLite. Miblo also generates <a href="bases-de-donnees.html#mysql">MySQL projects</a>, which require a running database server and connection settings.</p>'),
        ])
    return p('exemple-equipes', 'Exemple d’API Rust : utilisateurs, groupes et relations', 'Démarrer',
        'Relier User et Group dans une API Rust : générer une clé étrangère SQL, conserver les données et ajouter POST /members avec Miblo CLI.', [
        ('depart', 'Partir d’une API fonctionnelle', '<p>Suivez d’abord le <a href="premiere-api.html">tutoriel Axum et SQLite</a>, jusqu’au POST qui crée Alice. Exécutez les commandes suivantes dans <code>team-api</code>. Cet exemple utilise SQLite en local, Miblo 0.9.1 et les templates 0.6.0.</p><p>Nous allons rattacher chaque utilisateur à un groupe facultatif. Miblo génère les types Rust, la migration SQL et les requêtes CRUD. Les droits et règles d’appartenance au groupe restent à écrire.</p>'),
        ('relation', '1. Ajouter Group et la clé étrangère', '<p>Arrêtez l’API avec <kbd>Ctrl+C</kbd> dans son terminal, ou <kbd>s</kbd> si Miblo l’a lancée. Exécutez ensuite :</p>' + code(ADD_RELATION) + '<p><code>int?</code> rend le champ facultatif ; <code>ref=Group</code> référence <code>groups.id</code>. Les utilisateurs existants conservent leurs identifiants, noms et e-mails ; leur nouveau <code>group_id</code> vaut <code>NULL</code>. La migration ajoute la clé étrangère et son index.</p>' + table(['Table', 'Clé primaire', 'Relation'], [('groups', '<code>id</code>', 'Un groupe peut être référencé par plusieurs utilisateurs.'), ('users', '<code>id</code>', '<code>group_id → groups.id</code>, facultatif.')]) + '<p>La relation est une clé étrangère : le JSON ne contient pas d’objet Group imbriqué. Par défaut, la suppression utilise <code>RESTRICT</code> : détachez les utilisateurs avant de supprimer leur groupe. <a href="relations.html">Options des relations →</a></p>'),
        ('verifier', '2. Vérifier qu’Alice est toujours présente', '<p>Laissez l’API tourner. Dans un second terminal :</p>' + code('curl http://127.0.0.1:3000/users/1') + '<p>Pour Alice créée comme premier utilisateur dans le tutoriel, la réponse est :</p>' + code('{"id":1,"name":"Alice","email":"alice@example.com","group_id":null}', 'json') + '<p>Aucune ligne existante n’a été supprimée ou remplacée. Consultez les <a href="migrations.html">modifications de modèles et migrations</a> pour faire évoluer votre propre projet.</p>'),
        ('lier', '3. Créer un groupe et l’attribuer', code(LINK_USER) + '<p>Le POST du groupe renvoie <strong>201</strong> ; le PATCH de l’utilisateur renvoie <strong>200</strong> avec <code>group_id: 1</code>. Remplacez les deux identifiants par les valeurs réellement reçues si votre base contient déjà des lignes. Une référence à un groupe inexistant renvoie <strong>400</strong>.</p><p>Dans l’interface, créez Group avec <kbd>a</kbd>, puis modifiez User avec <kbd>m</kbd> et choisissez un champ relation. Appliquez la migration avec <kbd>b</kbd>, redémarrez l’API et consultez le schéma avec <kbd>d</kbd>. La touche <kbd>x</kbd> permet de tester les routes avec un formulaire.</p>'),
        ('route', '4. Ajouter POST /members sur le modèle User', '<p>Arrêtez à nouveau l’API. Cette commande ajoute une autre URL de création qui utilise le code SQL existant de User :</p>' + code(CUSTOM_ROUTE) + '<p>Dans le second terminal :</p>' + code(CREATE_MEMBER) + '<p>Résultat attendu : <strong>HTTP 201</strong>. Bob est inséré dans <code>users</code> et apparaît dans <code>GET /users</code> ; aucune table <code>members</code> n’est créée. Dans l’interface, appuyez sur <kbd>g</kbd>, choisissez User et l’action de création, puis indiquez <code>/members</code>.</p><p><code>--action create</code> branche la route sur le SQL généré. Associer un modèle sans choisir d’action crée seulement une fonction à compléter. <a href="routes.html">Options des routes personnalisées →</a></p>'),
        ('adapter', 'Où ajouter votre code', '<p>Placez les règles d’appartenance aux groupes dans <code>src/resources/user/service.rs</code> et vos requêtes SQL ou jointures dans <code>repository.rs</code>. L’authentification, les droits d’accès et le déploiement restent à développer dans votre application. <a href="architecture.html">Lire le code généré →</a></p><p>Ce parcours a été exécuté avec SQLite. Miblo génère aussi des <a href="bases-de-donnees.html#mysql">projets MySQL</a>, qui nécessitent un serveur démarré et une connexion configurée.</p>'),
    ])
