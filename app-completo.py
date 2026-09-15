import io
from datetime import date, datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
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
            --ctr-primary: #047f9e;
            --ctr-secondary: #102f3b;
            --ctr-accent: #16a4c5;
            --ctr-light: #f2f7f9;
            --ctr-border: #d5e4e9;
            --ctr-text: #102f3b;
            --ctr-danger: #c62828;
            --ctr-warning: #ef6c00;
            --ctr-success: #2e7d32;
        }

        .stApp {
            background-color: #f7fafb;
            color: var(--ctr-text);
        }

        h1, h2, h3, h4, p, label, span {
            color: var(--ctr-text);
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #102f3b 0%, #174656 100%);
        }

        [data-testid="stSidebar"] * {
            color: #ffffff !important;
        }

        [data-testid="stSidebar"] input {
            color: #102f3b !important;
            background-color: #ffffff !important;
        }

        .ctr-header {
            padding: 24px;
            border-radius: 14px;
            background: linear-gradient(120deg, #102f3b, #047f9e);
            color: #ffffff !important;
            margin-bottom: 20px;
            box-shadow: 0 8px 22px rgba(16, 47, 59, 0.16);
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

        .ctr-card {
            background-color: #ffffff;
            border: 1px solid var(--ctr-border);
            border-left: 5px solid var(--ctr-primary);
            border-radius: 12px;
            padding: 18px;
            margin-bottom: 14px;
            box-shadow: 0 4px 14px rgba(16, 47, 59, 0.07);
        }

        .ctr-card h3,
        .ctr-card p {
            margin-top: 0;
        }

        .ctr-badge {
            display: inline-block;
            padding: 5px 10px;
            border-radius: 16px;
            background-color: #e1f4f8;
            color: #047f9e !important;
            font-weight: 700;
            font-size: 0.82rem;
        }

        .critical-box {
            background-color: #ffebee;
            border-left: 5px solid #c62828;
            border-radius: 10px;
            padding: 14px;
        }

        .warning-box {
            background-color: #fff3e0;
            border-left: 5px solid #ef6c00;
            border-radius: 10px;
            padding: 14px;
        }

        .success-box {
            background-color: #e8f5e9;
            border-left: 5px solid #2e7d32;
            border-radius: 10px;
            padding: 14px;
        }

        div[data-testid="stMetric"] {
            background-color: #ffffff;
            border: 1px solid var(--ctr-border);
            border-radius: 12px;
            padding: 16px;
            box-shadow: 0 4px 12px rgba(16, 47, 59, 0.06);
        }

        div[data-testid="stTextInput"] input,
        div[data-testid="stNumberInput"] input,
        div[data-testid="stDateInput"] input,
        div[data-testid="stTextArea"] textarea {
            background-color: #ffffff !important;
            color: #102f3b !important;
            border: 1px solid #b9cdd4 !important;
        }

        div[data-baseweb="select"] > div {
            background-color: #ffffff !important;
            color: #102f3b !important;
        }

        div[role="listbox"] {
            background-color: #ffffff !important;
        }

        div[role="option"] {
            color: #102f3b !important;
        }

        .stButton > button,
        .stDownloadButton > button {
            border-radius: 8px;
            font-weight: 700;
        }

        .ctr-footer {
            text-align: center;
            color: #5d747c;
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
        "Há procedimento formal de comunicação de incidentes?",
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

STATUS_ACAO = [
    "Não iniciado",
    "Em andamento",
    "Bloqueado",
    "Concluído",
]

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


# ============================================================
# ESTADO DA SESSÃO
# ============================================================

def inicializar_estado():
    estados = {
        "riscos": pd.DataFrame(
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
        ),
        "acoes": pd.DataFrame(
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
        ),
        "reunioes": pd.DataFrame(
            columns=[
                "Data",
                "Título",
                "Participantes",
                "Resumo",
                "Decisões",
                "Próximos passos",
            ]
        ),
        "assessment": {},
        "compliance": {},
    }

    for chave, valor in estados.items():
        if chave not in st.session_state:
            st.session_state[chave] = valor


inicializar_estado()


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def calcular_nivel_risco(probabilidade, impacto):
    pontuacao = int(probabilidade) * int(impacto)

    if pontuacao >= 20:
        return pontuacao, "Crítico"
    if pontuacao >= 12:
        return pontuacao, "Alto"
    if pontuacao >= 6:
        return pontuacao, "Médio"
    return pontuacao, "Baixo"


def cor_nivel(nivel):
    cores_niveis = {
        "Crítico": "#c62828",
        "Alto": "#ef6c00",
        "Médio": "#f9a825",
        "Baixo": "#2e7d32",
    }
    return cores_niveis.get(nivel, "#607d8b")


def calcular_assessment():
    resultados = {}

    for dimensao, perguntas in PERGUNTAS_NIST.items():
        valores = []

        for indice, _ in enumerate(perguntas):
            resposta = st.session_state.assessment.get(
                f"{dimensao}_{indice}",
                "Não implementado",
            )
            valores.append(OPCOES_MATURIDADE.get(resposta, 0))

        resultados[dimensao] = (
            round(sum(valores) / len(valores), 2) if valores else 0
        )

    return resultados


def obter_score_geral():
    resultados = calcular_assessment()

    if not resultados:
        return 0

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


def obter_recomendacoes():
    resultados = calcular_assessment()
    recomendacoes = []

    textos = {
        "Governar": "Formalizar políticas, responsabilidades, indicadores e supervisão executiva dos riscos.",
        "Identificar": "Atualizar inventários, classificar informações e institucionalizar avaliações de risco.",
        "Proteger": "Priorizar MFA, gestão de acessos, conscientização e proteção dos backups.",
        "Detectar": "Centralizar logs, definir casos de uso e implementar monitoramento contínuo.",
        "Responder": "Documentar, testar e manter um plano de resposta a incidentes.",
        "Recuperar": "Definir RTO/RPO, testar restauração e aprimorar a continuidade operacional.",
    }

    for dimensao, valor in sorted(resultados.items(), key=lambda item: item[1]):
        if valor < 3:
            recomendacoes.append(
                {
                    "Dimensão": dimensao,
                    "Maturidade": valor,
                    "Recomendação": textos[dimensao],
                }
            )

    return recomendacoes


def sanitizar_texto(valor):
    if pd.isna(valor):
        return ""
    return str(valor).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def gerar_pdf_executivo(empresa, consultor):
    buffer = io.BytesIO()

    documento = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=1.3 * cm,
        leftMargin=1.3 * cm,
        topMargin=1.2 * cm,
        bottomMargin=1.2 * cm,
        title="Relatório Executivo CTR DEFENSE",
    )

    estilos = getSampleStyleSheet()

    titulo = ParagraphStyle(
        "TituloCTR",
        parent=estilos["Title"],
        alignment=TA_CENTER,
        textColor=colors.HexColor("#102f3b"),
        fontSize=22,
        spaceAfter=16,
    )

    subtitulo = ParagraphStyle(
        "SubtituloCTR",
        parent=estilos["Heading2"],
        textColor=colors.HexColor("#047f9e"),
        fontSize=15,
        spaceBefore=12,
        spaceAfter=8,
    )

    normal = ParagraphStyle(
        "NormalCTR",
        parent=estilos["BodyText"],
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#263238"),
    )

    elementos = []

    score = obter_score_geral()
    classificacao = classificar_maturidade(score)
    resultados = calcular_assessment()
    recomendacoes = obter_recomendacoes()

    elementos.append(Paragraph("CTR DEFENSE", titulo))
    elementos.append(Paragraph("Relatório Executivo de Cibersegurança", subtitulo))
    elementos.append(Spacer(1, 10))

    dados_capa = [
        ["Organização", sanitizar_texto(empresa or "Não informada")],
        ["Consultor", sanitizar_texto(consultor or "CTR DEFENSE")],
        ["Data de emissão", datetime.now().strftime("%d/%m/%Y %H:%M")],
        ["Score de maturidade", f"{score}%"],
        ["Classificação", classificacao],
    ]

    tabela_capa = Table(dados_capa, colWidths=[5 * cm, 17 * cm])
    tabela_capa.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#102f3b")),
                ("TEXTCOLOR", (0, 0), (0, -1), colors.white),
                ("BACKGROUND", (1, 0), (1, -1), colors.HexColor("#f2f7f9")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#b0bec5")),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("PADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    elementos.append(tabela_capa)
    elementos.append(PageBreak())

    elementos.append(Paragraph("Maturidade por dimensão", subtitulo))

    dados_maturidade = [["Dimensão", "Nota", "Percentual"]]

    for dimensao, nota in resultados.items():
        dados_maturidade.append(
            [
                dimensao,
                f"{nota:.2f} / 5",
                f"{(nota / 5) * 100:.1f}%",
            ]
        )

    tabela_maturidade = Table(
        dados_maturidade,
        colWidths=[10 * cm, 6 * cm, 6 * cm],
    )
    tabela_maturidade.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#047f9e")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#b0bec5")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [
                    colors.white,
                    colors.HexColor("#f2f7f9"),
                ]),
                ("ALIGN", (1, 1), (-1, -1), "CENTER"),
                ("PADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )
    elementos.append(tabela_maturidade)

    elementos.append(Paragraph("Recomendações prioritárias", subtitulo))

    if recomendacoes:
        dados_recomendacoes = [["Dimensão", "Nota", "Recomendação"]]

        for item in recomendacoes:
            dados_recomendacoes.append(
                [
                    item["Dimensão"],
                    str(item["Maturidade"]),
                    Paragraph(sanitizar_texto(item["Recomendação"]), normal),
                ]
            )

        tabela_recomendacoes = Table(
            dados_recomendacoes,
            colWidths=[4 * cm, 3 * cm, 16 * cm],
        )
        tabela_recomendacoes.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#102f3b")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#b0bec5")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("PADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        elementos.append(tabela_recomendacoes)
    else:
        elementos.append(
            Paragraph(
                "Nenhuma recomendação crítica foi identificada.",
                normal,
            )
        )

    elementos.append(PageBreak())
    elementos.append(Paragraph("Registro de riscos", subtitulo))

    if not st.session_state.riscos.empty:
        colunas = [
            "ID",
            "Risco",
            "Probabilidade",
            "Impacto",
            "Nível",
            "Responsável",
            "Status",
        ]

        dados_riscos = [colunas]

        for _, linha in st.session_state.riscos[colunas].iterrows():
            dados_riscos.append(
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

        tabela_riscos = Table(
            dados_riscos,
            repeatRows=1,
            colWidths=[
                1.2 * cm,
                7.5 * cm,
                2.7 * cm,
                2.3 * cm,
                2.2 * cm,
                4.2 * cm,
                3 * cm,
            ],
        )
        tabela_riscos.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#047f9e")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#b0bec5")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("PADDING", (0, 0), (-1, -1), 5),
                ]
            )
        )
        elementos.append(tabela_riscos)
    else:
        elementos.append(Paragraph("Nenhum risco cadastrado.", normal))

    elementos.append(Paragraph("Plano de ação", subtitulo))

    if not st.session_state.acoes.empty:
        colunas = [
            "ID",
            "Ação",
            "Prioridade",
            "Responsável",
            "Prazo",
            "Status",
            "Progresso",
        ]

        dados_acoes = [colunas]

        for _, linha in st.session_state.acoes[colunas].iterrows():
            dados_acoes.append(
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

        tabela_acoes = Table(
            dados_acoes,
            repeatRows=1,
            colWidths=[
                1.2 * cm,
                7.5 * cm,
                2.5 * cm,
                4 * cm,
                2.8 * cm,
                3.2 * cm,
                2.2 * cm,
            ],
        )
        tabela_acoes.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#102f3b")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#b0bec5")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("PADDING", (0, 0), (-1, -1), 5),
                ]
            )
        )
        elementos.append(tabela_acoes)
    else:
        elementos.append(Paragraph("Nenhuma ação cadastrada.", normal))

    documento.build(elementos)
    buffer.seek(0)
    return buffer.getvalue()


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


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown("## 🛡️ CTR DEFENSE")
    st.caption("Plataforma de Consultoria Profissional")

    empresa = st.text_input(
        "Organização",
        value=st.session_state.get("empresa", ""),
        placeholder="Nome do cliente",
    )
    consultor = st.text_input(
        "Consultor responsável",
        value=st.session_state.get("consultor", ""),
        placeholder="Nome do consultor",
    )

    st.session_state.empresa = empresa
    st.session_state.consultor = consultor

    menu = st.radio(
        "Módulos",
        [
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
    st.caption("Versão Pro 1.0")


# ============================================================
# DASHBOARD
# ============================================================

if menu == "Dashboard Executivo":
    cabecalho(
        "Dashboard Executivo",
        "Visão consolidada da postura de segurança e das prioridades do cliente.",
    )

    score = obter_score_geral()
    maturidade = classificar_maturidade(score)

    riscos_criticos = 0
    if not st.session_state.riscos.empty:
        riscos_criticos = int(
            (st.session_state.riscos["Nível"] == "Crítico").sum()
        )

    total_acoes = len(st.session_state.acoes)
    concluidas = 0

    if total_acoes:
        concluidas = int(
            (st.session_state.acoes["Status"] == "Concluído").sum()
        )

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Maturidade geral", f"{score}%")
    col2.metric("Classificação", maturidade)
    col3.metric("Riscos críticos", riscos_criticos)
    col4.metric("Ações concluídas", f"{concluidas}/{total_acoes}")

    resultados = calcular_assessment()

    col_grafico1, col_grafico2 = st.columns(2)

    with col_grafico1:
        st.subheader("Radar de maturidade")

        valores = list(resultados.values())
        dimensoes = list(resultados.keys())

        fig_radar = go.Figure(
            data=go.Scatterpolar(
                r=valores + [valores[0]],
                theta=dimensoes + [dimensoes[0]],
                fill="toself",
                line_color="#047f9e",
                fillcolor="rgba(4,127,158,0.25)",
                name="Maturidade",
            )
        )

        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 5],
                )
            ),
            showlegend=False,
            margin=dict(l=35, r=35, t=30, b=30),
            paper_bgcolor="rgba(0,0,0,0)",
        )

        st.plotly_chart(fig_radar, use_container_width=True)

    with col_grafico2:
        st.subheader("Distribuição de riscos")

        if not st.session_state.riscos.empty:
            distribuicao = (
                st.session_state.riscos["Nível"]
                .value_counts()
                .reindex(["Crítico", "Alto", "Médio", "Baixo"], fill_value=0)
                .reset_index()
            )
            distribuicao.columns = ["Nível", "Quantidade"]

            fig_riscos = px.bar(
                distribuicao,
                x="Nível",
                y="Quantidade",
                color="Nível",
                color_discrete_map={
                    "Crítico": "#c62828",
                    "Alto": "#ef6c00",
                    "Médio": "#f9a825",
                    "Baixo": "#2e7d32",
                },
                text_auto=True,
            )
            fig_riscos.update_layout(
                showlegend=False,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
            )
            st.plotly_chart(fig_riscos, use_container_width=True)
        else:
            st.info("Cadastre riscos para visualizar a distribuição.")

    st.subheader("Prioridades recomendadas")

    recomendacoes = obter_recomendacoes()

    if recomendacoes:
        for item in recomendacoes[:3]:
            st.markdown(
                f"""
                <div class="warning-box">
                    <strong>{item["Dimensão"]} — nota {item["Maturidade"]}/5</strong><br>
                    {item["Recomendação"]}
                </div><br>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.success("Nenhuma dimensão abaixo do nível mínimo recomendado.")


# ============================================================
# ASSESSMENT
# ============================================================

elif menu == "Assessment NIST CSF":
    cabecalho(
        "Assessment NIST CSF 2.0",
        "Avaliação estruturada de maturidade nas seis funções do framework.",
    )

    preenchidas = sum(
        1
        for dimensao, perguntas in PERGUNTAS_NIST.items()
        for indice, _ in enumerate(perguntas)
        if f"{dimensao}_{indice}" in st.session_state.assessment
    )

    total_perguntas = sum(len(p) for p in PERGUNTAS_NIST.values())
    progresso = preenchidas / total_perguntas if total_perguntas else 0

    st.write(f"Progresso: **{preenchidas}/{total_perguntas} respostas**")
    st.progress(progresso)

    abas = st.tabs(DIMENSOES)

    for aba, dimensao in zip(abas, DIMENSOES):
        with aba:
            st.markdown(
                f'<span class="ctr-badge">NIST CSF — {dimensao}</span>',
                unsafe_allow_html=True,
            )
            st.write("")

            for indice, pergunta in enumerate(PERGUNTAS_NIST[dimensao]):
                chave = f"{dimensao}_{indice}"
                valor_atual = st.session_state.assessment.get(
                    chave,
                    "Não implementado",
                )

                st.markdown(
                    f"""
                    <div class="ctr-card">
                        <strong>{indice + 1}. {pergunta}</strong>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                resposta = st.selectbox(
                    "Nível de implementação",
                    list(OPCOES_MATURIDADE.keys()),
                    index=list(OPCOES_MATURIDADE.keys()).index(valor_atual),
                    key=f"select_{chave}",
                )

                st.session_state.assessment[chave] = resposta

    st.subheader("Resultado atual")

    resultados = calcular_assessment()
    colunas = st.columns(6)

    for coluna, dimensao in zip(colunas, DIMENSOES):
        coluna.metric(dimensao, f"{resultados[dimensao]:.2f}/5")

    if st.button("Limpar assessment", type="secondary"):
        st.session_state.assessment = {}

        for dimensao, perguntas in PERGUNTAS_NIST.items():
            for indice, _ in enumerate(perguntas):
                chave_widget = f"select_{dimensao}_{indice}"
                if chave_widget in st.session_state:
                    del st.session_state[chave_widget]

        st.rerun()


# ============================================================
# VULNERABILIDADES
# ============================================================

elif menu == "Vulnerabilidades":
    cabecalho(
        "Gestão de Vulnerabilidades",
        "Importe resultados de ferramentas como Nessus, OpenVAS ou planilhas internas.",
    )

    arquivo = st.file_uploader(
        "Importar arquivo CSV",
        type=["csv"],
        help="O sistema aceita qualquer CSV e tenta identificar as colunas disponíveis.",
    )

    if arquivo:
        try:
            vulnerabilidades = pd.read_csv(arquivo)

            st.success(
                f"Arquivo carregado: {len(vulnerabilidades)} registros."
            )
            st.dataframe(
                vulnerabilidades,
                use_container_width=True,
                hide_index=True,
            )

            colunas = vulnerabilidades.columns.tolist()
            coluna_severidade = st.selectbox(
                "Coluna que representa a severidade",
                ["Não selecionar"] + colunas,
            )

            if coluna_severidade != "Não selecionar":
                resumo = (
                    vulnerabilidades[coluna_severidade]
                    .astype(str)
                    .value_counts()
                    .reset_index()
                )
                resumo.columns = ["Severidade", "Quantidade"]

                fig = px.bar(
                    resumo,
                    x="Severidade",
                    y="Quantidade",
                    color="Severidade",
                    text_auto=True,
                )
                fig.update_layout(showlegend=False)
                st.plotly_chart(fig, use_container_width=True)

            st.download_button(
                "Baixar vulnerabilidades tratadas",
                vulnerabilidades.to_csv(index=False).encode("utf-8-sig"),
                file_name="vulnerabilidades_ctr_defense.csv",
                mime="text/csv",
            )

        except Exception as erro:
            st.error(f"Não foi possível processar o CSV: {erro}")

    else:
        st.info(
            "Faça upload de um CSV para iniciar a análise de vulnerabilidades."
        )


# ============================================================
# MATRIZ DE RISCOS
# ============================================================

elif menu == "Matriz de Riscos":
    cabecalho(
        "Matriz de Riscos",
        "Registro e priorização com base em probabilidade e impacto.",
    )

    with st.expander("Adicionar novo risco", expanded=True):
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
                "Estratégia de tratamento",
                ["Mitigar", "Evitar", "Transferir", "Aceitar"],
            )

            enviado = st.form_submit_button(
                "Adicionar risco",
                type="primary",
            )

            if enviado:
                if not risco.strip():
                    st.error("Informe a descrição do risco.")
                else:
                    pontuacao, nivel = calcular_nivel_risco(
                        probabilidade,
                        impacto,
                    )

                    nova_linha = pd.DataFrame(
                        [
                            {
                                "ID": len(st.session_state.riscos) + 1,
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

                    st.session_state.riscos = pd.concat(
                        [st.session_state.riscos, nova_linha],
                        ignore_index=True,
                    )

                    st.success(
                        f"Risco adicionado com nível {nivel} ({pontuacao})."
                    )
                    st.rerun()

    if not st.session_state.riscos.empty:
        st.subheader("Registro de riscos")

        st.dataframe(
            st.session_state.riscos,
            use_container_width=True,
            hide_index=True,
        )

        st.subheader("Heatmap 5 × 5")

        matriz = pd.DataFrame(
            0,
            index=[5, 4, 3, 2, 1],
            columns=[1, 2, 3, 4, 5],
        )

        for _, linha in st.session_state.riscos.iterrows():
            prob = int(linha["Probabilidade"])
            imp = int(linha["Impacto"])
            matriz.loc[prob, imp] += 1

        texto = matriz.astype(str)

        fig_heatmap = go.Figure(
            data=go.Heatmap(
                z=[
                    [5, 10, 15, 20, 25],
                    [4, 8, 12, 16, 20],
                    [3, 6, 9, 12, 15],
                    [2, 4, 6, 8, 10],
                    [1, 2, 3, 4, 5],
                ],
                x=[1, 2, 3, 4, 5],
                y=[5, 4, 3, 2, 1],
                text=texto.values,
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
                hovertemplate=(
                    "Impacto: %{x}<br>"
                    "Probabilidade: %{y}<br>"
                    "%{text}<extra></extra>"
                ),
            )
        )

        fig_heatmap.update_layout(
            xaxis_title="Impacto",
            yaxis_title="Probabilidade",
            height=500,
        )
        st.plotly_chart(fig_heatmap, use_container_width=True)

        col_download, col_limpar = st.columns([3, 1])

        col_download.download_button(
            "Exportar riscos em CSV",
            st.session_state.riscos.to_csv(index=False).encode("utf-8-sig"),
            file_name="matriz_de_riscos.csv",
            mime="text/csv",
        )

        if col_limpar.button("Excluir todos os riscos"):
            st.session_state.riscos = st.session_state.riscos.iloc[0:0]
            st.rerun()
    else:
        st.info("Nenhum risco cadastrado.")


# ============================================================
# PLANO DE AÇÃO
# ============================================================

elif menu == "Plano de Ação":
    cabecalho(
        "Plano de Ação e Roadmap",
        "Transforme riscos e lacunas de conformidade em iniciativas acompanháveis.",
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
            responsavel_acao = col3.text_input("Responsável")

            col4, col5 = st.columns(2)
            inicio = col4.date_input("Data de início", value=date.today())
            prazo = col5.date_input("Prazo", value=date.today())

            status = st.selectbox("Status", STATUS_ACAO)
            progresso_acao = st.slider("Progresso", 0, 100, 0, step=5)

            enviado = st.form_submit_button(
                "Adicionar ao roadmap",
                type="primary",
            )

            if enviado:
                if not acao.strip():
                    st.error("Informe a ação.")
                elif prazo < inicio:
                    st.error("O prazo não pode ser anterior à data de início.")
                else:
                    nova_acao = pd.DataFrame(
                        [
                            {
                                "ID": len(st.session_state.acoes) + 1,
                                "Ação": acao.strip(),
                                "Origem": origem,
                                "Prioridade": prioridade,
                                "Responsável": responsavel_acao.strip(),
                                "Início": inicio,
                                "Prazo": prazo,
                                "Status": status,
                                "Progresso": progresso_acao,
                            }
                        ]
                    )

                    st.session_state.acoes = pd.concat(
                        [st.session_state.acoes, nova_acao],
                        ignore_index=True,
                    )
                    st.success("Ação adicionada.")
                    st.rerun()

    if not st.session_state.acoes.empty:
        st.dataframe(
            st.session_state.acoes,
            use_container_width=True,
            hide_index=True,
        )

        dados_gantt = st.session_state.acoes.copy()
        dados_gantt["Início"] = pd.to_datetime(dados_gantt["Início"])
        dados_gantt["Prazo"] = pd.to_datetime(dados_gantt["Prazo"])

        fig_gantt = px.timeline(
            dados_gantt,
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

        fig_gantt.update_yaxes(autorange="reversed")
        fig_gantt.update_layout(height=max(400, len(dados_gantt) * 55))
        st.plotly_chart(fig_gantt, use_container_width=True)

        col1, col2 = st.columns([3, 1])

        col1.download_button(
            "Exportar plano de ação",
            st.session_state.acoes.to_csv(index=False).encode("utf-8-sig"),
            file_name="plano_de_acao.csv",
            mime="text/csv",
        )

        if col2.button("Excluir todas as ações"):
            st.session_state.acoes = st.session_state.acoes.iloc[0:0]
            st.rerun()
    else:
        st.info("Nenhuma ação cadastrada.")


# ============================================================
# COMPLIANCE
# ============================================================

elif menu == "Compliance":
    cabecalho(
        "Adequação e Compliance",
        "Acompanhamento simplificado de NIST CSF, ISO 27001 e LGPD.",
    )

    framework = st.selectbox(
        "Framework",
        list(FRAMEWORKS.keys()),
    )

    st.subheader(f"Controles — {framework}")

    pontuacoes = []

    for indice, controle in enumerate(FRAMEWORKS[framework]):
        chave = f"{framework}_{indice}"

        col1, col2 = st.columns([3, 2])
        col1.markdown(f"**{controle}**")

        valor_anterior = st.session_state.compliance.get(chave, 0)

        valor = col2.select_slider(
            "Percentual de atendimento",
            options=[0, 25, 50, 75, 100],
            value=valor_anterior,
            key=f"compliance_widget_{chave}",
            label_visibility="collapsed",
        )

        st.session_state.compliance[chave] = valor
        pontuacoes.append(valor)

    media_compliance = (
        round(sum(pontuacoes) / len(pontuacoes), 1)
        if pontuacoes
        else 0
    )

    st.subheader("Resultado")
    st.progress(media_compliance / 100)
    st.metric("Nível de conformidade", f"{media_compliance}%")

    if media_compliance < 40:
        st.error("Nível crítico: recomenda-se iniciar um plano estruturado de adequação.")
    elif media_compliance < 70:
        st.warning("Nível intermediário: ainda existem lacunas relevantes.")
    else:
        st.success("Bom nível de conformidade. Mantenha evidências e melhoria contínua.")


# ============================================================
# REUNIÕES
# ============================================================

elif menu == "Reuniões":
    cabecalho(
        "Reuniões Executivas",
        "Registre decisões, responsáveis e próximos passos da consultoria.",
    )

    with st.form("form_reuniao", clear_on_submit=True):
        col1, col2 = st.columns(2)
        data_reuniao = col1.date_input("Data", value=date.today())
        titulo_reuniao = col2.text_input("Título da reunião")

        participantes = st.text_input("Participantes")
        resumo = st.text_area("Resumo da reunião", height=120)
        decisoes = st.text_area("Decisões tomadas", height=100)
        proximos_passos = st.text_area("Próximos passos", height=100)

        enviado = st.form_submit_button(
            "Registrar reunião",
            type="primary",
        )

        if enviado:
            if not titulo_reuniao.strip():
                st.error("Informe o título da reunião.")
            else:
                nova_reuniao = pd.DataFrame(
                    [
                        {
                            "Data": data_reuniao,
                            "Título": titulo_reuniao.strip(),
                            "Participantes": participantes.strip(),
                            "Resumo": resumo.strip(),
                            "Decisões": decisoes.strip(),
                            "Próximos passos": proximos_passos.strip(),
                        }
                    ]
                )

                st.session_state.reunioes = pd.concat(
                    [st.session_state.reunioes, nova_reuniao],
                    ignore_index=True,
                )
                st.success("Reunião registrada.")
                st.rerun()

    if not st.session_state.reunioes.empty:
        st.dataframe(
            st.session_state.reunioes,
            use_container_width=True,
            hide_index=True,
        )

        st.download_button(
            "Exportar atas em CSV",
            st.session_state.reunioes.to_csv(index=False).encode("utf-8-sig"),
            file_name="atas_de_reuniao.csv",
            mime="text/csv",
        )
    else:
        st.info("Nenhuma reunião registrada.")


# ============================================================
# RELATÓRIOS
# ============================================================

elif menu == "Relatórios":
    cabecalho(
        "Relatórios e Entregáveis",
        "Gere documentos executivos para apresentação e acompanhamento do cliente.",
    )

    score = obter_score_geral()
    maturidade = classificar_maturidade(score)

    col1, col2, col3 = st.columns(3)
    col1.metric("Score geral", f"{score}%")
    col2.metric("Maturidade", maturidade)
    col3.metric(
        "Itens registrados",
        len(st.session_state.riscos) + len(st.session_state.acoes),
    )

    st.subheader("Relatório executivo em PDF")

    st.write(
        "O documento inclui maturidade NIST, recomendações prioritárias, "
        "registro de riscos e plano de ação."
    )

    try:
        pdf = gerar_pdf_executivo(
            st.session_state.get("empresa", ""),
            st.session_state.get("consultor", ""),
        )

        nome_empresa = (
            st.session_state.get("empresa", "cliente")
            .strip()
            .lower()
            .replace(" ", "_")
        ) or "cliente"

        st.download_button(
            "Gerar e baixar relatório executivo",
            data=pdf,
            file_name=f"relatorio_ctr_defense_{nome_empresa}.pdf",
            mime="application/pdf",
            type="primary",
        )

    except Exception as erro:
        st.error(f"Não foi possível gerar o PDF: {erro}")

    st.subheader("Exportações individuais")

    col1, col2, col3 = st.columns(3)

    col1.download_button(
        "Matriz de riscos",
        st.session_state.riscos.to_csv(index=False).encode("utf-8-sig"),
        file_name="riscos.csv",
        mime="text/csv",
        use_container_width=True,
    )

    col2.download_button(
        "Plano de ação",
        st.session_state.acoes.to_csv(index=False).encode("utf-8-sig"),
        file_name="acoes.csv",
        mime="text/csv",
        use_container_width=True,
    )

    col3.download_button(
        "Atas de reunião",
        st.session_state.reunioes.to_csv(index=False).encode("utf-8-sig"),
        file_name="reunioes.csv",
        mime="text/csv",
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
