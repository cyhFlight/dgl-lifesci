# -*- coding: utf-8 -*-
#
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import os
import shutil
import torch

from dgllife.data import *
from dgllife.data.uspto import get_bond_changes, process_file
from dgllife.utils import JTVAEVocab

def remove_file(fname):
    if os.path.isfile(fname):
        try:
            os.remove(fname)
        except OSError:
            pass

def remove_dir(dir_name):
    if os.path.isdir(dir_name):
        try:
            shutil.rmtree(dir_name)
        except OSError:
            pass

def test_alchemy():
    print('Test alchemy')
    dataset = TencentAlchemyDataset(mode='valid',
                                    node_featurizer=None,
                                    edge_featurizer=None)
    dataset = TencentAlchemyDataset(mode='valid',
                                    node_featurizer=None,
                                    edge_featurizer=None,
                                    load=False)

def test_pdbbind():
    print('Test PDBBind')
    dataset = PDBBind(subset='core', remove_hs=True)

def test_pubchem_aromaticity():
    print('Test pubchem aromaticity')
    dataset = PubChemBioAssayAromaticity()
    remove_file('pubchem_aromaticity_dglgraph.bin')

def test_tox21():
    print('Test Tox21')
    dataset = Tox21()
    remove_file('tox21_dglgraph.bin')
    assert len(dataset[0]) == 4
    dataset.load_full = True
    assert len(dataset[0]) == 5
    train_ids = torch.arange(1000)
    assert torch.allclose(dataset.task_pos_weights(train_ids),
                          torch.tensor([26.9706, 35.3750, 5.9756, 21.6364, 6.4404, 21.4500,
                                        26.0000, 5.0826, 21.4390, 14.7692, 6.1442, 12.4308]))

def test_esol():
    print('Test ESOL')
    dataset = ESOL()
    remove_file('esol_dglgraph.bin')
    assert len(dataset[0]) == 3
    dataset.load_full = True
    assert len(dataset[0]) == 11

def test_freesolv():
    print('Test FreeSolv')
    dataset = FreeSolv()
    remove_file('freesolv_dglgraph.bin')
    assert len(dataset[0]) == 3
    dataset.load_full = True
    assert len(dataset[0]) == 5

def test_lipophilicity():
    print('Test Lipophilicity')
    dataset = Lipophilicity()
    remove_file('lipophilicity_dglgraph.bin')
    assert len(dataset[0]) == 3
    dataset.load_full = True
    assert len(dataset[0]) == 4

def test_bace():
    print('Test BACE')
    dataset = BACE()
    remove_file('bace_dglgraph.bin')
    assert len(dataset[0]) == 4
    dataset.load_full = True
    assert len(dataset[0]) == 5

def test_bbbp():
    print('Test BBBP')
    dataset = BBBP()
    remove_file('bbbp_dglgraph.bin')
    assert len(dataset[0]) == 4
    dataset.load_full = True
    assert len(dataset[0]) == 5

def test_toxcast():
    print('Test ToxCast')
    dataset = ToxCast()
    remove_file('toxcast_dglgraph.bin')
    assert len(dataset[0]) == 4

def test_sider():
    print('Test SIDER')
    dataset = SIDER()
    remove_file('sider_dglgraph.bin')
    assert len(dataset[0]) == 4

def test_clintox():
    print('Test ClinTox')
    dataset = ClinTox()
    remove_file('clintox_dglgraph.bin')
    assert len(dataset[0]) == 4

def test_astrazeneca_chembl_solubility():
    print('Test AstraZenecaChEMBLSolubility')
    dataset = AstraZenecaChEMBLSolubility()
    remove_file('AstraZeneca_chembl_solubility_graph.bin')
    assert len(dataset[0]) == 3
    dataset.load_full = True
    assert len(dataset[0]) == 5

def test_wln_reaction():
    print('Test datasets for reaction prediction with WLN')

    reaction1 = '[CH2:15]([CH:16]([CH3:17])[CH3:18])[Mg+:19].[CH2:20]1[O:21][CH2:22][CH2:23]' \
                '[CH2:24]1.[Cl-:14].[OH:1][c:2]1[n:3][cH:4][c:5]([C:6](=[O:7])[N:8]([O:9]' \
                '[CH3:10])[CH3:11])[cH:12][cH:13]1>>[OH:1][c:2]1[n:3][cH:4][c:5]([C:6](=[O:7])' \
                '[CH2:15][CH:16]([CH3:17])[CH3:18])[cH:12][cH:13]1\n'
    reaction2 = '[CH3:14][NH2:15].[N+:1](=[O:2])([O-:3])[c:4]1[cH:5][c:6]([C:7](=[O:8])[OH:9])' \
                '[cH:10][cH:11][c:12]1[Cl:13].[OH2:16]>>[N+:1](=[O:2])([O-:3])[c:4]1[cH:5][c:6]' \
                '([C:7](=[O:8])[OH:9])[cH:10][cH:11][c:12]1[NH:15][CH3:14]\n'
    reactions = [reaction1, reaction2]

    # Test utility functions
    assert get_bond_changes(reaction2) == {('12', '13', 0.0), ('12', '15', 1.0)}
    with open('test.txt', 'w') as f:
        for reac in reactions:
            f.write(reac)
    process_file('test.txt')
    with open('test.txt.proc', 'r') as f:
        lines = f.readlines()
        for i in range(len(lines)):
            l = lines[i].strip()
            react = reactions[i].strip()
            bond_changes = get_bond_changes(react)
            assert l == '{} {}'.format(
                react,
                ';'.join(['{}-{}-{}'.format(x[0], x[1], x[2]) for x in bond_changes]))
    remove_file('test.txt.proc')

    # Test configured dataset
    dataset = WLNCenterDataset('test.txt', './test_graphs.bin')
    remove_file('test_graphs.bin')

    with open('test_candidate_bond_changes.txt', 'w') as f:
        for reac in reactions:
            # simulate fake candidate bond changes
            candidate_string = ''
            for i in range(2):
                candidate_string += '{} {} {:.1f} {:.3f};'.format(i+1, i+2, 0.0, 0.234)
            candidate_string += '\n'
            f.write(candidate_string)

    dataset = WLNRankDataset('test.txt.proc', 'test_candidate_bond_changes.txt', 'train')
    remove_file('test.txt')
    remove_file('test.txt.proc')
    remove_file('test_graphs.bin')
    remove_file('test_candidate_bond_changes.txt')

    # Test a file of both valid and invalid reactions
    reaction1 = '[CH2:15]([CH:16]([CH3:17])[CH3:18])[Mg+:19].[CH2:20]1[O:21][CH2:22][CH2:23]' \
                '[CH2:24]1.[Cl-:14].[OH:1][c:2]1[n:3][cH:4][c:5]([C:6](=[O:7])[N:8]([O:9]' \
                '[CH3:10])[CH3:11])[cH:12][cH:13]1>>[OH:1][c:2]1[n:3][cH:4][c:5]([C:6](=[O:7])' \
                '[CH2:15][CH:16]([CH3:17])[CH3:18])[cH:12][cH:13]1\n'
    reaction2 = '[CH3:14][NH2:15].[N+:1](=[O:2])([O-:3])[c:4]1[cH:5][c:6]([C:7](=[O:8])[OH:9])' \
                '[cH:10][cH:11][c:12]1[Cl:44].[OH2:16]>>[N+:1](=[O:2])([O-:3])[c:4]1[cH:5][c:6]' \
                '([C:7](=[O:8])[OH:9])[cH:10][cH:11][c:12]1[NH:15][CH3:14]\n'
    reactions = [reaction1, reaction2]
    with open('test.txt', 'w') as f:
        for reac in reactions:
            f.write(reac)
    dataset = WLNCenterDataset('test.txt', './test_graphs.bin')
    remove_file('test.txt')
    remove_file('test.txt.proc')
    remove_file('test_graphs.bin')
    remove_file('_valid_reactions.proc')
    remove_file('_invalid_reactions.proc')

def test_jtvae():
    vocab = JTVAEVocab()
    dataset = JTVAEZINC('train', vocab)

if __name__ == '__main__':
    # test_alchemy()
    # test_pdbbind()
    # test_pubchem_aromaticity()
    # test_tox21()
    # test_esol()
    # test_freesolv()
    # test_lipophilicity()
    # test_astrazeneca_chembl_solubility()
    # test_wln_reaction()
    test_jtvae()
