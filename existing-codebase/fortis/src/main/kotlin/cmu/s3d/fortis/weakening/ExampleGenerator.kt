package cmu.s3d.fortis.weakening

import cmu.s3d.fortis.ts.alphabet
import cmu.s3d.fortis.ts.lts.traceToLTS
import cmu.s3d.fortis.ts.parallel
import net.automatalib.alphabet.Alphabet
import net.automatalib.automaton.fsa.NFA
import net.automatalib.util.automaton.builder.AutomatonBuilders
import net.automatalib.word.Word
import java.util.*
import kotlin.collections.ArrayDeque

open class ExampleGenerator<S, I>(
    private val model: NFA<S, I>,
    numOfAdditionalExamples: Int
) : Iterator<Word<I>>, Iterable<Word<I>> {
    private val dfsStack: ArrayDeque<DFSRecord<S, I>> = ArrayDeque()
    private val visited: MutableSet<S> = mutableSetOf()
    private val examples: Queue<Word<I>> = LinkedList()
    private val numOfAdditionalExamples = if (numOfAdditionalExamples < 0) Int.MAX_VALUE else numOfAdditionalExamples
    private var additionalExamplesCount = 0
    private var exampleFilter: ExampleFilter<I>? = null

    private class DFSRecord<S, I>(val state: S, val trace: Word<I>, val visited: Set<S>)

    override fun iterator(): Iterator<Word<I>> {
        dfsStack.clear()
        model.initialStates.forEach { dfsStack.add(DFSRecord(it, Word.epsilon(), emptySet())) }
        visited.clear()
        examples.clear()
        additionalExamplesCount = 0
        exampleFilter?.reset()
        return this
    }

    private fun searchNext() {
        if (visited.size == model.size() && additionalExamplesCount++ >= numOfAdditionalExamples)
            return

        val currentExampleSize = examples.size
        // a DFS search
        while (dfsStack.isNotEmpty()) {
            val record = dfsStack.removeLast()
            var isDeadlock = true

            visited.add(record.state)
            for (a in model.alphabet()) {
                val successors = model.getSuccessors(record.state, a)
                isDeadlock = isDeadlock && successors.isEmpty()
                // search non-lasso cases
                for (s in successors - record.visited) {
                    dfsStack.add(
                        DFSRecord(
                            state = s,
                            trace = Word.fromList(record.trace + a),
                            visited = record.visited + record.state
                        )
                    )
                }
                // search lasso cases
                if ((successors intersect record.visited).isNotEmpty()) {
                    offerExample(Word.fromList(record.trace + a))
                }
            }
            if (isDeadlock) {
                offerExample(record.trace)
            }
            if (examples.size > currentExampleSize) {
                return
            }
        }
    }

    protected open fun offerExample(trace: Word<I>) {
        if (exampleFilter == null || exampleFilter!!.filter(trace)) {
            examples.offer(trace)
        }
    }

    override fun hasNext(): Boolean {
        if (examples.isEmpty()) {
            searchNext()
            return examples.isNotEmpty()
        }
        return true
    }

    override fun next(): Word<I> {
        return if (examples.isNotEmpty()) examples.poll() else error("No more examples")
    }

    fun withFilter(filter: ExampleFilter<I>): ExampleGenerator<S, I> {
        exampleFilter = filter
        return this
    }
}

@Deprecated("Use TraceExampleGenerator instead")
class ProgressExampleGenerator<S, I>(model: NFA<S, I>, progress: I) : ExampleGenerator<Int, I>(
    parallel(model, progress.let {
        val inputs = model.alphabet()
        val builder = AutomatonBuilders.newDFA(inputs)
            .withInitial(0)
            .from(0).on(it).to(1)
        for (a in inputs) {
            if (a != it) {
                builder.from(0).on(a).loop()
            }
        }
        builder.create()
    }),
    0
)

class TraceExampleGenerator<S, I>(
    model: NFA<S, I>,
    private val observedTrace: Word<I>,
    private val observedInputs: Alphabet<I>,
    numOfAdditionalExamples: Int = 0
) : ExampleGenerator<Int, I>(
    parallel(model, traceToLTS(observedTrace, observedInputs, makeError = false)),
    numOfAdditionalExamples
) {
    override fun offerExample(trace: Word<I>) {
        val projected = trace.filter { it in observedInputs }
        if (observedTrace.asList() == projected) {
            super.offerExample(trace)
        }
    }
}