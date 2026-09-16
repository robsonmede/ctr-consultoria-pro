import io
import re
import unicodedata
from datetime import date, datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ============================================================
# CONFIGURAÇÃO DA PÁGINA
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
            --ctr-secondary: #0b3040;
            --ctr-text: #102f3b;
            --ctr-muted: #5d7480;
            --ctr-bg: #eef4f7;
            --ctr-card: #ffffff;
            --ctr-border: #cbdce3;
        }

        .stApp {
            background:
                linear-gradient(
                    135deg,
                    #eef4f7 0%,
                    #f8fbfc 50%,
                    #e6f0f4 100%
                );
            color: var(--ctr-text);
        }

        section[data-testid="stSidebar"] {
            background:
                linear-gradient(
                    180deg,
                    #081f2c 0%,
                    #0b3040 55%,
                    #047f9e 140%
                );
        }

        section[data-testid="stSidebar"] * {
            color: #f5fbfd !important;
        }

        section[data-testid="stSidebar"] input {
            color: #102f3b !important;
            background-color: #ffffff !important;
        }

        section[data-testid="stSidebar"]
        div[data-baseweb="select"] > div {
            color: #102f3b !important;
            background-color: #ffffff !important;
        }

        h1, h2, h3, h4, h5, h6,
        p, label, span {
            color: var(--ctr-text);
        }

        .ctr-header {
            padding: 1.25rem 1.4rem;
            margin-bottom: 1rem;
            border: 1px solid var(--ctr-border);
            border-left: 6px solid var(--ctr-primary);
            border-radius: 14px;
            background: rgba(255, 255, 255, 0.94);
            box-shadow: 0 8px 24px rgba(11, 48, 64, 0.07);
        }

        .ctr-header h2 {
            margin: 0;
            color: var(--ctr-secondary);
        }

        .ctr-header p {
            margin: 0.4rem 0 0 0;
            color: var(--ctr-muted);
        }

        .question-card {
            padding: 0.85rem 1rem;
            margin: 0.6rem 0 0.25rem 0;
            border: 1px solid var(--ctr-border);
            border-left: 5px solid var(--ctr-primary);
            border-radius: 10px;
            background-color: #ffffff;
            color: var(--ctr-text);
        }

        .info-card {
            padding: 1rem;
            border: 1px solid var(--ctr-border);
            border-radius: 12px;
            background-color: #ffffff;
            box-shadow: 0 5px 18px rgba(11, 48, 64, 0.06);
        }

        div[data-testid="stMetric"] {
            padding: 1rem;
            border: 1px solid var(--ctr-border);
            border-radius: 12px;
            background-color: #ffffff;
            box-shadow: 0 5px 18px rgba(11, 48, 64, 0.06);
        }

        div[data-testid="stTextInput"] input,
        div[data-testid="stTextArea"] textarea,
        div[data-testid="stNumberInput"] input,
        div[data-baseweb="select"] > div {
            color: var(--ctr-text) !important;
            background-color: #ffffff !important;
            border-color: var(--ctr-border) !important;
        }

        div[role="listbox"],
        div[role="option"],
        ul[role="listbox"] {
            color: var(--ctr-text) !important;
            background-color: #ffffff !important;
        }

        div[role="option"]:hover {
            background-color: #e6f3f6 !important;
        }

        div[data-testid="stExpander"] {
            background-color: #ffffff;
            border-color: var(--ctr-border);
        }

        .stButton > button,
        .stDownloadButton > button {
            border-radius: 8px;
            border: 1px solid var(--ctr-primary);
        }

        .stButton > button[kind="primary"] {
            background-color: var(--ctr-primary);
            color: #ffffff;
        }

        div[data-testid="stDataFrame"],
        div[data-testid="stTable"] {
            background-color: #ffffff;
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

OPCOES_MATURIDADE = {
    "Não implementado": 0,
    "Inicial": 1,
    "Básico": 2,
    "Definido": 3,
    "Gerenciado": 4,
    "Otimizado": 5,
}

PERGUNTAS_NIST = {
    "Governar": [
        "A organização possui uma política formal de segurança da informação?",
        "Papéis e responsabilidades de cibersegurança estão documentados?",
        "Os riscos cibernéticos são considerados nas decisões estratégicas?",
        "Fornecedores são avaliados quanto aos riscos de segurança?",
        "A liderança acompanha indicadores de segurança periodicamente?",
    ],
    "Identificar": [
        "Existe um inventário atualizado de ativos de hardware e software?",
        "Dados críticos estão identificados e classificados?",
        "Vulnerabilidades são identificadas periodicamente?",
        "A organização mantém um registro formal de riscos?",
        "Dependências e serviços críticos estão documentados?",
    ],
    "Proteger": [
        "Controles de acesso seguem o princípio do menor privilégio?",
        "Autenticação multifator é utilizada em acessos críticos?",
        "Colaboradores recebem treinamento de segurança?",
        "Backups são protegidos contra alteração e exclusão indevida?",
        "Existe processo formal de gestão de patches?",
    ],
    "Detectar": [
        "Logs de sistemas críticos são centralizados e monitorados?",
        "Há alertas para atividades suspeitas?",
        "Eventos de segurança são analisados por responsáveis definidos?",
        "Existe monitoramento de endpoints e rede?",
        "As regras de detecção são revisadas periodicamente?",
    ],
    "Responder": [
        "Existe um plano documentado de resposta a incidentes?",
        "O plano define responsáveis, contatos e escalonamento?",
        "Incidentes são registrados e classificados?",
        "São realizados exercícios ou simulações de incidentes?",
        "Existe um processo de comunicação durante crises?",
    ],
    "Recuperar": [
        "Existe um plano de continuidade e recuperação?",
        "Os backups são testados periodicamente?",
        "Objetivos de recuperação RTO e RPO estão definidos?",
        "Lições aprendidas são incorporadas após incidentes?",
        "A restauração dos principais serviços é testada?",
    ],
}

FRAMEWORKS = {
    "NIST CSF 2.0": [
        "Governança e estratégia de segurança",
        "Gestão de ativos e riscos",
        "Proteção de identidades e acessos",
        "Monitoramento e detecção",
        "Resposta a incidentes",
        "Recuperação e continuidade",
    ],
    "ISO 27001": [
        "Contexto da organização",
        "Liderança e política de segurança",
        "Planejamento e avaliação de riscos",
        "Suporte e conscientização",
        "Operação dos controles",
        "Avaliação de desempenho",
        "Melhoria contínua",
    ],
    "LGPD": [
        "Mapeamento de dados pessoais",
        "Bases legais de tratamento",
        "Atendimento aos direitos dos titulares",
        "Gestão de operadores e terceiros",
        "Segurança dos dados pessoais",
        "Resposta a incidentes de privacidade",
        "Governança e atuação do encarregado",
    ],
}

COLUNAS_RISCOS = [
    "ID",
    "Risco",
    "Categoria",
    "Probabilidade",
    "Impacto",
    "Nível",
    "Tratamento",
    "Responsável",
    "Status",
]

COLUNAS_ACOES = [
    "ID",
    "Ação",
    "Origem",
    "Prioridade",
    "Responsável",
    "Prazo",
    "Status",
]

COLUNAS_REUNIOES = [
    "ID",
    "Data",
    "Título",
    "Participantes",
    "Notas",
]

# ============================================================
# ESTADO E FUNÇÕES AUXILIARES
# ============================================================


def criar_dados_organizacao():
    return {
        "assessment": {},
        "riscos": [],
        "acoes": [],
        "compliance": {},
        "reunioes": [],
    }


def inicializar_estado():
    if "organizacoes" not in st.session_state:
        st.session_state.organizacoes = {}

    if "organizacao_ativa_id" not in st.session_state:
        st.session_state.organizacao_ativa_id = None


def normalizar_id(texto):
    texto = unicodedata.normalize("NFKD", texto)
    texto = texto.encode("ascii", "ignore").decode("ascii")
    texto = re.sub(r"[^a-zA-Z0-9]+", "-", texto.lower()).strip("-")
    return texto or f"organizacao-{int(datetime.now().timestamp())}"


def obter_organizacao_ativa():
    organizacao_id = st.session_state.get("organizacao_ativa_id")

    if not organizacao_id:
        return None

    return st.session_state.organizacoes.get(organizacao_id)


def obter_dados_ativos():
    organizacao = obter_organizacao_ativa()

    if organizacao is None:
        return None

    if "dados" not in organizacao:
        organizacao["dados"] = criar_dados_organizacao()

    return organizacao["dados"]


def cabecalho(titulo, subtitulo):
    st.markdown(
        f"""
        <div class="ctr-header">
            <h2>{titulo}</h2>
            <p>{subtitulo}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def dataframe_lista(lista, colunas):
    if not lista:
        return pd.DataFrame(columns=colunas)

    df = pd.DataFrame(lista)

    for coluna in colunas:
        if coluna not in df.columns:
            df[coluna] = ""

    return df[colunas]


def calcular_assessment(dados):
    resultados = {}

    for dimensao in DIMENSOES:
        valores = []

        for indice, _ in enumerate(PERGUNTAS_NIST[dimensao]):
            chave = f"{dimensao}_{indice}"
            resposta = dados["assessment"].get(
                chave,
                "Não implementado",
            )
            valores.append(OPCOES_MATURIDADE.get(resposta, 0))

        resultados[dimensao] = (
            sum(valores) / len(valores) if valores else 0
        )

    resultados["Geral"] = (
        sum(resultados[dimensao] for dimensao in DIMENSOES)
        / len(DIMENSOES)
    )

    return resultados


def classificar_maturidade(pontuacao):
    if pontuacao < 1:
        return "Não implementado"
    if pontuacao < 2:
        return "Inicial"
    if pontuacao < 3:
        return "Básico"
    if pontuacao < 4:
        return "Definido"
    if pontuacao < 4.75:
        return "Gerenciado"
    return "Otimizado"


def classificar_risco(probabilidade, impacto):
    valor = probabilidade * impacto

    if valor >= 20:
        return "Crítico"
    if valor >= 12:
        return "Alto"
    if valor >= 6:
        return "Médio"
    return "Baixo"


def cor_risco(nivel):
    return {
        "Crítico": "#b91c1c",
        "Alto": "#ea580c",
        "Médio": "#eab308",
        "Baixo": "#16a34a",
    }.get(nivel, "#64748b")


def proximo_id(registros):
    if not registros:
        return 1

    ids = []

    for registro in registros:
        try:
            ids.append(int(registro.get("ID", 0)))
        except (TypeError, ValueError):
            pass

    return max(ids, default=0) + 1


def remover_registro(lista, registro_id):
    return [
        item
        for item in lista
        if str(item.get("ID")) != str(registro_id)
    ]


def gerar_csv_completo(organizacao, dados):
    buffer = io.StringIO()

    buffer.write("CTR DEFENSE - RELATORIO CONSOLIDADO\n")
    buffer.write(f"Organizacao;{organizacao['nome']}\n")
    buffer.write(f"Segmento;{organizacao.get('segmento', '')}\n")
    buffer.write(f"Responsavel;{organizacao.get('responsavel', '')}\n")
    buffer.write(f"Data;{datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n")

    resultados = calcular_assessment(dados)

    buffer.write("MATURIDADE NIST CSF 2.0\n")
    buffer.write("Dimensao;Pontuacao;Nivel\n")

    for dimensao in DIMENSOES:
        pontuacao = resultados[dimensao]
        buffer.write(
            f"{dimensao};{pontuacao:.2f};"
            f"{classificar_maturidade(pontuacao)}\n"
        )

    buffer.write(
        f"Geral;{resultados['Geral']:.2f};"
        f"{classificar_maturidade(resultados['Geral'])}\n\n"
    )

    secoes = [
        ("RISCOS", dados["riscos"], COLUNAS_RISCOS),
        ("PLANO DE ACAO", dados["acoes"], COLUNAS_ACOES),
        ("REUNIOES", dados["reunioes"], COLUNAS_REUNIOES),
    ]

    for titulo, registros, colunas in secoes:
        buffer.write(f"{titulo}\n")
        df = dataframe_lista(registros, colunas)
        buffer.write(df.to_csv(index=False, sep=";"))
        buffer.write("\n")

    buffer.write("COMPLIANCE\n")
    buffer.write("Controle;Percentual\n")

    for chave, valor in dados["compliance"].items():
        buffer.write(f"{chave};{valor}\n")

    return buffer.getvalue().encode("utf-8-sig")


def gerar_pdf(organizacao, dados):
    try:
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
    except ImportError:
        return None

    buffer = io.BytesIO()
    documento = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=1.2 * cm,
        leftMargin=1.2 * cm,
        topMargin=1.2 * cm,
        bottomMargin=1.2 * cm,
    )

    estilos = getSampleStyleSheet()
    estilos.add(
        ParagraphStyle(
            name="TituloCTR",
            parent=estilos["Title"],
            textColor=colors.HexColor("#0b3040"),
            alignment=TA_CENTER,
            fontSize=23,
            leading=28,
        )
    )

    elementos = [
        Paragraph("CTR DEFENSE", estilos["TituloCTR"]),
        Paragraph(
            "Relatório Executivo de Cibersegurança",
            estilos["Heading2"],
        ),
        Spacer(1, 0.5 * cm),
        Paragraph(
            f"<b>Organização:</b> {organizacao['nome']}",
            estilos["BodyText"],
        ),
        Paragraph(
            f"<b>Segmento:</b> {organizacao.get('segmento', '-')}",
            estilos["BodyText"],
        ),
        Paragraph(
            f"<b>Responsável:</b> "
            f"{organizacao.get('responsavel', '-')}",
            estilos["BodyText"],
        ),
        Paragraph(
            f"<b>Emissão:</b> "
            f"{datetime.now().strftime('%d/%m/%Y %H:%M')}",
            estilos["BodyText"],
        ),
        Spacer(1, 0.7 * cm),
    ]

    resultados = calcular_assessment(dados)
    elementos.append(Paragraph("Maturidade NIST CSF 2.0", estilos["Heading2"]))

    tabela_maturidade = [["Dimensão", "Pontuação", "Nível"]]

    for dimensao in DIMENSOES:
        pontuacao = resultados[dimensao]
        tabela_maturidade.append(
            [
                dimensao,
                f"{pontuacao:.2f}/5",
                classificar_maturidade(pontuacao),
            ]
        )

    tabela_maturidade.append(
        [
            "Geral",
            f"{resultados['Geral']:.2f}/5",
            classificar_maturidade(resultados["Geral"]),
        ]
    )

    tabela = Table(
        tabela_maturidade,
        colWidths=[8 * cm, 4 * cm, 6 * cm],
    )
    tabela.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0b3040")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#dceff4")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#a8c3cc")),
                ("ALIGN", (1, 1), (1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 1), (-1, -1), 6),
            ]
        )
    )

    elementos.extend([tabela, Spacer(1, 0.7 * cm)])
    elementos.append(Paragraph("Registro de Riscos", estilos["Heading2"]))

    if dados["riscos"]:
        tabela_riscos = [
            ["ID", "Risco", "Prob.", "Impacto", "Nível", "Status"]
        ]

        for risco in dados["riscos"]:
            tabela_riscos.append(
                [
                    str(risco.get("ID", "")),
                    Paragraph(
                        str(risco.get("Risco", "")),
                        estilos["BodyText"],
                    ),
                    str(risco.get("Probabilidade", "")),
                    str(risco.get("Impacto", "")),
                    str(risco.get("Nível", "")),
                    str(risco.get("Status", "")),
                ]
            )

        tabela = Table(
            tabela_riscos,
            colWidths=[
                1.2 * cm,
                11 * cm,
                2 * cm,
                2 * cm,
                2.5 * cm,
                3 * cm,
            ],
            repeatRows=1,
        )
        tabela.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.HexColor("#0b3040"),
                    ),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ]
            )
        )
        elementos.append(tabela)
    else:
        elementos.append(
            Paragraph(
                "Nenhum risco registrado.",
                estilos["BodyText"],
            )
        )

    elementos.append(PageBreak())
    elementos.append(Paragraph("Plano de Ação", estilos["Heading2"]))

    if dados["acoes"]:
        tabela_acoes = [
            ["ID", "Ação", "Prioridade", "Responsável", "Prazo", "Status"]
        ]

        for acao in dados["acoes"]:
            tabela_acoes.append(
                [
                    str(acao.get("ID", "")),
                    Paragraph(
                        str(acao.get("Ação", "")),
                        estilos["BodyText"],
                    ),
                    str(acao.get("Prioridade", "")),
                    str(acao.get("Responsável", "")),
                    str(acao.get("Prazo", "")),
                    str(acao.get("Status", "")),
                ]
            )

        tabela = Table(
            tabela_acoes,
            colWidths=[
                1.2 * cm,
                10 * cm,
                2.5 * cm,
                4 * cm,
                3 * cm,
                3.5 * cm,
            ],
            repeatRows=1,
        )
        tabela.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.HexColor("#0b3040"),
                    ),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ]
            )
        )
        elementos.append(tabela)
    else:
        elementos.append(
            Paragraph(
                "Nenhuma ação registrada.",
                estilos["BodyText"],
            )
        )

    documento.build(elementos)
    buffer.seek(0)
    return buffer.getvalue()


# ============================================================
# ORGANIZAÇÕES
# ============================================================


def modulo_organizacoes():
    cabecalho(
        "Organizações",
        "Cadastre e gerencie os clientes atendidos pela CTR DEFENSE.",
    )

    with st.form("form_nova_organizacao", clear_on_submit=True):
        st.subheader("Cadastrar organização")

        col1, col2 = st.columns(2)

        nome = col1.text_input("Nome da organização")
        segmento = col2.text_input("Segmento")

        col3, col4 = st.columns(2)

        responsavel = col3.text_input("Responsável")
        email = col4.text_input("E-mail")

        cadastrar = st.form_submit_button(
            "Cadastrar organização",
            type="primary",
            use_container_width=True,
        )

        if cadastrar:
            nome_limpo = nome.strip()

            if not nome_limpo:
                st.error("Informe o nome da organização.")
            else:
                base_id = normalizar_id(nome_limpo)
                organizacao_id = base_id
                contador = 2

                while organizacao_id in st.session_state.organizacoes:
                    organizacao_id = f"{base_id}-{contador}"
                    contador += 1

                st.session_state.organizacoes[organizacao_id] = {
                    "id": organizacao_id,
                    "nome": nome_limpo,
                    "segmento": segmento.strip(),
                    "responsavel": responsavel.strip(),
                    "email": email.strip(),
                    "criado_em": datetime.now().isoformat(),
                    "dados": criar_dados_organizacao(),
                }

                st.session_state.organizacao_ativa_id = organizacao_id
                st.success("Organização cadastrada com sucesso.")
                st.rerun()

    st.subheader("Organizações cadastradas")

    if not st.session_state.organizacoes:
        st.info("Nenhuma organização foi cadastrada.")
        return

    for organizacao_id, organizacao in list(
        st.session_state.organizacoes.items()
    ):
        ativa = (
            organizacao_id
            == st.session_state.get("organizacao_ativa_id")
        )

        with st.expander(
            f"{'✅ ' if ativa else ''}{organizacao['nome']}",
            expanded=ativa,
        ):
            col1, col2, col3 = st.columns([2, 2, 1])

            col1.write(
                f"**Segmento:** "
                f"{organizacao.get('segmento') or 'Não informado'}"
            )
            col1.write(
                f"**Responsável:** "
                f"{organizacao.get('responsavel') or 'Não informado'}"
            )
            col2.write(
                f"**E-mail:** "
                f"{organizacao.get('email') or 'Não informado'}"
            )
            col2.write(f"**ID:** `{organizacao_id}`")

            if col3.button(
                "Selecionar",
                key=f"selecionar_{organizacao_id}",
                use_container_width=True,
            ):
                st.session_state.organizacao_ativa_id = organizacao_id
                st.rerun()

            if col3.button(
                "Excluir",
                key=f"excluir_{organizacao_id}",
                use_container_width=True,
            ):
                del st.session_state.organizacoes[organizacao_id]

                if (
                    st.session_state.get("organizacao_ativa_id")
                    == organizacao_id
                ):
                    st.session_state.organizacao_ativa_id = None

                st.rerun()


# ============================================================
# DASHBOARD
# ============================================================


def modulo_dashboard():
    organizacao = obter_organizacao_ativa()
    dados = obter_dados_ativos()

    if organizacao is None or dados is None:
        st.warning("Cadastre ou selecione uma organização.")
        return

    cabecalho(
        f"Dashboard Executivo — {organizacao['nome']}",
        "Visão consolidada da maturidade, riscos e plano de ação.",
    )

    resultados = calcular_assessment(dados)
    riscos_criticos = sum(
        1
        for risco in dados["riscos"]
        if risco.get("Nível") == "Crítico"
        and risco.get("Status") != "Encerrado"
    )
    acoes_concluidas = sum(
        1
        for acao in dados["acoes"]
        if acao.get("Status") == "Concluída"
    )
    total_acoes = len(dados["acoes"])

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Maturidade geral",
        f"{resultados['Geral']:.2f}/5",
        classificar_maturidade(resultados["Geral"]),
    )
    col2.metric("Riscos registrados", len(dados["riscos"]))
    col3.metric("Riscos críticos", riscos_criticos)
    col4.metric(
        "Ações concluídas",
        f"{acoes_concluidas}/{total_acoes}",
    )

    col_grafico1, col_grafico2 = st.columns(2)

    with col_grafico1:
        radar = go.Figure()

        radar.add_trace(
            go.Scatterpolar(
                r=[resultados[d] for d in DIMENSOES],
                theta=DIMENSOES,
                fill="toself",
                name="Maturidade",
                line_color="#047f9e",
            )
        )

        radar.update_layout(
            title="Radar NIST CSF 2.0",
            polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
            showlegend=False,
            height=430,
            paper_bgcolor="rgba(255,255,255,0)",
        )

        st.plotly_chart(radar, use_container_width=True)

    with col_grafico2:
        df_maturidade = pd.DataFrame(
            {
                "Dimensão": DIMENSOES,
                "Pontuação": [resultados[d] for d in DIMENSOES],
            }
        )

        barras = px.bar(
            df_maturidade,
            x="Dimensão",
            y="Pontuação",
            range_y=[0, 5],
            color="Pontuação",
            color_continuous_scale=["#d9eef3", "#047f9e", "#0b3040"],
            title="Maturidade por dimensão",
        )
        barras.update_layout(
            coloraxis_showscale=False,
            height=430,
            paper_bgcolor="rgba(255,255,255,0)",
        )

        st.plotly_chart(barras, use_container_width=True)

    st.subheader("Distribuição de riscos")

    if dados["riscos"]:
        contagem = (
            pd.DataFrame(dados["riscos"])["Nível"]
            .value_counts()
            .reindex(
                ["Crítico", "Alto", "Médio", "Baixo"],
                fill_value=0,
            )
            .reset_index()
        )
        contagem.columns = ["Nível", "Quantidade"]

        pizza = px.pie(
            contagem,
            names="Nível",
            values="Quantidade",
            color="Nível",
            color_discrete_map={
                "Crítico": "#b91c1c",
                "Alto": "#ea580c",
                "Médio": "#eab308",
                "Baixo": "#16a34a",
            },
            hole=0.45,
        )
        st.plotly_chart(pizza, use_container_width=True)
    else:
        st.info("Nenhum risco registrado.")


# ============================================================
# ASSESSMENT
# ============================================================


def modulo_assessment():
    # Correção do NameError: contexto obtido no início do módulo.
    organizacao = obter_organizacao_ativa()
    dados = obter_dados_ativos()

    if organizacao is None or dados is None:
        st.error("Nenhuma organização ativa foi encontrada.")
        return

    assessment = dados["assessment"]

    cabecalho(
        "Assessment NIST CSF 2.0",
        "Avaliação de maturidade nas seis funções do framework.",
    )

    total = sum(len(perguntas) for perguntas in PERGUNTAS_NIST.values())

    preenchidas = sum(
        1
        for dimensao in DIMENSOES
        for indice, _ in enumerate(PERGUNTAS_NIST[dimensao])
        if f"{dimensao}_{indice}" in assessment
    )

    st.write(f"Progresso: **{preenchidas}/{total} respostas**")
    st.progress(min(preenchidas / total, 1.0))

    abas = st.tabs(DIMENSOES)

    for aba, dimensao in zip(abas, DIMENSOES):
        with aba:
            for indice, pergunta in enumerate(
                PERGUNTAS_NIST[dimensao]
            ):
                chave = f"{dimensao}_{indice}"
                resposta_atual = assessment.get(
                    chave,
                    "Não implementado",
                )

                if resposta_atual not in OPCOES_MATURIDADE:
                    resposta_atual = "Não implementado"

                st.markdown(
                    (
                        '<div class="question-card">'
                        f"<strong>{indice + 1}. {pergunta}</strong>"
                        "</div>"
                    ),
                    unsafe_allow_html=True,
                )

                opcoes = list(OPCOES_MATURIDADE.keys())

                resposta = st.selectbox(
                    "Nível de implementação",
                    options=opcoes,
                    index=opcoes.index(resposta_atual),
                    key=(
                        f"assessment_"
                        f"{organizacao['id']}_"
                        f"{chave}"
                    ),
                )

                assessment[chave] = resposta

    st.subheader("Resultado atual")

    resultados = calcular_assessment(dados)
    colunas = st.columns(6)

    for coluna, dimensao in zip(colunas, DIMENSOES):
        coluna.metric(
            dimensao,
            f"{resultados[dimensao]:.2f}/5",
        )

    st.metric(
        "Maturidade geral",
        f"{resultados['Geral']:.2f}/5",
        classificar_maturidade(resultados["Geral"]),
    )

    if st.button(
        "Limpar assessment",
        key=f"limpar_assessment_{organizacao['id']}",
    ):
        dados["assessment"] = {}
        prefixo = f"assessment_{organizacao['id']}_"

        chaves_para_remover = [
            chave_estado
            for chave_estado in list(st.session_state.keys())
            if str(chave_estado).startswith(prefixo)
        ]

        for chave_estado in chaves_para_remover:
            del st.session_state[chave_estado]

        st.rerun()


# ============================================================
# RISCOS
# ============================================================


def modulo_riscos():
    organizacao = obter_organizacao_ativa()
    dados = obter_dados_ativos()

    if organizacao is None or dados is None:
        st.error("Nenhuma organização ativa foi encontrada.")
        return

    cabecalho(
        "Matriz de Riscos",
        "Registre, classifique e acompanhe riscos cibernéticos.",
    )

    with st.form(
        f"form_risco_{organizacao['id']}",
        clear_on_submit=True,
    ):
        risco = st.text_area("Descrição do risco", height=90)

        col1, col2, col3 = st.columns(3)

        categoria = col1.selectbox(
            "Categoria",
            [
                "Governança",
                "Tecnologia",
                "Pessoas",
                "Processos",
                "Terceiros",
                "Privacidade",
            ],
        )
        probabilidade = col2.slider("Probabilidade", 1, 5, 3)
        impacto = col3.slider("Impacto", 1, 5, 3)

        col4, col5, col6 = st.columns(3)

        tratamento = col4.selectbox(
            "Tratamento",
            ["Mitigar", "Evitar", "Transferir", "Aceitar"],
        )
        responsavel = col5.text_input("Responsável")
        status = col6.selectbox(
            "Status",
            ["Ativo", "Em tratamento", "Monitorado", "Encerrado"],
        )

        adicionar = st.form_submit_button(
            "Adicionar risco",
            type="primary",
            use_container_width=True,
        )

        if adicionar:
            if not risco.strip():
                st.error("Descreva o risco.")
            else:
                nivel = classificar_risco(
                    probabilidade,
                    impacto,
                )

                dados["riscos"].append(
                    {
                        "ID": proximo_id(dados["riscos"]),
                        "Risco": risco.strip(),
                        "Categoria": categoria,
                        "Probabilidade": probabilidade,
                        "Impacto": impacto,
                        "Nível": nivel,
                        "Tratamento": tratamento,
                        "Responsável": responsavel.strip(),
                        "Status": status,
                    }
                )
                st.success("Risco registrado com sucesso.")
                st.rerun()

    df_riscos = dataframe_lista(
        dados["riscos"],
        COLUNAS_RISCOS,
    )

    st.subheader("Registro de riscos")
    st.dataframe(
        df_riscos,
        use_container_width=True,
        hide_index=True,
    )

    if dados["riscos"]:
        st.subheader("Heatmap de riscos")

        matriz = pd.DataFrame(
            0,
            index=[1, 2, 3, 4, 5],
            columns=[1, 2, 3, 4, 5],
        )

        for item in dados["riscos"]:
            prob = int(item["Probabilidade"])
            impacto = int(item["Impacto"])
            matriz.loc[prob, impacto] += 1

        heatmap = px.imshow(
            matriz,
            labels={
                "x": "Impacto",
                "y": "Probabilidade",
                "color": "Quantidade",
            },
            x=[1, 2, 3, 4, 5],
            y=[1, 2, 3, 4, 5],
            text_auto=True,
            color_continuous_scale=[
                [0.0, "#dcfce7"],
                [0.35, "#fef08a"],
                [0.65, "#fb923c"],
                [1.0, "#b91c1c"],
            ],
            aspect="auto",
        )

        st.plotly_chart(heatmap, use_container_width=True)

        col1, col2 = st.columns([2, 1])

        risco_id = col1.selectbox(
            "Selecione o risco para exclusão",
            options=[item["ID"] for item in dados["riscos"]],
            format_func=lambda valor: next(
                (
                    f"#{item['ID']} — {item['Risco']}"
                    for item in dados["riscos"]
                    if item["ID"] == valor
                ),
                str(valor),
            ),
            key=f"risco_exclusao_{organizacao['id']}",
        )

        if col2.button(
            "Excluir risco",
            key=f"excluir_risco_{organizacao['id']}",
            use_container_width=True,
        ):
            dados["riscos"] = remover_registro(
                dados["riscos"],
                risco_id,
            )
            st.rerun()

        st.download_button(
            "Baixar riscos em CSV",
            data=df_riscos.to_csv(
                index=False,
                sep=";",
            ).encode("utf-8-sig"),
            file_name=f"riscos-{organizacao['id']}.csv",
            mime="text/csv",
        )


# ============================================================
# PLANO DE AÇÃO
# ============================================================


def modulo_acoes():
    organizacao = obter_organizacao_ativa()
    dados = obter_dados_ativos()

    if organizacao is None or dados is None:
        st.error("Nenhuma organização ativa foi encontrada.")
        return

    cabecalho(
        "Plano de Ação",
        "Transforme os achados da consultoria em um roadmap executável.",
    )

    with st.form(
        f"form_acao_{organizacao['id']}",
        clear_on_submit=True,
    ):
        acao = st.text_area("Descrição da ação", height=90)

        col1, col2, col3 = st.columns(3)

        origem = col1.selectbox(
            "Origem",
            [
                "Assessment",
                "Risco",
                "Vulnerabilidade",
                "Compliance",
                "Reunião",
                "Outro",
            ],
        )
        prioridade = col2.selectbox(
            "Prioridade",
            ["Crítica", "Alta", "Média", "Baixa"],
        )
        responsavel = col3.text_input("Responsável")

        col4, col5 = st.columns(2)

        prazo = col4.date_input(
            "Prazo",
            value=date.today(),
            format="DD/MM/YYYY",
        )
        status = col5.selectbox(
            "Status",
            [
                "Não iniciada",
                "Em andamento",
                "Bloqueada",
                "Concluída",
            ],
        )

        adicionar = st.form_submit_button(
            "Adicionar ação",
            type="primary",
            use_container_width=True,
        )

        if adicionar:
            if not acao.strip():
                st.error("Descreva a ação.")
            else:
                dados["acoes"].append(
                    {
                        "ID": proximo_id(dados["acoes"]),
                        "Ação": acao.strip(),
                        "Origem": origem,
                        "Prioridade": prioridade,
                        "Responsável": responsavel.strip(),
                        "Prazo": prazo.strftime("%d/%m/%Y"),
                        "Status": status,
                    }
                )
                st.success("Ação adicionada com sucesso.")
                st.rerun()

    df_acoes = dataframe_lista(
        dados["acoes"],
        COLUNAS_ACOES,
    )

    st.subheader("Roadmap")
    st.dataframe(
        df_acoes,
        use_container_width=True,
        hide_index=True,
    )

    if dados["acoes"]:
        contagem_status = (
            df_acoes["Status"].value_counts().reset_index()
        )
        contagem_status.columns = ["Status", "Quantidade"]

        grafico = px.bar(
            contagem_status,
            x="Status",
            y="Quantidade",
            color="Status",
            title="Ações por status",
        )
        st.plotly_chart(grafico, use_container_width=True)

        col1, col2 = st.columns([2, 1])

        acao_id = col1.selectbox(
            "Selecione a ação para exclusão",
            options=[item["ID"] for item in dados["acoes"]],
            format_func=lambda valor: next(
                (
                    f"#{item['ID']} — {item['Ação']}"
                    for item in dados["acoes"]
                    if item["ID"] == valor
                ),
                str(valor),
            ),
            key=f"acao_exclusao_{organizacao['id']}",
        )

        if col2.button(
            "Excluir ação",
            key=f"excluir_acao_{organizacao['id']}",
            use_container_width=True,
        ):
            dados["acoes"] = remover_registro(
                dados["acoes"],
                acao_id,
            )
            st.rerun()

        st.download_button(
            "Baixar plano de ação em CSV",
            data=df_acoes.to_csv(
                index=False,
                sep=";",
            ).encode("utf-8-sig"),
            file_name=f"plano-acao-{organizacao['id']}.csv",
            mime="text/csv",
        )


# ============================================================
# COMPLIANCE
# ============================================================


def modulo_compliance():
    # Correção do NameError: contexto obtido no início do módulo.
    organizacao = obter_organizacao_ativa()
    dados = obter_dados_ativos()

    if organizacao is None or dados is None:
        st.error("Nenhuma organização ativa foi encontrada.")
        return

    cabecalho(
        "Adequação e Compliance",
        "Acompanhamento de NIST CSF 2.0, ISO 27001 e LGPD.",
    )

    framework = st.selectbox(
        "Framework",
        options=list(FRAMEWORKS.keys()),
        key=f"framework_{organizacao['id']}",
    )

    pontuacoes = []
    opcoes_percentual = [0, 25, 50, 75, 100]

    for indice, controle in enumerate(FRAMEWORKS[framework]):
        chave = f"{framework}_{indice}"
        col1, col2 = st.columns([3, 2])

        with col1:
            st.markdown(f"**{indice + 1}. {controle}**")

        valor_atual = dados["compliance"].get(chave, 0)

        try:
            valor_atual = int(valor_atual)
        except (TypeError, ValueError):
            valor_atual = 0

        if valor_atual not in opcoes_percentual:
            valor_atual = min(
                opcoes_percentual,
                key=lambda opcao: abs(opcao - valor_atual),
            )

        with col2:
            valor = st.select_slider(
                f"Conformidade de {controle}",
                options=opcoes_percentual,
                value=valor_atual,
                key=(
                    f"compliance_"
                    f"{organizacao['id']}_"
                    f"{chave}"
                ),
                label_visibility="collapsed",
            )

        dados["compliance"][chave] = valor
        pontuacoes.append(valor)

    media = (
        round(sum(pontuacoes) / len(pontuacoes), 1)
        if pontuacoes
        else 0.0
    )

    st.progress(min(max(media / 100, 0.0), 1.0))
    st.metric("Nível de conformidade", f"{media:.1f}%")

    if media < 40:
        st.error(
            "Nível crítico de conformidade. "
            "Priorize um plano de adequação."
        )
    elif media < 70:
        st.warning(
            "Existem lacunas relevantes de conformidade."
        )
    else:
        st.success(
            "A organização apresenta um bom nível de conformidade."
        )

    if st.button(
        "Limpar avaliação",
        key=f"limpar_compliance_{organizacao['id']}_{framework}",
    ):
        prefixo_dados = f"{framework}_"

        chaves_framework = [
            chave_salva
            for chave_salva in list(dados["compliance"].keys())
            if chave_salva.startswith(prefixo_dados)
        ]

        for chave_salva in chaves_framework:
            dados["compliance"].pop(chave_salva, None)

        prefixo_widget = (
            f"compliance_{organizacao['id']}_{framework}_"
        )

        chaves_widgets = [
            chave_estado
            for chave_estado in list(st.session_state.keys())
            if str(chave_estado).startswith(prefixo_widget)
        ]

        for chave_estado in chaves_widgets:
            del st.session_state[chave_estado]

        st.rerun()


# ============================================================
# REUNIÕES
# ============================================================


def modulo_reunioes():
    organizacao = obter_organizacao_ativa()
    dados = obter_dados_ativos()

    if organizacao is None or dados is None:
        st.error("Nenhuma organização ativa foi encontrada.")
        return

    cabecalho(
        "Relatórios de Reunião",
        "Registre reuniões, decisões e próximos passos.",
    )

    with st.form(
        f"form_reuniao_{organizacao['id']}",
        clear_on_submit=True,
    ):
        col1, col2 = st.columns([1, 2])

        data_reuniao = col1.date_input(
            "Data",
            value=date.today(),
            format="DD/MM/YYYY",
        )
        titulo = col2.text_input("Título da reunião")

        participantes = st.text_input("Participantes")
        notas = st.text_area(
            "Notas, decisões e próximos passos",
            height=180,
        )

        salvar = st.form_submit_button(
            "Salvar reunião",
            type="primary",
            use_container_width=True,
        )

        if salvar:
            if not titulo.strip():
                st.error("Informe o título da reunião.")
            else:
                dados["reunioes"].append(
                    {
                        "ID": proximo_id(dados["reunioes"]),
                        "Data": data_reuniao.strftime("%d/%m/%Y"),
                        "Título": titulo.strip(),
                        "Participantes": participantes.strip(),
                        "Notas": notas.strip(),
                    }
                )
                st.success("Reunião registrada com sucesso.")
                st.rerun()

    if not dados["reunioes"]:
        st.info("Nenhuma reunião registrada.")
        return

    for reuniao in reversed(dados["reunioes"]):
        with st.expander(
            f"{reuniao['Data']} — {reuniao['Título']}"
        ):
            st.write(
                f"**Participantes:** "
                f"{reuniao.get('Participantes') or 'Não informado'}"
            )
            st.write(reuniao.get("Notas") or "Sem notas.")

            if st.button(
                "Excluir reunião",
                key=(
                    f"excluir_reuniao_"
                    f"{organizacao['id']}_"
                    f"{reuniao['ID']}"
                ),
            ):
                dados["reunioes"] = remover_registro(
                    dados["reunioes"],
                    reuniao["ID"],
                )
                st.rerun()

    df_reunioes = dataframe_lista(
        dados["reunioes"],
        COLUNAS_REUNIOES,
    )

    st.download_button(
        "Baixar reuniões em CSV",
        data=df_reunioes.to_csv(
            index=False,
            sep=";",
        ).encode("utf-8-sig"),
        file_name=f"reunioes-{organizacao['id']}.csv",
        mime="text/csv",
    )


# ============================================================
# RELATÓRIOS
# ============================================================


def modulo_relatorios():
    organizacao = obter_organizacao_ativa()
    dados = obter_dados_ativos()

    if organizacao is None or dados is None:
        st.error("Nenhuma organização ativa foi encontrada.")
        return

    cabecalho(
        "Relatórios e Exportações",
        "Gere entregáveis executivos consolidados para o cliente.",
    )

    resultados = calcular_assessment(dados)

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Maturidade geral",
        f"{resultados['Geral']:.2f}/5",
    )
    col2.metric("Riscos", len(dados["riscos"]))
    col3.metric("Ações", len(dados["acoes"]))

    st.subheader("Resumo por dimensão")

    df_resumo = pd.DataFrame(
        [
            {
                "Dimensão": dimensao,
                "Pontuação": round(resultados[dimensao], 2),
                "Nível": classificar_maturidade(
                    resultados[dimensao]
                ),
            }
            for dimensao in DIMENSOES
        ]
    )

    st.dataframe(
        df_resumo,
        use_container_width=True,
        hide_index=True,
    )

    csv_completo = gerar_csv_completo(
        organizacao,
        dados,
    )

    st.download_button(
        "Baixar relatório consolidado em CSV",
        data=csv_completo,
        file_name=f"relatorio-ctr-defense-{organizacao['id']}.csv",
        mime="text/csv",
        use_container_width=True,
    )

    pdf = gerar_pdf(organizacao, dados)

    if pdf is None:
        st.warning(
            "A biblioteca ReportLab não está instalada. "
            "Adicione `reportlab` ao requirements.txt para gerar PDF."
        )
    else:
        st.download_button(
            "Baixar relatório executivo em PDF",
            data=pdf,
            file_name=f"relatorio-ctr-defense-{organizacao['id']}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )

    st.info(
        "Os dados desta versão são armazenados na sessão do Streamlit. "
        "Para produção, utilize SQLite, PostgreSQL ou outro banco persistente."
    )


# ============================================================
# NAVEGAÇÃO
# ============================================================


def construir_sidebar():
    st.sidebar.markdown("## 🛡️ CTR DEFENSE")
    st.sidebar.caption("Gestão de Consultoria Profissional")

    organizacoes = st.session_state.organizacoes

    if organizacoes:
        ids = list(organizacoes.keys())
        id_atual = st.session_state.get("organizacao_ativa_id")

        if id_atual not in ids:
            id_atual = ids[0]
            st.session_state.organizacao_ativa_id = id_atual

        indice_atual = ids.index(id_atual)

        selecionada = st.sidebar.selectbox(
            "Organização ativa",
            options=ids,
            index=indice_atual,
            format_func=lambda organizacao_id: organizacoes[
                organizacao_id
            ]["nome"],
            key="seletor_organizacao_sidebar",
        )

        if selecionada != st.session_state.organizacao_ativa_id:
            st.session_state.organizacao_ativa_id = selecionada
            st.rerun()

        organizacao = obter_organizacao_ativa()

        if organizacao:
            st.sidebar.success(
                f"Cliente ativo: {organizacao['nome']}"
            )
    else:
        st.sidebar.warning("Cadastre uma organização para começar.")

    menu = st.sidebar.radio(
        "Módulos",
        [
            "Dashboard Executivo",
            "Organizações",
            "Assessment NIST CSF",
            "Matriz de Riscos",
            "Plano de Ação",
            "Compliance",
            "Reuniões",
            "Relatórios",
        ],
    )

    st.sidebar.markdown("---")
    st.sidebar.caption(
        f"CTR DEFENSE © {datetime.now().year} | Versão Pro"
    )

    return menu


# ============================================================
# EXECUÇÃO
# ============================================================

inicializar_estado()
menu = construir_sidebar()

if menu == "Organizações":
    modulo_organizacoes()

elif menu == "Dashboard Executivo":
    modulo_dashboard()

elif menu == "Assessment NIST CSF":
    modulo_assessment()

elif menu == "Matriz de Riscos":
    modulo_riscos()

elif menu == "Plano de Ação":
    modulo_acoes()

elif menu == "Compliance":
    modulo_compliance()

elif menu == "Reuniões":
    modulo_reunioes()

elif menu == "Relatórios":
    modulo_relatorios()
