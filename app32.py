import io
import re
import unicodedata
from datetime import date, datetime, timedelta

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from fpdf import FPDF
from fpdf.enums import XPos, YPos


# ============================================================
# CONFIGURAÇÃO
# ============================================================

st.set_page_config(
    page_title="CTR DEFENSE",
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
            --primary: #047f9e;
            --secondary: #0b3040;
            --text: #102f3b;
            --muted: #647b85;
            --border: #c8dce4;
        }

        .stApp {
            background: linear-gradient(
                135deg,
                #edf4f7 0%,
                #f9fbfc 50%,
                #e6f0f4 100%
            );
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

        section[data-testid="stSidebar"]
        div[data-baseweb="select"] > div {
            color: #102f3b !important;
            background: #ffffff !important;
        }

        h1, h2, h3, h4, h5, h6, p, label {
            color: var(--text);
        }

        .ctr-header {
            padding: 1.2rem 1.4rem;
            margin-bottom: 1rem;
            border: 1px solid var(--border);
            border-left: 6px solid var(--primary);
            border-radius: 14px;
            background: #ffffff;
            box-shadow: 0 8px 22px rgba(11, 48, 64, .07);
        }

        .ctr-header h2 {
            margin: 0;
            color: var(--secondary);
        }

        .ctr-header p {
            margin: .4rem 0 0;
            color: var(--muted);
        }

        .question-card {
            padding: .85rem 1rem;
            margin: .6rem 0 .25rem;
            border: 1px solid var(--border);
            border-left: 5px solid var(--primary);
            border-radius: 10px;
            background: #ffffff;
        }

        div[data-testid="stMetric"] {
            padding: 1rem;
            border: 1px solid var(--border);
            border-radius: 12px;
            background: #ffffff;
        }

        .stButton > button,
        .stDownloadButton > button {
            background: #047f9e !important;
            color: #ffffff !important;
            border: 1px solid #047f9e !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
        }

        .stButton > button:hover,
        .stDownloadButton > button:hover {
            background: #0b3040 !important;
            color: #ffffff !important;
            border-color: #0b3040 !important;
        }

        .logout-button button {
            background: #b91c1c !important;
            color: #ffffff !important;
            border-color: #b91c1c !important;
        }

        .logout-button button:hover {
            background: #7f1d1d !important;
            border-color: #7f1d1d !important;
        }

        div[data-testid="stExpander"] {
            background: #ffffff;
            border-color: var(--border);
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
        "Existe política formal de segurança da informação?",
        "Papéis e responsabilidades estão definidos?",
        "Riscos cibernéticos são considerados nas decisões?",
        "Fornecedores são avaliados quanto à segurança?",
        "Indicadores são apresentados à liderança?",
    ],
    "Identificar": [
        "Existe inventário de hardware e software?",
        "Dados críticos estão identificados e classificados?",
        "Vulnerabilidades são identificadas periodicamente?",
        "Existe registro formal de riscos?",
        "Serviços críticos estão documentados?",
    ],
    "Proteger": [
        "Os acessos seguem o menor privilégio?",
        "MFA é utilizado em acessos críticos?",
        "Colaboradores recebem treinamento?",
        "Backups são protegidos contra alteração?",
        "Existe gestão formal de patches?",
    ],
    "Detectar": [
        "Logs críticos são centralizados?",
        "Existem alertas para atividades suspeitas?",
        "Eventos são analisados periodicamente?",
        "Existe monitoramento de endpoints e rede?",
        "Regras de detecção são atualizadas?",
    ],
    "Responder": [
        "Existe plano de resposta a incidentes?",
        "Responsáveis e contatos estão definidos?",
        "Incidentes são registrados e classificados?",
        "São realizados exercícios de resposta?",
        "Existe comunicação durante crises?",
    ],
    "Recuperar": [
        "Existe plano de continuidade?",
        "Backups são testados?",
        "RTO e RPO estão definidos?",
        "Lições aprendidas são registradas?",
        "A restauração de serviços é testada?",
    ],
}


def criar_controles_cis():
    nomes = [
        "Inventário e controle de ativos corporativos",
        "Inventário e controle de ativos de software",
        "Proteção de dados",
        "Configuração segura de ativos corporativos",
        "Gestão de contas",
        "Gestão de controle de acesso",
        "Gestão contínua de vulnerabilidades",
        "Gestão de logs de auditoria",
        "Proteções de e-mail e navegador",
        "Defesas contra malware",
        "Recuperação de dados",
        "Gestão da infraestrutura de rede",
        "Monitoramento e defesa de rede",
        "Treinamento de conscientização e habilidades",
        "Gestão de provedores de serviço",
        "Segurança de aplicações",
        "Gestão de resposta a incidentes",
        "Testes de penetração",
    ]

    # Classificação operacional por grupo de implementação.
    # A aplicação permite revisar essa classificação individualmente
    # no futuro, se necessário.
    grupos = [
        "IG1", "IG1", "IG1", "IG1", "IG1", "IG1",
        "IG2", "IG2", "IG2", "IG2", "IG2", "IG2",
        "IG3", "IG3", "IG3", "IG3", "IG3", "IG3",
    ]

    return [
        {
            "codigo": f"CIS-{indice:02d}",
            "controle": nome,
            "categoria": "Controle técnico",
            "prioridade": grupos[indice - 1],
            "descricao": (
                f"Implementar o CIS Control {indice} "
                f"com prioridade {grupos[indice - 1]}."
            ),
        }
        for indice, nome in enumerate(nomes, 1)
    ]


def criar_controles_rmf():
    etapas = [
        ("Prepare", "Preparar"),
        ("Categorize", "Categorizar"),
        ("Select", "Selecionar"),
        ("Implement", "Implementar"),
        ("Assess", "Avaliar"),
        ("Authorize", "Autorizar"),
        ("Monitor", "Monitorar"),
    ]

    descricoes = [
        "Preparar a organização e o sistema para o gerenciamento de riscos.",
        "Categorizar o sistema e as informações processadas.",
        "Selecionar controles de segurança e privacidade.",
        "Implementar os controles selecionados.",
        "Avaliar a eficácia dos controles implementados.",
        "Autorizar o sistema com base no risco residual.",
        "Monitorar continuamente riscos e controles.",
    ]

    return [
        {
            "codigo": f"RMF-{i:02d}",
            "controle": f"{ingles} — {portugues}",
            "categoria": "Ciclo de vida",
            "descricao": descricoes[i - 1],
        }
        for i, (ingles, portugues) in enumerate(etapas, 1)
    ]


CONTROLES_FRAMEWORKS = {
    "CIS Controls v8": criar_controles_cis(),
    "NIST RMF": criar_controles_rmf(),
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
    ],
    "NIST CSF 2.0": [
        {
            "codigo": "GV",
            "controle": "Governar riscos de cibersegurança",
            "categoria": "Governar",
        },
        {
            "codigo": "ID",
            "controle": "Identificar ativos e riscos",
            "categoria": "Identificar",
        },
        {
            "codigo": "PR",
            "controle": "Proteger dados e infraestrutura",
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
            "controle": "Recuperar operações",
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
            "controle": "Liderança e política",
            "categoria": "Liderança",
        },
        {
            "codigo": "ISO-06",
            "controle": "Planejamento e riscos",
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
    ],
}


COLUNAS_RISCOS = [
    "ID", "Risco", "Categoria", "Probabilidade", "Impacto",
    "Nível", "Tratamento", "Responsável", "Status",
]

COLUNAS_GAPS = [
    "ID", "Framework", "Controle", "Estado Atual",
    "Estado Desejado", "Gap", "Criticidade", "Recomendação",
    "Responsável", "Prazo", "Status",
]

COLUNAS_ACOES = [
    "ID", "Ação", "Origem", "Prioridade",
    "Responsável", "Prazo", "Status",
]

COLUNAS_ROADMAP = [
    "ID", "Iniciativa", "Pilar", "Início", "Fim",
    "Prioridade", "Responsável", "Progresso", "Status",
]

COLUNAS_REUNIOES = [
    "ID", "Data", "Título", "Participantes", "Notas",
]


# ============================================================
# ESTADO
# ============================================================

def criar_dados():
    return {
        "assessment": {},
        "riscos": [],
        "gaps": [],
        "acoes": [],
        "roadmap": [],
        "reunioes": [],
        "adequacao": {},
    }


def inicializar_estado():
    if "organizacoes" not in st.session_state:
        st.session_state.organizacoes = {}

    if "organizacao_ativa_id" not in st.session_state:
        st.session_state.organizacao_ativa_id = None


def organizacao_ativa():
    codigo = st.session_state.get("organizacao_ativa_id")

    if not codigo:
        return None

    return st.session_state.organizacoes.get(codigo)


def dados_ativos():
    organizacao = organizacao_ativa()

    if not organizacao:
        return None

    if "dados" not in organizacao:
        organizacao["dados"] = criar_dados()

    return organizacao["dados"]


# ============================================================
# FUNÇÕES AUXILIARES
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
    texto = re.sub(r"[^a-zA-Z0-9]+", "-", texto.lower())
    return texto.strip("-") or "organizacao"


def proximo_id(registros):
    ids = []

    for item in registros:
        try:
            ids.append(int(item.get("ID", 0)))
        except (TypeError, ValueError):
            pass

    return max(ids, default=0) + 1


def dataframe_lista(registros, colunas):
    if not registros:
        return pd.DataFrame(columns=colunas)

    df = pd.DataFrame(registros)

    for coluna in colunas:
        if coluna not in df.columns:
            df[coluna] = ""

    return df[colunas]


def calcular_assessment(dados):
    resultado = {}

    for dimensao in DIMENSOES:
        valores = []

        for indice in range(len(PERGUNTAS_NIST[dimensao])):
            chave = f"{dimensao}_{indice}"
            resposta = dados["assessment"].get(
                chave,
                "Não implementado",
            )
            valores.append(NIVEIS_MATURIDADE.get(resposta, 0))

        resultado[dimensao] = (
            sum(valores) / len(valores)
            if valores
            else 0
        )

    resultado["Geral"] = (
        sum(resultado[d] for d in DIMENSOES) / len(DIMENSOES)
        if DIMENSOES
        else 0
    )

    return resultado


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
    valor = probabilidade * impacto

    if valor >= 20:
        return "Crítico"
    if valor >= 12:
        return "Alto"
    if valor >= 6:
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


def progresso_framework(dados, framework):
    controles = CONTROLES_FRAMEWORKS.get(framework, [])

    if not controles:
        return 0

    valores = []

    for controle in controles:
        chave = f"{framework}_{controle['codigo']}"
        registro = dados["adequacao"].get(chave, {})
        status = registro.get("status", "Não iniciado")
        valores.append(PERCENTUAL_STATUS.get(status, 0))

    return sum(valores) / len(valores)


# ============================================================
# PDF
# ============================================================

def limpar_texto_pdf(valor, padrao="-"):
    if valor is None:
        return padrao

    try:
        if pd.isna(valor):
            return padrao
    except (TypeError, ValueError):
        pass

    texto = str(valor).strip()

    if not texto:
        return padrao

    substituicoes = {
        "—": "-",
        "–": "-",
        "“": '"',
        "”": '"',
        "‘": "'",
        "’": "'",
        "✅": "",
        "🛡️": "",
        "•": "-",
        "→": "->",
        "←": "<-",
        "…": "...",
        "\t": " ",
        "\r": " ",
    }

    for origem, destino in substituicoes.items():
        texto = texto.replace(origem, destino)

    texto = "".join(
        c for c in texto
        if c == "\n" or ord(c) >= 32
    )

    texto = (
        texto.encode("latin-1", "replace")
        .decode("latin-1")
        .strip()
    )

    return texto or padrao


def quebrar_textos_longos(texto, limite=75):
    texto = limpar_texto_pdf(texto)
    resultado = []

    for linha in texto.splitlines():
        linha = linha.strip()

        if not linha:
            resultado.append("-")
            continue

        palavras = linha.split()
        atual = ""

        for palavra in palavras:
            while len(palavra) > limite:
                if atual:
                    resultado.append(atual)
                    atual = ""

                resultado.append(palavra[:limite])
                palavra = palavra[limite:]

            if not palavra:
                continue

            candidato = (
                palavra
                if not atual
                else f"{atual} {palavra}"
            )

            if len(candidato) > limite:
                resultado.append(atual)
                atual = palavra
            else:
                atual = candidato

        if atual:
            resultado.append(atual)

    return "\n".join(resultado) or "-"


class RelatorioPDF(FPDF):
    def __init__(self):
        super().__init__(
            orientation="P",
            unit="mm",
            format="A4",
        )

        self.set_margins(15, 22, 15)
        self.set_auto_page_break(True, 18)

    def largura_total(self):
        return max(
            self.w - self.l_margin - self.r_margin,
            1,
        )

    def largura_disponivel(self):
        return max(
            self.w - self.r_margin - self.get_x(),
            1,
        )

    def garantir_linha(self, altura=6):
        if self.get_y() + altura > self.h - self.b_margin:
            self.add_page()

    def header(self):
        self.set_fill_color(11, 48, 64)
        self.rect(0, 0, self.w, 18, "F")

        self.set_text_color(255, 255, 255)
        self.set_font("Arial", "B", 13)

        self.cell(
            self.largura_total(),
            10,
            "CTR DEFENSE",
            align="C",
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
        )

        self.ln(8)
        self.set_text_color(16, 47, 59)

    def footer(self):
        self.set_y(-15)
        self.set_text_color(100, 100, 100)
        self.set_font("Arial", "", 8)

        self.cell(
            self.largura_total(),
            10,
            f"Pagina {self.page_no()}",
            align="C",
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
        )


def pdf_texto(pdf, texto, altura=6):
    pdf.garantir_linha(altura)
    pdf.set_font("Arial", "", 9)

    pdf.multi_cell(
        pdf.largura_total(),
        altura,
        quebrar_textos_longos(texto),
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT,
    )


def pdf_linha(pdf, titulo, valor, largura_titulo=42):
    pdf.garantir_linha(7)

    largura_total = pdf.largura_total()
    largura_titulo = min(largura_titulo, largura_total - 20)
    largura_valor = max(largura_total - largura_titulo, 20)

    pdf.set_font("Arial", "B", 9)
    pdf.cell(
        largura_titulo,
        6,
        limpar_texto_pdf(titulo),
        new_x=XPos.RIGHT,
        new_y=YPos.TOP,
    )

    pdf.set_font("Arial", "", 9)
    pdf.multi_cell(
        largura_valor,
        6,
        quebrar_textos_longos(valor),
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT,
    )


def pdf_secao(pdf, titulo):
    pdf.garantir_linha(14)
    pdf.ln(4)

    pdf.set_font("Arial", "B", 13)
    pdf.set_text_color(11, 48, 64)

    pdf.cell(
        pdf.largura_total(),
        8,
        limpar_texto_pdf(titulo),
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT,
    )

    pdf.set_text_color(16, 47, 59)


def gerar_pdf_relatorio(organizacao, dados):
    pdf = RelatorioPDF()
    pdf.add_page()

    pdf.set_font("Arial", "B", 18)
    pdf.cell(
        pdf.largura_total(),
        12,
        "Relatorio Executivo de Ciberseguranca",
        align="C",
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT,
    )

    pdf.set_font("Arial", "", 10)
    pdf.cell(
        pdf.largura_total(),
        7,
        limpar_texto_pdf(
            datetime.now().strftime(
                "Emissao: %d/%m/%Y %H:%M"
            )
        ),
        align="C",
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT,
    )

    pdf_secao(pdf, "Identificacao da organizacao")

    pdf_linha(pdf, "Organizacao:", organizacao.get("nome"))
    pdf_linha(pdf, "Segmento:", organizacao.get("segmento"))
    pdf_linha(pdf, "Responsavel:", organizacao.get("responsavel"))
    pdf_linha(pdf, "E-mail:", organizacao.get("email"))

    resultado = calcular_assessment(dados)

    pdf_secao(pdf, "Resumo executivo")

    pdf_linha(
        pdf,
        "Maturidade geral:",
        (
            f"{resultado['Geral']:.2f}/5 - "
            f"{classificar_maturidade(resultado['Geral'])}"
        ),
    )

    pdf_linha(pdf, "Total de riscos:", len(dados["riscos"]))
    pdf_linha(pdf, "Total de gaps:", len(dados["gaps"]))
    pdf_linha(pdf, "Total de acoes:", len(dados["acoes"]))
    pdf_linha(pdf, "Total de iniciativas:", len(dados["roadmap"]))

    pdf_secao(pdf, "Maturidade NIST CSF 2.0")

    for dimensao in DIMENSOES:
        pdf_linha(
            pdf,
            f"{dimensao}:",
            (
                f"{resultado[dimensao]:.2f}/5 - "
                f"{classificar_maturidade(resultado[dimensao])}"
            ),
        )

    pdf_secao(pdf, "Adequacao por framework")

    for framework in CONTROLES_FRAMEWORKS:
        pdf_linha(
            pdf,
            f"{framework}:",
            f"{progresso_framework(dados, framework):.1f}%",
        )

    pdf.add_page()

    pdf_secao(pdf, "Riscos")

    if not dados["riscos"]:
        pdf_texto(pdf, "Nenhum risco registrado.")
    else:
        for risco in dados["riscos"]:
            pdf_texto(
                pdf,
                (
                    f"#{risco.get('ID', '-')} - "
                    f"{risco.get('Risco', '-')} | "
                    f"Nivel: {risco.get('Nível', '-')} | "
                    f"Status: {risco.get('Status', '-')}"
                ),
            )

    pdf_secao(pdf, "Gaps")

    if not dados["gaps"]:
        pdf_texto(pdf, "Nenhum gap registrado.")
    else:
        for gap in dados["gaps"]:
            pdf_texto(
                pdf,
                (
                    f"#{gap.get('ID', '-')} - "
                    f"{gap.get('Controle', '-')} | "
                    f"Framework: {gap.get('Framework', '-')} | "
                    f"Criticidade: {gap.get('Criticidade', '-')} | "
                    f"Status: {gap.get('Status', '-')}"
                ),
            )

    pdf_secao(pdf, "Plano de acao")

    if not dados["acoes"]:
        pdf_texto(pdf, "Nenhuma acao registrada.")
    else:
        for acao in dados["acoes"]:
            pdf_texto(
                pdf,
                (
                    f"#{acao.get('ID', '-')} - "
                    f"{acao.get('Ação', '-')} | "
                    f"Prioridade: {acao.get('Prioridade', '-')} | "
                    f"Prazo: {acao.get('Prazo', '-')} | "
                    f"Status: {acao.get('Status', '-')}"
                ),
            )

    return bytes(pdf.output())


# ============================================================
# ORGANIZAÇÕES
# ============================================================

def modulo_organizacoes():
    cabecalho(
        "Organizacoes",
        "Cadastre e selecione o cliente da CTR DEFENSE.",
    )

    with st.form("form_organizacao", clear_on_submit=True):
        nome = st.text_input("Nome da organizacao")
        segmento = st.text_input("Segmento")
        responsavel = st.text_input("Responsavel")
        email = st.text_input("E-mail")

        salvar = st.form_submit_button(
            "Cadastrar organizacao",
            type="primary",
            use_container_width=True,
        )

        if salvar:
            if not nome.strip():
                st.error("Informe o nome da organizacao.")
                return

            base = normalizar_id(nome)
            codigo = base
            contador = 2

            while codigo in st.session_state.organizacoes:
                codigo = f"{base}-{contador}"
                contador += 1

            st.session_state.organizacoes[codigo] = {
                "id": codigo,
                "nome": nome.strip(),
                "segmento": segmento.strip(),
                "responsavel": responsavel.strip(),
                "email": email.strip(),
                "dados": criar_dados(),
            }

            st.session_state.organizacao_ativa_id = codigo
            st.success("Organizacao cadastrada.")
            st.rerun()

    if not st.session_state.organizacoes:
        st.info("Nenhuma organizacao cadastrada.")
        return

    for codigo, organizacao in st.session_state.organizacoes.items():
        ativa = codigo == st.session_state.organizacao_ativa_id

        with st.expander(
            f"{'Ativa - ' if ativa else ''}{organizacao['nome']}",
            expanded=ativa,
        ):
            st.write(
                f"**Segmento:** "
                f"{organizacao.get('segmento') or '-'}"
            )
            st.write(
                f"**Responsavel:** "
                f"{organizacao.get('responsavel') or '-'}"
            )
            st.write(
                f"**E-mail:** "
                f"{organizacao.get('email') or '-'}"
            )

            col1, col2 = st.columns(2)

            if col1.button(
                "Selecionar",
                key=f"selecionar_{codigo}",
                use_container_width=True,
            ):
                st.session_state.organizacao_ativa_id = codigo
                st.rerun()

            if col2.button(
                "Excluir",
                key=f"excluir_{codigo}",
                use_container_width=True,
            ):
                del st.session_state.organizacoes[codigo]

                if ativa:
                    st.session_state.organizacao_ativa_id = None

                st.rerun()


# ============================================================
# DASHBOARD
# ============================================================

def modulo_dashboard():
    organizacao = organizacao_ativa()
    dados = dados_ativos()

    if not organizacao or not dados:
        st.warning("Cadastre ou selecione uma organizacao.")
        return

    cabecalho(
        f"Dashboard Executivo - {organizacao['nome']}",
        "Visao consolidada da seguranca e conformidade.",
    )

    resultado = calcular_assessment(dados)

    riscos_criticos = sum(
        item.get("Nível") == "Crítico"
        and item.get("Status") != "Encerrado"
        for item in dados["riscos"]
    )

    gaps_criticos = sum(
        item.get("Criticidade") == "Crítica"
        and item.get("Status") != "Concluído"
        for item in dados["gaps"]
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Maturidade",
        f"{resultado['Geral']:.2f}/5",
        classificar_maturidade(resultado["Geral"]),
    )
    col2.metric("Riscos criticos", riscos_criticos)
    col3.metric("Gaps criticos", gaps_criticos)
    col4.metric("Acoes", len(dados["acoes"]))

    esquerda, direita = st.columns(2)

    with esquerda:
        radar = go.Figure(
            go.Scatterpolar(
                r=[resultado[item] for item in DIMENSOES],
                theta=DIMENSOES,
                fill="toself",
                line_color="#047f9e",
            )
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
        )

        st.plotly_chart(radar, use_container_width=True)

    with direita:
        df = pd.DataFrame(
            {
                "Framework": list(CONTROLES_FRAMEWORKS),
                "Conformidade": [
                    progresso_framework(dados, framework)
                    for framework in CONTROLES_FRAMEWORKS
                ],
            }
        )

        figura = px.bar(
            df,
            x="Framework",
            y="Conformidade",
            range_y=[0, 100],
            color="Conformidade",
            title="Conformidade por framework",
        )

        figura.update_layout(coloraxis_showscale=False)
        st.plotly_chart(figura, use_container_width=True)


# ============================================================
# ASSESSMENT
# ============================================================

def modulo_assessment():
    organizacao = organizacao_ativa()
    dados = dados_ativos()

    if not organizacao or not dados:
        st.error("Nenhuma organizacao ativa.")
        return

    cabecalho(
        "Assessment NIST CSF 2.0",
        "Avalie as seis funcoes do NIST Cybersecurity Framework.",
    )

    abas = st.tabs(DIMENSOES)
    opcoes = list(NIVEIS_MATURIDADE)

    for aba, dimensao in zip(abas, DIMENSOES):
        with aba:
            for indice, pergunta in enumerate(
                PERGUNTAS_NIST[dimensao]
            ):
                chave = f"{dimensao}_{indice}"

                st.markdown(
                    f"""
                    <div class="question-card">
                        <strong>
                            {indice + 1}. {pergunta}
                        </strong>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                atual = dados["assessment"].get(
                    chave,
                    "Não implementado",
                )

                resposta = st.selectbox(
                    "Nivel de implementacao",
                    opcoes,
                    index=opcoes.index(atual),
                    key=f"assessment_{organizacao['id']}_{chave}",
                )

                dados["assessment"][chave] = resposta

    resultado = calcular_assessment(dados)

    st.subheader("Resultado")

    colunas = st.columns(6)

    for coluna, dimensao in zip(colunas, DIMENSOES):
        coluna.metric(
            dimensao,
            f"{resultado[dimensao]:.2f}/5",
        )

    st.metric(
        "Maturidade geral",
        f"{resultado['Geral']:.2f}/5",
        classificar_maturidade(resultado["Geral"]),
    )


# ============================================================
# FRAMEWORKS
# ============================================================

def modulo_framework(framework):
    organizacao = organizacao_ativa()
    dados = dados_ativos()

    if not organizacao or not dados:
        st.error("Nenhuma organizacao ativa.")
        return

    controles = CONTROLES_FRAMEWORKS[framework]

    if framework == "CIS Controls v8":
        subtitulo = (
            "18 controles com priorizacao operacional "
            "por grupos IG1, IG2 e IG3."
        )
    elif framework == "NIST RMF":
        subtitulo = (
            "Acompanhamento das sete etapas do "
            "Risk Management Framework."
        )
    else:
        subtitulo = "Acompanhamento de adequacao do framework."

    cabecalho(framework, subtitulo)

    if framework == "CIS Controls v8":
        st.info(
            "IG1: essencial | IG2: intermediario | "
            "IG3: avancado."
        )

        grupos = st.multiselect(
            "Filtrar por grupo",
            ["IG1", "IG2", "IG3"],
            default=["IG1", "IG2", "IG3"],
        )

        controles_exibidos = [
            item for item in controles
            if item.get("prioridade") in grupos
        ]
    else:
        controles_exibidos = controles

    progresso = progresso_framework(dados, framework)

    col1, col2, col3 = st.columns(3)

    col1.metric("Conformidade", f"{progresso:.1f}%")
    col2.metric("Controles/etapas", len(controles))
    col3.metric(
        "Implementados",
        sum(
            dados["adequacao"].get(
                f"{framework}_{item['codigo']}",
                {},
            ).get("status")
            in ["Implementado", "Não aplicável"]
            for item in controles
        ),
    )

    st.progress(progresso / 100)

    for controle in controles_exibidos:
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

        prioridade = ""

        if controle.get("prioridade"):
            prioridade = f" | {controle['prioridade']}"

        with st.expander(
            f"{controle['codigo']} - "
            f"{controle['controle']}{prioridade}"
        ):
            st.write(
                f"**Categoria:** "
                f"{controle.get('categoria', '-')}"
            )

            if controle.get("descricao"):
                st.write(
                    f"**Descricao:** {controle['descricao']}"
                )

            status_atual = registro.get(
                "status",
                "Não iniciado",
            )

            if status_atual not in STATUS_ADEQUACAO:
                status_atual = "Não iniciado"

            col1, col2 = st.columns(2)

            status = col1.selectbox(
                "Status",
                STATUS_ADEQUACAO,
                index=STATUS_ADEQUACAO.index(status_atual),
                key=f"status_{organizacao['id']}_{chave}",
            )

            responsavel = col2.text_input(
                "Responsavel",
                value=registro.get("responsavel", ""),
                key=f"resp_{organizacao['id']}_{chave}",
            )

            col3, col4 = st.columns(2)

            try:
                prazo_inicial = date.fromisoformat(
                    registro.get("prazo", "")
                )
            except (TypeError, ValueError):
                prazo_inicial = date.today() + timedelta(days=90)

            prazo = col3.date_input(
                "Prazo",
                prazo_inicial,
                format="DD/MM/YYYY",
                key=f"prazo_{organizacao['id']}_{chave}",
            )

            evidencia = col4.text_input(
                "Evidencia",
                value=registro.get("evidencia", ""),
                key=f"evidencia_{organizacao['id']}_{chave}",
            )

            observacoes = st.text_area(
                "Observacoes",
                value=registro.get("observacoes", ""),
                key=f"obs_{organizacao['id']}_{chave}",
            )

            dados["adequacao"][chave] = {
                "status": status,
                "responsavel": responsavel,
                "prazo": prazo.isoformat(),
                "evidencia": evidencia,
                "observacoes": observacoes,
            }

    st.subheader("Resumo tecnico")

    linhas = []

    for controle in controles:
        chave = f"{framework}_{controle['codigo']}"
        registro = dados["adequacao"].get(chave, {})

        linha = {
            "Codigo": controle["codigo"],
            "Controle/Etapa": controle["controle"],
            "Categoria": controle.get("categoria", ""),
            "Status": registro.get("status", "Não iniciado"),
            "Percentual": PERCENTUAL_STATUS.get(
                registro.get("status", "Não iniciado"),
                0,
            ),
            "Responsavel": registro.get("responsavel", ""),
            "Prazo": registro.get("prazo", ""),
            "Evidencia": registro.get("evidencia", ""),
        }

        if controle.get("prioridade"):
            linha["Prioridade"] = controle["prioridade"]

        linhas.append(linha)

    df = pd.DataFrame(linhas)

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
    )

    st.download_button(
        "Baixar framework em CSV",
        data=df.to_csv(
            index=False,
            sep=";",
        ).encode("utf-8-sig"),
        file_name=(
            f"{normalizar_id(framework)}-"
            f"{organizacao['id']}.csv"
        ),
        mime="text/csv",
        use_container_width=True,
    )


# ============================================================
# RISCOS
# ============================================================

def modulo_riscos():
    organizacao = organizacao_ativa()
    dados = dados_ativos()

    if not organizacao or not dados:
        st.error("Nenhuma organizacao ativa.")
        return

    cabecalho(
        "Matriz de Riscos",
        "Registre e classifique os riscos da organizacao.",
    )

    with st.form(f"form_risco_{organizacao['id']}"):
        risco = st.text_area("Descricao do risco")

        col1, col2, col3 = st.columns(3)

        categoria = col1.selectbox(
            "Categoria",
            [
                "Governanca",
                "Tecnologia",
                "Pessoas",
                "Processos",
                "Terceiros",
                "Privacidade",
            ],
        )

        probabilidade = col2.slider(
            "Probabilidade",
            1,
            5,
            3,
        )

        impacto = col3.slider(
            "Impacto",
            1,
            5,
            3,
        )

        tratamento = st.selectbox(
            "Tratamento",
            ["Mitigar", "Evitar", "Transferir", "Aceitar"],
        )

        responsavel = st.text_input("Responsavel")

        status = st.selectbox(
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

    st.dataframe(
        dataframe_lista(
            dados["riscos"],
            COLUNAS_RISCOS,
        ),
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# GAPS
# ============================================================

def modulo_gaps():
    organizacao = organizacao_ativa()
    dados = dados_ativos()

    if not organizacao or not dados:
        st.error("Nenhuma organizacao ativa.")
        return

    cabecalho(
        "Gap Analysis",
        "Compare o estado atual com o estado desejado.",
    )

    with st.form(f"form_gap_{organizacao['id']}"):
        framework = st.selectbox(
            "Framework",
            list(CONTROLES_FRAMEWORKS),
        )

        controle = st.text_input("Controle ou requisito")

        col1, col2 = st.columns(2)

        atual = col1.slider("Estado atual", 0, 5, 1)
        desejado = col2.slider("Estado desejado", 0, 5, 3)

        recomendacao = st.text_area("Recomendacao")
        responsavel = st.text_input("Responsavel")

        prazo = st.date_input(
            "Prazo",
            date.today() + timedelta(days=60),
            format="DD/MM/YYYY",
        )

        status = st.selectbox(
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
                st.error("Informe o controle.")
            elif desejado < atual:
                st.error(
                    "O estado desejado deve ser maior ou igual ao atual."
                )
            else:
                valor_gap = desejado - atual

                dados["gaps"].append(
                    {
                        "ID": proximo_id(dados["gaps"]),
                        "Framework": framework,
                        "Controle": controle.strip(),
                        "Estado Atual": atual,
                        "Estado Desejado": desejado,
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

    st.dataframe(
        dataframe_lista(dados["gaps"], COLUNAS_GAPS),
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# AÇÕES
# ============================================================

def modulo_acoes():
    organizacao = organizacao_ativa()
    dados = dados_ativos()

    if not organizacao or not dados:
        st.error("Nenhuma organizacao ativa.")
        return

    cabecalho(
        "Plano de Acao",
        "Gerencie acoes corretivas e preventivas.",
    )

    with st.form(f"form_acao_{organizacao['id']}"):
        acao = st.text_area("Descricao da acao")

        origem = st.selectbox(
            "Origem",
            [
                "Assessment",
                "Risco",
                "Gap Analysis",
                "CIS Controls v8",
                "NIST RMF",
                "Outro",
            ],
        )

        prioridade = st.selectbox(
            "Prioridade",
            ["Critica", "Alta", "Media", "Baixa"],
        )

        responsavel = st.text_input("Responsavel")

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
            "Adicionar acao",
            type="primary",
            use_container_width=True,
        )

        if salvar:
            if not acao.strip():
                st.error("Descreva a acao.")
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

                st.success("Acao adicionada.")
                st.rerun()

    st.dataframe(
        dataframe_lista(dados["acoes"], COLUNAS_ACOES),
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# ROADMAP
# ============================================================

def modulo_roadmap():
    organizacao = organizacao_ativa()
    dados = dados_ativos()

    if not organizacao or not dados:
        st.error("Nenhuma organizacao ativa.")
        return

    cabecalho(
        "Roadmap de Seguranca",
        "Planeje e acompanhe as iniciativas.",
    )

    with st.form(f"form_roadmap_{organizacao['id']}"):
        iniciativa = st.text_area("Iniciativa")

        pilar = st.selectbox(
            "Pilar",
            [
                "Governanca",
                "Gestao de Riscos",
                "CIS Controls v8",
                "NIST RMF",
                "NIST CSF 2.0",
                "LGPD",
                "ISO 27001",
            ],
        )

        col1, col2 = st.columns(2)

        inicio = col1.date_input(
            "Inicio",
            date.today(),
            format="DD/MM/YYYY",
        )

        fim = col2.date_input(
            "Fim",
            date.today() + timedelta(days=90),
            format="DD/MM/YYYY",
        )

        prioridade = st.selectbox(
            "Prioridade",
            ["Critica", "Alta", "Media", "Baixa"],
        )

        responsavel = st.text_input("Responsavel")
        progresso = st.slider("Progresso", 0, 100, 0, 5)

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
                st.error(
                    "A data final não pode ser anterior à inicial."
                )
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

    st.dataframe(
        dataframe_lista(
            dados["roadmap"],
            COLUNAS_ROADMAP,
        ),
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# REUNIÕES
# ============================================================

def modulo_reunioes():
    organizacao = organizacao_ativa()
    dados = dados_ativos()

    if not organizacao or not dados:
        st.error("Nenhuma organizacao ativa.")
        return

    cabecalho(
        "Reunioes",
        "Registre decisoes e proximos passos.",
    )

    with st.form(f"form_reuniao_{organizacao['id']}"):
        data_reuniao = st.date_input(
            "Data",
            date.today(),
            format="DD/MM/YYYY",
        )

        titulo = st.text_input("Titulo")
        participantes = st.text_input("Participantes")
        notas = st.text_area("Notas")

        salvar = st.form_submit_button(
            "Salvar reuniao",
            type="primary",
            use_container_width=True,
        )

        if salvar:
            if not titulo.strip():
                st.error("Informe o titulo.")
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

                st.success("Reuniao registrada.")
                st.rerun()

    for item in reversed(dados["reunioes"]):
        with st.expander(
            f"{item['Data']} - {item['Título']}"
        ):
            st.write(
                f"**Participantes:** "
                f"{item.get('Participantes') or '-'}"
            )
            st.write(item.get("Notas") or "-")


# ============================================================
# CSV
# ============================================================

def gerar_csv(organizacao, dados):
    buffer = io.StringIO()

    def escrever_linha(*valores):
        valores_limpos = []

        for valor in valores:
            texto = str(valor if valor is not None else "")
            texto = texto.replace('"', '""')
            valores_limpos.append(f'"{texto}"')

        buffer.write(";".join(valores_limpos) + "\n")

    escrever_linha("CTR DEFENSE - RELATORIO CONSOLIDADO")
    escrever_linha("Organizacao", organizacao.get("nome", "-"))
    escrever_linha(
        "Emissao",
        datetime.now().strftime("%d/%m/%Y %H:%M"),
    )
    buffer.write("\n")

    resultado = calcular_assessment(dados)

    escrever_linha("MATURIDADE NIST CSF 2.0")
    escrever_linha("Dimensao", "Pontuacao", "Nivel")

    for dimensao in DIMENSOES:
        escrever_linha(
            dimensao,
            f"{resultado[dimensao]:.2f}",
            classificar_maturidade(resultado[dimensao]),
        )

    secoes = [
        ("RISCOS", dados["riscos"], COLUNAS_RISCOS),
        ("GAPS", dados["gaps"], COLUNAS_GAPS),
        ("ACOES", dados["acoes"], COLUNAS_ACOES),
        ("ROADMAP", dados["roadmap"], COLUNAS_ROADMAP),
        ("REUNIOES", dados["reunioes"], COLUNAS_REUNIOES),
    ]

    for nome, registros, colunas in secoes:
        buffer.write("\n")
        escrever_linha(nome)

        df = dataframe_lista(registros, colunas)

        if df.empty:
            escrever_linha("Nenhum registro")
            continue

        escrever_linha(*df.columns.tolist())

        for linha in df.itertuples(index=False):
            escrever_linha(*linha)

    return buffer.getvalue().encode("utf-8-sig")


# ============================================================
# RELATÓRIOS
# ============================================================

def modulo_relatorios():
    organizacao = organizacao_ativa()
    dados = dados_ativos()

    if not organizacao or not dados:
        st.error("Nenhuma organizacao ativa.")
        return

    cabecalho(
        "Relatorios",
        "Exporte os dados consolidados da organizacao.",
    )

    resultado = calcular_assessment(dados)

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Maturidade",
        f"{resultado['Geral']:.2f}/5",
    )
    col2.metric("Riscos", len(dados["riscos"]))
    col3.metric("Gaps", len(dados["gaps"]))
    col4.metric("Acoes", len(dados["acoes"]))

    st.subheader("Adequacao dos frameworks")

    df_frameworks = pd.DataFrame(
        [
            {
                "Framework": framework,
                "Conformidade": round(
                    progresso_framework(dados, framework),
                    1,
                ),
            }
            for framework in CONTROLES_FRAMEWORKS
        ]
    )

    st.dataframe(
        df_frameworks,
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Maturidade por dimensao")

    df_maturidade = pd.DataFrame(
        [
            {
                "Dimensao": dimensao,
                "Pontuacao": round(resultado[dimensao], 2),
                "Nivel": classificar_maturidade(
                    resultado[dimensao]
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

    pdf = gerar_pdf_relatorio(organizacao, dados)
    csv = gerar_csv(organizacao, dados)

    col_pdf, col_csv = st.columns(2)

    col_pdf.download_button(
        "Baixar relatorio em PDF",
        data=pdf,
        file_name=f"relatorio-{organizacao['id']}.pdf",
        mime="application/pdf",
        use_container_width=True,
    )

    col_csv.download_button(
        "Baixar relatorio em CSV",
        data=csv,
        file_name=f"relatorio-{organizacao['id']}.csv",
        mime="text/csv",
        use_container_width=True,
    )


# ============================================================
# SIDEBAR
# ============================================================

def construir_sidebar():
    st.sidebar.markdown("## CTR DEFENSE")

    st.sidebar.markdown(
        """
        <div style="
            padding: .7rem;
            border: 1px solid rgba(255,255,255,.3);
            border-radius: 8px;
            margin-bottom: 1rem;
        ">
            <strong>Administrador CTR</strong><br>
            <small>Perfil: Administrador</small>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.session_state.organizacoes:
        ids = list(st.session_state.organizacoes)
        atual = st.session_state.organizacao_ativa_id

        if atual not in ids:
            atual = ids[0]
            st.session_state.organizacao_ativa_id = atual

        selecionada = st.sidebar.selectbox(
            "Organizacao ativa",
            ids,
            index=ids.index(atual),
            format_func=lambda codigo:
                st.session_state.organizacoes[codigo]["nome"],
        )

        if selecionada != atual:
            st.session_state.organizacao_ativa_id = selecionada
            st.rerun()
    else:
        st.sidebar.warning("Cadastre uma organizacao.")

    menu = st.sidebar.radio(
        "Modulos",
        [
            "Dashboard Executivo",
            "Organizacoes",
            "Assessment NIST",
            "CIS Controls v8",
            "NIST RMF",
            "Matriz de Riscos",
            "Gap Analysis",
            "Plano de Acao",
            "Roadmap de Seguranca",
            "Reunioes",
            "Relatorios",
        ],
    )

    st.sidebar.markdown("---")
    st.sidebar.caption(
        f"CTR DEFENSE - {datetime.now().year}"
    )

    st.sidebar.markdown(
        '<div class="logout-button">',
        unsafe_allow_html=True,
    )

    if st.sidebar.button(
        "Sair",
        use_container_width=True,
        key="sair",
    ):
        # Não apaga os dados das organizações.
        st.session_state.organizacao_ativa_id = None
        st.rerun()

    st.sidebar.markdown(
        "</div>",
        unsafe_allow_html=True,
    )

    return menu


# ============================================================
# EXECUÇÃO PRINCIPAL
# ============================================================

inicializar_estado()
menu = construir_sidebar()

if menu == "Dashboard Executivo":
    modulo_dashboard()

elif menu == "Organizacoes":
    modulo_organizacoes()

elif menu == "Assessment NIST":
    modulo_assessment()

elif menu == "CIS Controls v8":
    modulo_framework("CIS Controls v8")

elif menu == "NIST RMF":
    modulo_framework("NIST RMF")

elif menu == "Matriz de Riscos":
    modulo_riscos()

elif menu == "Gap Analysis":
    modulo_gaps()

elif menu == "Plano de Acao":
    modulo_acoes()

elif menu == "Roadmap de Seguranca":
    modulo_roadmap()

elif menu == "Reunioes":
    modulo_reunioes()

elif menu == "Relatorios":
    modulo_relatorios()
