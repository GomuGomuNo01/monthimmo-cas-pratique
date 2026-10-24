from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

F = "C:/Windows/Fonts/"
pdfmetrics.registerFont(TTFont("Cal", F + "calibri.ttf"))
pdfmetrics.registerFont(TTFont("Cal-B", F + "calibrib.ttf"))
pdfmetrics.registerFontFamily("Cal", normal="Cal", bold="Cal-B", italic="Cal", boldItalic="Cal-B")

INK = colors.HexColor("#1f2933")
ACC = colors.HexColor("#1d4e89")
SOFT = colors.HexColor("#eef3f9")

title = ParagraphStyle("t", fontName="Cal-B", fontSize=15.5, leading=19, textColor=ACC)
sub = ParagraphStyle("s", fontName="Cal", fontSize=9.5, leading=12, textColor=colors.HexColor("#52606d"))
h = ParagraphStyle("h", fontName="Cal-B", fontSize=11.5, leading=14, textColor=ACC, spaceBefore=7, spaceAfter=3)
body = ParagraphStyle("b", fontName="Cal", fontSize=10, leading=13, textColor=INK, spaceAfter=3)
li = ParagraphStyle("l", parent=body, leftIndent=11, bulletIndent=1, spaceAfter=1.5)
cell = ParagraphStyle("c", fontName="Cal", fontSize=9.3, leading=11.5, textColor=INK)
cellb = ParagraphStyle("cb", parent=cell, fontName="Cal-B")


def bullets(items):
    return [Paragraph(i, li, bulletText="•") for i in items]


s = [
    Paragraph("Suivi des leads Habitat Presto : adoption et mesure", title),
    Paragraph("Cédric Kouadio, cas pratique alternance AI Builder, Month'immo, 24 octobre 2026", sub),
    Spacer(1, 4),
    Paragraph("<b>Ce que fait l'outil.</b> Chaque mail de lead arrivé dans la boîte Gmail dédiée est lu par n8n, puis par l'IA, qui en extrait le nom, le téléphone, "
              "l'email, la ville, les travaux, le budget et le délai. Le lead est rangé dans le tableau de suivi Airtable, "
              "un client déjà connu met à jour sa fiche au lieu d'en créer une seconde, et le conducteur de travaux reçoit "
              "une alerte par email. Si une information manque ou si l'IA ne répond pas, la ligne est créée en "
              "« À compléter » : <b>aucun lead n'est perdu</b>.", body),

    Paragraph("1. Faire adopter le suivi par le conducteur de travaux", h),
    *bullets([
        "<b>Partir de son quotidien.</b> Une demi-heure avec lui, sur place ou en visio, pour voir comment il reçoit et "
        "rappelle les leads aujourd'hui : souvent sur un chantier, avec son téléphone.",
        "<b>Ne lui demander qu'un seul geste.</b> Tout est rempli automatiquement ; lui change seulement le statut après "
        "chaque appel (Appelé, RDV pris, Devis envoyé, Gagné, Perdu).",
        "<b>Passer par ses outils.</b> L'alerte email contient de quoi rappeler le client sans ouvrir le tableau. La vue "
        "Airtable « À rappeler aujourd'hui » (relances du jour ou en retard, hors leads gagnés ou perdus) est déjà en place et se consulte sur l'application mobile.",
        "<b>Former en dix minutes</b>, avec une fiche d'une page et une vidéo de deux minutes à garder sous la main.",
        "<b>Revenir le voir à une semaine, puis à trois semaines</b> : vérifier qu'il s'en sert encore, noter ce qui le "
        "gêne et ajuster les statuts, les colonnes ou l'alerte. Un outil qui n'est plus utilisé est un outil à corriger.",
        "<b>Lui montrer son bénéfice</b> : plus de lead oublié, des relances faciles, l'historique de chaque client.",
    ]),

    Paragraph("2. Mesurer que ça marche (suivi chaque semaine, directement dans Airtable)", h),
]

rows = [
    ["Indicateur", "Comment le mesurer", "Objectif"],
    ["Taux de capture", "Leads dans le tableau, comparés aux leads reçus sur Habitat Presto", "100 %"],
    ["Rapidité du premier appel", "Écart entre la date de réception et le passage au statut « Appelé » (champ « Statut modifie le », rempli automatiquement à chaque changement de statut)", "Moins de 24 h ouvrées"],
    ["Leads en retard", "Leads encore « Nouveau » après leur date de relance", "0"],
    ["Fiches à compléter", "Lignes « À compléter » corrigées sous 48 h", "100 %"],
    ["Usage réel par le conducteur", "Part des leads dont il a lui-même changé le statut", "Plus de 90 % à trois semaines"],
    ["Résultat commercial", "Conversion lead, puis RDV, puis devis, puis gagné, mois après mois", "En progression"],
]
t = Table([[Paragraph(c, cellb if r == 0 else cell) for c in row] for r, row in enumerate(rows)],
          colWidths=[38 * mm, 98 * mm, 34 * mm])
t.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), SOFT),
    ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#c5d0dc")),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("TOPPADDING", (0, 0), (-1, -1), 2.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
]))
s += [t, Spacer(1, 3),
      Paragraph("Point de départ : aujourd'hui, un lead qui n'est pas saisi à la main n'existe nulle part. Chaque lead "
                "suivi est donc un gain mesurable dès la première semaine.", body),

      Paragraph("3. Limites et suite", h),
      *bullets([
          "Deux entrées possibles : la boîte Gmail (déclencheur IMAP sur les mails « Habitat Presto » non lus) et un "
          "formulaire de secours pour coller un lead à la main. En production, une adresse dédiée aux leads est préférable.",
          "Le doublon repose sur l'email et sur les neuf derniers chiffres du téléphone (numéros français).",
          "Données personnelles : accès au tableau réservé au conducteur et à la direction, clés stockées dans n8n, "
          "aucune donnée réelle utilisée pour ce test.",
          "Coût : modèle Claude Haiku, le plus économique, avec une température à zéro pour des réponses stables.",
          "Workflow construit uniquement avec des nœuds n8n, sans nœud de code : quelques formules simples suffisent, il peut être relu et modifié par quelqu'un qui n'est pas développeur.",
      ])]

doc = SimpleDocTemplate("Note_Adoption_Mesure_Cedric_Kouadio.pdf", pagesize=A4, leftMargin=20 * mm,
                        rightMargin=20 * mm, topMargin=15 * mm, bottomMargin=13 * mm,
                        title="Suivi des leads Habitat Presto : adoption et mesure", author="Cédric Kouadio")
doc.build(s)
print("ok")
