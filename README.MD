# About

We are attempting to convert UML diagrams to adapt to the Fortis robustification. Additionally, we aim to convert state transition diagrams (STDs) to LTS notation, as we consider STDs to be automata.

## UML To Alloy

Unfortunately, we have found no existing tool for converting UML diagrams to Alloy, like [UML to Alloy and back again](https://link.springer.com/chapter/10.1007/978-3-642-12261-3_16). As a result, we have decided to develop our own solution.

[](misc/uml-to-alloy.png)

We will focus on UML diagrams that include OCL constraints.

## STD to LTS

Since state transition diagrams are a form of automata, we believe it should be straightforward to convert them to LTS notation.

[](misc/voting-std.png)

For the provided STD, we have the following `sys.lts` specification:

```LTS
EM = (password -> P1),
P1 = (select -> P2),
P2 = (vote -> P3 | back -> P1),
P3 = (confirm -> EM | back -> P2).
```

We have gathered several examples of LTS specifications from the [Concurrency: State Models & Java Programs Book](https://www.doc.ic.ac.uk/ltsa/samples/), and we are utilizing the [LTS tool](https://github.com/yylonly/LTSA) to validate our conversions.

Please let me know if you need further details or modifications!
