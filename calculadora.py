
import ast
import math
import operator
import tkinter as tk
from tkinter import messagebox


#Configuracao da janela

janela = tk.Tk()
janela.title("Calculadora")
janela.geometry("360x640")
janela.minsize(320, 560)
janela.configure(bg="#151515")

expressao = tk.StringVar(value="0")
historico = tk.StringVar(value="")

calculado = False

COR_FUNDO = "#151515"
COR_VISOR = "#202020"
COR_NUMERO = "#303030"
COR_FUNCAO = "#505050"
COR_OPERADOR = "#ff9f0a"
COR_TEXTO = "#ffffff"


#Avaliacao segura das expressoes

OPERADORES = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
}


def avaliar(no):
    """Avalia apenas operações e funções matemáticas permitidas."""

    if isinstance(no, ast.Expression):
        return avaliar(no.body)

    if isinstance(no, ast.Constant):
        if type(no.value) in (int, float):
            return no.value
        raise ValueError("Valor inválido")

    if isinstance(no, ast.BinOp):
        tipo = type(no.op)

        if tipo not in OPERADORES:
            raise ValueError("Operação não permitida")

        a = avaliar(no.left)
        b = avaliar(no.right)

        if tipo is ast.Pow and abs(b) > 1000:
            raise ValueError("Expoente muito grande")

        resultado = OPERADORES[tipo](a, b)

        if isinstance(resultado, complex):
            raise ValueError("Resultado complexo")

        if not math.isfinite(resultado):
            raise ValueError("Resultado fora do limite")

        return resultado

    if isinstance(no, ast.UnaryOp):
        valor = avaliar(no.operand)

        if isinstance(no.op, ast.UAdd):
            return valor
        if isinstance(no.op, ast.USub):
            return -valor

        raise ValueError("Operação inválida")

    if isinstance(no, ast.Call):
        if not isinstance(no.func, ast.Name):
            raise ValueError("Função inválida")

        funcoes = {
            "sqrt": math.sqrt,
            "factorial": math.factorial,
        }

        nome = no.func.id

        if nome not in funcoes or no.keywords:
            raise ValueError("Função não permitida")

        argumentos = [avaliar(a) for a in no.args]

        if nome == "factorial":
            if len(argumentos) != 1:
                raise ValueError("Argumento inválido")

            n = argumentos[0]

            if not isinstance(n, int) or n < 0 or n > 170:
                raise ValueError("Fatorial requer inteiro entre 0 e 170")

        resultado = funcoes[nome](*argumentos)

        if not math.isfinite(resultado):
            raise ValueError("Resultado fora do limite")

        return resultado

    raise ValueError("Expressão inválida")


def calcular(texto):
    # Converte a notação visual para sintaxe Python.
    texto = (
        texto.replace("×", "*")
        .replace("÷", "/")
        .replace("−", "-")
        .replace("^", "**")
    )

    arvore = ast.parse(texto, mode="eval")
    return avaliar(arvore)


def formatar(valor):
    if isinstance(valor, float):
        if valor.is_integer():
            return str(int(valor))
        return f"{valor:.12g}"

    return str(valor)


#Funcoes da calculadora

def adicionar(valor):
    global calculado

    atual = expressao.get()

    if calculado:
        if valor in "+−×÷^":
            calculado = False
        else:
            atual = "0"
            calculado = False

    if atual == "0":
        if valor.isdigit():
            atual = valor
        elif valor == ".":
            atual = "0."
        elif valor == "−":
            atual = "−"
        else:
            atual += valor
    else:
        atual += valor

    expressao.set(atual)
    historico.set("")


def limpar():
    global calculado
    expressao.set("0")
    historico.set("")
    calculado = False


def apagar():
    global calculado

    atual = expressao.get()

    if calculado:
        limpar()
        return

    atual = atual[:-1]

    if not atual or atual == "−":
        atual = "0"

    expressao.set(atual)


def resultado():
    global calculado

    texto = expressao.get()

    try:
        valor = calcular(texto)
        historico.set(texto + " =")
        expressao.set(formatar(valor))
        calculado = True

    except ZeroDivisionError:
        messagebox.showerror("Erro", "Não é possível dividir por zero.")
    except (ValueError, SyntaxError, TypeError, OverflowError):
        messagebox.showerror(
            "Erro", "Expressão inválida ou operação matemática impossível."
        )


def porcentagem():
    global calculado

    try:
        valor = calcular(expressao.get())
        expressao.set(formatar(valor / 100))
        calculado = False
        historico.set("")
    except (ValueError, SyntaxError, ZeroDivisionError,
            TypeError, OverflowError):
        messagebox.showerror("Erro", "Não foi possível calcular a porcentagem.")


def transformar(funcao):
    global calculado

    try:
        valor = calcular(expressao.get())

        if funcao == "sqrt":
            novo = math.sqrt(valor)
        elif funcao == "quadrado":
            novo = valor ** 2
        elif funcao == "inverso":
            novo = 1 / valor
        elif funcao == "fatorial":
            if not isinstance(valor, int) or valor < 0 or valor > 170:
                raise ValueError
            novo = math.factorial(valor)
        else:
            return

        if isinstance(novo, complex) or not math.isfinite(novo):
            raise ValueError

        historico.set(f"{funcao}({expressao.get()}) =")
        expressao.set(formatar(novo))
        calculado = True

    except ZeroDivisionError:
        messagebox.showerror("Erro", "Não é possível dividir por zero.")
    except (ValueError, TypeError, OverflowError):
        messagebox.showerror("Erro", "Não foi possível realizar essa operação.")


def trocar_sinal():
    global calculado

    try:
        valor = calcular(expressao.get())
        expressao.set(formatar(-valor))
        calculado = False
        historico.set("")
    except (ValueError, SyntaxError, ZeroDivisionError,
            TypeError, OverflowError):
        messagebox.showerror("Erro", "Expressão inválida.")


#Visor 

visor = tk.Frame(janela, bg=COR_VISOR)
visor.pack(fill="both", padx=12, pady=(12, 8), expand=True)

tk.Label(
    visor,
    textvariable=historico,
    bg=COR_VISOR,
    fg="#aaaaaa",
    font=("Arial", 12),
    anchor="e",
).pack(fill="x", padx=14, pady=(18, 4))

tk.Label(
    visor,
    textvariable=expressao,
    bg=COR_VISOR,
    fg=COR_TEXTO,
    font=("Arial", 30),
    anchor="e",
    justify="right",
    wraplength=320,
).pack(fill="both", expand=True, padx=14, pady=(4, 16))


#Botoes 

area_botoes = tk.Frame(janela, bg=COR_FUNDO)
area_botoes.pack(fill="both", expand=True, padx=10, pady=(0, 10))

botoes = [
    [("AC", "limpar", COR_FUNCAO),
     ("⌫", "apagar", COR_FUNCAO),
     ("%", "porcentagem", COR_FUNCAO),
     ("÷", "÷", COR_OPERADOR)],

    [("√", "sqrt", COR_FUNCAO),
     ("x²", "quadrado", COR_FUNCAO),
     ("xʸ", "^", COR_FUNCAO),
     ("×", "×", COR_OPERADOR)],

    [("7", "7", COR_NUMERO),
     ("8", "8", COR_NUMERO),
     ("9", "9", COR_NUMERO),
     ("−", "−", COR_OPERADOR)],

    [("4", "4", COR_NUMERO),
     ("5", "5", COR_NUMERO),
     ("6", "6", COR_NUMERO),
     ("+", "+", COR_OPERADOR)],

    [("1", "1", COR_NUMERO),
     ("2", "2", COR_NUMERO),
     ("3", "3", COR_NUMERO),
     ("=", "resultado", COR_OPERADOR)],

    [("+/−", "sinal", COR_FUNCAO),
     ("0", "0", COR_NUMERO),
     (".", ".", COR_NUMERO),
     ("1/x", "inverso", COR_FUNCAO)],

    [("(", "(", COR_FUNCAO),
     (")", ")", COR_FUNCAO),
     ("n!", "fatorial", COR_FUNCAO),
     ("%", "porcentagem", COR_FUNCAO)],
]


def executar(acao):
    if acao == "limpar":
        limpar()
    elif acao == "apagar":
        apagar()
    elif acao == "resultado":
        resultado()
    elif acao == "porcentagem":
        porcentagem()
    elif acao == "sinal":
        trocar_sinal()
    elif acao in ("sqrt", "quadrado", "inverso", "fatorial"):
        transformar(acao)
    else:
        adicionar(acao)


for linha, itens in enumerate(botoes):
    area_botoes.rowconfigure(linha, weight=1)

    for coluna, (rotulo, acao, cor) in enumerate(itens):
        area_botoes.columnconfigure(coluna, weight=1)

        botao = tk.Button(
            area_botoes,
            text=rotulo,
            command=lambda a=acao: executar(a),
            bg=cor,
            fg=COR_TEXTO,
            activebackground="#777777",
            activeforeground=COR_TEXTO,
            font=("Arial", 16, "bold"),
            relief="flat",
            bd=0,
            cursor="hand2",
        )

        botao.grid(
            row=linha,
            column=coluna,
            sticky="nsew",
            padx=3,
            pady=3,
        )


#Atalhos do teclado 

def teclado(evento):
    tecla = evento.keysym
    caractere = evento.char

    if tecla in ("Return", "KP_Enter"):
        resultado()
    elif tecla == "BackSpace":
        apagar()
    elif tecla == "Escape":
        limpar()
    elif caractere in "0123456789.()+-*/^":
        conversao = {
            "*": "×",
            "/": "÷",
            "-": "−",
        }
        adicionar(conversao.get(caractere, caractere))
    elif caractere == "%":
        porcentagem()


janela.bind("<Key>", teclado)

janela.mainloop()
