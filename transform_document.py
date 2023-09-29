import openai
import json
from docx import Document

openai.api_key = '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'


def get_completion(prompt, model="gpt-3.5-turbo"):
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0, # this is the degree of randomness of the model's output
    )
    return response.choices[0].message["content"]


def formata_lista_simples(lista):
    if not lista:
        return ''
    string_formatada = '\n'.join([f'    ●    {item}' for item in lista])
    return string_formatada


def formata_formacao_academica(formacoes):
    if not formacoes:
        return ''
    formacoes_formatadas = [
        f"{formacao.get('nome_formacao')} - {formacao.get('nome_instituicao')} - {formacao.get('ano_finalizacao')}"
        for formacao in formacoes
    ]
    return formata_lista_simples(formacoes_formatadas)


def formata_cursos(cursos):
    if not cursos:
        return ''
    cursos_formatados = [
        f"{curso.get('nome_curso')} - {curso.get('nome_instituicao')} - {curso.get('ano_finalizacao')}"
        for curso in cursos
    ]
    return formata_lista_simples(cursos_formatados)


def formata_experiencias(experiencias):
    if not experiencias:
        return ''
    experiencias_formatada = []
    for experiencia in experiencias:
        titulo_experiencia = f"{experiencia.get('nome_da_empresa').upper()} ● {experiencia.get('periodo')}"
        cargos_formatados = []
        for cargo in experiencia.get('cargos'):
            titulo_cargo = f"{cargo.get('nome_cargo')} ● {cargo.get('periodo')}"
            encargos = formata_lista_simples(cargo.get('encargos'))
            cargo_formatado = f'{titulo_cargo}\n\n{encargos}'
            cargos_formatados.append(cargo_formatado)
        cargos_formatados_str = '\n\n'.join(cargos_formatados)
        experiencia_formatada = f'{titulo_experiencia}\n{cargos_formatados_str}'
        experiencias_formatada.append(experiencia_formatada)
    experiencias_formatada_str = '\n\n'.join(experiencias_formatada)
    return experiencias_formatada_str


def transform_document(contexto):
    text = f"""
    Você irá receber entre crases duplas o contéudo de um currículo profissional, e terá que encontrar alguns parâmetros do candidato e retornar no formato json abaixo, entre * está o formato, e entre # está a descrição:

    - nome *string* #nome do candidato#
    - cidade *string* #cidade em que mora o candidato#
    - estado *string* #uf da cidade em que mora o candidato#
    - linkedin *string* #link do Linkedin do candidato#
    - formacao_academica *lista de json no formato abaixo, do mais recente para o mais antigo*
    -- nome_formacao *string*
    -- nome_instituicao *string*
    -- ano_finalizacao *string* #se ainda estiver cursando, preencha com: Em andamento#
    - idioma *lista de strings* #idioma e nível no formato: idioma - nível, em tópicos#
    - resumo *string* #resumo do candidato, em tópicos, com no máximo 10 linhas#
    - experiencia_profissional *lista de json no formato abaixo, do mais recente para o mais antigo*
    -- nome_da_empresa *string*
    -- periodo *string* #formato: mes/ano - mes/ano, se for a atual experiencia: mes/ano - Presente#
    -- cargos *lista de json no formato abaixo, do mais recente para o mais antigo*
    --- nome_cargo *string*
    --- periodo *string* #formato: mes/ano - mes/ano, se for a atual experiencia: mes/ano - Presente#
    --- encargos *lista de string* # responsabilidades e atribuições, com no máximo 2 linhas para cada#
    - habilidades *lista de strings* #habilidades adicionais do candidato#
    - cursos *lista de json no formato abaixo, do mais recente para o mais antigo*
    -- nome_curso *string*
    -- nome_instituicao *string*
    -- ano_finalizacao *string #se ainda estiver cursando, preencha com: Em andamento#

    Observação: Quando não achar algum item que seja string, retorne uma string vazia. Quando não achar algum item que seja uma lista, retorne uma lista vazia.

    ``
    {contexto}
    ``

    """

    if len(text) > 4000:
        text = text[:4000]

    response = get_completion(text)

    response_json = json.loads(response)

    json_input = {
        "NOME_INPUT": response_json.get('nome'),
        "CIDADE_INPUT": response_json.get('cidade'),
        "ESTADO_INPUT": response_json.get('estado'),
        "LINKEDIN_INPUT": response_json.get('linkedin'),
        "FORMACAO_ACADEMICA_INPUT": formata_formacao_academica(response_json.get('formacao_academica')),
        "IDIOMA_INPUT": formata_lista_simples(response_json.get('idioma')),
        "RESUMO_INPUT": response_json.get('resumo'),
        "EXPERIENCIA_PROFISSIONAL_INPUT": formata_experiencias(response_json.get('experiencia_profissional')),
        "HABILIDADES_INPUT": formata_lista_simples(response_json.get('habilidades')),
        "CURSOS_INPUT": formata_cursos(response_json.get('cursos')),
    }

    doc = Document('yoctoo_model.docx')

    for paragraph in doc.paragraphs:
        for key, value in json_input.items():
            if key in paragraph.text and value:
                paragraph.text = paragraph.text.replace(key, value)

    nome_arquivo = f"Yoctoo - {response_json.get('nome')}.docx"

    return nome_arquivo, doc
