import io
import re
import unicodedata
from datetime import date, datetime

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


# ============================================================
# CONFIGURAÇÃO
# ============================================================

st.set_page_config(
    page_title="CTR DEFENSE | Consultoria Profissional",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# ESTILO
# ============================================================

st.markdown(
    """
    <style>
        :root {
            --ctr-primary: #0787a6;
            --ctr-secondary: #102f3b;
            --ctr-accent: #20b5d6;
            --ctr-background: #dcebef;
            --ctr-surface: #edf6f8;
            --ctr-card: #ffffff;
            --ctr-border: #b7d2da;
            --ctr-text: #102f3b;
            --ctr-muted: #54717b;
        }

        html,
        body,
        [data-testid="stAppViewContainer"],
        .stApp {
            background:
                radial-gradient(
                    circle at 85% 8%,
                    rgba(32, 181, 214, 0.18),
                    transparent 28%
                ),
                linear-gradient(
                    145deg,
                    #d5e7ec 0%,
                    #eaf4f7 48%,
                    #cddfe5 100%
                ) !important;
            color: var(--ctr-text);
        }

        [data-testid="stHeader"] {
            background-color: rgba(213, 231, 236, 0.84);
            backdrop-filter: blur(8px);
        }

        [data-testid="stMainBlockContainer"] {
            padding-top: 2rem;
        }

        h1, h2, h3, h4, p, label {
            color: var(--ctr-text);
        }

        [data-testid="stSidebar"] {
            background:
                linear-gradient(
                    180deg,
                    #0b2631 0%,
                    #103b49 55%,
                    #075d72 100%
                );
            border-right: 1px solid rgba(255, 255, 255, 0.12);
        }

        [data-testid="stSidebar"] * {
            color: #ffffff !important;
        }

        [data-testid="stSidebar"] input {
            color: #102f3b !important;
            background-color: #ffffff !important;
        }

        .ctr-header {
            padding: 27px;
            border-radius: 17px;
            background:
                linear-gradient(
                    120deg,
                    #102f3b 0%,
                    #075f74 54%,
                    #0795b7 100%
                );
            margin-bottom: 22px;
            box-shadow: 0 12px 28px rgba(16, 47, 59, 0.24);
        }

        .ctr-header h1,
        .ctr-header p {
            color: #ffffff !important;
            margin: 0;
        }

        .ctr-header p {
            margin-top: 8px;
            opacity: 0.92;
        }

        .organization-card {
            background:
                linear-gradient(
                    135deg,
                    rgba(7, 135, 166, 0.16),
                    rgba(255, 255, 255, 0.90)
                );
            border: 1px solid #91c1cd;
            border-left: 6px solid #0787a6;
            border-radius: 14px;
            padding: 17px 19px;
            margin-bottom: 19px;
            box-shadow: 0 6px 16px rgba(16, 47, 59, 0.10);
        }

        .question-card {
            background:
                linear-gradient(
                    145deg,
                    rgba(255, 255, 255, 0.98),
                    rgba(237, 247, 249, 0.98)
                );
            border: 1px solid #b7d2da;
            border-left: 5px solid #0787a6;
            border-radius: 12px;
            padding: 15px;
            margin: 12px 0 7px;
            box-shadow: 0 5px 14px rgba(16, 47, 59, 0.08);
        }

        [data-testid="stMetric"] {
            background:
                linear-gradient(
                    145deg,
                    rgba(255, 255, 255, 0.98),
                    rgba(230, 243, 247, 0.98)
                );
            border: 1px solid #a9cbd4;
            border-top: 4px solid #0787a6;
            border-radius: 14px;
            padding: 17px;
            box-shadow: 0 7px 18px rgba(16, 47, 59, 0.11);
        }

        [data-testid="stMetricValue"] {
            color: #075f74 !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"] {
            background-color: rgba(244, 250, 252, 0.74);
            border-color: #a9cbd4 !important;
            border-radius: 14px;
        }

        div[data-testid="stTextInput"] input,
        div[data-testid="stNumberInput"] input,
        div[data-testid="stDateInput"] input,
        div[data-testid="stTextArea"] textarea {
            background-color: #ffffff !important;
            color: #102f3b !important;
            border: 1px solid #9fbfc8 !important;
        }

        div[data-baseweb="select"] > div {
            background-color: #ffffff !important;
            color: #102f3b !important;
        }

        div[role="listbox"],
        div[role="option"] {
            background-color: #ffffff !important;
            color: #102f3b !important;
        }

        div[data-testid="stDataFrame"],
        div[data-testid="stPlotlyChart"] {
            background-color: rgba(247, 252, 253, 0.82);
            border: 1px solid #adcbd3;
            border-radius: 14px;
            padding: 8px;
            box-shadow: 0 5px 16px rgba(16, 47, 59, 0.09);
        }

        .warning-box {
            background: #fff3e0;
            border: 1px solid #ffd19a;
            border-left: 5px solid #ef6c00;
            border-radius: 10px;
            padding: 14px;
            margin-bottom: 10px;
            color: #563100;
        }

        .ctr-footer {
            text-align: center;
            color: #3f626d;
            font-size: 0.84rem;
            padding: 28px 8px 12px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# CONSTANTES
# ============================================================

DIMENSOES = [
    "Governar",
    "Identificar",
    "Proteger",
    "Detectar",
    "Responder",
    "Recuperar",
]

PERGUNTAS_NIST = {
    "Governar": [
        "Existe uma política formal de segurança da informação?",
        "Papéis e responsabilidades de segurança estão definidos?",
        "Riscos cibernéticos são reportados à liderança?",
        "Fornecedores são avaliados quanto à segurança?",
    ],
    "Identificar": [
        "A organização mantém inventário atualizado de ativos?",
        "Os dados críticos estão identificados e classificados?",
        "Existe processo formal de avaliação de riscos?",
        "Vulnerabilidades são identificadas periodicamente?",
    ],
    "Proteger": [
        "A autenticação multifator é utilizada em acessos críticos?",
        "Privilégios administrativos são controlados e revisados?",
        "Existe programa contínuo de conscientização?",
        "Backups são protegidos contra alteração ou exclusão?",
    ],
    "Detectar": [
        "Logs de segurança são coletados e centralizados?",
        "Há monitoramento contínuo de eventos suspeitos?",
        "Alertas possuem critérios de priorização?",
        "A organização realiza testes de detecção?",
    ],
    "Responder": [
        "Existe plano documentado de resposta a incidentes?",
        "Os responsáveis por incidentes são definidos?",
        "Existe procedimento de comunicação de incidentes?",
        "São realizados exercícios ou simulações periódicas?",
    ],
    "Recuperar": [
        "Existe plano de recuperação de desastres?",
        "Backups são testados periodicamente?",
        "Objetivos de recuperação RTO e RPO estão definidos?",
        "Lições aprendidas são incorporadas após incidentes?",
    ],
}

OPCOES_MATURIDADE = {
    "Não implementado": 0,
    "Inicial / informal": 1,
    "Parcialmente implementado": 2,
    "Implementado": 3,
    "Gerenciado e medido": 4,
    "Otimizado": 5,
}

FRAMEWORKS = {
    "NIST CSF 2.0": [
        "Governança de riscos cibernéticos",
        "Inventário e classificação de ativos",
        "Proteção de identidades e acessos",
        "Monitoramento e detecção",
        "Resposta a incidentes",
        "Recuperação e continuidade",
    ],
    "ISO 27001:2022": [
        "Contexto da organização",
        "Liderança e política de segurança",
        "Planejamento e tratamento de riscos",
        "Competência e conscientização",
        "Controles organizacionais e tecnológicos",
        "Auditoria e melhoria contínua",
    ],
    "LGPD": [
        "Mapeamento de dados pessoais",
        "Bases legais de tratamento",
        "Direitos dos titulares",
        "Gestão de operadores e terceiros",
        "Resposta a incidentes com dados pessoais",
        "Governança e registro das operações",
    ],
}

STATUS_ACAO = [
    "Não iniciado",
    "Em andamento",
    "Bloqueado",
    "Concluído",
]


# ============================================================
# DATAFRAMES E ESTADO
# ============================================================

def dataframe_riscos():
    return pd.DataFrame(
        columns=[
            "ID",
            "Risco",
            "Categoria",
            "Probabilidade",
            "Impacto",
            "Nível",
            "Responsável",
            "Tratamento",
            "Status",
        ]
    )


def dataframe_acoes():
    return pd.DataFrame(
        columns=[
            "ID",
            "Ação",
            "Origem",
            "Prioridade",
            "Responsável",
            "Início",
            "Prazo",
            "Status",
            "Progresso",
        ]
    )


def dataframe_reunioes():
    return pd.DataFrame(
        columns=[
            "Data",
            "Título",
            "Participantes",
            "Resumo",
            "Decisões",
            "Próximos passos",
        ]
    )


def criar_dados_organizacao():
    return {
        "assessment": {},
        "compliance": {},
        "riscos": dataframe_riscos(),
        "acoes": dataframe_acoes(),
        "reunioes": dataframe_reunioes(),
    }


def inicializar_estado():
    if "organizacoes" not in st.session_state:
        st.session_state.organizacoes = {}

    if "organizacao_ativa" not in st.session_state:
        st.session_state.organizacao_ativa = None

    if "consultor" not in st.session_state:
        st.session_state.consultor = ""


def gerar_id_organizacao():
    if not st.session_state.organizacoes:
        return 1
    return max(st.session_state.organizacoes.keys()) + 1


def cadastrar_organizacao(
    razao_social,
    nome_fantasia,
    documento,
    setor,
    porte,
    responsavel,
    email,
):
    organizacao_id = gerar_id_organizacao()

    st.session_state.organizacoes[organizacao_id] = {
        "id": organizacao_id,
        "razao_social": razao_social.strip(),
        "nome_fantasia": nome_fantasia.strip() or razao_social.strip(),
        "documento": documento.strip(),
        "setor": setor,
        "porte": porte,
        "responsavel": responsavel.strip(),
        "email": email.strip(),
        "data_cadastro": datetime.now(),
        "dados": criar_dados_organizacao(),
    }

    st.session_state.organizacao_ativa = organizacao_id


def excluir_organizacao(organizacao_id):
    st.session_state.organizacoes.pop(organizacao_id, None)
    ids = list(st.session_state.organizacoes.keys())
    st.session_state.organizacao_ativa = ids[0] if ids else None


def obter_organizacao_ativa():
    organizacao_id = st.session_state.organizacao_ativa
    if organizacao_id is None:
        return None
    return st.session_state.organizacoes.get(organizacao_id)


def obter_dados_ativos():
    organizacao = obter_organizacao_ativa()
    return organizacao["dados"] if organizacao else None


inicializar_estado()


# ============================================================
# FUNÇÕES DE NEGÓCIO
# ============================================================

def cabecalho(titulo, descricao):
    st.markdown(
        f"""
        <div class="ctr-header">
            <h1>{titulo}</h1>
            <p>{descricao}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def sanitizar_texto(valor):
    if pd.isna(valor):
        return ""

    return (
        str(valor)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def nome_seguro(nome):
    texto = unicodedata.normalize("NFKD", nome)
    texto = texto.encode("ascii", "ignore").decode("ascii")
    texto = re.sub(r"[^a-zA-Z0-9_-]+", "_", texto.lower())
    return texto.strip("_") or "cliente"


def calcular_nivel_risco(probabilidade, impacto):
    pontuacao = int(probabilidade) * int(impacto)

    if pontuacao >= 20:
        return pontuacao, "Crítico"
    if pontuacao >= 12:
        return pontuacao, "Alto"
    if pontuacao >= 6:
        return pontuacao, "Médio"
    return pontuacao, "Baixo"


def calcular_assessment(dados=None):
    dados = dados or obter_dados_ativos()

    if dados is None:
        return {dimensao: 0 for dimensao in DIMENSOES}

    assessment = dados["assessment"]
    resultados = {}

    for dimensao, perguntas in PERGUNTAS_NIST.items():
        valores = []

        for indice, _ in enumerate(perguntas):
            resposta = assessment.get(
                f"{dimensao}_{indice}",
                "Não implementado",
            )
            valores.append(OPCOES_MATURIDADE.get(resposta, 0))

        resultados[dimensao] = round(
            sum(valores) / len(valores),
            2,
        )

    return resultados


def obter_score_geral(dados=None):
    resultados = calcular_assessment(dados)
    media = sum(resultados.values()) / len(resultados)
    return round((media / 5) * 100, 1)


def classificar_maturidade(score):
    if score >= 85:
        return "Otimizado"
    if score >= 70:
        return "Gerenciado"
    if score >= 50:
        return "Definido"
    if score >= 30:
        return "Inicial"
    return "Ad hoc"


def obter_recomendacoes(dados=None):
    resultados = calcular_assessment(dados)

    textos = {
        "Governar": "Formalizar políticas, responsabilidades, indicadores e supervisão executiva dos riscos.",
        "Identificar": "Atualizar inventários, classificar informações e institucionalizar avaliações de risco.",
        "Proteger": "Priorizar MFA, gestão de acessos, conscientização e proteção dos backups.",
        "Detectar": "Centralizar logs, definir casos de uso e implementar monitoramento contínuo.",
        "Responder": "Documentar, testar e manter um plano de resposta a incidentes.",
        "Recuperar": "Definir RTO/RPO, testar restauração e aprimorar a continuidade operacional.",
    }

    return [
        {
            "Dimensão": dimensao,
            "Maturidade": nota,
            "Recomendação": textos[dimensao],
        }
        for dimensao, nota in sorted(
            resultados.items(),
            key=lambda item: item[1],
        )
        if nota < 3
    ]


# ============================================================
# GRÁFICOS PARA PDF
# ============================================================

def salvar_figura_buffer(figura):
    buffer = io.BytesIO()
    figura.savefig(
        buffer,
        format="png",
        dpi=170,
        bbox_inches="tight",
        facecolor="white",
    )
    plt.close(figura)
    buffer.seek(0)
    return buffer


def grafico_radar_pdf(resultados):
    dimensoes = list(resultados.keys())
    valores = list(resultados.values())
    angulos = np.linspace(
        0,
        2 * np.pi,
        len(dimensoes),
        endpoint=False,
    ).tolist()

    angulos += angulos[:1]
    valores += valores[:1]

    figura, eixo = plt.subplots(
        figsize=(7.2, 5.2),
        subplot_kw={"polar": True},
    )

    eixo.plot(angulos, valores, color="#047f9e", linewidth=2.5)
    eixo.fill(angulos, valores, color="#20b5d6", alpha=0.28)
    eixo.set_xticks(angulos[:-1])
    eixo.set_xticklabels(dimensoes, fontsize=9)
    eixo.set_ylim(0, 5)
    eixo.set_yticks([1, 2, 3, 4, 5])
    eixo.grid(color="#b7d2da", alpha=0.8)
    eixo.set_title(
        "Radar de maturidade NIST CSF 2.0",
        fontsize=13,
        fontweight="bold",
        color="#102f3b",
        pad=20,
    )

    figura.tight_layout()
    return salvar_figura_buffer(figura)


def grafico_barras_pdf(resultados):
    dimensoes = list(resultados.keys())
    valores = list(resultados.values())

    figura, eixo = plt.subplots(figsize=(7.5, 4.8))

    barras = eixo.barh(
        dimensoes,
        valores,
        color="#0787a6",
    )

    eixo.set_xlim(0, 5)
    eixo.set_xlabel("Nível de maturidade")
    eixo.set_title(
        "Maturidade por dimensão",
        fontsize=13,
        fontweight="bold",
        color="#102f3b",
    )
    eixo.grid(axis="x", linestyle="--", alpha=0.35)
    eixo.invert_yaxis()

    for barra, valor in zip(barras, valores):
        eixo.text(
            min(valor + 0.08, 4.8),
            barra.get_y() + barra.get_height() / 2,
            f"{valor:.2f}",
            va="center",
            fontweight="bold",
        )

    figura.tight_layout()
    return salvar_figura_buffer(figura)


def grafico_pizza_pdf(riscos):
    figura, eixo = plt.subplots(figsize=(7, 4.8))

    if riscos.empty:
        eixo.text(
            0.5,
            0.5,
            "Nenhum risco cadastrado",
            ha="center",
            va="center",
            fontsize=14,
            color="#54717b",
        )
        eixo.axis("off")
    else:
        distribuicao = (
            riscos["Nível"]
            .value_counts()
            .reindex(
                ["Crítico", "Alto", "Médio", "Baixo"],
                fill_value=0,
            )
        )
        distribuicao = distribuicao[distribuicao > 0]

        mapa_cores = {
            "Crítico": "#c62828",
            "Alto": "#ef6c00",
            "Médio": "#f9a825",
            "Baixo": "#2e7d32",
        }

        eixo.pie(
            distribuicao.values,
            labels=distribuicao.index,
            autopct="%1.1f%%",
            startangle=90,
            colors=[mapa_cores[nivel] for nivel in distribuicao.index],
            wedgeprops={"width": 0.55, "edgecolor": "white"},
        )
        eixo.set_title(
            "Distribuição dos riscos",
            fontsize=13,
            fontweight="bold",
            color="#102f3b",
        )

    figura.tight_layout()
    return salvar_figura_buffer(figura)


# ============================================================
# RELATÓRIO PDF
# ============================================================

def adicionar_rodape_pdf(canvas, documento):
    canvas.saveState()
    largura, _ = landscape(A4)

    canvas.setStrokeColor(colors.HexColor("#b7d2da"))
    canvas.line(1.3 * cm, 0.8 * cm, largura - 1.3 * cm, 0.8 * cm)

    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#54717b"))
    canvas.drawString(
        1.3 * cm,
        0.45 * cm,
        "CTR DEFENSE — Relatório confidencial",
    )
    canvas.drawRightString(
        largura - 1.3 * cm,
        0.45 * cm,
        f"Página {documento.page}",
    )
    canvas.restoreState()


def gerar_pdf_executivo(organizacao, consultor):
    dados = organizacao["dados"]
    riscos = dados["riscos"]
    acoes = dados["acoes"]
    resultados = calcular_assessment(dados)
    recomendacoes = obter_recomendacoes(dados)
    score = obter_score_geral(dados)
    classificacao = classificar_maturidade(score)

    riscos_criticos = (
        int((riscos["Nível"] == "Crítico").sum())
        if not riscos.empty
        else 0
    )

    acoes_concluidas = (
        int((acoes["Status"] == "Concluído").sum())
        if not acoes.empty
        else 0
    )

    buffer = io.BytesIO()

    documento = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=1.3 * cm,
        leftMargin=1.3 * cm,
        topMargin=1.2 * cm,
        bottomMargin=1.2 * cm,
        title="Relatório Executivo CTR DEFENSE",
        author="CTR DEFENSE",
    )

    estilos = getSampleStyleSheet()

    titulo = ParagraphStyle(
        "TituloCTR",
        parent=estilos["Title"],
        alignment=TA_CENTER,
        textColor=colors.HexColor("#102f3b"),
        fontSize=23,
        leading=28,
        spaceAfter=12,
    )

    subtitulo = ParagraphStyle(
        "SubtituloCTR",
        parent=estilos["Heading2"],
        textColor=colors.HexColor("#047f9e"),
        fontSize=15,
        leading=18,
        spaceBefore=10,
        spaceAfter=8,
    )

    normal = ParagraphStyle(
        "NormalCTR",
        parent=estilos["BodyText"],
        fontSize=8.5,
        leading=11,
        alignment=TA_JUSTIFY,
        textColor=colors.HexColor("#263238"),
    )

    elementos = [
        Spacer(1, 0.8 * cm),
        Paragraph("CTR DEFENSE", titulo),
        Paragraph("Relatório Executivo de Cibersegurança", subtitulo),
        Spacer(1, 0.3 * cm),
    ]

    dados_capa = [
        ["Organização", sanitizar_texto(organizacao["razao_social"])],
        ["Nome fantasia", sanitizar_texto(organizacao["nome_fantasia"])],
        ["Documento", sanitizar_texto(organizacao["documento"] or "Não informado")],
        ["Setor e porte", f"{organizacao['setor']} — {organizacao['porte']}"],
        ["Responsável", sanitizar_texto(organizacao["responsavel"] or "Não informado")],
        ["Consultor", sanitizar_texto(consultor or "CTR DEFENSE")],
        ["Emissão", datetime.now().strftime("%d/%m/%Y %H:%M")],
    ]

    tabela_capa = Table(
        dados_capa,
        colWidths=[5.4 * cm, 17.5 * cm],
    )
    tabela_capa.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#102f3b")),
                ("TEXTCOLOR", (0, 0), (0, -1), colors.white),
                ("BACKGROUND", (1, 0), (1, -1), colors.HexColor("#edf6f8")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#9fbfc8")),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("PADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    elementos.append(tabela_capa)
    elementos.append(Spacer(1, 0.6 * cm))

    indicadores = Table(
        [
            [
                "Maturidade geral",
                "Classificação",
                "Riscos críticos",
                "Ações concluídas",
            ],
            [
                f"{score}%",
                classificacao,
                str(riscos_criticos),
                f"{acoes_concluidas}/{len(acoes)}",
            ],
        ],
        colWidths=[5.7 * cm] * 4,
    )
    indicadores.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#047f9e")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#f4fafc")),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 1), (-1, 1), 14),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#9fbfc8")),
                ("PADDING", (0, 0), (-1, -1), 9),
            ]
        )
    )
    elementos.extend([indicadores, PageBreak()])

    elementos.append(Paragraph("Resumo executivo", subtitulo))
    elementos.append(
        Paragraph(
            (
                f"A organização apresenta maturidade geral de <b>{score}%</b>, "
                f"classificada como <b>{classificacao}</b>. Foram registrados "
                f"<b>{len(riscos)} riscos</b>, sendo <b>{riscos_criticos}</b> "
                f"críticos. O plano de ação possui <b>{len(acoes)} iniciativas</b>, "
                f"com <b>{acoes_concluidas}</b> concluídas."
            ),
            normal,
        )
    )
    elementos.append(Spacer(1, 0.3 * cm))

    radar = Image(
        grafico_radar_pdf(resultados),
        width=11.5 * cm,
        height=8.2 * cm,
    )
    barras = Image(
        grafico_barras_pdf(resultados),
        width=11.5 * cm,
        height=7.4 * cm,
    )

    elementos.append(
        Table(
            [[radar, barras]],
            colWidths=[12.2 * cm, 12.2 * cm],
            style=TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ]
            ),
        )
    )

    elementos.extend(
        [
            PageBreak(),
            Paragraph("Distribuição e priorização dos riscos", subtitulo),
            Image(
                grafico_pizza_pdf(riscos),
                width=12.3 * cm,
                height=8.3 * cm,
            ),
            Paragraph("Recomendações prioritárias", subtitulo),
        ]
    )

    if recomendacoes:
        linhas = [["Dimensão", "Nota", "Recomendação"]]

        for item in recomendacoes:
            linhas.append(
                [
                    item["Dimensão"],
                    f"{item['Maturidade']:.2f}",
                    Paragraph(
                        sanitizar_texto(item["Recomendação"]),
                        normal,
                    ),
                ]
            )

        tabela = Table(
            linhas,
            colWidths=[4 * cm, 2.5 * cm, 17.2 * cm],
            repeatRows=1,
        )
        tabela.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#102f3b")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [
                        colors.white,
                        colors.HexColor("#edf6f8"),
                    ]),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#9fbfc8")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("PADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        elementos.append(tabela)
    else:
        elementos.append(
            Paragraph(
                "Nenhuma dimensão abaixo do nível mínimo recomendado.",
                normal,
            )
        )

    elementos.extend(
        [
            PageBreak(),
            Paragraph("Registro de riscos", subtitulo),
        ]
    )

    if riscos.empty:
        elementos.append(Paragraph("Nenhum risco cadastrado.", normal))
    else:
        colunas = [
            "ID",
            "Risco",
            "Probabilidade",
            "Impacto",
            "Nível",
            "Responsável",
            "Status",
        ]
        linhas = [colunas]

        for _, linha in riscos[colunas].iterrows():
            linhas.append(
                [
                    sanitizar_texto(linha["ID"]),
                    Paragraph(sanitizar_texto(linha["Risco"]), normal),
                    sanitizar_texto(linha["Probabilidade"]),
                    sanitizar_texto(linha["Impacto"]),
                    sanitizar_texto(linha["Nível"]),
                    sanitizar_texto(linha["Responsável"]),
                    sanitizar_texto(linha["Status"]),
                ]
            )

        tabela = Table(
            linhas,
            repeatRows=1,
            colWidths=[
                1.1 * cm,
                7.4 * cm,
                2.7 * cm,
                2.3 * cm,
                2.2 * cm,
                4.2 * cm,
                3 * cm,
            ],
        )
        tabela.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#047f9e")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [
                        colors.white,
                        colors.HexColor("#edf6f8"),
                    ]),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#9fbfc8")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("PADDING", (0, 0), (-1, -1), 5),
                ]
            )
        )
        elementos.append(tabela)

    elementos.append(Paragraph("Plano de ação", subtitulo))

    if acoes.empty:
        elementos.append(Paragraph("Nenhuma ação cadastrada.", normal))
    else:
        colunas = [
            "ID",
            "Ação",
            "Prioridade",
            "Responsável",
            "Prazo",
            "Status",
            "Progresso",
        ]
        linhas = [colunas]

        for _, linha in acoes[colunas].iterrows():
            linhas.append(
                [
                    sanitizar_texto(linha["ID"]),
                    Paragraph(sanitizar_texto(linha["Ação"]), normal),
                    sanitizar_texto(linha["Prioridade"]),
                    sanitizar_texto(linha["Responsável"]),
                    sanitizar_texto(linha["Prazo"]),
                    sanitizar_texto(linha["Status"]),
                    f"{linha['Progresso']}%",
                ]
            )

        tabela = Table(
            linhas,
            repeatRows=1,
            colWidths=[
                1.1 * cm,
                7.5 * cm,
                2.5 * cm,
                4 * cm,
                2.8 * cm,
                3.2 * cm,
                2.2 * cm,
            ],
        )
        tabela.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#102f3b")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [
                        colors.white,
                        colors.HexColor("#edf6f8"),
                    ]),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#9fbfc8")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("PADDING", (0, 0), (-1, -1), 5),
                ]
            )
        )
        elementos.append(tabela)

    documento.build(
        elementos,
        onFirstPage=adicionar_rodape_pdf,
        onLaterPages=adicionar_rodape_pdf,
    )

    buffer.seek(0)
    return buffer.getvalue()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown("## 🛡️ CTR DEFENSE")
    st.caption("Plataforma de Consultoria Profissional")

    organizacoes = st.session_state.organizacoes

    if organizacoes:
        ids = list(organizacoes.keys())

        if st.session_state.organizacao_ativa not in ids:
            st.session_state.organizacao_ativa = ids[0]

        selecionada = st.selectbox(
            "Organização ativa",
            options=ids,
            index=ids.index(st.session_state.organizacao_ativa),
            format_func=lambda identificador: organizacoes[
                identificador
            ]["nome_fantasia"],
        )

        if selecionada != st.session_state.organizacao_ativa:
            st.session_state.organizacao_ativa = selecionada
            st.rerun()
    else:
        st.info("Cadastre a primeira organização.")

    st.text_input(
        "Consultor responsável",
        key="consultor",
        placeholder="Nome do consultor",
    )

    menu = st.radio(
        "Módulos",
        [
            "Organizações",
            "Dashboard Executivo",
            "Assessment NIST CSF",
            "Vulnerabilidades",
            "Matriz de Riscos",
            "Plano de Ação",
            "Compliance",
            "Reuniões",
            "Relatórios",
        ],
    )

    st.markdown("---")
    st.caption("CTR DEFENSE © 2026")
    st.caption("Versão Pro 2.0")


# ============================================================
# ORGANIZAÇÕES
# ============================================================

if menu == "Organizações":
    cabecalho(
        "Gestão de Organizações",
        "Cadastre e administre os clientes atendidos pela CTR DEFENSE.",
    )

    with st.expander("Cadastrar nova organização", expanded=True):
        with st.form("form_organizacao", clear_on_submit=True):
            col1, col2 = st.columns(2)
            razao_social = col1.text_input("Razão social *")
            nome_fantasia = col2.text_input("Nome fantasia")

            col3, col4 = st.columns(2)
            documento = col3.text_input("CNPJ ou documento")
            setor = col4.selectbox(
                "Setor",
                [
                    "Tecnologia",
                    "Saúde",
                    "Financeiro",
                    "Indústria",
                    "Varejo",
                    "Educação",
                    "Governo",
                    "Serviços",
                    "Outro",
                ],
            )

            col5, col6 = st.columns(2)
            porte = col5.selectbox(
                "Porte",
                ["Microempresa", "Pequena", "Média", "Grande"],
            )
            responsavel = col6.text_input("Responsável no cliente")
            email = st.text_input("E-mail do responsável")

            if st.form_submit_button(
                "Cadastrar organização",
                type="primary",
            ):
                if not razao_social.strip():
                    st.error("Informe a razão social.")
                else:
                    cadastrar_organizacao(
                        razao_social,
                        nome_fantasia,
                        documento,
                        setor,
                        porte,
                        responsavel,
                        email,
                    )
                    st.success("Organização cadastrada.")
                    st.rerun()

    st.subheader("Organizações cadastradas")

    if not organizacoes:
        st.info("Nenhuma organização cadastrada.")
    else:
        for organizacao_id, organizacao in list(organizacoes.items()):
            dados_org = organizacao["dados"]
            score = obter_score_geral(dados_org)

            with st.container(border=True):
                col_info, col_metricas, col_acoes = st.columns([3, 2, 1])

                with col_info:
                    st.markdown(f"### {organizacao['nome_fantasia']}")
                    st.write(f"**Razão social:** {organizacao['razao_social']}")
                    st.write(
                        f"**Setor:** {organizacao['setor']} | "
                        f"**Porte:** {organizacao['porte']}"
                    )
                    st.write(
                        f"**Responsável:** "
                        f"{organizacao['responsavel'] or 'Não informado'}"
                    )

                with col_metricas:
                    st.metric("Maturidade", f"{score}%")
                    st.caption(classificar_maturidade(score))
                    st.caption(
                        f"{len(dados_org['riscos'])} riscos | "
                        f"{len(dados_org['acoes'])} ações"
                    )

                with col_acoes:
                    if st.button(
                        "Selecionar",
                        key=f"selecionar_{organizacao_id}",
                        use_container_width=True,
                    ):
                        st.session_state.organizacao_ativa = organizacao_id
                        st.rerun()

                    if st.button(
                        "Excluir",
                        key=f"excluir_{organizacao_id}",
                        use_container_width=True,
                    ):
                        excluir_organizacao(organizacao_id)
                        st.rerun()


# ============================================================
# PROTEÇÃO SEM ORGANIZAÇÃO
# ============================================================

elif obter_organizacao_ativa() is None:
    cabecalho(
        "Nenhuma organização selecionada",
        "Cadastre uma organização para utilizar os módulos da plataforma.",
    )
    st.warning("Acesse o módulo Organizações e cadastre o primeiro cliente.")


# ============================================================
# DASHBOARD
# ============================================================

elif menu == "Dashboard Executivo":
    organizacao = obter_organizacao_ativa()
    dados = obter_dados_ativos()
    riscos = dados["riscos"]
    acoes = dados["acoes"]
    resultados = calcular_assessment(dados)

    cabecalho(
        "Dashboard Executivo",
        "Visão consolidada da postura de segurança e das prioridades.",
    )

    st.markdown(
        f"""
        <div class="organization-card">
            <strong>Organização ativa:</strong>
            {organizacao["nome_fantasia"]}<br>
            {organizacao["setor"]} • {organizacao["porte"]} •
            Responsável: {organizacao["responsavel"] or "Não informado"}
        </div>
        """,
        unsafe_allow_html=True,
    )

    score = obter_score_geral(dados)
    riscos_criticos = (
        int((riscos["Nível"] == "Crítico").sum())
        if not riscos.empty
        else 0
    )
    riscos_altos = (
        int((riscos["Nível"] == "Alto").sum())
        if not riscos.empty
        else 0
    )
    concluidas = (
        int((acoes["Status"] == "Concluído").sum())
        if not acoes.empty
        else 0
    )

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Maturidade geral", f"{score}%")
    col2.metric("Classificação", classificar_maturidade(score))
    col3.metric("Riscos críticos", riscos_criticos)
    col4.metric("Riscos altos", riscos_altos)
    col5.metric("Ações concluídas", f"{concluidas}/{len(acoes)}")

    grafico1, grafico2 = st.columns(2)

    with grafico1:
        st.subheader("Radar de maturidade")

        dimensoes = list(resultados.keys())
        valores = list(resultados.values())

        figura = go.Figure(
            go.Scatterpolar(
                r=valores + [valores[0]],
                theta=dimensoes + [dimensoes[0]],
                fill="toself",
                line=dict(color="#0787a6", width=3),
                fillcolor="rgba(7,135,166,0.28)",
            )
        )
        figura.update_layout(
            polar=dict(
                bgcolor="rgba(255,255,255,0.48)",
                radialaxis=dict(visible=True, range=[0, 5]),
            ),
            showlegend=False,
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=40, r=40, t=35, b=35),
        )
        st.plotly_chart(figura, use_container_width=True)

    with grafico2:
        st.subheader("Maturidade por dimensão")

        df_maturidade = pd.DataFrame(
            {
                "Dimensão": list(resultados.keys()),
                "Maturidade": list(resultados.values()),
            }
        )

        figura = px.bar(
            df_maturidade,
            x="Maturidade",
            y="Dimensão",
            orientation="h",
            color="Maturidade",
            color_continuous_scale=[
                "#c62828",
                "#f9a825",
                "#0787a6",
                "#2e7d32",
            ],
            text_auto=".2f",
            range_x=[0, 5],
        )
        figura.update_layout(
            coloraxis_showscale=False,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(255,255,255,0.45)",
            yaxis=dict(autorange="reversed"),
        )
        st.plotly_chart(figura, use_container_width=True)

    grafico3, grafico4 = st.columns(2)

    with grafico3:
        st.subheader("Distribuição dos riscos")

        if riscos.empty:
            st.info("Cadastre riscos para visualizar a distribuição.")
        else:
            distribuicao = (
                riscos["Nível"]
                .value_counts()
                .reset_index()
            )
            distribuicao.columns = ["Nível", "Quantidade"]

            figura = px.pie(
                distribuicao,
                names="Nível",
                values="Quantidade",
                hole=0.46,
                color="Nível",
                color_discrete_map={
                    "Crítico": "#c62828",
                    "Alto": "#ef6c00",
                    "Médio": "#f9a825",
                    "Baixo": "#2e7d32",
                },
            )
            figura.update_traces(
                textposition="inside",
                textinfo="percent+label",
            )
            figura.update_layout(paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(figura, use_container_width=True)

    with grafico4:
        st.subheader("Situação do plano de ação")

        if acoes.empty:
            st.info("Cadastre ações para visualizar o andamento.")
        else:
            status = acoes["Status"].value_counts().reset_index()
            status.columns = ["Status", "Quantidade"]

            figura = px.bar(
                status,
                x="Status",
                y="Quantidade",
                color="Status",
                text_auto=True,
                color_discrete_map={
                    "Não iniciado": "#78909c",
                    "Em andamento": "#0787a6",
                    "Bloqueado": "#c62828",
                    "Concluído": "#2e7d32",
                },
            )
            figura.update_layout(
                showlegend=False,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(255,255,255,0.45)",
            )
            st.plotly_chart(figura, use_container_width=True)

    st.subheader("Prioridades recomendadas")

    recomendacoes = obter_recomendacoes(dados)

    if recomendacoes:
        for item in recomendacoes[:3]:
            st.markdown(
                f"""
                <div class="warning-box">
                    <strong>{item["Dimensão"]} —
                    nota {item["Maturidade"]}/5</strong><br>
                    {item["Recomendação"]}
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.success("Nenhuma dimensão abaixo do nível mínimo recomendado.")


# ============================================================
# ASSESSMENT
# ============================================================

elif menu == "Assessment NIST CSF":
    dados = obter_dados_ativos()
    assessment = dados["assessment"]

    cabecalho(
        "Assessment NIST CSF 2.0",
        "Avaliação de maturidade nas seis funções do framework.",
    )

    total = sum(len(perguntas) for perguntas in PERGUNTAS_NIST.values())
    preenchidas = len(assessment)

    st.write(f"Progresso: **{preenchidas}/{total} respostas**")
    st.progress(min(preenchidas / total, 1.0))

    abas = st.tabs(DIMENSOES)

    for aba, dimensao in zip(abas, DIMENSOES):
        with aba:
            for indice, pergunta in enumerate(PERGUNTAS_NIST[dimensao]):
                chave = f"{dimensao}_{indice}"
                atual = assessment.get(chave, "Não implementado")

                st.markdown(
                    f'<div class="question-card"><strong>'
                    f'{indice + 1}. {pergunta}</strong></div>',
                    unsafe_allow_html=True,
                )

                assessment[chave] = st.selectbox(
                    "Nível de implementação",
                    list(OPCOES_MATURIDADE.keys()),
                    index=list(OPCOES_MATURIDADE.keys()).index(atual),
                    key=f"assessment_{organizacao['id']}_{chave}",
                )

    resultados = calcular_assessment(dados)
    colunas = st.columns(6)

    for coluna, dimensao in zip(colunas, DIMENSOES):
        coluna.metric(dimensao, f"{resultados[dimensao]:.2f}/5")

    if st.button("Limpar assessment"):
        dados["assessment"] = {}
        st.rerun()


# ============================================================
# VULNERABILIDADES
# ============================================================

elif menu == "Vulnerabilidades":
    cabecalho(
        "Gestão de Vulnerabilidades",
        "Importe resultados em CSV de scanners ou planilhas internas.",
    )

    arquivo = st.file_uploader("Importar arquivo CSV", type=["csv"])

    if arquivo:
        try:
            vulnerabilidades = pd.read_csv(arquivo)
            st.success(f"{len(vulnerabilidades)} registros carregados.")
            st.dataframe(vulnerabilidades, use_container_width=True)

            coluna = st.selectbox(
                "Coluna de severidade",
                ["Não selecionar"] + vulnerabilidades.columns.tolist(),
            )

            if coluna != "Não selecionar":
                resumo = (
                    vulnerabilidades[coluna]
                    .astype(str)
                    .value_counts()
                    .reset_index()
                )
                resumo.columns = ["Severidade", "Quantidade"]

                figura = px.bar(
                    resumo,
                    x="Severidade",
                    y="Quantidade",
                    color="Severidade",
                    text_auto=True,
                )
                st.plotly_chart(figura, use_container_width=True)

            st.download_button(
                "Baixar CSV processado",
                vulnerabilidades.to_csv(index=False).encode("utf-8-sig"),
                "vulnerabilidades.csv",
                "text/csv",
            )
        except Exception as erro:
            st.error(f"Erro ao processar o arquivo: {erro}")
    else:
        st.info("Selecione um arquivo CSV para iniciar.")


# ============================================================
# RISCOS
# ============================================================

elif menu == "Matriz de Riscos":
    dados = obter_dados_ativos()

    cabecalho(
        "Matriz de Riscos",
        "Registro e priorização por probabilidade e impacto.",
    )

    with st.expander("Adicionar risco", expanded=True):
        with st.form("form_risco", clear_on_submit=True):
            risco = st.text_input("Descrição do risco")

            col1, col2 = st.columns(2)
            categoria = col1.selectbox(
                "Categoria",
                [
                    "Cibernético",
                    "Privacidade",
                    "Operacional",
                    "Terceiros",
                    "Compliance",
                    "Continuidade",
                ],
            )
            responsavel = col2.text_input("Responsável")

            col3, col4 = st.columns(2)
            probabilidade = col3.slider("Probabilidade", 1, 5, 3)
            impacto = col4.slider("Impacto", 1, 5, 3)

            tratamento = st.selectbox(
                "Tratamento",
                ["Mitigar", "Evitar", "Transferir", "Aceitar"],
            )

            if st.form_submit_button("Adicionar risco", type="primary"):
                if not risco.strip():
                    st.error("Informe a descrição do risco.")
                else:
                    _, nivel = calcular_nivel_risco(
                        probabilidade,
                        impacto,
                    )

                    novo = pd.DataFrame(
                        [
                            {
                                "ID": len(dados["riscos"]) + 1,
                                "Risco": risco.strip(),
                                "Categoria": categoria,
                                "Probabilidade": probabilidade,
                                "Impacto": impacto,
                                "Nível": nivel,
                                "Responsável": responsavel.strip(),
                                "Tratamento": tratamento,
                                "Status": "Ativo",
                            }
                        ]
                    )

                    dados["riscos"] = pd.concat(
                        [dados["riscos"], novo],
                        ignore_index=True,
                    )
                    st.rerun()

    riscos = dados["riscos"]

    if riscos.empty:
        st.info("Nenhum risco cadastrado.")
    else:
        st.dataframe(riscos, use_container_width=True, hide_index=True)

        matriz = pd.DataFrame(
            0,
            index=[5, 4, 3, 2, 1],
            columns=[1, 2, 3, 4, 5],
        )

        for _, linha in riscos.iterrows():
            matriz.loc[
                int(linha["Probabilidade"]),
                int(linha["Impacto"]),
            ] += 1

        figura = go.Figure(
            go.Heatmap(
                z=[
                    [5, 10, 15, 20, 25],
                    [4, 8, 12, 16, 20],
                    [3, 6, 9, 12, 15],
                    [2, 4, 6, 8, 10],
                    [1, 2, 3, 4, 5],
                ],
                x=[1, 2, 3, 4, 5],
                y=[5, 4, 3, 2, 1],
                text=matriz.astype(str).values,
                texttemplate="Riscos: %{text}",
                colorscale=[
                    [0.00, "#43a047"],
                    [0.24, "#8bc34a"],
                    [0.25, "#fdd835"],
                    [0.47, "#fdd835"],
                    [0.48, "#fb8c00"],
                    [0.79, "#fb8c00"],
                    [0.80, "#c62828"],
                    [1.00, "#c62828"],
                ],
                showscale=False,
            )
        )
        figura.update_layout(
            xaxis_title="Impacto",
            yaxis_title="Probabilidade",
            height=500,
        )
        st.plotly_chart(figura, use_container_width=True)

        col1, col2 = st.columns([3, 1])
        col1.download_button(
            "Exportar riscos",
            riscos.to_csv(index=False).encode("utf-8-sig"),
            "riscos.csv",
            "text/csv",
        )

        if col2.button("Excluir todos"):
            dados["riscos"] = dataframe_riscos()
            st.rerun()


# ============================================================
# PLANO DE AÇÃO
# ============================================================

elif menu == "Plano de Ação":
    dados = obter_dados_ativos()

    cabecalho(
        "Plano de Ação e Roadmap",
        "Gerencie iniciativas de redução de riscos e conformidade.",
    )

    with st.expander("Adicionar ação", expanded=True):
        with st.form("form_acao", clear_on_submit=True):
            acao = st.text_input("Ação recomendada")

            col1, col2, col3 = st.columns(3)
            origem = col1.selectbox(
                "Origem",
                [
                    "Assessment",
                    "Risco",
                    "Vulnerabilidade",
                    "Auditoria",
                    "Compliance",
                ],
            )
            prioridade = col2.selectbox(
                "Prioridade",
                ["Crítica", "Alta", "Média", "Baixa"],
            )
            responsavel = col3.text_input("Responsável")

            col4, col5 = st.columns(2)
            inicio = col4.date_input("Início", value=date.today())
            prazo = col5.date_input("Prazo", value=date.today())

            status = st.selectbox("Status", STATUS_ACAO)
            progresso = st.slider("Progresso", 0, 100, 0, step=5)

            if st.form_submit_button("Adicionar ação", type="primary"):
                if not acao.strip():
                    st.error("Informe a ação.")
                elif prazo < inicio:
                    st.error("O prazo não pode ser anterior ao início.")
                else:
                    nova = pd.DataFrame(
                        [
                            {
                                "ID": len(dados["acoes"]) + 1,
                                "Ação": acao.strip(),
                                "Origem": origem,
                                "Prioridade": prioridade,
                                "Responsável": responsavel.strip(),
                                "Início": inicio,
                                "Prazo": prazo,
                                "Status": status,
                                "Progresso": progresso,
                            }
                        ]
                    )

                    dados["acoes"] = pd.concat(
                        [dados["acoes"], nova],
                        ignore_index=True,
                    )
                    st.rerun()

    acoes = dados["acoes"]

    if acoes.empty:
        st.info("Nenhuma ação cadastrada.")
    else:
        st.dataframe(acoes, use_container_width=True, hide_index=True)

        gantt = acoes.copy()
        gantt["Início"] = pd.to_datetime(gantt["Início"])
        gantt["Prazo"] = pd.to_datetime(gantt["Prazo"])

        figura = px.timeline(
            gantt,
            x_start="Início",
            x_end="Prazo",
            y="Ação",
            color="Prioridade",
            hover_data=["Responsável", "Status", "Progresso"],
            color_discrete_map={
                "Crítica": "#c62828",
                "Alta": "#ef6c00",
                "Média": "#f9a825",
                "Baixa": "#2e7d32",
            },
        )
        figura.update_yaxes(autorange="reversed")
        st.plotly_chart(figura, use_container_width=True)

        col1, col2 = st.columns([3, 1])
        col1.download_button(
            "Exportar ações",
            acoes.to_csv(index=False).encode("utf-8-sig"),
            "plano_de_acao.csv",
            "text/csv",
        )

        if col2.button("Excluir todas"):
            dados["acoes"] = dataframe_acoes()
            st.rerun()


# ============================================================
# COMPLIANCE
# ============================================================

elif menu == "Compliance":
    dados = obter_dados_ativos()

    cabecalho(
        "Adequação e Compliance",
        "Acompanhamento de NIST CSF, ISO 27001 e LGPD.",
    )

    framework = st.selectbox("Framework", list(FRAMEWORKS.keys()))
    pontuacoes = []

    for indice, controle in enumerate(FRAMEWORKS[framework]):
        chave = f"{framework}_{indice}"
        col1, col2 = st.columns([3, 2])
        col1.markdown(f"**{controle}**")

        valor = col2.select_slider(
            "Percentual",
            options=[0, 25, 50, 75, 100],
            value=dados["compliance"].get(chave, 0),
            key=f"compliance_{organizacao['id']}_{chave}",
            label_visibility="collapsed",
        )

        dados["compliance"][chave] = valor
        pontuacoes.append(valor)

    media = round(sum(pontuacoes) / len(pontuacoes), 1)
    st.progress(media / 100)
    st.metric("Nível de conformidade", f"{media}%")

    if media < 40:
        st.error("Nível crítico de conformidade.")
    elif media < 70:
        st.warning("Existem lacunas relevantes de conformidade.")
    else:
        st.success("Bom nível de conformidade.")


# ============================================================
# REUNIÕES
# ============================================================

elif menu == "Reuniões":
    dados = obter_dados_ativos()

    cabecalho(
        "Reuniões Executivas",
        "Registre decisões e próximos passos da consultoria.",
    )

    with st.form("form_reuniao", clear_on_submit=True):
        col1, col2 = st.columns(2)
        data_reuniao = col1.date_input("Data", value=date.today())
        titulo = col2.text_input("Título")
        participantes = st.text_input("Participantes")
        resumo = st.text_area("Resumo")
        decisoes = st.text_area("Decisões")
        proximos = st.text_area("Próximos passos")

        if st.form_submit_button("Registrar reunião", type="primary"):
            if not titulo.strip():
                st.error("Informe o título.")
            else:
                nova = pd.DataFrame(
                    [
                        {
                            "Data": data_reuniao,
                            "Título": titulo.strip(),
                            "Participantes": participantes.strip(),
                            "Resumo": resumo.strip(),
                            "Decisões": decisoes.strip(),
                            "Próximos passos": proximos.strip(),
                        }
                    ]
                )

                dados["reunioes"] = pd.concat(
                    [dados["reunioes"], nova],
                    ignore_index=True,
                )
                st.rerun()

    if dados["reunioes"].empty:
        st.info("Nenhuma reunião registrada.")
    else:
        st.dataframe(
            dados["reunioes"],
            use_container_width=True,
            hide_index=True,
        )
        st.download_button(
            "Exportar atas",
            dados["reunioes"].to_csv(index=False).encode("utf-8-sig"),
            "reunioes.csv",
            "text/csv",
        )


# ============================================================
# RELATÓRIOS
# ============================================================

elif menu == "Relatórios":
    organizacao = obter_organizacao_ativa()
    dados = obter_dados_ativos()
    arquivo_base = nome_seguro(organizacao["nome_fantasia"])

    cabecalho(
        "Relatórios e Entregáveis",
        "Gere o relatório executivo da organização selecionada.",
    )

    score = obter_score_geral(dados)

    col1, col2, col3 = st.columns(3)
    col1.metric("Score geral", f"{score}%")
    col2.metric("Maturidade", classificar_maturidade(score))
    col3.metric(
        "Itens registrados",
        len(dados["riscos"]) + len(dados["acoes"]),
    )

    st.info(f"Organização: {organizacao['nome_fantasia']}")

    try:
        pdf = gerar_pdf_executivo(
            organizacao,
            st.session_state.consultor,
        )

        st.download_button(
            "Gerar e baixar relatório executivo",
            data=pdf,
            file_name=f"relatorio_ctr_defense_{arquivo_base}.pdf",
            mime="application/pdf",
            type="primary",
        )
    except Exception as erro:
        st.error(f"Não foi possível gerar o PDF: {erro}")

    st.subheader("Exportações individuais")

    col1, col2, col3 = st.columns(3)

    col1.download_button(
        "Matriz de riscos",
        dados["riscos"].to_csv(index=False).encode("utf-8-sig"),
        f"riscos_{arquivo_base}.csv",
        "text/csv",
        use_container_width=True,
    )

    col2.download_button(
        "Plano de ação",
        dados["acoes"].to_csv(index=False).encode("utf-8-sig"),
        f"acoes_{arquivo_base}.csv",
        "text/csv",
        use_container_width=True,
    )

    col3.download_button(
        "Atas de reunião",
        dados["reunioes"].to_csv(index=False).encode("utf-8-sig"),
        f"reunioes_{arquivo_base}.csv",
        "text/csv",
        use_container_width=True,
    )


# ============================================================
# RODAPÉ
# ============================================================

st.markdown(
    """
    <div class="ctr-footer">
        CTR DEFENSE — Plataforma de Consultoria em Cibersegurança<br>
        NIST CSF 2.0 • ISO 27001 • LGPD • Gestão de Riscos
    </div>
    """,
    unsafe_allow_html=True,
)
