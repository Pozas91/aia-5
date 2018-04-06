import os
from time import time

import utils as u


def get_rules(path: str, min_support: int, min_confidence: float, min_lift: float) -> list:
    """
    Programa principal que devuelve las reglas producidas con las características impuestas del fichero incado "path"
    :param path: Ruta del fichero a extraer información
    :param min_support: Soporte mínimo para dar por válida una regla
    :param min_confidence: Confianza mínima para dar por valida una regla
    :param min_lift: Parámetro de ajuste para evitar reglas que devuelvan artículos muy solicitados
    :return: Devuelve una lista de las reglas descubiertas.
    """
    rules = list()

    ####################################################################################################################

    t0 = time()

    print('Cargando el fichero con los datos de las compras...', end=' ')

    d, unit_elements_occurrences = u.load_shopping_cart(path)

    print('terminado en {0:.2f}s\n'.format(time() - t0))

    ####################################################################################################################

    t0 = time()

    print('Ejecutando algoritmo apriori para generar los candidatos a reglas...', end=' ')

    candidates = u.apriori(d, min_support, unit_elements_occurrences)

    print('terminado en {0:.2f}s\n'.format(time() - t0))

    ####################################################################################################################

    t0 = time()

    print('Generando las reglas...', end=' ')

    for candidate in candidates:
        candidate = set(candidate)
        from_size = len(candidate) - 1

        rules += u.generate_rules(
            s=candidate, d=d, from_size=from_size, min_support=min_support, min_confidence=min_confidence
        )

    print('terminado en {0:.2f}s\n'.format(time() - t0))

    ####################################################################################################################

    """Si no es necesario hacer un post-filtro de las reglas generadas evitando aquellas que ya den unos productos 
    que se encuentran en muchas compras, podemos comentar las siguientes líneas. """

    # t0 = time()
    #
    # print('Filtrando las reglas con el parámetro min_lift="{0}"...'.format(min_lift), end=' ')
    #
    # rules = u.filter_lift_rules(rules=rules, d=d, min_lift=min_lift)
    #
    # print('terminado en {0:.2f}s\n'.format(time() - t0))

    ####################################################################################################################

    return rules


if __name__ == '__main__':

    t0 = time()

    print('Iniciando la ejecución del programa principal...', end='\n\n')

    min_support = 10000
    min_confidence = 0.5
    min_lift = 0.5
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets\\retail.dat')

    rules = get_rules(path=path, min_support=min_support, min_confidence=min_confidence, min_lift=min_lift)

    print('Mostrando las reglas generadas...')

    for rule, support, confidence in rules:
        x, y = rule
        print('{0} --> {1}'.format(x, y))
        print('\tSoporte: {0}, Confianza: {1:.1f}%'.format(support, round(confidence * 100, 1)), end='\n\n')

    print('\nLa ejecución total del programa ha sido de {0:.2f}s'.format(time() - t0))
