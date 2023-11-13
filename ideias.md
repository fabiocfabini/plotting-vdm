# Future Ideas to the plot package

## Plot Modifiers

We could want to change the look of a specific plot. Change ylim, xlim, add a particular text to it etc. Making the Plotter class accept a sequence of modifiers would be a good idea. The modifiers would be functions that take a plot as input and return a plot as output. The plotter would then apply all the modifiers to the plot before returning it.