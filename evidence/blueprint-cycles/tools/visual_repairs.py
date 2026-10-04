"""Explicit direction diagrams; no measured orbital-density/energy claim."""
def torsion(ids):
    groups=[]
    content=[
      '<text x="25" y="38">Fixed connectivity: H-C(=O)-NH2 in both cases</text><text x="25" y="74">End-on view along C-N; centres project together.</text>',
      '<line x1="180" y1="120" x2="180" y2="325" stroke-dasharray="9 6"/><line x1="470" y1="120" x2="470" y2="325" stroke-dasharray="9 6"/><text x="25" y="370">Dashed: fixed carbonyl p direction.</text>',
      '<line x1="180" y1="130" x2="180" y2="315" stroke-width="7"/><circle cx="180" cy="220" r="7"/><text x="85" y="110">Aligned donor</text>',
      '<line x1="375" y1="220" x2="565" y2="220" stroke-width="7"/><circle cx="470" cy="220" r="7"/><text x="370" y="110">90° donor twist</text><text x="25" y="410">Solid: donor p direction; axis out of page.</text>',
      '<text x="25" y="448">18 valence / 24 total electrons in both cases.</text><text x="25" y="484">Four pi-space electrons in the supplied model.</text><text x="25" y="520">Orientation changes; no measured energy follows.</text>',
    ]
    for sid,text in zip(ids,content):groups.append(f'<g data-g9-stage-id="{sid}">{text}</g>')
    return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 540" role="img" aria-label="Fixed-connectivity formamide direction comparison" font-family="sans-serif" font-size="22"><title>End-on planar and twisted donor directions</title><desc>The carbonyl direction stays fixed; the donor direction actually changes by 90 degrees about the viewed C-N axis. Connectivity and electron counts are invariant. Qualitative direction diagram only.</desc><style>text{stroke:none}</style><g stroke="currentColor" stroke-width="3" fill="currentColor">'+''.join(groups)+'</g></svg>'

def allene(ids):
    content=[
      '<text x="25" y="40">Allene connectivity: H2C=C=CH2</text><text x="25" y="75">Construct directions; do not infer from page layout.</text>',
      '<line x1="70" y1="125" x2="570" y2="125"/><text x="70" y="155">C1</text><text x="295" y="155">C2</text><text x="545" y="155">C3</text><text x="25" y="195">Two central sigma directions share the C=C=C axis.</text>',
      '<line x1="320" y1="250" x2="320" y2="415"/><line x1="235" y1="330" x2="405" y2="330" stroke-dasharray="8 6"/><text x="25" y="235">End-on central p directions are perpendicular.</text>',
      '<line x1="205" y1="330" x2="435" y2="330" stroke-width="6"/><line x1="320" y1="220" x2="320" y2="440" stroke-width="6" stroke-dasharray="8 6"/><text x="25" y="478">Terminal sigma-plane traces: perpendicular.</text>',
      '<text x="25" y="514">Each terminal p aligns with one central p.</text><text x="25" y="550">This model uses terminal sp2 / central sp.</text><text x="25" y="586">No one-atomic-orbital-one-bond Pauli prohibition.</text>',
    ]
    return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 610" role="img" aria-label="Allene direction construction" font-family="sans-serif" font-size="22"><title>Allene local basis and terminal-plane directions</title><desc>Five stages construct the fixed chain, sigma axis, two perpendicular central p directions, terminal sigma-plane traces and a bounded local-model explanation. The end-on diagram looks along C=C=C.</desc><style>text{stroke:none}</style><g stroke="currentColor" stroke-width="3" fill="currentColor">'+''.join(f'<g data-g9-stage-id="{sid}">{text}</g>' for sid,text in zip(ids,content))+'</g></svg>'

def model_scope(ids):
    content=[
      '<text x="25" y="40">Amide: local inventory and physical inference</text><text x="310" y="220">N</text><text x="170" y="310">H</text><text x="470" y="310">H</text><text x="310" y="100">C(=O)H</text>',
      '<line x1="320" y1="200" x2="320" y2="120"/><line x1="305" y1="230" x2="200" y2="290"/><line x1="340" y1="230" x2="450" y2="290"/><text x="25" y="350">Given approximately planar sigma framework.</text>',
      '<text x="25" y="390">Lewis bookkeeping: three bonds + one pair.</text>',
      '<rect x="25" y="410" width="270" height="70" fill="none"/><rect x="325" y="410" width="285" height="70" fill="none"/><text x="40" y="440">Aligned donor model</text><text x="340" y="440">Physical measurements</text><text x="40" y="465">qualitative account</text><text x="340" y="465">needed for strength</text>',
      '<text x="25" y="520">Geometry constrains a model.</text><text x="25" y="555">It does not measure a unique orbital basis.</text>',
    ]
    return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 580" role="img" aria-label="Amide evidence and model-scope map" font-family="sans-serif" font-size="22"><title>Inventory, model and physical evidence</title><desc>Construct the planar nuclear framework and local Lewis inventory, then distinguish a qualitative aligned-donor account from the evidence needed for quantitative claims. This is not the torsion diagram.</desc><style>text{stroke:none}</style><g stroke="currentColor" stroke-width="3" fill="currentColor">'+''.join(f'<g data-g9-stage-id="{sid}">{text}</g>' for sid,text in zip(ids,content))+'</g></svg>'
