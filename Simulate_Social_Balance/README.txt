**SIMULATE SOCIAL BALANCE**
**Sameet Sreenivasan, Aug. 2014 **

The file "sim_balance.py" simulates a scenario where there is an external "media" field biasing individuals on a social network to become centrists, while considerations of social balance (see: http://arxiv.org/pdf/physics/0605183.pdf), cause individuals to update their states spontaneously, to become leftists, rightists or centrists. The assumption is that a link between a leftist and rightist is always unfriendly, whereas links between other combinations of states are friendly. The competition between external influence and social balance determines whether the system evolves to the all-centrist consensus state or to a steady state where the population is mixed, and consists of non-zero fractions of leftists, rightists and centrists.


To run the simulation from command line:
	python sim_balance.py

To set parameters, use the "balanceParams.yaml" file. (see main file header comment for details) Note that the parameter "timesteps", is the number of time steps in units of N that one requires the simulation to be run for.