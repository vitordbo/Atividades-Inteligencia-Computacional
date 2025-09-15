% Modelo simples do Mundo Wumpus 4x4

% --- limites do mundo (1..4)
dentro_limite(X,Y) :-
    X >= 1, X =< 4, Y >= 1, Y =< 4.

% --- fatos (configuração estática do mundo)
% exemplo: Wumpus na (2,3), poços em (3,1) e (1,3), ouro em (4,4)
wumpus(2,3).
poco(3,1).
poco(1,3).
ouro(4,4).

% --- adjacência (4-vizinhos ortogonais)
adjacente(X,Y,X1,Y) :- X1 is X+1, dentro_limite(X1,Y).
adjacente(X,Y,X1,Y) :- X1 is X-1, dentro_limite(X1,Y).
adjacente(X,Y,X,Y1) :- Y1 is Y+1, dentro_limite(X,Y1).
adjacente(X,Y,X,Y1) :- Y1 is Y-1, dentro_limite(X,Y1).

% --- percepções derivadas
% há fedor em uma célula se o Wumpus está em alguma adjacente
fedor(X,Y) :-
    adjacente(X,Y,WX,WY),
    wumpus(WX,WY).

% há brisa se há algum poço adjacente
brisa(X,Y) :-
    adjacente(X,Y,PX,PY),
    poco(PX,PY).

% há brilho se ouro na mesma célula
brilho(X,Y) :-
    ouro(X,Y).

% --- segurança simples: seguro se não tem poço nem wumpus na célula
seguro(X,Y) :-
    \+ poco(X,Y),
    \+ wumpus(X,Y),
    dentro_limite(X,Y).

% --- gerar percepção completa para posição
percepcao(X,Y,Percepcoes) :-
    findall(P, ( (fedor(X,Y), P = fedor) ;
                 (brisa(X,Y), P = brisa) ;
                 (brilho(X,Y), P = brilho) ), L),
    list_to_set(L, Percepcoes).  % remove duplicatas

% Exemplo de consulta para listar todas as posições seguras:
% ?- findall((X,Y), seguro(X,Y), Lista).
