## Variable Introduction

The biophysical neuron model describes the dynamics of a neuron using three state variables and a target output. The membrane potential, x₁, represents the electrical voltage across the neuron's cell membrane, typically measured in millivolts (mV) [3, 5, 7]. A resting potential is often around -70 mV [3, 5]. Its dynamic fluctuations are fundamental to neuronal signaling and action potential generation [1, 3, 4].

The fast activation variable, x₂, models rapid ion channel dynamics, such as voltage-gated sodium channel activation, which drives quick depolarization during an action potential [1, 2, 3]. These processes occur on a fast millisecond timescale [1, 2].

The slow adaptation variable, x₃, captures slower biophysical processes like the activation of potassium or calcium-gated potassium currents [1, 2]. These currents mediate spike-frequency adaptation and regulate firing patterns over slower timescales [1, 2, 3].

The target variable, y = dx₁/dt, represents the rate of change of the membrane potential [1, 3, 4, 6, 7]. This derivative quantifies how quickly the membrane voltage changes, crucial for characterizing the rapid upstroke and repolarization phases of neuronal spikes [1, 3]. Its typical unit is millivolts per millisecond (mV/ms) [7].

### Sources
[1] PDF: https://perso.u-cergy.fr/~atorcini/ARTICOLI/lezione4-zillmer.pdf
[2] FitzHugh-Nagumo model - Wikipedia: https://en.wikipedia.org/wiki/FitzHugh–Nagumo_model
[3] PDF: https://www.ucl.ac.uk/~rmjbale/3307/Reading_FitzHughNagumo.pdf
[4] PDF: https://people.brandeis.edu/~pmiller/COMP_NEURO/lifb.pdf
[5] A&P1 Homework 5 & 6 Flashcards | Quizlet: https://quizlet.com/545982942/ap1-homework-5-6-flash-cards/
[6] 5.1 Thresholds in a nonlinear integrate-and-fire model - EPFL: https://neuronaldynamics.epfl.ch/online/Ch5.S1.html
[7] PDF: https://www.cns.nyu.edu/~david/handouts/membrane.pdf## Background Equations

The Hodgkin-Huxley (HH) model is a canonical biophysical neuron model describing action potential initiation and propagation [1, 2]. It represents the membrane as a capacitor and ion channels as voltage- and time-dependent conductances. The change in membrane potential ($x_1$) is governed by:

$C_m \frac{dx_1}{dt} = I - \bar{g}_{Na} m^3 h (x_1 - E_{Na}) - \bar{g}_K n^4 (x_1 - E_K) - \bar{g}_l (x_1 - E_l)$ [1, 3, 4]

Here, $m$ ($x_2$, fast activation), $h$ (fast inactivation), and $n$ ($x_3$, slow adaptation) are dimensionless gating variables. Their dynamics are described by voltage-dependent differential equations, typically of the form $\frac{dx}{dt} = \alpha_x(x_1)(1-x) - \beta_x(x_1)x$, where the rate constants $\alpha_x$ and $\beta_x$ often include exponential functions of membrane potential [1, 4, 5].

Simplified models include the FitzHugh-Nagumo (FHN) model, a two-dimensional system that captures spiking dynamics using polynomial terms [6, 7]. The Morris-Lecar (ML) model is another two-variable system, offering a more biophysically realistic simplification than FHN, with equations describing ionic currents [7, 8]. The Prescott model, a variant of Morris-Lecar, explicitly includes a slow adaptation variable ($z$) and various adaptation currents like voltage-gated K+ current, affecting threshold dynamics [9].

### Sources
[1] Hodgkin–Huxley model - Wikipedia: https://en.wikipedia.org/wiki/Hodgkin–Huxley_model
[2] PDF: https://pi.math.cornell.edu/~gucken/PDF/hh_twist.pdf
[3] 2.2 Hodgkin-Huxley Model | Neuronal Dynamics online book: https://neuronaldynamics.epfl.ch/online/Ch2.S2.html
[4] PDF: https://goldmanlab.faculty.ucdavis.edu/wp-content/uploads/sites/263/2016/07/HodgkinHuxley.pdf
[5] Biophysical mechanism of spike threshold dependence on the rate of rise ...: https://pubmed.ncbi.nlm.nih.gov/23344915/
[6] Fitzhugh-Nagumo Model - an overview | ScienceDirect Topics: https://www.sciencedirect.com/topics/biochemistry-genetics-and-molecular-biology/fitzhugh-nagumo-model
[7] PDF: https://www.math.fsu.edu/~bertram/lectures/neural_dynamics.pdf
[8] PDF: https://link.springer.com/content/pdf/10.1134/S2070048217030036.pdf?pdf=button
[9] Contributions of adaptation currents to dynamic spike threshold on slow ...: https://www.sciencedirect.com/science/article/pii/S1007570416304154## Physically Motivated Functional Terms

Biophysical neuron models frequently incorporate specific functional terms derived from underlying physiological processes. Linear and multiplicative terms are fundamental, representing Ohm's law for ion flow, where current is proportional to conductance and voltage difference (e.g., `g(V-E)`). This accounts for passive leak currents and active ionic currents (e.g., `x_1`, `x_1*x_2`, `x_1*x_3`) [4, 5, 8].

Polynomial terms, particularly powers, are essential for modeling voltage-gated ion channels. In the Hodgkin-Huxley model, the opening probabilities of sodium and potassium channels are represented by gating variables raised to powers like `m^3` and `n^4` (e.g., `x_2^3`, `x_3^4`), reflecting multiple independent gates [4, 8]. The FitzHugh-Nagumo model uses a cubic polynomial (`v^3`) to capture the neuron's non-linear voltage dynamics [7, 8].

Exponential terms (`exp`) are crucial for describing the rapid, sharp onset of action potentials, as seen in the adaptive exponential integrate-and-fire model [4]. They also appear in the voltage-dependent rate functions (alpha and beta) that govern the kinetics of Hodgkin-Huxley gating variables [8]. Other functions like `sqrt` and `log` are not typically found as direct functional terms of the state variables in canonical neuron dynamics, but `log` can appear in the Nernst equation for calculating constant reversal potentials [5]. While a modified FitzHugh-Nagumo model can use `sin` [8], it is not a universally canonical term for intrinsic biophysical dynamics.

### Sources
[1] Low-dimensional models of single neurons: a review: https://pubmed.ncbi.nlm.nih.gov/37060453/
[2] Automatically Selecting a Suitable Integration Scheme for Systems of ...: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6186990/
[3] Constructing functional models from biophysically-detailed neurons: https://pmc.ncbi.nlm.nih.gov/articles/PMC9455888/
[4] Biological neuron model - Wikipedia: https://en.wikipedia.org/wiki/Biological_neuron_model
[5] PDF: https://opencourse.inf.ed.ac.uk/sites/default/files/https/opencourse.inf.ed.ac.uk/cns/2023/cns3neurons1.pdf
[6] PDF: https://diposit.ub.edu/dspace/bitstream/2445/186707/2/tfg_pairo_lopez_alexandra.pdf
[7] FitzHugh-Nagumo model - Wikipedia: https://en.wikipedia.org/wiki/FitzHugh%E2%80%93Nagumo_model
[8] PDF: https://www.tnstate.edu/mathematics/mathreu/filesreu/Action_Potential_Report.pdf## Recommended Unary Operators

Based on analysis of canonical biophysical neuron models, specific unary operators are recommended for the symbolic regression search space. The `pow` and `exp` operators are essential. The Hodgkin-Huxley model, a foundational neuron model, utilizes integer powers (e.g., m³ and n⁴) to represent the probability of ion channel opening, reflecting the need for multiple independent gating subunits [2, 3, 4, 5].

Exponential functions are crucial for describing the voltage-dependent rate constants (alpha and beta functions) that govern ion channel kinetics [2, 3]. The "exponential integrate-and-fire" model also explicitly incorporates an exponential term for spike generation [4]. These models demonstrate the fundamental role of exponential relationships in neuronal dynamics.

Conversely, `sqrt`, `sin`, `cos`, and `log` operators are generally not found in the core equations of these biophysical neuron models [2, 3, 4, 5]. While CORDIC algorithms can compute these functions [6, 10], their direct physical relevance as unary operations on the state variables (membrane potential, activation, adaptation) within the differential equations for such systems is not supported by the surveyed literature on neuron dynamics [7, 8, 9]. Therefore, their exclusion from the search space is justified.

### Sources
[1] The Hodgkin-Huxley Heritage: From Channels to Circuits - PMC: https://pmc.ncbi.nlm.nih.gov/articles/PMC3500626/
[2] PDF: https://opencourse.inf.ed.ac.uk/sites/default/files/https/opencourse.inf.ed.ac.uk/cns/2024/cns4neurons2.pdf
[3] PDF: https://www2.et.byu.edu/~vps/ME505/AAEM/V7-01.pdf
[4] Biological neuron model - Wikipedia: https://en.wikipedia.org/wiki/Biological_neuron_model
[5] 2.3 The Zoo of Ion Channels | Neuronal Dynamics online book: https://neuronaldynamics.epfl.ch/online/Ch2.S3.html
[6] CORDIC - Wikipedia: https://en.wikipedia.org/wiki/CORDIC
[7] PDF: http://personal.kent.edu/~bosikiew/Algebra-handouts/appl-logs.pdf
[8] 6.5: Applications of Exponential and Logarithmic Functions: https://math.libretexts.org/Courses/Fresno_City_College/Precalculus:__Algebra_and_Trigonometry_(Math_4_-_FCC)/06:_Exponential_and_Logarithmic_Functions/6.05:_Applications_of_Exponential_and_Logarithmic_Functions
[9] 5.7 Applications of Exponential and Logarithmic Functions - Functions ...: https://odp.library.tamu.edu/math150/chapter/5-7-applications-of-exponential-and-logarithmic-functions/
[10] PDF: https://eprints.soton.ac.uk/267873/1/tcas1_cordic_review.pdf# Prior-Informed Symbolic Regression for Biophysical Neuron Dynamics

This report addresses the challenge of inferring the differential equation governing neuronal membrane potential ($dx_1/dt$) using symbolic regression. To ensure the discovered models are biophysically plausible and accurate, we integrate established knowledge from canonical neuron dynamics.

We provide a prior-informed guide by surveying common equation structures, interactions among variables, and typical functional forms observed in models like Hodgkin-Huxley. This analysis culminates in justified recommendations for which mathematical operators should be included or excluded from the symbolic regression search space.## Summary

This report guides symbolic regression for $dx_1/dt$ by surveying biophysical neuron models. Common structures involve ionic currents, with membrane potential ($x_1$) interacting with fast ($x_2$) and slow ($x_3$) gating variables. $x_1$ dictates $x_2$/$x_3$ kinetics, modulating conductances that affect $dx_1/dt$.

Key functional terms include linear/multiplicative forms (Ohm's law), powers (for ion channel gating), and exponentials (for voltage-dependent rates and spike initiation). Recommended unary operators are:

*   `pow`: For cooperative ion channel gating (e.g., $m^3, n^4$).
*   `exp`: For voltage-dependent kinetics and spike onset.

Operators like `sqrt`, `sin`, `cos`, and `log` are not directly supported by canonical biophysical neuron equations, hence recommended for exclusion. This selection enhances physical plausibility.