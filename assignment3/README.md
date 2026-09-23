 - Which mutation is most dangerous and why? Provide quantitative evidence. 

 Mutations A, B, C are all equally dangerous. The most dangerous one from a biological perspective is A, because it is the most direct cause, while B and C are equally dangerous but idirect causes to the same attractor. As evidence is the cancer-like basin size of one of the 2 attractors each has, where Growth = 1, DNA_damage = 1 and Death = 0. Aditionally, based on the percentage of all 256 states that lead to caner-like states, A, B and C have 50%, while D has 3.1%. For comparison, the original network also has a 3.1% cancer-like basin, so A, B, and C each multiply it by 16. These three mutations have these percentages bacuse 128 of the 256 states are cancer-like, while the other 128 belong to the basin of the DNA_damage = 0 attractor, the normal no-death growth state. Mutattion D adds a rule to TP53, which is not a node in the network, so it has no effect.


 - Explain the role of feedback loops (e.g., MYC → MDM2 → p53)

Before the mutations, the original netwrok has 3 attractors and the DNA_damage = 1 attractors are:
- p53 = 1; MDM2 = 0; MYC = 0; Death = 1 - p53 wins which results to death
- p53 = 0; MDM2 = 1; MYC = 1; Death = 0 - MYC/MDM2 win whcih reuslts to growth despite DNA damage
These two states form bistable toggle created by the mutual inhibitation between MYC and p53. The p53 is stabilized by the loop: p53 = DNA_damage AND p53, which is why the death attractor has a large basin size. After any of the mutations, A at p53 or B at MYC or C at MDM2, the p53=1/Death attractor is gone and only the MTC/MDM2 nodes remain high, whcih means one state has been destroyed. All three mutations converge on the same outcome (p53=0, Growth=1) even though they break the toggle at different points. Now, the feedback is what makes the mutation dangerous. Based on the loop: MYC -> MDM2 -| p53, by forcing MYC on actiavets MDM2 which suppresses p53. The loop trasnmits the oncogenuc signal to the tumor suppresor. 


 - What are the limitations of this Boolean network model? Discuss 3 specific limitations.

1. In the code, all 8 nodes update at the same at each step, which is not true in real life. In the code every gene reads and comoutes its next value at the same instant, while real genes turn on adn off at different speeds. This can create fake attractors or hide the real ones. For example, one gene that should respond to another gene's change might get the update too late or too ealry.

2. The network has only 8 nodes, which is too little for a biology network, especially fot the real p53 network which includes even more nodes. 

3. There is no randomness in the netwrok. Real cells are noisy. For example, two cells that are the same can respong in two different ways to the same damage or change.
 