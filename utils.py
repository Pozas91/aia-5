import itertools

from collections import Counter


def get_items(d: list) -> set:
    """
    Devuelve todos los elementos de una lista de conjuntos
    :param d: Lista de todas las transiciones producidas
    :return:
    """
    return set().union(*d)


def unit_sets(unit_elements_occurrences: dict, min_support: int) -> set:
    """
    Devuelve conjuntos de elementos unitarios dada una lista de conjuntos
    :param unit_elements_occurrences: Número de veces que aparece cada elemento
    :param min_support: Soporte mínimo que han de cumplir los conjuntos generados
    :return:
    """
    return set([
        frozenset({element})
        for (element, occurrence) in unit_elements_occurrences.items()
        if occurrence >= min_support
    ])


def get_similar_elements(element: set, elements: set) -> set:
    """
    Devuelve los conjuntos que difieran sólo en el elemento final del conjunto dado
    :param element: Conjunto de elementos
    :param elements: Lista de todas las transiciones producidas
    :return:
    """
    copy_l = element.copy()
    copy_l.pop()

    return set([frozenset(x).union(element) for x in elements if copy_l.issubset(x) and x is not element])


def get_support_of_rule(rule: (set, set), d: list) -> int:
    """
    Devuelve el soporte de la regla dada
    :param rule:
    :param d:
    :return:
    """
    x, y = rule
    return get_support(x.union(y), d)


def get_confidence_of_rule(rule: (set, set), d: list) -> float:
    """
    Devuelve la confianza de la regla dada
    :param rule:
    :param d:
    :return:
    """
    x, y = rule
    return get_support(x.union(y), d) / get_support(x, d)


def get_support(s: set, d: list) -> int:
    """
    Devuelve el soporte del conjunto dado
    :param s:
    :param d:
    :return:
    """
    return sum([True for x in d if s.issubset(x)])


def get_subsets(elements: set) -> set:
    """
    Obtiene subconjuntos de un elemento menos del conjunto dado
    :param elements:
    :return:
    """
    subsets = set()

    for element in elements:
        copy_elements = elements.copy()
        copy_elements.remove(element)
        subsets.add(frozenset(copy_elements))

    return subsets


def generates_candidates(s: set) -> set:

    candidates = set()
    dirty_candidates = set()

    # Cogemos todos los conjuntos que unidos dos a dos difieren sólo en el mayor de sus elementos.
    for x in s:
        dirty_candidates = dirty_candidates.union(get_similar_elements(set(x), s))

    # Comprobamos que todos los conjuntos de un elemento menos de los candidatos generados sigan perteneciendo al
    # conjunto general
    for dirty_candidate in dirty_candidates:

        subsets = get_subsets(set(dirty_candidate))
        correct = True

        for subset in subsets:

            # Si alguno ya no pertenece evitamos seguir buscando
            if subset not in s:
                correct = False
                break

        if correct:
            candidates.add(dirty_candidate)

    return candidates


def filter_candidates(candidates: set, d: list, min_support: int) -> set:
    """
    Filtra los candidatos, quedándonos sólo con los que tengan un soporte mínimo
    :param candidates:
    :param d:
    :param min_support:
    :return:
    """

    return set([candidate for candidate in candidates if get_support(candidate, d) >= min_support])


def apriori(d: list, min_support: int, unit_elements_occurrences: dict) -> set:

    # Sacamos los conjuntos unitarios que cumplan con el soporte mínimo
    current_list = unit_sets(unit_elements_occurrences, min_support)
    all_candidates = set()

    # Mientras sigamos pudiendo unir los conjuntos y no sean vacíos, seguimos buscando
    while len(current_list) > 0:

        candidates = generates_candidates(current_list)
        current_list = filter_candidates(candidates, d, min_support)

        # En las transparencias del algoritmo se pide devolver la unión de todos los candidatos generados hasta
        # ahora, si esto no fuese necesario, bastaria con cambiar la siguiente línea, por:
        # all_candidates = current_list
        all_candidates = all_candidates.union(current_list)

    return all_candidates


def load_shopping_cart(path: str) -> (list, list):
    """
    Cargamos todas las compras realizadas en el fichero indicado
    :param path:
    :return:
    """
    shopping_cart = list()
    all_elements = list()

    with open(path) as file:
        for line in file:

            # Get the transaction removing newlines characters and whitespaces
            elements = [int(element) for element in line.replace('\n', '').strip().split()]
            all_elements += elements
            transaction = set(elements)
            shopping_cart.append(transaction)

    return shopping_cart, Counter(all_elements)


def generate_rules(s: set, d: list, from_size=1, min_support=1, min_confidence=0.5) -> list:

    """
    Generamos una lista de reglas para el conjunto dado y las características impuestas. En nuestro caso, al querer
    reglas que sólo tengan un elemento unitario de consecuente, nos interesará indicar un "from_size" del tamaño del
    conjunto dado menos una unidad.
    from_size=(len(s) - 1)
    :param s:
    :param d:
    :param from_size:
    :param min_support:
    :param min_confidence:
    :return:
    """
    rules = list()

    size = from_size

    while size < len(s):

        # Buscamos todos los subconjuntos de tamaño size del conjunto dado
        subsets = find_subsets(s, size)

        for subset in subsets:

            # Creamos una regla por cada uno
            rule = (set(subset), s.difference(subset))

            # Sacamos el soporte y la confianza de la regla.
            support = get_support_of_rule(rule, d)
            confidence = get_confidence_of_rule(rule, d)

            # Comprobamos que cumplan con las características impuestas.
            if support >= min_support and confidence >= min_confidence:
                rules.append((rule, support, confidence))

            size += 1

    return rules


def find_subsets(s: set, size: int) -> set:
    """
    Genera subconjuntos de tamaño size del conjunto dado
    :param s:
    :param size:
    :return:
    """
    return set([frozenset(combination) for combination in itertools.combinations(s, size)])


def filter_lift_rules(rules: list, d: list, min_lift: float) -> list:

    """
    Filtra las reglas que recomienden productos demasiados solicitados
    :param rules:
    :param d:
    :param min_lift:
    :return:
    """

    filtered_rules = list()

    for rule, support, confidence in rules:
        x, y = rule

        total_x = get_support(x, d)
        total_y = get_support(y, d)

        lift = (total_y / total_x) / total_y

        if lift >= min_lift:
            filtered_rules.append(rule)

    return filtered_rules
