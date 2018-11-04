# 447Project2

**Due Friday, November 16th, 11:59 pm**

## Description

Expanding on the ideas from Project 1, write a program that can match a smaller pattern graph to a larger target graph.
A pattern graph matches if every node and arc can be aligned to a corresponding node or arc in the target graph.
In particular, if an arc from the pattern graph aligns to an edge in the target graph, then they must have the same label and
the nodes at the end points of the arcs must also align.  Take into account the type hierarchy for nodes.

The graphs are simplified versions of the full logical form, containing only types and roles.

## Examples

|pattern  |target   |result   |reason   |
|---------|---------|---------|---------|
|[APPLY-FORCE :agent ANIMAL] | [PUSH :agent PERSON :affected PHYS-OBJ] | success | PUSH < APPLY-FORCE |
| |[PUSH :affected PHYS-OBJ :agent PERSON]| success | role order doesn't matter|
| |[PUSH :affected PHYS-OBJ :agent PHYS-OBJECT]| fail | not (PHYS-OBJ < ANIMAL |
| |[PUSH :affected PHYS-OBJ | fail | no "agent" role|
| |[EVENT-OF-ACTION :agent ANIMAL] | fail | not (EVENT-OF-ACTION < APPLY-FORCE) |

## Notes

Your code should be able to match nested structures of arbitrary depths, eg
```
[WANT 
  :experiencer PERSON
  :formal [CONSUME
              :agent PERSON
          ]
]
```
is a valid pattern graph.

## Submission

This time, I'd like you to submit your final code as a jupyter notebook.  Your report can be included in the notebook.  
Submit a zip file containing all the relevant project files.  Your report should contain a description of any design
decisions you made and any issues you encountered.

Additionally, include 3 pattern graphs, including one pattern with at least 2 levels of nesting (like the example above)
and 3 sentences that each pattern should match (for a total of 3 patterns and 9 sentences)
