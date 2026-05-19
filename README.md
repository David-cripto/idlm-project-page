# IDLM Generation GIF Clarity Criteria

This project page contains an animated GIF for the section "Text Generation: DLM vs. IDLM".
The GIF should explain one idea:

> IDLM keeps the same target generation behavior as a discrete diffusion language model, but reaches the completed text in far fewer model calls.

## Success Criteria

The GIF is considered clear only if it satisfies all of the following.

1. Same target text
   Both panels must converge to the exact same long token sequence. Otherwise, a reader may confuse speedup with a change in the task.

2. Long visible sequence
   The generated sequence must contain more than 64 visible token positions. This prevents readers from confusing the 64 DLM sampling steps with sequence length and makes the visualization closer to the long text-strip style used by the DUO reference page.

3. Single main comparison variable
   The visual contrast must be the number of model calls: many calls for the DLM, few calls for IDLM. Token content, panel geometry, and final output should be controlled.

4. Synchronized stacked reading
   DLM and IDLM must be visible at the same time, with aligned long-sequence strips, so the reader does not need to remember one animation while watching another.

5. Early completion signal
   IDLM must visibly finish while the DLM panel is still partially masked. This creates the causal readout: same final text, fewer calls.

6. Low cognitive load
   The animation should use at most three semantic channels: tokens, call count/progress, and completion status. Extra diagrams, equations, and moving decorations are avoided.

7. No visual defects
   Text and tokens must stay inside their panels, the GIF must not clip important labels, and the page must not introduce horizontal overflow on mobile or desktop.

8. Accurate claim
   The GIF may illustrate one concrete example, such as a 72-token sequence generated with 64 calls vs. 4 calls, while the page text keeps the paper-level claim as 4x-64x fewer inference steps.

## Mathematical Clarity Model

There is no universal theorem proving that one visualization is maximally clear for every human reader. Instead, this page uses an explicit local model of clarity.

Let the intended proposition be:

`P = "IDLM reaches the same completed generated text with fewer model calls than a standard DLM."`

Let a visualization `V` contain visual variables `X_1, ..., X_n`. Define a simple clarity score:

`Clarity(V) = I(V; P) / (H(V | P) + epsilon)`

where:

- `I(V; P)` is the information the visualization gives about the intended proposition.
- `H(V | P)` is visual entropy not explained by the proposition: unrelated motion, uncontrolled text differences, changing layouts, decorative elements, and ambiguous labels.
- `epsilon > 0` prevents division by zero.

Under this model, the clearest visualization in our constrained family is one that maximizes signal about `P` while minimizing unrelated variation.

### Proof Sketch Under the Model

We restrict the design family to two-panel animated comparisons of DLM and IDLM generation.

1. If both methods generate different final token sequences, then output content becomes a confounder. Formally, the output sequence `Y` varies with method `M`, so part of `I(V; P)` is spent explaining `Y` instead of speed. Holding `Y` constant removes this confounder and reduces `H(V | P)`.

2. If the visualized sequence is shorter than the DLM step count, sequence length and step count are easy to conflate. Enforcing `sequence_length > 64` makes sequence length observably independent from the 64-call DLM budget, reducing ambiguity in `H(V | P)`.

3. If panel geometry differs, readers must infer whether position, size, or layout encodes meaning. Those variables are not part of `P`, so they increase `H(V | P)` without increasing `I(V; P)`. Aligned long-sequence strips are therefore clearer.

4. If the only intentionally changing variables are call count, token reveal state, and completion status, every change maps directly to `P`. Adding unrelated motion or extra visual encodings can only add entropy unless it is correlated with `P`.

5. Showing IDLM complete while DLM is still masked creates a visible separating event. In terms of a binary completion variable `D_t`, there exists a frame `t` such that `D_t(IDLM)=1` and `D_t(DLM)=0`. This directly encodes the proposition that IDLM needs fewer calls.

Therefore, within the stated design family and clarity score, the chosen implementation is locally optimal: it controls the final sequence and layout, encodes speed through call counts/progress, and removes visual changes that are not part of the proposition.

## Implementation Checklist

The generator script should produce:

- `assets/idlm-generation.gif`: the GIF used by the page.
- `assets/idlm-generation-preview.png`: a contact sheet for quick inspection.

The script should report whether:

- the target token sequence is identical in both panels;
- the sequence length is greater than 64 token positions;
- IDLM finishes before DLM;
- all declared text boxes fit;
- the GIF dimensions and file size are reasonable for the page.
