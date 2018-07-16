#!/usr/bin/env python3
from collections import defaultdict
import json
import csv
from random import SystemRandom


random = SystemRandom()


COUNTRIES_POPULATION = {
    'NG': 190632261,
    'CR': 4947490,
    'IR': 81000000,
    'KR': 51446201,
    'PE': 32280640,
    'SN': 15084690,
    'EG': 99375741,
    'TN': 11304482,
    'MX': 124574795,
    'PA': 3753142,
    'MA': 35740000,
    'CO': 49755971,
    'UY': 3360148,
    'CH': 8401120,
    'JP': 126714000,
    'AR': 43431886,
    'AU': 24989700,
    'BR': 209129000,
    'GB-EN': 55619400,
    'RU': 144526636,
    'ES': 48958159,
    'PL': 38433600,
    'RS': 7111973,
    'SA': 33000000,
    'HR': 4154200,
    'PT': 10291027,
    'DE': 82800000,
    'IS': 350710,
    'SE': 10151588,
    'BE': 11358357,
    'FR': 67186638,
    'DK': 5785864,
}


def s_random(team_a, team_b, **kwargs):
    """Random"""
    return random.choice([None, team_a, team_b])


def s_random_win(team_a, team_b, **kwargs):
    """Random (win only)"""
    return random.choice([team_a, team_b])


def s_null(**kwargs):
    """Null"""
    return None


def s_quote_best(team_a, team_b, quote_a, quote_b, quote_null, **kwargs):
    """Best quote"""
    return min([
        (quote_a, team_a),
        (quote_b, team_b),
        (quote_null, None),
    ], key=lambda x: x[0])[1]


def s_quote_worst(team_a, team_b, quote_a, quote_b, quote_null, **kwargs):
    """Worst quote"""
    return max([
        (quote_a, team_a),
        (quote_b, team_b),
        (quote_null, None),
    ], key=lambda x: x[0])[1]


def s_alphabetical(team_a, team_b, **kwargs):
    """ISO code alphabetical"""
    return min([team_a, team_b])


def s_alphabetical_reversed(team_a, team_b, **kwargs):
    """ISO code reversed alphabetical"""
    return max([team_a, team_b])


def s_forecast(team_a, team_b, forecast_a, forecast_b, **kwargs):
    if forecast_a == forecast_b:
        return None
    elif forecast_a > forecast_b:
        return team_a
    else:
        return team_b


def s_population_greatest(team_a, team_b, **kwargs):
    if COUNTRIES_POPULATION[team_a] > COUNTRIES_POPULATION[team_b]:
        return team_a
    else:
        return team_b


def s_population_smallest(team_a, team_b, **kwargs):
    if COUNTRIES_POPULATION[team_a] > COUNTRIES_POPULATION[team_b]:
        return team_b
    else:
        return team_a


def s_mostly_odds(odds, rnd, **kwargs):
    func = random.choice([s_quote_best] * odds + [s_random] * rnd)
    return func(**kwargs)


def s_mostly_odds_9_1(**kwargs):
    return s_mostly_odds(9, 1, **kwargs)


def s_mostly_odds_8_2(**kwargs):
    return s_mostly_odds(8, 2, **kwargs)


def s_mostly_odds_7_3(**kwargs):
    return s_mostly_odds(7, 3, **kwargs)


STRATEGIES = [
    (100, s_random),
    (100, s_random_win),
    (1, s_null),
    (1, s_quote_best),
    (1, s_quote_worst),
    (1, s_alphabetical),
    (1, s_alphabetical_reversed),
    (1, s_forecast),
    (1, s_population_greatest),
    (1, s_population_smallest),
    (100, s_mostly_odds_9_1),
    (100, s_mostly_odds_8_2),
    (100, s_mostly_odds_7_3),
]


def flatten(file_path, flat_path, scores_path):
    with open(file_path, encoding='utf-8') as f:
        data = json.load(f)

    results = data['results']
    scores = defaultdict(lambda: [])
    types = {
        'win': 0,
        'null': 0,
    }
    out = []

    print('{} matches overall'.format(len(results)))

    with open(flat_path, 'w', encoding='utf-8') as f:
        fields = [
            'team_a',
            'team_b',
            'quote_a',
            'quote_null',
            'quote_b',
            'forecast_a',
            'forecast_b',
            'goals_a',
            'goals_b',
        ]

        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()

        for match in data['forecast']['values']:
            r = results[match['id']]

            try:
                line = {
                    'team_a': r['home'],
                    'team_b': r['away'],
                    'quote_a': float(r['quotation']['home']),
                    'quote_null': float(r['quotation']['N']),
                    'quote_b': float(r['quotation']['away']),
                    'forecast_a': int(match['home']),
                    'forecast_b': int(match['away']),
                    'goals_a': int(r['score']['home']),
                    'goals_b': int(r['score']['away']),
                }

                writer.writerow(line)
                out.append(line)

                total = line['goals_a'] + line['goals_b']

                if total:
                    scores[line['team_a']].append(line['goals_a'] / total)
                    scores[line['team_b']].append(line['goals_b'] / total)

                if line['goals_a'] == line['goals_b']:
                    types['null'] += 1
                else:
                    types['win'] += 1
            except TypeError:
                pass

    print('{win} wins + {null} nulls'.format(**types))

    with open(scores_path, 'w', encoding='utf-8') as f:
        fields = ['team', 'score']
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()

        for team, s in scores.items():
            writer.writerow({
                'team': team,
                'score': 100 * float(sum(s)) / float(len(s)),
            })

    return out


def simulate(flat):
    for trials, strategy in STRATEGIES:
        print('---[ {} ]---'.format(strategy.__name__))
        results = []

        for _ in range(0, trials):
            results.append(simulate_one(flat, strategy))

        if len(results) == 1:
            print('guessed {1} | {0} points'.format(*results[0]))
        else:
            avg_g = float(sum(g for _, g in results)) / len(results)
            max_g = max(g for _, g in results)
            avg_p = float(sum(p for p, _ in results)) / len(results)
            max_p = max(p for p, _ in results)

            print('avg: guessed {1} | {0} points'.format(avg_g, avg_p))
            print('max: guessed {1} | {0} points'.format(max_g, max_p))

        print()


def simulate_one(flat, method):
    points = 0
    guessed = 0

    for match in flat:
        if match['goals_a'] == match['goals_b']:
            outcome = None
            quote = match['quote_null']
        elif match['goals_a'] > match['goals_b']:
            outcome = match['team_a']
            quote = match['quote_a']
        else:
            outcome = match['team_b']
            quote = match['quote_b']

        predicted = method(**match)

        if predicted == outcome:
            points += quote
            guessed += 1

    return points, guessed


def main():
    flat = flatten('results.json', 'flat.csv', 'scores.csv')

    print()
    print('-------')
    print()

    simulate(flat)


if __name__ == '__main__':
    main()
