import json

evidence = {
  'schema': 'evidence-cards/v1',
  'subject': 'Mathematics',
  'node_ref': 'MAT-09-POLYNOMIALS',
  'cards': [
    {
      'card_id': 'EV-MAT-09-POLY-01',
      'kind': 'DEFINITION',
      'claim': 'A polynomial is an algebraic expression where exponents of variables are non-negative integers.',
      'quote': 'Polynomials are expressions with non-negative integer powers.',
      'acquisition_ref': 'ACQ-0B3450C353FF29985152',
      'locator': {'page': 33},
      'harvested_by': 'reall',
      'harvested_at': '2026-09-28'
    },
    {
      'card_id': 'EV-MAT-09-POLY-02',
      'kind': 'QUESTION',
      'claim': 'Source question: Find the value of polynomial 5x - 4x^2 + 3 at x=0.',
      'quote': 'Find the value of polynomial 5x - 4x^2 + 3 at x=0.',
      'acquisition_ref': 'ACQ-1DD05CE5AA04B532EC68',
      'locator': {'page': 2},
      'harvested_by': 'reall',
      'harvested_at': '2026-09-28'
    },
    {
      'card_id': 'EV-MAT-09-POLY-03',
      'kind': 'ANSWER_KEY',
      'claim': 'Answer to polynomial evaluation at x=0 is 3.',
      'quote': '3',
      'acquisition_ref': 'ACQ-1DD05CE5AA04B532EC68',
      'locator': {'page': 10},
      'harvested_by': 'reall',
      'harvested_at': '2026-09-28'
    }
  ]
}
with open('Mathematics/research/evidence/MAT-09-POLYNOMIALS.cards.json', 'w') as f: json.dump(evidence, f, indent=2)

verification = {
  'schema': 'verification-cards/v1',
  'subject': 'Mathematics',
  'node_ref': 'MAT-09-POLYNOMIALS',
  'cards': [
    {
      'question_card_id': 'EV-MAT-09-POLY-02',
      'key_card_id': 'EV-MAT-09-POLY-03',
      'verifier': 'agent',
      'verified_at': '2026-09-28',
      'steps': ['Substitute x=0 into 5x - 4x^2 + 3', '5(0) - 4(0)^2 + 3 = 3', 'Matches key.'],
      'verdict': 'CONFIRMED_VALID'
    }
  ]
}
with open('Mathematics/research/verification/MAT-09-POLYNOMIALS.verification.json', 'w') as f: json.dump(verification, f, indent=2)

gates = {
  'schema_version': '1.0',
  'subject': 'Mathematics',
  'topic_id': 'MAT-09-POLYNOMIALS',
  'gates': [
    {
      'gate_id': 'MATH-GATE-POLY-DEF',
      'title': 'Definition of Polynomials',
      'required_evidence': ['EV-MAT-09-POLY-01'],
      'governing_relation': {
        'expression': '<math xmlns="http://www.w3.org/1998/Math/MathML"><mi>P</mi><mo>(</mo><mi>x</mi><mo>)</mo></math>',
        'conditions': ['Exponents must be non-negative integers.']
      }
    }
  ]
}
with open('Mathematics/gates/polynomials.v1.json', 'w') as f: json.dump(gates, f, indent=2)

rungs = {
  'schema_version': '1.0',
  'topic_id': 'MAT-09-POLYNOMIALS',
  'rungs': [
    {
      'rung_id': 'RUNG-POLY-1',
      'title': 'Understand definition and degree',
      'gates_unlocked': ['MATH-GATE-POLY-DEF']
    }
  ]
}
with open('Mathematics/matrices/polynomials.rungs.json', 'w') as f: json.dump(rungs, f, indent=2)
