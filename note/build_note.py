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


benefits = [
    ("Il gagne du temps",
     "Plus besoin de recopier les demandes : tout est déjà rempli dans le tableau. "
     "Estimation : environ 5 minutes gagnées par demande, soit près d'une heure par semaine pour deux demandes par jour."),
    ("Il n'oublie plus personne",
     "Chaque nouvelle demande lui arrive par email. Une liste « à rappeler aujourd'hui » l'attend sur son téléphone, "
     "même quand il est sur un chantier."),
    ("Il rappelle mieux",
     "Avant d'appeler, il a sous les yeux le nom, le téléphone, les travaux et le budget du client. "
     "Si le client a déjà écrit, il retrouve sa fiche : pas d'appel en double."),
    ("Un seul geste à faire",
     "Après son appel, il indique où en est le client (appelé, devis envoyé, gagné, perdu). "
     "Tout le reste est automatique."),
]
bcol = (W - LM - RM - 4 * mm) / 2


def benefit(head, text):
    return [Paragraph(head, card_t), Spacer(1, 1.5), Paragraph(text, card_b)]


grid = Table([[benefit(*benefits[0]), benefit(*benefits[1])], [benefit(*benefits[2]), benefit(*benefits[3])]],
             colWidths=[bcol + 2 * mm, bcol + 2 * mm])
grid.setStyle(TableStyle([
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("BACKGROUND", (0, 0), (-1, -1), SAGE),
    ("LINEBEFORE", (0, 0), (0, -1), 2.4, CORAL), ("LINEBEFORE", (1, 0), (1, -1), 2.4, CORAL),
    ("LINEBELOW", (0, 0), (-1, 0), 3, colors.white), ("LINEAFTER", (0, 0), (0, -1), 3, colors.white),
    ("LEFTPADDING", (0, 0), (-1, -1), 4 * mm), ("RIGHTPADDING", (0, 0), (-1, -1), 3.5 * mm),
    ("TOPPADDING", (0, 0), (-1, -1), 3 * mm), ("BOTTOMPADDING", (0, 0), (-1, -1), 3 * mm),
]))

how = Table([[Paragraph(
    "<b>Comment je m'y prends :</b> je lui montre l'outil sur une vraie demande (deux minutes), il l'essaie lui-même "
    "sur son téléphone (dix minutes), puis je reviens le voir au bout d'une semaine et de trois semaines "
    "pour corriger ce qui le gêne. Un outil qu'il aide à améliorer est un outil qu'il garde.", body)]],
    colWidths=[W - LM - RM])
how.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), PEACH),
                         ("LINEBEFORE", (0, 0), (0, -1), 2.4, CORAL),
                         ("LEFTPADDING", (0, 0), (-1, -1), 4 * mm), ("RIGHTPADDING", (0, 0), (-1, -1), 4 * mm),
                         ("TOPPADDING", (0, 0), (-1, -1), 2.8 * mm), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.8 * mm)]))

checks = [
    ("Aucun client n'est oublié",
     "Je compte les demandes reçues d'Habitat Presto et je vérifie qu'il y a une fiche pour chacune.",
     "chaque demande a sa fiche."),
    ("Les clients sont rappelés rapidement",
     "Je regarde combien de temps passe entre l'arrivée d'une demande et le premier appel du conducteur.",
     "le client est rappelé en moins d'une journée de travail."),
    ("Le conducteur utilise l'outil",
     "Je regarde s'il met lui-même à jour l'avancement de ses clients (appelé, devis envoyé, gagné, perdu).",
     "il le fait pour presque tous ses clients (9 sur 10) au bout de trois semaines."),
    ("L'outil rapporte des clients",
     "Je compte les devis envoyés et les ventes qui viennent de ces demandes.",
     "ces nombres augmentent de mois en mois."),
]
check_rows = []
for n, (head, what, ok) in enumerate(checks, 1):
    badge = Paragraph('<font color="white"><b>%d</b></font>' % n,
                      ParagraphStyle("nb", fontName="Man-ExtraBold", fontSize=10, leading=12, alignment=1))
    bt = Table([[badge]], colWidths=[7 * mm], rowHeights=[7 * mm])
    bt.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), GREEN), ("ROUNDEDCORNERS", [3.5 * mm] * 4),
                            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                            ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                            ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0)]))
    check_rows.append([bt, [Paragraph(head, card_t), Spacer(1, 1.5), Paragraph(what, card_b),
                            Spacer(1, 1.5),
                            Paragraph("<font color='#EE7766'><b>C'est réussi si :</b></font> " + ok, card_b)]])
t = Table(check_rows, colWidths=[13 * mm, W - LM - RM - 13 * mm])
t.setStyle(TableStyle([
    ("ROWBACKGROUNDS", (0, 0), (-1, -1), [SAGE, colors.white]),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("LINEBELOW", (0, 0), (-1, -1), 0.4, LINE),
    ("LEFTPADDING", (0, 0), (0, -1), 3.5 * mm), ("RIGHTPADDING", (0, 0), (0, -1), 0),
    ("LEFTPADDING", (1, 0), (1, -1), 1 * mm), ("RIGHTPADDING", (1, 0), (1, -1), 4 * mm),
    ("TOPPADDING", (0, 0), (-1, -1), 2.6 * mm), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.6 * mm),
]))

story = [
    Paragraph("SUIVI DES DEMANDES HABITAT PRESTO", kicker),
    Spacer(1, 1.5),
    Paragraph("Adoption et mesure du suivi des leads", title),
    Spacer(1, 4),
    Paragraph(
        "Chaque demande reçue d'Habitat Presto est rangée automatiquement dans un tableau de suivi, et notre conducteur "
        "de travaux en est prévenu par email. Même incomplète, une demande est gardée : <b>aucun client n'est perdu</b>.",
        lead),
    Paragraph("1. Comment je ferais adopter ce suivi par notre conducteur de travaux", h),
    Paragraph("Je ne lui demande pas de changer ses habitudes. Je lui montre ce que l'outil lui enlève comme travail.", body),
    Spacer(1, 3),
    grid,
    Spacer(1, 4),
    how,
    Paragraph("2. Comment je mesurerais que ça marche", h),
    Paragraph("Chaque semaine, je vérifie quatre choses simples dans le tableau de suivi.", body),
    Spacer(1, 3),
    t,
    Spacer(1, 4),
    Paragraph(
        "<b>Mon rythme :</b> dix minutes par semaine pour lire ces chiffres dans le tableau. "
        "Si l'un d'eux baisse, j'en parle d'abord avec le conducteur avant de changer quoi que ce soit.", body),
    Spacer(1, 5),
    Paragraph(
        "<b>À savoir :</b> l'outil a été testé avec des demandes fictives. Pour une vraie mise en service, il faudra "
        "une adresse email dédiée aux demandes et le vrai destinataire des alertes. Le gain de temps est une estimation, "
        "à confirmer avec le conducteur.", small),
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
