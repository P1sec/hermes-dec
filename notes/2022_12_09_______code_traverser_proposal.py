#!/usr/bin/python3
#-*- encoding: Utf-8 -*-
from typing import List, Tuple, Dict, Set, Sequence, Union, Optional, Any
from dataclasses import dataclass

# First, obtain a "branching_point" set of local function
# code address/offsets from the caller of the current
# module (referencing jump, switch, generator resume,
# exception handling, return, throw points), in order
# to be able to delimite discrete code segments that will
# serve for splitting up code paths.

# Explore all code paths and represent these with lists of
# "CodePathItem"s representing segments of the explored
# code along with jump choices.
#
# Include the exploration of error throwing conditions.
class CodePathItem: 
    code_sequence_start : int
    code_sequence_end : int
    jump_target_item : Optional[int]
    did_jump : bool
    
    is_throw_action : bool
    is_forin_init : bool
    is_forin_iter : bool
    if_switch_action : bool
    
    is_cyclic_end : bool
    # is_throw_end : bool # : These are normally explored, and not actual ends
    is_return_end : bool

    is_conditional_jump : bool
    is_unconditional_jump : bool
    
jump_point_to_pos_and_neg_paths = Dict[int, Tuple[List[CodePathItem], List[CodePathItem]]]

"""
    Proposed post-processing algorithms:
        In order to determine actual final-decompiled-code
        loop (for..in, for, while, break, continue, do..while) structures:
      a. Gather loops boundaries present in the code through
         observing cycling points. Many loop or condition
         extremities may lead at a cycling point. The actual
         check that led to the cycling may be any of the
         latest branch conditions that were evaluated.
      b. Discriminate the checks that led not to jump in
         other code paths. Observe the latest checks.
        b2. We should check for the following information:
            which of the jumps interverting while making
            the same other choices will lead NOT to cycle?
                => We should keep table of choices somewhere
                   in order to filter the corresponding
                   combinations
                    (just the other serialized code paths?)
                            => Maybe we should keep up a
                            "jump_point_to_pos_and_neg_paths : Dict[int, Tuple[List[CodePathItem], List[CodePathItem]]]" structure for this purpose?
                            
                            /** (Likely insufficient because of nested loops, breaks etc.:)
                            => AND THEN
                            Check jump points for which {pos,neg} branching
                            leads to ALWAYS or NEVER cycling at the given
                            point, when the opposite {neg,pos} braching lead
                            to SOMETIMES or NEVER/ALWAYS cycle at the given point
                            
                                => These are "break" or "continue" or for/while/do..while
                                => extremities
                               */
                                
                                =>====> (We should produce "while(1)" loops with
                                => conditional "break" and "continue"
                                => statements only in a first time,
                                => and optimize it into "for..in", "for"
                                => and "while" loops later I think)
                                
                                    => TODO: How to detect the "continue"
                                    => statements?
                                    
                                            ====> On va faire des "while(1)" OUI,
                                            ==< MAIS COMBIEN D'IMBRIQUÉS
                                            ET  
                                                Jusu'à o    ù   
                                                 ?
                                                    c'est oute la question
                                                    
                                                        Peut-être que l'ajout d'une imbrication doit
                                                        être fait à posteriori et réservé aux
                                                        problèmes d'imbrication de blocs (plus tard...)
                                                        déjà)
                                                        
                                                        
                                                        
                                                        
                                                        Mais, en fait, plutôt que de faire des "code
                                                        paths" avec des sequents et des choix de
                                                        sauts booléens qui se concurrencent
                                                        mutuellement, ce serait pas mieux de revenir
                                                        à l'approche des basic blocks connectés avec
                                                        des edge/nodes pour mettre des while(1) autour
                                                        des structures cycliques à ce stade ?
                                                        
                                        Pour régler la question de l'imbrication, il
                                        s'agira aussi et surtout de trouver les circuits
                                        cycliques "fermés" à eux-mêmes et ne dépassant pas
                                            au-delà d'un autre point de cyclage :
                                                            
                                while(1) { <-- X (unconditional cyclic jump target)
                                    while(1) {
                                        if(7) {
                                            if(4) continue; // <- C'est le fait qu'il y ait un continue ici et un "}" plus loin à la fois qui détermine qu'on ne soit pas dans une simple partie de la boucle supérieure précédent un if je pense ? Non, tout pourrait tenir dans un "!4" (le "while(1) {" c'est juste une instruction de retour à un point précédent qui veut être actionnée par n'importe quel "{" "continue" tandis que le "}" "break" sont une instructon de saut vers un second point pas encore visité) <- Faire des "continue" dans des boucles imbriquées l'une immédiatement dans le début de l'autre est OK ça ne créé pas de zbeul 
                                        }
                                        while(1) {
                                            if(6) break;
                                        }
                                        if(9) {
                                            console.log('tata')
                                            if(5) break; // <- Là ça va faire couic s'il n'y a pas la deuxième boucle imbriquée non ?
                                            console.log('quelque chose')
                                        }
                                        if(7) {
                                            alert('bonjour')
                                        }
                                    }
                                    if(4) continue;
                                    if(5) break;
                                    console.log('l')
                                } <-- unconditional cyclic jump to X

                                vv  
                                
                                            => Franchement, traverser des graphes de code
                                            c'est bien plus utile que de comparer des
                                            chemins de code visitables je pense
                                
                                    ^ Il faut trouver les circuits fermés là-dedans
                                        => 
                                        
                                        
                                            ==+>+>>
                                                Au final il faudriat peut-êtrre
                                                    utiliser le premier outil (le control flow graph)
                                                        pour former les while(1) de base
                                                            et ensuite tester les superpositions par
              Vous avez 30 jours pour choisir                                                  segments de code pour trouver
                                                                    les opportunités de if()
                                                                        et ajouter les
                                                                            break les continue et
                                                                                    les autres while(1)
                                                                                    continue selon
                                                                                        les possibilités
                                                                                            non ?
                                                                                                
                                                                                            
                                                                                            
                                                                                            Mettre un while(1) à chaque point de cyclage 
                                                                                                selon le 
                                                                                                    control flow
                                                                                                        graph
                                                                                                            serait la première étape en
                                                                                                                fait.
"""
