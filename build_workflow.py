"""Génère le workflow n8n « Leads Habitat Presto » (100 % nœuds natifs n8n).

Le JSON produit se colle dans l'éditeur n8n (Ctrl+V) ou s'importe via « Import from file ».
Aucune clé ni aucun mot de passe n'y figure : seuls les identifiants internes des credentials n8n.
"""
import json
import uuid

BASE_ID = "appreB902fRBB9HtK"   # base Airtable « MonthImmo Leads »
TABLE_ID = "tblgYtq4tIGgQmYmm"  # table « Leads »
CRED_ANTHROPIC = {"id": "VJRmhHJ901VZlrKp", "name": "Anthropic account"}
CRED_AIRTABLE = {"id": "1nhMnE206MqmQT19", "name": "Airtable Personal Access Token account"}
CRED_SMTP = {"id": "ShVQBg96K7vqmxbQ", "name": "SMTP account"}
MAIL_FROM = "leads@monthimmo-demo.fr"
MAIL_TO = "conducteur.travaux@monthimmo-demo.fr"

TEXT_FIELDS = ["Nom", "Telephone", "Email", "Ville", "Type de travaux", "Delai", "Statut",
               "Responsable", "Date reception", "Date de relance", "Commentaire", "Source"]
NUM_FIELDS = ["Budget min", "Budget max", "Nb contacts"]


def uid():
    return str(uuid.uuid4())


def col(name, typ="string", read_only=False, match=False):
    return {"id": name, "displayName": name, "required": False, "defaultMatch": match,
            "canBeUsedToMatch": True, "display": True, "type": typ, "readOnly": read_only,
            "removed": False}


def airtable_record(op, values, schema, matching=None):
    return {
        "operation": op,
        "base": {"__rl": True, "mode": "id", "value": BASE_ID},
        "table": {"__rl": True, "mode": "id", "value": TABLE_ID},
        "columns": {"mappingMode": "defineBelow", "value": values,
                    "matchingColumns": matching or [], "schema": schema,
                    "attemptToConvertTypes": False, "convertFieldsToString": False},
        "options": {"typecast": True},
    }


def assign(name, value, typ="string"):
    return {"id": uid(), "name": name, "value": value, "type": typ}


# ---------------------------------------------------------------- expressions
O = "$json.output"
TEL_DIGITS = f"String({O}.telephone || '').replace(/\\D/g, '').slice(-9)"
PREP = "$('Préparer le lead').first().json"
FULL_SCHEMA = [col(n) for n in TEXT_FIELDS] + [col(n, "number") for n in NUM_FIELDS]

prepare_assignments = [
    assign("Nom", f"={{{{ {O}.nom || '' }}}}"),
    assign("Telephone", f"={{{{ {TEL_DIGITS}.length === 9 ? '+33' + {TEL_DIGITS} : '' }}}}"),
    assign("Email", f"={{{{ String({O}.email || '').trim().toLowerCase() }}}}"),
    assign("Ville", f"={{{{ {O}.ville || '' }}}}"),
    assign("Type de travaux", f"={{{{ {O}.type_travaux || '' }}}}"),
    assign("Budget min", f"={{{{ {O}.budget_min ?? null }}}}", "number"),
    assign("Budget max", f"={{{{ {O}.budget_max ?? {O}.budget_min ?? null }}}}", "number"),
    assign("Delai", f"={{{{ {O}.delai || '' }}}}"),
    assign("Statut", f"={{{{ {O}.nom && ({O}.email || {TEL_DIGITS}.length === 9) ? 'Nouveau' : 'À compléter' }}}}"),
    assign("Responsable", "Conducteur de travaux"),
    assign("Date reception", "={{ $now.toFormat('yyyy-MM-dd') }}"),
    assign("Date de relance", "={{ $now.plus({ days: 2 }).toFormat('yyyy-MM-dd') }}"),
    assign("Commentaire", f"={{{{ {O}.nom && ({O}.email || {TEL_DIGITS}.length === 9) ? 'Lead créé automatiquement depuis Habitat Presto.' : 'À compléter : ' + [!{O}.nom && 'nom', !({O}.email || {TEL_DIGITS}.length === 9) && 'téléphone ou email'].filter(Boolean).join(', ') + '. Vérifier le mail d\\'origine.' }}}}"),
    assign("Source", "Habitat Presto"),
    assign("Cle email", f"={{{{ String({O}.email || '').trim().toLowerCase().replace(/'/g, '') }}}}"),
    assign("Cle telephone", f"={{{{ {TEL_DIGITS}.length === 9 ? {TEL_DIGITS} : '' }}}}"),
]

FORMULA = ("={{ $json['Cle email'] && $json['Cle telephone'] "
           "? \"OR(LOWER({Email})='\" + $json['Cle email'] + \"', RIGHT({Telephone}, 9)='\" + $json['Cle telephone'] + \"')\" "
           ": $json['Cle email'] ? \"LOWER({Email})='\" + $json['Cle email'] + \"'\" "
           ": $json['Cle telephone'] ? \"RIGHT({Telephone}, 9)='\" + $json['Cle telephone'] + \"'\" "
           ": 'FALSE()' }}")

create_values = {n: f"={{{{ {PREP}['{n}'] }}}}" for n in TEXT_FIELDS + ["Budget min", "Budget max"]}
create_values["Nb contacts"] = "={{ 1 }}"

update_values = {
    "id": "={{ $json.id }}",
    "Commentaire": "={{ ($json.Commentaire ? $json.Commentaire + ' | ' : '') + 'Nouveau contact le ' + $now.toFormat('dd/MM/yyyy') + ' via Habitat Presto (doublon détecté automatiquement).' }}",
    "Nb contacts": "={{ ($json['Nb contacts'] || 1) + 1 }}",
    "Date de relance": "={{ $now.plus({ days: 1 }).toFormat('yyyy-MM-dd') }}",
}
update_schema = [col("id", read_only=True, match=True), col("Commentaire"), col("Date de relance"),
                 col("Nb contacts", "number")]

error_values = {
    "Nom": "À identifier",
    "Statut": "À compléter",
    "Responsable": "Conducteur de travaux",
    "Source": "Habitat Presto",
    "Date reception": "={{ $now.toFormat('yyyy-MM-dd') }}",
    "Date de relance": "={{ $now.plus({ days: 1 }).toFormat('yyyy-MM-dd') }}",
    "Commentaire": "={{ 'Extraction par IA impossible, lead à saisir à la main. Mail reçu : ' + $('Formulaire lead').first().json['Mail du lead'] }}",
    "Nb contacts": "={{ 1 }}",
}

lead_body = (
    "={{ 'Bonjour,\\n\\nUn nouveau lead Habitat Presto vient d\\'être enregistré dans le tableau de suivi.\\n\\n'"
    f" + 'Statut : ' + {PREP}.Statut + '\\n'"
    f" + 'Client : ' + ({PREP}.Nom || 'non renseigné') + '\\n'"
    f" + 'Téléphone : ' + ({PREP}.Telephone || 'non renseigné') + '\\n'"
    f" + 'Email : ' + ({PREP}.Email || 'non renseigné') + '\\n'"
    f" + 'Ville : ' + ({PREP}.Ville || 'non renseignée') + '\\n'"
    f" + 'Travaux : ' + ({PREP}['Type de travaux'] || 'non renseignés') + '\\n'"
    f" + 'Budget : ' + ({PREP}['Budget min'] ? {PREP}['Budget min'] + ' à ' + {PREP}['Budget max'] + ' EUR' : 'non précisé') + '\\n'"
    f" + 'Délai : ' + ({PREP}.Delai || 'non précisé') + '\\n\\n'"
    f" + ({PREP}.Statut === 'À compléter' ? 'Attention : ' + {PREP}.Commentaire + '\\n\\n' : '')"
    f" + 'À rappeler au plus tard le ' + {PREP}['Date de relance'] + '.\\n' }}}}"
)
dup_body = (
    "={{ 'Bonjour,\\n\\nCe client a déjà une fiche dans le tableau de suivi : aucune nouvelle ligne n\\'a été créée.\\n\\n'"
    f" + 'Client : ' + ({PREP}.Nom || 'non renseigné') + '\\n'"
    f" + 'Téléphone : ' + ({PREP}.Telephone || 'non renseigné') + '\\n'"
    f" + 'Email : ' + ({PREP}.Email || 'non renseigné') + '\\n'"
    f" + 'Nouvelle demande : ' + ({PREP}['Type de travaux'] || 'non précisée') + '\\n\\n'"
    " + 'La fiche existante a été mise à jour (commentaire et nombre de contacts). Pensez à le rappeler.\\n' }}"
)
err_body = ("={{ 'Bonjour,\\n\\nUn mail de lead n\\'a pas pu être analysé automatiquement. "
            "Une ligne « À compléter » a été créée dans le tableau de suivi.\\n\\nMail reçu :\\n' "
            "+ $('Formulaire lead').first().json['Mail du lead'] }}")

SYSTEM_PROMPT = (
    "Tu extrais les informations d'un mail de demande de travaux reçu d'une plateforme de mise en relation. "
    "Règles : n'invente jamais une information ; si elle n'apparaît pas dans le texte, laisse le champ vide. "
    "Ignore les formules de politesse, les signatures et les liens de désinscription. "
    "Les montants sont des nombres entiers en euros, sans espace ni symbole."
)

ATTRS = [
    ("nom", "string", "Nom du client tel qu'écrit dans le mail, avec la civilité si présente (ex : Mme Claire D.)."),
    ("telephone", "string", "Numéro de téléphone du client au format international sans espace, ex : 06 12 34 56 78 devient +33612345678."),
    ("email", "string", "Adresse email du client, en minuscules."),
    ("ville", "string", "Ville du chantier, sans code postal ni numéro de département."),
    ("type_travaux", "string", "Description courte des travaux demandés, en français."),
    ("budget_min", "number", "Budget minimum en euros. Si un seul montant est donné, mettre ce montant."),
    ("budget_max", "number", "Budget maximum en euros. Si un seul montant est donné, mettre ce même montant."),
    ("delai", "string", "Délai de démarrage souhaité, tel qu'exprimé dans le mail (ex : sous 3 mois)."),
]


def node(name, typ, version, pos, params, **extra):
    n = {"parameters": params, "id": uid(), "name": name, "type": typ, "typeVersion": version,
         "position": pos}
    n.update(extra)
    return n


def email_node(name, pos, subject, body):
    return node(name, "n8n-nodes-base.emailSend", 2.1, pos, {
        "fromEmail": MAIL_FROM, "toEmail": MAIL_TO, "subject": subject,
        "emailFormat": "text", "text": body, "options": {"appendAttribution": False},
    }, credentials={"smtp": CRED_SMTP})


def sticky(text, pos, w, h, color):
    return node(f"Note {uid()[:6]}", "n8n-nodes-base.stickyNote", 1, pos,
                {"content": text, "height": h, "width": w, "color": color})


nodes = [
    sticky("## 1. Réception du lead\nLe mail Habitat Presto est collé dans le formulaire (en production : déclencheur Gmail ou IMAP).", [-560, -260], 300, 420, 7),
    sticky("## 2. Extraction par l'IA\nClaude Haiku extrait nom, téléphone, email, ville, travaux, budget et délai. Température 0, rien n'est inventé. Deux essais, puis sortie d'erreur.", [-240, -260], 440, 560, 5),
    sticky("## 3. Règles métier et doublon\nStatut, dates de relance et clé de doublon (email en minuscules, 9 derniers chiffres du téléphone).", [220, -260], 640, 420, 6),
    sticky("## 4. Tableau de suivi et alerte\nNouveau lead : création de la ligne. Doublon : mise à jour de la fiche existante. Le conducteur reçoit un email dans tous les cas.", [880, -400], 500, 640, 4),
    sticky("## Cas d'erreur\nSi l'IA ne répond pas, le lead n'est pas perdu : ligne « À compléter » avec le mail brut, et alerte.", [220, 200], 1160, 300, 3),
    node("Formulaire lead", "n8n-nodes-base.formTrigger", 2.3, [-480, 0], {
        "formTitle": "Nouveau lead Habitat Presto",
        "formDescription": "Collez ici le texte du mail reçu de la plateforme Habitat Presto.",
        "formFields": {"values": [{"fieldLabel": "Mail du lead", "fieldType": "textarea",
                                   "requiredField": True}]},
        "options": {},
    }, webhookId=uid()),
    node("Extraction IA", "@n8n/n8n-nodes-langchain.informationExtractor", 1.2, [-180, 0], {
        "text": "={{ $json['Mail du lead'] }}",
        "schemaType": "fromAttributes",
        "attributes": {"attributes": [{"name": n, "type": t, "description": d, "required": False}
                                      for n, t, d in ATTRS]},
        "options": {"systemPromptTemplate": SYSTEM_PROMPT},
    }, retryOnFail=True, maxTries=2, onError="continueErrorOutput"),
    node("Claude Haiku", "@n8n/n8n-nodes-langchain.lmChatAnthropic", 1.6, [-180, 200], {
        "model": {"__rl": True, "mode": "id", "value": "claude-haiku-5-5"},
        "options": {"temperature": 0, "maxTokensToSample": 600},
    }, credentials={"anthropicApi": CRED_ANTHROPIC}),
    node("Préparer le lead", "n8n-nodes-base.set", 3.4, [260, -100], {
        "mode": "manual", "assignments": {"assignments": prepare_assignments},
        "options": {"ignoreConversionErrors": True},
    }),
    node("Chercher un doublon", "n8n-nodes-base.airtable", 2.1, [480, -100], {
        "operation": "search",
        "base": {"__rl": True, "mode": "id", "value": BASE_ID},
        "table": {"__rl": True, "mode": "id", "value": TABLE_ID},
        "filterByFormula": FORMULA, "returnAll": False, "limit": 1, "options": {},
    }, alwaysOutputData=True, credentials={"airtableTokenApi": CRED_AIRTABLE}),
    node("Doublon ?", "n8n-nodes-base.if", 2.2, [700, -100], {
        "conditions": {
            "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "loose", "version": 2},
            "conditions": [{"id": uid(), "leftValue": "={{ $json.id }}", "rightValue": "",
                            "operator": {"type": "string", "operation": "exists", "singleValue": True}}],
            "combinator": "and",
        },
        "options": {},
    }),
    node("Mettre à jour la fiche", "n8n-nodes-base.airtable", 2.1, [940, -240],
         airtable_record("update", update_values, update_schema, ["id"]),
         credentials={"airtableTokenApi": CRED_AIRTABLE}),
    node("Créer le lead", "n8n-nodes-base.airtable", 2.1, [940, 20],
         airtable_record("create", create_values, FULL_SCHEMA),
         credentials={"airtableTokenApi": CRED_AIRTABLE}),
    email_node("Alerte doublon", [1180, -240],
               f"={{{{ '[Doublon] ' + ({PREP}.Nom || 'Client') + ' - ' + ({PREP}.Ville || 'ville inconnue') }}}}",
               dup_body),
    email_node("Alerte nouveau lead", [1180, 20],
               f"={{{{ '[' + ({PREP}.Statut === 'Nouveau' ? 'Nouveau lead' : 'À compléter') + '] ' + ({PREP}.Nom || 'Lead sans nom') + ' - ' + ({PREP}.Ville || 'ville inconnue') }}}}",
               lead_body),
    node("Créer le lead (sans IA)", "n8n-nodes-base.airtable", 2.1, [480, 320],
         airtable_record("create", error_values, FULL_SCHEMA),
         credentials={"airtableTokenApi": CRED_AIRTABLE}),
    email_node("Alerte erreur IA", [940, 320], "[À compléter] Lead à saisir à la main", err_body),
]

connections = {
    "Formulaire lead": {"main": [[{"node": "Extraction IA", "type": "main", "index": 0}]]},
    "Claude Haiku": {"ai_languageModel": [[{"node": "Extraction IA", "type": "ai_languageModel", "index": 0}]]},
    "Extraction IA": {"main": [[{"node": "Préparer le lead", "type": "main", "index": 0}],
                               [{"node": "Créer le lead (sans IA)", "type": "main", "index": 0}]]},
    "Préparer le lead": {"main": [[{"node": "Chercher un doublon", "type": "main", "index": 0}]]},
    "Chercher un doublon": {"main": [[{"node": "Doublon ?", "type": "main", "index": 0}]]},
    "Doublon ?": {"main": [[{"node": "Mettre à jour la fiche", "type": "main", "index": 0}],
                           [{"node": "Créer le lead", "type": "main", "index": 0}]]},
    "Mettre à jour la fiche": {"main": [[{"node": "Alerte doublon", "type": "main", "index": 0}]]},
    "Créer le lead": {"main": [[{"node": "Alerte nouveau lead", "type": "main", "index": 0}]]},
    "Créer le lead (sans IA)": {"main": [[{"node": "Alerte erreur IA", "type": "main", "index": 0}]]},
}

workflow = {"name": "Leads Habitat Presto vers tableau de suivi", "nodes": nodes,
            "connections": connections,
            "settings": {"executionOrder": "v1", "timezone": "Europe/Paris"}}

if __name__ == "__main__":
    out = "MonthImmo_CasPratique/workflow/Leads_HabitatPresto_source.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(workflow, f, ensure_ascii=False, indent=2)
    print("ecrit", out, len(nodes), "noeuds")
