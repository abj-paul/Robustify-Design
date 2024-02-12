package cmu.s3d.fortis.weakening

import cmu.s3d.fortis.ts.lts.Fluent
import cmu.s3d.fortis.ts.lts.evaluateFluent
import cmu.s3d.ltl.LassoTrace
import cmu.s3d.ltl.State
import cmu.s3d.ltl.learning.LTLLearner
import cmu.s3d.ltl.learning.LTLLearningSolution
import net.automatalib.word.Word

data class SimpleGR1Invariant(
    val antecedent: CNF,
    val consequent: DNF,
)

class GR1InvariantWeakener(
    private val invariant: List<SimpleGR1Invariant>,
    private val fluents: List<Fluent>,
    positiveExamples: List<Word<String>>,
    negativeExamples: List<Word<String>>,
    maxNumOfNode: Int
) {
    private val ltlLearner: LTLLearner

    init {
        val constraints = generateConstraints()
        ltlLearner = LTLLearner(
            literals = fluents.map { it.name },
            positiveExamples = positiveExamples.map { toLassoTrace(evaluateFluent(it, fluents)) },
            negativeExamples = negativeExamples.map { toLassoTrace(evaluateFluent(it, fluents)) },
            maxNumOfNode = maxNumOfNode,
            excludedOperators = listOf("F", "Until", "X"),
            customConstraints = constraints
        )
    }

    fun learn(): LTLLearningSolution? {
        return ltlLearner.learn()
    }

    fun generateAlloyModel(): String {
        return ltlLearner.generateAlloyModel()
    }

    private fun toLassoTrace(valuation: List<Map<Fluent, Boolean>>): LassoTrace {
        return LassoTrace(
            prefix = valuation.map { s -> State(s.map { (k, v) -> k.name to v }.toMap()) }
        )
    }

    private fun generateConstraints(): String {
        return """
            fun childrenOf[n: DAGNode]: set DAGNode { n.^(l+r) }
            fun childrenAndSelfOf[n: DAGNode]: set DAGNode { n.*(l+r) }
            fun ancestorsOf[n: DAGNode]: set DAGNode { n.~^(l+r) }
            
            fact {
                // learn G(a -> b) && G(c -> d)
                root in G + And
                all n: G {
                    ancestorsOf[n] in And
                    n.l in Imply
                    all n': childrenOf[n.l] | n' not in Imply + G
                    all n': childrenOf[n.l] & Neg | n'.l in Literal
                    all n': childrenAndSelfOf[n.l.l] & Or | no childrenOf[n'] & And
                    all n': childrenAndSelfOf[n.l.r] & And | no childrenOf[n'] & Or
                }
            }
            ${invariant.joinToString("") { generateInvariantConstraints(it) } }
        """
    }

    private fun generateInvariantConstraints(inv: SimpleGR1Invariant): String {
        val antecedentDAG = mutableListOf<String>()
        val antecedentAnds = mutableListOf<String>()
        val antecedentOrs = mutableListOf<String>()
        val antecedentNegs = mutableListOf<String>()
        val antecedentRoot = generateDAG(inv.antecedent, antecedentDAG, antecedentAnds, antecedentOrs, antecedentNegs)

        val consequentDAG = mutableListOf<String>()
        val consequentAnds = mutableListOf<String>()
        val consequentOrs = mutableListOf<String>()
        val consequentNegs = mutableListOf<String>()
        val consequentRoot = generateDAG(inv.consequent, consequentDAG, consequentAnds, consequentOrs, consequentNegs)

        return """
            fact {
                some rt: childrenAndSelfOf[root] & G {
                    some antecedent: DAGNode${
            if (antecedentAnds.isNotEmpty()) ", ${antecedentAnds.joinToString(", ")}: And" else ""
        }${
            if (antecedentOrs.isNotEmpty()) ", ${antecedentOrs.joinToString(", ")}: Or" else ""
        }${
            if (antecedentNegs.isNotEmpty()) ", ${antecedentNegs.joinToString(", ")}: Neg" else ""
        } {
                        antecedent in $antecedentRoot
                        rt.l.l in $antecedentRoot or rt.l.l in And and rt.l.l.l in $antecedentRoot
                        ${if (antecedentDAG.isNotEmpty()) "(${antecedentDAG.joinToString(" + ")}) in ((l+r) :> rt.l.l.^(l+r))" else ""}
                    }
                
                    some consequent: DAGNode${
            if (consequentOrs.isNotEmpty()) ", ${consequentOrs.joinToString(", ")}: Or" else ""
        }${
            if (consequentAnds.isNotEmpty()) ", ${consequentAnds.joinToString(", ")}: And" else ""
        }${
            if (consequentNegs.isNotEmpty()) ", ${consequentNegs.joinToString(", ")}: Neg" else ""
        } {
                        consequent in $consequentRoot
                        rt.l.r in $consequentRoot or rt.l.r in Or and rt.l.r.l in $consequentRoot
                        ${if (consequentDAG.isNotEmpty()) "(${consequentDAG.joinToString(" + ")}) in ((l+r) :> rt.l.r.^(l+r))" else ""}
                    }
                }
            }
        """
    }

    private fun generateDAG(
        cnf: CNF,
        dag: MutableList<String>,
        ands: MutableList<String>,
        ors: MutableList<String>,
        negs: MutableList<String>
    ): String {
        if (cnf.clauses.size == 1)
            return generateDAG(cnf.clauses[0], dag, ands, ors, negs)
        else {
            val and = "a${ands.size}"
            ands.add(and)
            val l = generateDAG(cnf.clauses[0], dag, ands, ors, negs)
            val r = generateDAG(CNF(cnf.clauses.subList(1, cnf.clauses.size)), dag, ands, ors, negs)
            dag.add("$and->$l")
            dag.add("$and->$r")
            return and
        }
    }

    private fun generateDAG(
        dnf: DNF,
        dag: MutableList<String>,
        ands: MutableList<String>,
        ors: MutableList<String>,
        negs: MutableList<String>
    ): String {
        if (dnf.clauses.size == 1)
            return generateDAG(dnf.clauses[0], dag, ands, ors, negs)
        else {
            val or = "o${ors.size}"
            ors.add(or)
            val l = generateDAG(dnf.clauses[0], dag, ands, ors, negs)
            val r = generateDAG(DNF(dnf.clauses.subList(1, dnf.clauses.size)), dag, ands, ors, negs)
            dag.add("$or->$l")
            dag.add("$or->$r")
            return or
        }
    }

    private fun generateDAG(
        conjunction: Conjunctions,
        dag: MutableList<String>,
        ands: MutableList<String>,
        ors: MutableList<String>,
        negs: MutableList<String>
    ): String {
        if (conjunction.props.size == 1)
            return generateDAG(conjunction.props[0], dag, ands, ors, negs)
        else {
            val and = "a${ands.size}"
            ands.add(and)
            val l = generateDAG(conjunction.props[0], dag, ands, ors, negs)
            val r = generateDAG(Conjunctions(conjunction.props.subList(1, conjunction.props.size)), dag, ands, ors, negs)
            dag.add("$and->$l")
            dag.add("$and->$r")
            return and
        }
    }

    private fun generateDAG(
        disjunction: Disjunctions,
        dag: MutableList<String>,
        ands: MutableList<String>,
        ors: MutableList<String>,
        negs: MutableList<String>
    ): String {
        if (disjunction.props.size == 1)
            return generateDAG(disjunction.props[0], dag, ands, ors, negs)
        else {
            val or = "o${ors.size}"
            ors.add(or)
            val l = generateDAG(disjunction.props[0], dag, ands, ors, negs)
            val r = generateDAG(Disjunctions(disjunction.props.subList(1, disjunction.props.size)), dag, ands, ors, negs)
            dag.add("$or->$l")
            dag.add("$or->$r")
            return or
        }
    }

    private fun generateDAG(
        prop: Proposition,
        dag: MutableList<String>,
        ands: MutableList<String>,
        ors: MutableList<String>,
        negs: MutableList<String>
    ): String {
        if (prop.second) {
            return prop.first
        } else {
            val neg = "ng${negs.size}"
            negs.add(neg)
            dag.add("$neg->${prop.first}")
            return neg
        }
    }
}