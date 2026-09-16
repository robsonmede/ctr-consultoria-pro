import io
import re
import unicodedata
from datetime import date, datetime, timedelta

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


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
            background:
                linear-gradient(
                    135deg,
                    #edf4f7 0%,
                    #f9fbfc 50%,
                    #e6f0f4 100%
                );
            color: var(--ctr-text);
        }

        section[data-testid="stSidebar"] {
            background:
                linear-gradient(
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
            background-color: #ffffff !important;
        }

        section[data-testid="stSidebar"]
        div[data-baseweb="select"] > div {
            color: #102f3b !important;
            background-color: #ffffff !important;
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
            background-color: rgba(255, 255, 255, 0.96);
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
            margin-bottom: 0.7rem;
            border: 1px solid var(--ctr-border);
            border-radius: 12px;
            background-color: #ffffff;
            box-shadow: 0 5px 16px rgba(11, 48, 64, 0.05);
        }

        .question-card {
            padding: 0.85rem 1rem;
            margin: 0.6rem 0 0.25rem;
            border: 1px solid var(--ctr-border);
            border-left: 5px solid var(--ctr-primary);
            border-radius: 10px;
            background-color: #ffffff;
            color: var(--ctr-text);
        }

        div[data-testid="stMetric"] {
            padding: 1rem;
            border: 1px solid var(--ctr-border);
            border-radius: 12px;
            background-color: #ffffff;
            box-shadow: 0 5px 16px rgba(11, 48, 64, 0.06);
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
            background-color: #e4f2f6 !important;
        }

        div[data-testid="stExpander"] {
            background-color: #ffffff;
            border-color: var(--ctr-border);
        }

        .stButton > button,
        .stDownloadButton > button {
            border-radius: 8px;
            border-color: var(--ctr-primary);
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
        "Existe um registro formal de riscos cibernéticos?",
        "Serviços e dependências críticas estão documentados?",
    ],
    "Proteger": [
        "Os acessos seguem o princípio do menor privilégio?",
        "Autenticação multifator é utilizada em acessos críticos?",
        "Colaboradores recebem treinamento de segurança?",
        "Backups são protegidos contra alteração e exclusão?",
        "Existe processo formal de atualização e gestão de patches?",
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
            "controle": "Plano de resposta a incidentes de privacidade",
            "categoria": "Incidentes",
        },
        {
            "codigo": "LGPD-07",
            "controle": "Relatório de impacto à proteção de dados",
            "categoria": "Riscos",
        },
        {
            "codigo": "LGPD-08",
            "controle": "Programa de governança em privacidade",
            "categoria": "Governança",
        },
    ],
    "NIST CSF 2.0": [
        {
            "codigo": "GV",
            "controle": "Governar os riscos de cibersegurança",
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
            "controle": "Recursos, competências e conscientização",
            "categoria": "Suporte",
        },
        {
            "codigo": "ISO-08",
            "controle": "Operação do SGSI",
            "categoria": "Operação",
        },
        {
            "codigo": "ISO-09",
            "controle": "Avaliação de desempenho e auditoria",
            "categoria": "Avaliação",
        },
        {
            "codigo": "ISO-10",
            "controle": "Não conformidades e melhoria contínua",
            "categoria": "Melhoria",
        },
        {
            "codigo": "ISO-A.5",
            "controle": "Controles organizacionais",
            "categoria": "Anexo A",
        },
        {
            "codigo": "ISO-A.8",
            "controle": "Controles tecnológicos",
            "categoria": "Anexo A",
        },
    ],
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
        "roadmap": [],
        "gaps": [],
        "adequacao": {},
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

    if not texto:
        texto = f"organizacao-{int(datetime.now().timestamp())}"

    return texto


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

    dados = organizacao["dados"]

    estrutura = criar_dados_organizacao()

    for chave, valor_padrao in estrutura.items():
        if chave not in dados:
            dados[chave] = valor_padrao

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


def proximo_id(registros):
    ids = []

    for registro in registros:
        try:
            ids.append(int(registro.get("ID", 0)))
        except (TypeError, ValueError):
            continue

    return max(ids, default=0) + 1


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

        for indice, _ in enumerate(PERGUNTAS_NIST[dimensao]):
            chave = f"{dimensao}_{indice}"
            resposta = dados["assessment"].get(
                chave,
                "Não implementado",
            )
            valores.append(NIVEIS_MATURIDADE.get(resposta, 0))

        resultados[dimensao] = (
            sum(valores) / len(valores)
            if valores
            else 0
        )

    resultados["Geral"] = (
        sum(resultados[dimensao] for dimensao in DIMENSOES)
        / len(DIMENSOES)
    )

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


def classificar_gap(gap):
    if gap >= 4:
        return "Crítica"
    if gap == 3:
        return "Alta"
    if gap == 2:
        return "Média"

    return "Baixa"


def calcular_progresso_adequacao(dados, framework):
    controles = CONTROLES_FRAMEWORKS[framework]
    valores = []

    for controle in controles:
        chave = f"{framework}_{controle['codigo']}"
        registro = dados["adequacao"].get(chave, {})
        status = registro.get("status", "Não iniciado")
        valores.append(PERCENTUAL_STATUS.get(status, 0))

    return sum(valores) / len(valores) if valores else 0


def percentual_acoes_concluidas(dados):
    if not dados["acoes"]:
        return 0

    concluidas = sum(
        1
        for acao in dados["acoes"]
        if acao.get("Status") == "Concluída"
    )

    return 100 * concluidas / len(dados["acoes"])


def adicionar_gap_ao_roadmap(dados, gap):
    inicio = date.today()
    fim = inicio + timedelta(days=90)

    dados["roadmap"].append(
        {
            "ID": proximo_id(dados["roadmap"]),
            "Iniciativa": gap["Recomendação"],
            "Pilar": gap["Framework"],
            "Início": inicio.isoformat(),
            "Fim": fim.isoformat(),
            "Prioridade": gap["Criticidade"],
            "Responsável": gap["Responsável"],
            "Progresso": 0,
            "Status": "Planejado",
        }
    )


def gerar_csv_consolidado(organizacao, dados):
    buffer = io.StringIO()

    buffer.write("CTR DEFENSE - RELATORIO CONSOLIDADO\n")
    buffer.write(f"Organizacao;{organizacao['nome']}\n")
    buffer.write(f"Segmento;{organizacao.get('segmento', '')}\n")
    buffer.write(f"Responsavel;{organizacao.get('responsavel', '')}\n")
    buffer.write(
        f"Emissao;{datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
    )

    resultados = calcular_assessment(dados)

    buffer.write("ASSESSMENT NIST CSF 2.0\n")
    buffer.write("Dimensao;Pontuacao;Nivel\n")

    for dimensao in DIMENSOES:
        valor = resultados[dimensao]
        nivel = classificar_maturidade(valor)
        buffer.write(f"{dimensao};{valor:.2f};{nivel}\n")

    buffer.write(
        f"Geral;{resultados['Geral']:.2f};"
        f"{classificar_maturidade(resultados['Geral'])}\n\n"
    )

    secoes = [
        ("RISCOS", dados["riscos"], COLUNAS_RISCOS),
        ("PLANO DE ACAO", dados["acoes"], COLUNAS_ACOES),
        ("ROADMAP", dados["roadmap"], COLUNAS_ROADMAP),
        ("GAP ANALYSIS", dados["gaps"], COLUNAS_GAPS),
        ("REUNIOES", dados["reunioes"], COLUNAS_REUNIOES),
    ]

    for titulo, registros, colunas in secoes:
        buffer.write(f"{titulo}\n")
        df = dataframe_lista(registros, colunas)
        buffer.write(df.to_csv(index=False, sep=";"))
        buffer.write("\n")

    buffer.write("ADEQUACAO\n")
    buffer.write(
        "Framework;Codigo;Controle;Status;Responsavel;"
        "Prazo;Evidencia;Observacoes\n"
    )

    for framework, controles in CONTROLES_FRAMEWORKS.items():
        for controle in controles:
            chave = f"{framework}_{controle['codigo']}"
            registro = dados["adequacao"].get(chave, {})

            linha = [
                framework,
                controle["codigo"],
                controle["controle"],
                registro.get("status", "Não iniciado"),
                registro.get("responsavel", ""),
                registro.get("prazo", ""),
                registro.get("evidencia", ""),
                registro.get("observacoes", ""),
            ]

            linha = [
                str(valor).replace(";", ",").replace("\n", " ")
                for valor in linha
            ]

            buffer.write(";".join(linha) + "\n")

    return buffer.getvalue().encode("utf-8-sig")


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
                st.success("Organização cadastrada.")
                st.rerun()

    if not st.session_state.organizacoes:
        st.info("Nenhuma organização cadastrada.")
        return

    st.subheader("Clientes cadastrados")

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

    if organizacao is None or dados is None:
        st.warning("Cadastre ou selecione uma organização.")
        return

    cabecalho(
        f"Dashboard Executivo — {organizacao['nome']}",
        "Visão consolidada da postura de segurança e conformidade.",
    )

    resultados = calcular_assessment(dados)

    riscos_criticos = sum(
        1
        for risco in dados["riscos"]
        if risco.get("Nível") == "Crítico"
        and risco.get("Status") != "Encerrado"
    )

    gaps_criticos = sum(
        1
        for gap in dados["gaps"]
        if gap.get("Criticidade") == "Crítica"
        and gap.get("Status") != "Concluído"
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

        fig = px.bar(
            conformidade,
            x="Framework",
            y="Conformidade",
            range_y=[0, 100],
            color="Conformidade",
            color_continuous_scale=["#dceff4", "#047f9e", "#0b3040"],
            title="Adequação por framework",
        )

        fig.update_layout(
            coloraxis_showscale=False,
            height=430,
            paper_bgcolor="rgba(255,255,255,0)",
        )

        st.plotly_chart(fig, use_container_width=True)


# ============================================================
# ASSESSMENT NIST
# ============================================================

def modulo_assessment():
    organizacao = obter_organizacao_ativa()
    dados = obter_dados_ativos()

    if organizacao is None or dados is None:
        st.error("Nenhuma organização ativa foi encontrada.")
        return

    cabecalho(
        "Assessment NIST CSF 2.0",
        "Avalie a maturidade nas seis funções do framework.",
    )

    assessment = dados["assessment"]
    total = sum(len(lista) for lista in PERGUNTAS_NIST.values())

    preenchidas = sum(
        1
        for dimensao in DIMENSOES
        for indice in range(len(PERGUNTAS_NIST[dimensao]))
        if f"{dimensao}_{indice}" in assessment
    )

    st.write(f"Progresso: **{preenchidas}/{total} respostas**")
    st.progress(min(preenchidas / total, 1.0))

    abas = st.tabs(DIMENSOES)
    opcoes = list(NIVEIS_MATURIDADE.keys())

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

                if resposta_atual not in opcoes:
                    resposta_atual = "Não implementado"

                st.markdown(
                    (
                        '<div class="question-card">'
                        f"<strong>{indice + 1}. {pergunta}</strong>"
                        "</div>"
                    ),
                    unsafe_allow_html=True,
                )

                resposta = st.selectbox(
                    "Nível de implementação",
                    options=opcoes,
                    index=opcoes.index(resposta_atual),
                    key=(
                        f"assessment_{organizacao['id']}_"
                        f"{dimensao}_{indice}"
                    ),
                )

                assessment[chave] = resposta

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

    if st.button(
        "Limpar assessment",
        key=f"limpar_assessment_{organizacao['id']}",
    ):
        dados["assessment"] = {}
        prefixo = f"assessment_{organizacao['id']}_"

        for chave in list(st.session_state.keys()):
            if str(chave).startswith(prefixo):
                del st.session_state[chave]

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
        "Registre e classifique os riscos da organização.",
    )

    with st.form(
        f"form_risco_{organizacao['id']}",
        clear_on_submit=True,
    ):
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
        matriz = pd.DataFrame(
            0,
            index=[1, 2, 3, 4, 5],
            columns=[1, 2, 3, 4, 5],
        )

        for risco in dados["riscos"]:
            probabilidade = int(risco["Probabilidade"])
            impacto = int(risco["Impacto"])
            matriz.loc[probabilidade, impacto] += 1

        fig = px.imshow(
            matriz,
            x=[1, 2, 3, 4, 5],
            y=[1, 2, 3, 4, 5],
            text_auto=True,
            aspect="auto",
            labels={
                "x": "Impacto",
                "y": "Probabilidade",
                "color": "Quantidade",
            },
            color_continuous_scale=[
                [0, "#dcfce7"],
                [0.4, "#fef08a"],
                [0.7, "#fb923c"],
                [1, "#b91c1c"],
            ],
        )

        st.plotly_chart(fig, use_container_width=True)

        col1, col2 = st.columns([3, 1])

        risco_id = col1.selectbox(
            "Risco para exclusão",
            options=[item["ID"] for item in dados["riscos"]],
            format_func=lambda valor: next(
                (
                    f"#{item['ID']} — {item['Risco']}"
                    for item in dados["riscos"]
                    if item["ID"] == valor
                ),
                str(valor),
            ),
        )

        if col2.button(
            "Excluir risco",
            use_container_width=True,
        ):
            dados["riscos"] = remover_registro(
                dados["riscos"],
                risco_id,
            )
            st.rerun()


# ============================================================
# PLANO DE AÇÃO
# ============================================================

def modulo_plano_acao():
    organizacao = obter_organizacao_ativa()
    dados = obter_dados_ativos()

    if organizacao is None or dados is None:
        st.error("Nenhuma organização ativa foi encontrada.")
        return

    cabecalho(
        "Plano de Ação",
        "Gerencie ações corretivas, preventivas e de melhoria.",
    )

    with st.form(
        f"form_acao_{organizacao['id']}",
        clear_on_submit=True,
    ):
        acao = st.text_area("Descrição da ação")

        col1, col2, col3 = st.columns(3)

        origem = col1.selectbox(
            "Origem",
            [
                "Assessment",
                "Risco",
                "Gap Analysis",
                "Adequação",
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
            value=date.today() + timedelta(days=30),
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

    if dados["acoes"]:
        col1, col2 = st.columns([3, 1])

        acao_id = col1.selectbox(
            "Ação para exclusão",
            options=[item["ID"] for item in dados["acoes"]],
            format_func=lambda valor: next(
                (
                    f"#{item['ID']} — {item['Ação']}"
                    for item in dados["acoes"]
                    if item["ID"] == valor
                ),
                str(valor),
            ),
        )

        if col2.button(
            "Excluir ação",
            use_container_width=True,
        ):
            dados["acoes"] = remover_registro(
                dados["acoes"],
                acao_id,
            )
            st.rerun()


# ============================================================
# ROADMAP DE SEGURANÇA
# ============================================================

def modulo_roadmap():
    organizacao = obter_organizacao_ativa()
    dados = obter_dados_ativos()

    if organizacao is None or dados is None:
        st.error("Nenhuma organização ativa foi encontrada.")
        return

    cabecalho(
        "Roadmap de Segurança",
        "Planeje iniciativas estratégicas e acompanhe a execução.",
    )

    with st.form(
        f"form_roadmap_{organizacao['id']}",
        clear_on_submit=True,
    ):
        iniciativa = st.text_area("Iniciativa de segurança")

        col1, col2, col3 = st.columns(3)

        pilar = col1.selectbox(
            "Pilar",
            [
                "Governança",
                "Gestão de Riscos",
                "Identidade e Acesso",
                "Proteção de Dados",
                "Infraestrutura",
                "Detecção e Resposta",
                "Continuidade",
                "LGPD",
                "ISO 27001",
                "NIST CSF 2.0",
            ],
        )
        inicio = col2.date_input(
            "Data de início",
            value=date.today(),
            format="DD/MM/YYYY",
        )
        fim = col3.date_input(
            "Data de conclusão",
            value=date.today() + timedelta(days=90),
            format="DD/MM/YYYY",
        )

        col4, col5, col6 = st.columns(3)

        prioridade = col4.selectbox(
            "Prioridade",
            ["Crítica", "Alta", "Média", "Baixa"],
        )
        responsavel = col5.text_input("Responsável")
        status = col6.selectbox(
            "Status",
            [
                "Planejado",
                "Em andamento",
                "Bloqueado",
                "Concluído",
                "Cancelado",
            ],
        )

        progresso = st.slider(
            "Progresso da iniciativa",
            min_value=0,
            max_value=100,
            value=0,
            step=5,
            format="%d%%",
        )

        salvar = st.form_submit_button(
            "Adicionar ao roadmap",
            type="primary",
            use_container_width=True,
        )

        if salvar:
            if not iniciativa.strip():
                st.error("Descreva a iniciativa.")
            elif fim < inicio:
                st.error(
                    "A data de conclusão não pode ser anterior ao início."
                )
            else:
                if status == "Concluído":
                    progresso = 100

                dados["roadmap"].append(
                    {
                        "ID": proximo_id(dados["roadmap"]),
                        "Iniciativa": iniciativa.strip(),
                        "Pilar": pilar,
                        "Início": inicio.isoformat(),
                        "Fim": fim.isoformat(),
                        "Prioridade": prioridade,
                        "Responsável": responsavel.strip(),
                        "Progresso": progresso,
                        "Status": status,
                    }
                )

                st.success("Iniciativa adicionada ao roadmap.")
                st.rerun()

    if not dados["roadmap"]:
        st.info("Nenhuma iniciativa cadastrada no roadmap.")
        return

    st.subheader("Filtros")

    col_f1, col_f2 = st.columns(2)

    status_disponiveis = sorted(
        {
            item["Status"]
            for item in dados["roadmap"]
        }
    )
    pilares_disponiveis = sorted(
        {
            item["Pilar"]
            for item in dados["roadmap"]
        }
    )

    filtro_status = col_f1.multiselect(
        "Status",
        status_disponiveis,
        default=status_disponiveis,
    )
    filtro_pilar = col_f2.multiselect(
        "Pilar",
        pilares_disponiveis,
        default=pilares_disponiveis,
    )

    df = dataframe_lista(
        dados["roadmap"],
        COLUNAS_ROADMAP,
    )

    df_filtrado = df[
        df["Status"].isin(filtro_status)
        & df["Pilar"].isin(filtro_pilar)
    ].copy()

    st.dataframe(
        df_filtrado,
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

    if not df_filtrado.empty:
        df_gantt = df_filtrado.copy()
        df_gantt["Início"] = pd.to_datetime(df_gantt["Início"])
        df_gantt["Fim"] = pd.to_datetime(df_gantt["Fim"])

        gantt = px.timeline(
            df_gantt,
            x_start="Início",
            x_end="Fim",
            y="Iniciativa",
            color="Status",
            hover_data=[
                "Pilar",
                "Prioridade",
                "Responsável",
                "Progresso",
            ],
            color_discrete_map={
                "Planejado": "#64748b",
                "Em andamento": "#047f9e",
                "Bloqueado": "#b91c1c",
                "Concluído": "#15803d",
                "Cancelado": "#374151",
            },
            title="Cronograma estratégico",
        )

        gantt.update_yaxes(autorange="reversed")
        gantt.update_layout(height=max(400, len(df_gantt) * 55))

        st.plotly_chart(gantt, use_container_width=True)

    st.subheader("Atualizar iniciativa")

    item_id = st.selectbox(
        "Selecione a iniciativa",
        options=[item["ID"] for item in dados["roadmap"]],
        format_func=lambda valor: next(
            (
                f"#{item['ID']} — {item['Iniciativa']}"
                for item in dados["roadmap"]
                if item["ID"] == valor
            ),
            str(valor),
        ),
    )

    item = next(
        item
        for item in dados["roadmap"]
        if item["ID"] == item_id
    )

    col_u1, col_u2 = st.columns(2)

    novo_status = col_u1.selectbox(
        "Novo status",
        [
            "Planejado",
            "Em andamento",
            "Bloqueado",
            "Concluído",
            "Cancelado",
        ],
        index=[
            "Planejado",
            "Em andamento",
            "Bloqueado",
            "Concluído",
            "Cancelado",
        ].index(item["Status"]),
        key=f"roadmap_status_{organizacao['id']}_{item_id}",
    )

    novo_progresso = col_u2.slider(
        "Novo progresso",
        0,
        100,
        int(item.get("Progresso", 0)),
        5,
        key=f"roadmap_progresso_{organizacao['id']}_{item_id}",
    )

    col_b1, col_b2 = st.columns(2)

    if col_b1.button(
        "Salvar atualização",
        type="primary",
        use_container_width=True,
    ):
        item["Status"] = novo_status
        item["Progresso"] = (
            100 if novo_status == "Concluído" else novo_progresso
        )
        st.success("Roadmap atualizado.")
        st.rerun()

    if col_b2.button(
        "Excluir iniciativa",
        use_container_width=True,
    ):
        dados["roadmap"] = remover_registro(
            dados["roadmap"],
            item_id,
        )
        st.rerun()

    st.download_button(
        "Baixar roadmap em CSV",
        data=df.to_csv(index=False, sep=";").encode("utf-8-sig"),
        file_name=f"roadmap-{organizacao['id']}.csv",
        mime="text/csv",
    )


# ============================================================
# GAP ANALYSIS
# ============================================================

def modulo_gap_analysis():
    organizacao = obter_organizacao_ativa()
    dados = obter_dados_ativos()

    if organizacao is None or dados is None:
        st.error("Nenhuma organização ativa foi encontrada.")
        return

    cabecalho(
        "Gap Analysis",
        "Compare a situação atual com o nível desejado e priorize melhorias.",
    )

    with st.form(
        f"form_gap_{organizacao['id']}",
        clear_on_submit=True,
    ):
        col1, col2 = st.columns(2)

        framework = col1.selectbox(
            "Framework ou referência",
            [
                "LGPD",
                "NIST CSF 2.0",
                "ISO 27001",
                "Política Interna",
                "Boas Práticas",
            ],
        )
        controle = col2.text_input(
            "Controle, requisito ou processo",
        )

        col3, col4 = st.columns(2)

        estado_atual = col3.slider(
            "Maturidade atual",
            min_value=0,
            max_value=5,
            value=1,
            help="0 = inexistente; 5 = otimizado.",
        )
        estado_desejado = col4.slider(
            "Maturidade desejada",
            min_value=0,
            max_value=5,
            value=3,
        )

        recomendacao = st.text_area(
            "Recomendação para eliminar ou reduzir o gap"
        )

        col5, col6, col7 = st.columns(3)

        responsavel = col5.text_input("Responsável")
        prazo = col6.date_input(
            "Prazo",
            value=date.today() + timedelta(days=60),
            format="DD/MM/YYYY",
        )
        status = col7.selectbox(
            "Status",
            [
                "Aberto",
                "Em tratamento",
                "Aceito",
                "Concluído",
            ],
        )

        criar_roadmap = st.checkbox(
            "Criar automaticamente uma iniciativa no Roadmap"
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
                criticidade = classificar_gap(valor_gap)

                registro = {
                    "ID": proximo_id(dados["gaps"]),
                    "Framework": framework,
                    "Controle": controle.strip(),
                    "Estado Atual": estado_atual,
                    "Estado Desejado": estado_desejado,
                    "Gap": valor_gap,
                    "Criticidade": criticidade,
                    "Recomendação": recomendacao.strip(),
                    "Responsável": responsavel.strip(),
                    "Prazo": prazo.isoformat(),
                    "Status": status,
                }

                dados["gaps"].append(registro)

                if criar_roadmap and recomendacao.strip():
                    adicionar_gap_ao_roadmap(dados, registro)

                st.success("Gap registrado com sucesso.")
                st.rerun()

    if not dados["gaps"]:
        st.info("Nenhum gap registrado.")
        return

    df = dataframe_lista(dados["gaps"], COLUNAS_GAPS)

    col_m1, col_m2, col_m3, col_m4 = st.columns(4)

    col_m1.metric("Total de gaps", len(df))
    col_m2.metric(
        "Gaps críticos",
        int((df["Criticidade"] == "Crítica").sum()),
    )
    col_m3.metric(
        "Gaps altos",
        int((df["Criticidade"] == "Alta").sum()),
    )
    col_m4.metric(
        "Gap médio",
        f"{pd.to_numeric(df['Gap']).mean():.1f}",
    )

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
    )

    col_g1, col_g2 = st.columns(2)

    with col_g1:
        criticidade = (
            df["Criticidade"]
            .value_counts()
            .reset_index()
        )
        criticidade.columns = ["Criticidade", "Quantidade"]

        fig = px.pie(
            criticidade,
            names="Criticidade",
            values="Quantidade",
            hole=0.4,
            title="Gaps por criticidade",
            color="Criticidade",
            color_discrete_map={
                "Crítica": "#b91c1c",
                "Alta": "#ea580c",
                "Média": "#eab308",
                "Baixa": "#15803d",
            },
        )

        st.plotly_chart(fig, use_container_width=True)

    with col_g2:
        por_framework = (
            df.groupby("Framework", as_index=False)["Gap"]
            .sum()
            .sort_values("Gap", ascending=False)
        )

        fig = px.bar(
            por_framework,
            x="Framework",
            y="Gap",
            color="Gap",
            title="Gap acumulado por framework",
            color_continuous_scale=["#dceff4", "#047f9e", "#0b3040"],
        )

        fig.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    gap_id = st.selectbox(
        "Gap para exclusão",
        options=[item["ID"] for item in dados["gaps"]],
        format_func=lambda valor: next(
            (
                f"#{item['ID']} — {item['Controle']}"
                for item in dados["gaps"]
                if item["ID"] == valor
            ),
            str(valor),
        ),
    )

    if st.button("Excluir gap"):
        dados["gaps"] = remover_registro(
            dados["gaps"],
            gap_id,
        )
        st.rerun()

    st.download_button(
        "Baixar Gap Analysis em CSV",
        data=df.to_csv(index=False, sep=";").encode("utf-8-sig"),
        file_name=f"gap-analysis-{organizacao['id']}.csv",
        mime="text/csv",
    )


# ============================================================
# ADEQUAÇÃO LGPD / NIST / ISO
# ============================================================

def modulo_adequacao():
    organizacao = obter_organizacao_ativa()
    dados = obter_dados_ativos()

    if organizacao is None or dados is None:
        st.error("Nenhuma organização ativa foi encontrada.")
        return

    cabecalho(
        "Adequação LGPD / NIST / ISO 27001",
        "Gerencie controles, evidências, responsáveis e prazos.",
    )

    framework = st.selectbox(
        "Selecione o framework",
        options=list(CONTROLES_FRAMEWORKS.keys()),
        key=f"framework_adequacao_{organizacao['id']}",
    )

    progresso = calcular_progresso_adequacao(
        dados,
        framework,
    )

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Conformidade",
        f"{progresso:.1f}%",
    )
    col2.metric(
        "Controles",
        len(CONTROLES_FRAMEWORKS[framework]),
    )

    implementados = sum(
        1
        for controle in CONTROLES_FRAMEWORKS[framework]
        if dados["adequacao"].get(
            f"{framework}_{controle['codigo']}",
            {},
        ).get("status") in ["Implementado", "Não aplicável"]
    )

    col3.metric("Concluídos", implementados)

    st.progress(min(max(progresso / 100, 0.0), 1.0))

    if progresso < 40:
        st.error("Nível crítico de adequação.")
    elif progresso < 70:
        st.warning("Existem lacunas relevantes de conformidade.")
    else:
        st.success("Bom nível de adequação ao framework.")

    controles = CONTROLES_FRAMEWORKS[framework]

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

        titulo = (
            f"{controle['codigo']} — {controle['controle']} "
            f"({registro.get('status', 'Não iniciado')})"
        )

        with st.expander(titulo):
            col_a, col_b = st.columns(2)

            status_atual = registro.get(
                "status",
                "Não iniciado",
            )

            if status_atual not in STATUS_ADEQUACAO:
                status_atual = "Não iniciado"

            status = col_a.selectbox(
                "Status",
                STATUS_ADEQUACAO,
                index=STATUS_ADEQUACAO.index(status_atual),
                key=(
                    f"adequacao_status_{organizacao['id']}_"
                    f"{framework}_{controle['codigo']}"
                ),
            )

            responsavel = col_b.text_input(
                "Responsável",
                value=registro.get("responsavel", ""),
                key=(
                    f"adequacao_responsavel_{organizacao['id']}_"
                    f"{framework}_{controle['codigo']}"
                ),
            )

            col_c, col_d = st.columns(2)

            prazo_salvo = registro.get("prazo", "")

            try:
                prazo_inicial = date.fromisoformat(prazo_salvo)
            except (TypeError, ValueError):
                prazo_inicial = date.today() + timedelta(days=90)

            prazo = col_c.date_input(
                "Prazo",
                value=prazo_inicial,
                format="DD/MM/YYYY",
                key=(
                    f"adequacao_prazo_{organizacao['id']}_"
                    f"{framework}_{controle['codigo']}"
                ),
            )

            evidencia = col_d.text_input(
                "Referência da evidência",
                value=registro.get("evidencia", ""),
                placeholder="Ex.: Política PSI v2, ata, relatório...",
                key=(
                    f"adequacao_evidencia_{organizacao['id']}_"
                    f"{framework}_{controle['codigo']}"
                ),
            )

            observacoes = st.text_area(
                "Observações e lacunas",
                value=registro.get("observacoes", ""),
                key=(
                    f"adequacao_obs_{organizacao['id']}_"
                    f"{framework}_{controle['codigo']}"
                ),
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

        linhas.append(
            {
                "Código": controle["codigo"],
                "Controle": controle["controle"],
                "Categoria": controle["categoria"],
                "Status": registro.get(
                    "status",
                    "Não iniciado",
                ),
                "Percentual": PERCENTUAL_STATUS.get(
                    registro.get("status", "Não iniciado"),
                    0,
                ),
                "Responsável": registro.get("responsavel", ""),
                "Prazo": registro.get("prazo", ""),
                "Evidência": registro.get("evidencia", ""),
            }
        )

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

    status_df = (
        df["Status"]
        .value_counts()
        .reset_index()
    )
    status_df.columns = ["Status", "Quantidade"]

    fig = px.bar(
        status_df,
        x="Status",
        y="Quantidade",
        color="Status",
        title=f"Situação dos controles — {framework}",
    )

    st.plotly_chart(fig, use_container_width=True)

    col_b1, col_b2 = st.columns(2)

    col_b1.download_button(
        "Baixar adequação em CSV",
        data=df.to_csv(index=False, sep=";").encode("utf-8-sig"),
        file_name=(
            f"adequacao-{normalizar_id(framework)}-"
            f"{organizacao['id']}.csv"
        ),
        mime="text/csv",
        use_container_width=True,
    )

    if col_b2.button(
        "Limpar avaliação deste framework",
        use_container_width=True,
    ):
        prefixo_dados = f"{framework}_"

        for chave in list(dados["adequacao"].keys()):
            if chave.startswith(prefixo_dados):
                del dados["adequacao"][chave]

        prefixos_widgets = [
            f"adequacao_status_{organizacao['id']}_{framework}_",
            f"adequacao_responsavel_{organizacao['id']}_{framework}_",
            f"adequacao_prazo_{organizacao['id']}_{framework}_",
            f"adequacao_evidencia_{organizacao['id']}_{framework}_",
            f"adequacao_obs_{organizacao['id']}_{framework}_",
        ]

        for chave in list(st.session_state.keys()):
            if any(
                str(chave).startswith(prefixo)
                for prefixo in prefixos_widgets
            ):
                del st.session_state[chave]

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
        "Registre decisões, participantes e próximos passos.",
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
                    f"excluir_reuniao_{organizacao['id']}_"
                    f"{reuniao['ID']}"
                ),
            ):
                dados["reunioes"] = remover_registro(
                    dados["reunioes"],
                    reuniao["ID"],
                )
                st.rerun()


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
        "Exporte os dados consolidados da consultoria.",
    )

    resultados = calcular_assessment(dados)

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Maturidade",
        f"{resultados['Geral']:.2f}/5",
    )
    col2.metric("Riscos", len(dados["riscos"]))
    col3.metric("Gaps", len(dados["gaps"]))
    col4.metric("Roadmap", len(dados["roadmap"]))

    st.subheader("Maturidade por dimensão")

    df_maturidade = pd.DataFrame(
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
        df_maturidade,
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Adequação por framework")

    df_adequacao = pd.DataFrame(
        [
            {
                "Framework": framework,
                "Conformidade": round(
                    calcular_progresso_adequacao(
                        dados,
                        framework,
                    ),
                    1,
                ),
            }
            for framework in CONTROLES_FRAMEWORKS
        ]
    )

    st.dataframe(
        df_adequacao,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Conformidade": st.column_config.ProgressColumn(
                "Conformidade",
                min_value=0,
                max_value=100,
                format="%.1f%%",
            )
        },
    )

    arquivo = gerar_csv_consolidado(
        organizacao,
        dados,
    )

    st.download_button(
        "Baixar relatório consolidado em CSV",
        data=arquivo,
        file_name=(
            f"relatorio-ctr-defense-{organizacao['id']}.csv"
        ),
        mime="text/csv",
        use_container_width=True,
    )

    st.info(
        "Nesta versão, os dados são armazenados na sessão. "
        "Para produção, recomenda-se PostgreSQL ou SQLite."
    )


# ============================================================
# SIDEBAR
# ============================================================

def construir_sidebar():
    st.sidebar.markdown("## 🛡️ CTR DEFENSE")
    st.sidebar.caption("Consultoria Profissional de Cibersegurança")

    organizacoes = st.session_state.organizacoes

    if organizacoes:
        ids = list(organizacoes.keys())
        id_atual = st.session_state.get("organizacao_ativa_id")

        if id_atual not in ids:
            id_atual = ids[0]
            st.session_state.organizacao_ativa_id = id_atual

        selecionada = st.sidebar.selectbox(
            "Organização ativa",
            options=ids,
            index=ids.index(id_atual),
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
                f"Cliente: {organizacao['nome']}"
            )
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
            "Adequação LGPD/NIST/ISO",
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

if menu == "Dashboard Executivo":
    modulo_dashboard()

elif menu == "Organizações":
    modulo_organizacoes()

elif menu == "Assessment NIST CSF":
    modulo_assessment()

elif menu == "Matriz de Riscos":
    modulo_riscos()

elif menu == "Plano de Ação":
    modulo_plano_acao()

elif menu == "Roadmap de Segurança":
    modulo_roadmap()

elif menu == "Gap Analysis":
    modulo_gap_analysis()

elif menu == "Adequação LGPD/NIST/ISO":
    modulo_adequacao()

elif menu == "Reuniões":
    modulo_reunioes()

elif menu == "Relatórios":
    modulo_relatorios()
