"""Génère la note d'une page : adoption par le conducteur de travaux et mesure des résultats.
Charte graphique Month'immo : vert #3C5B56, corail #EE7766, police Manrope, logo du site monthimmo.fr.
"""
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table,
                                TableStyle, KeepTogether)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics import renderPDF
from svglib.svglib import svg2rlg

HERE = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(HERE, "assets")
for name in ["Regular", "Medium", "SemiBold", "Bold", "ExtraBold"]:
    pdfmetrics.registerFont(TTFont("Man-" + name, os.path.join(A, "Manrope-%s.ttf" % name)))
pdfmetrics.registerFontFamily("Man-Regular", normal="Man-Regular", bold="Man-Bold",
                              italic="Man-Regular", boldItalic="Man-Bold")

GREEN = colors.HexColor("#3C5B56")
CORAL = colors.HexColor("#EE7766")
INK = colors.HexColor("#27332f")
GREY = colors.HexColor("#5d6b67")
SAGE = colors.HexColor("#eef2f1")
PEACH = colors.HexColor("#fdf0ed")
LINE = colors.HexColor("#d5dedb")

W, H = A4
LM = RM = 18 * mm

title = ParagraphStyle("t", fontName="Man-ExtraBold", fontSize=17, leading=21, textColor=GREEN)
kicker = ParagraphStyle("k", fontName="Man-SemiBold", fontSize=8.5, leading=11, textColor=CORAL)
lead = ParagraphStyle("l", fontName="Man-Regular", fontSize=9.6, leading=14, textColor=INK)
h = ParagraphStyle("h", fontName="Man-ExtraBold", fontSize=12.5, leading=16, textColor=GREEN,
                   spaceBefore=7, spaceAfter=4)
body = ParagraphStyle("b", fontName="Man-Regular", fontSize=9.2, leading=13, textColor=INK)
card_t = ParagraphStyle("ct", fontName="Man-Bold", fontSize=9.6, leading=12.5, textColor=GREEN)
card_b = ParagraphStyle("cb", fontName="Man-Regular", fontSize=8.7, leading=12, textColor=INK)
th = ParagraphStyle("th", fontName="Man-Bold", fontSize=8.6, leading=11, textColor=colors.white)
td = ParagraphStyle("td", fontName="Man-Regular", fontSize=8.7, leading=11.6, textColor=INK)
tdb = ParagraphStyle("tdb", parent=td, fontName="Man-Bold", textColor=GREEN)
tdc = ParagraphStyle("tdc", parent=td, fontName="Man-Bold", textColor=CORAL)
small = ParagraphStyle("s", fontName="Man-Regular", fontSize=7.8, leading=10.5, textColor=GREY)


def on_page(c, doc):
    # bandeau haut : logo à gauche, filet corail
    logo = svg2rlg(os.path.join(A, "logo.svg"))
    target_h = 17 * mm
    k = target_h / logo.height
    logo.scale(k, k)
    logo.width *= k
    logo.height *= k
    renderPDF.draw(logo, c, LM, H - 12 * mm - target_h)
    c.setFillColor(GREEN)
    c.setFont("Man-SemiBold", 8.2)
    c.drawRightString(W - RM, H - 17 * mm, "Cas pratique alternance IA Builder")
    c.setFillColor(GREY)
    c.setFont("Man-Regular", 8.2)
    c.drawRightString(W - RM, H - 21.5 * mm, "Cédric Kouadio, 24 octobre 2026")
    c.setStrokeColor(CORAL)
    c.setLineWidth(1.6)
    c.line(LM, H - 33 * mm, W - RM, H - 33 * mm)
    # pied de page
    c.setFillColor(GREEN)
    c.rect(0, 0, W, 8 * mm, stroke=0, fill=1)
    c.setFillColor(colors.white)
    c.setFont("Man-Medium", 7.6)
    c.drawString(LM, 3.1 * mm, "Month'immo  |  Votre investissement immobilier clé en main")
    c.drawRightString(W - RM, 3.1 * mm, "monthimmo.fr")


def step_card(num, head, text, w):
    badge = Table([[Paragraph('<font color="white"><b>%s</b></font>' % num,
                              ParagraphStyle("n", fontName="Man-ExtraBold", fontSize=10, leading=12,
                                             alignment=1))]],
                  colWidths=[7 * mm], rowHeights=[7 * mm])
    badge.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), CORAL),
                               ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                               ("ROUNDEDCORNERS", [3.5 * mm] * 4),
                               ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                               ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0)]))
    inner = Table([[badge, [Paragraph(head, card_t), Spacer(1, 1.5), Paragraph(text, card_b)]]],
                  colWidths=[9.5 * mm, w - 9.5 * mm - 7 * mm])
    inner.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                               ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                               ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0)]))
    return inner


steps = [
    ("1", "Je lui montre sur un vrai cas",
     "Pendant la présentation, il voit une demande arriver, sa fiche apparaître et l'alerte "
     "tomber sur son téléphone. Deux minutes, sans jargon."),
    ("2", "Je lui fais essayer lui-même",
     "Dix minutes sur son téléphone, avec une demande d'exemple : il rappelle le client "
     "et change son état. Je reste à côté."),
    ("3", "Je ne lui demande qu'un seul geste",
     "Tout le reste est automatique. Lui indique seulement où en est le client après chaque appel "
     "(appelé, devis, gagné, perdu)."),
    ("4", "L'outil vient à lui",
     "Chaque demande lui arrive par email, prête à rappeler. Une liste « à rappeler aujourd'hui » "
     "l'attend sur son téléphone."),
    ("5", "J'écoute ses remarques et je corrige vite",
     "À une semaine, je lui demande ce qui le gêne et j'ajuste l'outil (une information en plus dans "
     "l'alerte, par exemple). Il devient le sien."),
    ("6", "Je lui montre ses résultats",
     "À trois semaines, je lui présente ses chiffres : clients rappelés, délais, devis obtenus. "
     "Voir son travail progresser donne envie de continuer."),
]

gain_items = [
    ("Plus aucun client oublié", "Chaque demande est classée et rappelée à sa date."),
    ("Moins de saisie", "Les informations du client sont déjà remplies : nom, téléphone, travaux, budget."),
    ("Son travail devient visible", "L'historique de chaque client est au même endroit, utile pour les devis et pour la direction."),
]
gcol = (W - LM - RM) / 3
gcells = [[Paragraph(a, card_t), Paragraph(b, card_b)] for a, b in gain_items]
gains = Table([[gcells[0], gcells[1], gcells[2]]], colWidths=[gcol] * 3)
gains.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, -1), PEACH),
    ("LINEBEFORE", (0, 0), (0, 0), 2.2, CORAL), ("LINEBEFORE", (1, 0), (2, 0), 0.6, colors.white),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("LEFTPADDING", (0, 0), (-1, -1), 3.5 * mm), ("RIGHTPADDING", (0, 0), (-1, -1), 3 * mm),
    ("TOPPADDING", (0, 0), (-1, -1), 2.4 * mm), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.6 * mm),
]))

col_w = (W - LM - RM - 6 * mm) / 2
cells = [step_card(n, t, x, col_w) for n, t, x in steps]
grid = Table([[cells[0], cells[1]], [cells[2], cells[3]], [cells[4], cells[5]]],
             colWidths=[col_w + 3 * mm, col_w + 3 * mm])
grid.setStyle(TableStyle([
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("BACKGROUND", (0, 0), (-1, -1), SAGE),
    ("LINEBELOW", (0, 0), (-1, 1), 3, colors.white),
    ("LINEAFTER", (0, 0), (0, -1), 3, colors.white),
    ("LEFTPADDING", (0, 0), (-1, -1), 4 * mm), ("RIGHTPADDING", (0, 0), (-1, -1), 2 * mm),
    ("TOPPADDING", (0, 0), (-1, -1), 2.3 * mm), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.3 * mm),
]))

rows = [
    ["Ce que je veux savoir", "Comment je le vois", "Objectif"],
    ["Aucune demande n'est perdue ?",
     "Je compare les clients du tableau aux demandes reçues sur Habitat Presto.", "100 %"],
    ["Les clients sont rappelés vite ?",
     "Le tableau note l'heure à laquelle il change l'état d'un client : j'en déduis le délai avant le premier appel.", "Moins de 24 h ouvrées"],
    ["Y a-t-il des oublis ?",
     "Je compte les clients encore « nouveaux » après leur date de rappel.", "Zéro"],
    ["Les fiches incomplètes sont corrigées ?",
     "Je regarde combien de fiches « à compléter » sont terminées sous 48 heures.", "100 %"],
    ["Le conducteur s'en sert vraiment ?",
     "Je compte la part des clients dont il met lui-même l'état à jour.", "Plus de 90 % à trois semaines"],
]
tdata = []
for i, r in enumerate(rows):
    if i == 0:
        tdata.append([Paragraph(c, th) for c in r])
    else:
        tdata.append([Paragraph(r[0], tdb), Paragraph(r[1], td), Paragraph(r[2], tdc)])
t = Table(tdata, colWidths=[44 * mm, 90 * mm, W - LM - RM - 134 * mm], repeatRows=1)
t.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), GREEN),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, SAGE]),
    ("LINEBELOW", (0, 0), (-1, -1), 0.4, LINE),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("LEFTPADDING", (0, 0), (-1, -1), 3 * mm), ("RIGHTPADDING", (0, 0), (-1, -1), 2.5 * mm),
    ("TOPPADDING", (0, 0), (-1, -1), 1.5 * mm), ("BOTTOMPADDING", (0, 0), (-1, -1), 1.5 * mm),
]))

rhythm = Table([[Paragraph(
    "<b>Mon rythme :</b> dix minutes par semaine pour lire ces chiffres dans le tableau. "
    "Si l'un baisse, j'en parle d'abord avec le conducteur avant de changer quoi que ce soit.", body)]],
    colWidths=[W - LM - RM])
rhythm.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), PEACH),
                            ("LINEBEFORE", (0, 0), (0, -1), 2.2, CORAL),
                            ("LEFTPADDING", (0, 0), (-1, -1), 4 * mm), ("RIGHTPADDING", (0, 0), (-1, -1), 4 * mm),
                            ("TOPPADDING", (0, 0), (-1, -1), 2.6 * mm), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.6 * mm)]))

story = [
    Paragraph("SUIVI DES DEMANDES HABITAT PRESTO", kicker),
    Spacer(1, 1.5),
    Paragraph("Faire adopter l'outil par le conducteur de travaux, et mesurer qu'il fonctionne", title),
    Spacer(1, 4),
    Paragraph(
        "<b>L'outil en une phrase :</b> chaque demande reçue d'Habitat Presto est rangée automatiquement dans un tableau "
        "de suivi, et le conducteur de travaux en est prévenu par email. Si une demande est incomplète, elle est "
        "gardée quand même, marquée « à compléter » : <b>aucun client n'est perdu</b>.", lead),
    Paragraph("1. Ce que le conducteur de travaux y gagne", h),
    gains,
    Paragraph("2. Comment je l'accompagne après la présentation", h),
    grid,
    Paragraph("3. Comment je mesure que ça marche", h),
    t,
    Spacer(1, 3),
    rhythm,
    Spacer(1, 2),
    Paragraph(
        "<b>À savoir :</b> l'outil a été testé avec des demandes fictives. Pour une vraie mise en service, il faudra "
        "une adresse email dédiée aux demandes et le vrai destinataire des alertes.", small),
]

doc = BaseDocTemplate(os.path.join(HERE, "Note_Adoption_Mesure_Cedric_Kouadio.pdf"), pagesize=A4,
                      leftMargin=LM, rightMargin=RM, topMargin=36 * mm, bottomMargin=12 * mm,
                      title="Faire adopter le suivi des demandes Habitat Presto et mesurer les résultats",
                      author="Cédric Kouadio")
frame = Frame(LM, 12 * mm, W - LM - RM, H - 37 * mm - 12 * mm, leftPadding=0, rightPadding=0,
              topPadding=0, bottomPadding=0)
doc.addPageTemplates([PageTemplate(id="p", frames=[frame], onPage=on_page)])
doc.build(story)
print("ok")
