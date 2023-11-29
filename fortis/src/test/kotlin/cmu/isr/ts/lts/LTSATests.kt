package cmu.isr.ts.lts

import cmu.isr.ts.alphabet
import cmu.isr.ts.lts.ltsa.LTSACall
import cmu.isr.ts.lts.ltsa.LTSACall.asDetLTS
import cmu.isr.ts.lts.ltsa.LTSACall.asLTS
import cmu.isr.ts.lts.ltsa.LTSACall.compose
import cmu.isr.ts.lts.ltsa.writeFSP
import net.automatalib.util.automata.Automata
import net.automatalib.util.automata.builders.AutomatonBuilders
import net.automatalib.words.impl.Alphabets
import org.junit.jupiter.api.Test
import java.io.ByteArrayOutputStream
import kotlin.test.assertEquals

class LTSATests {

  @Test
  fun testParseError() {
    val spec = "A = (a -> b -> A | b -> ERROR)."
    val m = LTSACall.compile(spec).compose().asDetLTS()
    val e = AutomatonBuilders.newDFA(Alphabets.fromArray("a", "b"))
      .withInitial(0)
      .from(0).on("a").to(1)
      .from(1).on("b").to(0)
      .from(0).on("b").to(-1)
      .withAccepting(0, 1)
      .create()
    assert(Automata.testEquivalence(e, m, e.inputAlphabet))
  }

  @Test
  fun testParseNoError() {
    val spec = "A = (a -> b -> A)."
    val m = LTSACall.compile(spec).compose().asDetLTS()
    val e = AutomatonBuilders.newDFA(Alphabets.fromArray("a", "b"))
      .withInitial(0)
      .from(0).on("a").to(1)
      .from(1).on("b").to(0)
      .withAccepting(0, 1)
      .create()
    assert(Automata.testEquivalence(e, m, e.inputAlphabet))
  }

  @Test
  fun testWriteFSPWithError() {
    val a = AutomatonBuilders.newDFA(Alphabets.fromArray("a", "b"))
      .withInitial(0)
      .from(0).on("a").to(1)
      .from(1).on("b").to(2)
      .withAccepting(0, 1)
      .create()
      .asLTS()
    val out = ByteArrayOutputStream()
    writeFSP(out, a, a.inputAlphabet)
    assertEquals("S0 = (a -> S1),\nS1 = (b -> ERROR).\n", out.toString())
  }

  @Test
  fun testWriteFSPWithStop() {
    val a = AutomatonBuilders.newDFA(Alphabets.fromArray("a", "b"))
      .withInitial(0)
      .from(0).on("a").to(1)
      .from(1).on("b").to(2)
      .withAccepting(0, 1, 2)
      .create()
      .asLTS()
    val out = ByteArrayOutputStream()
    writeFSP(out, a, a.inputAlphabet)
    assertEquals("S0 = (a -> S1),\nS1 = (b -> STOP).\n", out.toString())
  }

  @Test
  fun testCompileAndWriteWithError() {
    val spec = "A = (a -> b -> ERROR)."
    val m = LTSACall.compile(spec).compose().asLTS()
    val out = ByteArrayOutputStream()
    writeFSP(out, m, m.alphabet())
    assertEquals("S0 = (a -> S1),\nS1 = (b -> ERROR).\n", out.toString())
  }

  @Test
  fun testCompileAndWriteWithStop() {
    val spec = "A = (a -> b -> STOP)."
    val m = LTSACall.compile(spec).compose().asLTS()
    val out = ByteArrayOutputStream()
    writeFSP(out, m, m.alphabet())
    assertEquals("S0 = (a -> S1),\nS1 = (b -> STOP).\n", out.toString())
  }

  @Test
  fun testWriteFSPRemoveError() {
    val spec = "A = (a -> b -> ERROR)."
    val m = LTSACall.compile(spec).compose().asLTS(removeError = true)
    val out = ByteArrayOutputStream()
    writeFSP(out, m, m.alphabet())
    assertEquals("S0 = (a -> STOP).\n", out.toString())
  }

  @Test
  fun testCompileSafetyLTL() {
    val safety = LTSACall.compileSafetyLTL(
      ClassLoader.getSystemResource("specs/therac25-2/p1.lts").readText(), "OVER_DOSE")
      .asDetLTS(removeError = true)
    val out = ByteArrayOutputStream()
    writeFSP(out, safety, safety.alphabet())
    assertEquals(
      "S0 = (set_ebeam -> S0 | reset -> S0 | set_xray -> S1 | e -> S2 | x -> S0),\n" +
            "S1 = (set_ebeam -> S0 | reset -> S0 | set_xray -> S1 | x -> S1),\n" +
            "S2 = (set_ebeam -> S2 | reset -> S2 | e -> S2 | x -> S0).\n",
      out.toString())
  }
}