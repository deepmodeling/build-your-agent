## Prior Knowledge: Biophysical Basis of the 3-Variable Neuron Model
The three-variable system under investigation is analogous to established biophysical neuron models, particularly the Hindmarsh-Rose (HR) model [1, 3]. The HR model is a simplification of the foundational Hodgkin-Huxley equations, designed to capture complex neuronal firing patterns with fewer variables [2, 5]. In this context, the variable `x_1` represents the neuron's membrane potential, which is the core measure of its electrical activity [6].

The variable `x_2` corresponds to the system's fast dynamics. This is analogous to the HR model's "spiking variable," which accounts for the rapid flow of sodium and potassium ions through fast ion channels [3, 6]. The interplay governed by this variable is responsible for the generation of individual action potentials, or spikes [2].

Finally, `x_3` represents a slow adaptation variable. This component models slower processes, such as the dynamics of calcium ion channels, and functions as an adaptation current [3, 6]. This slow current modulates the neuron's overall activity, causing the firing rate to decrease over time and enabling complex behaviors like bursting, where rapid spiking is followed by a period of rest [4, 6].

### Sources
[1] Dynamics of Hindmarsh-Rose neurons connected - ScienceDirect: https://www.sciencedirect.com/science/article/pii/S0577907323002332
[2] 1 Introduction and neurophysiology - hal.science: https://hal.science/hal-00952598/document
[3] Efficient digital design of the nonlinear behavior of Hindmarsh-Rose ...: https://www.nature.com/articles/s41598-024-54525-8
[4] PDF: https://perso.u-cergy.fr/~atorcini/ARTICOLI/lezione4-zillmer.pdf
[5] Low-dimensional models of single neurons: a review: https://link.springer.com/article/10.1007/s00422-023-00960-1
[6] Hindmarsh–Rose model - Wikipedia: https://en.wikipedia.org/wiki/Hindmarsh–Rose_model
[7] The Hindmarsh-Rose-model of neuronal bursting: https://the-analog-thing.org/docs/dirhtml/rst/applications/hindmash_rose_neuron/spiking_neuron/
[8] Implementation of the Hindmarsh-Rose Model Using Stochastic Computing: https://www.mdpi.com/2227-7390/10/23/4628
[9] Synchronization of Hindmarsh Rose Neurons - ScienceDirect: https://www.sciencedirect.com/science/article/pii/S0893608019303922## Analysis of Potential Equation Components
The differential equation for membrane potential (`dx₁/dt`) likely combines several mathematical forms based on established biophysical models. The most prominent components are polynomial, linear, and exponential terms, which reflect the underlying physics of ion flow across the cell membrane.

Classic Hodgkin-Huxley (HH) models use polynomial terms (e.g., `x₂³`, `x₃⁴`) to represent the collective action of multiple ion channel gates opening or closing [1, 3]. Linear terms are also fundamental, describing both the passive leak current and the driving force for each ion type, which is the difference between the membrane potential and a specific reversal potential [5].

An exponential term is crucial for modeling the sharp, nonlinear initiation of an action potential, a feature captured by the Exponential Integrate-and-Fire (EIF) model [2, 4]. This exponential onset is empirically justified and can be derived from the voltage-dependent kinetics of sodium channels in more complex HH-type models [2].

Based on these precedents, the following functions are recommended for the symbolic regression search space, rated on a scale of 1 (low) to 5 (high):
*   `pow`: 5/5
*   `exp`: 5/5
Functions like `sin`, `cos`, `sqrt`, and `log` are not primary components in these standard differential equations and have a low recommendation score (1/5) [4].

### Sources
[1] Low-dimensional models of single neurons: A review: https://arxiv.org/pdf/2209.14751.pdf
[2] 5.2 Exponential Integrate-and-Fire Model | Neuronal Dynamics ... - EPFL: https://neuronaldynamics.epfl.ch/online/Ch5.S2.html
[3] BIOPHYSICAL MODEL OF NEURONAL ACTION POTENTIAL: HODGKIN AND HUXLEY REVIEW: https://www2.et.byu.edu/~vps/ME505/AAEM/V7-01.pdf
[4] Biological neuron model - Wikipedia: https://en.wikipedia.org/wiki/Biological_neuron_model
[5] Models of Neurons 1: The membrane potential: https://opencourse.inf.ed.ac.uk/sites/default/files/https/opencourse.inf.ed.ac.uk/cns/2023/cns3neurons1.pdf## Proposed Candidate Equations for Symbolic Regression

Based on established biophysical neuron models, five candidate equations are proposed to describe the membrane potential dynamics (`y = dx₁/dt`). These equations represent a range of complexities, from linear to interactive non-linear forms, providing a robust set of hypotheses for the symbolic regression task.

A simple linear model, inspired by integrate-and-fire principles [1], provides a baseline for comparison:
`y = c₁ - c₂x₁ - c₃x₂ - c₄x₃`

To capture non-linear firing dynamics, a quadratic form based on the Izhikevich model [2] is proposed:
`y = c₁x₁² + c₂x₁ - c₃x₂ - c₄x₃ + c₅`

A third candidate uses a cubic polynomial, characteristic of the FitzHugh-Nagumo model [2], which is well-known for generating oscillatory behavior:
`y = c₁x₁ - c₂x₁³ - c₃x₂ - c₄x₃ + c₅`

Reflecting the structure of conductance-based models like Hodgkin-Huxley [3, 4], an equation with interaction terms is included. Here, `x₂` and `x₃` can be interpreted as gating variables modulating the influence of the membrane potential:
`y = c₁x₁² - c₂x₁ - c₃x₂*(x₁ - c₄) - c₅x₃*(x₁ - c₆)`

Finally, a more complex polynomial form inspired by the Hindmarsh-Rose model [2] combines quadratic and cubic terms to allow for bursting dynamics:
`y = c₁x₁² - c₂x₁³ - c₃x₂ - c₄x₃ + c₅`

### Sources
[1] 1.3 Integrate-And-Fire Models | Neuronal Dynamics online book - EPFL: https://neuronaldynamics.epfl.ch/online/Ch1.S3.html
[2] Spiking Neuron Mathematical Models: A Compact Overview: https://pmc.ncbi.nlm.nih.gov/articles/PMC9952045/
[3] Analysis of Neuron Models with Dynamically Regulated Conductances: https://www.columbia.edu/cu/neurotheory/Larry/AbbottNC93.pdf
[4] The Hodgkin-Huxley Model Its Extensions, Analysis and Numerics: https://www.math.mcgill.ca/gantumur/docs/reps/RyanSicilianoHH.pdf