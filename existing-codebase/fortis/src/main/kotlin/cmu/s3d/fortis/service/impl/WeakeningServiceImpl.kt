package cmu.s3d.fortis.service.impl

import cmu.s3d.fortis.common.Spec
import cmu.s3d.fortis.common.SpecType
import cmu.s3d.fortis.common.asSerializableWord
import cmu.s3d.fortis.service.WeakeningService
import cmu.s3d.fortis.ts.lts.ltsa.LTSACall
import cmu.s3d.fortis.ts.lts.ltsa.LTSACall.asLTS
import cmu.s3d.fortis.ts.lts.ltsa.LTSACall.compose
import cmu.s3d.fortis.ts.lts.toFluent
import cmu.s3d.fortis.ts.parallel
import cmu.s3d.fortis.weakening.*
import net.automatalib.alphabet.Alphabets
import net.automatalib.automaton.fsa.NFA
import net.automatalib.word.Word

class WeakeningServiceImpl : WeakeningService {
    @Deprecated("Use generateExamplesFromTrace instead")
    override fun generateExamplesFromProgress(
        sysSpecs: List<Spec>,
        envSpecs: List<Spec>,
        progress: String,
        fluents: List<String>
    ): List<Word<String>> {
        val sys = parseSpecs(sysSpecs)
        val env = parseSpecs(envSpecs)
        val model = parallel(sys, env)
        return ProgressExampleGenerator(model, progress)
            .withFilter(InvariantExampleFilter(fluents.map { it.toFluent()?: error("Invalid fluent string") }))
            .map { it.asSerializableWord() }.toList()
    }

    override fun generateExamplesFromTrace(
        sysSpecs: List<Spec>,
        envSpecs: List<Spec>,
        trace: Word<String>,
        inputs: Collection<String>,
        fluents: List<String>,
        numOfAdditionalExamples: Int
    ): List<Word<String>> {
        val sys = parseSpecs(sysSpecs)
        val env = parseSpecs(envSpecs)
        val model = parallel(sys, env)
        return TraceExampleGenerator(model, trace, Alphabets.fromCollection(inputs), numOfAdditionalExamples)
            .withFilter(InvariantExampleFilter(fluents.map { it.toFluent()?: error("Invalid fluent string") }))
            .map { it.asSerializableWord() }.toList()
    }

    override fun weakenSafetyInvariant(
        invariant: String,
        fluents: List<String>,
        positiveExamples: List<Word<String>>,
        negativeExamples: List<Word<String>>
    ): List<String> {
        // FIXME: This assumes that the invariant is in the form: [](a -> b) && [](c -> d), but LTSA does not support.
        val invariantPairs = SimpleInvariant.multipleFromString(invariant)
        if (invariantPairs.isEmpty())
            error("Invalid invariant format")

        val weakener = SimpleInvariantWeakener.build(
            invariant = invariantPairs,
            fluents = fluents.map { it.toFluent()?: error("Invalid fluent string") },
            positiveExamples = positiveExamples,
            negativeExamples = negativeExamples
        )
        val solutions = mutableListOf<String>()
        var solution = weakener.learn()
        while (solution != null) {
            solutions.add(solution.getInvariant().joinToString(" && "))
            solution = solution.next()
        }
        return solutions
    }

    override fun weakenGR1Invariant(
        invariant: String,
        fluents: List<String>,
        positiveExamples: List<Word<String>>,
        negativeExamples: List<Word<String>>,
        maxNumOfNode: Int
    ): String? {
        // FIXME: This assumes that the invariant is in the form: [](a -> b) && [](c -> d), but LTSA does not support.
        val invariantPairs = SimpleGR1Invariant.multipleFromString(invariant)
        if (invariantPairs.isEmpty())
            error("Invalid invariant format")

        val weakener = GR1InvariantWeakener.build(
            invariant = invariantPairs,
            fluents = fluents.map { it.toFluent()?: error("Invalid fluent string") },
            positiveExamples = positiveExamples,
            negativeExamples = negativeExamples,
            maxNumOfNode = maxNumOfNode + fluents.size
        )
        val solution = weakener.learn()
        return solution?.getGR1Invariant()
    }

    private fun parseSpec(spec: Spec): NFA<Int, String> {
        return when (spec.type) {
            SpecType.FSP -> LTSACall.compile(spec.content).compose().asLTS()
            else -> error("Unsupported spec type")
        }
    }

    private fun parseSpecs(specs: List<Spec>): NFA<Int, String> {
        if (specs.isEmpty()) error("Specs cannot be empty")
        if (specs.size == 1) return parseSpec(specs.first())
        return parallel(*specs.map { parseSpec(it) }.toTypedArray())
    }
}