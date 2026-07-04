<main class="dashboard-container">
<h1>About</h1>
<p>
My name is George and I am interested in energy markets and the renewable transition! 
This page aims to unify information on UK energy markets and present it in a useful manner.
</p>
<p>
This project is built with <a href="https://svelte.dev/">SvelteKit</a> and the source code is available <a href="https://github.com/georgesm2/Energy-Hub">here</a>.
</p>
<p>
I have taken inspiration from the very well-designed dashboard by <a href="https://grid.iamkate.com">National Grid: Live</a> although I have some methodological differences. 
Generation data is taken from the Elexon FUELINST stream except for embedded solar which is from the <a href="https://api.pvlive.uk/">Sheffield Solar API</a>.
Carbon intensity data comes from the <a href="https://carbonintensity.org.uk/">NESO API</a>.
</p>
Wholesale price data comes from elexon while the <a href="">Octopus Energy API</a> is used to get the current agile price. The listed Ofgem price cap is the average across the country 
although it should be noted that this changes from region to region. 
<p>
Contains <a href="https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/B1610/stream">BMRS data</a> © Elexon Limited copyright and database right 2026.
</p>
</main>

<style>
.dashboard-container {
  margin: 0rem auto;
  padding: 0rem 2.5rem 0rem 2.5rem;;
  max-width: 1600px;
  align-items: center;
  font-family: sans-serif;
  line-height: 1.5;
}
</style>