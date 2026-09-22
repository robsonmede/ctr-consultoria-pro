import io
import re
import unicodedata
from datetime import date, datetime, timedelta

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from fpdf import FPDF


# ============================================================
# CONFIGURAÇÃO
# ============================================================

st.set_page_config(
    page_title="CTR DEFENSE | Administrador CTR",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
    <style>
        :root {
            --ctr-primary: #047f9e;
            --ctr-secondary: #0b3040;
            --ctr-text: #102f3b;
            --ctr-muted: #647b85;
            --ctr-bg: #edf4f7;
            --ctr-card: #ffffff;
            --ctr-border: #c8dce4;
            --ctr-success: #15803d;
            --ctr-warning: #d97706;
            --ctr-danger: #b91c1c;
        }

        .stApp {
            background: linear-gradient(
                135deg,
                #edf4f7 0%,
                #f9fbfc 50%,
                #e6f0f4 100%
            );
            color: var(--ctr-text);
        }

        section[data-testid="stSidebar"] {
            background: linear-gradient(
                180deg,
                #071e2a 0%,
                #0b3040 60%,
                #047f9e 150%
            );
        }

        section[data-testid="stSidebar"] * {
            color: #f4fbfd !important;
        }

        section[data-testid="stSidebar"] input {
            color: #102f3b !important;
            background: #ffffff !important;
        }

        section[data-testid="stSidebar"] div[data-baseweb="select"] > div {
            color: #102f3b !important;
            background: #ffffff !important;
        }

        h1, h2, h3, h4, h5, h6, p, label {
            color: var(--ctr-text);
        }

        .ctr-header {
            padding: 1.2rem 1.4rem;
            margin-bottom: 1rem;
            border: 1px solid var(--ctr-border);
            border-left: 6px solid var(--ctr-primary);
            border-radius: 14px;
            background: rgba(255, 255, 255, 0.96);
            box-shadow: 0 8px 22px rgba(11, 48, 64, 0.07);
        }

        .ctr-header h2 {
            margin: 0;
            color: var(--ctr-secondary);
        }

        .ctr-header p {
            margin: 0.4rem 0 0;
            color: var(--ctr-muted);
        }

        .ctr-card {
            padding: 1rem;
            margin-bottom: .7rem;
            border: 1px solid var(--ctr-border);
            border-radius: 12px;
            background: #ffffff;
            box-shadow: 0 5px 16px rgba(11, 48, 64, .05);
        }

        .question-card {
            padding: .85rem 1rem;
            margin: .6rem 0 .25rem;
            border: 1px solid var(--ctr-border);
            border-left: 5px solid var(--ctr-primary);
            border-radius: 10px;
            background: #ffffff;
        }

        div[data-testid="stMetric"] {
            padding: 1rem;
            border: 1px solid var(--ctr-border);
            border-radius: 12px;
            background: #ffffff;
            box-shadow: 0 5px 16px rgba(11, 48, 64, .06);
        }

        div[data-testid="stTextInput"] input,
        div[data-testid="stTextArea"] textarea,
        div[data-testid="stNumberInput"] input,
        div[data-baseweb="select"] > div {
            color: var(--ctr-text) !important;
            background: #ffffff !important;
            border-color: var(--ctr-border) !important;
        }

        .stButton > button,
        .stDownloadButton > button,
        button[kind="secondary"],
        button[kind="primary"] {
            background-color: #047f9e !important;
            color: #ffffff !important;
            border: 1px solid #047f9e !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            min-height: 2.5rem;
        }

        .stButton > button:hover,
        .stDownloadButton > button:hover,
        button[kind="secondary"]:hover,
        button[kind="primary"]:hover {
            background-color: #0b3040 !important;
            color: #ffffff !important;
            border-color: #0b3040 !important;
        }

        .stButton > button:focus,
        .stDownloadButton > button:focus {
            color: #ffffff !important;
            box-shadow: 0 0 0 .2rem rgba(4, 127, 158, .25) !important;
        }

        /* Botão Sair */
        .logout-button button {
            background: #b91c1c !important;
            color: #ffffff !important;
            border-color: #b91c1c !important;
        }

        .logout-button button:hover {
            background: #7f1d1d !important;
            color: #ffffff !important;
            border-color: #7f1d1d !important;
        }

        div[data-testid="stExpander"] {
            background: #ffffff;
            border-color: var(--ctr-border);
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

NIVEIS_MATURIDADE = {
    "Não implementado": 0,
    "Inicial": 1,
    "Básico": 2,
    "Definido": 3,
    "Gerenciado": 4,
    "Otimizado": 5,
}

STATUS_ADEQUACAO = [
    "Não iniciado",
    "Em análise",
    "Em implementação",
    "Parcialmente implementado",
    "Implementado",
    "Não aplicável",
]

PERCENTUAL_STATUS = {
    "Não iniciado": 0,
    "Em análise": 15,
    "Em implementação": 50,
    "Parcialmente implementado": 75,
    "Implementado": 100,
    "Não aplicável": 100,
}

PERGUNTAS_NIST = {
    "Governar": [
        "Existe uma política formal de segurança da informação?",
        "Papéis e responsabilidades de segurança estão definidos?",
        "Riscos cibernéticos são considerados nas decisões estratégicas?",
        "Fornecedores são avaliados quanto aos riscos de segurança?",
        "Indicadores de segurança são apresentados à liderança?",
    ],
    "Identificar": [
        "Existe inventário atualizado de hardware e software?",
        "Os dados críticos estão identificados e classificados?",
        "Vulnerabilidades são identificadas periodicamente?",
        "Existe registro formal de riscos cibernéticos?",
        "Serviços e dependências críticas estão documentados?",
    ],
    "Proteger": [
        "Os acessos seguem o princípio do menor privilégio?",
        "Autenticação multifator é utilizada em acessos críticos?",
        "Colaboradores recebem treinamento de segurança?",
        "Backups são protegidos contra alteração e exclusão?",
        "Existe processo de atualização e gestão de patches?",
    ],
    "Detectar": [
        "Logs de sistemas críticos são centralizados?",
        "Existem alertas para atividades suspeitas?",
        "Eventos de segurança são analisados periodicamente?",
        "Existe monitoramento de endpoints e rede?",
        "Regras de detecção são revisadas e atualizadas?",
    ],
    "Responder": [
        "Existe plano documentado de resposta a incidentes?",
        "O plano define responsáveis e contatos de escalonamento?",
        "Incidentes são registrados e classificados?",
        "São realizados exercícios de resposta a incidentes?",
        "Existe processo de comunicação durante crises?",
    ],
    "Recuperar": [
        "Existe plano de continuidade e recuperação?",
        "Backups são testados periodicamente?",
        "RTO e RPO estão formalmente definidos?",
        "Lições aprendidas são registradas após incidentes?",
        "A restauração de serviços críticos é testada?",
    ],
}


def controles_cis():
    nomes = [
        "Inventory and Control of Enterprise Assets",
        "Inventory and Control of Software Assets",
        "Data Protection",
        "Secure Configuration of Enterprise Assets and Software",
        "Account Management",
        "Access Control Management",
        "Continuous Vulnerability Management",
        "Audit Log Management",
        "Email and Web Browser Protections",
        "Malware Defenses",
        "Data Recovery",
        "Network Infrastructure Management",
        "Network Monitoring and Defense",
        "Security Awareness and Skills Training",
        "Service Provider Management",
        "Application Software Security",
        "Incident Response Management",
        "Penetration Testing",
    ]

    grupos = (
        ["IG1"] * 6
        + ["IG2"] * 6
        + ["IG3"] * 6
    )

    return [
        {
            "codigo": f"CIS-{i:02d}",
            "controle": nome,
            "categoria": "Controle técnico",
            "prioridade": grupo,
        }
        for i, (nome, grupo) in enumerate(zip(nomes, grupos), 1)
    ]


CONTROLES_FRAMEWORKS = {
    "LGPD": [
        {
            "codigo": "LGPD-01",
            "controle": "Inventário de dados pessoais",
            "categoria": "Governança",
        },
        {
            "codigo": "LGPD-02",
            "controle": "Mapeamento das bases legais",
            "categoria": "Tratamento",
        },
        {
            "codigo": "LGPD-03",
            "controle": "Política de privacidade",
            "categoria": "Transparência",
        },
        {
            "codigo": "LGPD-04",
            "controle": "Atendimento aos direitos dos titulares",
            "categoria": "Titulares",
        },
        {
            "codigo": "LGPD-05",
            "controle": "Gestão de operadores e terceiros",
            "categoria": "Terceiros",
        },
        {
            "codigo": "LGPD-06",
            "controle": "Resposta a incidentes de privacidade",
            "categoria": "Incidentes",
        },
    ],
    "NIST CSF 2.0": [
        {
            "codigo": "GV",
            "controle": "Governar riscos de cibersegurança",
            "categoria": "Governar",
        },
        {
            "codigo": "ID",
            "controle": "Identificar ativos, ameaças e riscos",
            "categoria": "Identificar",
        },
        {
            "codigo": "PR",
            "controle": "Proteger identidades, dados e infraestrutura",
            "categoria": "Proteger",
        },
        {
            "codigo": "DE",
            "controle": "Detectar eventos e anomalias",
            "categoria": "Detectar",
        },
        {
            "codigo": "RS",
            "controle": "Responder a incidentes",
            "categoria": "Responder",
        },
        {
            "codigo": "RC",
            "controle": "Recuperar serviços e operações",
            "categoria": "Recuperar",
        },
    ],
    "ISO 27001": [
        {
            "codigo": "ISO-04",
            "controle": "Contexto da organização",
            "categoria": "SGSI",
        },
        {
            "codigo": "ISO-05",
            "controle": "Liderança e política de segurança",
            "categoria": "Liderança",
        },
        {
            "codigo": "ISO-06",
            "controle": "Planejamento e tratamento de riscos",
            "categoria": "Planejamento",
        },
        {
            "codigo": "ISO-07",
            "controle": "Recursos e conscientização",
            "categoria": "Suporte",
        },
        {
            "codigo": "ISO-08",
            "controle": "Operação do SGSI",
            "categoria": "Operação",
        },
        {
            "codigo": "ISO-09",
            "controle": "Avaliação e auditoria",
            "categoria": "Avaliação",
        },
    ],
    "CIS Controls v8": controles_cis(),
    "NIST RMF": [
        {
            "codigo": "RMF-01",
            "controle": "Prepare — Preparar",
            "categoria": "Ciclo de vida",
        },
        {
            "codigo": "RMF-02",
            "controle": "Categorize — Categorizar",
            "categoria": "Ciclo de vida",
        },
        {
            "codigo": "RMF-03",
            "controle": "Select — Selecionar",
            "categoria": "Ciclo de vida",
        },
        {
            "codigo": "RMF-04",
            "controle": "Implement — Implementar",
            "categoria": "Ciclo de vida",
        },
        {
            "codigo": "RMF-05",
            "controle": "Assess — Avaliar",
            "categoria": "Ciclo de vida",
        },
        {
            "codigo": "RMF-06",
            "controle": "Authorize — Autorizar",
            "categoria": "Ciclo de vida",
        },
        {
            "codigo": "RMF-07",
            "controle": "Monitor — Monitorar",
            "categoria": "Ciclo de vida",
        },
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

COLUNAS_GAPS = [
    "ID",
    "Framework",
    "Controle",
    "Estado Atual",
    "Estado Desejado",
    "Gap",
    "Criticidade",
    "Recomendação",
    "Responsável",
    "Prazo",
    "Status",
]

COLUNAS_ROADMAP = [
    "ID",
    "Iniciativa",
    "Pilar",
    "Início",
    "Fim",
    "Prioridade",
    "Responsável",
    "Progresso",
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
# ESTADO
# ============================================================

def criar_dados_organizacao():
    return {
        "assessment": {},
        "riscos": [],
        "acoes": [],
        "gaps": [],
        "roadmap": [],
        "adequacao": {},
        "reunioes": [],
    }


def inicializar_estado():
    if "organizacoes" not in st.session_state:
        st.session_state.organizacoes = {}

    if "organizacao_ativa_id" not in st.session_state:
        st.session_state.organizacao_ativa_id = None

    if "autenticado" not in st.session_state:
        st.session_state.autenticado = True


def obter_organizacao_ativa():
    codigo = st.session_state.get("organizacao_ativa_id")

    if not codigo:
        return None

    return st.session_state.organizacoes.get(codigo)


def obter_dados_ativos():
    organizacao = obter_organizacao_ativa()

    if not organizacao:
        return None

    if "dados" not in organizacao:
        organizacao["dados"] = criar_dados_organizacao()

    dados = organizacao["dados"]
    padrao = criar_dados_organizacao()

    for chave, valor in padrao.items():
        if chave not in dados:
            dados[chave] = valor

    return dados


# ============================================================
# AUXILIARES
# ============================================================

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


def normalizar_id(texto):
    texto = unicodedata.normalize("NFKD", texto)
    texto = texto.encode("ascii", "ignore").decode("ascii")
    texto = re.sub(r"[^a-zA-Z0-9]+", "-", texto.lower()).strip("-")
    return texto or f"organizacao-{int(datetime.now().timestamp())}"


def proximo_id(registros):
    valores = []

    for registro in registros:
        try:
            valores.append(int(registro.get("ID", 0)))
        except (TypeError, ValueError):
            pass

    return max(valores, default=0) + 1


def dataframe_lista(registros, colunas):
    if not registros:
        return pd.DataFrame(columns=colunas)

    df = pd.DataFrame(registros)

    for coluna in colunas:
        if coluna not in df.columns:
            df[coluna] = ""

    return df[colunas]


def remover_registro(registros, registro_id):
    return [
        registro
        for registro in registros
        if str(registro.get("ID")) != str(registro_id)
    ]


def calcular_assessment(dados):
    resultados = {}

    for dimensao in DIMENSOES:
        valores = []

        for indice in range(len(PERGUNTAS_NIST[dimensao])):
            chave = f"{dimensao}_{indice}"
            valor = dados["assessment"].get(
                chave,
                "Não implementado",
            )
            valores.append(NIVEIS_MATURIDADE.get(valor, 0))

        resultados[dimensao] = sum(valores) / len(valores)

    resultados["Geral"] = sum(
        resultados[dimensao] for dimensao in DIMENSOES
    ) / len(DIMENSOES)

    return resultados


def classificar_maturidade(valor):
    if valor < 1:
        return "Não implementado"
    if valor < 2:
        return "Inicial"
    if valor < 3:
        return "Básico"
    if valor < 4:
        return "Definido"
    if valor < 4.75:
        return "Gerenciado"
    return "Otimizado"


def classificar_risco(probabilidade, impacto):
    pontuacao = probabilidade * impacto

    if pontuacao >= 20:
        return "Crítico"
    if pontuacao >= 12:
        return "Alto"
    if pontuacao >= 6:
        return "Médio"

    return "Baixo"


def classificar_gap(valor):
    if valor >= 4:
        return "Crítica"
    if valor == 3:
        return "Alta"
    if valor == 2:
        return "Média"
    return "Baixa"


def calcular_progresso_adequacao(dados, framework):
    controles = CONTROLES_FRAMEWORKS[framework]
    percentuais = []

    for controle in controles:
        chave = f"{framework}_{controle['codigo']}"
        registro = dados["adequacao"].get(chave, {})
        status = registro.get("status", "Não iniciado")
        percentuais.append(PERCENTUAL_STATUS.get(status, 0))

    return sum(percentuais) / len(percentuais)


def percentual_acoes_concluidas(dados):
    if not dados["acoes"]:
        return 0

    concluidas = sum(
        acao.get("Status") == "Concluída"
        for acao in dados["acoes"]
    )

    return concluidas * 100 / len(dados["acoes"])


# ============================================================
# PDF
# ============================================================

def texto_pdf(texto):
    """
    Evita erros de codificação em fontes padrão do FPDF.
    """
    texto = str(texto or "")
    substituicoes = {
        "—": "-",
        "–": "-",
        "’": "'",
        "“": '"',
        "”": '"',
        "✅": "",
        "🛡️": "",
    }

    for origem, destino in substituicoes.items():
        texto = texto.replace(origem, destino)

    return texto.encode("latin-1", "replace").decode("latin-1")


class RelatorioPDF(FPDF):
    def header(self):
        self.set_fill_color(11, 48, 64)
        self.rect(0, 0, 210, 18, "F")
        self.set_text_color(255, 255, 255)
        self.set_font("Arial", "B", 13)
        self.cell(0, 10, "CTR DEFENSE", ln=True, align="C")
        self.ln(8)
        self.set_text_color(16, 47, 59)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "", 8)
        self.set_text_color(100, 100, 100)
        self.cell(
            0,
            10,
            texto_pdf(f"Página {self.page_no()}"),
            align="C",
        )


def pdf_titulo(pdf, texto):
    pdf.set_font("Arial", "B", 13)
    pdf.set_text_color(11, 48, 64)
    pdf.cell(0, 8, texto_pdf(texto), ln=True)
    pdf.ln(2)


def pdf_linha(pdf, rotulo, valor):
    pdf.set_font("Arial", "B", 9)
    pdf.cell(42, 6, texto_pdf(rotulo))
    pdf.set_font("Arial", "", 9)
    pdf.multi_cell(0, 6, texto_pdf(valor))


def gerar_pdf_relatorio(organizacao, dados):
    pdf = RelatorioPDF()
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()

    pdf.set_font("Arial", "B", 18)
    pdf.cell(
        0,
        12,
        texto_pdf("Relatório Executivo de Cibersegurança"),
        ln=True,
        align="C",
    )

    pdf.set_font("Arial", "", 10)
    pdf.cell(
        0,
        7,
        texto_pdf(
            f"Emissão: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        ),
        ln=True,
        align="C",
    )
    pdf.ln(7)

    pdf_titulo(pdf, "Identificação da organização")
    pdf_linha(pdf, "Organização:", organizacao.get("nome", ""))
    pdf_linha(pdf, "Segmento:", organizacao.get("segmento", ""))
    pdf_linha(pdf, "Responsável:", organizacao.get("responsavel", ""))
    pdf_linha(pdf, "E-mail:", organizacao.get("email", ""))

    resultados = calcular_assessment(dados)

    pdf.ln(5)
    pdf_titulo(pdf, "Resumo executivo")

    pdf_linha(
        pdf,
        "Maturidade geral:",
        f"{resultados['Geral']:.2f}/5 - "
        f"{classificar_maturidade(resultados['Geral'])}",
    )
    pdf_linha(pdf, "Total de riscos:", len(dados["riscos"]))
    pdf_linha(pdf, "Total de gaps:", len(dados["gaps"]))
    pdf_linha(pdf, "Total de ações:", len(dados["acoes"]))
    pdf_linha(pdf, "Total de iniciativas:", len(dados["roadmap"]))

    pdf.ln(5)
    pdf_titulo(pdf, "Maturidade NIST CSF 2.0")

    for dimensao in DIMENSOES:
        valor = resultados[dimensao]
        pdf_linha(
            pdf,
            f"{dimensao}:",
            f"{valor:.2f}/5 - {classificar_maturidade(valor)}",
        )

    pdf.ln(5)
    pdf_titulo(pdf, "Adequação por framework")

    for framework in CONTROLES_FRAMEWORKS:
        percentual = calcular_progresso_adequacao(dados, framework)
        pdf_linha(pdf, framework + ":", f"{percentual:.1f}%")

    pdf.add_page()
    pdf_titulo(pdf, "Riscos registrados")

    if not dados["riscos"]:
        pdf.cell(0, 7, texto_pdf("Nenhum risco registrado."), ln=True)
    else:
        for risco in dados["riscos"]:
            texto = (
                f"#{risco.get('ID')} - {risco.get('Risco')} | "
                f"Nível: {risco.get('Nível')} | "
                f"Status: {risco.get('Status')}"
            )
            pdf.multi_cell(0, 6, texto_pdf(texto))

    pdf.ln(5)
    pdf_titulo(pdf, "Gaps prioritários")

    if not dados["gaps"]:
        pdf.cell(0, 7, texto_pdf("Nenhum gap registrado."), ln=True)
    else:
        for gap in dados["gaps"]:
            texto = (
                f"#{gap.get('ID')} - {gap.get('Controle')} | "
                f"{gap.get('Framework')} | "
                f"Criticidade: {gap.get('Criticidade')} | "
                f"Status: {gap.get('Status')}"
            )
            pdf.multi_cell(0, 6, texto_pdf(texto))

    pdf.ln(5)
    pdf_titulo(pdf, "Plano de ação")

    if not dados["acoes"]:
        pdf.cell(0, 7, texto_pdf("Nenhuma ação registrada."), ln=True)
    else:
        for acao in dados["acoes"]:
            texto = (
                f"#{acao.get('ID')} - {acao.get('Ação')} | "
                f"Prioridade: {acao.get('Prioridade')} | "
                f"Prazo: {acao.get('Prazo')} | "
                f"Status: {acao.get('Status')}"
            )
            pdf.multi_cell(0, 6, texto_pdf(texto))

    saida = pdf.output()
    return bytes(saida)


# ============================================================
# ORGANIZAÇÕES
# ============================================================

def modulo_organizacoes():
    cabecalho(
        "Organizações",
        "Cadastre e gerencie os clientes da CTR DEFENSE.",
    )

    with st.form("nova_organizacao", clear_on_submit=True):
        col1, col2 = st.columns(2)

        nome = col1.text_input("Nome da organização")
        segmento = col2.text_input("Segmento")

        col3, col4 = st.columns(2)

        responsavel = col3.text_input("Responsável")
        email = col4.text_input("E-mail")

        salvar = st.form_submit_button(
            "Cadastrar organização",
            type="primary",
            use_container_width=True,
        )

        if salvar:
            if not nome.strip():
                st.error("Informe o nome da organização.")
            else:
                base_id = normalizar_id(nome)
                organizacao_id = base_id
                contador = 2

                while organizacao_id in st.session_state.organizacoes:
                    organizacao_id = f"{base_id}-{contador}"
                    contador += 1

                st.session_state.organizacoes[organizacao_id] = {
                    "id": organizacao_id,
                    "nome": nome.strip(),
                    "segmento": segmento.strip(),
                    "responsavel": responsavel.strip(),
                    "email": email.strip(),
                    "criado_em": datetime.now().isoformat(),
                    "dados": criar_dados_organizacao(),
                }

                st.session_state.organizacao_ativa_id = organizacao_id
                st.success("Organização cadastrada com sucesso.")
                st.rerun()

    if not st.session_state.organizacoes:
        st.info("Nenhuma organização cadastrada.")
        return

    st.subheader("Organizações cadastradas")

    for organizacao_id, organizacao in list(
        st.session_state.organizacoes.items()
    ):
        ativa = (
            organizacao_id
            == st.session_state.organizacao_ativa_id
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

                if ativa:
                    st.session_state.organizacao_ativa_id = None

                st.rerun()


# ============================================================
# DASHBOARD
# ============================================================

def modulo_dashboard():
    organizacao = obter_organizacao_ativa()
    dados = obter_dados_ativos()

    if not organizacao or not dados:
        st.warning("Cadastre ou selecione uma organização.")
        return

    cabecalho(
        f"Dashboard Executivo - {organizacao['nome']}",
        "Visão consolidada da postura de segurança e conformidade.",
    )

    resultados = calcular_assessment(dados)

    riscos_criticos = sum(
        risco.get("Nível") == "Crítico"
        and risco.get("Status") != "Encerrado"
        for risco in dados["riscos"]
    )

    gaps_criticos = sum(
        gap.get("Criticidade") == "Crítica"
        and gap.get("Status") != "Concluído"
        for gap in dados["gaps"]
    )

    roadmap_medio = (
        sum(item.get("Progresso", 0) for item in dados["roadmap"])
        / len(dados["roadmap"])
        if dados["roadmap"]
        else 0
    )

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric(
        "Maturidade",
        f"{resultados['Geral']:.2f}/5",
        classificar_maturidade(resultados["Geral"]),
    )
    col2.metric("Riscos críticos", riscos_criticos)
    col3.metric("Gaps críticos", gaps_criticos)
    col4.metric("Roadmap", f"{roadmap_medio:.0f}%")
    col5.metric(
        "Ações concluídas",
        f"{percentual_acoes_concluidas(dados):.0f}%",
    )

    col_g1, col_g2 = st.columns(2)

    with col_g1:
        radar = go.Figure(
            data=[
                go.Scatterpolar(
                    r=[resultados[d] for d in DIMENSOES],
                    theta=DIMENSOES,
                    fill="toself",
                    line_color="#047f9e",
                    name="Maturidade",
                )
            ]
        )

        radar.update_layout(
            title="Maturidade NIST CSF 2.0",
            polar={
                "radialaxis": {
                    "visible": True,
                    "range": [0, 5],
                }
            },
            showlegend=False,
            height=430,
            paper_bgcolor="rgba(255,255,255,0)",
        )

        st.plotly_chart(radar, use_container_width=True)

    with col_g2:
        conformidade = pd.DataFrame(
            {
                "Framework": list(CONTROLES_FRAMEWORKS.keys()),
                "Conformidade": [
                    calcular_progresso_adequacao(dados, framework)
                    for framework in CONTROLES_FRAMEWORKS
                ],
            }
        )

        figura = px.bar(
            conformidade,
            x="Framework",
            y="Conformidade",
            range_y=[0, 100],
            color="Conformidade",
            color_continuous_scale=[
                "#dceff4",
                "#047f9e",
                "#0b3040",
            ],
            title="Adequação por framework",
        )

        figura.update_layout(
            coloraxis_showscale=False,
            height=430,
            paper_bgcolor="rgba(255,255,255,0)",
        )

        st.plotly_chart(figura, use_container_width=True)


# ============================================================
# ASSESSMENT
# ============================================================

def modulo_assessment():
    organizacao = obter_organizacao_ativa()
    dados = obter_dados_ativos()

    if not organizacao or not dados:
        st.error("Nenhuma organização ativa foi encontrada.")
        return

    cabecalho(
        "Assessment NIST CSF 2.0",
        "Avalie a maturidade nas seis funções do framework.",
    )

    abas = st.tabs(DIMENSOES)
    opcoes = list(NIVEIS_MATURIDADE.keys())

    for aba, dimensao in zip(abas, DIMENSOES):
        with aba:
            for indice, pergunta in enumerate(
                PERGUNTAS_NIST[dimensao]
            ):
                chave = f"{dimensao}_{indice}"

                st.markdown(
                    f"""
                    <div class="question-card">
                        <strong>{indice + 1}. {pergunta}</strong>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                atual = dados["assessment"].get(
                    chave,
                    "Não implementado",
                )

                resposta = st.selectbox(
                    "Nível de implementação",
                    opcoes,
                    index=opcoes.index(atual),
                    key=f"assessment_{organizacao['id']}_{chave}",
                )

                dados["assessment"][chave] = resposta

    resultados = calcular_assessment(dados)

    st.subheader("Resultado")

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


# ============================================================
# RISCOS
# ============================================================

def modulo_riscos():
    organizacao = obter_organizacao_ativa()
    dados = obter_dados_ativos()

    if not organizacao or not dados:
        st.error("Nenhuma organização ativa foi encontrada.")
        return

    cabecalho(
        "Matriz de Riscos",
        "Registre, classifique e acompanhe os riscos.",
    )

    with st.form(f"form_risco_{organizacao['id']}"):
        risco = st.text_area("Descrição do risco")

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

        salvar = st.form_submit_button(
            "Adicionar risco",
            type="primary",
            use_container_width=True,
        )

        if salvar:
            if not risco.strip():
                st.error("Descreva o risco.")
            else:
                dados["riscos"].append(
                    {
                        "ID": proximo_id(dados["riscos"]),
                        "Risco": risco.strip(),
                        "Categoria": categoria,
                        "Probabilidade": probabilidade,
                        "Impacto": impacto,
                        "Nível": classificar_risco(
                            probabilidade,
                            impacto,
                        ),
                        "Tratamento": tratamento,
                        "Responsável": responsavel.strip(),
                        "Status": status,
                    }
                )

                st.success("Risco registrado.")
                st.rerun()

    df = dataframe_lista(dados["riscos"], COLUNAS_RISCOS)
    st.dataframe(df, use_container_width=True, hide_index=True)

    if dados["riscos"]:
        risco_id = st.selectbox(
            "Risco para exclusão",
            [item["ID"] for item in dados["riscos"]],
            format_func=lambda valor: next(
                (
                    f"#{item['ID']} - {item['Risco']}"
                    for item in dados["riscos"]
                    if item["ID"] == valor
                ),
                str(valor),
            ),
        )

        if st.button("Excluir risco"):
            dados["riscos"] = remover_registro(
                dados["riscos"],
                risco_id,
            )
            st.rerun()


# ============================================================
# ADEQUAÇÃO DE FRAMEWORKS
# ============================================================

def modulo_adequacao():
    organizacao = obter_organizacao_ativa()
    dados = obter_dados_ativos()

    if not organizacao or not dados:
        st.error("Nenhuma organização ativa foi encontrada.")
        return

    cabecalho(
        "Adequação de Frameworks",
        "Gerencie controles, prioridades, evidências e responsáveis.",
    )

    framework = st.selectbox(
        "Framework",
        list(CONTROLES_FRAMEWORKS.keys()),
        key=f"framework_{organizacao['id']}",
    )

    controles = CONTROLES_FRAMEWORKS[framework]
    progresso = calcular_progresso_adequacao(dados, framework)

    col1, col2, col3 = st.columns(3)

    col1.metric("Conformidade", f"{progresso:.1f}%")
    col2.metric("Controles", len(controles))
    col3.metric(
        "Implementados",
        sum(
            dados["adequacao"].get(
                f"{framework}_{controle['codigo']}",
                {},
            ).get("status")
            in ["Implementado", "Não aplicável"]
            for controle in controles
        ),
    )

    st.progress(progresso / 100)

    if framework == "CIS Controls v8":
        st.info(
            "Priorização CIS: IG1 representa higiene cibernética essencial; "
            "IG2 adiciona controles para organizações com maior exposição; "
            "IG3 contempla ambientes de alta criticidade."
        )

    for controle in controles:
        chave = f"{framework}_{controle['codigo']}"
        registro = dados["adequacao"].get(
            chave,
            {
                "status": "Não iniciado",
                "responsavel": "",
                "prazo": "",
                "evidencia": "",
                "observacoes": "",
            },
        )

        prioridade = (
            f" | Prioridade: {controle['prioridade']}"
            if "prioridade" in controle
            else ""
        )

        titulo = (
            f"{controle['codigo']} - {controle['controle']}"
            f"{prioridade}"
        )

        with st.expander(titulo):
            col1, col2 = st.columns(2)

            status_atual = registro.get(
                "status",
                "Não iniciado",
            )

            if status_atual not in STATUS_ADEQUACAO:
                status_atual = "Não iniciado"

            status = col1.selectbox(
                "Status",
                STATUS_ADEQUACAO,
                index=STATUS_ADEQUACAO.index(status_atual),
                key=f"status_{organizacao['id']}_{chave}",
            )

            responsavel = col2.text_input(
                "Responsável",
                value=registro.get("responsavel", ""),
                key=f"responsavel_{organizacao['id']}_{chave}",
            )

            col3, col4 = st.columns(2)

            prazo_salvo = registro.get("prazo", "")

            try:
                prazo_inicial = date.fromisoformat(prazo_salvo)
            except (TypeError, ValueError):
                prazo_inicial = date.today() + timedelta(days=90)

            prazo = col3.date_input(
                "Prazo",
                value=prazo_inicial,
                format="DD/MM/YYYY",
                key=f"prazo_{organizacao['id']}_{chave}",
            )

            evidencia = col4.text_input(
                "Evidência",
                value=registro.get("evidencia", ""),
                key=f"evidencia_{organizacao['id']}_{chave}",
            )

            observacoes = st.text_area(
                "Observações",
                value=registro.get("observacoes", ""),
                key=f"observacoes_{organizacao['id']}_{chave}",
            )

            dados["adequacao"][chave] = {
                "status": status,
                "responsavel": responsavel,
                "prazo": prazo.isoformat(),
                "evidencia": evidencia,
                "observacoes": observacoes,
            }

    st.subheader("Resumo dos controles")

    linhas = []

    for controle in controles:
        chave = f"{framework}_{controle['codigo']}"
        registro = dados["adequacao"].get(chave, {})

        linha = {
            "Código": controle["codigo"],
            "Controle": controle["controle"],
            "Categoria": controle["categoria"],
            "Status": registro.get("status", "Não iniciado"),
            "Percentual": PERCENTUAL_STATUS.get(
                registro.get("status", "Não iniciado"),
                0,
            ),
            "Responsável": registro.get("responsavel", ""),
            "Prazo": registro.get("prazo", ""),
            "Evidência": registro.get("evidencia", ""),
        }

        if "prioridade" in controle:
            linha["Prioridade"] = controle["prioridade"]

        linhas.append(linha)

    df = pd.DataFrame(linhas)

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Percentual": st.column_config.ProgressColumn(
                "Percentual",
                min_value=0,
                max_value=100,
                format="%d%%",
            )
        },
    )

    st.download_button(
        "Baixar adequação em CSV",
        data=df.to_csv(
            index=False,
            sep=";",
        ).encode("utf-8-sig"),
        file_name=(
            f"adequacao-{normalizar_id(framework)}-"
            f"{organizacao['id']}.csv"
        ),
        mime="text/csv",
        use_container_width=True,
    )


# ============================================================
# GAP ANALYSIS
# ============================================================

def modulo_gaps():
    organizacao = obter_organizacao_ativa()
    dados = obter_dados_ativos()

    if not organizacao or not dados:
        st.error("Nenhuma organização ativa foi encontrada.")
        return

    cabecalho(
        "Gap Analysis",
        "Compare o estado atual com o estado desejado.",
    )

    with st.form(f"form_gap_{organizacao['id']}"):
        col1, col2 = st.columns(2)

        framework = col1.selectbox(
            "Framework",
            list(CONTROLES_FRAMEWORKS.keys()),
        )
        controle = col2.text_input("Controle ou requisito")

        col3, col4 = st.columns(2)

        estado_atual = col3.slider(
            "Estado atual",
            0,
            5,
            1,
        )
        estado_desejado = col4.slider(
            "Estado desejado",
            0,
            5,
            3,
        )

        recomendacao = st.text_area("Recomendação")

        col5, col6, col7 = st.columns(3)

        responsavel = col5.text_input("Responsável")
        prazo = col6.date_input(
            "Prazo",
            date.today() + timedelta(days=60),
            format="DD/MM/YYYY",
        )
        status = col7.selectbox(
            "Status",
            ["Aberto", "Em tratamento", "Aceito", "Concluído"],
        )

        salvar = st.form_submit_button(
            "Registrar gap",
            type="primary",
            use_container_width=True,
        )

        if salvar:
            if not controle.strip():
                st.error("Informe o controle ou requisito.")
            elif estado_desejado < estado_atual:
                st.error(
                    "O estado desejado deve ser igual ou superior ao atual."
                )
            else:
                valor_gap = estado_desejado - estado_atual

                dados["gaps"].append(
                    {
                        "ID": proximo_id(dados["gaps"]),
                        "Framework": framework,
                        "Controle": controle.strip(),
                        "Estado Atual": estado_atual,
                        "Estado Desejado": estado_desejado,
                        "Gap": valor_gap,
                        "Criticidade": classificar_gap(valor_gap),
                        "Recomendação": recomendacao.strip(),
                        "Responsável": responsavel.strip(),
                        "Prazo": prazo.isoformat(),
                        "Status": status,
                    }
                )

                st.success("Gap registrado.")
                st.rerun()

    df = dataframe_lista(dados["gaps"], COLUNAS_GAPS)
    st.dataframe(df, use_container_width=True, hide_index=True)

    if not df.empty:
        por_criticidade = (
            df["Criticidade"]
            .value_counts()
            .reset_index()
        )
        por_criticidade.columns = ["Criticidade", "Quantidade"]

        figura = px.pie(
            por_criticidade,
            names="Criticidade",
            values="Quantidade",
            hole=.4,
            title="Gaps por criticidade",
        )

        st.plotly_chart(figura, use_container_width=True)


# ============================================================
# PLANO DE AÇÃO
# ============================================================

def modulo_acoes():
    organizacao = obter_organizacao_ativa()
    dados = obter_dados_ativos()

    if not organizacao or not dados:
        st.error("Nenhuma organização ativa foi encontrada.")
        return

    cabecalho(
        "Plano de Ação",
        "Gerencie ações corretivas, preventivas e de melhoria.",
    )

    with st.form(f"form_acao_{organizacao['id']}"):
        acao = st.text_area("Descrição da ação")

        col1, col2, col3 = st.columns(3)

        origem = col1.selectbox(
            "Origem",
            [
                "Assessment",
                "Risco",
                "Gap Analysis",
                "Adequação",
                "Outro",
            ],
        )
        prioridade = col2.selectbox(
            "Prioridade",
            ["Crítica", "Alta", "Média", "Baixa"],
        )
        responsavel = col3.text_input("Responsável")

        prazo = st.date_input(
            "Prazo",
            date.today() + timedelta(days=30),
            format="DD/MM/YYYY",
        )

        status = st.selectbox(
            "Status",
            [
                "Não iniciada",
                "Em andamento",
                "Bloqueada",
                "Concluída",
            ],
        )

        salvar = st.form_submit_button(
            "Adicionar ação",
            type="primary",
            use_container_width=True,
        )

        if salvar:
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
                        "Prazo": prazo.isoformat(),
                        "Status": status,
                    }
                )

                st.success("Ação adicionada.")
                st.rerun()

    df = dataframe_lista(dados["acoes"], COLUNAS_ACOES)
    st.dataframe(df, use_container_width=True, hide_index=True)


# ============================================================
# ROADMAP
# ============================================================

def modulo_roadmap():
    organizacao = obter_organizacao_ativa()
    dados = obter_dados_ativos()

    if not organizacao or not dados:
        st.error("Nenhuma organização ativa foi encontrada.")
        return

    cabecalho(
        "Roadmap de Segurança",
        "Planeje e acompanhe iniciativas estratégicas.",
    )

    with st.form(f"form_roadmap_{organizacao['id']}"):
        iniciativa = st.text_area("Iniciativa")

        col1, col2, col3 = st.columns(3)

        pilar = col1.selectbox(
            "Pilar",
            [
                "Governança",
                "Gestão de Riscos",
                "CIS Controls v8",
                "NIST RMF",
                "Identidade e Acesso",
                "Proteção de Dados",
                "Detecção e Resposta",
                "Continuidade",
            ],
        )

        inicio = col2.date_input(
            "Início",
            date.today(),
            format="DD/MM/YYYY",
        )

        fim = col3.date_input(
            "Fim",
            date.today() + timedelta(days=90),
            format="DD/MM/YYYY",
        )

        col4, col5, col6 = st.columns(3)

        prioridade = col4.selectbox(
            "Prioridade",
            ["Crítica", "Alta", "Média", "Baixa"],
        )
        responsavel = col5.text_input("Responsável")
        progresso = col6.slider("Progresso", 0, 100, 0, 5)

        status = st.selectbox(
            "Status",
            [
                "Planejado",
                "Em andamento",
                "Bloqueado",
                "Concluído",
                "Cancelado",
            ],
        )

        salvar = st.form_submit_button(
            "Adicionar iniciativa",
            type="primary",
            use_container_width=True,
        )

        if salvar:
            if not iniciativa.strip():
                st.error("Informe a iniciativa.")
            elif fim < inicio:
                st.error("A data final não pode ser anterior à inicial.")
            else:
                dados["roadmap"].append(
                    {
                        "ID": proximo_id(dados["roadmap"]),
                        "Iniciativa": iniciativa.strip(),
                        "Pilar": pilar,
                        "Início": inicio.isoformat(),
                        "Fim": fim.isoformat(),
                        "Prioridade": prioridade,
                        "Responsável": responsavel.strip(),
                        "Progresso": (
                            100
                            if status == "Concluído"
                            else progresso
                        ),
                        "Status": status,
                    }
                )

                st.success("Iniciativa adicionada.")
                st.rerun()

    df = dataframe_lista(dados["roadmap"], COLUNAS_ROADMAP)

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Progresso": st.column_config.ProgressColumn(
                "Progresso",
                min_value=0,
                max_value=100,
                format="%d%%",
            )
        },
    )


# ============================================================
# REUNIÕES
# ============================================================

def modulo_reunioes():
    organizacao = obter_organizacao_ativa()
    dados = obter_dados_ativos()

    if not organizacao or not dados:
        st.error("Nenhuma organização ativa foi encontrada.")
        return

    cabecalho(
        "Reuniões",
        "Registre decisões, participantes e próximos passos.",
    )

    with st.form(f"form_reuniao_{organizacao['id']}"):
        col1, col2 = st.columns(2)

        data_reuniao = col1.date_input(
            "Data",
            date.today(),
            format="DD/MM/YYYY",
        )
        titulo = col2.text_input("Título")

        participantes = st.text_input("Participantes")
        notas = st.text_area("Notas e decisões")

        salvar = st.form_submit_button(
            "Salvar reunião",
            type="primary",
            use_container_width=True,
        )

        if salvar:
            if not titulo.strip():
                st.error("Informe o título.")
            else:
                dados["reunioes"].append(
                    {
                        "ID": proximo_id(dados["reunioes"]),
                        "Data": data_reuniao.isoformat(),
                        "Título": titulo.strip(),
                        "Participantes": participantes.strip(),
                        "Notas": notas.strip(),
                    }
                )

                st.success("Reunião registrada.")
                st.rerun()

    for reuniao in reversed(dados["reunioes"]):
        with st.expander(
            f"{reuniao['Data']} - {reuniao['Título']}"
        ):
            st.write(
                f"**Participantes:** "
                f"{reuniao.get('Participantes') or 'Não informado'}"
            )
            st.write(reuniao.get("Notas") or "Sem notas.")


# ============================================================
# RELATÓRIOS
# ============================================================

def gerar_csv_consolidado(organizacao, dados):
    buffer = io.StringIO()

    buffer.write("CTR DEFENSE - RELATÓRIO CONSOLIDADO\n")
    buffer.write(f"Organização;{organizacao['nome']}\n")
    buffer.write(
        f"Emissão;{datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
    )

    resultados = calcular_assessment(dados)

    buffer.write("ASSESSMENT NIST CSF 2.0\n")
    buffer.write("Dimensão;Pontuação;Nível\n")

    for dimensao in DIMENSOES:
        buffer.write(
            f"{dimensao};"
            f"{resultados[dimensao]:.2f};"
            f"{classificar_maturidade(resultados[dimensao])}\n"
        )

    buffer.write("\nRISCOS\n")
    buffer.write(
        dataframe_lista(
            dados["riscos"],
            COLUNAS_RISCOS,
        ).to_csv(index=False, sep=";")
    )

    buffer.write("\nGAPS\n")
    buffer.write(
        dataframe_lista(
            dados["gaps"],
            COLUNAS_GAPS,
        ).to_csv(index=False, sep=";")
    )

    buffer.write("\nPLANO DE AÇÃO\n")
    buffer.write(
        dataframe_lista(
            dados["acoes"],
            COLUNAS_ACOES,
        ).to_csv(index=False, sep=";")
    )

    buffer.write("\nROADMAP\n")
    buffer.write(
        dataframe_lista(
            dados["roadmap"],
            COLUNAS_ROADMAP,
        ).to_csv(index=False, sep=";")
    )

    return buffer.getvalue().encode("utf-8-sig")


def modulo_relatorios():
    organizacao = obter_organizacao_ativa()
    dados = obter_dados_ativos()

    if not organizacao or not dados:
        st.error("Nenhuma organização ativa foi encontrada.")
        return

    cabecalho(
        "Relatórios e Exportações",
        "Gere relatórios executivos em PDF e exportações em CSV.",
    )

    resultados = calcular_assessment(dados)

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Maturidade",
        f"{resultados['Geral']:.2f}/5",
    )
    col2.metric("Riscos", len(dados["riscos"]))
    col3.metric("Gaps", len(dados["gaps"]))
    col4.metric("Ações", len(dados["acoes"]))

    st.subheader("Maturidade por dimensão")

    df_maturidade = pd.DataFrame(
        [
            {
                "Dimensão": dimensao,
                "Pontuação": round(
                    resultados[dimensao],
                    2,
                ),
                "Nível": classificar_maturidade(
                    resultados[dimensao]
                ),
            }
            for dimensao in DIMENSOES
        ]
    )

    st.dataframe(
        df_maturidade,
        use_container_width=True,
        hide_index=True,
    )

    pdf_bytes = gerar_pdf_relatorio(
        organizacao,
        dados,
    )

    csv_bytes = gerar_csv_consolidado(
        organizacao,
        dados,
    )

    col_pdf, col_csv = st.columns(2)

    col_pdf.download_button(
        "Baixar relatório completo em PDF",
        data=pdf_bytes,
        file_name=f"relatorio-ctr-defense-{organizacao['id']}.pdf",
        mime="application/pdf",
        use_container_width=True,
    )

    col_csv.download_button(
        "Baixar relatório consolidado em CSV",
        data=csv_bytes,
        file_name=f"relatorio-ctr-defense-{organizacao['id']}.csv",
        mime="text/csv",
        use_container_width=True,
    )

    st.info(
        "O PDF inclui identificação da organização, maturidade NIST CSF, "
        "adequação dos frameworks, riscos, gaps e plano de ação."
    )


# ============================================================
# SIDEBAR
# ============================================================

def sair():
    st.session_state.autenticado = False
    st.session_state.organizacao_ativa_id = None
    st.rerun()


def construir_sidebar():
    st.sidebar.markdown("## 🛡️ CTR DEFENSE")
    st.sidebar.caption("Consultoria Profissional de Cibersegurança")

    st.sidebar.markdown(
        """
        <div style="
            padding: .7rem;
            border: 1px solid rgba(255,255,255,.25);
            border-radius: 8px;
            margin-bottom: 1rem;
        ">
            <strong>👤 Administrador CTR</strong><br>
            <small>Perfil: Administrador</small>
        </div>
        """,
        unsafe_allow_html=True,
    )

    organizacoes = st.session_state.organizacoes

    if organizacoes:
        ids = list(organizacoes.keys())
        atual = st.session_state.get("organizacao_ativa_id")

        if atual not in ids:
            atual = ids[0]
            st.session_state.organizacao_ativa_id = atual

        selecionada = st.sidebar.selectbox(
            "Organização ativa",
            ids,
            index=ids.index(atual),
            format_func=lambda codigo: organizacoes[codigo]["nome"],
            key="organizacao_sidebar",
        )

        if selecionada != atual:
            st.session_state.organizacao_ativa_id = selecionada
            st.rerun()
    else:
        st.sidebar.warning(
            "Cadastre uma organização para começar."
        )

    menu = st.sidebar.radio(
        "Módulos",
        [
            "Dashboard Executivo",
            "Organizações",
            "Assessment NIST CSF",
            "Matriz de Riscos",
            "Plano de Ação",
            "Roadmap de Segurança",
            "Gap Analysis",
            "Adequação de Frameworks",
            "Reuniões",
            "Relatórios",
        ],
    )

    st.sidebar.markdown("---")

    st.sidebar.caption(
        f"CTR DEFENSE © {datetime.now().year} | Versão Pro"
    )

    st.sidebar.markdown(
        '<div class="logout-button">',
        unsafe_allow_html=True,
    )

    if st.sidebar.button(
        "Sair",
        use_container_width=True,
        key="botao_sair",
    ):
        sair()

    st.sidebar.markdown(
        "</div>",
        unsafe_allow_html=True,
    )

    return menu


# ============================================================
# EXECUÇÃO
# ============================================================

inicializar_estado()

if not st.session_state.autenticado:
    st.markdown(
        """
        <div class="ctr-header">
            <h2>Sessão encerrada</h2>
            <p>Recarregue a página para iniciar uma nova sessão.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("Iniciar nova sessão", type="primary"):
        st.session_state.autenticado = True
        st.rerun()

    st.stop()


menu = construir_sidebar()

if menu == "Dashboard Executivo":
    modulo_dashboard()

elif menu == "Organizações":
    modulo_organizacoes()

elif menu == "Assessment NIST CSF":
    modulo_assessment()

elif menu == "Matriz de Riscos":
    modulo_riscos()

elif menu == "Plano de Ação":
    modulo_acoes()

elif menu == "Roadmap de Segurança":
    modulo_roadmap()

elif menu == "Gap Analysis":
    modulo_gaps()

elif menu == "Adequação de Frameworks":
    modulo_adequacao()

elif menu == "Reuniões":
    modulo_reunioes()

elif menu == "Relatórios":
    modulo_relatorios()
